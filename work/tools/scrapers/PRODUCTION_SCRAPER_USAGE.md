# Production Scraper Usage Guide

## Overview

The production scraper (`run_production_display.py`) provides a professional live dashboard for scraping Kurdish news websites with real-time statistics and monitoring.

## Features

✅ **Live Dashboard** - Fixed header/footer with scrolling logs  
✅ **Real-time Metrics** - Articles, sentences, rates, ETA, success rate  
✅ **Parallel Processing** - Multiple workers scraping simultaneously  
✅ **Smart Deduplication** - Skip already scraped articles  
✅ **Auto-refresh** - Display updates every 2 seconds  
✅ **Color-coded Status** - Easy visual monitoring

## Basic Usage

### Scrape All Websites (Production Mode)

```bash
cd /mnt/c/tesseract/work/tools/scrapers
python3 run_production_display.py --config configs/websites --all --parallel --workers 3
```

### Scrape Specific Websites

```bash
python3 run_production_display.py --config configs/websites --websites avanews,awene,balinde --parallel --workers 3
```

### Single Website (Testing)

```bash
python3 run_production_display.py --config configs/websites --websites avanews --workers 1
```

### Fresh Scrape (Clear Deduplication)

```bash
python3 run_production_display.py --config configs/websites --all --parallel --workers 3 --fresh
```

## Command-line Arguments

| Argument     | Description                                  | Required |
| ------------ | -------------------------------------------- | -------- |
| `--config`   | Path to website configs directory            | ✅ Yes   |
| `--all`      | Scrape all enabled websites                  | No       |
| `--parallel` | Enable parallel scraping                     | No       |
| `--workers`  | Number of parallel workers (default: 3)      | No       |
| `--websites` | Comma-separated list of specific websites    | No       |
| `--fresh`    | Clear deduplication database before scraping | No       |

## Dashboard Layout

```
==================================================================================
🚀 PRODUCTION SCRAPER | Time: 01:23 | Workers: 3/13 | Rate: 45.2 sent/min
▶ Active: W0:avanews, W1:awene, W2:balinde
==================================================================================
TIMESTAMP    STATUS     WEBSITE              CATEGORY        SCRAPE LOGS
----------------------------------------------------------------------------------
12:34:56     START      AvaNews              news            Starting category scrape
12:34:57     DATA       AvaNews              news            Found 19 new articles
12:34:58     INFO       Awene                politics        Adding 3 paragraphs as sentences
[... scrolling logs ...]
==================================================================================
■ Progress: [██████████░░░░░░░░░░░░░░░░░░░░] 33% | 4/13 sites | ETA: 8m 23s
■ Collected: 1,234 articles, 5,678 sentences | Success: 75%
■ Performance: Avg: 1,419 sent/site, 186s/site | Failed: 1
```

## Status Indicators

- 🟢 **GREEN (DONE)** - Successful completion
- 🔴 **RED (ERROR)** - Failed operation
- 🟡 **YELLOW (WARN)** - Warning message
- 🔵 **CYAN (START)** - Starting new task
- 🟣 **BLUE (DATA)** - Data processing
- ⚪ **WHITE/MAGENTA (INFO)** - General information

## Live Metrics Explained

### Header Metrics

- **Time** - Elapsed time since start (HH:MM)
- **Workers** - Active workers / Total websites (e.g., 3/13)
- **Rate** - Current sentences per minute

### Footer Metrics

- **Progress** - Completion percentage and visual bar
- **Collected** - Total articles and sentences scraped
- **Success** - Percentage of successfully completed websites
- **Performance** - Average sentences per site and time per site
- **Failed** - Number of failed websites

## Tips for Production Use

1. **Use Deduplication** - Don't use `--fresh` in production unless you want to re-scrape everything
2. **Parallel Workers** - Use 3-5 workers for optimal performance
3. **Monitor ETA** - Provides accurate time estimates based on current progress
4. **Check Success Rate** - Should be >90% for healthy operation
5. **Ctrl+C Once** - Single interrupt gracefully stops all workers

## Output Files

- **Corpus** - `corpus/{website}/{category}.txt`
- **Logs** - `logs/scraper_YYYYMMDD_HHMMSS.log`
- **Deduplication DB** - `article_dedup.db` (SQLite)
- **Cache** - Redis (localhost:6379, 24h TTL)

## Troubleshooting

### Low Success Rate

- Check internet connection
- Verify website configurations
- Review logs for specific errors

### Sentence Rate Too Low

- Increase parallel workers
- Check if websites are slow to respond
- Verify extraction patterns are working

### Display Issues

- Ensure terminal supports ANSI escape codes
- Use standard terminal (not minimal/embedded)
- Check terminal size (minimum 80x24 recommended)

## Production Checklist

Before running production scraping:

- [ ] Deduplication database exists (or use --fresh for first run)
- [ ] Redis server is running (localhost:6379)
- [ ] Sufficient disk space for corpus files
- [ ] All website configs are enabled and tested
- [ ] Network connection is stable

## Example Production Command

```bash
# Full production run with all optimizations
cd /mnt/c/tesseract/work/tools/scrapers
python3 run_production_display.py \
    --config configs/websites \
    --all \
    --parallel \
    --workers 3 \
    > /dev/null 2>&1 &

# Monitor logs in real-time
tail -f logs/scraper_*.log
```

---

## Phase 7: Biographical Content for OCR Training

### Overview

**Goal:** Find biographical Kurdish text with **6-10% ZWNJ density** to improve OCR accuracy on biographical documents from 71.69% → 76%+.

### Why ZWNJ Matters

