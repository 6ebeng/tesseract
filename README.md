# Kurdish OCR Training System

## 📁 Project Structure

```
tesseract/
├── README.md              # Overview and quick start
├── .editorconfig          # Consistent line endings (LF for WSL scripts, CRLF for PowerShell)
├── .gitattributes         # Normalize endings, mark binaries
├── .gitignore             # Ignore generated artifacts
├── run_training.ps1       # Windows/WSL launcher
├── fonts.conf             # Fontconfig override (used by generation)
├── tessdata/              # Trained models (ckb.traineddata installed here)
├── tessdata_best/         # Optional: upstream best models
├── docs/                  # Documentation (moved references here)
│   ├── README.md
│   └── kurdish_characters.md
└── work/                  # Training system (runs inside WSL Ubuntu)
    ├── generate_ckb_training_data.sh
    ├── execute_ckb_training.sh
    ├── verify_ckb_traineddata.py
    ├── corpus/ckb.training_text
    └── fonts/ (TTF files used for synthetic data)
```

## 🚀 Quick Start

All training functionality is in the `work/` directory.

### Run the training flow (PowerShell → WSL)

```powershell
# From the repo root on Windows
./run_training.ps1 -Mode GenerateTrain
```

### Quick Test

```powershell
# Quick smoke test (optionally after training)
./run_training.ps1 -Mode SmokeTest
```

## 📚 Documentation

- Docs now live under `docs/`.
- Kurdish characters reference moved to `docs/kurdish_characters.md`.
- Training scripts live under `work/`. Use the launcher for common tasks.

## ✅ Latest Training Results

Add your latest results here after running your experiments.

## 🛠️ Requirements

- Windows 10/11 with WSL2
- Ubuntu installed in WSL
- Tesseract OCR installed in WSL

---

For detailed instructions and troubleshooting, navigate to the `work/` directory.

## ✅ Verify Kurdish character coverage

After training or copying a `ckb.traineddata`, you can verify that it includes all Kurdish Arabic-based letters and Arabic‑Indic digits.

- From PowerShell, run the launcher and choose the verify option or run non-interactively:

```powershell
./run_training.ps1
# then choose: 5. Verify ckb.traineddata covers Kurdish chars

# Non-interactive:
./run_training.ps1 -Mode SmokeTest
```

- Or run the verifier directly inside WSL from the `work` folder:

```bash
python3 work/verify_ckb_traineddata.py --traineddata /mnt/c/tesseract/tessdata/ckb.traineddata --out work/output/verify_report.json
```

The script unpacks the traineddata using `combine_tessdata -u`, reads the `.unicharset`, and checks coverage. It returns:

- 0 if all required characters are present
- 2 if any characters are missing
- 1 on environment/tool errors
