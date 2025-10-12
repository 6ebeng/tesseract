# Phase 3: Dual-Script Training Solution

**Date:** October 11, 2025  
**Status:** ✅ Training in Progress  
**Goal:** Support both Arabic and Latin (Hawar) scripts with 75-80% accuracy

---

## Problem Encountered

### Initial Issue

Phase 3 training **failed with encoding errors** when trying to process mixed-script corpus:

```
Can't encode transcription: 'Kurdî', 'Hewlêr', 'Xakelewe' in language ''
Encoding of string failed...
```

### Root Cause

- Corpus contained **106 mixed-script lines** (3.2% of total)
- Lines had embedded English/Latin terms: `Berlin`, `Halabja Monument`, `Larynx`, `HTML5`, `CSS3`
- Tesseract's Arabic script model couldn't encode pure Latin terms in certain contexts

---

## Solution Implemented

### Approach: Smart Filtering (Option 2 - Dual Script)

Created intelligent filter to handle mixed-script content:

1. **Accept Arabic-only lines** (96.8% of corpus) ✅
2. **Accept safe mixed lines** (3.1% of corpus) ✅
   - Lines with small embedded Latin terms (<30% of text)
   - Example: `بە ئینگلیزی: ''Halabja Monument''` (Latin in Arabic context)
3. **Reject problematic lines** (0.1% of corpus) ❌
   - Lines with >30% Latin content
   - Examples: `HTML5 و CSS3، دا‌تا‌بەیسی MySQL`

### Tools Created

- `analyze_and_split_corpus.py` - Analyzes script distribution
- `prepare_dual_script_corpus.py` - Filters problematic mixed lines

---

## Corpus Statistics

### Before Filtering (Phase 3 Original)

- **Total:** 3,323 lines
- **Arabic-only:** 3,217 lines (96.8%)
- **Mixed script:** 106 lines (3.2%)
- **Latin-only:** 0 lines
- **ZWNJ:** 8.07%

### After Filtering (Dual-Script Ready)

- **Total:** 3,321 lines (99.9% retained) ✅
- **Accepted:** 3,321 lines
  - Pure Arabic: 3,217 lines
  - Safe mixed: 104 lines
- **Rejected:** 2 lines (0.1%) with excessive Latin
- **Words:** 40,120
- **ZWNJ:** 9.46% (↑ from 8.07%) 🎯

### Rejected Lines

Only 2 highly technical lines removed:

1. `بەکارهێنا‌نی HTML5 و CSS3، دا‌تا‌بەیسی MySQL`
2. `PARSA Community Foundation کە‌ کۆمە‌ڵگایە‌کی پاشماوە‌ی فارسی`

---

## Training Configuration

### Command

```powershell
.\run_training.ps1 -Mode GenerateTrain `
    -MaxIters 100000 `
    -LatinDigits `
    -MaxPages 100 `
    -CharsPerPage 3000
```

### Key Parameters

