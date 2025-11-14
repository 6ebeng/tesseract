# Kurdish OCR Project Structure

**Last Updated:** November 14, 2025  
**Status:** ✅ Organized and Production Ready

---

## 📁 Directory Structure

```
c:\tesseract\
├── README.md                          # Main project README
├── DOCUMENTATION_INDEX.md             # Central documentation hub ⭐ START HERE
├── run_training.ps1                   # Main driver script (all operations)
├── REORGANIZATION_PLAN.md             # Reorganization details
├── PROJECT_STRUCTURE.md               # This file
│
├── docs/                              # 📚 All Documentation
│   ├── normalization/                 # Normalization system docs
│   │   ├── CORPUS_NORMALIZATION.md                 # Main guide
│   │   ├── NORMALIZATION_COMPLETE_SUMMARY.md       # Complete overview
│   │   ├── NORMALIZATION_IMPROVEMENTS_v2.md        # v2.0 features
│   │   ├── NORMALIZATION_IMPROVEMENTS_v2.1.md      # v2.1 features
│   │   ├── NORMALIZATION_IMPROVEMENTS_v2.2.md      # v2.2 features (latest)
│   │   └── MIXED_KURDISH_ARABIC_HANDLING.md        # Multi-language support
│   │
│   ├── phases/                        # Project phases
│   │   ├── PHASE6_COMPLETE.md                      # Phase 6 results
│   │   ├── PHASE7_COMPLETE.md                      # Phase 7 summary
│   │   └── PHASE7_COMPLETE_GUIDE.md                # Phase 7 guide
│   │
│   ├── guides/                        # User guides
│   │   ├── RUN_TRAINING_OPTIONS.md                 # All run_training.ps1 options
│   │   ├── BATCH_PROCESSING_GUIDE.md               # Batch processing
│   │   └── BATCH_PROCESSING_WORKFLOW.md            # Detailed workflow
│   │
│   ├── analysis/                      # Technical analysis
│   │   ├── UNICODE_CHARACTER_ANALYSIS.md           # Unicode insights
│   │   └── ZWNJ_TATWEEL_SUMMARY.md                 # ZWNJ analysis
│   │
│   ├── kurdish_characters.md          # Kurdish character reference
│   ├── PRODUCTION_READINESS.md        # Production deployment
│   └── SCRAPER_QUICK_START.md         # Scraper quick start
│
├── work/                              # 🔧 Working Directory
│   ├── corpus/                        # Training corpora
│   │   ├── ckb.training_text.final           # Final built corpus
│   │   ├── scraped_all_sources.txt           # Combined scraped data
│   │   └── *.training_text                   # Source corpora
│   │
│   ├── tools/                         # Active tool scripts
│   │   ├── corpus_build.py                   # ⭐ Main corpus builder (ZWNJ-aware)
│   │   ├── corpus_audit.py                   # Quality checker
│   │   ├── validate_source_quality.py        # ZWNJ validator
│   │   ├── blend_corpus.py                   # Corpus blending
│   │   ├── eval_real_cer.py                  # CER evaluation
│   │   ├── merge_corpus.py                   # Corpus merging
│   │   ├── corpus_stats.py                   # Statistics
│   │   ├── analyze_errors.py                 # Error analysis
│   │   ├── analyze_ocr_errors.py             # OCR error analysis
│   │   ├── analyze_zwnj_patterns.py          # ZWNJ pattern analysis
│   │   ├── aggregate_error_analysis.py       # Aggregate analysis
│   │   ├── detailed_error_analysis.py        # Detailed analysis
│   │   ├── extract_quality_sentences.py      # Quality extraction
│   │   ├── eval_tuner.py                     # Evaluation tuner
│   │   ├── generate_shaping_augment.py       # Shaping augmentation
│   │   ├── build_kurdish_dictionary.py       # Dictionary builder
│   │   ├── corpus_quality_checker.py         # Quality checker
│   │   ├── kurdish_spell_checker.py          # Spell checker
│   │   ├── kurdish_zwnj_rules.py             # ZWNJ rules
│   │   ├── kurdish_zwnj_postprocessor.py     # ZWNJ postprocessing
│   │   ├── find_selectors.py                 # Selector finder
│   │   └── filter_corpus.py                  # Corpus filtering
│   │
│   ├── scrapers/                      # Production scraper system
│   │   ├── run_production_display.py          # ⭐ Production scraper
│   │   ├── generic_scraper.py                 # Scraper engine
│   │   ├── scrape.sh                          # Interactive launcher
│   │   ├── filter_corpus.py                   # Corpus filtering
│   │   ├── filter_wiki_bio.py                 # Wikipedia filtering
│   │   ├── configs/                           # Website configs (14 sites)
│   │   ├── corpus/                            # Scraped content output
│   │   ├── logs/                              # Scraper logs
│   │   ├── PRODUCTION_SCRAPER_USAGE.md        # Usage guide
│   │   └── README.md                          # Scraper docs
│   │
│   ├── fonts/                         # Kurdish fonts (downloaded)
│   ├── output/                        # Build outputs
│   │   ├── char_histogram.csv                 # Character distribution
│   │   ├── corpus_stats.txt                   # Corpus statistics
│   │   └── corpus_audit.json/.txt             # Audit results
│   │
│   ├── training_output/               # Training results (Fast profile)
│   ├── training_output_best/          # Training results (Best profile)
│   ├── training_output_fast/          # Training results (Fast profile)
│   ├── real_gt/                       # Ground truth test data
│   ├── charsets/                      # Character sets
│   ├── logs/                          # Training logs
│   │
│   ├── kurdish_character_fixer.py     # ⭐ Main normalization engine (v2.2)
│   ├── analyze_unicode_chars.py       # ⭐ ZWNJ/Unicode analyzer
│   ├── verify_ckb_traineddata.py      # Model verifier
│   ├── generate_ckb_training_data.sh  # ⭐ Data generation script
│   ├── execute_ckb_training.sh        # ⭐ Training execution script
│   ├── batch_lstmf_processor.sh       # Batch processing
│   ├── parallel_font_processor.sh     # Parallel font processing
│   ├── download_kurdish_fonts.sh      # Font downloader
│   ├── cleanup_unnecessary_files.sh   # Cleanup utility
│   ├── Makefile                       # Build automation
│   ├── fonts.conf                     # Font configuration
│   └── README.md                      # Work directory README
│
├── tessdata/                          # 🎯 Tesseract Models
│   ├── best/                          # LSTM models (high accuracy)
│   ├── fast/                          # Fast models
│   └── configs/                       # Tesseract configs
│
├── samples/                           # 📸 Test Samples
│   └── README.md                      # Sample usage guide
│
├── logs/                              # 📝 Application Logs
│
└── archive/                           # 📦 Historical Artifacts
    ├── scripts/                       # Old/obsolete scripts
    │   ├── improve_training_generation.ps1
    │   └── setup_z_mount.sh
    │
    ├── phase7_docs/                   # Consolidated Phase 7 docs
    ├── phase1-5/                      # Early phase docs
    ├── experiments/                   # Experimental docs
    ├── batches/                       # Batch training docs
    └── old_corpus/                    # Old corpus files
```

