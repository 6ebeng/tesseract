# Kurdish OCR Training (work/)

This directory contains the end-to-end Kurdish (ckb) OCR training system built on Tesseract 5 (LSTM).

## Structure

```
work/
├─ scripts/                # Training and utility scripts
│  ├─ final_robust_train.sh   # Best/robust pipeline (all fonts + augmentation)
│  ├─ fast_robust_train.sh    # Faster subset pipeline
│  ├─ build_ckb_auto.sh       # Auto build pipeline
│  ├─ master_training.sh      # Menu helper (optional)
│  ├─ generate_font_list.sh   # Enumerate available fonts
│  ├─ debug_fonts.sh          # Diagnose font rendering
│  ├─ clean_workspace.sh      # Safe cleanup of generated artifacts
│  └─ fonts.conf              # WSL fontconfig (points to Windows fonts)
├─ corpus/                 # Training text (e.g., ckb.training_text)
├─ fonts/                  # Kurdish fonts (.ttf / .otf)
├─ output/                 # Logs, checkpoints, traineddata (generated)
├─ ground-truth-*/         # Generated ground-truth sets (generated)
├─ tessdata_tmp/           # Intermediate (generated)
├─ tmp/                    # Scratch (generated)
└─ docs/                   # Reports, summaries, status
```

## Prerequisites

- Windows 10/11 with WSL2 (Ubuntu)
- Tesseract 5.x (with text2image, lstmtraining, combine_tessdata) installed in WSL
- ImageMagick (optional; used for augmentation)

Check in WSL:

```bash
which tesseract text2image lstmtraining combine_tessdata
```

## WSL fonts configuration (important)

We use the Windows fonts from this repo and optionally system fonts. The scripts set:

- `FONTCONFIG_FILE=/mnt/c/tesseract/work/scripts/fonts.conf`

That file includes:

- `/mnt/c/tesseract/work/fonts`
- `/mnt/c/Windows/Fonts` (optional)
- A valid cache dir `/tmp/fontconfig-cache`

Rebuild cache if fonts change:

```bash
export FONTCONFIG_FILE=/mnt/c/tesseract/work/scripts/fonts.conf
mkdir -p /tmp/fontconfig-cache
fc-cache -f -v | head -n 50
```

Validate a font renders (handles spaces in names):

```bash
export FONTCONFIG_FILE=/mnt/c/tesseract/work/scripts/fonts.conf
text2image --text=/mnt/c/tesseract/work/corpus/ckb.training_text \
   --outputbase=/tmp/t2i_test \
   --font '08_Sarchia_Al Arabiya TV_1' \
   --fonts_dir=/mnt/c/tesseract/work/fonts \
   --resolution 300 --ptsize 12 --max_pages 1
ls -l /tmp/t2i_test.*
```

## Clean build

To wipe generated artifacts before a fresh run:

```bash
wsl -d Ubuntu -- bash -lc 'cd /mnt/c/tesseract/work/scripts && ./clean_workspace.sh'
```

This preserves sources (fonts, corpus, docs) and removes: `ground-truth-*`, `output`, `tessdata_tmp`, `tmp`, `training`.

## Best/robust training run

Run the full robust pipeline (all fonts + augmentation):

```bash
wsl -d Ubuntu -- bash -lc '\
   cd /mnt/c/tesseract/work/scripts && \
   export FONTCONFIG_FILE=/mnt/c/tesseract/work/scripts/fonts.conf && \
   mkdir -p /mnt/c/tesseract/work/output/logs && \
   LOG=/mnt/c/tesseract/work/output/logs/robust_$(date +%Y%m%d_%H%M%S).log && \
   echo Logging to $LOG && \
   FONT_LIST_OVERRIDE=/tmp/fontlist.txt bash final_robust_train.sh 2>&1 | tee $LOG'
```

Pipeline stages:

1. Dependency checks (tesseract, text2image, lstmtraining, combine_tessdata, ImageMagick)
2. Input verification (corpus, fonts)
3. Clean environment (safe delete/move-aside)
4. Training data generation (text2image for each font, create .tif/.box/.gt.txt; optional augmentations)
5. LSTMF conversion (tesseract ... lstm.train over base .tif/.box)
6. Training (extract base LSTM from ara.traineddata; lstmtraining --continue_from ...; checkpoints created in `output`)
7. Finalize model and install to `tessdata/ckb.traineddata`

Monitor:

```bash
wsl -d Ubuntu -- bash -lc 'tail -n 60 /mnt/c/tesseract/work/output/logs/robust_*.log'
```

## Results

- Checkpoints: `work/output/ckb_robust*.checkpoint`
- Final model: `work/output/ckb_robust.traineddata`
- Installed copy: `tessdata/ckb.traineddata` (Windows repo)

Test OCR:

```bash
wsl -d Ubuntu -- bash -lc 'tesseract /mnt/c/tesseract/work/test-images/test.tif stdout -l ckb --psm 6'
```

## Troubleshooting

- PowerShell swallows bash `$()`/quotes:

  - Wrap the entire WSL command in single quotes; put bash quotes inside.

- Font list errors or segfault on `--list_available_fonts`:

  - The helper `generate_font_list.sh` falls back to filenames and supports writing to `/tmp` via `FONT_LIST_OUTPUT`.

- “No checkpoint found – training may have failed”:
  - Ensure LSTMF were created (see `work/output/robust-lstmf.txt`).
  - Confirm `combine_tessdata -e` produced `work/output/ara.lstm`.
  - Check the training log for iterations and `ckb_robust*.checkpoint` in `work/output`.

## Notes

- Some fonts may fail to render; the pipeline continues and uses successful ones.
- Augmentation requires ImageMagick; if absent, base images are still used.
