# Phase 6 Batch 2 - Manual News Collection Plan

**Date**: October 16, 2025  
**Status**: 🟡 READY TO START

---

## 📋 Batch 1 Lessons Applied

### ❌ What Failed in Batch 1

- Wikipedia source (even quality-filtered) → No improvement
- Only 11% net new unique data (too small)
- Same source as Phase 4/5 → Training converged to old checkpoints
- Result: 71.69% (0.00% improvement)

### ✅ Batch 2 Strategy Changes

1. **Different source**: Professional Kurdish news (NOT Wikipedia)
2. **Larger batch**: 1,000-1,500 sentences (vs 480)
3. **Higher ZWNJ**: Target 10-12% (news has more ZWNJ than Wikipedia)
4. **Manual collection**: Ensures quality and source diversity
5. **Target**: 30-40% corpus increase for stronger signal

---

## 🎯 Collection Goals

### Quantity

- **Target**: 1,000-1,500 unique sentences
- **After dedup**: ~800-1,200 net new
- **Final corpus**: 4,400-4,800 lines (~35% increase)

### Quality

- **ZWNJ density**: 10-12% (higher than Batch 1's 8.25%)
- **Sentence length**: 10-25 words
- **Kurdish purity**: >85%
- **Grade target**: A (90+/100)
- **Register**: Formal news language

### Sources (Priority Order)

#### 1. Rudaw (rudaw.net/sorani) - 400-600 sentences

- **Sections**: Kurdistan, Politics, Business, Culture
- **Why**: Largest Kurdish news site, formal Sorani, high ZWNJ usage
- **Articles to target**: Full news articles (not breaking news/headlines)

#### 2. BasNews (basnews.com) - 300-400 sentences

- **Sections**: News, Economy, Society
- **Why**: Professional journalism, diverse topics

#### 3. NRT (nrttv.com) - 200-300 sentences

- **Sections**: News reports, analysis pieces
- **Why**: Formal language, government/political focus

#### 4. K24 (k24.tv) - 100-200 sentences (if needed)

- **Sections**: News articles
- **Why**: Additional diversity

---

## 📝 Collection Process

### Setup

1. Create collection file:

   ```bash
   # File: c:\tesseract\work\corpus\kurdish_news_batch2.txt
   ```

2. Keep collection assistant handy:
   ```bash
   cd c:\tesseract\work
   wsl -d Ubuntu -- bash -lc "python3 tools/collection_assistant.py corpus/kurdish_news_batch2.txt"
   ```

### Collection Workflow

**For each news article:**

1. **Find article** on Rudaw/BasNews/NRT

   - Look for substantial articles (5+ paragraphs)
   - Avoid: Headlines, dates, author names, photo captions
   - Prefer: Politics, economy, culture, analysis

2. **Copy article body**

   - Select main text paragraphs
   - Exclude: Embedded tweets, quotes with Latin, advertisements

3. **Extract sentences**

   - Paste into text editor
   - Split into one sentence per line
   - Remove extra whitespace
   - Quick check: 10-25 words per sentence

4. **Add to file**

   - Append to `kurdish_news_batch2.txt`
   - No blank lines
   - One sentence per line

5. **Check progress** (every 100 sentences)
   ```bash
   python3 tools/collection_assistant.py corpus/kurdish_news_batch2.txt
   ```

### Quality Guidelines

**✅ Good Sentences:**

```
حکومەتی هەرێمی کوردستان ڕایگەیاند کە بەردەوامە لە چارەسەرکردنی کێشەکانی ئابووری.
لە کۆبوونەوەیەکی فەرمیدا لە هەولێر، سەرۆکی حکومەت گرنگی دا بە پێشخستنی پڕۆژە گشتییەکان.
وەزیری دارایی ڕوونی کردەوە کە بودجەی ساڵی داهاتوو لە کۆمەڵگەدا دابەشکراوە بە شێوەیەکی یەکسان.
```

**❌ Avoid:**

```
سەرەتا                          (too short)
BREAKING NEWS                   (English/Latin)
١٥ تشرینی یەکەم ٢٠٢٥         (date only)
www.rudaw.net/sorani           (URL)
بە پێی ڕاپۆرتەکانی BBC و CNN  (mixed Latin)
```

---

## 🔍 Expected Improvements Over Batch 1

| Metric             | Batch 1 (Wikipedia)           | Batch 2 (News) Target   |
| ------------------ | ----------------------------- | ----------------------- |
| Source             | Wikipedia (same as Phase 4/5) | Professional news (NEW) |
| Net new lines      | 359 (+11%)                    | 800-1,200 (+25-35%)     |
| ZWNJ density       | 9.17% → 8.25% combined        | 10-12% → 9-10% combined |
| Quality grade      | A (90) individual             | A (92-95) individual    |
| Register           | Encyclopedic/informal         | Formal news             |
| Vocabulary         | Academic/varied               | Professional/political  |
| Sentence structure | Complex/varied                | Clear/formal            |

---

## ⏱️ Timeline

### Phase 1: Collection (3-5 hours)

- **Day 1**: Collect 500 sentences (Rudaw focus)
  - Session 1: 2 hours → 250 sentences
  - Session 2: 2 hours → 250 sentences
- **Day 2**: Collect 500 sentences (BasNews + NRT)
  - Session 3: 1.5 hours → 250 sentences
  - Session 4: 1.5 hours → 250 sentences
- **Optional Day 3**: Additional 500 if needed (K24 + more Rudaw)

### Phase 2: Preparation (30 minutes)

1. Remove comment lines from file
2. Run quality checker → verify A grade
3. Check ZWNJ density → should be 10-12%
4. Check duplicate rate → should be <5%

### Phase 3: Training (3-5 hours)

1. Create Batch 2 corpus
2. Run training (automated)
3. Wait for completion

### Phase 4: Evaluation (30 minutes)

1. Test all 3 models
2. Compare to baseline (71.69%)
3. Make decision

---

## 🎯 Success Criteria

### Minimum (Keep Batch 2)

- **Accuracy**: ≥72.5% (+0.8% improvement)
- **Rationale**: Meaningful improvement, different source working
- **Next**: Continue to Batch 3 with more news

### Target (Successful)

- **Accuracy**: 73-73.5% (+1.3-1.8%)
- **Rationale**: Strong signal that news source is effective
- **Next**: Expand to official documents in Batch 3

### Excellent (Breakthrough)

- **Accuracy**: 73.5-74%+ (+1.8-2.3%+)
- **Rationale**: Major improvement, news is the right path
- **Next**: Continue aggressive news collection

### Failure (Discard)

- **Accuracy**: <72.5% (<+0.8%)
- **Rationale**: Not enough improvement for effort
- **Next**: Try official documents or parallel corpus

---

## 🚀 Quick Start Commands

### Start Collection

```bash
# Create file
cd c:\tesseract\work\corpus
# Open kurdish_news_batch2.txt in text editor
# Start adding sentences from Rudaw
```

### Check Progress

```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "python3 tools/collection_assistant.py corpus/kurdish_news_batch2.txt"
```

### When Complete

```bash
# 1. Quality check
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/corpus_quality_checker.py corpus/kurdish_news_batch2.txt"

# 2. Create Batch 2
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && cat corpus/ckb_phase4.training_text.backup corpus/kurdish_news_batch2.txt | sort -u > corpus/ckb_phase6_batch2.training_text && cp corpus/ckb_phase6_batch2.training_text corpus/ckb.training_text"

# 3. Train
cd c:\tesseract
.\run_training.ps1 -Mode GenerateTrain
```

---

## 📊 Progress Tracking

| Milestone               | Target          | Status         |
| ----------------------- | --------------- | -------------- |
| Rudaw articles          | 400-600         | 🔴 Not started |
| BasNews articles        | 300-400         | 🔴 Not started |
| NRT articles            | 200-300         | 🔴 Not started |
| K24 articles (optional) | 100-200         | 🔴 Not started |
| **Total collected**     | **1,000-1,500** | **0**          |
| Quality check           | A grade         | ⏳ Pending     |
| Training                | 3-5 hours       | ⏳ Pending     |
| Evaluation              | 72.5%+          | ⏳ Pending     |

---

## 💡 Tips for Efficient Collection

### 1. Work in Batches

- Collect 50-100 sentences at a time
- Check quality after each batch
- Adjust if issues found

### 2. Use Multiple Sources

- Don't collect more than 300 from any single website
- Diversity helps avoid overfitting

### 3. Save Often

- Save file every 50 sentences
- Backup periodically

### 4. Focus on Quality

- Better to have 800 high-quality sentences than 1,500 mediocre ones
- Professional news articles > opinion pieces > blog posts

### 5. Check ZWNJ Density

- If collection assistant shows <9% ZWNJ, find articles with more formal language
- Government/political news tends to have higher ZWNJ than sports/entertainment

---

## 🔄 Alternative if Manual Collection Fails

### Option A: Semi-Automated Scraping

- Use scraper template with manual URL list
- Collect article URLs manually
- Run scraper to extract text
- Quality filter output

### Option B: Parallel Corpus

- Find Kurdish-English subtitle files
- Extract Kurdish side
- Quality filter for ZWNJ and length

### Option C: Official Documents

- Kurdish government websites
- Academic papers in Kurdish
- Published literature

### Option D: Try Fresh Training

- Delete Phase 4 checkpoints
- Retrain Batch 1 from scratch
- See if forces new learning

---

**Status**: 🟡 **Ready for manual collection**  
**Next Action**: User collects 1,000-1,500 sentences from Kurdish news sites  
**Expected Outcome**: 72.5-74% accuracy (+0.8-2.3%)  
**Timeline**: 1-2 days (3-5 hours collection + 3-5 hours training)
