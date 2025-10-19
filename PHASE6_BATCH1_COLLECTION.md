# Phase 6 Batch 1: Sentence Collection Guide

**Goal**: Collect 500 high-quality Kurdish sentences  
**Status**: 🟡 IN PROGRESS (0/500)

---

## 📋 Collection Checklist

### Rudaw (Target: 200 sentences)
- [ ] Politics section (50 sentences)
- [ ] Kurdistan news (50 sentences)
- [ ] Middle East (50 sentences)
- [ ] Business/Economy (50 sentences)

### BasNews (Target: 150 sentences)
- [ ] Local news (50 sentences)
- [ ] Regional news (50 sentences)
- [ ] Culture/Society (50 sentences)

### NRT (Target: 150 sentences)
- [ ] News articles (75 sentences)
- [ ] Reports (75 sentences)

---

## 🎯 Quality Criteria

### ✅ Good Sentences
- **Length**: 10-25 words
- **Style**: Formal, professional writing
- **ZWNJ**: Natural usage (8-12% density)
- **Script**: >85% Kurdish characters
- **Content**: Complete sentences from article body

### ❌ Avoid
- Headlines (too short)
- Dates and timestamps
- Author names and bylines
- URLs, emails, phone numbers
- Lists and bullet points
- Comments and social media
- Mixed language text

---

## 📝 How to Collect

### Step 1: Open News Website
Example: https://www.rudaw.net/sorani/kurdistan

### Step 2: Select an Article
- Choose a substantial article (not breaking news)
- Prefer: Politics, economy, culture, analysis
- Avoid: Live blogs, photo galleries, videos only

### Step 3: Copy Article Paragraphs
- Read the article
- Select paragraph text (not headlines)
- Copy to clipboard

### Step 4: Extract Sentences
- Paste into `kurdish_news_batch1.txt`
- **One sentence per line**
- Split long paragraphs into individual sentences
- Remove extra spaces

### Step 5: Quick Check
Every 50 sentences, run:
```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/collection_assistant.py"
```

This will show:
- Current count
- Progress bar
- Quality issues
- ZWNJ density
- Average sentence length

---

## 💡 Example Session

### Visit Rudaw Article
URL: `https://www.rudaw.net/sorani/kurdistan/1410202501`

### Copy Paragraph:
```
حکومەتی هەرێمی کوردستان ڕایگەیاند کە بەردەوامە لە چارەسەرکردنی کێشەکانی ئابووری. 
ئەم ڕاگەیاندنە لە کاتێکدا هات کە هەژمارێکی زۆر لە خەڵکی هەرێم داوای چارەسەری خێراتر 
دەکەن. بەپێی ڕاپۆرتەکان، حکومەت پلانی نوێی دانا بۆ باشترکردنی دۆخی ئابووری لە هەرێمدا.
```

### Extract to File (one per line):
```
حکومەتی هەرێمی کوردستان ڕایگەیاند کە بەردەوامە لە چارەسەرکردنی کێشەکانی ئابووری.
ئەم ڕاگەیاندنە لە کاتێکدا هات کە هەژمارێکی زۆر لە خەڵکی هەرێم داوای چارەسەری خێراتر دەکەن.
بەپێی ڕاپۆرتەکان، حکومەت پلانی نوێی دانا بۆ باشترکردنی دۆخی ئابووری لە هەرێمدا.
```

**Result**: 3 sentences added ✅

---

## 🚀 Quick Start Commands

### Check Progress Anytime
```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/collection_assistant.py"
```

### When Complete (500 sentences)
```bash
# 1. Remove comment lines from file (lines starting with #)
# 2. Run quality check
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/corpus_quality_checker.py corpus/kurdish_news_batch1.txt"

# 3. If quality is good (B grade or better), create batch
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/incremental_training.py create 1 corpus/kurdish_news_batch1.txt 500"
```

---

## 📊 Progress Tracking

Update this as you collect:

| Source | Target | Collected | Status |
|--------|--------|-----------|--------|
| Rudaw | 200 | 0 | 🔴 Not started |
| BasNews | 150 | 0 | 🔴 Not started |
| NRT | 150 | 0 | 🔴 Not started |
| **Total** | **500** | **0** | **0%** |

---

## 🎓 Pro Tips

### 1. Work in Batches
Collect 50 sentences, then check quality. Adjust if needed.

### 2. Diverse Sources
Don't collect all from one article. Spread across multiple topics.

### 3. Natural ZWNJ
Don't worry too much about ZWNJ while collecting. Natural Kurdish text 
usually has 8-12% ZWNJ density automatically.

### 4. Read First
Skim the article first. If it's high quality (formal, well-written), 
then collect from it. Skip informal or poorly written articles.

### 5. Save Often
Save the file frequently (Ctrl+S) so you don't lose progress.

---

## ❓ FAQ

**Q: How long will this take?**  
A: About 2-4 hours depending on typing speed and source availability.

**Q: Can I use other Kurdish news sites?**  
A: Yes! Any professional Kurdish news site works. K24, KurdPress, etc.

**Q: What if I can't find 500 sentences?**  
A: Start with what you can collect (even 250-300 is useful). We can add more in Batch 2.

**Q: Should I fix grammar/spelling errors?**  
A: No, keep the text as-is. We want real-world Kurdish text.

**Q: Can I copy from social media?**  
A: No, only professional sources (news, official, literature).

---

## 🎯 Next Steps After Collection

Once you have 500 sentences:
1. ✅ Remove comment lines (#) from file
2. ✅ Run quality check (should be B grade or better)
3. ✅ Create Batch 1 corpus
4. ✅ Train model (3-5 hours)
5. ✅ Evaluate accuracy
6. ✅ If improved → Continue to Batch 2
7. ✅ If not improved → Review quality and try different source

---

**Current File**: `c:\tesseract\work\corpus\kurdish_news_batch1.txt`  
**Check Progress**: `python3 tools/collection_assistant.py`  
**Target**: 500 sentences for 72.5-73% accuracy (+0.3% improvement)
