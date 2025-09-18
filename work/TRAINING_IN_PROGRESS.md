# Kurdish OCR Training - Currently Running

## Status: IN PROGRESS 🔄

### Current Phase: Data Preparation

The system is currently generating training data from your Kurdish fonts and corpus text.

## What's Happening:

### Phase 1: Data Preparation (Current)

- ✅ Prerequisites checked successfully
- ✅ Found 670 fonts (all fonts in work/fonts/)
- ✅ Corpus file loaded (work/corpus/ckb.training_text)
- 🔄 Generating training text files
- ⏳ Will generate training images with each font
- ⏳ Will create LSTMF files for training

### Phase 2: Model Training (Upcoming)

- Will train for 2000 iterations
- Target error rate: 0.01 (1%)
- Using English base model for transfer learning

### Phase 3: Model Finalization (Upcoming)

- Will create final traineddata file
- Output: ckb_custom.traineddata

### Phase 4: Installation (Upcoming)

- Will install to WSL and Windows directories

### Phase 5: Testing (Upcoming)

- Will test the model with sample text

## Training Parameters:

- **Iterations**: 2000
- **Target Error Rate**: 0.01
- **Fonts Used**: 670 fonts
- **Base Model**: eng.traineddata
- **Output Model**: ckb_custom.traineddata

## Expected Duration:

- Data preparation: 10-30 minutes (depending on number of fonts)
- Training: 30-60 minutes (for 2000 iterations)
- Total: ~1-2 hours

## Files Being Generated:

- Training images: `work/ground-truth-custom/*.tif`
- Ground truth text: `work/ground-truth-custom/*.gt.txt`
- LSTMF files: `work/ground-truth-custom/*.lstmf`
- Training list: `work/output/all-lstmf.txt`

## Final Output:

- **Model Location (WSL)**: `/usr/share/tesseract-ocr/5/tessdata/ckb_custom.traineddata`
- **Model Location (Windows)**: `C:\tesseract\tessdata\ckb_custom.traineddata`

## How to Use After Training:

```bash
# In WSL or Linux
tesseract image.tif output -l ckb_custom --psm 6

# In Windows (if Tesseract is installed)
tesseract.exe image.tif output -l ckb_custom --psm 6
```

## Notes:

- The process is using all 670 fonts found in the fonts directory
- Each font will generate training samples with the Kurdish corpus text
- The more fonts used, the better the model's ability to recognize various writing styles
- Training with 2000 iterations should provide good accuracy for Kurdish text recognition

## Monitoring:

The terminal will show progress updates:

- Font processing progress during data preparation
- Iteration count and error rate during training
- Final success message when complete

---

_This document was created while training is in progress. Check the terminal for real-time updates._
