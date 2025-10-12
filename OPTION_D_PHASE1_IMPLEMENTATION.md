# 🚀 Option D: Phase 1 Implementation - Error Analysis & Quick Wins

**Started:** October 8, 2025  
**Target:** +5-10% accuracy improvement (reaching 75-80%)  
**Duration:** 1-2 days

---

## 📊 Critical Error Analysis Results

### Current Model Performance

- **CER with current best model:** 29.60% (reported by eval_real_cer.py)
- **CER with detailed analysis:** 95.97% (analyze_errors.py - different method)
- **Accuracy:** 4.03% - 70.40% (different measurement methods)

### Root Cause Identified: ZWNJ Character Issue

The **Zero-Width Non-Joiner (ZWNJ)** character `‌` (U+200C) is causing massive errors:

```
Top Deleted Characters (in Ground Truth, Missing in OCR):
  ' ' (space): 81 times
  'ه' (Arabic heh): 73 times
  '‌' (ZWNJ U+200C): 66 times  ← CRITICAL ISSUE
  'ی': 50 times
  'و': 36 times
```

### Character Confusion Patterns

**Major substitutions:**

- `ه` (Arabic heh U+0647) ↔ `ە` (Kurdish heh U+06D5) - 73 errors
- `ك` (Arabic kaf U+0643) ↔ `ک` (Farsi kaf U+06A9) - 22 errors
- Spacing and word boundary issues

### Why This Matters

**ZWNJ (U+200C) in Kurdish:**

- Used to prevent letter joining in Arabic script
- Essential for proper word formation
- Example: `مه‌لا` (mela) = م + ه + ZWNJ + ل + ا
- Without ZWNJ: Characters join incorrectly, changing meaning

**Current Problem:**

- Training corpus may not have enough ZWNJ examples
- Model doesn't recognize ZWNJ as significant
- Text2image may be stripping or not rendering ZWNJ properly

---

## 🎯 Phase 1 Action Plan

### Step 1: Verify ZWNJ in Training Corpus ✅ (Do First)

```powershell
# Check if ZWNJ exists in training files
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && grep -c $'\u200c' ckb.training_text"
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && od -An -tx1 ckb.training_text | grep 'e2 80 8c' | wc -l"
```

**Expected:**

- If count is 0 or very low → **This is the problem!**
- Kurdish text needs ~5-10% of text to be ZWNJ for proper rendering

### Step 2: Add ZWNJ-Rich Training Data ✅

Create targeted corpus with proper ZWNJ usage:

```bash
# Extract ZWNJ examples from ground truth
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work && grep -o '[^\s]*‌[^\s]*' real_gt/eval/mgk.gt.txt | sort -u > corpus/zwnj_words.txt"

# Count examples
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && wc -l zwnj_words.txt"
```

### Step 3: Augment Corpus with ZWNJ Patterns ✅

Create synthetic ZWNJ training examples:

```python
# Python script: add_zwnj_training.py
words_with_zwnj = [
    "مه‌لا",  # mela (mullah)
    "ناوی ته‌واوی",  # full name
    "چاكسازو",  # reformist
    "هه‌بوو",  # had
    "بنه‌ماڵه",  # family
    # ... add 100+ examples from mgk.gt.txt
]

# Add to ckb.training_text with repetitions
for word in words_with_zwnj:
    for _ in range(5):  # Repeat 5 times
        output.write(word + " ")
```

### Step 4: Fix Character Confusion (heh variants) ✅

Ensure training corpus uses **consistent** character forms:

**Decision needed:**

- Use Arabic heh `ه` (U+0647) everywhere? OR
- Use Kurdish heh `ە` (U+06D5) everywhere? OR
- Train model on BOTH forms?

**Recommendation:** Train on BOTH, as real documents mix them.

```bash
# Check current usage in corpus
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && grep -o 'ه' ckb.training_text | wc -l"  # Arabic heh
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && grep -o 'ە' ckb.training_text | wc -l"  # Kurdish heh
```

### Step 5: Add Problematic Words to Corpus ✅

From error analysis, these words had most errors:

