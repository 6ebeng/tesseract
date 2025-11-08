# Training Data Generation Improvements for Better Accuracy

**Created:** November 2, 2025  
**Goal:** Improve OCR accuracy through better training data generation (multi-scale + augmentation)  
**Expected Gain:** +1% to +3% accuracy on biographical text without needing new corpus sources

---

## 📊 Current Status

- **Phase 7 Result:** 71.69% accuracy on biographical text (mgk.tif)
- **Current Fonts:** 9 fonts (Noto Naskh, Noto Kufi, Noto Sans Arabic)
- **Current Generation:** Single scale (18pt, 300 DPI, 1 exposure)
- **Problem:** Limited training variety may be limiting accuracy

---

## 🎯 Improvements Implemented

### 1. **Multi-Scale Font Sizes**
- **Old:** Fixed 18pt
- **New:** 16pt, 18pt, 20pt, 22pt
- **Why:** Real documents vary in font size; training on multiple scales improves robustness

### 2. **Multi-Resolution DPI**
- **Old:** Fixed 300 DPI
- **New:** 200, 300, 400 DPI
- **Why:** 
  - 200 DPI: Old scans, low-quality sources
  - 300 DPI: Standard documents
  - 400 DPI: High-quality modern scans

### 3. **Multiple Exposures**
- **Old:** -1, 0, 1 (3 exposures)
- **New:** -2, -1, 0, 1, 2 (5 exposures)
- **Why:** Better handling of lighting variations in real documents

### 4. **Enhanced Augmentation (8 Variants)**
- **Old:** 2 basic variants (Gaussian noise + JPEG)
- **New:** 8 realistic variants:
  1. **Light blur + noise** - Common scan artifacts
  2. **JPEG compression** - Mobile camera captures
  3. **Sharpening** - Over-processed images
  4. **Slight rotation (±0.5°)** - Document skew
  5. **Darker** - Underexposed scans
  6. **Lighter** - Overexposed scans
  7. **Salt & pepper noise** - Old photocopies
  8. **Motion blur** - Camera shake
- **Why:** These are real-world conditions the model will encounter

### 5. **Parameter Variations**
- **Margins:** 10px, 15px, 20px
- **Leading (line spacing):** 18px, 22px, 26px
- **Character spacing:** 0.5, 1.0, 1.5
- **Why:** Documents vary in layout; training on variations improves layout robustness

### 6. **Additional Fonts (15+ total)**
Downloaded from Google Fonts:
- **Noto Fonts** (comprehensive coverage): Naskh, Kufi, Sans variants
- **Traditional fonts** (common in Kurdish documents): Amiri, Scheherazade, Lateef
- **Modern fonts** (contemporary texts): Cairo, Tajawal
- **Why:** More font variety = better generalization to unseen fonts

---

## 📈 Expected Training Output

### Before (Old Generation):
- 9 fonts × 3 exposures = **27 base images**
- With augmentation (2 variants): **~54 total images**

### After (Improved Generation):
- 9 fonts × 5 exposures × 4 font sizes × 3 DPIs × 3 margins × 3 leadings × 3 char spacings
- = 9 × 5 × 4 × 3 × 3 × 3 × 3 = **14,580 combinations**
- With augmentation (8 variants): **~116,640 total images** (if all combinations generated)

**Note:** Script is optimized to generate practical subset to avoid disk space issues

### With 15+ Fonts (After Font Download):
- 15+ fonts × varied parameters = **~194,400+ training images**

---

## 🚀 How to Use

### Quick Start (All-in-One):
```powershell
cd c:\tesseract
.\improve_training_generation.ps1 -All
```

### Step-by-Step:

#### Step 1: Download Additional Fonts (Optional but Recommended)
```powershell
cd c:\tesseract
.\improve_training_generation.ps1 -DownloadFonts
```
This downloads 15+ high-quality Kurdish/Arabic fonts from Google Fonts.

#### Step 2: Generate Improved Training Data
```powershell
cd c:\tesseract
.\improve_training_generation.ps1 -Generate
```
This generates multi-scale training images with augmentation.

**Expected Time:** 30-45 minutes for 9 fonts, 60-90 minutes for 15+ fonts

#### Step 3: Train Model with New Data
```powershell
cd c:\tesseract
.\run_training.ps1 -Mode GenerateTrain -LatinDigits
```
**Expected Time:** ~2 hours (fast fine-tuning)

