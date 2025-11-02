# Phase 7 Execution Plan - run_training.ps1 Workflow

**Created:** November 1, 2025  
**Status:** Ready to Execute

---

## 🎯 Decision Point: What to Do Next?

### Current State
- ✅ Phase 6 Complete: **76.9%** accuracy on news, **71.69%** on biographical
- ✅ Excellent news corpus: `ckb_scraped_filtered.training_text` (394 KB, **9.33% ZWNJ**)
- ✅ Production scraper ready: 14 websites, 6 with culture/poetry categories
- ✅ All tools ready: validator, blender, training pipeline

### Two Paths Forward

---

## 📊 OPTION A: Quick Training (Recommended Start)

**Goal:** Establish baseline with existing corpus  
**Time:** 12-16 hours  
**Risk:** Low (corpus already validated)

### Execute Now

```powershell
# Navigate to project root
cd c:\tesseract

# Generate training data and train with existing corpus
.\run_training.ps1 -Mode GenerateTrain -LatinDigits
```

**What this does:**
1. Uses existing `ckb_scraped_filtered.training_text` (9.33% ZWNJ ✅)
2. Generates training images with text2image
3. Trains LSTM model (8-12 hours)
4. Outputs: `work/training_output/ckb.traineddata`

### Expected Results
- News accuracy: **76-77%** (maintain or improve)
- Biographical: **72-74%** (slight improvement from balanced training)

### After Training

```powershell
# Quick test on mgk.tif
.\run_training.ps1 -Mode SmokeTestBest

# Full evaluation (multiple PSM modes)
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

### ✅ Advantages
- Fast path to results
- Establishes baseline
- Tests entire pipeline
- Can deploy if results good enough

### ⚠️ Limitations
- May not reach 76%+ on biographical text
- News-heavy corpus (not ideal for biographical domain)

---

## 🎯 OPTION B: Full Phase 7 (Maximum Accuracy)

**Goal:** Find biographical content, achieve 76%+ on biographical text  
**Time:** 2-4 weeks (depends on source availability)  
**Risk:** Medium (finding 6-10% ZWNJ sources)

### Step 1: Scrape Biographical Content

```bash
# Navigate to scraper
cd work/tools/scrapers

# Interactive menu (easiest)
./scrape.sh
# Select: Option 4 (Custom scraping)
# Websites: awene,balinde,rudaw,nrt,kurdistan24,kurdsat
# Categories: culture,poetry
```

**Or direct command:**

```bash
python3 run_production_display.py \
    --config configs/websites \
    --websites awene,balinde,rudaw,nrt \
    --categories culture,poetry \
    --parallel --workers 2
```

**Output:** `corpus/{website}/culture.txt`, `corpus/{website}/poetry.txt`

---

### Step 2: Combine & Validate

```bash
cd /mnt/c/tesseract/work

# Combine all biographical content
cat corpus/awene/culture.txt \
    corpus/balinde/culture.txt \
    corpus/balinde/poetry.txt \
    corpus/rudaw/culture.txt \
    corpus/nrt/culture.txt \
    > corpus/ckb_phase7_biographical_raw.txt

# Validate ZWNJ density (CRITICAL!)
python3 tools/validate_source_quality.py corpus/ckb_phase7_biographical_raw.txt
```

**Expected output:**
```
✅ ACCEPT - High Quality Source
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZWNJ Density: 7.8% ✅ (Target: 6-10%)
Kurdish Script: 99.2% ✅
Sentences: 847
Status: Ready for training 🚀
```

**If REJECT (<6% ZWNJ):**
- ❌ Don't use for training
- Try different sources (books, academic papers, literature)
- Consider Option A instead

---

### Step 3: Apply Character Fixing

```bash
cd /mnt/c/tesseract/work

# Fix encoding and normalization
python3 kurdish_character_fixer.py \
    --input corpus/ckb_phase7_biographical_raw.txt \
    --output corpus/ckb_phase7_biographical.training_text

