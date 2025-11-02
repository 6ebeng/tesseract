# Phase 7 Complete Guide - Kurdish OCR Training

**Goal:** Improve biographical text accuracy from 71.69% → 76%+ by finding Kurdish biographical sources with 6-10% ZWNJ density.

**Status:** ✅ All tools ready | 🔍 Ready to begin source collection

---

## 📋 Quick Overview

### Current State (Phase 6 Complete)

- **News accuracy:** 76.9% ✅ (production-ready)
- **Biographical accuracy:** 71.69% (target: 76%+)
- **News corpus quality:** 9.33% ZWNJ ✅ (excellent)
- **Training system:** Fully automated pipeline

### Phase 7 Goal

- **Find:** 500-1,000 biographical sentences with 6-10% ZWNJ
- **Train:** New model with blended corpus (news + biographical)
- **Achieve:** 76%+ accuracy on biographical text (mgk.tif)
- **Maintain:** ≥76% accuracy on news images

### Critical Success Factor

**ZWNJ Density 6-10% is MANDATORY**

- News (9.3% ZWNJ) → 76.9% accuracy ✅
- Wikipedia (0.1% ZWNJ) → FAILED ❌
- **Always validate BEFORE acquiring full text**

---

## 🚀 Getting Started

### Your Existing Tools

You have a **complete production scraper system** in `work/tools/scrapers/`:

1. **Production scraper** - 14 Kurdish news websites configured
2. **Interactive launcher** - `scrape.sh` with menu
3. **Live dashboard** - Real-time progress monitoring
4. **Documentation** - Complete usage guide

**New Phase 7 tools** in `work/tools/`:

1. **validate_source_quality.py** - Quick ACCEPT/REJECT based on ZWNJ
2. **blend_corpus.py** - Mix sources to target ZWNJ density
3. **analyze_unicode_chars.py** - Detailed ZWNJ/Unicode analysis

---

## 📖 Phase 7 Workflow

### Step 1: Use Your Scraper for Biographical Content

#### Check Available Categories

Your scraper has **14 websites** with these biographical categories:

| Website         | Categories               | Best For             |
| --------------- | ------------------------ | -------------------- |
| **awene**       | culture, poetry, society | Biography profiles   |
| **balinde**     | culture, poetry          | Cultural figures     |
| **kurdistan24** | culture, arts            | Artist profiles      |
| **rudaw**       | culture, lifestyle       | Historical figures   |
| **nrt**         | culture, society         | Obituaries, profiles |
| **kurdsat**     | culture                  | Limited content      |

#### Scrape Biographical Content

**Method 1: Interactive Menu (Recommended)**

```bash
cd /mnt/c/tesseract/work/tools/scrapers
./scrape.sh
# Select option 4 (Custom scraping)
# Enter websites: awene,balinde,rudaw
# Enter categories: culture,poetry
```

**Method 2: Direct Command**

```bash
cd /mnt/c/tesseract/work/tools/scrapers

# Scrape culture/poetry from multiple sites
python3 run_production_display.py \
    --config configs/websites \
    --websites awene,balinde,rudaw,nrt \
    --categories culture,poetry \
    --parallel --workers 2
```

**Method 3: Test Single Site First**

```bash
# Test one site to check quality
python3 run_production_display.py \
    --config configs/websites \
    --websites awene \
    --categories culture \
    --workers 1
```

---

### Step 2: Validate Scraped Content

**ALWAYS validate BEFORE training!**

#### Combine Scraped Files

```bash
cd /mnt/c/tesseract/work

# Combine all biographical content
cat corpus/awene/culture.txt \
    corpus/balinde/culture.txt \
    corpus/rudaw/culture.txt \
    > corpus/ckb_phase7_raw.txt
```

#### Validate ZWNJ Density

```bash
python3 tools/validate_source_quality.py corpus/ckb_phase7_raw.txt
```

**Expected Output:**

```
✅ ACCEPT - High Quality Source
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZWNJ Density: 8.5% ✅ (Target: 6-10%)
Kurdish Script: 99.5% ✅
Sentences: 892
Status: Ready for training 🚀
```

**If REJECT (<6% ZWNJ):**

- ❌ Don't use for training
- Try different categories (poetry instead of culture)
- Try older news sites (more traditional language)
- Look for other sources (books, literature, academic papers)

