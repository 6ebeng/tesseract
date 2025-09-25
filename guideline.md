# Kurdish (ckb) OCR Training – Complete Guide

This guide explains how to generate training data, train a Kurdish Sorani (ckb) Tesseract model, evaluate it, and package artifacts—using the provided PowerShell launcher on Windows with WSL.

- Target readers: Windows users with WSL (Ubuntu) and VS Code
- Scope: End‑to‑end pipeline with one command, plus advanced tuning

---

## TL;DR (one command)

Run the full pipeline (Corpus → Generate → Train). This produces two variants and installs them:

- best (float) → `tessdata/best/ckb.traineddata`
- fast (int8) → `tessdata/fast/ckb.traineddata`

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\tesseract\run_training.ps1 -Mode All -UseFixer -SkipEval
```

- Remove `-SkipEval` if you’ve prepared real eval pairs under `work/real_gt/eval`.
- Use the interactive menu by running the script without parameters.

---

## Prerequisites

- Windows 10/11 with WSL (Ubuntu) installed and accessible
- VS Code (optional but recommended)
- Disk space: ~3–5 GB (fonts, synthesized data, logs)
- Internet (to install WSL packages during bootstrap)

### WSL packages (auto-handled by Bootstrap)

- `tesseract-ocr` and training tools: `tesseract-ocr-dev`
- `imagemagick`, `fontconfig`, `python3`, `python3-pip`

If you haven’t prepared WSL yet, run Bootstrap once:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\tesseract\run_training.ps1 -Mode Bootstrap
```

---

## Repository structure (key paths)

```
tessdata/                 # Packaged models used by Tesseract
  best/                   # Preferred best model output
  fast/                   # Fast model output
work/
  fonts/                  # TTF/OTF fonts used for synthesis
  corpus/                 # Input corpus files (*.txt). Final corpus file written here
  training_output/        # Generated ground truth, model, logs
  real_gt/                # Real-world eval pairs (images + ground truth .txt)
  tools/                  # Helper scripts: corpus builder, real CER, etc.
  *.sh, *.py              # WSL scripts and Python utilities
run_training.ps1          # Windows launcher (pipeline + menu)
```

---

## Quick start – Menu

Launch the menu:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\tesseract\run_training.ps1
```

Menu options:

- 1: Cleanup workspace
- 2: Generate → optionally Train
- 3: Train (skip generation)
- 4: Smoke test trained model
- 5: Verify model covers Kurdish characters
- 6: Build balanced corpus (uses fixer)
- 7: Evaluate real-world CER
- 8: Bootstrap WSL training toolchain
- 9: All: Corpus → Generate → Train → Eval

---

## One-command pipeline (non-interactive)

- All steps, skipping real evaluation:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\tesseract\run_training.ps1 -Mode All -UseFixer -SkipEval
```

- All steps, with real evaluation (requires data under `work/real_gt/eval`):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\tesseract\run_training.ps1 -Mode All -UseFixer
```

Notes:

- If `work/corpus` has no sources, corpus build will skip with a warning and the existing `ckb.training_text` will be used.
- After training, you get both variants under `work/training_output/model/` as `ckb.best.traineddata` and `ckb.fast.traineddata` (based on the preferred base). They’re also installed to the folders above.

---

## Individual modes and flags

- Bootstrap tools once in WSL:

```powershell
powershell.exe -File C:\tesseract\run_training.ps1 -Mode Bootstrap
```

- Build corpus (balanced):

```powershell
powershell.exe -File C:\tesseract\run_training.ps1 -Mode BuildCorpus -UseFixer -CorpusMinCount 10
```

- Generate only:

```powershell
powershell.exe -File C:\tesseract\run_training.ps1 -Mode Generate
```

- Train only:

```powershell
powershell.exe -File C:\tesseract\run_training.ps1 -Mode Train
```

- Generate + Train:

```powershell
powershell.exe -File C:\tesseract\run_training.ps1 -Mode GenerateTrain
```

- Evaluate real CER:

```powershell
powershell.exe -File C:\tesseract\run_training.ps1 -Mode Eval
```

- Smoke test (prints first lines of OCR):

```powershell
powershell.exe -File C:\tesseract\run_training.ps1 -Mode SmokeTest
```

### Useful flags

- Generation:
  - `-FontSize 18 -DPI 300 -Margin 15 -Leading 22 -CharSpacing 1 -EnableAug`
  - Overrides: `-CorpusFileOverride C:\path\ckb.txt -FontsDirOverride C:\path\fonts -OutputDirOverride C:\path\out`
- Training:
  - `-MaxIters 1500 -DebugInterval 50 -OEM 1 -PSM 6 -LatinDigits`
  - Extra args: `-TrainingExtraArgs "--some_lstmtraining_flag value"`
- All-mode:
  - `-SkipEval` to skip real eval

---

## Data preparation

### Fonts

- Place TTF/OTF files under `work/fonts`.
- The repo includes a starter set. Add more for diversity.

### Corpus

- Put one or more `.txt` files in `work/corpus/` (UTF-8). Examples: news, literature, common phrases, numbers, punctuation.
- The corpus builder balances rare Kurdish characters and writes `work/corpus/ckb.training_text.final`.

Run via menu option 6, or:

```powershell
powershell.exe -File C:\tesseract\run_training.ps1 -Mode BuildCorpus -UseFixer -CorpusMinCount 10
```

Outputs:

- `work/corpus/ckb.training_text.final`
- `work/output/char_histogram.csv`
- `work/output/corpus_stats.txt`

If you don’t run the corpus builder, generation uses `work/corpus/ckb.training_text`.

### Real-world evaluation set (optional but recommended)

Create pairs under `work/real_gt/eval`:

```
work/real_gt/eval/
  doc001.png   doc001.txt
  page_A.jpg   page_A.txt