ZWNJ (Zero-Width Non-Joiner) density is the **critical quality metric** for Kurdish OCR training:
- News corpus (9.3% ZWNJ) → **76.9% accuracy** ✅
- Wikipedia (0.1% ZWNJ) → **FAILED** ❌

**Rule:** Only use sources with 6-10% ZWNJ density. Always validate before scraping.

### Websites with Biographical Content

Based on scraper configurations, these websites have culture/biography categories:

| Website | Categories | Best for Phase 7 |
|---------|-----------|------------------|
| **awene** | culture, poetry, society | ✅ Biography profiles |
| **balinde** | culture, poetry | ✅ Cultural figures |
| **kurdistan24** | culture, arts | ✅ Artist profiles |
| **rudaw** | culture, lifestyle | ✅ Historical figures |
| **nrt** | culture, society | ✅ Obituaries, bios |
| **kurdsat** | culture | ⚠️ Limited content |

### Scraping Biographical Content

#### Method 1: Use Interactive Menu (Recommended)

```bash
cd /mnt/c/tesseract/work/tools/scrapers
./scrape.sh
# Select option 4 (Custom scraping)
# Enter: awene,balinde,rudaw
# Select categories: culture,poetry
```

#### Method 2: Direct Command

```bash
# Scrape culture/poetry from multiple sites
python3 run_production_display.py \
    --config configs/websites \
    --websites awene,balinde,rudaw,nrt \
    --categories culture,poetry \
    --parallel --workers 2
```

#### Method 3: Single Site Test

```bash
# Test one site first
python3 run_production_display.py \
    --config configs/websites \
    --websites awene \
    --categories culture \
    --workers 1
```

### Validation Workflow

**After scraping, ALWAYS validate before training:**

#### Step 1: Combine scraped content

```bash
cd /mnt/c/tesseract/work
# Combine all culture/biography files
cat corpus/awene/culture.txt corpus/balinde/culture.txt corpus/rudaw/culture.txt > corpus/ckb_phase7_raw.txt
```

#### Step 2: Validate ZWNJ density

```bash
python3 tools/validate_source_quality.py corpus/ckb_phase7_raw.txt
```

**Expected output:**
```
✅ ACCEPT - High Quality Source
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZWNJ Density: 8.5% ✅ (Target: 6-10%)
Kurdish Script: 99.5% ✅
Sentences: 892
Status: Ready for training 🚀
```

**If REJECT (<6% ZWNJ):** Don't use for training, try different categories/websites.

#### Step 3: Apply character fixing

```bash
python3 kurdish_character_fixer.py --input corpus/ckb_phase7_raw.txt --output corpus/ckb_phase7.training_text
```

#### Step 4: Validate fixed corpus

```bash
python3 tools/validate_source_quality.py corpus/ckb_phase7.training_text
# Should still show 6-10% ZWNJ after fixing
```

### Integration with Training Pipeline

Once you have validated Phase 7 corpus:

```powershell
# Windows (from c:\tesseract)
.\run_training.ps1 -Mode BuildCorpus -UseFixer -KeepRTLControls `
    -BalanceDigits -BalanceLatinDigits -BalancePuncs -CorpusMinCount 1

.\run_training.ps1 -Mode GenerateTrain -LatinDigits

.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

### Troubleshooting Phase 7

#### Problem: Scraped content has low ZWNJ (<6%)

**Solutions:**
1. Try `poetry` category instead of `culture`
2. Try older news sites (more traditional language)
3. Manually find Kurdish books/literature
4. Check `logs/scraper_*.log` for extraction issues

#### Problem: Not enough sentences (<500)

**Solutions:**
1. Scrape more websites (add more to `--websites`)
2. Enable pagination in config YAML files
3. Run scraper multiple times over several days
4. Combine with manually sourced content

#### Problem: Mixed content (news + biography)

**Solutions:**
1. Use `tools/blend_corpus.py` to mix sources:
   ```bash
   python3 tools/blend_corpus.py \
       --sources corpus/ckb_scraped_filtered.training_text corpus/ckb_phase7.training_text \
       --output corpus/ckb_blended.training_text \
       --target-zwnj 8.0
   ```

### Phase 7 Tools

#### validate_source_quality.py

Quick ACCEPT/REJECT validation based on ZWNJ density:

```bash
python3 tools/validate_source_quality.py sample.txt
```

**Output:** ✅ ACCEPT | ⚠️ REVIEW | ❌ REJECT

#### blend_corpus.py

Blend multiple sources to achieve target ZWNJ density:

```bash
python3 tools/blend_corpus.py \
    --sources file1.txt file2.txt \
    --output blended.txt \
    --target-zwnj 8.0 \
    --weights 0.6 0.4
```

### Expected Results

**Current (Phase 6):**
- Biographical text (mgk.tif): **71.69%**
- News images: **76.9%**

**Phase 7 Target:**
- Biographical text (mgk.tif): **76%+** (4.3% improvement)
- News images: **≥76%** (maintain)

### Production Checklist for Phase 7

Before scraping biographical content:

- [ ] Identify websites with culture/poetry categories
- [ ] Test scrape small sample (100-200 sentences)
- [ ] Validate sample ZWNJ density (must be 6-10%)
- [ ] If accepted, scrape full content
- [ ] Combine and validate final corpus
- [ ] Apply character fixing
- [ ] Build balanced corpus with existing news content
- [ ] Train and evaluate

**Timeline:** 2-4 weeks (depends on source availability)

---

**Status**: ✅ Production Ready  
**Last Updated**: November 1, 2025  
**Maintained by**: Tesseract Kurdish OCR Project
