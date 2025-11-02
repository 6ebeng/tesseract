# Phase 7 Quick Start Guide

**Goal:** Improve accuracy from 71.69% → 76%+ by finding high-quality biographical sources

---

## Step 1: Validate Potential Sources (START HERE) ✅

### 1a. Use Your Existing Scraper System

**You already have a production scraper** in `work/tools/scrapers/`

```bash
# See available websites
cd work/tools/scrapers
python3 generic_scraper.py --list

# Check scraper documentation
cat PRODUCTION_SCRAPER_USAGE.md
```

**Look for biographical sections:**
- News biography/profile articles
- Historical figures
- Cultural personalities
- Obituaries

**Or manually find:**
- Kurdish books (Archive.org, Google Books)
- Academic papers in Kurdish
- Kurdish literature

**Extract:** 100+ sentences as a sample

### 1b. Run Validation Tool

```bash
cd c:\tesseract
python work\tools\validate_source_quality.py samples\your_sample.txt
```

**Check output:**
- ✅ **ACCEPT** (ZWNJ 6-10%) → Use this source! 🎉
- ⚠️ **REVIEW** (borderline) → Check issues, may be usable
- ❌ **REJECT** (ZWNJ <6%) → Skip this source

### 1c. Document Results

Create a tracking file: `phase7_sources.txt`

```
Source Name         | ZWNJ%  | Status | Notes
--------------------|--------|--------|---------------------------
Archive.org Book1   | 8.5%   | ACCEPT | Historical biography
News Site Bio       | 7.2%   | ACCEPT | Modern biographies
Wikipedia Sample    | 0.1%   | REJECT | Too low, skip
```

**Target:** Find 3-5 sources with ZWNJ 6-10%

---

## Step 2: Acquire Full Text

Once you have validated sources (ACCEPT status):

### Option A: Manual Download
1. Download full text from source
2. Save as UTF-8 text file
3. Name: `source_name.txt`

### Option B: Use Scraper (if news website)
```bash
cd c:\tesseract\work\tools\scrapers
python scraper.py --url <source_url> --output ../../corpus/source_name.txt
```

---

## Step 3: Clean and Prepare Corpus

### 3a. Apply Kurdish Character Fixer

```bash
cd c:\tesseract\work
python kurdish_character_fixer.py --input corpus/source_name.txt --output corpus/source_name_fixed.txt
```

### 3b. Combine Sources

```bash
# Combine all your validated sources
cat corpus/source1_fixed.txt corpus/source2_fixed.txt > corpus/ckb_phase7_raw.txt
```

### 3c. Final Validation

```bash
# Check combined corpus quality
python tools\validate_source_quality.py corpus\ckb_phase7_raw.txt
```

**Must show:**
- ZWNJ: 6-10% ✅
- Kurdish script: >85% ✅
- Sentences: 500+ ✅

---

## Step 4: Build Balanced Corpus

Blend Phase 7 sources with existing high-quality news corpus:

```powershell
# Copy Phase 7 corpus to work directory
Copy-Item work\corpus\ckb_phase7_raw.txt work\corpus\ckb_phase7.training_text

# Build balanced corpus (blends with existing sources)
.\run_training.ps1 -Mode BuildCorpus -UseFixer -KeepRTLControls `
    -BalanceDigits -BalanceLatinDigits -BalancePuncs -CorpusMinCount 1
```

**This will:**
- Combine Phase 7 corpus with existing news corpus
- Balance digits and punctuation
- Apply character fixing
- Output: `work\corpus\ckb.training_text`

---

## Step 5: Train Model

```powershell
# Generate training data and train
.\run_training.ps1 -Mode GenerateTrain -LatinDigits
```

**Timeline:**
- Data generation: 2-4 hours
- Training: 8-12 hours
- **Total: ~16 hours**

---

## Step 6: Evaluate Results

### Quick Test (mgk.tif)
```powershell
.\run_training.ps1 -Mode SmokeTestBest
```

**Check result:**
- Current: 71.69%
- **Target: >76%** (improvement of 4.3%)

### Comprehensive Evaluation (Multiple PSM modes)
```powershell
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

