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

```bash
# Test all 14 websites (3 articles each) - from work/tools directory
cd work/tools
wsl -d Ubuntu -- bash -lc "cd '/mnt/c/tesseract/work/tools' && python3 test_suite.py --max-articles 3"

# Test specific website
python3 test_suite.py yariga --max-articles 10

# Debug website selectors
python3 test_debug.py kurdistan24 --category politics --test-selectors
```

### 2. Generate Training Data

```powershell
# Windows (PowerShell)
.\run_training.ps1 -Mode BuildCorpus

# WSL/Linux
cd work
bash execute_ckb_training.sh
```

### 3. Train Model

```powershell
# Full training pipeline
.\run_training.ps1 -Mode GenerateTrain

# Smoke test trained model
.\run_training.ps1 -Mode SmokeTest
```

### 4. Verify Kurdish Character Coverage

```powershell
# Verify traineddata includes all Kurdish characters
.\run_training.ps1 -Mode Verify

# Or directly in WSL
cd work
python3 verify_ckb_traineddata.py --traineddata /mnt/c/tesseract/tessdata/best/ckb.traineddata
```

---

## 📊 Current Status

### Phase 6: Complete ✅ | Phase 7: Planning 🚀

**Phase 6 Achievement:**
- ✅ **76.9% accuracy** on modern Kurdish news text
- ⚠️ **71.69% accuracy** on biographical text
- ✅ **ZWNJ density:** 9.331% in training corpus (excellent quality)
- ✅ **Model ready for production deployment**
- ✅ **Unicode analysis complete** - discovered ZWNJ as THE quality metric

**Phase 7 Goal:**
- 🎯 Improve biographical accuracy from 71.69% → **76%+**
- 🎯 Find sources with 6-10% ZWNJ density
- 🎯 Target: 500-1,000 biographical sentences

**Quality Indicators:**

- **ZWNJ (U+200C):** 9-11% density indicates proper Kurdish formatting
- **Tatweel (U+0640):** ~0.025% (irrelevant for Kurdish OCR)
- **News corpus:** High-quality source with proper ZWNJ usage
- **Wikipedia:** Excluded due to low ZWNJ (0.106% = corrupted)

**See:** 
- [PHASE6_COMPLETE.md](PHASE6_COMPLETE.md) - Phase 6 summary and strategic options
- [PHASE7_QUICKSTART.md](PHASE7_QUICKSTART.md) - Start improving accuracy now!
- [UNICODE_CHARACTER_ANALYSIS.md](UNICODE_CHARACTER_ANALYSIS.md) - Detailed quality analysis

### Working Websites (13/14)

| Website     | Categories | Sentences/Test | Speed | Notes                |
| ----------- | ---------- | -------------- | ----- | -------------------- |
| avanews     | 6          | 18             | 576s  | ✅ Full support      |
| awene       | 3          | 126            | 127s  | ✅ Full support      |
| balinde     | 2          | 330            | 88s   | ✅ Poetry & articles |
| govkrd      | 1          | 19             | 45s   | ✅ Government news   |
| kurdistan24 | 5          | 109            | 132s  | ✅ **FlareSolverr**  |
| kurdsat     | 5          | 48             | 130s  | ✅ Full support      |
| lvinpress   | 3          | 68             | 295s  | ✅ Full support      |
| nrt         | 6          | 109            | 282s  | ✅ Full support      |
| rudaw       | 3          | 68             | 79s   | ✅ Full support      |
| sekokurd    | 2          | 113            | 78s   | ✅ Full support      |
| sharpress   | 2          | 6              | 73s   | ✅ Full support      |
| xendan      | 3          | 9              | 112s  | ✅ Full support      |
| yariga      | 1          | 29             | 46s   | ✅ Full support      |

**Disabled:** khak (API issues)

## **Total:** 1,052 sentences per test run across 48 categories

## 🔧 Configuration

### Adding a New Website

1. Create YAML config in `work/tools/scrapers/configs/`:

```yaml
name: 'Website Name'
base_url: 'https://example.com'
enabled: true

selectors:
  article_list: 'article.post'
  article_title: 'h1.title'
  article_body: 'div.content p'

categories:
  news:
    url: 'https://example.com/news'
    pagination:
      type: 'url_template'
      pages: 3
      page_param: 'page'
```

2. Test it:

```bash
cd work/tools
python3 test_suite.py your_website --max-articles 1
```

3. Debug if needed:

```bash
python3 test_debug.py your_website --test-selectors
```

See [docs/SCRAPER_QUICK_START.md](docs/SCRAPER_QUICK_START.md) for detailed configuration options.

---

## 📚 Documentation

### User Guides

