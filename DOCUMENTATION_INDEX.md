# Documentation Index - Kurdish OCR Project

**Project Status:** ✅ Phase 6 Complete (76.9% news, 71.69% biographical) | 🔍 Phase 7 Ready

---

## 📖 Main Documentation (Read These)

### Core Documentation

| File | Purpose | When to Read |
|------|---------|--------------|
| **[README.md](README.md)** | Project overview and setup | First time setup |
| **[PHASE6_COMPLETE.md](PHASE6_COMPLETE.md)** | Phase 6 final results and analysis | Understanding current state |
| **[PHASE7_COMPLETE_GUIDE.md](PHASE7_COMPLETE_GUIDE.md)** | Complete Phase 7 workflow | **START HERE for Phase 7** ⭐ |

### Technical Analysis

| File | Purpose | When to Read |
|------|---------|--------------|
| **[UNICODE_CHARACTER_ANALYSIS.md](UNICODE_CHARACTER_ANALYSIS.md)** | Unicode character insights | Understanding ZWNJ/character issues |
| **[ZWNJ_TATWEEL_SUMMARY.md](ZWNJ_TATWEEL_SUMMARY.md)** | ZWNJ analysis summary | Understanding quality metrics |

### Scraper System

| File | Purpose | When to Read |
|------|---------|--------------|
| **[work/tools/scrapers/PRODUCTION_SCRAPER_USAGE.md](work/tools/scrapers/PRODUCTION_SCRAPER_USAGE.md)** | Complete scraper usage guide | Using the scraper system |
| **[work/tools/scrapers/README.md](work/tools/scrapers/README.md)** | Scraper framework documentation | Understanding scraper architecture |

---

## 🛠️ Scripts & Tools

### Main Automation Script

- **`run_training.ps1`** - Main training pipeline (PowerShell)
  - Modes: BuildCorpus, GenerateTrain, SmokeTest, Eval, Verify
  - Documentation: See comments in script

### Phase 7 Tools (work/tools/)

| Tool | Purpose | Usage |
|------|---------|-------|
| **validate_source_quality.py** | ACCEPT/REJECT validation | `python work/tools/validate_source_quality.py sample.txt` |
| **blend_corpus.py** | Blend sources to target ZWNJ | `python work/tools/blend_corpus.py --sources f1.txt f2.txt --output out.txt` |
| **analyze_unicode_chars.py** | Detailed ZWNJ analysis | `python work/analyze_unicode_chars.py corpus.txt` |

### Corpus Processing Tools (work/)

| Tool | Purpose |
|------|---------|
| **kurdish_character_fixer.py** | Fix character encoding/normalization |
| **verify_ckb_traineddata.py** | Verify trained model |
| **execute_ckb_training.sh** | WSL training script (called by run_training.ps1) |
| **generate_ckb_training_data.sh** | WSL data generation script |

### Scraper Tools (work/tools/scrapers/)

| Tool | Purpose |
|------|---------|
| **run_production_display.py** | Production scraper with live dashboard |
| **scrape.sh** | Interactive scraper launcher |
| **generic_scraper.py** | Core YAML-driven scraper |
| **filter_corpus.py** | Filter scraped corpus |

---

## 📁 Directory Structure

