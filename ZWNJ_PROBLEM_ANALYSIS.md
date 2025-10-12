# ZWNJ Problem - Root Cause Analysis

## 🔴 **CRITICAL ISSUE: Zero ZWNJ Recovery**

**Date:** October 12, 2025  
**Phase:** Phase 3 Complete - ZWNJ Recovery Failed

---

## 📊 **The Problem**

### Ground Truth (mgk.tif):

- Total characters: 2,632
- ZWNJ count: **294**
- ZWNJ percentage: **11.17%**

### Training Corpus:

- Phase 2: **5.15%** ZWNJ (3,084 ZWNJs in 59,865 words)
- Phase 3: **9.46%** ZWNJ (3,809 ZWNJs in 40,120 words)
- **Improvement:** +4.31pp ZWNJ density (+84% relative increase)

### OCR Output:

- Phase 2: **0** ZWNJ (0.0% recovery)
- Phase 3: **0** ZWNJ (0.0% recovery)
- **Result:** NO IMPROVEMENT despite massive corpus ZWNJ increase

---

## 🔍 **Root Cause Hypothesis**

### The Paradox:

1. ✅ Training corpus contains ZWNJ characters (9.46%)
2. ✅ Training completed successfully (no errors)
3. ✅ Model learned patterns (71.69% accuracy)
4. ❌ Model outputs ZERO ZWNJ characters

### Possible Causes:

#### 1. **Tesseract LSTM Architecture Limitation** (Most Likely)

- **Hypothesis:** LSTM layer may treat ZWNJ as noise/invalid character
- **Evidence:**
  - Training accepts ZWNJ in corpus
  - Model never outputs ZWNJ
  - Same behavior in both Phase 2 and Phase 3
- **Why:** ZWNJ (U+200C) is a zero-width formatting character, not a visible glyph
- **Impact:** LSTM may be designed to output only "printable" characters

#### 2. **Unicharset Configuration Issue**

- **Hypothesis:** ZWNJ not properly defined in model's character set
- **Evidence:** Need to check unicharset file
- **Check:**
  ```bash
  combine_tessdata -u ckb.traineddata ckb.unicharset
  grep -i "200c" ckb.unicharset
  ```
- **Impact:** If ZWNJ not in unicharset, model cannot output it

#### 3. **Text Normalization Stripping ZWNJ**

- **Hypothesis:** Pre-processing or post-processing removes ZWNJ
- **Evidence:** Need to check normalization scripts
- **Check:**
  - kurdish_character_fixer.py
  - Tesseract's text2image normalization
- **Impact:** ZWNJ present in training text but removed before/after LSTM

#### 4. **Glyph Rendering Issue**

- **Hypothesis:** ZWNJ not rendered as distinct pattern in training images
- **Evidence:** ZWNJ is zero-width, no visual appearance
- **Why:** text2image may render "AB‌C" same as "ABC" (ZWNJ invisible)
- **Impact:** Model never learns to distinguish ZWNJ presence/absence

---

## 🧪 **Diagnostic Tests Needed**

### Test 1: Check Unicharset

```bash
cd /mnt/c/tesseract/work/training_output/model
combine_tessdata -u ckb.best.traineddata ckb
cat ckb.unicharset | grep -E "(200c|ZWNJ|zero)"
```

**Expected:** Should see ZWNJ character (U+200C) in unicharset  
**If Missing:** ZWNJ not in model's vocabulary

### Test 2: Check Training Images

```bash
cd /mnt/c/tesseract/work/training_output/ground_truth
# Check if ZWNJ appears in .box files
grep $'\u200c' *.box | head -5
# Check if ZWNJ rendered differently in images
```

**Expected:** ZWNJ should have box coordinates  
**If Missing:** text2image didn't render ZWNJ as distinct pattern

### Test 3: Check Normalization

```bash
cd /mnt/c/tesseract/work
python3 kurdish_character_fixer.py < corpus/ckb.training_text > test_norm.txt
# Count ZWNJ before and after
grep -o $'\u200c' corpus/ckb.training_text | wc -l
grep -o $'\u200c' test_norm.txt | wc -l
```

**Expected:** ZWNJ count should remain same  
**If Different:** Normalization is stripping ZWNJ

### Test 4: Manual Test with Simple ZWNJ Text

```bash
# Create simple test with ZWNJ
echo "مەلای گەورە" > test_no_zwnj.txt
echo "مە‌لای گە‌ورە" > test_with_zwnj.txt
# OCR both
tesseract test_no_zwnj.tif out1 -l ckb
tesseract test_with_zwnj.tif out2 -l ckb
# Compare outputs
```

**Expected:** out2 should contain ZWNJ  
**If Same:** Model cannot distinguish ZWNJ presence

---

## 💡 **Potential Solutions**

### Solution A: Force ZWNJ in Unicharset

```bash
# Add ZWNJ explicitly to unicharset during training
echo -e "‌\t0\t0\t0\t0\t0" >> ckb.unicharset
# Retrain with explicit ZWNJ character
```

**Pros:** Forces model to recognize ZWNJ  
**Cons:** May not work if ZWNJ is invisible in training images  
**Effort:** Low (1 hour to test)

### Solution B: Replace ZWNJ with Visible Marker