---

### Step 3: Apply Character Fixing

```bash
cd /mnt/c/tesseract/work

# Fix character encoding and normalization
python3 kurdish_character_fixer.py \
    --input corpus/ckb_phase7_raw.txt \
    --output corpus/ckb_phase7.training_text
```

#### Validate Fixed Corpus

```bash
# Should still show 6-10% ZWNJ after fixing
python3 tools/validate_source_quality.py corpus/ckb_phase7.training_text
```

---

### Step 4: Build Balanced Corpus

Blend Phase 7 corpus with existing high-quality news corpus:

```powershell
# Windows PowerShell (from c:\tesseract)
.\run_training.ps1 -Mode BuildCorpus -UseFixer -KeepRTLControls `
    -BalanceDigits -BalanceLatinDigits -BalancePuncs -CorpusMinCount 1
```

**What this does:**

- Combines Phase 7 corpus with existing news corpus
- Balances digits and punctuation
- Applies character fixing
- Outputs: `work\corpus\ckb.training_text`

**Alternative: Manual Blending**

If you want precise control over ZWNJ density:

```bash
cd /mnt/c/tesseract/work

python3 tools/blend_corpus.py \
    --sources corpus/ckb_scraped_filtered.training_text corpus/ckb_phase7.training_text \
    --output corpus/ckb_blended.training_text \
    --target-zwnj 8.0 \
    --weights 0.6 0.4
```

---

### Step 5: Train Model

```powershell
# Generate training data and train
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
```

---

### Step 6: Evaluate Results

#### Quick Test (mgk.tif)

```powershell
.\run_training.ps1 -Mode SmokeTestBest
```

**Check result:**

- Current: 71.69%
- **Target: >76%** (improvement of 4.3%+)

#### Comprehensive Evaluation (Multiple PSM modes)

```powershell
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

**Compare:**

- mgk.tif (biographical): Current 71.69% → Target >76%
- News images: Current 76.9% → Maintain ≥76%

---

## 🛠️ Tools Reference

### 1. validate_source_quality.py

**Purpose:** Quick ACCEPT/REJECT validation based on ZWNJ density

**Usage:**

```bash
python3 work/tools/validate_source_quality.py sample.txt
```

**Checks:**

- ✅ ZWNJ density (6-10% = ACCEPT)
- ✅ Kurdish script purity (>85%)
- ✅ Sentence quality
- ✅ Character distribution

**Output:** ✅ ACCEPT | ⚠️ REVIEW | ❌ REJECT

---

### 2. blend_corpus.py

**Purpose:** Blend multiple sources to achieve target ZWNJ density

**Basic Usage:**

```bash
python3 work/tools/blend_corpus.py \
    --sources file1.txt file2.txt \
    --output blended.txt \
    --target-zwnj 8.0
```

**Advanced Usage (weighted):**

```bash
python3 work/tools/blend_corpus.py \
    --sources news.txt biographical.txt \
    --output blended.txt \
    --target-zwnj 8.0 \
    --weights 0.6 0.4
```

**Equal Blending:**

```bash
python3 work/tools/blend_corpus.py \
    --sources file1.txt file2.txt \
    --output blended.txt \
    --equal
```

---

### 3. analyze_unicode_chars.py

**Purpose:** Detailed ZWNJ and Unicode analysis

**Usage:**

```bash
python3 work/analyze_unicode_chars.py corpus_file.txt
```

**Shows:**

- Detailed ZWNJ statistics
- Tatweel statistics
- Sentence coverage
- Character distribution
- Script purity percentage

---

### 4. Production Scraper

**Purpose:** Scrape Kurdish news websites with live dashboard

**Documentation:** `work/tools/scrapers/PRODUCTION_SCRAPER_USAGE.md`

**Quick Commands:**

```bash
cd /mnt/c/tesseract/work/tools/scrapers

# Interactive menu
./scrape.sh

# Production mode (all sites)
python3 run_production_display.py --config configs/websites --all --parallel --workers 3

# Specific websites
python3 run_production_display.py --config configs/websites --websites awene,rudaw --parallel

# Fresh scrape (clear deduplication)
python3 run_production_display.py --config configs/websites --all --fresh --parallel --workers 3
```

---

## 🔍 Alternative Sources (If Scraper Not Enough)

