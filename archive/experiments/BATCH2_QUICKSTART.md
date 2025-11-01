# Phase 6 Batch 2 - Quick Start Guide

**Goal**: Collect 1,000-1,500 sentences from Kurdish news sites  
**Why**: Batch 1 failed (Wikipedia insufficient), need professional news source  
**Expected**: 72.5-74% accuracy (+0.8-2.3% improvement)

---

## 🚀 Quick Start (5 Steps)

### Step 1: Open Collection File

```
Location: c:\tesseract\work\corpus\kurdish_news_batch2.txt
Action: Open in text editor (Notepad, VS Code, etc.)
```

### Step 2: Visit Kurdish News Site

Start with: **https://www.rudaw.net/sorani**

Navigate to sections:

- Kurdistan (کوردستان)
- Politics (سیاست)
- Business (ئابووری)
- Culture (کلتور)

### Step 3: Copy Article Text

1. Click on a full article (not breaking news)
2. **Avoid**: Headlines, dates, author names, photo captions
3. **Copy**: Main article paragraphs (body text)
4. Select and copy 5-10 paragraphs

### Step 4: Extract Sentences

1. Paste into `kurdish_news_batch2.txt`
2. **One sentence per line** (split paragraphs)
3. Remove blank lines
4. Remove English/Latin text
5. Keep only 10-25 word sentences

### Step 5: Check Progress

Every 50-100 sentences, run:

```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "python3 tools/collection_assistant.py corpus/kurdish_news_batch2.txt"
```

---

## 📝 Example Workflow

### 1. Find Article on Rudaw

URL: https://www.rudaw.net/sorani/kurdistan/161020251

### 2. Copy Article Paragraph:

```
حکومەتی هەرێمی کوردستان لە کۆبوونەوەیەکی ئاساییدا چەندین بڕیاری گرنگی
دەرکرد کە پەیوەندیی بە پێشخستنی پڕۆژە گشتییەکانەوە هەیە. بەپێی ڕاگەیاندنی
فەرمی، ئەم بڕیارانە لە چوارچێوەی پلانی حکومەتدا بۆ باشترکردنی خزمەتگوزاری
دەخرێنە بواری جێبەجێکردنەوە.
```

### 3. Split into Sentences (one per line):

```
حکومەتی هەرێمی کوردستان لە کۆبوونەوەیەکی ئاساییدا چەندین بڕیاری گرنگی دەرکرد کە پەیوەندیی بە پێشخستنی پڕۆژە گشتییەکانەوە هەیە.
بەپێی ڕاگەیاندنی فەرمی، ئەم بڕیارانە لە چوارچێوەی پلانی حکومەتدا بۆ باشترکردنی خزمەتگوزاری دەخرێنە بواری جێبەجێکردنەوە.
```

### 4. Add to File

Paste these 2 sentences into `kurdish_news_batch2.txt` below the header.

### 5. Repeat

- Find another article
- Copy, split, add
- Continue until 1,000-1,500 sentences

---

## 🎯 Collection Targets

| Source    | Target          | Progress | Status         |
| --------- | --------------- | -------- | -------------- |
| Rudaw     | 400-600         | 0        | 🔴 Not started |
| BasNews   | 300-400         | 0        | 🔴 Not started |
| NRT       | 200-300         | 0        | 🔴 Not started |
| K24       | 100-200         | 0        | 🔴 Not started |
| **Total** | **1,000-1,500** | **0**    | **0%**         |

---

## ✅ Quality Checklist

**Good Sentence:**