---

## 🚀 Quick Start

### For New Users

1. **Read:** [README.md](README.md) - Project overview
2. **Index:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - Find all documentation
3. **Training:** [docs/guides/RUN_TRAINING_OPTIONS.md](docs/guides/RUN_TRAINING_OPTIONS.md) - Learn the main driver

### For Training

```powershell
# Build high-quality corpus with ZWNJ filters
.\run_training.ps1 -Mode BuildCorpus -UseFixer -MinZWNJ 2.0 -TargetZWNJ 6.0

# Generate training data and train
.\run_training.ps1 -Mode GenerateTrain -LatinDigits

# Evaluate model
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

### For Scraping

```bash
cd work/tools/scrapers
./scrape.sh  # Interactive menu
```

---

## ⭐ Key Active Scripts

### Main Driver

- **run_training.ps1** - All operations (BuildCorpus, GenerateTrain, Eval, etc.)

### Corpus Management

- **work/tools/corpus_build.py** - ZWNJ-aware corpus builder
- **work/tools/corpus_audit.py** - Quality auditor
- **work/tools/validate_source_quality.py** - ZWNJ validator
- **work/tools/blend_corpus.py** - Corpus blender

### Normalization

- **work/kurdish_character_fixer.py** - v2.2 with Latin word preservation

### Analysis

- **work/analyze_unicode_chars.py** - ZWNJ density checker
- **work/tools/eval_real_cer.py** - CER evaluation

### Training

- **work/generate_ckb_training_data.sh** - Data generation
- **work/execute_ckb_training.sh** - Training execution

### Scraping

- **work/tools/scrapers/run_production_display.py** - Production scraper
- **work/tools/scrapers/generic_scraper.py** - Scraper engine

---

## 📊 Current Status

**Training:** Phase 6 Complete (76.9% accuracy on news)  
**Corpus Quality:** ZWNJ-aware with filtering and oversampling  
**Normalization:** v2.2 (Kurdish + Arabic + Latin/English support)  
**Scrapers:** 14 Kurdish news websites active  
**Production Ready:** ✅ Yes

---

## 🔧 Recent Improvements

### November 14, 2025

- ✅ **ZWNJ-Aware Corpus Builder** - Filters low-ZWNJ sentences, oversamples high-ZWNJ
- ✅ **Project Reorganization** - Clean structure, organized documentation
- ✅ **Removed 23 obsolete files** - Cleaner, more maintainable codebase
- ✅ **Updated main driver** - New `-MinZWNJ` and `-TargetZWNJ` parameters

### Previous

- ✅ **Normalization v2.2** - Latin/English word preservation, HEH+ZWNJ→AE
- ✅ **Normalization v2.1** - Enhanced whitespace, quote normalization, Latin digits
- ✅ **Normalization v2.0** - Arabic word preservation, hamza variants
- ✅ **Production Scraper** - 14 Kurdish news websites, parallel processing
- ✅ **Batch Processing** - Network drive support, 22 parallel workers

---

## 📚 Documentation

All documentation is in **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)**

### By Category

- **Normalization:** [docs/normalization/](docs/normalization/)
- **Phases:** [docs/phases/](docs/phases/)
- **Guides:** [docs/guides/](docs/guides/)
- **Analysis:** [docs/analysis/](docs/analysis/)

### Most Important

1. [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - Start here
2. [docs/phases/PHASE7_COMPLETE_GUIDE.md](docs/phases/PHASE7_COMPLETE_GUIDE.md) - Phase 7 workflow
3. [docs/normalization/NORMALIZATION_COMPLETE_SUMMARY.md](docs/normalization/NORMALIZATION_COMPLETE_SUMMARY.md) - Normalization system
4. [docs/guides/RUN_TRAINING_OPTIONS.md](docs/guides/RUN_TRAINING_OPTIONS.md) - All training options

---

## 🎯 Best Practices

### Corpus Building

1. Always use `-UseFixer` for normalization
2. Set `-MinZWNJ 2.0` to filter low-quality sentences
3. Set `-TargetZWNJ 6.0` for optimal OCR quality
4. Verify ZWNJ density: check `work/output/corpus_stats.txt`

### Training

1. Use `GenerateTrain` mode (combines generation + training)
2. Add `-LatinDigits` to preserve Western numerals
3. Test with `SmokeTestBest` before full evaluation
4. Evaluate with multiple PSMs: `-EvalPSMs "6,11,7,13"`

### Scraping

1. Use production scraper for quality and deduplication
2. Filter scraped corpus for ZWNJ density before using
3. Prefer culture/poetry/literary sources (higher ZWNJ)

---

## 🆘 Troubleshooting

**Low ZWNJ Density (<1%)**

- Increase `-MinZWNJ` threshold
- Use validate_source_quality.py to check sources
- Scrape from culture/literary websites

**Corpus Build Errors**

- Check `work/output/corpus_audit.txt` for issues
- Verify source files exist in `work/corpus/`
- Ensure WSL Ubuntu is running

**Training Failures**

- Check `work/logs/training_*.log`
- Verify fonts in `work/fonts/`
- Ensure sufficient disk space

---

**Maintained By:** Kurdish OCR Training Project  
**License:** See LICENSE file  
**Version:** 7.0 (Post-Reorganization)
