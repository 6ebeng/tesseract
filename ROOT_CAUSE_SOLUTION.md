# 🎯 ROOT CAUSE IDENTIFIED: ZWNJ Missing from Unicharset

**Date:** October 12, 2025  
**Status:** ✅ **PROBLEM DIAGNOSED** - Solution Ready

---

## 🔍 **THE SMOKING GUN**

### Diagnostic Test Results:

```
Model Unicharset: 119 characters
ZWNJ (U+200C) Present: ❌ NO
```

**CONFIRMED:** The model's character vocabulary does **NOT include ZWNJ**.

### Evidence:

1. ✅ **Training corpus** contains ZWNJ (9.46% density, 3,809 occurrences)
2. ✅ **Ground truth files** contain ZWNJ (162 out of 324 files = 50%)
3. ❌ **Model unicharset** does NOT contain ZWNJ (missing from 119-character set)
4. ❌ **OCR output** contains zero ZWNJ (model cannot output what's not in vocabulary)

---

## 💡 **Why This Happened**

### Tesseract's Unicharset Generation Process:

1. **text2image** reads training text
2. **Renders text to images** using fonts
3. **Extracts visible glyphs** from rendered images
4. **Creates unicharset** from extracted glyphs
5. **Problem:** ZWNJ is **zero-width** (invisible) - no glyph to extract!

### The Critical Flaw:

```
Input Text:    "مە‌لا"  (with ZWNJ between ە and ل)
Rendered:      "مەلا"  (ZWNJ is invisible, zero-width)
Extracted:     م + ە + ل + ا  (only visible characters)
Unicharset:    م ە ل ا  (ZWNJ never added)
```

**Result:** ZWNJ present in training text, but never makes it into the model's vocabulary because it has no visual representation.

---

## ✅ **THE SOLUTION**

### Fix: Manually Add ZWNJ to Unicharset

Tesseract LSTM training requires ZWNJ to be **explicitly added** to the unicharset as a special character.

### Step-by-Step Solution:

#### 1. **Create Custom Unicharset with ZWNJ** (Before Training)

```bash
cd /mnt/c/tesseract/work

# Extract base unicharset from Farsi model
combine_tessdata -u tessdata/best/fas.traineddata fas

# Add ZWNJ as special character
echo "‌	0	Common	0	0	0	# ZWNJ U+200C" >> fas.unicharset

# Use this unicharset in training
lstmtraining \
  --continue_from tessdata/best/fas.traineddata \
  --traineddata ckb_from_fas.traineddata \
  --unicharset fas.unicharset \
  --net_spec "[1,36,0,1 Ct3,3,16 Mp3,3 Lfys48 Lfx96 Lrx96 Lfx256 O1c`expr unicharambigs|wc -l`]" \
  --model_output output/ckb \
  --train_listfile train_list.txt \
  --max_iterations 100000
```

#### 2. **Alternative: Use Tesseract's wordlist2dawg with ZWNJ**

```bash
# Create word list with ZWNJ
cat corpus/ckb.training_text | tr ' ' '\n' | sort -u > ckb.wordlist

# Ensure ZWNJ preserved in wordlist
# Train with --wordlist flag to force ZWNJ inclusion
```

#### 3. **Quick Fix: Add ZWNJ to Existing Model** (Experimental)

```bash
# Extract unicharset
combine_tessdata -u ckb.best.traineddata ckb

# Add ZWNJ line
echo "‌	0	Common	0	0	0	# ZWNJ U+200C" >> ckb.lstm-unicharset

# Repack model
combine_tessdata -o ckb_fixed.traineddata \
  ckb.lstm \
  ckb.lstm-unicharset \
  ckb.lstm-recoder
```

**Warning:** Option 3 may not work properly without retraining the LSTM weights.

---

## 🎯 **Recommended Action Plan**

### Phase 4: Retrain with ZWNJ in Unicharset

#### Preparation (30 minutes):

1. ✅ Backup current Phase 3 model
2. ✅ Extract Farsi base unicharset
3. ✅ Add ZWNJ character to unicharset
4. ✅ Verify ZWNJ appears in unicharset

#### Training (6-8 hours):

5. ✅ Run training with custom unicharset including ZWNJ
6. ✅ Monitor training for errors
7. ✅ Verify checkpoint files being created

#### Evaluation (30 minutes):

8. ✅ Test on mgk.tif
9. ✅ Count ZWNJ in output
10. ✅ Compare accuracy vs Phase 3

### Expected Results:

**Minimum Success:**

- ZWNJ Recovery: >50% (147+ out of 294)
- Accuracy: >68% (acceptable -3pp trade-off)

**Realistic Success:**

- ZWNJ Recovery: 70-80% (206-235 out of 294)
- Accuracy: 70-72% (minimal impact)

**Best Case:**

- ZWNJ Recovery: 85-95% (250-280 out of 294)
- Accuracy: 71-73% (maintained or improved)

---

## 📋 **Implementation Checklist**

### Before Starting Phase 4:

- [ ] Read Tesseract LSTM training documentation
- [ ] Understand unicharset format
- [ ] Backup Phase 3 model and corpus
- [ ] Prepare custom unicharset with ZWNJ
- [ ] Test unicharset format is valid
- [ ] Estimate training time (6-8 hours)

### Training Commands:

```bash
# Step 1: Prepare unicharset
cd /mnt/c/tesseract/work
combine_tessdata -u tessdata/best/fas.traineddata fas_base

# Step 2: Add ZWNJ to unicharset
# Add this line to fas_base.lstm-unicharset:
# ‌	0	Common	0	0	0	# ZWNJ U+200C (Zero-Width Non-Joiner)

# Step 3: Start training with custom unicharset
./run_training.ps1 -Mode GenerateTrain -MaxIters 100000 -LatinDigits

# Note: May need to modify run_training.ps1 to pass --unicharset flag
```

### Post-Training Validation:

```bash
# Extract and verify ZWNJ in new model
combine_tessdata -u ckb_phase4.traineddata ckb_p4
grep $'\u200c' ckb_p4.lstm-unicharset
# Should output: ‌	0	Common	0	0	0	# ZWNJ U+200C

# Run OCR test
tesseract mgk.tif mgk_p4 -l ckb_phase4 --psm 6

# Count ZWNJ
python3 -c "
import sys
with open('mgk_p4.txt', 'r') as f:
    text = f.read()
    zwnj_count = text.count('\u200c')
    print(f'ZWNJ count: {zwnj_count}')
    print(f'Recovery: {zwnj_count}/294 = {zwnj_count/294*100:.1f}%')
"
```

---

## ⚙️ **Technical Details**

### Unicharset Format:

```
<char> <properties> <script> <id> <top> <bottom> # <comment>
```

**For ZWNJ:**

```
‌	0	Common	118	0	0	# ZWNJ U+200C (Zero-Width Non-Joiner)
```

- `‌` = actual ZWNJ character (U+200C)
- `0` = properties (0 = none)
- `Common` = script class (not language-specific)
- `118` = unique character ID (next available)
- `0` = top baseline (N/A for zero-width)
- `0` = bottom baseline (N/A for zero-width)

### LSTM Training Parameters:

The model must be trained with awareness that ZWNJ:

- Has no visual glyph (zero-width)
- Affects spacing/joining behavior
- Is contextual (appears between certain character pairs)

This may require:

- Custom loss function weighting
- Special handling in recoder network
- Or accept that ZWNJ is "learned" from context only

---

## 🚀 **Next Steps (In Order)**

### Today (October 12):

1. **Review this document with stakeholder**
2. **Decide**: Proceed with Phase 4 retrain?
3. **If YES**: Prepare unicharset modification
4. **If NO**: Consider rule-based post-processing instead

### Phase 4 Timeline:

- **Preparation:** 30-60 minutes (today)
- **Training:** 6-8 hours (tonight/tomorrow)
- **Evaluation:** 30 minutes (tomorrow morning)
- **Total:** ~8-10 hours wall-clock time

### Alternative (If Not Retraining):

- **Implement rule-based ZWNJ insertion** (8-12 hours)
- **Use existing Phase 3 model** (71.69% accuracy)
- **Add ZWNJ via post-processing rules**
- **Pros:** No retraining needed, faster to deploy
- **Cons:** Rules may be imperfect, requires maintenance

---

## 📊 **Cost-Benefit Analysis**

### Phase 4 Retrain:

- **Cost:** 8-10 hours (mostly unattended training)
- **Benefit:** Proper ZWNJ support, 70-80% recovery expected
- **Risk:** Low (same corpus, just added character)

### Rule-Based Approach:

- **Cost:** 8-12 hours (development + testing)
- **Benefit:** Works with existing model, no retraining
- **Risk:** Medium (rules may miss edge cases)

### Do Nothing:

- **Cost:** 0 hours
- **Benefit:** Phase 3 model works (71.69% accuracy)
- **Risk:** High (missing 294 ZWNJ = poor readability)

---

## ✅ **Recommendation**

**PROCEED WITH PHASE 4 RETRAIN**

**Rationale:**

1. ✅ Root cause identified (ZWNJ missing from unicharset)
2. ✅ Solution is straightforward (add ZWNJ to unicharset)
3. ✅ Low risk (same corpus, training process proven)
4. ✅ High reward (proper ZWNJ support, better accuracy)
5. ✅ Relatively low cost (8-10 hours, mostly unattended)

**Expected Outcome:**

- Training completes successfully
- ZWNJ appears in output
- 70-80% ZWNJ recovery achieved
- Accuracy maintained at 70-72%
- **Total accuracy with ZWNJ: 75-80% effective**

---

**Analysis Completed:** October 12, 2025  
**Status:** Ready to proceed with Phase 4  
**Estimated Completion:** October 13, 2025

---

## 🎯 **SUCCESS CRITERIA**

Phase 4 will be considered successful if:

- ✅ ZWNJ appears in model's unicharset
- ✅ ZWNJ recovery rate >50% (147+ out of 294)
- ✅ Character accuracy >68% (max -3pp from Phase 3)
- ✅ Training completes without errors

Target metrics:

- **ZWNJ Recovery:** 70-80% (206-235 ZWNJs)
- **Character Accuracy:** 70-72%
- **Overall Quality:** Significantly improved readability
