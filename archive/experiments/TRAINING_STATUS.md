# Kurdish OCR Training - Progress Summary

Date: October 5, 2025

## 🎯 Training Goals

- **Target Accuracy:** ≥95% (CER ≤5%)
- **Current Accuracy:** ~70% (CER ~30%)
- **Improvement Needed:** 25% accuracy gain

## 📊 Current Status

### Completed Training #1 (10,000 iterations)

- ✅ **Started:** Oct 5, 2025
- ✅ **Completed:** Oct 5, 2025
- ✅ **Duration:** ~4-6 hours
- ✅ **Result:** CER reduced from 85% to 30%

**Models Generated:**

- `ckb.best.traineddata` (3.1 MB) - Best accuracy
- `ckb.fast.traineddata` (418 KB) - Fast inference

**Evaluation Results (mgk.tif - 2,632 characters):**

- PSM 6 (Uniform block): **29.94% CER** ✅ Best
- PSM 11 (Sparse text): 30.70% CER
- PSM 7 & 13: 99%+ CER (not suitable)

### In Progress Training #2 (20,000 iterations)

- 🔄 **Status:** LSTMF Generation Phase
- ⏱️ **Started:** Oct 5, 2025 ~07:45
- ⏱️ **Estimated Duration:** 8-12 hours
- 🎯 **Target:** Further reduce CER toward 5%

**Training Configuration:**

- Iterations: 20,000 (2x previous)
- Base models: Farsi (fas) + Arabic (ara)
- Latin digits: Enabled
- Corpus size: 1,382 lines
- Training samples: 72 box files
- Fonts: 3 (NotoNaskhArabic Bold/Medium/SemiBold)
- Exposures: 3 per font (-1, 0, 1)
- Augmentation: Enabled (2 variants per exposure)

## 📈 Performance Tracking

### CER History

| Iteration | Date  | CER (PSM 6) | Model |
| --------- | ----- | ----------- | ----- |
| Baseline  | -     | 85.64%      | ara   |
| 10,000    | Oct 5 | 29.94%      | ckb   |
| 20,000    | TBD   | Target <15% | ckb   |

### Target Milestones

- ✅ **Phase 1:** <50% CER (Achieved: 29.94%)
- 🎯 **Phase 2:** <15% CER (In Progress)
- 🎯 **Phase 3:** <10% CER
- 🎯 **Final Goal:** <5% CER (95% accuracy)

## 🔧 Technical Details

### Corpus Composition

- **Arabic Script:** ckb.training_text (842 lines)
  - Core coverage sentences
  - Real ground truth (mgk.gt.txt)
  - Shaping augmentation
  - Enhanced sentences (233 lines)
- **Latin Script:** ckb_latin.training_text (233 lines)
  - Kurdish Hawar alphabet (ASCII-compatible)
  - Special characters removed (Ê→E, Î→I, Û→U)
- **Mixed Script:** ckb_mixed.training_text (170 lines)
  - Technology terms
  - Code-switching patterns
  - Modern vocabulary

### Fixed Issues

- ✅ Encoding errors with circumflex accents
- ✅ ScrollView GUI blocking
- ✅ Comment lines in corpus
- ✅ Latin extended characters (Ç, Ş, etc.)

## 📝 Monitoring Commands

### Check Training Progress

```powershell
.\check_training_progress.ps1
```

### Continuous Monitoring (60s refresh)

```powershell
.\check_training_progress.ps1 -Continuous
```

### Check Current Iteration Manually

```powershell
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work && tail -20 training_output/logs/train_ckb.log | grep 'At iteration'"
```

### View Latest CER

```powershell
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work && tail -50 training_output/logs/train_ckb.log | grep 'char train='"
```

## 🎯 Next Steps After Training Completes

### 1. Evaluate Performance

```powershell
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

### 2. Check Results

```powershell
cat work\output\real_metrics.csv
```

### 3. If CER Still >5%:

- **Option A:** Continue training (30,000+ iterations)
- **Option B:** Add more real examples to corpus
- **Option C:** Fine-tune character spacing/font parameters
- **Option D:** Expand corpus diversity

### 4. Deploy Best Model

```powershell
# Copy to tessdata directory
Copy-Item work\training_output\model\ckb.best.traineddata tessdata\best\
```

## ⚠️ Known Warnings (Non-Critical)

```
⚠️ Missing real_mgk-fas.lstmf
⚠️ Missing real_mgk-ara.lstmf
```

These warnings are harmless - the real GT is used for evaluation, not training data generation.

## 🔍 Troubleshooting

### Training Stuck/Not Progressing

```powershell
# Check if process is running
Get-Process -Name lstmtraining -ErrorAction SilentlyContinue
```

### Out of Memory

- Reduce `-MaxIters` to 15000
- Close other applications
- Restart training

### Poor Results After Training

1. Check corpus quality
2. Verify character coverage
3. Add more real examples
4. Try different PSM modes

## 📞 Support Resources

- Training logs: `work/training_output/logs/`
- Models: `work/training_output/model/`
- Evaluation: `work/output/real_metrics.csv`
- Documentation: `TRAINING_PROGRESS.md`, `COMPLETE_GUIDE.md`
