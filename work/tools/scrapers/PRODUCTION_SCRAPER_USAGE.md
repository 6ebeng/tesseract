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

**Status**: ✅ Production Ready  
**Last Updated**: October 30, 2025  
**Maintained by**: Tesseract Kurdish OCR Project
