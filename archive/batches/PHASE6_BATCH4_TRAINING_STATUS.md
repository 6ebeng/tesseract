# Phase 6 Batch 4 - Training Status

**Date**: October 31, 2025  
**Status**: 🔄 Training In Progress  
**Strategy**: Hybrid approach (biography + high-ZWNJ news)

---

## Key Finding: Wikipedia ZWNJ Problem

**Critical Discovery**: Kurdish Wikipedia has **extremely low ZWNJ usage (0.08%)**!

This is a fundamental issue:

- Target ZWNJ density for OCR: 6-10%
- Wikipedia biography corpus: **0.08%** (80x too low!)
- News scraped corpus (filtered): **9.15%** (perfect!)

**Implication**: Wikipedia alone won't improve mgk.tif accuracy (which relies on proper ZWNJ).

---

## Batch 4 Hybrid Strategy

Since Wikipedia has poor ZWNJ but good biographical style, we're using a **hybrid approach**:

### Corpus Composition

| Source             | Sentences | ZWNJ Density | Purpose                      |
| ------------------ | --------- | ------------ | ---------------------------- |
| **Batch 3**        | 5,186     | 6.36%        | Baseline (news-heavy)        |
| **Wikipedia Bio**  | 300       | 0.08%        | Biographical style diversity |
| **High-ZWNJ News** | 200       | 9.15%        | High ZWNJ density            |
| **Batch 4 Total**  | **5,686** | **5.83%**    | Blended quality              |

### Quality Metrics

