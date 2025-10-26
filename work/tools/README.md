# Kurdish Web Scraping Tools

This directory contains tools for scraping Kurdish news websites and generating training data for Tesseract OCR.

## Table of Contents

1. [Web Scraping Tools](#web-scraping-tools)
2. [Debug and Testing](#debug-and-testing)
3. [Network Features](#network-features)
4. [Corpus Building](#corpus-building)
5. [Evaluation](#evaluation)

## Web Scraping Tools

### Generic Scraper (V5.0)

Production-ready scraper with configuration-driven approach.

**Location**: `scrapers/generic_scraper.py`

**Features**:

- Configuration-driven (YAML configs)
- 14/17 websites working
- FlareSolverr support for Cloudflare
- Language detection
- Click-through navigation
- Multiple pagination types
- Advanced network features

**Usage**:

```bash
cd work/tools
python3 run_scraper.py WEBSITE --category CATEGORY
```

**Supported Websites**:

- ✅ rudaw
- ✅ nrt
- ✅ kurdsat
- ✅ kurdistan24
- ✅ xendan
- ✅ awene
- ✅ lvinpress
- ✅ avanews
- ✅ balinde
- ✅ govkrd
- ✅ sharpress
- ✅ sekokurd
- ⏭️ yariga (partial)
- ⏭️ khak (partial)

## Debug and Testing

### Debug Tool

**Location**: `test_debug.py`

Interactive debugging tool with extensive logging and controls.

**Features**:

- Website configuration viewer
- Category-specific debugging
- Selector testing
- Pagination testing
- Wait strategy debugging
- Screenshot capture
- **🆕 URL tracking** - Monitor all network requests

**Usage**:

```bash
# Debug entire website
python3 test_debug.py rudaw

# Debug specific category
python3 test_debug.py rudaw --category kurdistan

# Test selectors
python3 test_debug.py rudaw --category kurdistan --test-selectors

# Debug with headful browser
python3 test_debug.py rudaw --headful --verbose

# Track all URLs (identify third-party services)
python3 test_debug.py rudaw --category kurdistan --track-urls --headful
```

**Options**:

- `--category, -c`: Specific category to debug
- `--max-articles, -m`: Maximum articles to scrape (default: 3)
- `--headful`: Run browser in visible mode
- `--verbose, -v`: Enable verbose logging
- `--screenshots, -s`: Save screenshots during debugging
- `--track-urls, -t`: **Track and analyze all network requests**
- `--config-only`: Show configuration without scraping
- `--test-selectors`: Test selector extraction only
- `--pagination-only`: Test pagination without article extraction
- `--debug-waits`: Debug wait strategies

### URL Tracking Feature 🆕

Monitor all network requests to identify third-party services (analytics, ads, tracking) and create accurate whitelist/blacklist rules.

**Quick Start**:

```bash
# Track URLs during scraping
python3 test_debug.py rudaw --category kurdistan --track-urls --headful
```

**Output**:

```
🌐 NETWORK REQUEST TRACKING SUMMARY
================================================================================

📊 Overview:
   Total Requests: 87
   First-Party: 32 requests
   Third-Party: 55 requests from 12 domains
   Base Domain: rudaw.net

📋 Requests by Type:
   SCRIPT           38 total (25 third-party)
   STYLESHEET       12 total (5 third-party)
   IMAGE            41 total (30 third-party)
   XHR              15 total (10 third-party)

🌍 Third-Party Domains (12):
      18x  google-analytics.com
      12x  googletagmanager.com
       8x  facebook.net
       5x  doubleclick.net

💡 Suggested Blacklist Patterns (Third-Party Services):
   # Analytics/Tracking
   '*.google-analytics.com'
   '*.googletagmanager.com'

   # Advertising
   '*.doubleclick.net'

   # Social Media
   '*.facebook.net'

💡 Suggested Whitelist Patterns (Main Content):
   '*.rudaw.net'  # Main website
   '*.rudaw-cdn.net'  # CDN

💡 Path-Based Patterns:
   '*/analytics/*'
   '*/tracking/*'
   '*/pixel/*'
   '*/beacon/*'

📁 URL tracking report saved: url_tracking_rudaw_20240115_143022.json
```

**Use Cases**:

1. Identify third-party tracking/analytics
2. Create URL filters to block unwanted services
3. Improve scraping performance
4. Reduce attack surface
5. Privacy & security auditing

**Documentation**: See [docs/URL_TRACKING.md](../../docs/URL_TRACKING.md)

## Network Features

### Advanced Network Features Module

**Location**: `network_features.py`

Production-ready HTTP client with advanced features.

**Features**:

- ✅ Response caching (memory + disk)
- ✅ Automatic retry with exponential backoff
- ✅ Proxy rotation with health checking
- ✅ **URL filtering with wildcards**

**Components**:

#### 1. SessionManager

HTTP client with pooling and compression.

```python
from network_features import SessionManager

session = SessionManager(
    cache_enabled=True,
    retry_enabled=True,
    proxy_enabled=False
)

response = session.get('https://example.com')
```

#### 2. ResponseCache

Two-tier caching system (memory LRU + disk).

```python
from network_features import ResponseCache

cache = ResponseCache(cache_dir='cache', ttl=3600)
cache.set('key', 'value')
value = cache.get('key')
```

#### 3. RetryHandler

Exponential backoff with jitter.

```python
from network_features import RetryHandler

retry = RetryHandler(max_retries=3, backoff_factor=2.0, jitter=True)
retry.wait(attempt=1)  # Waits with backoff
```

#### 4. ProxyManager

Round-robin rotation with health checking.

```python
from network_features import ProxyManager

proxy_mgr = ProxyManager(['proxy1:8080', 'proxy2:8080'])
proxy = proxy_mgr.get_proxy()
```

#### 5. URLFilter 🆕

Whitelist/blacklist with wildcard patterns.

```python
from network_features import URLFilter

url_filter = URLFilter(
    whitelist=[
        '*.rudaw.net',           # Main website
        '*.rudaw-cdn.net',       # CDN
    ],
    blacklist=[
        '*.google-analytics.com',  # Analytics
        '*.facebook.net',          # Social tracking
        '*/analytics/*',           # Path-based
        '*/tracking/*',            # Path-based
        '*.pdf',                   # File type
    ]
)

allowed, reason = url_filter.is_allowed('https://rudaw.net/article')
# (True, "Matched whitelist pattern: *.rudaw.net")

allowed, reason = url_filter.is_allowed('https://google-analytics.com/collect')
# (False, "Matched blacklist pattern: *.google-analytics.com")
```

**Pattern Matching**:

- Wildcard support: `*`, `?`, `[abc]`
- Domain patterns: `*.domain.com`
- Path patterns: `/api/*/data`, `*/ads/*`
- File patterns: `*.pdf`, `*.mp4`

**Integration**:

```python
# Use URLFilter with SessionManager
session = SessionManager(
    url_whitelist=['*.rudaw.net', '*.nrt.tv'],
    url_blacklist=['*.google-analytics.com', '*/tracking/*']
)

# Blocked URLs return None
response = session.get('https://google-analytics.com/collect')  # None
response = session.get('https://rudaw.net/article')  # Success
```

**Documentation**: See [docs/NETWORK_FEATURES.md](../../docs/NETWORK_FEATURES.md)

## Corpus Building

### Corpus Builder

**Location**: `tools/corpus_build.py`

Builds training corpus from scraped sentences.

**Features**:

- Character balancing
- Frequency filtering
- Deduplication
- Format validation
- Multiple sources

**Usage**:

```bash
cd work/tools
python3 corpus_build.py --input sentences.txt --output corpus.txt --min-count 2
```

### Corpus Auditor

**Location**: `tools/corpus_audit.py`

Analyzes corpus composition and coverage.

**Features**:

- Character frequency analysis
- Coverage statistics
- Format validation
- Detailed reporting

**Usage**:

```bash
python3 corpus_audit.py corpus/ckb.training_text
```

### Corpus Statistics

**Location**: `tools/corpus_stats.py`

Generates detailed statistics about corpus.

**Usage**:

```bash
python3 corpus_stats.py corpus/ckb.training_text
```

## Evaluation

### Real CER Evaluator

**Location**: `tools/eval_real_cer.py`

Evaluates Tesseract accuracy on real images.

**Usage**:

```bash
cd work/tools
python3 eval_real_cer.py
```

**Requirements**:

- Images in `work/real_gt/eval/`
- Ground truth `.gt.txt` files
- Tesseract installed

### Evaluation Tuner

**Location**: `tools/eval_tuner.py`

Tunes PSM (Page Segmentation Mode) for best accuracy.

**Usage**:

```bash
python3 eval_tuner.py --psm-range 6,7,11,13
```

## Demo Scripts

### Network Features Demo

**Location**: `demo_network_features.py`

Interactive demos for all network features.

```bash
python3 demo_network_features.py
```

### URL Tracking Demo 🆕

**Location**: `demo_url_tracking.py`

Quick start guide for URL tracking feature.

```bash
python3 demo_url_tracking.py
```

### URL Filter Demo

**Location**: `quick_test_url_filter.py`

Test URL filtering patterns.

```bash
python3 quick_test_url_filter.py
```

## Test Scripts

### Test Debug

**Location**: `test_debug.py`

Main debugging tool (described above).

### Test Network Features

**Location**: `test_network_features.py`

Verify network features module.

```bash
python3 test_network_features.py
```

### Test URL Filter

**Location**: `test_url_filter.py`

Test URL filtering functionality.

```bash
python3 test_url_filter.py
```

### Test URL Tracking 🆕

**Location**: `test_url_tracking.py`

Verify URL tracking feature.

```bash
python3 test_url_tracking.py
```

**Output**:

```
================================================================================
URL TRACKING FEATURE TESTS
================================================================================
[PASS]: URL Tracking Structure
[PASS]: URL Categorization
[PASS]: Report Generation
[PASS]: Pattern Suggestions

4/4 tests passed
```

## Configuration Files

### Website Configs

**Location**: `scrapers/configs/*.yaml`

YAML configuration files for each website.

**Structure**:

```yaml
name: Website Name
base_url: https://example.com
enabled: true

selectors:
  article: '.article'
  title: 'h1.title'
  content: '.content p'

categories:
  news:
    url: https://example.com/news
    enabled: true
    type: pagination
```

## Utilities

### Kurdish Character Fixer

**Location**: `kurdish_character_fixer.py`

Normalizes Kurdish text for training.

**Features**:

- Character normalization
- Diacritic handling
- Shaping mark normalization

### Bootstrap WSL Training

**Location**: `tools/bootstrap_wsl_training.sh`

Sets up WSL environment for Tesseract training.

### Generate Shaping Augment

**Location**: `tools/generate_shaping_augment.py`

Generates text variations for Arabic shaping.

## Quick Reference

### Common Workflows

#### 1. Debug a Website

```bash
cd work/tools
python3 test_debug.py rudaw --category kurdistan --headful --verbose
```

#### 2. Track URLs to Create Filters

```bash
# Step 1: Track URLs
python3 test_debug.py rudaw --category kurdistan --track-urls --headful

# Step 2: Review output and create filter
# (See suggestions in console output)

# Step 3: Use filter in SessionManager
python3 -c "
from network_features import SessionManager
session = SessionManager(
    url_whitelist=['*.rudaw.net'],
    url_blacklist=['*.google-analytics.com']
)
"
```

#### 3. Scrape with Advanced Features

```python
from scrapers.generic_scraper import GenericScraper

scraper = GenericScraper('scrapers/configs')
result = scraper.scrape_category('rudaw', 'kurdistan', max_articles=10)
```

#### 4. Build Corpus

```bash
cd work/tools
python3 corpus_build.py \
    --input scraped_sentences.txt \
    --output corpus/ckb.training_text \
    --min-count 2 \
    --balance-digits \
    --balance-puncs
```

#### 5. Evaluate Model

```bash
cd work
python3 tools/eval_real_cer.py
```

## Documentation

### Main Docs

- [URL Tracking Guide](../../docs/URL_TRACKING.md) - Complete URL tracking documentation
- [URL Tracking Implementation](../../docs/URL_TRACKING_IMPLEMENTATION.md) - Technical details
- [Network Features](../../docs/NETWORK_FEATURES.md) - Complete network features guide
- [Kurdish Characters](../../docs/kurdish_characters.md) - Kurdish script reference

### README Files

- [Work README](../README.md) - Main work directory README
- [Project README](../../README.md) - Top-level project README

## Dependencies

### Required

- Python 3.6+
- Selenium WebDriver
- Chrome/Chromium browser
- ChromeDriver (for Selenium)
- Tesseract OCR (for evaluation)

### Python Packages

```bash
pip install selenium requests pyyaml pillow
```

### Optional

- FlareSolverr (for Cloudflare bypass)
- WSL (for Tesseract training on Windows)

## Environment Setup

### WSL (Ubuntu)

```bash
# Install Python packages
pip3 install selenium requests pyyaml pillow

# Install Chrome/Chromium
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver

# Install Tesseract
sudo apt-get install tesseract-ocr
```

### Windows

```powershell
# Install Python packages
pip install selenium requests pyyaml pillow

# Download ChromeDriver
# https://chromedriver.chromium.org/

# Add to PATH
```

## Troubleshooting

### Common Issues

#### 1. ChromeDriver version mismatch

```bash
# Check Chrome version
google-chrome --version

# Download matching ChromeDriver
# https://chromedriver.chromium.org/downloads
```

#### 2. Selenium can't find ChromeDriver

```bash
# Add to PATH
export PATH=$PATH:/path/to/chromedriver
```

#### 3. URL tracking shows 0 requests

```bash
# Use Chrome (not Firefox)
# Enable headful mode to debug
python3 test_debug.py rudaw --track-urls --headful --verbose
```

#### 4. Website blocks scraping

```bash
# Try with FlareSolverr
# See docs/FLARESOLVERR.md
```

## Contributing

### Adding a New Website

1. Create config file: `scrapers/configs/WEBSITE.yaml`
2. Test with debug tool: `python3 test_debug.py WEBSITE --headful`
3. Verify selectors: `python3 test_debug.py WEBSITE --test-selectors`
4. Test pagination: `python3 test_debug.py WEBSITE --pagination-only`
5. Track URLs if needed: `python3 test_debug.py WEBSITE --track-urls`

### Testing Changes

```bash
# Run all tests
cd work/tools

python3 test_network_features.py
python3 test_url_filter.py
python3 test_url_tracking.py
python3 test_debug.py rudaw --config-only
```

## License

See main project LICENSE file.

## Contact

For issues or questions, please use the project issue tracker.

---

**Last Updated**: 2024-01-15  
**Tools Version**: V5.0  
**Key Features**: URL Tracking, Network Features, Generic Scraper