- ✅ 10-25 words
- ✅ Full sentence (subject, verb, complete thought)
- ✅ Formal news language
- ✅ High ZWNJ usage (you'll see ‌ characters between words)
- ✅ Pure Kurdish script (>85%)

**Bad Sentence:**

- ❌ Too short (< 10 words) or too long (> 25 words)
- ❌ Headlines only
- ❌ Dates, timestamps, URLs
- ❌ Mixed English/Kurdish
- ❌ Author names, photo captions
- ❌ Social media quotes

---

## 🔍 Progress Commands

### Check Current Status

```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "python3 tools/collection_assistant.py corpus/kurdish_news_batch2.txt"
```

**Shows:**

- Current sentence count (X/1,000-1,500)
- Progress bar
- ZWNJ density
- Average words per sentence
- Problem sentences (if any)

### Count Lines Quickly

```bash
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && wc -l corpus/kurdish_news_batch2.txt"
```

---

## 📊 When You're Done (1,000+ sentences)

### 1. Clean Up File

- Remove header comments (lines starting with #)
- Remove blank lines
- One sentence per line only

### 2. Quality Check

```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "python3 tools/corpus_quality_checker.py corpus/kurdish_news_batch2.txt"
```

**Target**: A grade (90+/100) with:

- ZWNJ density: 10-12%
- Avg words: 15-20
- Kurdish purity: >90%

### 3. Create Batch 2 Corpus

```bash
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && cat corpus/ckb_phase4.training_text.backup corpus/kurdish_news_batch2.txt | sort -u > corpus/ckb_phase6_batch2.training_text"
```

### 4. Activate for Training

```bash
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && cp corpus/ckb_phase6_batch2.training_text corpus/ckb.training_text"
```

### 5. Train Models

```powershell
cd c:\tesseract
.\run_training.ps1 -Mode GenerateTrain
```

**Wait**: 3-5 hours for training to complete

### 6. Evaluate

```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/eval_real_cer.py"
```

### 7. Make Decision

- **If ≥72.5%** (+0.8%+): ✅ Success! Continue to Batch 3
- **If 72.0-72.4%**: ⚠️ Marginal, review quality
- **If <72.0%**: ❌ Try different approach

---

## 💡 Tips for Success

### 1. Work in Sessions

- Session 1: 250 sentences (2 hours)
- Session 2: 250 sentences (2 hours)
- Session 3: 250 sentences (1.5 hours)
- Session 4: 250 sentences (1.5 hours)
- **Total**: 1,000 sentences in 7 hours

### 2. Diversify Sources

- Don't collect >300 from one website
- Mix politics, economy, culture articles
- Avoid sports/entertainment (lower ZWNJ)

### 3. Focus on ZWNJ

- Look for formal political/government articles
- These naturally have more ZWNJ (10-12%)
- If collection assistant shows <9%, adjust source

### 4. Check Quality Often

- Run collection assistant every 100 sentences
- Fix issues early
- Maintain quality > quantity

### 5. Save Frequently

- Save file every 50 sentences
- Don't lose progress!

---

## 🌐 Direct Links

### Rudaw Sections

- Kurdistan: https://www.rudaw.net/sorani/kurdistan
- Politics: https://www.rudaw.net/sorani/middleeast
- Business: https://www.rudaw.net/sorani/business
- Culture: https://www.rudaw.net/sorani/culture

### BasNews

- Main: https://www.basnews.com/so/
- News: https://www.basnews.com/so/babat

### NRT

- Main: https://www.nrttv.com/so/
- News: https://www.nrttv.com/so/News.aspx

---

## ⏱️ Time Estimate

| Task          | Duration       | Type           |
| ------------- | -------------- | -------------- |
| Collection    | 5-7 hours      | Manual work    |
| Quality check | 15 minutes     | Semi-automated |
| Training      | 3-5 hours      | Automated      |
| Evaluation    | 15 minutes     | Automated      |
| **Total**     | **9-13 hours** | **1-2 days**   |

---

## 🎯 Success Metrics

### Phase 6 Batch 2 Goals

- **Minimum success**: 72.5% (+0.8%)
- **Target**: 73-73.5% (+1.3-1.8%)
- **Excellent**: 74%+ (+2.3%+)

### Why This Should Work

1. ✅ **Different source** (news vs Wikipedia)
2. ✅ **Higher ZWNJ** (10-12% vs 8-9%)
3. ✅ **Formal language** (professional journalism)
4. ✅ **More data** (1,000-1,500 vs 480)
5. ✅ **Vocabulary diversity** (politics, economy, culture)

---

## 🚀 Ready to Start?

**Your next action:**

1. Open `c:\tesseract\work\corpus\kurdish_news_batch2.txt` in a text editor
2. Visit https://www.rudaw.net/sorani/kurdistan
3. Find a substantial article (5+ paragraphs)
4. Copy article text
5. Paste sentences one per line
6. Repeat until 1,000-1,500 sentences

**Check progress anytime:**

```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "python3 tools/collection_assistant.py corpus/kurdish_news_batch2.txt"
```

---

**Good luck! This manual collection is our best chance to break through 72% accuracy.** 🎯
