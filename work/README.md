# Work area (WSL)

This folder contains all scripts and data used for generating ground truth and training the Kurdish `ckb` model for Tesseract.

Key scripts:

- `generate_ckb_training_data.sh`: renders synthetic ground-truth from the corpus using local fonts.
- `execute_ckb_training.sh`: runs the LSTM fine-tuning pipeline and exports `ckb.traineddata`.
- `verify_ckb_traineddata.py`: checks that a traineddata covers Kurdish characters.
- `tools/eval_real_cer.py`: computes real-world CER on `real_gt/eval` image+gt pairs and writes `output/real_metrics.csv`.

Data layout:

- `corpus/ckb.training_text`: main corpus used to render text.
- `corpus/ckb.training_text.final`: optional final built corpus produced by the corpus builder.
- Optional curated additions the generator will auto-include when present:
  - `corpus/ckb_core_coverage.txt`, `corpus/ckb_extra_sentences.txt`, `corpus/ckb_formats_ner.txt`
  - `corpus/ckb_latin.training_text`, `corpus/ckb_latin_core_coverage.txt`, `corpus/ckb_latin_extra_sentences.txt`, `corpus/ckb_latin_formats_ner.txt`
  - `corpus/ckb_mixed.training_text` (Arabic + Latin in same lines)
- `fonts/`: TTF files used to render images.
- `training_output/`: generated artifacts (ground truth, tmp, model output). Ignored by Git.

Run everything from Windows using the repo launcher:

```powershell
./run_training.ps1 -Mode GenerateTrain
```

Or run individual steps inside WSL by `cd` into this folder.

Real eval (optional):

- Put a few real images and their matching `.gt.txt` under `real_gt/eval/`.
- Then run: `python3 tools/eval_real_cer.py` (from this folder in WSL) to get average CER.
