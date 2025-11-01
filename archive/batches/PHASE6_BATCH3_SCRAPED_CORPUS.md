# Phase 6 Batch 3 - Scraped Corpus Integration

**Date:** October 30, 2025  
**Status:** ✅ Corpus Collected → 🔄 Training In Progress

## Executive Summary

Successfully scraped **98,053 sentences** from 13 Kurdish news websites, filtered to **1,279 high-quality sentences**, and started **Phase 6 Batch 3** training with 500 new sentences added to existing corpus.

---

## Corpus Collection Results

### Raw Scraping Output

- **Total Sentences:** 98,053 (79,600 unique after dedup)
- **Websites:** 13 Kurdish news sources
- **Categories:** 42 files across politics, culture, economy, health, etc.
- **Collection Time:** ~3 hours with 3 parallel workers
- **Deduplication:** ✅ Working (article_dedup.db tracking)

### Top Sources

1. **avanews/economy.txt** - 12,680 sentences
2. **awene/politics.txt** - 9,905 sentences
3. **balinde/kurdish_poetry.txt** - 7,615 sentences
4. **avanews/environment.txt** - 7,953 sentences
5. **avanews/news.txt** - 7,785 sentences

### Raw Corpus Quality

| Metric                | Value                       | Assessment                  |
| --------------------- | --------------------------- | --------------------------- |
| Avg Words/Sentence    | 28.07                       | ❌ Too long (target: 10-25) |
| ZWNJ Density          | 1.33%                       | ❌ Too low (target: 8-12%)  |
| Kurdish Script %      | 99.30%                      | ✅ Excellent                |
| Sentence Distribution | 36.9% very long (30+ words) | ⚠️ Needs filtering          |

---

## Quality Filtering

### Filter Criteria

```python
zwnj_min=2.0%     # More lenient than ideal 8-12%
zwnj_max=15.0%
length_min=6 words
length_max=35 words
kurdish_purity=90%
```

### Filtering Results

```
Total sentences processed: 79,600
  Duplicates removed: 3,037
  Bad length: 37,995 (47.7%)
  Bad ZWNJ density: 37,204 (46.7%)  ← Main bottleneck
  Bad purity: 85 (0.1%)
  ACCEPTED: 1,279 (1.61% acceptance rate)
```

### Filtered Corpus Quality

| Metric                 | Value  | Target      | Status              |
| ---------------------- | ------ | ----------- | ------------------- |
| **Sentences**          | 1,279  | 5,000-8,000 | 🔄 Can collect more |
| **Avg Words/Sentence** | 20.77  | 10-25       | ✅ Perfect          |
| **ZWNJ Density**       | 9.15%  | 8-12%       | ✅ Ideal!           |
| **Kurdish Purity**     | 99.86% | >85%        | ✅ Excellent        |

**Output File:** `work/corpus/ckb_scraped_filtered.training_text`

---

## Phase 6 Batch 3 Training

### Corpus Composition

```bash
# Phase 6 Batch 2 (baseline): 4,686 sentences
# + New scraped corpus:        500 sentences (top quality from filtered)
# = Phase 6 Batch 3:           5,186 sentences
```

### Quality Metrics

| Metric             | Batch 2 | Batch 3 | Change        |
| ------------------ | ------- | ------- | ------------- |
| Sentences          | 4,686   | 5,186   | +500 (+10.7%) |
| Avg Words/Sentence | 13.69   | 14.46   | +0.77         |
| ZWNJ Density       | 5.12%   | 6.36%   | +1.24%        |

**Status:** Training started at current time

- **Command:** `.\run_training.ps1 -Mode GenerateTrain -CorpusFileOverride work\corpus\ckb_phase6_batch3.training_text`
- **Current Stage:** Generating training data (font rendering)
- **ETA:** ~45-60 minutes for full training cycle

---

## Key Insights

### 1. ZWNJ Density is the Main Filter Bottleneck

- **46.7%** of sentences rejected due to low ZWNJ density
- Most news articles don't use ZWNJ properly between Kurdish compound words
- This is actually GOOD - we're filtering for quality, not quantity
- The 1,279 accepted sentences have ideal ZWNJ density (9.15%)

### 2. News Writing Style Differs from Poetry/Formal Text

- News articles tend to have **longer sentences** (28 words vs. 14 words)
- News uses **less ZWNJ** (1.33% vs. 5-12% in formal/poetry)
- **Solution:** Applied strict filtering to extract only formal-style sentences

### 3. Script Purity is Excellent

- **99.86%** Kurdish script in filtered corpus
- Minimal Latin character mixing (<1%)
- No quality concerns with script purity

### 4. Incremental Approach Working Well

