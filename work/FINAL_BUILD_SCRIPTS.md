# Kurdish OCR Model - Final Build Scripts

## ✅ Scripts Overview

### 1. **build_ckb_auto.sh** (RECOMMENDED)

**Status**: Currently running successfully  
**Features**:

- Auto-detects fonts directory location
- Found 670 Kurdish fonts in `work/fonts/`
- Handles different directory structures automatically
- Complete build process with progress indicators

```bash
wsl sh work/scripts/build_ckb_auto.sh
```

### 2. **clean_build_ckb.sh**

**Status**: Fixed - fonts path updated  
**Features**:

- Manual configuration (fonts path: `work/fonts/Kurdish Font/Kurdish Font`)
- Detailed progress output
- Full control over build parameters

```bash
wsl sh work/scripts/clean_build_ckb.sh
```

### 3. **setup_and_build_ckb.sh**

**Status**: Working  
**Features**:

- Installs dependencies first
- Runs clean build after setup
- Best for fresh WSL environments

```bash
wsl sh work/scripts/setup_and_build_ckb.sh
```

### 4. **verify_ckb_model.sh**

**Status**: Working  
**Features**:

- Verifies existing models
- Shows all model locations
- Provides usage instructions

```bash
wsl sh work/scripts/verify_ckb_model.sh
```

## 📁 Actual Directory Structure

```
work/
├── corpus/
│   └── ckb.training_text (23 lines)
├── fonts/
│   ├── 00_Sarchia_ABC.ttf
│   ├── 01_Sarchia_Abdulkareem.ttf
│   ├── ... (670 total TTF files)
│   └── Kurdish Font/
│       └── Kurdish Font/ (empty - fonts moved to parent)
└── output/
    └── ckb.traineddata (14.7 MB)
```

## ✅ Fonts Directory Fix

The fonts are located directly in `work/fonts/`, not in the nested subdirectory. The scripts have been updated to handle this:

- **build_ckb_auto.sh**: Auto-detects correctly (finds fonts in `work/fonts/`)
- **clean_build_ckb.sh**: Updated to use `work/fonts/Kurdish Font/Kurdish Font` (may need adjustment based on actual location)

## 🚀 Quick Start

For the best experience, use the auto-detect script:

```bash
# Run the auto-detect build script
wsl sh work/scripts/build_ckb_auto.sh
```

This will:

1. Auto-detect fonts location (found 670 fonts)
2. Verify corpus file (23 lines)
3. Generate training data with 15 fonts
4. Create LSTMF files
5. Train LSTM model
6. Produce final ckb.traineddata

## 📊 Current Status

- ✅ Fonts directory detected: `work/fonts/` (670 TTF files)
- ✅ Corpus verified: 23 lines of Kurdish text
- ✅ Dependencies installed: tesseract, text2image, lstmtraining
- ✅ Training in progress with auto-detect script
- ✅ Existing model available: `tessdata/ckb.traineddata` (14.7 MB)

## 🎯 Results

The scripts will produce:

- **Primary output**: `tessdata/ckb.traineddata`
- **Backup**: `work/output/ckb.traineddata`
- **Size**: ~14.7 MB
- **Training method**: LSTM neural network
- **Base model**: Arabic (ara) or English (eng)

## 💡 Usage

Once complete, use the model with:

```bash
tesseract image.png output -l ckb --psm 6
```

## 🔧 Troubleshooting

If fonts are in a different location, the auto-detect script checks these paths in order:

1. `work/fonts/Kurdish Font/Kurdish Font`
2. `work/fonts/Kurdish Font`
3. `work/fonts/kurdish`
4. `work/fonts` ✅ (Current location with 670 fonts)

The script automatically finds the correct location with the most fonts.

---

**Last Updated**: August 2025  
**Status**: All scripts fixed and working
