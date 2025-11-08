# Quick Reference - Improved Training Generation

## One Command to Rule Them All 🚀

```powershell
cd c:\tesseract
.\run_training.ps1 -Mode ImprovedGenerateTrain -LatinDigits
```

**What it does:**
1. Downloads 15+ Kurdish/Arabic fonts (if needed)
2. Generates multi-scale training data with augmentation
3. Trains the model automatically
4. Quick smoke test evaluation

**Time:** 2-3 hours total  
**Expected gain:** +1% to +3% accuracy

---

## Why This Improves Accuracy

| Feature | Before | After | Benefit |
|---------|--------|-------|---------|
| Font sizes | 18pt only | 16,18,20,22pt | Handles varied text sizes |
| DPI | 300 only | 200,300,400 | Robust to scan quality |
| Exposures | 3 | 5 | Better lighting variations |
| Augmentation | 2 variants | 8 variants | Real-world robustness |
| Fonts | 9 | 15+ | Better generalization |

---

## Commands (Now Integrated into run_training.ps1!)

### All-in-One (RECOMMENDED)
```powershell
.\run_training.ps1 -Mode ImprovedGenerateTrain -LatinDigits
```

### Download Fonts Only
```powershell
.\run_training.ps1 -Mode DownloadFonts
```

### Generate Improved Training Data Only
```powershell
.\run_training.ps1 -Mode ImprovedGenerate
```

### Train with Standard Generation (Old Method)
```powershell
.\run_training.ps1 -Mode GenerateTrain -LatinDigits
```

### Evaluate After Training
```powershell
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

---

## Expected Results

**Before:** 71.69% (mgk.tif biographical)  
**After:** 72.5-74.5% biographical (+1-3%)

**Why:**
- Multi-scale: mgk.tif has varied font sizes ✓
- Augmentation: Real scans have blur, noise, lighting issues ✓
- More fonts: Better at unseen typefaces ✓

---

## Requirements

✅ **Disk space:** 244 GB available (need ~4 GB)  
✅ **Time:** 2-3 hours  
✅ **Dependencies:** All installed (WSL, ImageMagick, text2image)

---

## Troubleshooting

**"Font download failed"**  
→ Continue anyway, 9 fonts is enough for testing

**"Generation too slow"**  
→ Reduce parameters in `generate_ckb_training_data_improved.sh`

**"Disk space warning"**  
→ Clean old training: `Remove-Item "c:\tesseract\work\training_output\ground_truth\*" -Force`

---

## What Gets Improved

✓ **Biographical text** (mgk.tif): Primary target, expect +1-3%  
✓ **News text**: Secondary benefit, expect +0.5-1.5%  
✓ **Various scan qualities**: More robust to real-world conditions  
✓ **Different fonts**: Better generalization

---

## Next Steps After This

**If accuracy reaches 73-74%:**
- Deploy as v1.1 ✅
- Success! Model improved

**If still below 76% target:**
- See `PHASE7_COMPLETE.md` for Option 2 (better corpus)
- Expected: +4-8% gain but takes 2-4 weeks

**Recommended strategy:**
1. Do this first (2-3 hours, +1-3%)
2. If still need more, pursue Option 2

---

## Files Reference

- `IMPROVED_TRAINING_GENERATION.md` - Full documentation
- `improve_training_generation.ps1` - Easy execution wrapper
- `generate_ckb_training_data_improved.sh` - Enhanced generator
- `download_kurdish_fonts.sh` - Font downloader

---

**Last Updated:** November 2, 2025  
**Status:** ✅ Ready to execute  
**Command:** `.\improve_training_generation.ps1 -All`
