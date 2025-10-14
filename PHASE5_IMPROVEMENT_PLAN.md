# Phase 5 Improvement Plan - Corpus Expansion

## Date: October 12, 2025

## Current State

### Phase 4 Results

- **Accuracy**: 71.69% (CER 0.2831)
- **Training BCER**: 0.195 (excellent convergence)
- **Corpus Size**: 3,321 lines
- **ZWNJ Recovery**: 0% (architectural limitation)

### Error Analysis Findings

1. **Character Recognition Issues**:

   - Missing characters (e.g., `ل` in `مهلای` → `مهای`)
   - Extra/wrong spacing
   - Character confusion (similar shapes)

2. **Root Cause**: **Insufficient training data**
   - 3,321 lines is below recommended minimum (5,000-10,000)
   - Limited character bigram/trigram coverage
   - Insufficient context for LSTM to learn patterns

## Target for Phase 5

### Goal: **85-90% Character Accuracy**

- Current: 71.69% → Target: 85-90% (+13-18 points)
- Required: Significantly larger, more diverse corpus
- Timeline: 2-3 days for corpus expansion, 1 day for training

### Success Criteria

✅ Training corpus: 10,000+ lines (3x current size)  
✅ Character accuracy: ≥85%  
✅ Diverse text sources (news, books, Wikipedia, social media)  
✅ Maintained ZWNJ density (8-10%)  
✅ Training BCER: <0.15

## Corpus Expansion Strategy

### Source 1: Wikipedia Expansion (HIGHEST PRIORITY)

**Current**: ~1,500 lines from Kurdish Wikipedia  
**Target**: 5,000-7,000 lines

**Method**:

```bash
# Extract more articles from Kurdish Wikipedia dump
- Currently using: limited article set
- Expand to: Top 500 most-viewed articles
- Categories: History, Geography, Biography, Science, Culture
```

**Estimated yield**: 4,000-5,000 additional lines

### Source 2: Kurdish News Articles

**Target**: 2,000-3,000 lines

**Sources**:

- NRT News (nrttv.com) - Kurdish news
- Rudaw (rudaw.net) - Kurdish news
- Kurdistan24 (kurdistan24.net)

**Method**: Web scraping of article archives (2020-2025)  
**Estimated yield**: 2,000-3,000 lines

### Source 3: Kurdish Literature/Books

**Target**: 1,000-2,000 lines

**Sources**:

- Public domain Kurdish poetry
- Kurdish historical texts
- Educational materials

**Estimated yield**: 1,000-2,000 lines

### Source 4: Synthetic Augmentation

**Target**: 1,000-1,500 lines

**Method**:

- Sentence shuffling/recombination
- Synonym substitution
- Paraphrase generation from existing corpus

**Estimated yield**: 1,000-1,500 lines

## Implementation Plan

### Phase 5.1: Wikipedia Expansion (Day 1)

**Time**: 4-6 hours  
**Tasks**:

1. ✅ Download full Kurdish Wikipedia dump
2. ✅ Extract top 500 articles by views/links
3. ✅ Clean and normalize text
4. ✅ Filter quality (remove stubs, lists)
5. ✅ Add to corpus with ZWNJ verification

**Expected output**: 4,000-5,000 new lines

### Phase 5.2: News Scraping (Day 2)

**Time**: 4-6 hours  
**Tasks**:

1. ✅ Write web scraping scripts for Kurdish news sites
2. ✅ Extract article text (2020-2025 archives)
3. ✅ Clean HTML, normalize encoding
4. ✅ Deduplicate against existing corpus
5. ✅ Add to corpus

**Expected output**: 2,000-3,000 new lines

### Phase 5.3: Corpus Integration & Balancing (Day 2-3)

**Time**: 2-3 hours  
**Tasks**:

1. ✅ Merge all sources
2. ✅ Deduplicate lines
3. ✅ Balance character frequencies
4. ✅ Verify ZWNJ density (target: 8-10%)
5. ✅ Run corpus audit

**Expected output**: 10,000-12,000 line final corpus

### Phase 5.4: Training (Day 3)

**Time**: 6-8 hours (overnight)  
**Tasks**:

1. ✅ Generate training data (text2image)
2. ✅ Train from Farsi base (same as Phase 4)
3. ✅ Monitor convergence (target BCER <0.15)
4. ✅ Save best/fast models

**Expected output**: ckb_phase5.traineddata

### Phase 5.5: Evaluation (Day 4)

**Time**: 1-2 hours  
**Tasks**:

1. ✅ Test on mgk.tif
2. ✅ Test on additional documents
3. ✅ Calculate accuracy improvement
4. ✅ Verify character recognition quality

**Expected results**: 85-90% accuracy

## After Phase 5: ZWNJ Strategy

Once base accuracy reaches 85-90%, we can retry ZWNJ rule insertion:

### Why 85-90% Accuracy Matters for ZWNJ

- **At 71% accuracy**: Too many char errors, text misalignment breaks rules
- **At 85%+ accuracy**: Character positions stable enough for pattern matching
- **Expected ZWNJ recovery**: 70-85% with rules (vs. current 7.8%)

### ZWNJ Implementation (After Phase 5)

1. ✅ Use improved Phase 5 model for base OCR (85-90% chars)
2. ✅ Apply refined `ه` + consonant rule (98% of ZWNJs)
3. ✅ Add ezafe rules (‌ی patterns)
4. ✅ Add compound word dictionary
5. ✅ Target: 70-85% ZWNJ recovery

**Combined system**:

```
Input Image → Phase 5 OCR (85-90% chars) → ZWNJ Rules → Final Text (85%+ chars, 70-85% ZWNJ)
```

## Alternative: If Corpus Expansion is Too Time-Consuming

### Option: Use Pre-trained Farsi Model Directly

- Farsi (fas) and Kurdish (ckb) are linguistically similar
- Farsi base model: already has good accuracy
- Fine-tuning: Only add Kurdish-specific characters (ە, ۆ, ێ, ڵ, ڕ)
- Training time: Much faster (2-3 hours vs. 8 hours)
- Expected accuracy: 75-80% (improvement without large corpus)

## Resource Requirements

### Compute

- **Corpus extraction**: CPU-bound (2-3 hours)
- **Training**: GPU recommended (8 hours CPU, 2-3 hours GPU)
- **Storage**: ~50 MB corpus, ~10 MB models

### Human Time

- **Day 1**: Wikipedia extraction (4-6 hours)
- **Day 2**: News scraping + integration (6-8 hours)
- **Day 3**: Training (mostly automated, 1 hour setup)
- **Day 4**: Evaluation (1-2 hours)

**Total**: 12-17 hours active work + 8 hours training

## Decision Point

### Proceed with Phase 5?

**YES** → Follow plan above, target 85-90% accuracy  
**NO** → Try Farsi model fine-tuning (faster, 75-80% accuracy)

### Recommendation

Given that:

1. Phase 4 plateau at 71.69% is due to corpus size
2. ZWNJ rules require better base accuracy (85%+)
3. Wikipedia + news sources are readily available

**→ RECOMMEND: Proceed with Phase 5 corpus expansion**

Expected outcome:

- **Phase 5**: 85-90% character accuracy
- **Phase 5 + ZWNJ rules**: 85%+ chars, 70-85% ZWNJ recovery
- **Total system**: Production-ready Kurdish OCR

---

## Next Steps

1. ✅ User approval to proceed with Phase 5
2. ✅ Start with Wikipedia expansion (highest ROI)
3. ✅ Implement news scraping
4. ✅ Train Phase 5 model
5. ✅ Evaluate and refine ZWNJ rules

**Status**: Awaiting user decision to proceed
