# Tesseract OCR Training - Central Kurdish (ckb)

**Status:** Production Ready ✅  
**Version:** 6.0.0  
**Last Updated:** November 8, 2025

---

## 🎯 Project Overview

This project trains a custom Tesseract OCR model for **Central Kurdish (Sorani)** script using modern machine learning techniques and real-world Kurdish news articles.

### Key Features

- ✅ **Parallel Training Generation** - 3 workers process fonts simultaneously
- ✅ **Fully Resumable** - Stop and restart without losing progress
- ✅ **Auto-mount NAS Storage** - Automatic Z: drive configuration
- ✅ **Live Progress Bars** - Real-time worker status display
- ✅ **Dual Training Profiles** - Best (2-3 days) and Fast (2-3 hours)
- ✅ **14 Kurdish news websites** successfully scraped (1,052 sentences per test run)
- ✅ **Generic Scraper V5.0** - unified configuration-driven architecture
- ✅ **FlareSolverr integration** for Cloudflare-protected sites
- ✅ **Advanced features**: deduplication, language detection, rate limiting
- ✅ **100% configuration-based** - no code changes needed for new sites

---

## 📁 Project Structure

```
tesseract/
├── README.md                      # This file
├── run_training.ps1               # Main training driver (PowerShell)
├── setup_z_mount.sh               # NAS Z: drive auto-mount script
├── docs/                          # Documentation
│   ├── SCRAPER_QUICK_START.md    # Quick start guide
│   ├── PRODUCTION_READINESS.md    # Production deployment
│   └── kurdish_characters.md      # Kurdish script reference
├── work/                          # Training workspace
│   ├── generate_ckb_training_data.sh      # Main generation script
│   ├── parallel_font_processor.sh         # Parallel worker script
│   ├── kurdish_character_fixer.py         # Corpus normalizer
│   ├── corpus/                    # Training text data
│   ├── fonts/                     # Kurdish fonts (9 fonts)
│   ├── training_output_best/      # Best profile output
│   ├── training_output_fast/      # Fast profile output
│   └── tools/                     # Scraping & utilities
│       ├── test_suite.py         # Production test suite
│       └── scrapers/             # Generic scraper framework
│           ├── generic_scraper.py        # V5.0 unified scraper
│           └── configs/                  # 17 website configs
└── tessdata/                      # Trained models
    ├── best/                      # Best quality models
    └── fast/                      # Fast models
```

---

## 🚀 Quick Start

### 1. Generate Training Data (Parallel Mode)

```powershell
# Fast profile (2-3 hours, ~2,592 images)
.\run_training.ps1 -Mode ImprovedGenerate -TrainingProfile Fast

# Best profile (2-3 days, ~87,480 images) with 3 parallel workers
.\run_training.ps1 -Mode ImprovedGenerate -TrainingProfile Best -ParallelJobs 3

# Best profile on NAS storage (auto-mounts Z: drive)
.\run_training.ps1 -Mode ImprovedGenerate -TrainingProfile Best -ParallelJobs 3 -OutputDirOverride "Z:\training_output_best" -NoClear

# Resume interrupted generation (automatically skips existing files)
.\run_training.ps1 -Mode ImprovedGenerate -TrainingProfile Best -ParallelJobs 3 -NoClear
```

**Resumability**: You can safely press `Ctrl+C` to stop generation and restart anytime. The system automatically skips already-generated files.

### 2. Test Web Scrapers

```bash
# Test all 14 websites (3 articles each) - from work/tools directory
cd work/tools
wsl -d Ubuntu -- bash -lc "cd '/mnt/c/tesseract/work/tools' && python3 test_suite.py --max-articles 3"

# Test specific website
python3 test_suite.py yariga --max-articles 10
```

### 3. Train Model

```powershell
# Full training pipeline (generation + training)
.\run_training.ps1 -Mode GenerateTrain

# Smoke test trained model
.\run_training.ps1 -Mode SmokeTest
```

---

## � Parallel Training Generation

### Overview

The training data generation system supports parallel processing with **3 simultaneous workers** (configurable), dramatically reducing generation time from weeks to hours:

- **Best Profile**: ~87,480 images in ~29 hours with 3 workers (vs. ~262 hours sequential)
- **Fast Profile**: ~2,592 images in ~0.8 hours with 3 workers (vs. ~2.5 hours sequential)

Each worker processes a complete font (all parameter combinations) while displaying live progress on its own line.

### Architecture

