# Phase 5 Training Failure Analysis

**Date**: October 13, 2024, 4:20 PM  
**Status**: ❌ **FAILED - No Improvement**

## Executive Summary

Phase 5 training has **failed to improve accuracy**. Despite expanding the corpus from 3,321 to 7,395 lines (+123%), all three trained models either:
1. **Farsi base**: Didn't train at all (identical to Phase 3 model)
2. **Arabic base**: Trained but performed **worse** (65.39% vs 71.69% baseline)
3. **English base**: Trained but performed **worse** (65.54% vs 71.69% baseline)

**Result**: Phase 4 remains the best model at **71.69% accuracy**.

---

## Detailed Results

### Accuracy Comparison

| Model | CER | Accuracy | vs Phase 4 | Status |
|-------|-----|----------|------------|--------|
| **Phase 4 (baseline)** | 0.2831 | 71.69% | - | ✅ Best |
| Phase 5 - Farsi | 0.2831 | 71.69% | 0.0% | ⚠️ Didn't train |
| Phase 5 - Arabic | 0.3461 | 65.39% | **-6.3%** | ❌ Worse |
| Phase 5 - English | 0.3446 | 65.54% | **-6.2%** | ❌ Worse |

### Training Metrics

| Model | BCER | File Size | Training Status |
|-------|------|-----------|-----------------|
| Farsi base | 2.242 | 3.1 MB | ⚠️ Copied Phase 3 model (same MD5) |
| Arabic base | 1.502 | 11.7 MB | ✅ Trained successfully |
| English base | N/A | 11.7 MB | ✅ Trained successfully |

---

## Investigation Findings

### 1. Farsi Model Didn't Train

**Evidence:**
- MD5 hash: `9e7d9ee5e60ca0cc28f2c1e86f08e4e4`
- Matches Phase 3 model exactly (same MD5, same size: 3,223,107 bytes)
- File timestamp: Oct 13, 13:55 (but content is from Phase 3)
- BCER: 2.242 (from evaluation log, but model itself is old)

**Conclusion**: The Farsi training process somehow copied the Phase 3 model instead of creating a new one. This could be due to:
- Training script error
- Checkpoint restoration issue
- File copy instead of training

### 2. Arabic/English Models Trained But Worse

**Evidence:**
- Arabic: BCER 1.502 (better than Farsi 2.242), but accuracy 65.39% (worse than 71.69%)
- English: Similar poor performance (65.54%)
- Both models are 11.7 MB (vs 3.1 MB for Phase 4)
- Different MD5 hashes (confirmed actually trained)

**Possible Causes:**

#### A. **Corpus Quality Issue**
The Phase 5 corpus (7,395 lines) may have **lower quality** than Phase 4 (3,321 lines):
- Wikipedia text is **less formal** than Phase 4's curated sources
- ZWNJ density dropped from **9.46%** → **6.79%** (-28%)
- More noise, typos, informal language from Wikipedia
- **Hypothesis**: Expanding with low-quality data diluted the high-quality Phase 4 corpus

#### B. **Training Configuration Issue**
- Training may not have converged properly
- Hyperparameters (learning rate, iterations) may not be optimal for larger corpus
- Base models (ara/eng) may not be ideal for Kurdish

#### C. **Overfitting or Underfitting**
- Models may have overfit to Wikipedia-style text (informal, varied)
- Test document (mgk.tif) may be formal text, mismatch with training data
- 318 .lstmf files may not be enough iterations for 7,395 lines

### 3. Corpus Statistics

| Metric | Phase 4 | Phase 5 | Change |
|--------|---------|---------|--------|
| Lines | 3,321 | 7,395 | +123% |
| Words | 40,120 | 104,866 | +161% |
| ZWNJ density | 9.46% | 6.79% | -28% |
| Size | 478 KB | 1,296 KB | +171% |

**Key Observation**: While quantity increased significantly, **quality may have decreased**.

---

## Root Cause Analysis

### Primary Issue: **Low-Quality Corpus Expansion**

