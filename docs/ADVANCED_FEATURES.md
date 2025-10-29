# Advanced Features Guide

Complete guide to using advanced features in the Web Scraper Framework.

## Table of Contents

1. [Phase 5 Production Features](#phase-5-production-features) **✅ NEW**
   - [Rate Limiting](#rate-limiting)
   - [Redis Caching](#redis-caching)
   - [Retry Logic](#retry-logic)
   - [Proxy Rotation](#proxy-rotation)
2. [Multi-Language Support](#multi-language-support)
3. [Article Deduplication](#article-deduplication)
4. [Browser Fingerprinting Prevention](#browser-fingerprinting-prevention)
5. [CLI Tools](#cli-tools)
6. [Configuration Wizard](#configuration-wizard)
7. [Admin Dashboard](#admin-dashboard)

---

## Phase 5 Production Features

**Status:** ✅ **COMPLETE** - All 4 features implemented and tested (2025-10-29)

All advanced features are now fully integrated and configurable per-website via YAML. Features are **optional** and gracefully degrade if dependencies are unavailable.

### Rate Limiting

Polite scraping with configurable request rate per minute. Prevents IP blocking and server overload.

**Configuration:**

```yaml
# configs/websites/example.yaml
rate_limiting:
  enabled: true
  max_requests_per_minute: 30 # Adjust based on website tolerance
```

**Output:**

```
✅ Rate limiting enabled: 30 requests/min
```

**Features:**

- Configurable requests per minute
- Burst handling (allows temporary spikes)
- Per-website configuration
- Automatic waiting between requests

**When to use:**

- All production scraping (recommended)
- Websites with strict rate limits
- To avoid IP blocking

---

### Redis Caching

24-hour cache for scraped articles. Dramatically speeds up re-runs and reduces server load.

**Prerequisites:**

```bash
# Install Redis
sudo apt install redis-server

# Start Redis
sudo systemctl start redis
```

**Configuration:**

```yaml
caching:
  enabled: true
  redis_host: localhost # Or remote Redis server
  redis_port: 6379
  ttl_hours: 24 # Cache duration
```

**Output:**

```
✅ Redis cache connected: localhost:6379 (TTL: 24h)
✅ Redis caching enabled: localhost:6379 (TTL: 24h)
```

**Features:**

- 24-hour article cache
- Automatic cache invalidation
- Per-category caching
- Graceful degradation (works without Redis)

**Performance:**

- First run: Normal speed
- Cached run: **60x faster** (< 1 minute vs 60 minutes)

**When to use:**

- Development/testing (avoid re-scraping same content)
- Daily updates (re-scrape only after 24h)
- High-volume scraping

---

### Retry Logic

Automatic retry on failures with configurable attempts and exponential backoff.

**Configuration:**

```yaml
retry:
  enabled: true
  max_attempts: 3
  delay_seconds: 2 # Initial delay, doubles on each retry
```

**Output:**

```
✅ Retry logic enabled: 3 attempts, 2s delay
```

**Features:**

- Automatic retry on network errors
- Exponential backoff (2s, 4s, 8s)
- Configurable max attempts
- Detailed error logging

**When to use:**

- Unreliable network connections
- Websites with intermittent errors
- Production environments (recommended)

---

### Proxy Rotation

Round-robin or random proxy selection with automatic failure detection and tracking.

**Prerequisites:**
Create `proxies.txt` with your proxy list:

```
# proxies.txt
# Format: protocol://host:port or host:port (assumes http)

# HTTP proxies
http://proxy1.example.com:8080
192.168.1.100:3128

# SOCKS5 proxies
socks5://proxy2.example.com:1080
```

**Configuration:**

```yaml
proxy:
  enabled: true
  file: proxies.txt
  strategy: round-robin # or 'random'
```

**Output:**

```
✅ Proxy rotation enabled: proxies.txt (round-robin)
🔀 Using proxy: http://proxy1.example.com:8080
```

**Features:**

- Round-robin or random rotation
- Automatic failure detection
- Success/failure tracking per proxy
- HTTP and SOCKS5 support
- Automatic proxy switching on failures
- Warning when proxy failure rate exceeds 50%

**When to use:**

- IP blocking bypass
- Geographic distribution
- High-volume scraping
- Websites with strict IP limits

**Testing:**

```bash
# Verify proxy rotation works
python test_proxy_rotation.py
```

---

### Complete Configuration Example

Enable all 4 features in a website config:

```yaml
# configs/websites/example.yaml
name: 'Example News'
base_url: 'https://example.com'

# Rate Limiting - Polite scraping
rate_limiting:
  enabled: true
  max_requests_per_minute: 30

# Redis Caching - Fast re-runs
caching:
  enabled: true
  redis_host: localhost
  redis_port: 6379
  ttl_hours: 24

# Retry Logic - Automatic recovery
retry:
  enabled: true
  max_attempts: 3
  delay_seconds: 2

# Proxy Rotation - IP blocking bypass
proxy:
  enabled: true
  file: proxies.txt
  strategy: round-robin
# ... rest of config (categories, selectors, etc.)
```

**Expected Output:**

```
✅ Rate limiting enabled: 30 requests/min
✅ Redis cache connected: localhost:6379 (TTL: 24h)
✅ Redis caching enabled: localhost:6379 (TTL: 24h)
✅ Retry logic enabled: 3 attempts, 2s delay
✅ Proxy rotation enabled: proxies.txt (round-robin)
```

### Implementation Details

All features are initialized in `_init_advanced_features()` and integrated with the scraper:

- **Initialization**: Reads YAML config and initializes features per-website
- **Lazy Loading**: Only imports when feature is enabled
- **Graceful Degradation**: System works even if dependencies unavailable
- **Clear Logging**: Easy to see which features are active

**See Documentation:**

- `scrapers/PHASE5_TEST_RESULTS.md` - Complete test results
- `scrapers/PROXY_ROTATION_IMPLEMENTATION.md` - Proxy rotation guide
- `scrapers/PHASE5_FEATURES_IMPLEMENTATION.md` - Implementation details

---

## Multi-Language Support

Automatically detect and filter articles by language.

### Features

- **Language Detection**: Detect Kurdish (Sorani/Kurmanji), Arabic, Persian, English
- **Confidence Scoring**: Get confidence scores for language detection
- **Article Filtering**: Filter articles by target languages
- **Per-Language Configuration**: Different selectors for different languages

### Basic Usage

```python
from advanced_features import LanguageDetector

# Create detector
detector = LanguageDetector()

# Detect language
text = "هەواڵی نوێ لە کوردستان"
lang = detector.detect(text)
print(f"Language: {lang}")  # Output: ckb (Kurdish Sorani)

# Get confidence score
lang, confidence = detector.detect_with_confidence(text)
print(f"Language: {lang}, Confidence: {confidence:.2f}")

# Filter articles by language
articles = [
    {'title': 'هەواڵ', 'content': '...'},
    {'title': 'News', 'content': '...'},
]

filtered = detector.filter_by_language(articles, ['ckb', 'ar'])
```

### Configuration Example

```yaml
kurdsat:
  name: 'Kurdsat'
  base_url: 'https://kurdsat.tv'

  # Enable language detection
  language_detection:
    enabled: true
    filter: ['ckb', 'ar', 'en'] # Only keep these languages

  # Default selectors
  selectors:
    article_list: 'div.post-card'
    article_title: 'h1'

  # Per-language overrides
  languages:
    ckb: # Kurdish Sorani
      enabled: true
      selectors:
        article_content:
          - 'div.ناوەرۆک' # Kurdish class name
          - 'div.content-ku'
          - 'div.content'
      processing:
        normalize_digits: true

    ar: # Arabic
      enabled: true
      selectors:
        article_content: 'div.content-ar'

    en: # English
      enabled: false # Don't scrape English
```

### Supported Languages

| Code  | Language         | Script | Detection Method                                    |
| ----- | ---------------- | ------ | --------------------------------------------------- |
| `ckb` | Kurdish Sorani   | Arabic | Character ranges + specific letters (ڕ، ڵ، ە، ۆ، ێ) |
| `kmr` | Kurdish Kurmanji | Latin  | Latin + Kurdish letters (ç, ê, î, ş, û)             |
| `ar`  | Arabic           | Arabic | Arabic character range                              |
| `fa`  | Persian          | Arabic | Persian-specific letters (پ، چ، ژ، گ)               |
| `en`  | English          | Latin  | Latin character range                               |

---

## Article Deduplication

Prevent scraping duplicate articles across different sources.

### Features

- **URL Matching**: Exact URL hash matching
- **Title Similarity**: Fuzzy matching on article titles (85% threshold)
- **Content Similarity**: Compare first 500 characters (90% threshold)
- **Statistics**: Track deduplication effectiveness

### Basic Usage

```python
from advanced_features import ArticleDeduplicator

# Create deduplicator
dedup = ArticleDeduplicator('article_dedup.db')

# Check if article is duplicate
article = {
    'url': 'https://example.com/article1',
    'title': 'Breaking News from Kurdistan',
    'content': 'Full article text...'
}

is_duplicate, reason = dedup.is_duplicate(
    article,
    article['url'],
    article['title'],
    article['content'],
    title_threshold=0.85,    # 85% similar titles = duplicate
    content_threshold=0.90   # 90% similar content = duplicate
)

if is_duplicate:
    print(f"Skipping duplicate: {reason}")
else:
    # Process new article
    print("Processing new article")

# Get statistics
stats = dedup.get_stats()
print(f"Unique articles: {stats['unique_articles']}")
print(f"Duplicates detected: {stats['duplicates_detected']}")
print(f"Deduplication rate: {stats['deduplication_rate']}")
```

### Integration with Scraper

```python
# In your scraper code
deduplicator = ArticleDeduplicator()

for article in scraped_articles:
    is_dup, reason = deduplicator.is_duplicate(
        article,
        article['url'],
        article['title'],
        article['content']
    )

    if is_dup:
        logger.info(f"Skipping duplicate: {reason}")
        continue

    # Save to corpus
    save_article(article)
```

### Database Schema

The deduplication database stores:

- `url_hash`: SHA-256 hash of URL
- `title_hash`: Hash of normalized title
- `content_hash`: Hash of first 500 chars
- `first_seen`: When first encountered
- `last_seen`: When last seen
- `seen_count`: Number of times encountered

---

## Browser Fingerprinting Prevention

Prevent websites from detecting automated scraping.

### Features

- **User Agent Rotation**: Randomize from real browsers
- **WebRTC Blocking**: Prevent IP address leaks
- **Canvas Fingerprinting Protection**: Add noise to canvas data
- **Navigator Property Spoofing**: Hide automation markers
- **Automation Detection Bypass**: Remove webdriver property

### Basic Usage

```python
from advanced_features import StealthBrowser
from selenium import webdriver

# Create stealth browser
stealth = StealthBrowser()

# Get stealth options
options_config = stealth.get_stealth_options()

# Create Chrome driver with stealth
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument(f"user-agent={options_config['user_agent']}")

for arg in options_config['arguments']:
    options.add_argument(arg)

for key, value in options_config['experimental_options']['excludeSwitches']:
    options.add_experimental_option(key, value)

driver = webdriver.Chrome(options=options)

# Apply stealth mode
stealth.apply_stealth_mode(driver)

# Now use driver normally
driver.get('https://example.com')
```

### What It Does

1. **User Agent**: Rotates between 5+ real browser user agents
2. **WebRTC**: Disables WebRTC to prevent IP leaks
3. **Canvas**: Adds noise to canvas fingerprinting
4. **Navigator**: Spoofs `navigator.webdriver`, `navigator.plugins`, `navigator.languages`
5. **Automation**: Removes automation detection markers

---

## CLI Tools

Command-line tools for testing and debugging scrapers.

### Installation

```bash
pip install -r requirements.txt
```

### Available Commands

#### 1. Test Selector

Test CSS or XPath selectors on live pages.

```bash
# Test CSS selector
python cli_tools.py test-selector "https://kurdsat.tv" "div.post-card"

# Test XPath selector
python cli_tools.py test-selector "https://example.com" "//div[@class='article']" --type xpath

# Save screenshot
python cli_tools.py test-selector "https://example.com" "article" --screenshot

# Custom wait time
python cli_tools.py test-selector "https://example.com" "div.content" --wait 15
```

**Output:**

```
🔍 Testing selector on: https://example.com
   Selector: div.post-card
   Type: CSS

⏳ Loading page...
✅ Page loaded in 1.23s

⏳ Waiting for selector (max 10s)...
✅ Found 12 element(s)

   Element 1:
   - Tag: div
   - Text: Breaking news from...
   - ID: post-123
   - Class: post-card featured

📸 Screenshot saved: selector_test_1234567890.png
💾 Full results saved to: selector_test_1234567890.json
```

#### 2. Validate Configuration

Validate YAML configuration files.

```bash
python cli_tools.py validate websites.yaml
```

**Output:**

```
🔍 Validating configuration: websites.yaml

✅ YAML syntax valid

📝 Checking website: kurdsat
   ✅ name: Kurdsat
   ✅ base_url: https://kurdsat.tv
   ✅ selectors: present

============================================================
✅ Configuration is valid!
   Websites: 12
```

#### 3. Run Scraper

Run a scraper manually with custom options.

```bash
# Run scraper for website
python cli_tools.py run kurdsat

# Run specific category
python cli_tools.py run kurdsat --category news

# Limit articles
python cli_tools.py run kurdsat --limit 10

# Verbose output
python cli_tools.py run kurdsat --verbose
```

#### 4. Show Statistics

Display scraping statistics.

```bash
# Show stats for last 7 days
python cli_tools.py stats

# Show stats for specific website
python cli_tools.py stats --website kurdsat

# Show stats for last 30 days
python cli_tools.py stats --days 30
```

**Output:**

```
📊 Scraping Statistics (last 7 days)

============================================================
Total Scrapes: 156
Total Articles: 2,340
Total Sentences: 45,678
Avg Articles/Scrape: 15
Success Rate: 94.0%
Websites: 12
```

#### 5. Debug URL

Debug a problematic URL.

```bash
# Debug URL
python cli_tools.py debug "https://example.com/article"

# Verbose debugging
python cli_tools.py debug "https://example.com" --verbose
```

**Output:**

```
🐛 Debugging URL: https://example.com

⏳ Loading page...
✅ Loaded in 1.45s

Page Title: Example Domain
Body text length: 1234 characters

📝 Looking for common article elements...

Articles:
   ✅ article: 5 found
   ⚪ .article: not found
   ✅ .post: 3 found

Titles:
   ✅ h1: 1 found
   ✅ h2: 8 found

📸 Screenshot saved: debug_1234567890.png
```

---

## Configuration Wizard

Interactive tool to create scraper configurations.

### Basic Usage

```bash
# Run full interactive wizard
python config_wizard.py

# Auto-detect selectors from URL
python config_wizard.py --auto https://kurdsat.tv/news

# Generate quick-start template
python config_wizard.py --template > websites_template.yaml
```

### Wizard Steps

**Step 1: Basic Information**

```
📝 Step 1: Basic Information

Website ID (lowercase, no spaces) [kurdsat]: kurdsat
Website Name [Kurdsat]: Kurdsat News
Base URL [https://kurdsat.tv]: https://kurdsat.tv
```

**Step 2: Selector Configuration**

```
📡 Step 2: Selector Configuration

Attempt automatic selector detection? [Y/n]: y
Enter a sample article list URL for detection: https://kurdsat.tv/news

🔍 Analyzing https://kurdsat.tv/news...
✅ Page loaded

🔍 Looking for article list containers...
   ✅ Found 12 articles with: div.post-card

🔍 Looking for article links...
   ✅ Found links: 'a'

📊 Detection Summary:
   • article_list: div.post-card
   • article_link: a
   • article_title: h1
   • article_content: div.content

Use these detected selectors? [Y/n]: y
```

**Step 3: Categories**

```
📂 Step 3: Categories

Add category-specific configurations? [y/N]: y

Category name (or Enter to finish): news
URL for category 'news': https://kurdsat.tv/news
Override selectors for 'news'? [y/N]: n

Category name (or Enter to finish): [Enter]
✅ Added 1 categories
```

**Step 4: Advanced Options**

```
⚙️  Step 4: Advanced Options

Configure advanced options? [y/N]: y

📄 Pagination:
Enable pagination? [Y/n]: y
Pagination type (next_page/infinite_scroll) [next_page]: next_page
Max pages to scrape [5]: 5
Next button selector [a.next]: a.next-page

⏳ Wait Strategy:
Configure wait strategy? [y/N]: y
Wait type (selector/manual) [selector]: selector
Wait selector [div.content]: div.content
Timeout (seconds) [10]: 10
```

**Step 5: Review and Save**

```
📋 Step 5: Review Configuration

============================================================
kurdsat:
  name: Kurdsat News
  base_url: https://kurdsat.tv
  selectors:
    article_list: div.post-card
    article_link: a
    article_title: h1
    article_content: div.content
  ...

Save this configuration? [Y/n]: y
Output filename [kurdsat_config.yaml]: kurdsat_config.yaml

✅ Configuration saved to: /path/to/kurdsat_config.yaml

Validate configuration now? [Y/n]: y

🔍 Validating configuration...
✅ Configuration is valid!
```

---

## Admin Dashboard

Real-time web dashboard for monitoring scrapers.

### Starting the Dashboard

```bash
cd work/tools/scrapers/dashboard
python app.py
```

**Output:**

```
======================================================================
🚀 Starting Admin Dashboard
======================================================================

Dashboard URL: http://localhost:5000
Database: ../article_scraping.db

Press Ctrl+C to stop

 * Running on http://0.0.0.0:5000
```

### Dashboard Features

#### 1. Overview Statistics

- **Total Articles**: Count of all scraped articles
- **Articles Today**: Articles scraped in last 24 hours
- **Total Sentences**: Estimated sentence count
- **Active Websites**: Number of configured websites
- **Deduplication Rate**: Percentage of duplicates detected
- **Duplicates Detected**: Total duplicate articles found

#### 2. Charts & Visualizations

**Articles Over Time**

- Line chart showing daily article counts
- Last 7 days by default
- Interactive tooltips

**Articles by Website**

- Bar chart showing articles per website
- Top 10 websites
- Color-coded bars

#### 3. Website Status

Real-time status for each website:

- **Active** (green): Scraped within last 2 hours
- **Idle** (yellow): Scraped within last 24 hours
- **Stale** (red): Not scraped in over 24 hours

Shows:

- Last scrape time
- Total articles
- Articles scraped today

#### 4. Recent Activity

Live feed of recently scraped articles:

- Website name
- Article title
- Time ago (e.g., "5m ago", "2h ago")
- Auto-refreshes every 30 seconds

#### 5. Error Logs

Recent errors and warnings:

- Timestamp
- Severity level (ERROR/WARNING)
- Website name
- Error message
- Sortable and filterable

### API Endpoints

The dashboard provides REST APIs:

```bash
# Overview statistics
GET /api/overview

# Website status
GET /api/websites

# Recent activity
GET /api/activity?limit=50

# Metrics history
GET /api/metrics?days=7

# Error logs
GET /api/errors?limit=100

# Health check
GET /api/health
```

### Customization

Edit `dashboard/templates/dashboard.html` to customize:

- Colors and styling
- Chart types
- Refresh intervals
- Data display formats

---

## Complete Integration Example

Here's how to use all advanced features together:

```python
from advanced_features import (
    LanguageDetector,
    ArticleDeduplicator,
    StealthBrowser
)
from selenium import webdriver

# Initialize components
lang_detector = LanguageDetector()
deduplicator = ArticleDeduplicator()
stealth = StealthBrowser()

# Create stealth driver
options_config = stealth.get_stealth_options()
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={options_config['user_agent']}")
driver = webdriver.Chrome(options=options)
stealth.apply_stealth_mode(driver)

# Scrape articles
driver.get('https://kurdsat.tv/news')
articles = scrape_articles(driver)

# Process articles
processed = []
for article in articles:
    # 1. Detect language
    lang, confidence = lang_detector.detect_with_confidence(article['content'])

    # 2. Filter by language
    if lang not in ['ckb', 'ar']:
        continue

    # 3. Check for duplicates
    is_dup, reason = deduplicator.is_duplicate(
        article,
        article['url'],
        article['title'],
        article['content']
    )

    if is_dup:
        continue

    # 4. Add language metadata
    article['language'] = lang
    article['language_confidence'] = confidence

    processed.append(article)

driver.quit()

print(f"Processed {len(processed)} unique articles")
print(f"Deduplication stats: {deduplicator.get_stats()}")
```

---

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Test CLI tools**: `python cli_tools.py test-selector <url> <selector>`
3. **Create configuration**: `python config_wizard.py`
4. **Start dashboard**: `cd dashboard && python app.py`
5. **Integrate features**: Use examples above in your scrapers

## Support

- Check [PRODUCTION_READINESS.md](../PRODUCTION_READINESS.md) for framework details
- See [README.md](README.md) for quick start guide
- Review [IMPLEMENTATION_SUMMARY.md](../../IMPLEMENTATION_SUMMARY.md) for overview