```
run_training.ps1 (PowerShell)
    ↓
setup_z_mount.sh (Auto-mount NAS if Z: path detected)
    ↓
generate_ckb_training_data.sh (Main Bash Script)
    ↓
GNU Parallel (Spawns 3 workers)
    ↓
parallel_font_processor.sh × 3 (Each processes 1 font)
    ↓
Ground truth files (.tif + .box)
```

### Live Progress Display

Each worker displays periodic progress updates as they process fonts. Progress updates are shown every 50 images or at 10% milestones to keep output readable:

```
[Worker 1/9] Arial-Unicode-MS - Starting...
[Worker 2/9] DejaVu-Sans - Starting...
[Worker 3/9] NRT-Reg - Starting...
[Worker 1/9] Arial-Unicode-MS [===>---------] 10% (293/2934) - New: 293, Skipped: 0
[Worker 2/9] DejaVu-Sans [===>---------] 10% (293/2934) - New: 293, Skipped: 0
[Worker 3/9] NRT-Reg [===>---------] 10% (293/2934) - New: 150, Skipped: 143
[Worker 1/9] Arial-Unicode-MS [======>------] 20% (587/2934) - New: 587, Skipped: 0
[Worker 2/9] DejaVu-Sans [======>------] 20% (587/2934) - New: 587, Skipped: 0
...
```

When complete:

```
[Worker 1/9] Arial-Unicode-MS ✅ Success (New: 2850, Skipped: 84, Total: 2934/2934)
[Worker 2/9] DejaVu-Sans ✅ Success (New: 2934, Skipped: 0, Total: 2934/2934)
[Worker 3/9] NRT-Reg ✅ Success (New: 2500, Skipped: 434, Total: 2934/2934)
```

**Note**: Updates are interleaved from all workers, creating a live stream of progress from all 3 parallel processes.

### Resumability

**Automatic Skip Detection**: The system checks for existing `.tif` and `.box` files before generating each image. If both exist, the file is skipped (counted in "Skipped").

**Resume After Interruption**:

```powershell
# Start generation
.\run_training.ps1 -Mode GenerateTrain -TrainingProfile Best -ParallelJobs 3

# Press Ctrl+C to interrupt
# Re-run the same command - it will skip all existing files and continue
.\run_training.ps1 -Mode GenerateTrain -TrainingProfile Best -ParallelJobs 3
```

**Progress Tracking**:

- Shows percentage complete based on (New + Skipped) / Total
- Displays file counts: newly created vs. skipped
- Updates every 5 images to balance visibility and output volume

### NAS Storage Integration

**Automatic Z: Drive Mounting**:

- When `OutputDirOverride` contains a Z: path, the script automatically mounts it in WSL
- Runs `setup_z_mount.sh` to configure passwordless sudo and mount `/mnt/z`
- Creates all required directories with proper permissions

**Example**:

```powershell
# Automatically mounts Z: as /mnt/z in WSL
.\run_training.ps1 -Mode GenerateTrain -TrainingProfile Best -OutputDirOverride "Z:\training_output_best" -ParallelJobs 3
```

**Manual Setup** (one-time):

```bash
# In WSL, configure passwordless mounting
wsl -d Ubuntu -- bash /mnt/c/tesseract/setup_z_mount.sh
```

### Training Profiles

| Parameter             | Best Profile                                   | Fast Profile           |
| --------------------- | ---------------------------------------------- | ---------------------- |
| Font Sizes            | 4 (24,32,40,48)                                | 2 (32,40)              |
| DPIs                  | 3 (200,250,300)                                | 2 (200,300)            |
| Leading               | 3 (24,32,40)                                   | 2 (28,36)              |
| Character Spacing     | 3 (0.0,0.05,0.1)                               | 2 (0.0,0.05)           |
| Exposures             | 5 (-2,-1,0,+1,+2)                              | 3 (-1,0,+1)            |
| Variants              | 6 (normal,bold,italic,underline,shadow,random) | 3 (normal,bold,random) |
| **Total Images**      | ~87,480 images                                 | ~2,592 images          |
| **Time (3 workers)**  | ~29 hours                                      | ~0.8 hours             |
| **Time (Sequential)** | ~262 hours (11 days)                           | ~2.5 hours             |

### Performance Tuning

**Adjust Worker Count**:

```powershell
# More workers = faster (up to CPU core count)
.\run_training.ps1 -Mode GenerateTrain -TrainingProfile Best -ParallelJobs 8

# Sequential (no parallelism)
.\run_training.ps1 -Mode GenerateTrain -TrainingProfile Best -ParallelJobs 0
```

**Recommended Worker Counts**:

