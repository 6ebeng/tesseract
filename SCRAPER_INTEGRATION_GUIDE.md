# Production Scraper Integration - Quick Reference

## ✅ Integration Complete!

The production Kurdish news scraper is now integrated into `run_training.ps1`.

---

## 🚀 Usage Options

### Option 1: Interactive Menu

```powershell
.\run_training.ps1
# Select option 9: Scrape Kurdish news corpus
```

### Option 2: Command-Line (All Websites)

```powershell
.\run_training.ps1 -Mode ScrapeCorpus -ScraperAll -ScraperWorkers 3
```

### Option 3: Command-Line (Specific Websites)

```powershell
.\run_training.ps1 -Mode ScrapeCorpus -ScraperWebsites "avanews,awene,rudaw" -ScraperWorkers 2
```

### Option 4: Fresh Scrape (Clear Deduplication)

```powershell
.\run_training.ps1 -Mode ScrapeCorpus -ScraperAll -ScraperWorkers 3 -ScraperFresh
```

---

## 📋 Parameters

| Parameter            | Description                  | Default                         |
| -------------------- | ---------------------------- | ------------------------------- |
| `-Mode ScrapeCorpus` | Run scraper mode             | Required                        |
| `-ScraperAll`        | Scrape all 13 websites       | Either this or -ScraperWebsites |
| `-ScraperWebsites`   | Comma-separated website list | Either this or -ScraperAll      |
| `-ScraperWorkers`    | Number of parallel workers   | 3                               |
| `-ScraperFresh`      | Clear deduplication database | Off (dedup enabled)             |

---

## 🎯 Complete Training Pipeline

### Step-by-Step Workflow

1. **Scrape Kurdish news corpus**

   ```powershell
   .\run_training.ps1 -Mode ScrapeCorpus -ScraperAll -ScraperWorkers 3
   ```

2. **Build balanced corpus**

   ```powershell
   .\run_training.ps1 -Mode BuildCorpus -UseFixer
   ```

3. **Generate training data and train**

   ```powershell
   .\run_training.ps1 -Mode GenerateTrain
   ```

4. **Evaluate results**
   ```powershell
   .\run_training.ps1 -Mode Eval
   ```

### Or Run All at Once

```powershell
# First scrape corpus
.\run_training.ps1 -Mode ScrapeCorpus -ScraperAll -ScraperWorkers 3

# Then run complete pipeline
.\run_training.ps1 -Mode All
```

---

## 📊 Output Locations

After scraping:

- **Corpus files**: `work/tools/scrapers/corpus/{website}/{category}.txt`
- **Logs**: `work/tools/scrapers/logs/scraper_*.log`
- **Dedup DB**: `work/tools/scrapers/article_dedup.db`

After building corpus:

- **Training corpus**: `work/corpus/ckb.training_text.final`

After generating training data:

- **Training files**: `work/data/ckb/`

After training:

- **Trained model**: `work/data/ckb.traineddata` or `tessdata/ckb.traineddata`

---

## 🎨 Interactive Menu Example

```
╔══════════════════════════════════════════════════════╗
║       KURDISH OCR - TRAINING/BUILD LAUNCHER         ║
╚══════════════════════════════════════════════════════╝

Select an option:
1. Cleanup workspace (remove tests/.md)
2. Generate training data (then optionally Train)
3. Train now (skip generation)
4. Smoke test trained ckb model (auto: best→fast)
5. Smoke test (best only)
6. Smoke test (fast only)
7. Verify ckb.traineddata covers Kurdish chars
8. Build balanced corpus (uses fixer)
9. Scrape Kurdish news corpus (production scraper)  ← NEW!
10. Evaluate real-world CER (real_gt/eval)
11. Bootstrap WSL training toolchain
12. All: Corpus → Generate → Train → Eval

Enter your choice (1-12): 9

Production scraper options:
1. Scrape all 13 websites (recommended)
2. Scrape specific websites
Enter choice (1-2): 1

Number of parallel workers (default: 3): 3
Clear deduplication database (fresh scrape)? (y/N): n

╔══════════════════════════════════════════════════════╗
║      KURDISH CORPUS SCRAPING - PRODUCTION MODE      ║
╚══════════════════════════════════════════════════════╝

Scraping all 13 enabled Kurdish news websites
Workers: 3 parallel
Deduplication: ON

Starting production scraper...

[Live dashboard appears here...]
```

---

## 💡 Tips

### First Time Scraping

```powershell
# Use fresh mode to start clean
.\run_training.ps1 -Mode ScrapeCorpus -ScraperAll -ScraperFresh
```

### Daily Updates

```powershell
# Use deduplication to skip already-scraped articles
.\run_training.ps1 -Mode ScrapeCorpus -ScraperAll
```

### Targeted Scraping

```powershell
# Scrape only specific high-quality sources
.\run_training.ps1 -Mode ScrapeCorpus -ScraperWebsites "avanews,rudaw,nrt"
```

### Maximum Speed

```powershell
# Use more workers (if system can handle it)
.\run_training.ps1 -Mode ScrapeCorpus -ScraperAll -ScraperWorkers 5
```

---

## 🆘 Troubleshooting

### Check Scraper Logs

```powershell
# View recent logs
wsl -d Ubuntu -- bash -c "tail -100 /mnt/c/tesseract/work/tools/scrapers/logs/scraper_*.log"
```

### Verify Output

```powershell
# List scraped corpus files
wsl -d Ubuntu -- bash -c "find /mnt/c/tesseract/work/tools/scrapers/corpus -name '*.txt' -exec wc -l {} +"
```

### Clear Deduplication

```powershell
# If you need to re-scrape everything
.\run_training.ps1 -Mode ScrapeCorpus -ScraperAll -ScraperFresh
```

---

## 📚 Related Documentation

- **Scraper Usage**: `work/tools/scrapers/PRODUCTION_SCRAPER_USAGE.md`
- **Scraper README**: `work/tools/scrapers/README.md`
- **Training Guide**: Root directory documentation

---

**Status**: ✅ Fully Integrated  
**Date**: October 30, 2025