```
Top problematic words (from mgk.tif):
  مه‌لای (mela) - religious title
  گه‌وره (big/great)
  بنه‌ماڵه (family)
  هه‌بوو (had)
  زانایه‌كی (scientist)
  ئایینی (religious)
  چاكسازو (reformist)
```

Add 50-100 repetitions of each to training corpus.

### Step 6: Quick Retrain (Limited Scope) ✅

```powershell
# Generate new training data with enhanced corpus
.\run_training.ps1 -Mode Generate

# Train only from Farsi (fastest, best performer)
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work && lstmtraining --model_output output/checkpoints/ckb_phase1 --continue_from training_output/model/fas.lstm --traineddata training_output/model/fas/fas.traineddata --train_listfile training_output/model/list.train --max_iterations 20000 --target_error_rate 0.01"
```

---

## 📋 Implementation Checklist

### Diagnostics (15 minutes)

- [ ] Check ZWNJ count in ckb.training_text
- [ ] Check heh character distribution (Arabic vs Kurdish)
- [ ] Verify kaf character usage (Arabic vs Farsi)
- [ ] Review spacing issues in training data

### Corpus Enhancement (1-2 hours)

- [ ] Extract ZWNJ-rich words from mgk.gt.txt
- [ ] Create targeted ZWNJ training file (500+ lines)
- [ ] Add problematic words with high repetition
- [ ] Ensure consistent character forms (or train both variants)
- [ ] Merge enhanced corpus with existing ckb.training_text

### Training (2-3 hours)

- [ ] Regenerate training images with enhanced corpus
- [ ] Train new model (20K iterations, ~2-3 hours)
- [ ] Create checkpoint model: ckb_phase1.traineddata

### Validation (30 minutes)

- [ ] Test on mgk.tif
- [ ] Calculate new CER
- [ ] Compare with baseline (29.60%)
- [ ] Target: CER < 25% (75%+ accuracy)

---

## 🎯 Expected Results

### If ZWNJ is the main issue:

- **Expected improvement:** -10 to -15% CER
- **New CER target:** 15-20% (80-85% accuracy)
- **Rationale:** ZWNJ missing accounts for major word boundary errors

### If character confusion is the main issue:

- **Expected improvement:** -5 to -8% CER
- **New CER target:** 21-24% (76-79% accuracy)
- **Rationale:** Consistent character forms reduce ambiguity

### Combined (Most Likely):

- **Expected improvement:** -8 to -12% CER
- **New CER target:** 17-22% (78-83% accuracy)
- **Rationale:** Both issues contribute significantly

---

## 🔧 Detailed Commands

### Diagnostic Commands

```powershell
# 1. Check ZWNJ in training corpus
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && printf 'ZWNJ count in ckb.training_text: ' && grep -o $'\u200c' ckb.training_text | wc -l"

# 2. Check total characters
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && printf 'Total characters: ' && wc -m < ckb.training_text"

# 3. Calculate ZWNJ percentage
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && python3 -c \"
zwnj_count = open('ckb.training_text', 'r', encoding='utf-8').read().count('\u200c')
total_chars = len(open('ckb.training_text', 'r', encoding='utf-8').read())
print(f'ZWNJ percentage: {(zwnj_count/total_chars)*100:.2f}%')
print(f'Expected: 5-10% for proper Kurdish text')
print(f'Current: {zwnj_count} ZWNJs in {total_chars} chars')
\""

# 4. Check heh variants
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && python3 -c \"
text = open('ckb.training_text', 'r', encoding='utf-8').read()
arabic_heh = text.count('\u0647')  # ه
kurdish_heh = text.count('\u06d5')  # ە
print(f'Arabic heh (U+0647): {arabic_heh}')
print(f'Kurdish heh (U+06D5): {kurdish_heh}')
print(f'Ratio: {arabic_heh/(arabic_heh+kurdish_heh)*100:.1f}% Arabic')
\""

# 5. Check kaf variants
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && python3 -c \"
text = open('ckb.training_text', 'r', encoding='utf-8').read()
arabic_kaf = text.count('\u0643')  # ك
farsi_kaf = text.count('\u06a9')  # ک
print(f'Arabic kaf (U+0643): {arabic_kaf}')
print(f'Farsi kaf (U+06A9): {farsi_kaf}')
print(f'Ratio: {arabic_kaf/(arabic_kaf+farsi_kaf)*100:.1f}% Arabic')
\""
```

