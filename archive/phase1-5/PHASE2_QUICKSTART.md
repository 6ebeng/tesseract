# 🚀 Phase 2: Quick Start Guide

**Date:** October 9, 2025  
**Goal:** Extract 50,000+ words from Kurdish Wikipedia and retrain

---

## ⚡ Fast Track (2-3 hours total)

### Option A: Quick API Method (Recommended for testing)

**Advantages:**

- ✅ No large download needed
- ✅ Faster to start (5 minutes vs 30 minutes)
- ✅ Can specify exact word count
- ✅ Cleaner text (pre-processed by Wikipedia)

**Steps:**

```powershell
# 1. Install Python requests library (if not installed)
wsl -d Ubuntu -- bash -c "pip3 install requests || sudo apt-get install -y python3-requests"

# 2. Extract 50,000 words from Wikipedia
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/quick_wikipedia_extract.py \
    /mnt/c/tesseract/work/corpus/ckb_wikipedia.txt \
    50000

# Expected time: 30-45 minutes
# Output: ckb_wikipedia.txt with 50,000+ words

# 3. Merge with existing corpus
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/merge_corpus.py \
    /mnt/c/tesseract/work/corpus/ckb.training_text \
    /mnt/c/tesseract/work/corpus/ckb_wikipedia.txt \
    /mnt/c/tesseract/work/corpus/ckb.training_text

# Expected: ~65,000 total words

# 4. Verify corpus
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/check_source_zwnj.py

# Expected:
#   - 60,000+ words
#   - 40,000+ ZWNJs
#   - 7-9% ZWNJ percentage

# 5. Retrain with expanded corpus
.\run_training.ps1 -Mode GenerateTrain -MaxIters 50000 -LatinDigits -MaxPages 100 -CharsPerPage 3000

# Expected time: 3-4 hours
# Result: CER 10-15% (85-90% accuracy)
```

---

### Option B: Full Wikipedia Dump Method

**Advantages:**

- ✅ More comprehensive coverage
- ✅ Higher quality articles
- ✅ Can process offline after download

**Steps:**

```powershell
# 1. Create download directory
New-Item -ItemType Directory -Force -Path "C:\tesseract\work\corpus\wikipedia"

# 2. Download Wikipedia dump (50-100 MB, 10-15 minutes)
$url = "https://dumps.wikimedia.org/ckbwiki/latest/ckbwiki-latest-pages-articles.xml.bz2"
$output = "C:\tesseract\work\corpus\wikipedia\ckbwiki-latest.xml.bz2"

# Option 2a: PowerShell download
Invoke-WebRequest -Uri $url -OutFile $output

# Option 2b: Or use wget in WSL
wsl -d Ubuntu -- wget -O /mnt/c/tesseract/work/corpus/wikipedia/ckbwiki-latest.xml.bz2 \
    https://dumps.wikimedia.org/ckbwiki/latest/ckbwiki-latest-pages-articles.xml.bz2

# 3. Extract text (not implemented yet - see PHASE2_WIKIPEDIA_EXTRACTION.md for full script)
# For now, use Option A (API method) above
```

---

## 📊 Verification Steps

### Check Corpus Statistics

```powershell
wsl -d Ubuntu -- python3 << 'PYTHON'
text = open('/mnt/c/tesseract/work/corpus/ckb.training_text', 'r', encoding='utf-8').read()
lines = [l for l in text.split('\n') if l.strip()]
words = text.split()
zwnj = text.count('\u200c')

print("📊 Corpus Statistics:")
print(f"  Lines: {len(lines):,}")
print(f"  Words: {len(words):,}")
print(f"  Characters: {len(text):,}")
print(f"  ZWNJ count: {zwnj:,}")
print(f"  ZWNJ percentage: {(zwnj/len(text)*100):.2f}%")

# Target check
if len(words) >= 50000:
    print("\n✅ Target reached: 50,000+ words")
else:
    print(f"\n⚠️ Need {50000 - len(words):,} more words")

if 6.0 <= (zwnj/len(text)*100) <= 10.0:
    print("✅ ZWNJ percentage in target range (6-10%)")
else:
    print(f"⚠️ ZWNJ percentage out of range: {(zwnj/len(text)*100):.2f}%")
PYTHON
```

---

## 🎯 Expected Results

### Corpus Growth

| Metric     | Before Phase 2 | After Phase 2 | Change |
| ---------- | -------------- | ------------- | ------ |
| Words      | 14,456         | 65,000+       | +350%  |
| ZWNJ Count | 8,309          | 40,000+       | +380%  |
| Lines      | 5,261          | 12,000+       | +128%  |

### Accuracy Improvement

| Test     | Before | Target After | Expected Gain |
| -------- | ------ | ------------ | ------------- |
| CER      | 30-33% | 10-15%       | -18%          |
| Accuracy | 67-70% | 85-90%       | +18%          |

---

## 🚨 Troubleshooting

### Error: "requests module not found"

```bash
# Install requests
wsl -d Ubuntu -- pip3 install requests

# Or use system package
wsl -d Ubuntu -- sudo apt-get install -y python3-requests
```

### Error: "Connection timeout"

```bash
# Wikipedia API might be slow, increase timeout or try later
# Or use fewer articles at a time (reduce batch size)
```

### Error: "Low ZWNJ percentage"

```bash
# Filter more strictly
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/filter_wikipedia_quality.py \
    ckb_wikipedia.txt ckb_wikipedia_filtered.txt 5.0
# Last parameter (5.0) is minimum ZWNJ percentage
```

### Error: "Training takes too long"

```bash
# Start with fewer words (25,000) for faster testing
quick_wikipedia_extract.py ckb_wikipedia.txt 25000
```

---

## 📅 Timeline

### If starting now (October 9, 2:00 PM):

**2:00 PM** - Start Wikipedia extraction (API method)  
**2:45 PM** - Extraction complete, merge corpus  
**3:00 PM** - Start training  
**6:30 PM** - Training complete  
**7:00 PM** - Evaluation complete

**Total: ~5 hours**

---

## ✅ Success Criteria

**Minimum (Phase 2 Complete):**

- ✅ 50,000+ words in corpus
- ✅ CER < 20%
- ✅ Accuracy > 80%

**Good (Phase 2 Success):**

- ✅ 65,000+ words
- ✅ CER < 15%
- ✅ Accuracy > 85%

**Exceptional (Ahead of Schedule):**

- ✅ 80,000+ words
- ✅ CER < 12%
- ✅ Accuracy > 88%

---

## 🔄 Next Steps

**After Phase 2:**

**If CER < 15%:**
→ Proceed to Phase 3 (Advanced training techniques)

**If CER 15-20%:**
→ Extract more Wikipedia (target 100K words)
→ Quick retrain

**If CER < 10%:**
→ Skip Phase 3, go to Phase 4 (fine-tuning for 95%)

---

## 📝 Quick Commands Reference

```powershell
# Extract Wikipedia
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/quick_wikipedia_extract.py \
    /mnt/c/tesseract/work/corpus/ckb_wikipedia.txt 50000

# Check corpus stats
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/check_source_zwnj.py

# Merge corpus (if needed)
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/merge_corpus.py \
    existing.txt wikipedia.txt output.txt

# Train
.\run_training.ps1 -Mode GenerateTrain -MaxIters 50000 -LatinDigits -MaxPages 100

# Monitor
wsl -d Ubuntu -- python3 /mnt/c/tesseract/show_progress.py

# Evaluate
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

---

**Status:** 📋 READY TO START  
**Recommended:** Start with Option A (Quick API Method)  
**Next:** See PHASE2_WIKIPEDIA_EXTRACTION.md for full details