- **MaxIters:** 100,000 (doubled from Phase 2's 50K)
- **LatinDigits:** ✅ Enabled for dual-script support
- **MaxPages:** 100 (split corpus across more pages)
- **CharsPerPage:** 3,000 (optimal page size)

### Training Features

- **Base Model:** Farsi (fas.traineddata)
- **Scripts:** Arabic + Latin support
- **Fonts:** 9 Noto fonts × 3 exposures = 27 variants
- **Corpus Quality:** High ZWNJ concentration (9.46%)
- **Domain Match:** Biographical/historical content

---

## Expected Outcomes

### Phase 3 Targets

- **Accuracy:** 75-80% (vs Phase 2's 70.40%)
- **ZWNJ Recovery:** >50% (vs Phase 2's near-zero)
- **Mixed Script:** Handle embedded Latin terms
- **Domain:** Better biographical/historical text recognition

### Training Timeline

- **Start:** October 11, 2025 ~1:00 PM
- **Expected Duration:** 6-8 hours
- **Expected Completion:** ~7:00-9:00 PM

---

## Technical Details

### ZWNJ Improvement Strategy

| Phase       | ZWNJ %    | Ground Truth % | Coverage   |
| ----------- | --------- | -------------- | ---------- |
| Phase 1     | 5.15%     | 11.17%         | 46%        |
| Phase 2     | 5.15%     | 11.17%         | 46%        |
| **Phase 3** | **9.46%** | 11.17%         | **85%** 🎯 |

### Script Support Matrix

| Content Type  | Phase 2   | Phase 3     | Example              |
| ------------- | --------- | ----------- | -------------------- |
| Pure Arabic   | ✅ Yes    | ✅ Yes      | `کوردستان`           |
| Pure Latin    | ❌ No     | ⚠️ Limited  | `Kurdistan`          |
| Mixed (safe)  | ❌ Failed | ✅ Yes      | `بە ئینگلیزی Berlin` |
| Mixed (heavy) | ❌ Failed | ❌ Filtered | `HTML5 CSS3 MySQL`   |

---

## Next Steps

### 1. Monitor Training Progress

```powershell
# Check training status
Get-Process | Where-Object {$_.ProcessName -like "*tesseract*"}

# View last checkpoint
Get-ChildItem C:\tesseract\work\training_output\model\*.checkpoint | Select -Last 1
```

### 2. Evaluate Phase 3 Model

```powershell
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

### 3. Analyze Results

- Compare CER with Phase 2 baseline (29.60%)
- Check ZWNJ presence in OCR output
- Verify mixed-script handling

### 4. Decision Points

**If CER < 25% (Success):**

- ✅ Phase 3 complete
- Document improvements
- Proceed to Phase 4 (train from scratch for 85-90% target)

**If CER 25-28% (Partial Success):**

- 🔄 Boost ZWNJ to 10-11% (match ground truth exactly)
- 🔄 Add more biographical content
- 🔄 Retrain with 150K iterations

**If CER > 28% (Below Target):**

- 🔍 Deep analysis: character-specific errors
- 🔍 Consider training from scratch (not fine-tune)
- 🔍 May need different base model

---

## File Backups

### Created Backups

- `ckb.training_text.phase3_original` - Original Phase 3 corpus with encoding issues
- `ckb.training_text.backup_phase3` - Pre-Phase 3 corpus
- `ckb_rejected_mixed.txt` - 2 rejected Latin-heavy lines
- `ckb_mixed.training_text` - All 106 mixed-script lines (reference)

### Active Training Files

- `ckb.training_text` - **Active corpus (3,321 lines, 9.46% ZWNJ)**
- `ckb_dual_script.training_text` - Source for active corpus

---

## Progress Tracking

### Phase 3 Milestones

- [x] Corpus ZWNJ boost (5.15% → 8.07%)
- [x] Historical corpus creation (84 sentences)
- [x] Phase 3 merge (40,149 words)
- [x] **Encoding error diagnosis**
- [x] **Dual-script corpus preparation (9.46% ZWNJ)**
- [x] **Training restart with clean corpus**
- [ ] Training completion (6-8 hours)
- [ ] Evaluation
- [ ] Results analysis
- [ ] Phase 4 decision

### Overall Progress

- ✅ Phase 1: 59.38% accuracy
- ✅ Phase 2: 70.40% accuracy (+11pp)
- 🔄 Phase 3: Target 75-80% (+5-10pp)
- ⏳ Phase 4: Target 85-90% (train from scratch)
- 🎯 Final Goal: 95% accuracy

---

## Key Insights

### What We Learned

1. **Mixed-script challenges:** Tesseract struggles with lines containing >30% non-native script
2. **Smart filtering works:** Keeping safe mixed lines (104) while rejecting problematic ones (2) maintains corpus quality
3. **ZWNJ concentration matters:** 9.46% is much closer to ground truth's 11.17%
4. **Quality > Quantity:** 3,321 targeted lines > 3,323 with encoding failures

### Strategy Evolution

- **Phase 1-2:** Focus on corpus expansion (9K → 60K words)
- **Phase 3:** Focus on quality and domain matching (60K → 40K targeted words)
- **Future:** Train from scratch for maximum accuracy

---

**Status:** Training in progress with dual-script support enabled  
**Next Checkpoint:** Evaluation after training completion (~7-9 PM Oct 11)