### Kurdish Digital Libraries & Books

**Archive.org:**

- Search: "کوردی" (Kurdish) + "biography"
- URL: https://archive.org/search.php?query=kurdish
- Extract 100-sentence sample → validate

**Google Books:**

- Search: Kurdish biographies, Kurdish literature
- Look for preview/full view books
- Extract sample → validate

**Kurdish Publishing Houses:**

- Aras Publishing
- Ranj Publishing
- Check for digital copies or PDFs

---

### Academic Sources

**Kurdistan Universities:**

- Salahaddin University (Erbil)
- University of Sulaimani
- University of Duhok
- Check: Digital repositories, thesis archives

**ResearchGate:**

- Search: Papers written in Kurdish
- Focus: History, literature, cultural studies

**Kurdish Studies Journals:**

- Look for open-access journals
- Download PDFs of articles in Kurdish

---

## 📊 Success Criteria

### ✅ Minimum Success

- mgk.tif: **74%** (+2.3% improvement)
- News: ≥76% (maintain)

### 🎯 Target Success

- mgk.tif: **76%** (+4.3% improvement)
- News: ≥76% (maintain)

### 🚀 Stretch Goal

- mgk.tif: **78%** (+6.3% improvement)
- News: ≥77% (improve)

---

## ⚠️ Troubleshooting

### Problem: Scraped content has low ZWNJ (<6%)

**Solutions:**

1. Try `poetry` category instead of `culture`
2. Try older news sites (more traditional Kurdish)
3. Look for Kurdish books/literature manually
4. Check `logs/scraper_*.log` for extraction issues
5. Consider different websites from your 14 available

---

### Problem: Not enough sentences (<500)

**Solutions:**

1. Scrape more websites (use all 6 with culture categories)
2. Enable pagination in YAML config files
3. Run scraper multiple times over several days
4. Combine with manually sourced content (books, academic papers)

---

### Problem: Training doesn't improve accuracy

**Check:**

1. Corpus ZWNJ density: Must be 6-10%
2. Script purity: Must be >85% Kurdish
3. Sentence quality: No encoding issues
4. Blend ratio: Not too much low-quality content

**If still no improvement:**

- Current model (71.69% / 76.9%) is already solid for v1.0
- Consider deploying as production
- Phase 7 can be revisited in future (v2.0)

---

### Problem: Mixed content quality (news + biographical)

**Solution - Use blend_corpus.py:**

```bash
python3 work/tools/blend_corpus.py \
    --sources corpus/ckb_scraped_filtered.training_text corpus/ckb_phase7.training_text \
    --output corpus/ckb_blended.training_text \
    --target-zwnj 8.0 \
    --weights 0.6 0.4
```

This gives you precise control over final ZWNJ density.

---

## 📅 Timeline Estimate

**Week 1: Source Discovery**

- Use scraper for culture/poetry categories
- Validate scraped content
- Find additional sources if needed

**Week 2: Content Acquisition**

- Scrape full content from validated sources
- Acquire text from books/academic sources if found
- Clean and prepare corpus files

**Week 3: Corpus Building**

- Combine all sources
- Apply character fixing
- Build balanced corpus
- Final validation

**Week 4: Training & Evaluation**

- Generate training data
- Train model (12-16 hours)
- Evaluate on mgk.tif and news images
- Document results

**Total: 4 weeks** (can be faster if scraper provides sufficient content)

---

## 📝 Production Checklist

### Before Scraping

- [ ] Identify websites with culture/poetry categories (you have 6)
- [ ] Test scrape small sample (100-200 sentences)
- [ ] Validate sample ZWNJ density (must be 6-10%)

### After Scraping

- [ ] Combine all scraped content
- [ ] Validate combined corpus ZWNJ density
- [ ] If ACCEPT (6-10%), proceed to fixing
- [ ] If REJECT (<6%), try different sources

### Corpus Preparation

- [ ] Apply character fixing (`kurdish_character_fixer.py`)
- [ ] Validate fixed corpus
- [ ] Build balanced corpus with existing news content
- [ ] Final validation before training

### Training

- [ ] Generate training data (`GenerateTrain`)
- [ ] Monitor training progress (12-16 hours)
- [ ] Check for errors in logs

### Evaluation

