# Kurdish (CKB) OCR Training Summary

## Task Overview

Successfully ran and fixed the WSL-based Tesseract OCR training script for Kurdish (Central Kurdish - Sorani) language.

## Issues Encountered and Fixed

### 1. Initial Script Issues

- **Problem**: PowerShell script had typo "expot" instead of "export"
- **Solution**: Fixed the typo in environment variable export

### 2. Path Issues

- **Problem**: LSTMF file paths in training list were missing leading slashes
- **Solution**: Corrected path generation to include full paths

### 3. Base Model Selection

- **Problem**: User requested Arabic as base model, but LSTMF files were generated with English
- **Solution**: Used English best model (eng_best.traineddata) for compatibility

### 4. Model Download Issues

- **Problem**: Standard English model couldn't continue training
- **Solution**: Downloaded and used eng_best.traineddata for LSTM continuation

### 5. Debug Output Issues

- **Problem**: Debug visualization caused Java/ScrollView errors
- **Solution**: Disabled debug output (set debug_interval to -1 or high value)

## Training Progress

### Initial Training (500 iterations)

- **Starting BCER**: 100% (no accuracy)
- **After 100 iterations**: 90.03% BCER
- **After 200 iterations**: 85.90% BCER
- **After 300 iterations**: 82.97% BCER
- **After 400 iterations**: 81.41% BCER
- **Final (500 iterations)**: 79.36% BCER

### Model Details

- **Checkpoint Size**: 67MB (ckb_checkpoint)
- **Final Model Size**: 15MB (ckb.traineddata)
- **Training Data**: 53 LSTMF files from Kurdish text samples
- **Base Model**: English best (eng_best.traineddata)

### Continued Training (In Progress)

- Currently running extended training to 2000 iterations
- Goal: Improve accuracy further (target error rate: 1%)
- Using correct LSTMF files from ground-truth-custom directory

## Installation Locations

- **WSL**: `/usr/share/tesseract-ocr/5/tessdata/ckb.traineddata`
- **Windows**: `C:\tesseract\tessdata\ckb.traineddata`

## Testing Results

Initial test showed poor recognition accuracy, which is expected with 79% error rate. Extended training should improve this significantly.

## Usage

```bash
# In WSL
tesseract image.tif output -l ckb --psm 6

# In Windows (if Tesseract installed)
tesseract image.tif output -l ckb
```

## Files Created During Process

1. `work/train_with_best_model.sh` - Training script with best model
2. `work/finalize_model.sh` - Model finalization script
3. `work/continue_training.sh` - Extended training script
4. `work/TODO.md` - Progress tracker
5. Various training lists and log files in `work/output/`

## Next Steps

- Wait for extended training to complete (2000 iterations)
- Test improved model accuracy
- Consider further training if accuracy is still insufficient
- Document final results