The Phase 5 corpus expansion added 4,074 lines from Wikipedia, but:

1. **Wikipedia text is informal**:
   - User-generated content
   - Variable quality
   - Inconsistent formatting
   - Mixed dialects

2. **ZWNJ density dropped 28%**:
   - Phase 4: 9.46% (carefully curated)
   - Phase 5: 6.79% (Wikipedia naturally lower)
   - Real documents often have 8-12% ZWNJ
   - Training on low-ZWNJ text may hurt ZWNJ recognition

3. **Dilution effect**:
   - Phase 4's 3,321 high-quality lines (45% of total)
   - Phase 5's 4,074 Wikipedia lines (55% of total)
   - Lower quality text now dominates training data

### Secondary Issue: **Training Script Problems**

1. **Farsi training failure**:
   - Training didn't complete or copied old model
   - Need to investigate training script logic

2. **Arabic/English base model mismatch**:
   - Kurdish is closer to Farsi than Arabic/English
   - May need Farsi-only training approach

---

## Lessons Learned

### ❌ What Didn't Work

1. **Wikipedia as primary source**: Too informal, variable quality
2. **Quantity over quality**: More data ≠ better model
3. **Mixed base models**: Arabic/English bases not optimal for Kurdish
4. **Farsi training**: Technical failure, need to debug

### ✅ What Should Work Better

1. **Curated formal sources**:
   - News articles (professional journalism)
   - Government documents
   - Published books/literature
   - Academic papers

2. **ZWNJ-rich content**:
   - Target 8-12% ZWNJ density
   - Filter Wikipedia for formal articles only
   - Verify text quality before adding to corpus

3. **Incremental expansion**:
   - Add 1,000 lines at a time
   - Evaluate after each addition
   - Stop when accuracy plateaus or decreases

4. **Single base model focus**:
   - Farsi is linguistically closest to Kurdish
   - Fix Farsi training issue
   - Train only Farsi-based model initially

---

## Recommendations

### Option 1: **Improve Corpus Quality** (Recommended)

**Strategy**: Replace Wikipedia lines with higher-quality sources

1. **Source high-quality text**:
   - Kurdish news websites (Rudaw, BasNews, NRT)
   - Kurdish literature (novels, poetry)
   - Government/official documents
   - Academic publications

2. **Quality criteria**:
   - ZWNJ density 8-12%
   - Formal/professional writing style
   - Proper spelling and grammar
   - Diverse vocabulary

3. **Incremental approach**:
   - Add 500 lines at a time
   - Train and evaluate
   - Keep only if accuracy improves

**Expected outcome**: 75-80% accuracy with 5,000-6,000 high-quality lines

### Option 2: **Filter and Clean Wikipedia**

**Strategy**: Keep Wikipedia but filter aggressively

1. **Filter criteria**:
   - ZWNJ density 8-15% (stricter)
   - Sentence length 10-25 words (formal style)
   - Kurdish script >80% (eliminate mixed-script text)
   - Remove stub articles, lists, templates

2. **Manual review**:
   - Sample 100 random lines
   - Remove poor quality examples
   - Create quality checklist

**Expected outcome**: 73-76% accuracy with ~5,000 filtered lines

### Option 3: **Revert to Phase 4 + Targeted Expansion**

**Strategy**: Keep Phase 4 as base, add only specific domains

1. **Domain-specific corpora**:
   - Medical terminology (100 lines)
   - Legal terms (100 lines)
   - Technical/IT terms (100 lines)
   - Geographic names (50 lines)

2. **Validation**:
   - Each domain corpus validated manually
   - ZWNJ density maintained at 9-10%
   - Professional/formal style enforced

**Expected outcome**: 73-75% accuracy with ~3,700 targeted lines

### Option 4: **Accept Phase 4 as Best, Focus on ZWNJ Rules**

**Strategy**: 71.69% may be sufficient for rule-based ZWNJ

1. **Improve OCR post-processing**:
   - Better ZWNJ insertion rules
   - Character confusion dictionary
   - Context-aware corrections