- **Avg Words/Sentence**: 14.85 (good formal length)
- **ZWNJ Density**: 5.83% (slightly lower than Batch 3's 6.36%)
- **Domain Mix**: 91% news, 9% biography

---

## Expected Outcomes

### Scenario Analysis

**Best Case (+2-3% accuracy)**:

- Biography style helps with mgk.tif structure
- High-ZWNJ sentences strengthen ZWNJ recognition
- Result: 71.69% → 73-74%

**Moderate Case (+0.5-1% accuracy)**:

- Some improvement from biographical style
- Low Wikipedia ZWNJ partially offsets high-ZWNJ news
- Result: 71.69% → 72-73%

**Conservative Case (No improvement)**:

- Wikipedia's low ZWNJ dilutes corpus quality
- 300 low-ZWNJ + 200 high-ZWNJ = net neutral
- Result: 71.69% (plateau continues)

---

## Training Progress

### Current Status

```
Stage: Generation (font rendering)
Progress: Started at current time
ETA: ~45-60 minutes
```

### Models Being Trained

- ✅ Farsi base (ckb_from_fas)
- ✅ Arabic base (ckb_from_ara)
- ✅ English base (ckb_from_eng)

---

## Lessons from Wikipedia Scraping

### What Went Right ✅

1. **Scraping worked perfectly**: 651 sentences from 59 biographical pages
2. **High acceptance rate**: 82.8% (539/651 passed filters)
3. **Good biographical content**: Politicians, poets, historians, writers
4. **Proper sentence length**: 18.08 words average (good for formal style)
5. **Pure Kurdish script**: 100% passed purity check

### The ZWNJ Problem ❌

**Wikipedia doesn't use ZWNJ properly in Kurdish!**

**Evidence**:

- Raw corpus: 0.11% ZWNJ density
- Filtered corpus: 0.08% ZWNJ density
- Target for OCR: 6-10% ZWNJ density
- **Gap: 75x-125x too low!**

**Why this matters**:

- ZWNJ (Zero-Width Non-Joiner, U+200C) is critical for Kurdish compound words
- Example: `پێش‌وەشە` (leader) requires ZWNJ between `پێش` and `وەشە`
- Without ZWNJ: Characters connect improperly → OCR confusion
- mgk.tif test image: High ZWNJ usage (~5-8%)
- Model needs ZWNJ examples to learn proper recognition

**Root cause**:

- Wikipedia editors don't consistently use ZWNJ
- Kurdish keyboard layouts may not make ZWNJ easily accessible
- No automated ZWNJ insertion in Wikipedia's editing tools

---

## Alternative Strategies Considered

### Option A: Use Only High-ZWNJ News (Rejected)

**Plan**: Add 500 more high-ZWNJ news sentences  
**Problem**: Already tried in Batch 3, resulted in 0% improvement  
**Reason**: More news won't help with biographical text (mgk.tif)

### Option B: Use Only Wikipedia Biography (Rejected)

**Plan**: Add 500 Wikipedia biography sentences  
**Problem**: 0.08% ZWNJ will likely hurt model performance  
**Reason**: Model needs ZWNJ examples, Wikipedia has almost none

### Option C: Hybrid Approach (Selected) ⭐

**Plan**: Mix 300 Wikipedia bio (style) + 200 high-ZWNJ news (ZWNJ)  
**Rationale**: Get biography style WITHOUT sacrificing ZWNJ density  
**Risk**: Lower than pure Wikipedia, safer than pure news

### Option D: Find Better Biographical Sources (Future)

**Potential sources**:

- Kurdish literature websites (poetry, novels)
- Formal government documents
- Academic papers
- Traditional texts with proper ZWNJ

**Challenge**: Need to identify and scrape these sources

---

## Technical Details

### Wikipedia Scraper Performance

**Execution**:

- Start: 10:33:14
- End: 10:35:25
- Duration: ~2 minutes 11 seconds
- Pages scraped: 59
- Average: 2.2 seconds per page

**Categories scraped**:

1. ✅ Kurdish writers (19 pages)
2. ✅ Kurdish poets (19 pages)
3. ✅ Kurdish historians (20 pages)
4. ❌ Personalities of Kurdistan (404 error - bad URL encoding)
5. ✅ Kurdish politicians (1 page)

**Top contributors**:

- ئەحمەد موفتیزادە (Ahmad Muftizadeh): 57 sentences
- ئیبراھیم ئەحمەد (Ibrahim Ahmad): 49 sentences
- ئەحمەد ھەردی (Ahmad Hardi): 42 sentences

### Filtering Results

**Input**: 651 raw sentences  
**Output**: 539 filtered sentences (82.8% acceptance)

**Rejections**:

- Duplicates: 14 (2.2%)
- Bad length (<8 or >40 words): 98 (15.1%)
- Bad purity (<85% Kurdish): 0 (0%)

**Quality of filtered corpus**:

- Avg words: 18.08
- ZWNJ density: 0.08% ← **CRITICAL PROBLEM**

---

## Post-Training Plan

### If Batch 4 Improves Accuracy (≥72.5%)

1. **Continue hybrid approach** - Mix biography sources with high-ZWNJ content
2. **Find better bio sources** - Scrape literary/formal sites with proper ZWNJ
3. **Batch 5 plan**: 400 better bio + 100 high-ZWNJ = 500 more sentences

### If Batch 4 Shows No Improvement (71.69%)

1. **Abandon Wikipedia** as a source (too low ZWNJ)
2. **Focus on high-ZWNJ sources only** - Even if all news domain
3. **Alternative**: Accept that model is optimized for news (76.9% accuracy)
4. **Change benchmark**: Stop using mgk.tif as primary metric

### If Batch 4 Degrades Performance (<71.5%)

1. **STOP immediately** - Wikipedia ZWNJ problem confirmed
2. **Revert to Batch 3** as production model
3. **Completely new strategy needed** - Find ZWNJ-rich biographical sources

---

## Files Created

### Scraping & Filtering

- `work/tools/scrapers/wikipedia_bio_scraper.py` - Wikipedia biography scraper
- `work/tools/scrapers/wikipedia_bio_raw.txt` - 651 raw sentences
- `work/tools/scrapers/filter_wiki_bio.py` - Biography-specific filter
- `work/corpus/ckb_wikipedia_bio_filtered.training_text` - 539 filtered sentences

### Corpus Creation

- `work/corpus/create_batch4.py` - Batch 4 creator script
- `work/corpus/ckb_phase6_batch4.training_text` - 5,686 sentences (training corpus)

### Documentation

- `PHASE6_BATCH3_RESULTS.md` - Batch 3 analysis (no improvement found)
- `PHASE6_BATCH4_QUICKSTART.md` - Original Batch 4 plan
- `PHASE6_BATCH4_TRAINING_STATUS.md` - This document

---

## Critical Insight: The ZWNJ Dilemma

**The core problem with breaking the 71.69% plateau**:

1. **mgk.tif needs**: Biographical style + High ZWNJ density
2. **Wikipedia provides**: Biographical style + Almost no ZWNJ
3. **News corpus provides**: News style + High ZWNJ density

**The impossible requirement**:

> Find sources that are BOTH biographical-style AND ZWNJ-rich

**Sources that might work**:

- ✅ Kurdish poetry books (formal style, proper ZWNJ)
- ✅ Kurdish literary websites (classic texts with ZWNJ)
- ✅ Kurdish language textbooks (educational, ZWNJ-correct)
- ✅ Professional Kurdish publications (formal, edited)
- ❌ Wikipedia (informal editing, poor ZWNJ)
- ❌ Social media (too informal, poor ZWNJ)
- ❌ News sites (wrong style, good ZWNJ)

---

## Next Steps

1. **Wait for training** (~45 minutes remaining)
2. **Evaluate**: Run `.\run_training.ps1 -Mode Eval`
3. **Analyze results**: Compare to 71.69% baseline
4. **Decide path forward** based on outcomes above

---

**Training Started**: October 31, 2025, current time  
**Expected Completion**: ~45-60 minutes  
**Next Update**: After evaluation completes