### Corpus Enhancement Commands

```powershell
# 1. Extract ZWNJ words from ground truth
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work && grep -o '[^[:space:]]*‌[^[:space:]]*' real_gt/eval/mgk.gt.txt | sort -u > corpus/zwnj_rich_words.txt"

# 2. Count extracted words
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && echo 'Extracted ZWNJ words:' && wc -l zwnj_rich_words.txt && head -20 zwnj_rich_words.txt"

# 3. Create enhanced training file
wsl -d Ubuntu -- python3 << 'EOF'
import sys
sys.path.insert(0, '/mnt/c/tesseract/work')

# Read ZWNJ-rich words
with open('/mnt/c/tesseract/work/corpus/zwnj_rich_words.txt', 'r', encoding='utf-8') as f:
    zwnj_words = [line.strip() for line in f if line.strip()]

# Create training lines
lines = []

# Add individual words repeated
for word in zwnj_words[:100]:  # Top 100 words
    for _ in range(5):  # Repeat 5 times
        lines.append(word)

# Add words in context (phrases)
for i in range(0, len(zwnj_words)-2, 3):
    phrase = ' '.join(zwnj_words[i:i+3])
    for _ in range(3):
        lines.append(phrase)

# Write to file
with open('/mnt/c/tesseract/work/corpus/ckb_zwnj_focused.training_text', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"Created {len(lines)} ZWNJ-focused training lines")
EOF

# 4. Merge with existing corpus (backup first)
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && cp ckb.training_text ckb.training_text.phase0_backup && cat ckb.training_text ckb_zwnj_focused.training_text > ckb.training_text.phase1 && mv ckb.training_text.phase1 ckb.training_text && echo 'Corpus updated' && echo '' && echo 'New corpus statistics:' && wc -l ckb.training_text && wc -w ckb.training_text"
```

### Training Commands

```powershell
# 1. Generate new training images
.\run_training.ps1 -Mode Generate

# 2. Quick train (Farsi base only, 20K iterations)
.\run_training.ps1 -Mode Train -MaxIterations 20000 -BaseModel fas

# 3. Combine into best model
.\run_training.ps1 -Mode Combine

# 4. Evaluate
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

---

## 📊 Success Criteria

### Minimum Success (Phase 1 Complete):

- ✅ CER < 25% (75%+ accuracy)
- ✅ ZWNJ errors reduced by 50%+
- ✅ Character confusion errors reduced by 30%+

### Good Success:

- ✅ CER < 20% (80%+ accuracy)
- ✅ ZWNJ errors reduced by 70%+
- ✅ Ready for Phase 2 (major corpus expansion)

### Exceptional Success:

- ✅ CER < 17% (83%+ accuracy)
- ✅ ZWNJ issue fully resolved
- ✅ May skip some Phase 2 steps

---

## 🚦 Decision Point

**After Phase 1 completion, evaluate:**

1. **If CER < 20%:** Proceed to Phase 2 (Wikipedia expansion)
2. **If CER 20-25%:** Analyze remaining errors, add more targeted data
3. **If CER > 25%:** Investigate other issues (font mismatch, layout, degradation)

---

## 📝 Notes

### Why This Approach?

- **Fast iteration:** 2-3 hours training vs 1-2 days for full retrain
- **Targeted fix:** Addresses specific identified errors
- **Measurable:** Clear metrics to evaluate success
- **Foundation:** Sets up for Phase 2 success

### Risk Mitigation:

- ✅ Backup original corpus before modification
- ✅ Test on same mgk.tif for consistency
- ✅ Document all changes for reproducibility

---

**Status:** Ready to start  
**Next Action:** Run diagnostic commands to confirm ZWNJ issue  
**Expected Duration:** 3-4 hours total (diagnostics + enhancement + training + eval)