- **[Quick Start](docs/SCRAPER_QUICK_START.md)** - Get started in 5 minutes
- **[Advanced Features](docs/ADVANCED_FEATURES.md)** - FlareSolverr, deduplication, rate limiting
- **[Network Features](docs/NETWORK_FEATURES.md)** - HTTP caching, retry, proxy support ✨NEW
- **[Production Guide](docs/PRODUCTION_READINESS.md)** - Deployment best practices

### Technical Docs

- **[Generic Scraper](work/tools/scrapers/README.md)** - Framework documentation
- **[Debug Tool](work/tools/scrapers/docs/DEBUG_TOOL_GUIDE.md)** - Debugging guide
- **[Test Suite](work/tools/TEST_SUITE_RESUME.md)** - Test suite features

### Phase 7 Tools (Accuracy Improvement) 🚀

- **[Phase 7 Plan](PHASE7_IMPROVEMENT_PLAN.md)** - Complete improvement strategy
- **[Phase 7 Quick Start](PHASE7_QUICKSTART.md)** - Start improving accuracy now!
- **Source Validator** - `python work/tools/validate_source_quality.py sample.txt`
- **Corpus Blender** - `python work/tools/blend_corpus.py --sources file1.txt file2.txt`
- **Unicode Analyzer** - `python work/analyze_unicode_chars.py corpus.txt`

### Reference

- **[Kurdish Characters](docs/kurdish_characters.md)** - Script reference
- **[Config Schema](work/tools/scrapers/configs/config.schema.json)** - YAML validation

---

## 🐛 Troubleshooting

### Common Issues

**FlareSolverr not running (for Kurdistan24):**

```bash
# Start FlareSolverr
wsl -d Ubuntu -- sudo docker start flaresolverr

# Or install it:
docker run -d -p 8191:8191 --name flaresolverr ghcr.io/flaresolverr/flaresolverr:latest
```

**Selenium/ChromeDriver issues:**

```bash
# Install ChromeDriver in WSL
wsl -d Ubuntu -- sudo apt install chromium-chromedriver
```

**Test suite interrupted:**

```bash
# Resume from where it left off
cd work/tools
python3 test_suite.py --resume

# Start fresh
python3 test_suite.py --fresh
```

**Website selectors not working:**

```bash
# Debug selectors
python3 test_debug.py website_name --test-selectors --verbose

# Test pagination
python3 test_debug.py website_name --pagination-only

# View config
python3 test_debug.py website_name --config-only
```

See [docs/PRODUCTION_READINESS.md](docs/PRODUCTION_READINESS.md#troubleshooting) for more solutions.

---

## 🧪 Testing

```bash
cd work/tools

# Quick test (1 article per site)
python3 test_suite.py --max-articles 1

# Full test (all sites, 3 articles each)
python3 test_suite.py --max-articles 3

# Test specific sites
python3 test_suite.py yariga rudaw nrt --max-articles 5

# List available websites
python3 test_suite.py --list

# Debug specific website
python3 test_debug.py kurdistan24 --category politics --test-selectors
```

---

## 📈 Performance

- **Average:** 13 websites in ~45 minutes (3 articles each)
- **Fastest:** yariga (29 sentences in 46s)
- **Slowest:** avanews (18 sentences in 576s - rate limited)
- **FlareSolverr:** kurdistan24 (109 sentences in 132s)
- **Total Output:** ~1,052 sentences per full test run

---

## 🛠️ Requirements

### System Requirements

- Windows 10/11 with WSL2
- Ubuntu 20.04+ installed in WSL
- Python 3.8+ in WSL
- Tesseract OCR 4.1+ in WSL

### Python Dependencies (in WSL)

```bash
# Install from work/tools directory
cd work/tools
pip3 install -r requirements.txt
```

### Optional: FlareSolverr (for Cloudflare-protected sites)

```bash
# Install Docker in WSL
docker run -d -p 8191:8191 --name flaresolverr \
  ghcr.io/flaresolverr/flaresolverr:latest
```

---

## 🤝 Contributing

### Adding a Website

1. Create config file in `work/tools/scrapers/configs/`
2. Test with `python3 test_suite.py your_site`
3. Debug with `python3 test_debug.py your_site --test-selectors`
4. Submit PR with config file only (no code changes!)

### Improving Accuracy

1. Update selectors in YAML config
2. Test changes with test suite
3. No code changes needed - pure configuration!

---

## 📄 License

This project is for Kurdish language OCR training purposes.

---

## 🔗 Related Projects

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr)
- [Selenium](https://www.selenium.dev/)

---

**Questions?** See [docs/SCRAPER_QUICK_START.md](docs/SCRAPER_QUICK_START.md) or [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)