```

- Each image must have a `.txt` with the same base name containing the exact ground truth (UTF-8, normalized).
- Run `-Mode Eval` or include Eval in `-Mode All`.

---

## What the pipeline produces

- Synthetic ground truth:
  - `work/training_output/ground_truth/*.tif|.box|.gt.txt`
- Training logs and checkpoints:
  - `work/training_output/logs/`, `work/training_output/model/`
- Final trained models (installed):
  - best (float): `tessdata/best/ckb.traineddata`
  - fast (int8): `tessdata/fast/ckb.traineddata`
- Final trained models (copies in model folder):
  - `work/training_output/model/ckb.best.traineddata`
  - `work/training_output/model/ckb.fast.traineddata`
- Evaluation reports:
  - `work/output/metrics.csv` (training metrics)
  - `work/output/real_metrics.csv` (real eval CER)
  - `work/output/verify_report.json` (character coverage)

---

## Verification and evaluation

### Smoke test

Quick OCR on a sample image using your trained model:

```powershell
powershell.exe -File C:\tesseract\run_training.ps1 -Mode SmokeTest
```

### Verify character coverage

Checks Kurdish letters and Arabic-Indic digits are present in the model:

```powershell
powershell.exe -File C:\tesseract\run_training.ps1
# choose 5 in the menu, or:
powershell.exe -File C:\tesseract\run_training.ps1 -Mode Eval   # for CER
```

For coverage verification from WSL directly:

```bash
# In WSL, optional alternative
cd /mnt/c/tesseract/work
python3 verify_ckb_traineddata.py --traineddata /mnt/c/tesseract/tessdata/best/ckb.traineddata --out output/verify_report.json
```

### Real-world CER

If you’ve populated `work/real_gt/eval`, run:

```powershell
powershell.exe -File C:\tesseract\run_training.ps1 -Mode Eval
```

See `work/output/real_metrics.csv` for per-file CER and overall averages.

---

## Advanced tuning

### Generation parameters

- Font size, DPI, margins, leading, char spacing
- Exposures are fixed to -1, 0, +1 by the generator
- Light image augmentations can be toggled with `-EnableAug`

### Training parameters

- Iterations: `-MaxIters 1500` (increase for larger datasets)
- Debug interval: `-DebugInterval 50`
- OEM/PSM: typically `-OEM 1` and `-PSM 6` for line/paragraph images
- Latin digits: `-LatinDigits` (forces ASCII digits; otherwise Arabic-Indic digits are used)
- Extra flags: `-TrainingExtraArgs "..."`

### Language model (DAWG/wordlist)

- The training integrates a frequency-based wordlist (built from the corpus) into DAWG for better decoding.
- To improve it, ensure your corpus contains a wide vocabulary; the builder will produce a sorted word list internally.

---

## Troubleshooting

- Ubuntu not available in WSL

  - Install Ubuntu from the Microsoft Store, then retry.

- `text2image` missing

  - Run Bootstrap, or in WSL: `sudo apt-get update && sudo apt-get install -y tesseract-ocr-dev`

- Fonts not found or fallback fonts used

  - Place fonts in `work/fonts`. The generator refreshes Fontconfig cache automatically.

- CRLF line endings break WSL scripts (`$'\r'` error)

  - The launcher normalizes line endings before execution.

- No corpus sources found

  - Place `.txt` files under `work/corpus/` or use the repo’s default `ckb.training_text`. The pipeline will continue if none are found (warning only).

- Low accuracy on real data
  - Expand corpus with real text domains; add more fonts (especially low-quality/handwriting-like if needed); increase `-MaxIters`; add diverse images to `work/real_gt/eval` to track true CER.

---

## Tips for higher quality

- Corpus

  - Cover Kurdish letters comprehensively; include punctuation, numbers, dates, names, places
  - Balance long/short lines; remove duplicates and very noisy lines

- Fonts

  - Mix multiple families and styles that reflect your real usage
  - Ensure fonts support Kurdish glyphs (Sorani); remove broken/duplicate fonts

- Augmentations

  - Enable for robustness to noise/scans (`-EnableAug`)

- Iterations/early stopping
  - Start with ~1500. If overfitting or underfitting is suspected, adjust and monitor `work/output/metrics.csv`.

---

## VS Code tasks (optional)

- CKB: Generate + Train → runs the unattended `GenerateTrain` mode
- CKB: Smoke Test → quick OCR output preview

You can still prefer the new `-Mode All` flow for a single command pipeline.

---

## Appendix: Alternative (Makefile in WSL)

Advanced users can use the WSL Makefile directly:

```bash
cd /mnt/c/tesseract/work
make all             # bootstrap + corpus + generate + train + eval
make buildcorpus
make generate
make train
make eval
```

---

## Where to look next

- `docs/IMPROVEMENTS.md` for ongoing ideas and future enhancements
- `work/tools/corpus_build.py` and `work/tools/eval_real_cer.py` for implementation details
- `work/execute_ckb_training.sh` for the training pipeline internals