```
c:\tesseract\
│
├── README.md                          # Project overview
├── PHASE6_COMPLETE.md                 # Phase 6 results
├── PHASE7_COMPLETE_GUIDE.md           # Phase 7 complete guide ⭐
├── UNICODE_CHARACTER_ANALYSIS.md      # Unicode insights
├── ZWNJ_TATWEEL_SUMMARY.md           # ZWNJ analysis
├── run_training.ps1                   # Main automation script
│
├── work/                              # Working directory
│   ├── corpus/                        # Training corpora
│   ├── fonts/                         # Kurdish fonts
│   ├── output/                        # Training output
│   ├── training_output/               # Tesseract training files
│   ├── logs/                          # Training logs
│   ├── real_gt/                       # Ground truth test images
│   │
│   ├── analyze_unicode_chars.py       # ZWNJ analyzer
│   ├── kurdish_character_fixer.py     # Character fixer
│   ├── verify_ckb_traineddata.py      # Model verification
│   │
│   └── tools/                         # Tools directory
│       ├── validate_source_quality.py # Phase 7: Validation tool ⭐
│       ├── blend_corpus.py            # Phase 7: Blending tool ⭐
│       │
│       └── scrapers/                  # Production scraper system
│           ├── PRODUCTION_SCRAPER_USAGE.md  # Scraper usage guide ⭐
│           ├── README.md              # Scraper documentation
│           ├── scrape.sh              # Interactive launcher
│           ├── run_production_display.py    # Production scraper
│           ├── generic_scraper.py     # Core scraper
│           ├── configs/               # Website configs (14 sites)
│           └── corpus/                # Scraped content output
│
├── samples/                           # Test samples directory
│   └── README.md                      # Samples usage guide
│
├── tessdata/                          # Tesseract models
│   ├── best/                          # LSTM models
│   └── fast/                          # Fast models
│
├── docs/                              # Additional documentation
│   ├── kurdish_characters.md          # Kurdish character reference
│   ├── PRODUCTION_READINESS.md        # Production deployment
│   └── SCRAPER_QUICK_START.md         # Scraper quick start
│
└── archive/                           # Historical documents
    ├── phase1-5/                      # Early phase docs
    ├── experiments/                   # Experimental docs
    ├── old_corpus/                    # Old corpus files
    └── phase7_docs/                   # Consolidated Phase 7 docs
        ├── PHASE7_IMPROVEMENT_PLAN.md
        ├── PHASE7_QUICKSTART.md
        ├── phase7_source_tracking.md
        └── PHASE7_WSL_COMMANDS.md
```

---

## 🚀 Quick Start Guides

### For Phase 7 (Improving Accuracy)

**Read:** [PHASE7_COMPLETE_GUIDE.md](PHASE7_COMPLETE_GUIDE.md) ⭐

**Quick Steps:**
1. Use scraper to get biographical content: `cd work/tools/scrapers && ./scrape.sh`
2. Validate ZWNJ density: `python work/tools/validate_source_quality.py sample.txt`
3. If ACCEPT (6-10% ZWNJ), proceed to training
4. Build corpus: `.\run_training.ps1 -Mode BuildCorpus ...`
5. Train: `.\run_training.ps1 -Mode GenerateTrain -LatinDigits`
6. Evaluate: `.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"`

### For Scraping News

**Read:** [work/tools/scrapers/PRODUCTION_SCRAPER_USAGE.md](work/tools/scrapers/PRODUCTION_SCRAPER_USAGE.md)

**Quick Commands:**
```bash
cd /mnt/c/tesseract/work/tools/scrapers

# Interactive menu
./scrape.sh

# Production scraping (all sites)
python3 run_production_display.py --config configs/websites --all --parallel --workers 3
```

### For Training (After Corpus Ready)

**Quick Commands:**
```powershell
# Build corpus
.\run_training.ps1 -Mode BuildCorpus -UseFixer -KeepRTLControls `
    -BalanceDigits -BalanceLatinDigits -BalancePuncs -CorpusMinCount 1

# Generate training data and train
.\run_training.ps1 -Mode GenerateTrain -LatinDigits

# Quick test
.\run_training.ps1 -Mode SmokeTestBest

# Full evaluation
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

---

## 📊 Current Status

### Phase 6 (Completed)

**Accuracy:**
- News images: **76.9%** ✅
- Biographical text (mgk.tif): **71.69%**

**Corpus Quality:**
- News corpus: **9.33% ZWNJ** ✅ (excellent)
- Wikipedia: **0.11% ZWNJ** ❌ (rejected)

**Model:**
- Training: 5 batches completed
- Status: Production-ready for news text
- Next: Phase 7 to improve biographical accuracy

### Phase 7 (Ready to Start)

**Goal:** Improve mgk.tif from 71.69% → 76%+

**Approach:**
1. Find biographical sources with 6-10% ZWNJ
2. Use existing scraper (culture/poetry categories)
3. Or find Kurdish books, academic papers, literature
4. Validate with validation tool (MUST be 6-10% ZWNJ)
5. Train with blended corpus (news + biographical)

**Tools Ready:**
- ✅ Production scraper (14 websites)
- ✅ Validation tool (validate_source_quality.py)
- ✅ Blending tool (blend_corpus.py)
- ✅ Training pipeline (run_training.ps1)

