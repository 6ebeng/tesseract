# Phase 6: Quick Start Guide

**Goal**: Reach 80% accuracy through incremental high-quality corpus expansion  
**Current**: 72.19% (Phase 4 Farsi checkpoint)  
**Gap**: Need +7.81 percentage points

---

## ✅ Infrastructure Ready

Created tools:

- `tools/scrape_kurdish_news.py` - News scraper (template)
- `tools/corpus_quality_checker.py` - Quality analyzer ✅
- `tools/incremental_training.py` - Batch training manager ✅

**Phase 4 corpus baseline**: B grade (80/100)

- 3,278 lines
- 8.15% ZWNJ density ✅
- 17.4 avg words/line ✅
- 97.6% Kurdish purity ✅

---

## 🚀 Next Step: Collect First Batch (500 Lines)

### Option 1: Manual Collection (Fastest to Start)

**Sources to visit**:

1. **Rudaw** - https://www.rudaw.net/sorani

   - Navigate to: Kurdistan, Middleeast, Business sections
   - Copy article paragraphs (not headlines/dates)
   - Target: 200 lines

2. **BasNews** - https://www.basnews.com

   - Kurdish language section
   - Copy article content
   - Target: 150 lines

3. **NRT** - https://www.nrttv.com
   - News articles in Kurdish
   - Copy paragraphs
   - Target: 150 lines

**Quality guidelines**:

- ✅ One sentence per line
- ✅ 10-25 words per sentence
- ✅ Formal writing style (news/official)
- ✅ Proper ZWNJ usage (should look natural)
- ❌ No headlines, dates, author names
- ❌ No URLs, email addresses, phone numbers
- ❌ No lists or bullet points

**Where to save**: `work/corpus/kurdish_news_batch1.txt`

---

### Option 2: Automated Scraping (Requires Setup)

**Install dependencies**:

```bash
wsl -d Ubuntu
cd /mnt/c/tesseract/work
pip3 install requests beautifulsoup4
```

**Then customize** `tools/scrape_kurdish_news.py`:

- Update CSS selectors for each news site
- Implement pagination logic
- Add error handling

**Run scraper**:

```bash
python3 tools/scrape_kurdish_news.py
```

---

## 📋 Workflow: Process Batch 1

### Step 1: Create Batch Corpus

```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/incremental_training.py create 1 corpus/kurdish_news_batch1.txt 500"
```

This will:

- ✅ Combine Phase 4 (3,278 lines) + new lines (500)
- ✅ Check for duplicates
- ✅ Create `corpus/ckb_phase6_batch1.training_text` (3,778 lines)
- ✅ Run quality checker
- ✅ Activate as `corpus/ckb.training_text`

### Step 2: Train Model

```powershell
cd c:\tesseract
.\run_training.ps1 -Mode GenerateTrain
```

**Expected time**: 3-5 hours

### Step 3: Evaluate Accuracy

```bash
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/eval_real_cer.py"
```

### Step 4: Record Results

```bash
# Example if accuracy is 72.8%
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/incremental_training.py record 1 3778 72.8 0.272"
```

### Step 5: Decision

**If accuracy improved** (+0.3% or more):

- ✅ Keep batch
- ✅ Continue to Batch 2
- 🎯 Add next 500 lines

**If no improvement** (±0.0%):

- ⚠️ Review quality of new lines
- 🔄 Try different source
- ❓ Consider smaller batches (250 lines)

**If accuracy decreased**:

- ❌ Discard batch
- 🔍 Investigate quality issues
- 🔄 Use different source

---

## 📊 Expected Progress

| Batch | Total Lines | Target Accuracy | Source                |
| ----- | ----------- | --------------- | --------------------- |
| Start | 3,278       | 72.19%          | Phase 4 baseline      |
| 1     | 3,778       | 72.5-73.0%      | News (500)            |
| 2     | 4,278       | 73.0-73.5%      | News (500)            |
| 3     | 4,778       | 73.5-74.5%      | News (500)            |
| 4     | 5,278       | 74.5-75.5%      | News (500)            |
| 5     | 5,778       | 75.5-76.5%      | News + Official (500) |
| 6     | 6,278       | 76.5-77.5%      | Official (500)        |
| 7     | 6,778       | 77.5-78.5%      | Literature (500)      |
| 8     | 7,278       | 78.5-79.5%      | Mixed (500)           |
| 9     | 7,778       | 79.5-80%+       | High-ZWNJ (500)       |

**Timeline**: 2-3 weeks (depending on collection/training speed)

---

## 🎯 Success Criteria

**Minimum (acceptable)**:

- Reach 75% accuracy
- Add 1,500+ quality lines

**Target (good)**:

- Reach 78% accuracy
- Add 3,000+ quality lines

**Excellent (goal)**:

- Reach 80%+ accuracy
- Add 5,000+ quality lines
- Enable ZWNJ rules (60-75% recovery)

---

## 🚨 Important Notes

**Quality > Quantity**:

- Phase 5 added 4,074 lines and FAILED
- Phase 6 adds 500 lines at a time with EVALUATION
- Only keep batches that improve accuracy

**ZWNJ Density**:

- Maintain 8-12% (Phase 4 has 8.15%)
- Too low (<6%): Won't help ZWNJ recognition
- Too high (>15%): May be artificial/incorrect

**Kurdish Purity**:

- Maintain >85% (Phase 4 has 97.6%)
- Avoid mixing too much Latin script
- Professional Kurdish writing

---

## 💡 Tips for Collection

**Good sources**:

- ✅ News articles (main content, not comments)
- ✅ Official government announcements
- ✅ Published books/literature
- ✅ Academic papers
- ✅ Professional blogs

**Avoid**:

- ❌ Social media posts (informal)
- ❌ Comments/forums (quality varies)
- ❌ Machine-translated text
- ❌ Mixed-language content
- ❌ Lists, tables, menus

**Quality checks**:

1. Read 5 random sentences - do they look professional?
2. Check ZWNJ usage - does it look natural?
3. Verify Kurdish script - minimal Latin mixing?
4. Sentence length - not too short/long?

---

## 🔄 Ready to Start?

**Quick start (manual collection)**:

1. Visit Rudaw/BasNews/NRT
2. Copy 500 quality sentences to `work/corpus/kurdish_news_batch1.txt`
3. Run: `python3 tools/incremental_training.py create 1 corpus/kurdish_news_batch1.txt 500`
4. Train: `.\run_training.ps1 -Mode GenerateTrain`
5. Evaluate and decide whether to continue

**Questions?** Check `PHASE6_STRATEGIC_PLAN.md` for full details.

---

**Current status**: ✅ Infrastructure ready  
**Next action**: Collect first 500 high-quality Kurdish sentences  
**Goal**: Reach 80% accuracy for effective ZWNJ recovery
