# Ready to Improve Accuracy to 80%+

## Current Status
- **Batch 2 Model:** 76.90% average accuracy on modern Kurdish news
- **Training Data:** 4,686 sentences (too few for optimal performance)
- **Target:** 80-85% accuracy

## Solution: Expand Training Data

### Why More Data = Better Accuracy

**Industry Best Practice:**
- Good OCR: 10,000-20,000 sentences
- Current: 4,686 sentences (**47% of minimum**)
- Batch 3 Target: 8,000+ sentences (**80% of minimum**)

**Expected Improvement:**
- Current: 76.90% average
- **Batch 3 Target: 80%+ average** (+3-4%)

---

## One Command to Start

```powershell
.\run_training.ps1 -Mode ExpandCorpus
```

**What it does:**
1. Scrapes 3,500+ new Kurdish sentences
2. From 4 proven sources: Kurdsat, Rudaw, Khak TV, **NRT TV** (new!)
3. Quality filtered (10-30 words, >70% Kurdish)
4. Deduplicated automatically
5. Saves to: `work/corpus/kurdish_expanded_batch3.txt`

**Time:** 40-75 minutes  
**Safe:** 1-hour timeout, saves partial results

---

## After Collection Completes

### Step 1: Review Quality (2 minutes)

```powershell
# Check how many sentences collected
wsl -d Ubuntu -- wc -l /mnt/c/tesseract/work/corpus/kurdish_expanded_batch3.txt

# Preview first 20 sentences
wsl -d Ubuntu -- head -20 /mnt/c/tesseract/work/corpus/kurdish_expanded_batch3.txt
```

### Step 2: Combine with Existing Corpus (1 minute)

```powershell
# Combine Batch 2 + Batch 3
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work && cat corpus/ckb_phase6_batch2.training_text corpus/kurdish_expanded_batch3.txt | grep -v '^#' | grep -v '^$' | sort -u > corpus/ckb_phase6_batch3.training_text"

# Quality check
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work && python3 tools/corpus_quality_checker.py corpus/ckb_phase6_batch3.training_text"

# Activate for training
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work && cp corpus/ckb_phase6_batch3.training_text corpus/ckb.training_text"
```

### Step 3: Retrain Model (Overnight)

```powershell
# Start training (8-12 hours)
.\run_training.ps1 -Mode GenerateTrain
```

### Step 4: Validate Results (Tomorrow Morning)

```powershell
# Test on all images
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"

# Check results in work/output/real_metrics.csv
```

---

## Expected Results

### Before (Batch 2)
| Image | Accuracy | Type |
|-------|----------|------|
| rudaw2 | 82.17% | Short news |
| rudaw1 | 78.28% | Mixed news |
| kurdsat3 | 73.77% | Political |
| kurdsat2 | 73.38% | Political |
| mgk | 71.69% | Traditional |
| **AVERAGE** | **76.90%** | **Modern news** |

### After (Batch 3 - Expected)
| Image | Accuracy | Gain | Type |
|-------|----------|------|------|
| rudaw2 | **84-85%** | +2-3% | Short news |
| rudaw1 | **80-81%** | +2-3% | Mixed news |
| kurdsat3 | **76-77%** | +2-3% | Political |
| kurdsat2 | **76-77%** | +2-3% | Political |
| mgk | **74-76%** | +3-5% | Traditional |
| **AVERAGE** | **80-82%** | **+3-5%** | **Modern news** |

---

## Why This Will Work

1. **60% More Training Data**
   - Current: 4,686 sentences
   - Batch 3: ~7,500 sentences
   - Closer to industry minimum (10K)

2. **Same Proven Sources**
   - Kurdsat: Worked in Batch 2 ✅
   - Rudaw: Worked in Batch 2 ✅
   - Khak TV: Worked in Batch 2 ✅
   - Just scraping MORE from each

3. **LSTM Networks Love Data**
   - More examples = Better generalization
   - Diminishing returns after 20K
   - Sweet spot: 10-15K sentences

---

## If Batch 3 Doesn't Reach 80%

### Backup Plan: Batch 4 (Traditional Texts)

**Collect:**
- Kurdish religious texts
- Classical literature
- Historical documents

**Benefit:**
- Improve mgk.tif from 72% to 76%+
- Two specialized models (modern + traditional)

**Timeline:** Another 24-36 hours

---

## Timeline

| Step | Duration | When |
|------|----------|------|
| **Collection** | 30-60 min | Now |
| **Review & Combine** | 3 min | After collection |
| **Training** | 8-12 hours | Tonight (overnight) |
| **Validation** | 15 min | Tomorrow morning |
| **Total** | ~12 hours | 24 hours wall time |

---

## Start Now

```powershell
.\run_training.ps1 -Mode ExpandCorpus
```

Then follow the steps above after completion!

---

**Goal:** 80%+ accuracy  
**Method:** More training data  
**Timeline:** 24 hours  
**Risk:** Low (proven approach)

