# Tesseract OCR Training - Central Kurdish (ckb)

**Status:** Production Ready ✅  
**Version:** 5.0.0  
**Last Updated:** October 26, 2025

---

## 🎯 Project Overview

This project trains a custom Tesseract OCR model for **Central Kurdish (Sorani)** script using modern machine learning techniques and real-world Kurdish news articles.

### Key Features

- ✅ **14 Kurdish news websites** successfully scraped (1,052 sentences per test run)
- ✅ **Generic Scraper V5.0** - unified configuration-driven architecture
- ✅ **FlareSolverr integration** for Cloudflare-protected sites
- ✅ **Auto-resume test suite** with state management
- ✅ **Advanced features**: deduplication, language detection, rate limiting
- ✅ **Network features**: HTTP caching, automatic retry, proxy rotation, URL filtering ✨NEW
- ✅ **100% configuration-based** - no code changes needed for new sites

---

## 📁 Project Structure

```
tesseract/
├── README.md                      # This file
├── run_training.ps1               # Training automation (PowerShell)
├── docs/                          # Documentation
│   ├── SCRAPER_QUICK_START.md    # Quick start guide
│   ├── ADVANCED_FEATURES.md       # Advanced configuration
│   ├── PRODUCTION_READINESS.md    # Production deployment
│   └── kurdish_characters.md      # Kurdish script reference
├── work/                          # Training workspace
│   ├── corpus/                    # Training text data
│   ├── fonts/                     # Kurdish fonts
│   ├── training_output/           # Generated training data
│   └── tools/                     # Scraping & utilities
│       ├── test_suite.py         # Production test suite
│       ├── test_debug.py         # Debugging tool
│       └── scrapers/             # Generic scraper framework
│           ├── generic_scraper.py        # V5.0 unified scraper
│           ├── configs/                  # 17 website configs
│           └── docs/                     # Scraper documentation
└── tessdata/                      # Trained models
    ├── best/                      # Best quality models
    └── fast/                      # Fast models
```

---

## 🚀 Quick Start

### 1. Test Web Scrapers

# Kurdish OCR Training Project

Last updated: November 1, 2025

The repository contains the training and evaluation pipeline for a Central Kurdish (Sorani) Tesseract model. The pipeline is orchestrated from Windows PowerShell via `run_training.ps1`, executes work inside Ubuntu WSL, and produces models in `tessdata/best` and `tessdata/fast`.

## Current Status

- `tessdata/best/ckb.traineddata` and `tessdata/fast/ckb.traineddata` originate from **Phase 4 (Farsi base)** and remain the most reliable checkpoints.
- `mgk.tif` real-document benchmark (2,632 chars, biography layout) continues to plateau at **71.69 % accuracy / 0.2831 CER** when evaluated with `--psm 6` despite multiple corpus strategies.
- A high-ZWNJ corpus experiment (Batch 5, 1,313 sentences @ 11.68 % ZWNJ, perfectly matching the target document) reproduced the plateau, disproving ZWNJ density as the primary driver of errors.
- Modern Kurdish news images (≈9 % ZWNJ, short paragraphs) consistently achieve **≈76.9 % accuracy**, confirming the model is production-ready for contemporary layouts.
- Recommendation: deploy the current model for modern text, document the `mgk.tif` limitation, and treat any further improvement as a new research effort focusing on long-paragraph corpora or alternate architectures.

## Environment & Prerequisites

- Windows 10/11 with WSL2 and Ubuntu 20.04+ installed.
- Python 3.8+ and Tesseract OCR 4.1+ available inside WSL (most scripts use `/usr/bin/python3`).
- PowerShell 5.1+ on Windows (repository tasks invoke PowerShell).
- Optional: Docker + FlareSolverr for Cloudflare-protected scraping targets.

## Key Files & Directories

- `run_training.ps1` – PowerShell entry point with modes: `ScrapeCorpus`, `BuildCorpus`, `GenerateTrain`, `Train`, `Eval`, `SmokeTest(S)`, `Verify`, `Clean`, `All`.
- `cleanup_project.ps1` – archives or prunes legacy artifacts (`archive/` contains historical material).
- `work/` – WSL workspace:
  - `corpus/` (active corpora such as `ckb_high_zwnj.training_text` and filters including `filter_high_zwnj.py`).
  - `tools/scrapers/` (production scraper, configs, and utilities documented in `docs/PRODUCTION_READINESS.md`).
  - `tools/eval_real_cer.py` and supporting scripts used by evaluation tasks.
- `docs/` – current references:
  - `PRODUCTION_READINESS.md` (scraper deployment & monitoring).
  - `SCRAPER_QUICK_START.md` (adding or tuning websites).
  - `kurdish_characters.md` (glyph coverage reference).