- [ ] Quick test on mgk.tif (`SmokeTestBest`)
- [ ] Full evaluation with PSM sweep
- [ ] Compare with Phase 6 baseline (71.69% / 76.9%)
- [ ] Document improvements

### Decision

- [ ] If >76% on mgk.tif: ✅ Success! Deploy Phase 7 model
- [ ] If 74-76%: ✅ Good improvement, consider deploying
- [ ] If <74%: ⚠️ Analyze what happened, may need more sources
- [ ] Update documentation with final results

---

## 🎯 Key Insights from Phase 6

### What We Learned

1. **ZWNJ is THE critical metric**

   - More important than corpus size
   - More important than domain matching
   - 9.3% ZWNJ → 76.9% accuracy ✅
   - 0.1% ZWNJ → FAILED ❌

2. **Quality over quantity**

   - 1,000 sentences at 8% ZWNJ > 10,000 sentences at 0.1% ZWNJ
   - Always validate BEFORE spending time on a source

3. **Domain matters (but ZWNJ matters more)**

   - News corpus works great on news images
   - Need biographical corpus for biographical images
   - **But both need high ZWNJ density!**

4. **Current model is production-quality**
   - 76.9% on modern text is excellent
   - 71.69% on biographical is acceptable for v1.0
   - Only pursue Phase 7 if you find proper sources (6-10% ZWNJ)

---

## 📚 Documentation Structure

### Phase 7 Documentation (All in one place)

**This file:** Complete guide for Phase 7 (read this first)

**Scraper documentation:** `work/tools/scrapers/PRODUCTION_SCRAPER_USAGE.md`

- Complete usage guide for production scraper
- Phase 7 section with biographical scraping instructions
- All command-line options and examples

**Historical documentation:** `archive/` (reference only)

- PHASE6_COMPLETE.md - Phase 6 final results
- PHASE7_IMPROVEMENT_PLAN.md - Original planning document
- PHASE7_QUICKSTART.md - Alternative quick start guide
- phase7_source_tracking.md - Source tracking template
- PHASE7_WSL_COMMANDS.md - WSL command reference

### Current State Files (Keep)

- `README.md` - Project overview
- `run_training.ps1` - Main training automation script
- `UNICODE_CHARACTER_ANALYSIS.md` - Unicode insights
- `ZWNJ_TATWEEL_SUMMARY.md` - ZWNJ analysis summary

---

## 🎉 Next Steps

### Today

1. ✅ Read this guide
2. ✅ Check scraper documentation
3. 🔍 Run test scrape on one website (awene or rudaw)
4. 🔍 Validate scraped content

### This Week

1. Scrape culture/poetry from all 6 websites
2. Combine and validate content
3. If ACCEPT (6-10% ZWNJ): Proceed to training
4. If REJECT: Look for additional sources

### Decision Point

- **If scraper provides 500+ sentences with 6-10% ZWNJ:** ✅ Proceed to training
- **If not enough or low ZWNJ:** Look for books, academic papers, or literature
- **If still can't find good sources:** Current model (76.9% news) is already excellent for v1.0 deployment

---

## 📞 Quick Command Reference

```powershell
# === Windows PowerShell Commands ===

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

```bash
# === WSL Ubuntu Commands ===

# Navigate to project
cd /mnt/c/tesseract

# Scrape biographical content (interactive)
cd work/tools/scrapers
./scrape.sh

# Scrape specific sites/categories
python3 run_production_display.py \
    --config configs/websites \
    --websites awene,balinde,rudaw \
    --categories culture,poetry \
    --parallel --workers 2

# Validate content
python3 tools/validate_source_quality.py corpus/sample.txt

# Analyze ZWNJ
python3 work/analyze_unicode_chars.py corpus/file.txt

# Blend sources
python3 work/tools/blend_corpus.py \
    --sources file1.txt file2.txt \
    --output blended.txt \
    --target-zwnj 8.0

# Fix characters
python3 work/kurdish_character_fixer.py \
    --input corpus/raw.txt \
    --output corpus/fixed.txt
```

---

**Status:** ✅ Ready to Begin Phase 7  
**Last Updated:** November 1, 2025  
**Maintained by:** Tesseract Kurdish OCR Project

Good luck! 🚀

**Remember:** ZWNJ density 6-10% is NON-NEGOTIABLE. Always validate BEFORE committing time to a source!
