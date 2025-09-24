# Work area (WSL)

This folder contains all scripts and data used for generating ground truth and training the Kurdish `ckb` model for Tesseract.

Key scripts:

- `generate_ckb_training_data.sh`: renders synthetic ground-truth from the corpus using local fonts.
- `execute_ckb_training.sh`: runs the LSTM fine-tuning pipeline and exports `ckb.traineddata`.
- `verify_ckb_traineddata.py`: checks that a traineddata covers Kurdish characters.

Data layout:

- `corpus/ckb.training_text`: main corpus used to render text.
- `fonts/`: TTF files used to render images.
- `training_output/`: generated artifacts (ground truth, tmp, model output). Ignored by Git.

Run everything from Windows using the repo launcher:

```powershell
./run_training.ps1 -Mode GenerateTrain
```

Or run individual steps inside WSL by `cd` into this folder.