---

## 🎯 Key Metrics

### Critical Quality Metric: ZWNJ Density

**ZWNJ (Zero-Width Non-Joiner) is THE most important metric for Kurdish OCR:**

| Corpus | ZWNJ Density | Result | Status |
|--------|--------------|--------|--------|
| News (scraped) | 9.33% | 76.9% accuracy | ✅ Excellent |
| Wikipedia | 0.11% | Training failed | ❌ Rejected |
| **Target for Phase 7** | **6-10%** | Expected 76%+ | 🎯 Required |

**Rule:** Always validate ZWNJ density BEFORE acquiring full text or training!

---

## 💡 Key Insights

### What We Learned from Phase 6

1. **ZWNJ Density is Critical**
   - 9.3% ZWNJ → 76.9% accuracy ✅
   - 0.1% ZWNJ → Failed ❌
   - More important than corpus size or domain

2. **Quality Over Quantity**
   - 1,000 sentences at 8% ZWNJ > 10,000 sentences at 0.1% ZWNJ
   - Always validate BEFORE spending time on a source

3. **Domain Matters (But ZWNJ Matters More)**
   - News corpus works great on news images
   - Need biographical corpus for biographical text
   - But both MUST have 6-10% ZWNJ density

4. **Current Model is Production-Ready**
   - 76.9% on modern text is excellent for v1.0
   - Phase 7 is optional improvement
   - Only pursue if you find proper sources (6-10% ZWNJ)

---

## 🗑️ Archived Documentation

The following documents have been archived to `archive/phase7_docs/`:

- **PHASE7_IMPROVEMENT_PLAN.md** - Original planning (superseded by PHASE7_COMPLETE_GUIDE.md)
- **PHASE7_QUICKSTART.md** - Quick start guide (consolidated into PHASE7_COMPLETE_GUIDE.md)
- **phase7_source_tracking.md** - Source tracking template (guidance now in complete guide)
- **PHASE7_WSL_COMMANDS.md** - WSL commands (consolidated into PHASE7_COMPLETE_GUIDE.md)

**Reason for archival:** All information consolidated into single comprehensive guide (PHASE7_COMPLETE_GUIDE.md)

---

## 📝 Documentation Principles

### What We Keep

1. **User-focused** - Answers "How do I use this?"
2. **Action-oriented** - Clear examples and commands
3. **Consolidated** - One authoritative source per topic
4. **Maintained** - Updated with code changes

### What We Archive

1. **Redundant content** - Same information in multiple places
2. **Superseded guides** - Replaced by better documentation
3. **Historical artifacts** - Old planning documents
4. **Development notes** - Temporary implementation details

---

## 🎉 Documentation Status

**Before Cleanup:**
- Multiple overlapping Phase 7 docs (4 files)
- Redundant scraper documentation (2 files removed)
- Fragmented information

**After Cleanup:**
- ✅ Single comprehensive Phase 7 guide
- ✅ Scraper usage integrated into main scraper docs
- ✅ Clear documentation structure
- ✅ Easy to navigate and maintain

**Total Reduction:**
- Removed 6 redundant files
- Consolidated into 1 comprehensive guide
- All information preserved

---

## 📞 Getting Help

### For Phase 7 Questions
- **Read first:** [PHASE7_COMPLETE_GUIDE.md](PHASE7_COMPLETE_GUIDE.md)
- **Troubleshooting:** See troubleshooting section in complete guide
- **Tools:** All Phase 7 tools documented in complete guide

### For Scraper Questions
- **Read first:** [work/tools/scrapers/PRODUCTION_SCRAPER_USAGE.md](work/tools/scrapers/PRODUCTION_SCRAPER_USAGE.md)
- **Quick start:** Use `./scrape.sh` interactive menu
- **Phase 7 scraping:** See "Phase 7: Biographical Content" section

### For Training Questions
- **Script help:** `Get-Help .\run_training.ps1 -Detailed`
- **WSL commands:** See PHASE7_COMPLETE_GUIDE.md
- **Logs:** Check `work/logs/training_*.log`

---

**Status:** ✅ Documentation Consolidated and Production-Ready  
**Last Updated:** November 1, 2025  
**Maintained by:** Tesseract Kurdish OCR Project
