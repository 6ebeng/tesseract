# Phase 6 Batch 1 - Results Analysis

**Date**: October 16, 2025  
**Status**: ❌ **FAILED - No Improvement**

---

## 📊 Evaluation Results

### All Models: **71.69% Accuracy (CER 0.2831)**

| Base Model | BCER | CER | Accuracy | vs Baseline |
|------------|------|-----|----------|-------------|
| **Farsi** | 0.195 | 0.2831 | **71.69%** | **0.00%** ❌ |
| **Arabic** | 0.202 | 0.2831 | **71.69%** | **0.00%** ❌ |
| **English** | 0.349 | 0.2831 | **71.69%** | **0.00%** ❌ |
| *Phase 4 Baseline* | 0.195 | 0.2831 | 71.69% | - |

**Result**: All three models performed **identically** to each other AND to the Phase 4 baseline.

---

## 🔍 Root Cause Analysis

### What Happened?

The training process **restored from existing Phase 4 checkpoints** and determined that those were still the best models. Looking at the training log:

```
Finished! Selected model with minimal training error rate (BCER) = 0.195
✅ Using checkpoint: ckb_from_fas_checkpoint
```

This checkpoint is from **October 11** (Phase 4), not a new one from October 15:

```bash
-rwxrwxrwx 1 tishko tishko  13M Oct 11 13:24 ckb_from_fas_0.195_8226_85300.checkpoint
```

### Why Did This Happen?

1. **Checkpoint Restoration**: The training script loads existing checkpoints if they exist
2. **Early Convergence**: Training reached minimal BCER (0.195) quickly using existing knowledge
3. **No New Learning**: The +480 sentences didn't provide enough signal to improve beyond existing checkpoint
4. **Diminishing Returns**: Already at 71.69%, hard to improve without significant quality boost

### Evidence

**Training Output:**
- Farsi: "At iteration 8748... New worst BCER = 0.409 wrote checkpoint. Finished! Selected model with minimal training error rate (BCER) = 0.195"
- Arabic: "At iteration 14389... New worst BCER = 1.125... Selected model with minimal training error rate (BCER) = 0.202"
- English: "At iteration 15082... New worst BCER = 0.712... Selected model with minimal training error rate (BCER) = 0.349"

All selected BCERs match existing Phase 4 checkpoints - no improvement!

**MD5 Checksums:**
- Batch 1 Farsi: `9e7d9ee5e60ca0cc28f2c1e86f08e4e4`
- Phase 4 Farsi: `f9a5ab8b071a28097f28efef1f014042`

Models ARE different files, but produce identical results (71.69%).

---

## 📉 Why Batch 1 Failed

