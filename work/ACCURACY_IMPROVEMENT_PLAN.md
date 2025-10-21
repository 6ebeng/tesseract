# Kurdish OCR Accuracy Improvement Plan

**Current Status:** 76.90% average on modern news  
**Target:** 80-85% accuracy  
**Approach:** Data-driven training improvement

---

## Strategy: Quality Training Data Expansion

### Why This Will Work

1. **More diverse sources** = Better generalization
2. **10,000+ sentences** = Industry standard for good LSTM training
3. **Current: 4,686 sentences** = Too few for optimal performance
4. **Best practice: 10-20K sentences** for production-quality OCR

### Batch 3 Plan: Expand Training Data 107%

**Current Corpus:**

- Phase 4 (Wikipedia): 3,321 sentences
- Batch 2 (News): 1,408 sentences (Kurdsat, Rudaw, Khak TV)
- **Total: 4,686 sentences**

**Batch 3 Target (6 sources):**

- Kurdsat: ~1,000 sentences (30 clicks, 2x Batch 2)
- Rudaw: ~1,000 sentences (20 scrolls, 2x Batch 2)
- Khak TV: ~500 sentences (10 pages, 2x Batch 2)
- **NRT TV: ~1,000 sentences (NEW! 15 clicks + 50 articles)**
- **Awene: ~700 sentences (NEW! 10 pages + 50 articles)**
- **Kurdistan24: ~800 sentences (NEW! 10 pages via FlareSolverr)**
- **New Total: 5,000+ sentences**

**Combined Total: 9,700+ sentences (107% increase!)**

---

## Implementation Steps

### Step 1: Corpus Expansion ✅ Ready

**Command:**

```powershell
.\run_training.ps1 -Mode ExpandCorpus
```

**What it does:**

- Scrapes Kurdsat (30 clicks, 2x more than Batch 2)
- Scrapes Rudaw (20 scrolls, 2x more than Batch 2)
- Scrapes Khak TV (10 pages, 2x more than Batch 2)
- **Scrapes NRT TV (NEW! 15 clicks + 50 article visits)**
- **Scrapes Awene (NEW! 10 pages + 50 articles)**
- **Scrapes Kurdistan24 (NEW! 10 pages via FlareSolverr)**
- Quality filtering (10-30 words, >70% Kurdish purity)
- Auto-deduplication
- Saves to `work/corpus/kurdish_expanded_batch3.txt`

**Prerequisites:**

- FlareSolverr running: `sudo docker start flaresolverr`

**Estimated time:** 50-90 minutes  
**Expected output:** 5,000+ new sentences

### Step 2: Corpus Combination

**Manual steps:**

```powershell
# In WSL/Ubuntu
cd /mnt/c/tesseract/work

# Combine all corpora
cat corpus/ckb_phase6_batch2.training_text \
    corpus/kurdish_expanded_batch3.txt | \
    grep -v '^#' | grep -v '^$' | sort -u > \
    corpus/ckb_phase6_batch3.training_text

# Quality check
python3 tools/corpus_quality_checker.py corpus/ckb_phase6_batch3.training_text

# Activate for training
cp corpus/ckb_phase6_batch3.training_text corpus/ckb.training_text
```

### Step 3: Retrain Model

**Command:**

```powershell
.\run_training.ps1 -Mode GenerateTrain
```

**What it does:**

- Generates training images from 7,500+ sentences
- Trains 3 new models (fas, ara, eng bases)
- Takes ~8-12 hours (overnight)

### Step 4: Validate Results

**Command:**

