# Kurdish OCR Training System

## 📁 Project Structure

```
tesseract/
├── README.md           # This file
├── tessdata/          # Trained OCR models
│   └── ckb.traineddata   # Kurdish model
└── work/              # Training system
    ├── scripts/       # All training scripts
    ├── test-images/   # Test data
    ├── docs/          # Documentation
    └── README.md      # Detailed documentation
```

## 🚀 Quick Start

All training functionality is in the `work/` directory.

### Run the Master Training Script

```bash
# From PowerShell
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/scripts && bash master_training.sh"
```

### Quick Test

```bash
# From PowerShell
wsl -d Ubuntu -- bash -c "bash /mnt/c/tesseract/work/scripts/quick_test.sh"
```

## 📚 Documentation

- **Detailed Setup**: See [work/README.md](work/README.md)
- **Quick Reference**: See [work/QUICK_START_GUIDE.md](work/QUICK_START_GUIDE.md)
- **Training Report**: See [work/docs/FINAL_TRAINING_REPORT.md](work/docs/FINAL_TRAINING_REPORT.md)

## ✅ Latest Training Results

- **Error Rate**: Reduced from 54.864% to 7.314% (86.7% improvement)
- **Iterations**: 5000 completed
- **Model**: Kurdish (ckb) OCR model trained and installed

## 🛠️ Requirements

- Windows 10/11 with WSL2
- Ubuntu installed in WSL
- Tesseract OCR installed in WSL

---

For detailed instructions and troubleshooting, navigate to the `work/` directory.

## ✅ Verify Kurdish character coverage

After training or copying a `ckb.traineddata`, you can verify that it includes all Kurdish Arabic-based letters and Arabic‑Indic digits.

- From PowerShell, run the launcher and choose the verify option:

```powershell
./run_training.ps1
# Choose: 7. Verify ckb.traineddata covers Kurdish chars
```

- Or run the verifier directly inside WSL from the `work` folder:

```bash
python3 work/verify_ckb_traineddata.py --traineddata /mnt/c/tesseract/tessdata/ckb.traineddata --out work/output/verify_report.json
```

The script unpacks the traineddata using `combine_tessdata -u`, reads the `.unicharset`, and checks coverage. It returns:

- 0 if all required characters are present
- 2 if any characters are missing
- 1 on environment/tool errors
