# Kurdish OCR - Quick Start Guide

## Essential Commands

### 1. Run Master Training Script (All-in-One)

```powershell
# From PowerShell
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/scripts && bash master_training.sh"
```

### 2. Quick Test OCR

```powershell
# From PowerShell
wsl -d Ubuntu -- bash -c "bash /mnt/c/tesseract/work/scripts/quick_test.sh"
```

### 3. Verify Installation

```powershell
# From PowerShell
wsl -d Ubuntu -- bash -c "bash /mnt/c/tesseract/work/scripts/test_installation.sh"
```

## Master Script Menu Options

When you run `master_training.sh`, you'll see:

1. **Start New Training** - Begin from scratch
2. **Continue Training** - Resume from checkpoint
3. **Extended Training** - 5000 iterations for best accuracy
4. **Finalize Model** - Convert checkpoint to final model
5. **Test Model** - Test OCR on all test images
6. **Clean Data** - Remove temporary files
7. **Exit**

## Only 3 Scripts Needed

- `master_training.sh` - Everything you need for training
- `test_installation.sh` - Verify system is ready
- `quick_test.sh` - Fast OCR testing

## Model Locations

- **WSL**: `/usr/share/tesseract-ocr/5/tessdata/ckb.traineddata`
- **Windows**: `C:\tesseract\tessdata\ckb.traineddata`

## Troubleshooting

If scripts won't run, ensure you're using WSL:

```powershell
wsl -d Ubuntu -- bash -c "your_command_here"
```

## Latest Results

- **Error Rate**: Reduced from 54.864% to 7.314%
- **Improvement**: 86.7%
- **Training**: 5000 iterations completed