#### Step 4: Evaluate Improvement
```powershell
cd c:\tesseract
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

---

## 📊 Expected Results

### Baseline (Phase 7):
- **mgk.tif (biographical):** 71.69% accuracy
- **News images:** 76.9% accuracy

### With Improved Generation:
- **mgk.tif (biographical):** **72.5% - 74.5%** accuracy (+1% to +3%)
- **News images:** **77.5% - 78.5%** accuracy (+0.5% to +1.5%)

### Why This Helps:
1. **Multi-scale training** improves recognition across different font sizes (mgk.tif has varied sizes)
2. **Augmentation** makes model robust to real-world scan/photo variations
3. **More fonts** improve generalization to unseen typefaces
4. **Parameter variations** improve layout handling (tight/loose spacing, margins)

---

## 🎯 When to Use This Approach

### ✅ Use This If:
- You want quick accuracy gains (1-3%) without finding new corpus sources
- Your current accuracy is 70-75% (room for data-driven improvement)
- You have limited time (2-3 hours total)
- You want to improve robustness to various scan qualities

### ❌ Don't Use This If:
- You need 5-10% accuracy gains (need better corpus - see PHASE7_COMPLETE.md)
- Your accuracy is already 85%+ (model near theoretical maximum)
- You lack disk space (improved generation uses ~2-4 GB)

---

## 🔍 Technical Details

### Files Created:
1. **generate_ckb_training_data_improved.sh** - Enhanced generation script with multi-scale
2. **download_kurdish_fonts.sh** - Font downloader from Google Fonts
3. **improve_training_generation.ps1** - PowerShell wrapper for easy execution

### Key Parameters (in improved script):
```bash
FONT_SIZE_LIST="16,18,20,22"       # 4 sizes
DPI_LIST="200,300,400"              # 3 resolutions
MARGIN_LIST="10,15,20"              # 3 margins
LEADING_LIST="18,22,26"             # 3 line spacings
CHAR_SPACING_LIST="0.5,1.0,1.5"    # 3 char spacings
EXPOSURES=(-2 -1 0 1 2)             # 5 exposures
ENABLE_AUG=1                        # Enable augmentation
AUG_VARIANTS=8                      # 8 augmentation types
```

### Augmentation Details (ImageMagick):
```bash
1. Gaussian blur + noise: -attenuate 0.015 +noise Gaussian -blur 0x0.4
2. JPEG artifacts: -quality 75 (compress then decompress)
3. Sharpening: -sharpen 0x1
4. Rotation: -rotate 0.5 (±0.5° skew)
5. Darker: -brightness-contrast -10x0
6. Lighter: -brightness-contrast 10x0
7. Salt & pepper: -attenuate 0.01 +noise Impulse
8. Motion blur: -motion-blur 0x2+45
```

---

## 💾 Disk Space Requirements

### Before (Old Generation):
- ~54 images × ~200 KB/image = **~11 MB**

### After (Improved Generation):
- 9 fonts: **~500 MB to 1 GB**
- 15 fonts: **~800 MB to 2 GB**
- Full combinations (all parameters): **~4-6 GB**

**Recommendation:** Ensure at least 5 GB free space in `c:\tesseract\work\training_output\`

---

## 🔄 Comparison with Option 2 (Find Better Corpus)

| Approach | Time Required | Expected Gain | Difficulty | Disk Space |
|----------|---------------|---------------|------------|------------|
| **Improved Generation** (This) | 2-3 hours | +1% to +3% | Easy | 2-4 GB |
| **Option 2: Better Corpus** | 2-4 weeks | +4% to +8% | Hard | ~100 MB |

### Recommendation:
1. **Do This First:** Get quick 1-3% improvement today
2. **Then Option 2:** If you need 76%+ accuracy, pursue better biographical corpus (see PHASE7_COMPLETE.md)

---

## 📝 Troubleshooting

### Issue: Font download fails
**Solution:** Manually download fonts from https://fonts.google.com/?category=Arabic

### Issue: Generation too slow (>2 hours)
**Solution:** Reduce parameter combinations:
```bash
# Edit generate_ckb_training_data_improved.sh
FONT_SIZE_LIST="18,20"              # Reduce to 2 sizes
DPI_LIST="300"                       # Single resolution
AUG_VARIANTS=4                       # Fewer augmentations
```

### Issue: Disk space full
**Solution:** Clean old training data first:
```powershell
Remove-Item "c:\tesseract\work\training_output\ground_truth\*" -Force
```

### Issue: ImageMagick not installed (augmentation fails)
**Solution:** Install in WSL:
```bash
wsl -d Ubuntu -- bash -c "sudo apt-get update && sudo apt-get install -y imagemagick"
```

---

## 📚 Related Documentation

- **PHASE7_COMPLETE.md** - Option 2 strategies for finding better corpus (4-8% improvement)
- **PHASE7_COMPLETE_GUIDE.md** - Comprehensive Phase 7 workflow
- **TRAINING_IN_PROGRESS.md** - Monitoring training progress
- **run_training.ps1** - Main training automation script

---

## ✅ Success Criteria

After implementing improved generation and retraining:
- mgk.tif accuracy improves by at least 1%
- News accuracy improves by at least 0.5%
- Model handles various scan qualities better
- Model more robust to font variations

---

## 🚀 Next Steps After Success

1. **If accuracy reaches 73-74%:** Deploy as v1.1
2. **If still below 76% target:** Pursue Option 2 (better corpus) from PHASE7_COMPLETE.md
3. **If accuracy stagnates:** Investigate corpus domain mismatch (biographical vs news)

---

**Last Updated:** November 2, 2025  
**Status:** Ready to execute  
**Expected Completion:** 2-3 hours total