**Compare:**
- mgk.tif (biographical): Current 71.69% → Target >76%
- News images: Current 76.9% → Maintain ≥76%

---

## Success Criteria

### ✅ Minimum Success
- mgk.tif: **74%** (+2.3%)
- News: ≥76% (maintain)

### 🎯 Target Success
- mgk.tif: **76%** (+4.3%)
- News: ≥76% (maintain)

### 🚀 Stretch Goal
- mgk.tif: **78%** (+6.3%)
- News: ≥77% (improve)

---

## Troubleshooting

### Problem: Can't find sources with >6% ZWNJ

**Solutions:**
1. Try Kurdish literature (books, poetry)
2. Try academic papers (university repositories)
3. Try biographical news sections (obituaries, profiles)
4. Consider Option C: Synthetic ZWNJ enhancement

### Problem: Sources have ZWNJ but wrong domain

**Solutions:**
1. Mix multiple domains (literature + news + academic)
2. Validate vocabulary overlap with mgk.tif
3. Test incrementally (add 100 sentences, evaluate, repeat)

### Problem: Training doesn't improve accuracy

**Check:**
1. Corpus ZWNJ density: Must be 7-9%
2. Script purity: Must be >85% Kurdish
3. Sentence quality: No encoding issues
4. Blend ratio: Not too much low-quality content

**If still no improvement:**
- Current model (71.69% / 76.9%) is solid for v1.0
- Deploy as production, revisit in v2.0

---

## Key Insights from Phase 6

### What We Learned

1. **ZWNJ is THE metric** (more important than corpus size)
   - 9.331% ZWNJ → 76.9% accuracy ✅
   - 0.106% ZWNJ → FAILED ❌

2. **Domain matters** (but ZWNJ matters more)
   - News corpus works great on news images
   - Need biographical corpus for biographical images
   - But both need high ZWNJ!

3. **Quality over quantity**
   - 1,000 sentences with 8% ZWNJ > 10,000 sentences with 0.1% ZWNJ
   - Always validate BEFORE training

4. **Current model is production-quality**
   - 76.9% on modern text is excellent
   - 71.69% on biographical is acceptable
   - Only improve if you find proper sources

---

## Tools Reference

### Validation Tool
```bash
python work\tools\validate_source_quality.py sample.txt
```

**Checks:**
- ZWNJ density (must be 6-10%)
- Script purity (must be >85% Kurdish)
- Sentence quality
- Provides ACCEPT/REVIEW/REJECT decision

### Unicode Analysis Tool
```bash
python work\analyze_unicode_chars.py corpus_file.txt
```

**Shows:**
- Detailed ZWNJ statistics
- Tatweel statistics
- Sentence coverage
- Character counts

### Character Fixer
```bash
python work\kurdish_character_fixer.py --input source.txt --output fixed.txt
```

**Fixes:**
- Character encoding issues
- Unicode normalization
- Kurdish-specific corrections

---

## Quick Command Reference

```powershell
# Validate source
python work\tools\validate_source_quality.py sample.txt

# Build corpus
.\run_training.ps1 -Mode BuildCorpus -UseFixer -KeepRTLControls `
    -BalanceDigits -BalanceLatinDigits -BalancePuncs -CorpusMinCount 1

# Train model
.\run_training.ps1 -Mode GenerateTrain -LatinDigits

# Quick test
.\run_training.ps1 -Mode SmokeTestBest

# Full evaluation
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

---

## Timeline Estimate

- **Week 1:** Find and validate sources (use validation tool)
- **Week 2:** Acquire and clean text
- **Week 3:** Build and validate corpus
- **Week 4:** Train and evaluate

**Total: 4 weeks** (can be faster if sources are readily available)

---

## Next Actions

1. **NOW:** Run validation tool on any sample text you have
2. **TODAY:** Start searching for Kurdish biographical sources
3. **THIS WEEK:** Validate 5-10 potential sources
4. **NEXT WEEK:** Acquire full text from accepted sources
5. **WEEK 3:** Build and validate Phase 7 corpus
6. **WEEK 4:** Train and evaluate!

---

Good luck! 🚀

**Remember:** ZWNJ density 6-10% is NON-NEGOTIABLE. Always validate BEFORE spending time on a source!