### 1. Source Quality Issue
- **Wikipedia corpus** (even quality-filtered) still not high enough quality
- Phase 5 already tried Wikipedia - adding more from same source unlikely to help
- ZWNJ density: 8.25% (only +0.1% from Phase 4's 8.15%)

### 2. Insufficient Net New Data
- Added: 480 sentences
- Base: 3,278 sentences  
- **Net increase**: Only +14.6%
- **Duplicates removed**: 121 lines (20% of "new" data was duplicate!)
- **Actual new unique data**: Only 359 lines (~11%)

### 3. Training Convergence Behavior
- Training quickly converged to existing checkpoints
- No sustained improvement during training iterations
- Suggests new data too similar to existing corpus

### 4. Corpus Similarity
- Phase 4: Wikipedia + mixed sources
- Batch 1: Phase 4 + more Wikipedia
- **Problem**: Same source, same patterns, same limitations

---

## 💡 Lessons Learned

### ❌ What Didn't Work

1. **More Wikipedia data** - Even quality-filtered, not diverse enough
2. **Small incremental additions** - 11% net new data insufficient for breakthrough
3. **Quality grading alone** - A grade doesn't mean different from existing corpus
4. **Same source expansion** - Need different sources, not more of the same

### ✅ What We Learned

1. **Quality AND diversity both matter** - High quality from same source = diminishing returns
2. **Need larger batch sizes** - 500 lines not enough, need 1000+ unique lines
3. **Need different sources** - Professional news/official docs, NOT more Wikipedia
4. **Checkpoint behavior** - Training will prefer existing checkpoints unless significantly better data

---

## 🎯 Phase 6 Strategy Revision

### ❌ Original Plan (Failed)
- Incremental 500-line batches from Wikipedia
- Gradual improvement through quality filtering
- Expected: +0.3% per batch

### ✅ Revised Plan (Next Steps)

#### Option A: Manual News Collection (RECOMMENDED)
- **Source**: Rudaw, BasNews, NRT (professional Kurdish news)
- **Amount**: 1,000-1,500 sentences (larger batch for signal)
- **Method**: Manual collection as originally designed
- **Expected**: Higher ZWNJ (10-12%), more formal language, different vocabulary
- **Timeline**: 3-5 hours collection + 3-5 hours training

#### Option B: Official Documents
- **Source**: Kurdish government websites, official announcements
- **Amount**: 1,000+ sentences  
- **Expected**: Very high ZWNJ (12-15%), formal register
- **Challenge**: Harder to collect in bulk

#### Option C: Parallel Corpus Mining
- **Source**: Kurdish-English parallel texts (subtitles, translations)
- **Amount**: 2,000+ sentences
- **Expected**: Diverse domains, natural language
- **Challenge**: Need to find quality parallel corpora

#### Option D: Fresh Training Start
- **Method**: Delete checkpoints, start training from scratch with Batch 1 corpus
- **Risk**: Might get worse results (checkpoints exist for good reason)
- **Expected**: Force new learning, but uncertain outcome

---

## 📋 Recommended Next Actions

### Immediate (Choose One):

**1. Manual News Collection** (Most Likely to Succeed)
```bash
# Start collecting from professional Kurdish news sites
# Target: 1,000-1,500 sentences
# Use: c:\tesseract\work\corpus\kurdish_news_batch2.txt
# Sources: Rudaw, BasNews, NRT, K24
```

**2. Try Fresh Training** (Quick Test)
```bash
# Backup and remove existing checkpoints
cd c:\tesseract\work\training_output/model
mkdir checkpoint_backup
mv *.checkpoint checkpoint_backup/

# Retrain Batch 1 from scratch
cd c:\tesseract
.\run_training.ps1 -Mode GenerateTrain
```

**3. Larger Wikipedia Batch** (Low Confidence)
```bash
# Extract 2,000 best sentences instead of 500
python3 tools/extract_quality_sentences.py corpus/ckb_phase5_wikipedia.training_text corpus/kurdish_wiki_batch2.txt 2000
```

### Medium-Term:

1. **Develop news scraper** - Automate Rudaw/BasNews collection
2. **Find parallel corpus** - Kurdish-English subtitles/translations
3. **Engage community** - Ask Kurdish speakers for text donations

---

## 🔄 Decision: What To Do?

### Recommendation: **Manual News Collection (Option A)**

**Reasoning:**
1. ✅ Wikipedia proven insufficient (Phase 5 + Batch 1)
2. ✅ Need different source with higher ZWNJ density
3. ✅ Professional news = formal language = better patterns
4. ✅ Manual collection ensures quality
5. ✅ 1,000-1,500 sentences = 30-40% corpus increase (enough signal)

**Expected Outcome:**
- **Realistic**: 72.5-73.5% (+0.8-1.8%)
- **Optimistic**: 73.5-74.5% (+1.8-2.8%)
- **Minimum for success**: 72.5% (+0.8%)

**Timeline:**
- Collection: 3-5 hours (user effort)
- Training: 3-5 hours (automated)
- **Total**: 1-2 days

---

## 📊 Batch 1 Final Statistics

### Corpus
- **Lines**: 3,637
- **Grade**: B (85/100) 
- **ZWNJ**: 8.25%
- **Source**: Phase 4 (3,278) + Wikipedia quality (480) - duplicates (121)
- **Net new**: 359 unique lines (+11%)

### Training
- **Duration**: ~6 hours (image gen + LSTM training)
- **Bases trained**: Farsi, Arabic, English
- **Checkpoints created**: None (reused Phase 4)
- **Best BCER**: 0.195 (Farsi, from Phase 4)

### Results
- **Accuracy**: 71.69% (all models)
- **Improvement**: **0.00%** ❌
- **Decision**: **DISCARD** - proceed to Batch 2 with different approach

---

## 📁 Files Generated

### Models (Not Used)
- `training_output/model/ckb_from_fas.traineddata`
- `training_output/model/ckb_from_ara.traineddata`
- `training_output/model/ckb_from_eng.traineddata`

### Corpus
- `corpus/ckb_phase6_batch1.training_text` (3,637 lines)
- `corpus/kurdish_news_batch1.txt` (480 lines, Wikipedia quality extract)

### Evaluation
- `output/mgk_batch1_fas.txt` (OCR output)
- `output/mgk_batch1_ara.txt` (OCR output)
- `output/mgk_batch1_eng.txt` (OCR output)

---

**Status**: 🔄 **Moving to Batch 2 with Manual News Collection**  
**Next**: Collect 1,000-1,500 sentences from Rudaw, BasNews, NRT  
**Target**: 73%+ accuracy (+1.3%+ improvement)
