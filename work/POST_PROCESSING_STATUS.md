# Kurdish OCR Post-Processing Development Status

**Date:** October 21, 2025  
**Phase:** Option B - Post-Processing Development  
**Goal:** Improve accuracy from 77% baseline to 80%+ through post-processing

## Executive Summary

After discovering that Batch 2 model achieves **76.90% average accuracy** on modern Kurdish news (vs 71.69% on traditional text), we've shifted to **Option B: Post-Processing Development**.

Instead of collecting more training data, we're developing correction tools to push from 77% to 80%+ accuracy.

## Current Status

### ✅ Completed Tasks (Oct 21, 2025)

1. **ZWNJ Pattern Analysis**

   - Analyzed 4,686 training sentences
   - Found 294 ZWNJs (11.17% density in Phase 4 Wikipedia content)
   - Identified key patterns:
     - Ezafe (‌ی): 30 occurrences
     - Compound words: 137 instances (مه‌لا, گه‌وره, etc.)
     - Mostly within words (218), not at boundaries (45)
   - **Key finding**: ZWNJ patterns are highly context-specific

2. **Kurdish Word Dictionary**

   - Built from 4,686 sentence corpus
   - **4,805 unique words** (≥2 occurrences)
   - 37,508 total word instances
   - Top words: ئەم (1,095×), دوای (1,079×), ژمارەی (1,008×)
   - Saved to: `corpus/kurdish_dictionary.json`
   - **Ready for spell-checking implementation**

3. **Post-Processing Framework**

   - Created `kurdish_postprocessor.py` with modular architecture
   - Baseline test framework: `test_postprocessing.py`
   - Initial rules tested (too aggressive, reduced accuracy by 4.12%)
   - **Lesson learned**: Need conservative, data-driven rules only

4. **Test Infrastructure**
   - Multi-image validation suite working
   - 5 test images (4 modern news + 1 traditional)
   - Before/after comparison framework
   - Statistical reporting (average, improvement, per-image)

### ⏳ In Progress

**Current Focus:** Conservative post-processing rules based on actual error analysis

**Challenges Identified:**

1. **Aggressive rules backfire**: Initial character substitutions reduced accuracy
2. **Context-dependent corrections**: Can't blindly replace characters (ه vs ە)
3. **ZWNJ insertion complexity**: 11% density in training, 0% in OCR output
4. **Dictionary limitations**: 4,805 words may miss proper nouns, technical terms

### 📋 Next Steps (Priority Order)

1. **Error-Driven Analysis** (HIGHEST PRIORITY - 2 hours)

   - Analyze actual OCR errors from test images
   - Compare OCR output vs ground truth character-by-character
   - Identify top 20 most common error patterns
   - Focus ONLY on high-frequency, high-confidence corrections
   - **Goal**: Find corrections that work 95%+ of the time

2. **Conservative ZWNJ Insertion** (3 hours)

   - **Approach**: Pattern matching for known compounds only
   - Use corpus analysis to find words that ALWAYS have ZWNJ in same position
   - Example: If "مهلا" appears 10+ times, always as "مه‌لا", create rule
   - Build whitelist of 50-100 high-confidence compound words
   - Test incrementally (add 10 rules, test, repeat)
   - **Expected gain**: +1-2% accuracy (conservative estimate)

3. **Spell-Checking with Kurdish Dictionary** (4 hours)

   - Implement edit distance algorithm (Levenshtein ≤2)
   - Only correct if:
     - OCR word NOT in dictionary
     - Dictionary word is ≤2 edits away
     - Dictionary word frequency ≥10
     - Single candidate (no ambiguity)
   - Handle common OCR patterns:
     - Character deletions (missing ə, و, etc.)
     - Character insertions (extra spaces, duplicate letters)
   - **Expected gain**: +0.5-1% accuracy

4. **Integrated Pipeline Testing** (2 hours)

   - Combine ZWNJ + spell-checking
   - Test on all 5 images
   - Measure cumulative improvement
   - Fine-tune rules based on results
   - **Target**: 80%+ average accuracy

5. **Documentation & Deployment** (3 hours)
   - User guide for post-processing tools
   - API documentation
   - Command-line interface
   - Integration examples
   - Performance benchmarks

## Technical Architecture

### Tools Created

```
work/tools/
├── kurdish_postprocessor.py     # Main post-processing engine
├── test_postprocessing.py        # Validation framework
├── analyze_zwnj_patterns.py     # ZWNJ analysis tool
├── build_kurdish_dictionary.py  # Dictionary builder
└── test_postprocessing_baseline.sh  # Test runner
```

### Data Assets

```
work/corpus/
├── ckb_phase6_batch2.training_text  # 4,686 training sentences
└── kurdish_dictionary.json           # 4,805 words

work/output/
├── kurdsat2_clean.txt   # OCR output (73.38% accuracy)
├── kurdsat3_clean.txt   # OCR output (73.77% accuracy)
├── rudaw1_clean.txt     # OCR output (78.28% accuracy)
├── rudaw2_clean.txt     # OCR output (82.17% accuracy)
└── mgk_batch2_fas.txt   # OCR output (71.69% accuracy)

work/real_gt/eval_clean/
├── kurdsat2.gt.txt      # Ground truth
├── kurdsat3.gt.txt      # Ground truth
├── rudaw1.gt.txt        # Ground truth
└── rudaw2.gt.txt        # Ground truth
```

