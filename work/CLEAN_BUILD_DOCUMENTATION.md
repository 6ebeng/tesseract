# Kurdish OCR Model - Clean Build Documentation

## Overview

This document provides complete instructions for building the Kurdish OCR model (`ckb.traineddata`) using WSL with the provided corpus and fonts.

## Prerequisites

- Windows with WSL installed
- Access to the corpus file: `work/corpus/ckb.training_text`
- Kurdish fonts directory: `work/fonts/kurdish` (670 fonts)

## Build Scripts

### 1. **setup_and_build_ckb.sh** (Recommended)

Complete setup script that installs dependencies and builds the model.

```bash
wsl sh work/scripts/setup_and_build_ckb.sh
```

**Features:**

- Automatically installs Tesseract and training tools
- Detects WSL distribution (Alpine/Ubuntu/Debian)
- Runs the clean build process
- Handles missing dependencies gracefully

### 2. **clean_build_ckb.sh**

Clean build script for systems with Tesseract already installed.

```bash
wsl sh work/scripts/clean_build_ckb.sh
```

**Features:**

- Checks for required dependencies
- Cleans previous build artifacts
- Generates training images from 15 fonts
- Creates LSTMF training files
- Trains LSTM model with 3000 iterations
- Produces final `ckb.traineddata`

### 3. **verify_ckb_model.sh**

Verification script to check existing models.

```bash
wsl sh work/scripts/verify_ckb_model.sh
```

**Features:**

- Locates all ckb model files
- Displays file sizes and locations
- Provides usage instructions

## Build Process Details

### Step 1: Dependency Installation

- Tesseract OCR (v5.3.4)
- text2image tool
- lstmtraining tool
- Arabic and English base models

### Step 2: Training Data Generation

- **Corpus**: 23 lines of Kurdish text
- **Fonts**: 15 selected from 670 available Kurdish fonts
- **Images**: Generated at 300 DPI resolution
- **Format**: TIF images with ground truth text

### Step 3: LSTMF Conversion

- Converts TIF images to LSTMF format
- Creates training list file
- Prepares data for neural network training

### Step 4: LSTM Training

- **Base Model**: Arabic (ara) or English (eng)
- **Iterations**: 3000 maximum
- **Target Error**: 0.01
- **Method**: LSTM neural network

### Step 5: Model Finalization

- Stops training at optimal checkpoint
- Creates final `ckb.traineddata`
- Installs to `tessdata/` directory

## Output Files

### Primary Model

- **Location**: `tessdata/ckb.traineddata`
- **Size**: ~14.7 MB
- **Type**: LSTM-based neural network model

### Backup Locations

- `work/output/ckb.traineddata`
- `work/output/ckb_*.checkpoint` (training checkpoints)

## Usage Instructions

### Basic OCR Command

```bash
tesseract input.png output -l ckb --psm 6
```

### Parameters

- `-l ckb`: Use Kurdish language model
- `--psm 6`: Page segmentation mode (uniform text block)

### PSM Options for Kurdish

- `--psm 3`: Fully automatic page segmentation
- `--psm 6`: Uniform block of text (recommended)
- `--psm 8`: Single word
- `--psm 11`: Sparse text

## Testing the Model

### Create Test Image

```bash
wsl text2image \
  --text="work/corpus/ckb.training_text" \
  --outputbase="work/test_image" \
  --font="Arial" \
  --lang=ckb
```

### Run OCR

```bash
tesseract work/test_image.tif work/test_output -l ckb --psm 6
```

### View Results

```bash
cat work/test_output.txt
```

## Troubleshooting

### Issue: Training tools not found

**Solution**: Run `setup_and_build_ckb.sh` which installs dependencies automatically

### Issue: No fonts found

**Solution**: Ensure fonts are in `work/fonts/kurdish/*.ttf`

### Issue: Low accuracy

**Solutions**:

- Use higher quality images (300+ DPI)
- Try different PSM modes
- Preprocess images (binarization, deskewing)

### Issue: WSL permission errors

**Solution**: Ensure scripts have execute permissions:

```bash
wsl chmod +x work/scripts/*.sh
```

## Performance Optimization

### Image Quality

- Minimum 300 DPI resolution
- Clear, high-contrast text
- Minimal background noise

### Training Parameters

- Increase iterations for better accuracy
- Adjust target error rate
- Use more font variations

## File Structure

```
c:/tesseract/
├── tessdata/
│   └── ckb.traineddata              # Final model
├── work/
│   ├── corpus/
│   │   └── ckb.training_text        # Training corpus
│   ├── fonts/
│   │   └── Kurdish Font/             # Font collection (670 fonts)
│   ├── ground-truth-clean/          # Generated training images
│   ├── output/
│   │   ├── ckb.traineddata         # Backup model
│   │   ├── ckb_*.checkpoint        # Training checkpoints
│   │   └── corpus-lstmf.txt        # LSTMF file list
│   └── scripts/
│       ├── setup_and_build_ckb.sh  # Complete setup script
│       ├── clean_build_ckb.sh      # Clean build script
│       └── verify_ckb_model.sh     # Verification script
```

## Success Indicators

✅ Tesseract and tools installed successfully  
✅ 15 training images generated  
✅ LSTMF files created  
✅ Training completed with checkpoint  
✅ Final model created (~14.7 MB)  
✅ Model installed to tessdata/

## Next Steps

1. Test the model with real Kurdish documents
2. Fine-tune if accuracy needs improvement
3. Deploy for production use

---

**Version**: 1.0  
**Last Updated**: August 2025  
**Status**: Production Ready