# Validate after fixing (ZWNJ should still be 6-10%)
python3 tools/validate_source_quality.py corpus/ckb_phase7_biographical.training_text
```

---

### Step 4: Build Balanced Corpus

```powershell
cd c:\tesseract

# Build corpus blending news + biographical
.\run_training.ps1 -Mode BuildCorpus -UseFixer -KeepRTLControls `
    -BalanceDigits -BalanceLatinDigits -BalancePuncs -CorpusMinCount 1
```

**What this does:**
1. Combines all `.training_text` files in `work/corpus/`
2. Applies character fixing
3. Balances digits and punctuation
4. Outputs: `work/corpus/ckb.training_text`

**Verify blended corpus:**

```bash
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work && python3 tools/validate_source_quality.py corpus/ckb.training_text"
```

Should show: **7-9% ZWNJ** (balanced between news 9.3% and biographical ~7-8%)

---

### Step 5: Generate Training Data & Train

```powershell
cd c:\tesseract

# Generate images and train
.\run_training.ps1 -Mode GenerateTrain -LatinDigits
```

**Timeline:**
- Data generation: 2-4 hours
- Training: 8-12 hours
- **Total: 12-16 hours**

**Monitor progress:**

```powershell
# Check logs
Get-Content work\logs\training_*.log -Tail 50 -Wait

# Or WSL
wsl -d Ubuntu -- bash -c "tail -f /mnt/c/tesseract/work/logs/training_*.log"
```

---

### Step 6: Evaluate Results

```powershell
cd c:\tesseract

# Quick test on mgk.tif (biographical)
.\run_training.ps1 -Mode SmokeTestBest

# Full evaluation on multiple images with PSM sweep
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

**Success Criteria:**
- ✅ Minimum: mgk.tif **74%+** (2.3% improvement)
- 🎯 Target: mgk.tif **76%+** (4.3% improvement)
- 🚀 Stretch: mgk.tif **78%+** (6.3% improvement)
- ✅ Maintain: News **≥76%**

---

### Step 7: Compare with Baseline

```powershell
# Show evaluation results
Get-Content work\logs\eval_*.log | Select-String "Accuracy"

# Or detailed results
Get-Content work\real_gt\eval\*_results.txt
```

Compare:
- **Phase 6 baseline:** 71.69% (mgk.tif), 76.9% (news)
- **Phase 7 result:** Should be 76%+ (mgk.tif), ≥76% (news)

---

## 🤔 Which Option Should You Choose?

### Choose OPTION A if:
- ✅ You want quick results (12-16 hours)
- ✅ You want to test the pipeline first
- ✅ Current 71.69% is acceptable for v1.0
- ✅ You'll do Phase 7 later (v2.0)

### Choose OPTION B if:
- ✅ You need 76%+ on biographical text NOW
- ✅ You're willing to invest 2-4 weeks
- ✅ You can find/scrape biographical sources
- ✅ Sources validate at 6-10% ZWNJ

---

## 💡 Recommended Path: Hybrid Approach

**Best strategy:**

1. **Execute Option A first** (12-16 hours)
   - Establishes baseline
   - Tests pipeline
   - May be good enough!

2. **Evaluate Option A results**
   - If ≥74% on mgk.tif → ✅ Good enough for v1.0
   - If <74% on mgk.tif → Proceed to Option B

3. **If needed, execute Option B**
   - Now you know pipeline works
   - Can focus on finding quality sources
   - Have baseline to compare against

---

## 📋 Ready-to-Execute Commands

### For Option A (Quick Training):

```powershell
cd c:\tesseract

# Generate and train
.\run_training.ps1 -Mode GenerateTrain -LatinDigits

# After ~12-16 hours, evaluate
.\run_training.ps1 -Mode SmokeTestBest
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

### For Option B (Full Phase 7):