- `archive/` – preserved Phase 1-5 and experimental notes. Everything else in root reflects the current workflow.

## Typical Workflow

1. **Scrape / Refresh Corpus**

   - Interactive: `.
un_training.ps1` then choose menu option **9**.
   - Non-interactive: `.
un_training.ps1 -Mode ScrapeCorpus -ScraperAll -ScraperWorkers 3 [-ScraperFresh]`.
   - See `docs/PRODUCTION_READINESS.md` for monitoring, alerts, and troubleshooting.

2. **Build Balanced Corpus**

   - `.
un_training.ps1 -Mode BuildCorpus -UseFixer -BalanceDigits -BalanceLatinDigits -BalancePuncs -CorpusMinCount 1`
   - Produces `work/corpus/ckb.training_text` and validation reports in `work/logs/`.

3. **Generate Training Data & Train**

   - Recommended one-step task: select VS Code task **“CKB: Generate + Train”** or run `.
un_training.ps1 -Mode GenerateTrain [-LatinDigits]`.
   - Generation and training happen inside WSL via `work/execute_ckb_training.sh`.

4. **Evaluate**

   - Quick regression: `.
un_training.ps1 -Mode SmokeTest` (auto best→fast) or `-Mode SmokeTestBest` / `-Mode SmokeTestFast` with optional `-ImagePath`.
   - Full benchmark: `.
un_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"` (invokes `tools/eval_real_cer.py` for real ground truth).
   - VS Code task **“CKB: Regression Test”** runs Eval + optional real CER reporting.

5. **Verification & Maintenance**
   - Coverage: `.
un_training.ps1 -Mode Verify -VerifyRequireLatinDigits` or the task **“CKB: Verify (Require Latin Digits)”**.
   - Deep clean between large experiments: **“CKB: Clean (Deep)”** task (removes temporary output and obsolete corpora).
   - Monitor long-running jobs using `monitor_training.ps1` or `check_training_progress.ps1`.

## Model Performance History

| Attempt (PSM 6)    | Corpus Summary                                     | ZWNJ % | Accuracy    | CER    | Notes                                   |
| ------------------ | -------------------------------------------------- | ------ | ----------- | ------ | --------------------------------------- |
| Phase 4 baseline   | 3,321 curated sentences (mixed news + biographies) | 8.15   | **71.69 %** | 0.2831 | Current production model.               |
| Batch 4 (Oct 2025) | 5,686 sentences incl. Wikipedia biographies        | 5.78   | 71.69 %     | 0.2831 | Added data diluted ZWNJ; no gain.       |
| Batch 5 (Nov 2025) | 1,313 high-ZWNJ sentences (11.68 %)                | 11.68  | 71.69 %     | 0.2831 | Matched target ZWNJ; plateau confirmed. |

Additional benchmark: modern news document set (≈9 % ZWNJ) returns **76.9 % accuracy** with the Phase 4 checkpoint; this is the recommended production scenario.

## Lessons Learned & Open Questions

- **ZWNJ distribution is not the limiting factor.** Batch 5 matched the target distribution yet produced identical results.
- **Longest-line domain mismatch persists.** `mgk.tif` contains 700–1,200 character lines; future work should collect comparable paragraph-length Kurdish text or synthesize similar layouts.
- **Fonts or aging artifacts may contribute.** Investigating historical Kurdish typefaces or document restoration could help if further accuracy gains are required.
- **Next possible directions:**
  1. Accept current accuracy for old dense texts and focus on deployment/documentation.
  2. Collect long-form Kurdish biographies / legal texts (paragraph-length) and retrain with ≥8 k high-quality samples.
  3. Explore architecture changes (larger context windows or alternative OCR engines) if long-form data is unavailable.

## Maintenance Checklist

- Keep `archive/` intact; it contains Phase 1-5 and experimental references moved out of the root directory.
- Use `cleanup_project.ps1` after large experiments to keep the working tree lightweight.
- Monitor `work/logs/` and `logs/` for scraper or training anomalies.
- Document any new evaluations in a single location (this README) to avoid the drift that previously occurred across many Markdown files.

## Additional References

- `docs/PRODUCTION_READINESS.md` – scraper operations, monitoring, security, and deployment guidance.
- `docs/SCRAPER_QUICK_START.md` – configuration-only workflow for adding or tuning websites.
- `docs/kurdish_characters.md` – complete character coverage checklist.
- `work/verify_ckb_traineddata.py` – standalone verifier for traineddata coverage.

Questions or follow-up analyses should be added to this README or the `docs/` directory to keep the documentation unified. 2. Test it:
