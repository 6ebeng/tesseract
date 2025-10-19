# 🚀 Phase 6 Batch 2 - NOW READY!

**Date**: October 16, 2025  
**Status**: ✅ **READY FOR MANUAL COLLECTION**

---

## 📊 Batch 1 Summary (FAILED)

- ❌ **Result**: 71.69% accuracy (0.00% improvement)
- ❌ **Problem**: Wikipedia source insufficient, training reused old checkpoints
- ✅ **Lesson**: Need different source with more data

---

## 🎯 Batch 2 Plan (CURRENT)

### What's Different?
1. ✅ **Source**: Professional Kurdish news (NOT Wikipedia)
2. ✅ **Amount**: 1,000-1,500 sentences (vs 480)
3. ✅ **ZWNJ**: Target 10-12% (vs 8.25%)
4. ✅ **Diversity**: Multiple news sites and topics

### Expected Results
- **Minimum**: 72.5% (+0.8%) → Keep and continue
- **Target**: 73-73.5% (+1.3-1.8%) → Strong success
- **Excellent**: 74%+ (+2.3%+) → Breakthrough!

---

## 📝 YOUR TASK: Collect 1,000-1,500 Sentences

### Files Created for You
1. ✅ `work/corpus/kurdish_news_batch2.txt` - Collection file (empty, ready)
2. ✅ `BATCH2_QUICKSTART.md` - Detailed instructions
3. ✅ `tools/collection_assistant.py` - Progress tracker (already working)

### Quick Start

**Step 1**: Open the collection file
```
File: c:\tesseract\work\corpus\kurdish_news_batch2.txt
Tool: Any text editor (Notepad, VS Code, etc.)
```

**Step 2**: Visit Kurdish news sites
- Rudaw: https://www.rudaw.net/sorani/kurdistan
- BasNews: https://www.basnews.com/so/
- NRT: https://www.nrttv.com/so/

**Step 3**: Copy article text
- Click on full articles (not headlines)
- Copy main paragraphs (5-10 per article)
- Avoid: Headlines, dates, author names, photos

**Step 4**: Add to file
- Paste sentences **one per line**
- Split paragraphs into individual sentences
- Remove blank lines
- Keep only 10-25 word sentences

**Step 5**: Check progress
```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "python3 tools/collection_assistant.py corpus/kurdish_news_batch2.txt"
```

---

## 📋 Collection Targets

| Source | Target Sentences | Status |
|--------|-----------------|--------|
| Rudaw | 400-600 | 🔴 0 collected |
| BasNews | 300-400 | 🔴 0 collected |
| NRT | 200-300 | 🔴 0 collected |
| K24 (optional) | 100-200 | 🔴 0 collected |
| **TOTAL** | **1,000-1,500** | **0 / 1,000** |

---

## ⏱️ Time Estimate

- **Collection**: 5-7 hours (manual work, can split over multiple days)
- **Training**: 3-5 hours (automated, run overnight)
- **Evaluation**: 15 minutes (automated)

---

## ✅ Quality Guidelines

### Good Sentence Example:
```
حکومەتی هەرێمی کوردستان لە کۆبوونەوەیەکی ئاساییدا چەندین بڕیاری گرنگی دەرکرد.
```
- ✅ 10-17 words
- ✅ Formal news language
- ✅ Complete sentence
- ✅ High ZWNJ usage (‌ between words)

### Bad Sentence Examples:
```
سەرەتا                          ❌ Too short
BREAKING NEWS                   ❌ English
١٥ تشرینی یەکەم ٢٠٢٥         ❌ Date only
www.rudaw.net                   ❌ URL
```

---

## 🔄 After Collection (When you have 1,000+ sentences)

### 1. Clean the file
- Remove header comments (# lines)
- Remove blank lines
- One sentence per line only

### 2. Quality check
```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "python3 tools/corpus_quality_checker.py corpus/kurdish_news_batch2.txt"
```
**Target**: A grade (90+/100)

### 3. Create Batch 2 corpus
```bash
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && cat corpus/ckb_phase4.training_text.backup corpus/kurdish_news_batch2.txt | sort -u > corpus/ckb_phase6_batch2.training_text && cp corpus/ckb_phase6_batch2.training_text corpus/ckb.training_text"
```

### 4. Train
```powershell
cd c:\tesseract
.\run_training.ps1 -Mode GenerateTrain
```
**Wait**: 3-5 hours

### 5. Evaluate
```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/eval_real_cer.py"
```

### 6. Make decision
- ✅ If ≥72.5%: SUCCESS! Continue to Batch 3
- ⚠️ If 72.0-72.4%: Review and maybe keep
- ❌ If <72.0%: Try different approach

---

## 💡 Pro Tips

1. **Work in sessions**: 250 sentences per 2-hour session
2. **Save often**: Every 50 sentences
3. **Check progress**: Run collection assistant every 100 sentences
4. **Diverse sources**: Don't collect >300 from one site
5. **Focus on politics/economy**: Higher ZWNJ than sports/entertainment

---

## 🌐 Direct Links

### Rudaw
- Kurdistan: https://www.rudaw.net/sorani/kurdistan
- Politics: https://www.rudaw.net/sorani/middleeast
- Business: https://www.rudaw.net/sorani/business

### BasNews
- Main: https://www.basnews.com/so/

### NRT
- Main: https://www.nrttv.com/so/

---

## 📞 Quick Commands Reference

```bash
# Check progress
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "python3 tools/collection_assistant.py corpus/kurdish_news_batch2.txt"

# Count lines
wsl -d Ubuntu -- bash -lc "wc -l c:/tesseract/work/corpus/kurdish_news_batch2.txt"

# Quality check (when done)
wsl -d Ubuntu -- bash -lc "python3 tools/corpus_quality_checker.py corpus/kurdish_news_batch2.txt"
```

---

## 🎯 Why This Should Work

1. ✅ **Different source**: News ≠ Wikipedia (new patterns)
2. ✅ **More data**: 1,000-1,500 vs 480 (stronger signal)
3. ✅ **Higher ZWNJ**: 10-12% vs 8-9% (better quality)
4. ✅ **Formal language**: Professional journalism
5. ✅ **Corpus increase**: 30-40% vs 11% (meaningful change)

---

## 📁 Files Ready

- ✅ `work/corpus/kurdish_news_batch2.txt` (collection file)
- ✅ `BATCH2_QUICKSTART.md` (detailed guide)
- ✅ `PHASE6_BATCH2_PLAN.md` (strategy document)
- ✅ `PHASE6_BATCH1_RESULTS.md` (failure analysis)
- ✅ `tools/collection_assistant.py` (progress tracker)
- ✅ `tools/corpus_quality_checker.py` (quality analyzer)

---

## 🚀 START NOW!

**Your immediate next step:**

1. Open: `c:\tesseract\work\corpus\kurdish_news_batch2.txt`
2. Visit: https://www.rudaw.net/sorani/kurdistan
3. Find an article with 5+ paragraphs
4. Copy the article body text
5. Paste sentences one per line into the file
6. Repeat until you have 1,000-1,500 sentences

**This is our best chance to break through 72% accuracy!** 🎯

Let me know when you've collected the sentences and I'll help you with the next steps (training and evaluation).