```bash
# 1. Scrape (WSL)
cd /mnt/c/tesseract/work/tools/scrapers
./scrape.sh  # Select culture/poetry

# 2. Validate (WSL)
cd /mnt/c/tesseract/work
cat corpus/awene/culture.txt corpus/balinde/culture.txt > corpus/ckb_phase7_biographical_raw.txt
python3 tools/validate_source_quality.py corpus/ckb_phase7_biographical_raw.txt

# 3. Fix characters (WSL)
python3 kurdish_character_fixer.py --input corpus/ckb_phase7_biographical_raw.txt --output corpus/ckb_phase7_biographical.training_text

# 4. Build corpus (PowerShell)
cd c:\tesseract
.\run_training.ps1 -Mode BuildCorpus -UseFixer -KeepRTLControls `
    -BalanceDigits -BalanceLatinDigits -BalancePuncs -CorpusMinCount 1

# 5. Train (PowerShell)
.\run_training.ps1 -Mode GenerateTrain -LatinDigits

# 6. Evaluate (PowerShell)
.\run_training.ps1 -Mode SmokeTestBest
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

---

## 🔧 Troubleshooting

### Training fails or crashes

**Check:**
```powershell
# View logs
Get-Content work\logs\training_*.log -Tail 100

# Check disk space
wsl -d Ubuntu -- bash -c "df -h /mnt/c/tesseract/work"

# Check corpus exists
Test-Path work\corpus\ckb.training_text
```

### Low accuracy after training

**Possible causes:**
1. Corpus ZWNJ density wrong (<6% or >10%)
2. Not enough training data
3. Character encoding issues
4. Corpus quality low (mixed languages, noise)

**Solutions:**
1. Validate corpus with `validate_source_quality.py`
2. Check corpus size (should be 500+ sentences)
3. Review `kurdish_character_fixer.py` logs
4. Check training logs for errors

---

## 📊 Monitoring Training Progress

### Check Training Status

```powershell
# Real-time log monitoring
Get-Content work\logs\training_*.log -Tail 50 -Wait

# Check iteration progress
wsl -d Ubuntu -- bash -c "grep -i 'iteration' /mnt/c/tesseract/work/logs/training_*.log | tail -20"

# Check training output directory
Get-ChildItem work\training_output\ckb\*
```

### Training Output Files

During training, you'll see:
- `ckb_checkpoint` - Training checkpoints
- `ckb.lstm` - Model file
- `*.traineddata` - Final trained model

---

## ✅ Success Checklist

### Before Training
- [ ] Corpus exists: `work/corpus/*.training_text`
- [ ] Corpus validated (6-10% ZWNJ if Phase 7)
- [ ] Sufficient disk space (20+ GB free)
- [ ] WSL Ubuntu working
- [ ] All tools available

### During Training
- [ ] Logs updating (`work/logs/training_*.log`)
- [ ] No error messages
- [ ] Training output files created
- [ ] Iteration count increasing

### After Training
- [ ] Model file exists: `work/training_output/ckb.traineddata`
- [ ] Smoke test passes
- [ ] Evaluation complete
- [ ] Results documented

---

## 🎯 What I Recommend Now

**Start with Option A:**

```powershell
cd c:\tesseract
.\run_training.ps1 -Mode GenerateTrain -LatinDigits
```

**Why:**
1. Your existing corpus (9.33% ZWNJ) is excellent quality
2. Establishes baseline in 12-16 hours
3. Tests entire pipeline
4. Results may be good enough (72-74% on biographical)
5. If not enough, you can do Option B later

**After 12-16 hours, evaluate:**

```powershell
.\run_training.ps1 -Mode SmokeTestBest
```

**Decision point:**
- If ≥74% on mgk.tif → ✅ Deploy as v1.0
- If <74% on mgk.tif → Proceed with Option B (scrape biographical content)

---

**Ready to start?** Just run:

```powershell
cd c:\tesseract
.\run_training.ps1 -Mode GenerateTrain -LatinDigits
```

---

**Status:** ✅ Ready to Execute  
**Last Updated:** November 1, 2025  
**Next Action:** Choose Option A or B and execute