- **3 workers**: Default, balanced for most systems
- **8-16 workers**: High-end workstations with 16+ CPU cores
- **0 workers**: Sequential mode for debugging or limited resources

**Estimated Times** (Best Profile with 9 fonts):

- 1 worker (sequential): ~262 hours (11 days)
- 3 workers: ~29 hours
- 8 workers: ~11 hours
- 16 workers: ~6 hours

### Monitoring Progress

**Check Current Status**:

```powershell
# Count generated files
(Get-ChildItem "Z:\training_output_best\ground_truth\*.tif").Count

# Calculate percentage (Best profile)
$files = (Get-ChildItem "Z:\training_output_best\ground_truth\*.tif").Count
$total = 87480
$percent = [math]::Round(($files / $total) * 100, 2)
Write-Host "$percent% complete ($files / $total files)"
```

**Live Output**: Watch the console for real-time progress from each worker.

---

## Current Status

### Training Generation v6.0.0 ✅

**Latest Improvements:**

- ✅ **Parallel Processing**: 3 simultaneous workers (3× faster than sequential)
- ✅ **Resumability**: Automatic skip of existing files, interrupt/resume anytime
- ✅ **NAS Storage**: Auto-mount Z: drive for large-scale storage
- ✅ **Live Progress**: Each worker displays real-time progress on its own line
- ✅ **Dual Profiles**: Best (87k images, ~29h) and Fast (2.6k images, ~0.8h)

**Generation Statistics** (Current Run):

- **Profile**: Best (87,480 total images with 9 fonts)
- **Progress**: ~1,530 files generated (~1.75% complete)
- **Workers**: 3 parallel workers
- **Output**: Z:\training_output_best\ground_truth\
- **Estimated Remaining**: ~19 hours (with 3 workers)

### Phase 6-7: OCR Accuracy ✅

**Baseline Achievement:**

- ✅ **76.9% accuracy** on modern Kurdish news text
- ⚠️ **71.69% accuracy** on biographical text
- ✅ **ZWNJ density:** 9.331% in training corpus (excellent quality)
- ✅ **Model ready for production deployment**

**Current Goal:**

- 🎯 Improve biographical accuracy from 71.69% → **76%+** with Best profile
- 🎯 Leverage 60× larger training dataset (87k vs 1.4k images)
- 🎯 Target: High-quality corpus with 6-10% ZWNJ density

**Quality Indicators:**

- **ZWNJ (U+200C):** 9-11% density indicates proper Kurdish formatting
- **News corpus:** High-quality source with proper ZWNJ usage

**See:**

- [UNICODE_CHARACTER_ANALYSIS.md](UNICODE_CHARACTER_ANALYSIS.md) - Detailed quality analysis
- [ZWNJ_TATWEEL_SUMMARY.md](ZWNJ_TATWEEL_SUMMARY.md) - Character usage patterns

### Working Websites (13/14)

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

### Training & Generation

- **[Parallel Training Guide](#-parallel-training-generation)** - 3-worker parallel processing with live progress
- **[Training Profiles](#training-profiles)** - Best vs Fast profile comparison
- **[NAS Storage Setup](#nas-storage-integration)** - Auto-mount Z: drive configuration
- **[Resumability](#resumability)** - Interrupt and resume generation anytime

### Corpus & Quality Tools

- **Source Validator** - `python work/tools/validate_source_quality.py sample.txt`
- **Corpus Blender** - `python work/tools/blend_corpus.py --sources file1.txt file2.txt`
- **Unicode Analyzer** - `python work/analyze_unicode_chars.py corpus.txt`
- **[Unicode Analysis](UNICODE_CHARACTER_ANALYSIS.md)** - ZWNJ/Tatweel quality metrics
- **[Character Summary](ZWNJ_TATWEEL_SUMMARY.md)** - Character usage patterns

### Scraper Guides

- **[Quick Start](docs/SCRAPER_QUICK_START.md)** - Get started in 5 minutes
- **[Advanced Features](docs/ADVANCED_FEATURES.md)** - FlareSolverr, deduplication, rate limiting
- **[Network Features](docs/NETWORK_FEATURES.md)** - HTTP caching, retry, proxy support
- **[Production Guide](docs/PRODUCTION_READINESS.md)** - Deployment best practices

### Technical Docs

- **[Generic Scraper](work/tools/scrapers/README.md)** - Framework documentation
- **[Debug Tool](work/tools/scrapers/docs/DEBUG_TOOL_GUIDE.md)** - Debugging guide
- **[Test Suite](work/tools/TEST_SUITE_RESUME.md)** - Test suite features

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