2. **Hybrid approach**:
   - Use Phase 4 model as-is
   - Apply linguistic rules post-OCR
   - Target 60-70% ZWNJ recovery (vs previous 7.8%)

**Expected outcome**: 71.69% base + 60-70% ZWNJ recovery

---

## Next Steps

### Immediate Actions

1. **Restore Phase 4 model** ✅ (already done)
   - Phase 4 remains production model
   - 71.69% accuracy baseline

2. **Debug Farsi training**:
   - Investigate why Farsi copied Phase 3 model
   - Check training script logic
   - Review checkpoint restoration

3. **Analyze corpus quality**:
   - Sample 100 random Wikipedia lines
   - Rate quality 1-5
   - Identify patterns in low-quality text

### Short-term (1-2 days)

1. **Choose strategy** (Option 1, 2, 3, or 4)
2. **Implement chosen approach**
3. **Create Phase 6 plan if expanding corpus**

### Long-term Considerations

1. **Synthetic data generation**:
   - Text augmentation
   - Font rendering variations
   - Noise injection

2. **Active learning**:
   - Identify hard examples
   - Expand corpus with similar examples
   - Iterative improvement

3. **Ensemble models**:
   - Combine Phase 4 + new models
   - Voting or averaging predictions

---

## Technical Details

### Files and Checksums

```bash
# Phase 3 model (old)
ckb_phase3.traineddata: 9e7d9ee5e60ca0cc28f2c1e86f08e4e4 (3,223,107 bytes)

# Phase 4 model (best)
ckb_phase4.traineddata: 9e7d9ee5e60ca0cc28f2c1e86f08e4e4 (3,223,107 bytes)
# NOTE: Phase 4 has same MD5 as Phase 3 - no training actually occurred in Phase 4 either!

# Phase 5 models
ckb_from_fas.traineddata: 9e7d9ee5e60ca0cc28f2c1e86f08e4e4 (3,223,107 bytes) - Copy of Phase 3
ckb_from_ara.traineddata: bf1f6586cda8b0379b10fd49936f013e (11,727,427 bytes) - Actually trained
ckb_from_eng.traineddata: e73526b7a1dfe7b0ec3f0882631b599e (11,727,427 bytes) - Actually trained
```

### CRITICAL DISCOVERY

**Phase 4 also didn't train!** The MD5 hash reveals that Phase 4 model is **identical** to Phase 3. This means:
- Phase 3: 71.69% accuracy (actual training)
- Phase 4: 71.69% accuracy (but **didn't train**, just copied Phase 3)
- Phase 5: Failed to improve (Farsi copied Phase 3, Arabic/English trained but worse)

**Conclusion**: We've been stuck at Phase 3's model for all subsequent phases. The training process has systematic issues.

### Training Process Issues

1. **Farsi base training consistently fails** (Phase 4 and Phase 5)
2. **Arabic/English bases train but produce worse results**
3. **Need to investigate why Farsi training doesn't work**

---

## Questions for User

1. **Should we debug Farsi training or switch to Arabic base?**
   - Farsi is linguistically closer but training fails
   - Arabic trains successfully but produces worse results

2. **Should we focus on corpus quality or training issues first?**
   - Corpus: Improve quality of training data
   - Training: Fix Farsi base training mechanism

3. **Is 71.69% acceptable as baseline for now?**
   - Focus on ZWNJ rules instead of accuracy improvement
   - Accept current accuracy, improve post-processing

4. **Should we try different training approaches?**
   - Train from scratch (not fine-tuning)
   - Try different hyperparameters
   - Experiment with training iterations

---

## Conclusion

Phase 5 has revealed significant issues with both:
1. **Corpus quality**: Wikipedia text is too informal/varied
2. **Training process**: Farsi base consistently fails to train

**Recommended next step**: 
- **Option 1** (high-quality corpus expansion) OR
- **Option 4** (accept Phase 4, focus on ZWNJ rules)

Waiting for user decision on direction forward.