```powershell
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

**What to expect:**

- Test on all 5 images (4 news + mgk.tif)
- Compare Batch 3 vs Batch 2
- **Target: 80%+ average** (currently 76.90%)

---

## Expected Improvements

### Conservative Estimate

| Metric               | Current (Batch 2) | Expected (Batch 3) | Gain  |
| -------------------- | ----------------- | ------------------ | ----- |
| **Average Accuracy** | 76.90%            | 79-80%             | +2-3% |
| **Best Case**        | 82.17%            | 84-85%             | +2%   |
| **Worst Case**       | 71.69%            | 74-76%             | +3-5% |

### Why This Works

1. **More examples = Better generalization**

   - Current: 4,686 sentences
   - Batch 3: 7,500+ sentences (60% increase)

2. **Diverse news sources**

   - Current: 3 sources (Kurdsat, Rudaw, Khak TV)
   - Batch 3: 6 sources (+ NRT, Awene, BasNews)
   - Different writing styles, vocabulary, topics

3. **Industry best practices**
   - Good LSTM OCR: 10-20K sentences
   - We'll have 7,500+ (approaching lower bound)
   - Further improvement possible with 10K+

---

## Alternative: Batch 4 (Traditional Texts)

**If Batch 3 doesn't reach 80%:**

### Collect Traditional Kurdish Texts

**Sources:**

- Kurdish religious texts (Quran translations, Islamic books)
- Classical Kurdish literature
- Historical documents
- Traditional poetry

**Characteristics:**

- High ZWNJ density (8-12%)
- Formal language
- Dense paragraphs

**Target:** Improve mgk.tif from 72% to 76%+

**Benefit:** Two specialized models

- Model 1 (Batch 3): Modern news (80%+)
- Model 2 (Batch 4): Traditional texts (76%+)

---

## Timeline

### Batch 3 Execution

| Step                   | Duration      | When                      |
| ---------------------- | ------------- | ------------------------- |
| **Corpus Expansion**   | 1 hour        | Now                       |
| **Quality Review**     | 30 min        | After scraping            |
| **Corpus Combination** | 15 min        | After review              |
| **Training**           | 8-12 hours    | Overnight                 |
| **Evaluation**         | 30 min        | Next morning              |
| **Total**              | **~14 hours** | **24-36 hours wall time** |

### Batch 4 (If Needed)

| Step                   | Duration      | When                      |
| ---------------------- | ------------- | ------------------------- |
| **Manual collection**  | 2-4 hours     | After Batch 3 results     |
| **Corpus preparation** | 1 hour        | Same day                  |
| **Training**           | 8-12 hours    | Overnight                 |
| **Evaluation**         | 30 min        | Next morning              |
| **Total**              | **~14 hours** | **24-36 hours wall time** |

---

## Technical Improvements (Optional)

### 1. Training Parameters Tuning

**Current:** Default Tesseract LSTM settings  
**Possible:**

- Increase `--max_iterations` (default: ~10K, try 20K)
- Adjust learning rate
- Modify layer architecture

**Expected gain:** +0.5-1%  
**Risk:** May overfit, longer training time

### 2. Font Expansion

**Current:** 9 Noto Naskh Arabic variants  
**Possible:**

- Add more Arabic fonts (Traditional, Diwani, Kufi)
- Add bold/italic variants
- Mix fonts in same training image

**Expected gain:** +1-2%  
**Benefit:** Better generalization to different print styles

### 3. Data Augmentation

**Current:** Clean rendered text only  
**Possible:**

- Add noise/blur
- Rotation/skew
- Compression artifacts
- Real scan simulation

**Expected gain:** +2-3%  
**Benefit:** More robust to real-world image quality

---

## Success Metrics

### Batch 3 Goals

| Metric               | Target     | Stretch Goal |
| -------------------- | ---------- | ------------ |
| **Average Accuracy** | **80%+**   | **82%+**     |
| **Modern News**      | **80-85%** | **85%+**     |
| **Traditional Text** | **74%+**   | **76%+**     |
| **Training Corpus**  | **7,500+** | **10,000+**  |

### Validation

**Must improve on ALL test images:**

- ✅ kurdsat2: 73.38% → 76%+
- ✅ kurdsat3: 73.77% → 76%+
- ✅ rudaw1: 78.28% → 80%+
- ✅ rudaw2: 82.17% → 84%+
- ✅ mgk: 71.69% → 74%+

**If ANY image regresses:** Investigate and fix before deployment

---

## Risk Mitigation

### Risk 1: Scraping Fails

**Mitigation:**

- Timeout: 1 hour (saves partial results)
- Multiple sources (if one fails, others succeed)
- Quality filtering (only accept good sentences)

### Risk 2: Low Quality Data

**Mitigation:**

- Quality checker: 10-30 words, >70% Kurdish purity
- Manual review before combining
- Can discard bad sources

### Risk 3: No Improvement

**Mitigation:**

- Keep Batch 2 model (76.90% is good)
- Try Batch 4 (traditional texts)
- Try technical improvements (fonts, augmentation)

### Risk 4: Training Time

**Mitigation:**

- Run overnight
- Can pause/resume if needed
- ~12 hours should be sufficient

---

## Execution Plan

### Today (Step 1-2: Collection & Review)

```powershell
# 1. Start corpus expansion
.\run_training.ps1 -Mode ExpandCorpus

# 2. Wait 30-60 minutes for completion

# 3. Review results
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && wc -l corpus/kurdish_expanded_batch3.txt"
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && head -30 corpus/kurdish_expanded_batch3.txt"

# 4. Combine corpora (if quality is good)
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && cat corpus/ckb_phase6_batch2.training_text corpus/kurdish_expanded_batch3.txt | grep -v '^#' | grep -v '^$' | sort -u > corpus/ckb_phase6_batch3.training_text"

# 5. Quality check
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/corpus_quality_checker.py corpus/ckb_phase6_batch3.training_text"

# 6. Activate for training
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && cp corpus/ckb_phase6_batch3.training_text corpus/ckb.training_text"
```

### Tonight (Step 3: Training)

```powershell
# Start training (will run 8-12 hours)
.\run_training.ps1 -Mode GenerateTrain
```

### Tomorrow (Step 4: Validation)

```powershell
# Evaluate on all test images
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"

# Check if we hit 80%+ target
# If yes: Deploy Batch 3 model
# If no: Try Batch 4 or technical improvements
```

---

## Next Steps

**Run this command to start:**

```powershell
.\run_training.ps1 -Mode ExpandCorpus
```

This will collect 3,000+ new Kurdish sentences and save to:
`work/corpus/kurdish_expanded_batch3.txt`

After collection completes, review the file and proceed with combining and training!

---

**Status:** Ready to execute  
**Expected outcome:** 80%+ accuracy (from current 76.90%)  
**Timeline:** 24-36 hours total