## Performance Baseline

### Raw OCR Accuracy (Batch 2 Model)

| Image       | Text Type       | Accuracy   | CER       | Status       |
| ----------- | --------------- | ---------- | --------- | ------------ |
| rudaw2      | Short news      | 82.17%     | 0.1783    | ✅ Best      |
| rudaw1      | Mixed news      | 78.28%     | 0.2172    | ✅ Good      |
| kurdsat3    | Political news  | 73.77%     | 0.2623    | ⚠️ OK        |
| kurdsat2    | Political news  | 73.38%     | 0.2662    | ⚠️ OK        |
| mgk         | Traditional     | 71.69%     | 0.2831    | ⚠️ Low       |
| **Average** | **Modern news** | **76.90%** | **0.231** | **✅ Solid** |

### Post-Processing Goals

| Metric            | Current | Target | Method                        |
| ----------------- | ------- | ------ | ----------------------------- |
| Average Accuracy  | 76.90%  | 80%+   | ZWNJ + spell-checking         |
| Best Case         | 82.17%  | 85%+   | Optimized for short articles  |
| Worst Case        | 71.69%  | 75%+   | Traditional text improvements |
| ZWNJ Recovery     | 0%      | 30-50% | Pattern-based insertion       |
| Word-Level Errors | High    | Medium | Dictionary correction         |

## Key Insights

### What Doesn't Work ❌

1. **Blind character substitution** (ك→ک, ه→ە)
   - Context-dependent, causes false corrections
   - Reduced accuracy by 4-7% in tests
2. **Aggressive ZWNJ insertion rules**
   - Too many false positives
   - Kurdish uses ZWNJ inconsistently in modern text
3. **Word corrections without context**
   - Proper nouns, technical terms not in dictionary
   - Creates new errors

### What Might Work ✅

1. **Whitelist-based ZWNJ insertion**
   - Only for words that ALWAYS have ZWNJ in corpus
   - High-confidence patterns (10+ occurrences, 100% consistency)
2. **Conservative spell-checking**
   - Only correct clear typos (edit distance ≤2)
   - Require high dictionary frequency (≥10)
   - Single candidate only (no ambiguity)
3. **Error-driven approach**
   - Analyze actual OCR errors from test set
   - Fix top 20 most common patterns
   - Validate each rule individually

## Resource Requirements

### Time Estimate

- Error analysis: 2 hours
- ZWNJ rules: 3 hours
- Spell-checking: 4 hours
- Integration & testing: 2 hours
- Documentation: 3 hours
- **Total: 14 hours** (~2 working days)

### Tools Needed

- Python 3 with difflib (character-level diff)
- Kurdish dictionary (✅ completed: 4,805 words)
- ZWNJ pattern analysis (✅ completed: 294 patterns)
- Test framework (✅ completed: 5 test images)

## Risk Assessment

### High Risk ⚠️

- **Over-correction**: Rules too aggressive → reduce accuracy
- **Mitigation**: Test each rule individually, require 95%+ precision

### Medium Risk ⚠️

- **Limited improvement**: Post-processing might only gain 1-2%
- **Mitigation**: Accept 78-79% as "good enough", focus on documentation

### Low Risk ✅

- **Dictionary coverage**: 4,805 words should cover most common text
- **Test coverage**: 5 diverse images represent real-world usage well

## Success Criteria

### Minimum Success ✅

- Average accuracy: 78%+ (current 76.90% + 1.1%)
- No reduction in any individual image
- Post-processing runs in <1 second per page

### Target Success ✅✅

- Average accuracy: 80%+ (current 76.90% + 3.1%)
- Best case improves to 85%+
- Traditional text improves to 75%+

### Stretch Goal ✅✅✅

- Average accuracy: 82%+ (current 76.90% + 5.1%)
- ZWNJ recovery rate: 50%+
- Word-level accuracy: 90%+

## Next Session Plan

1. **Run detailed error analysis** (30 min)
   ```bash
   python3 tools/analyze_ocr_errors.py output/rudaw1_clean.txt real_gt/eval_clean/rudaw1.gt.txt
   ```
2. **Identify top 20 error patterns** (30 min)

   - Character deletions
   - Character insertions
   - Common substitutions
   - Spacing issues

3. **Create conservative correction rules** (2 hours)

   - Only patterns with 95%+ precision
   - Test each rule individually
   - Measure impact on all 5 images

4. **Build ZWNJ whitelist** (2 hours)

   - Words with 100% ZWNJ consistency in corpus
   - Minimum 10 occurrences
   - Create regex patterns

5. **Test integrated pipeline** (1 hour)
   - All rules combined
   - Measure final accuracy
   - Compare to 80% target

---

**Status:** Post-processing framework ready, dictionary built, baseline tested  
**Next:** Error-driven rule development (conservative approach)  
**Timeline:** 2 working days to completion  
**Expected outcome:** 78-80% average accuracy