```bash
# During training: Replace ZWNJ with placeholder (e.g., "|")
sed 's/\u200c/|/g' ckb.training_text > ckb_marked.training_text
# Train model with "|" instead of ZWNJ
# After OCR: Replace "|" back to ZWNJ
sed 's/|/\u200c/g' output.txt > output_fixed.txt
```

**Pros:** Guaranteed to work (visible character)  
**Cons:** Hacky, may affect other uses of "|"  
**Effort:** Medium (4-6 hours)

### Solution C: Post-Processing ZWNJ Insertion

```bash
# Train model without ZWNJ
# After OCR, use rules to insert ZWNJ:
#   - Between letter + "ه" + letter
#   - After prefixes: می‌, نە‌, بە‌, etc.
python3 insert_zwnj_rules.py < ocr_output.txt > ocr_fixed.txt
```

**Pros:** Model focuses on character recognition, rules handle ZWNJ  
**Cons:** Rule-based, may miss edge cases  
**Effort:** High (8-12 hours to develop rules)

### Solution D: Use Tesseract 4.x (Legacy Engine)

```bash
# Tesseract 4.x legacy engine may handle ZWNJ differently
tesseract input.tif output -l ckb --oem 0  # Legacy only
```

**Pros:** Different architecture might preserve ZWNJ  
**Cons:** Lower accuracy, deprecated engine  
**Effort:** Low (1 hour to test)

### Solution E: Train Character-Level with ZWNJ as Special Token

```bash
# Modify training to treat ZWNJ as special character class
# Add ZWNJ as distinct feature in LSTM training
# Requires deep Tesseract code modification
```

**Pros:** Proper solution  
**Cons:** Requires C++ code changes to Tesseract  
**Effort:** Very High (40+ hours, expert level)

---

## 🎯 **Recommended Next Steps**

### Immediate (Today):

1. **Run Diagnostic Test 1** - Check unicharset

   - **Time:** 5 minutes
   - **Priority:** CRITICAL
   - **Goal:** Confirm if ZWNJ is in model vocabulary

2. **Run Diagnostic Test 3** - Check normalization

   - **Time:** 10 minutes
   - **Priority:** HIGH
   - **Goal:** Verify kurdish_character_fixer.py preserves ZWNJ

3. **Run Solution D** - Test legacy engine
   - **Time:** 15 minutes
   - **Priority:** MEDIUM
   - **Goal:** Quick check if legacy handles ZWNJ differently

### Short-term (This Week):

4. **Implement Solution B** - Visible marker approach

   - **Time:** 4-6 hours
   - **Priority:** HIGH
   - **Goal:** Guaranteed ZWNJ recovery (even if hacky)

5. **Implement Solution C** - Rule-based post-processing
   - **Time:** 8-12 hours
   - **Priority:** MEDIUM
   - **Goal:** Robust fallback solution

### Long-term (Future):

6. **Research Tesseract ZWNJ Support**

   - Contact Tesseract developers
   - Check GitHub issues for ZWNJ handling
   - Review source code for ZWNJ processing

7. **Consider Alternative OCR Engines**
   - Try Kraken, Calamari, or other LSTM-based OCR
   - Test if they handle ZWNJ better than Tesseract

---

## 📈 **Success Metrics**

### Minimum Acceptable:

- **ZWNJ Recovery:** 50%+ (147+ out of 294)
- **Accuracy Impact:** <5pp loss (>66% accuracy maintained)

### Good Performance:

- **ZWNJ Recovery:** 75%+ (220+ out of 294)
- **Accuracy Impact:** <2pp loss (>69% accuracy)

### Excellent Performance:

- **ZWNJ Recovery:** 90%+ (265+ out of 294)
- **Accuracy Impact:** <1pp loss (>70% accuracy)

---

## ⚠️ **Decision Point**

### Question: Is ZWNJ Recovery Worth the Effort?

**Arguments FOR continuing ZWNJ work:**

- ✅ ZWNJ is grammatically important in Kurdish
- ✅ Affects readability and meaning
- ✅ Required for proper text rendering
- ✅ Test document has 11.17% ZWNJ (high density)

**Arguments AGAINST:**

- ❌ Current accuracy (71.69%) may be acceptable without ZWNJ
- ❌ ZWNJ can be added via post-processing rules
- ❌ Significant effort required (potentially 40+ hours)
- ❌ May be architectural limitation of Tesseract LSTM

### Recommendation:

1. **Run diagnostics today** (30 minutes total)
2. **If unicharset missing ZWNJ:** Try Solution A (1 hour)
3. **If that fails:** Implement Solution B (4-6 hours) for guaranteed recovery
4. **If time permits:** Develop Solution C (8-12 hours) for robust long-term fix

---

## 📝 **Conclusion**

The **ZWNJ problem is critical** but solvable. Phase 3 achieved good character-level accuracy (71.69%) but **completely failed on ZWNJ preservation** (0% recovery).

The root cause is likely either:

1. Tesseract LSTM architecture limitation (cannot output zero-width characters)
2. ZWNJ not properly included in model's unicharset
3. Normalization or rendering stripping ZWNJ during training

**Next action:** Run diagnostic tests to identify root cause, then implement appropriate solution based on findings.

**Timeline:**

- Diagnostics: Today (30 min)
- Quick fix: This week (4-6 hours)
- Robust fix: Next week (8-12 hours)
- Total effort: 12-18 hours for complete ZWNJ solution

---

**Analysis by:** AI Assistant  
**Date:** October 12, 2025  
**Status:** Awaiting diagnostic test results