- Phase 6 Batch 2: 4,686 sentences → **Accuracy baseline needed**
- Phase 6 Batch 3: 5,186 sentences → Training now
- Plan: Add 500 sentences per batch, evaluate each

---

## Sample Filtered Sentences

High-quality examples from the filtered corpus (ZWNJ shown as `‌`):

1. `له‌ دیمانه‌ی ڕۆژنامه‌وانیشدا به‌ده‌ر له‌م جووڵه‌ و ئاماژانه‌ی سه‌ره‌وه‌، ژماره‌یه‌ك جووڵه‌ی تری گرنگ هه‌یه‌`

2. `د. هه‌ڤاڵ ئه‌بوبه‌كر: خه‌نجه‌ره‌كانتان له‌پشتی یه‌ك ده‌ربێنن`

3. `دكتۆر ئینده‌ربیر گیل پزیشكی میزه‌ڵدان و سه‌رۆكی تیمی نه‌شته‌رگه‌ری دوپاتیكرده‌وه‌`

---

## Next Steps

### Immediate (While Training Runs)

1. ⏳ Wait for Batch 3 training to complete (~45-60 min)
2. 📊 Evaluate accuracy: `.\run_training.ps1 -Mode Eval`
3. 📈 Compare to Batch 2 baseline (need to establish this first)

### If Batch 3 Shows Improvement

1. Create Batch 4 with next 500 sentences (5,686 total)
2. Continue incremental growth: +500 sentences per batch
3. Stop when accuracy plateaus or degrades

### If Batch 3 Shows No Improvement

1. Analyze why: corpus quality vs. training issues
2. Consider stricter ZWNJ filtering (5-10% instead of 2-15%)
3. May need to collect from different sources (poetry, formal documents)

### Future Corpus Expansion

If we need more high-quality sentences:

- Still have **779 unused filtered sentences** (1,279 - 500 used)
- Can adjust filter to be more aggressive:
  - ZWNJ: 5-12% (stricter)
  - Length: 10-25 words (stricter)
- Or scrape from different source types:
  - Literary websites (poetry, novels)
  - Formal government documents
  - Academic papers

---

## Files Created/Modified

### New Files

- `work/tools/scrapers/check_corpus_quality.py` - Analyzes corpus metrics
- `work/tools/scrapers/filter_corpus.py` - Filters by ZWNJ/length/purity
- `work/corpus/ckb_scraped_filtered.training_text` - Filtered corpus (1,279 sentences)
- `work/corpus/ckb_phase6_batch3.training_text` - Training corpus (5,186 sentences)
- `work/corpus/check_batch3.py` - Quality check script

### Modified Files

- `run_production_display.py` - Added corpus file saving (already done in previous session)
- `run_training.ps1` - Integrated ScrapeCorpus mode (already done in previous session)

### Corpus Files Location

- **Raw Scraped:** `work/tools/scrapers/corpus/{website}/{category}.txt` (98,053 sentences)
- **Filtered:** `work/corpus/ckb_scraped_filtered.training_text` (1,279 sentences)
- **Training:** `work/corpus/ckb_phase6_batch3.training_text` (5,186 sentences)

---

## Performance Expectations

### Target Accuracy Improvement

- **Batch 2 Baseline:** Need to establish (likely similar to previous ~72%)
- **Batch 3 Target:** +2-3% improvement (74-75%)
- **Ultimate Goal:** 80% accuracy

### Why Incremental?

- Prevents overfitting
- Allows quality control at each step
- Can stop if accuracy degrades
- Each batch independently evaluated

### Training Time

- **Generation:** ~10-15 minutes (9 fonts × rendering time)
- **Training:** ~30-45 minutes (depends on corpus size)
- **Evaluation:** ~5-10 minutes
- **Total:** ~45-70 minutes per batch

---

## Conclusion

✅ **Successfully completed:**

- Scraped 98K sentences from 13 Kurdish news websites
- Filtered to 1,279 high-quality sentences (9.15% ZWNJ density)
- Created Phase 6 Batch 3 corpus (5,186 sentences)
- Started training pipeline

🔄 **Currently running:**

- Phase 6 Batch 3 training (Generation stage)

⏭️ **Next action:**

- Wait for training completion
- Run evaluation: `.\run_training.ps1 -Mode Eval`
- Compare accuracy to Batch 2 baseline
- Decide: continue with Batch 4 or adjust strategy

---

**Training Command:**

```powershell
.\run_training.ps1 -Mode GenerateTrain -CorpusFileOverride work\corpus\ckb_phase6_batch3.training_text
```

**Monitor Progress:**

```powershell
Get-Content work\logs\generate_training_latest.log -Wait
```
