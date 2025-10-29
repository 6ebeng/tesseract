# Production Scraper System - Complete Usage Documentation

**Version:** 2.0  
**Last Updated:** October 29, 2025  
**Status:** ✅ Production Ready

---

## 📖 Table of Contents

1. [System Overview](#system-overview)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [Configuration Guide](#configuration-guide)
5. [Advanced Features](#advanced-features)
6. [API Reference](#api-reference)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Examples](#examples)

---

## System Overview

### What is the Production Scraper?

The Production Scraper is a comprehensive, enterprise-ready web scraping framework designed for extracting Kurdish language content from news websites. It features:

- ✅ **Modular Architecture** - Separated concerns (pagination, extraction, URL filtering)
- ✅ **Configuration-Driven** - YAML-based configuration with validation
- ✅ **Advanced Features** - Rate limiting, caching, retry logic, proxy rotation
- ✅ **Production-Ready** - Error handling, monitoring, logging, testing
- ✅ **Multi-Language** - Kurdish (Sorani/Kurmanji), Arabic, Persian, English detection
- ✅ **Extensible** - Plugin system for custom scrapers

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Production Scraper                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Config     │  │   Monitor    │  │    Error     │  │
│  │  Validator   │  │   & Logging  │  │   Handler    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Advanced Features Layer                 │   │
│  ├──────────────┬──────────────┬────────────────────┤   │
│  │ Rate Limiter │ Redis Cache  │ Retry Logic        │   │
│  │ Proxy Rotate │ Deduplicator │ Language Detector  │   │
│  └──────────────┴──────────────┴────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Core Scraper Layer                   │   │
│  ├──────────────┬──────────────┬────────────────────┤   │
│  │ Base Scraper │ Pagination   │ URL Filtering      │   │
│  │ Extractors   │ Selectors    │ Wait Strategies    │   │
│  └──────────────┴──────────────┴────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │            Driver & Network Layer                 │   │
│  ├──────────────┬──────────────┬────────────────────┤   │
│  │ Selenium     │ FlareSolverr │ Stealth Mode       │   │
│  │ WebDriver    │ Integration  │ Anti-Detection     │   │
│  └──────────────┴──────────────┴────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Key Features

#### 1. **Configuration System**
- YAML-based configuration with schema validation
- Template system for reusable patterns
- Per-website and per-category customization
- Automatic validation on load

#### 2. **Advanced Features** (Phase 5)
- **Rate Limiting**: Prevent IP blocking (configurable requests/minute)
- **Redis Caching**: 60x faster re-runs with 24-hour cache
- **Retry Logic**: Automatic retry with exponential backoff
- **Proxy Rotation**: Round-robin/random with failure tracking

#### 3. **Monitoring & Observability**
- Structured logging (JSON + text formats)
- Real-time metrics (success rate, articles, sentences)
- Configurable alerts on thresholds
- Performance analytics by website/category

#### 4. **Error Handling**
- Automatic retry with exponential backoff
- WebDriver crash recovery
- Error classification (network, extraction, timeout)
- Detailed error reports

#### 5. **Security**
- Safe YAML loading (prevents code execution)
- XPath injection prevention
- Rate limiting to avoid bans
- User agent rotation
- Environment-based credential management

---

## Quick Start

### Installation

```bash
# 1. Navigate to scrapers directory
cd work/tools/scrapers

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# Optional: Install Redis for caching
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt-get install redis-server
# macOS: brew install redis
```

### Basic Usage

```python
from production_scraper import ProductionScraper

# 1. Initialize scraper with config
scraper = ProductionScraper('configs/websites/kurdsat.yaml')

# 2. Scrape single website
result = scraper.scrape_website('kurdsat')

# 3. View results
print(f"Articles: {result.articles_scraped}")
print(f"Sentences: {result.sentences_extracted}")
```

### Command Line

```bash
# Validate configuration
python config_validator.py configs/websites/kurdsat.yaml

# Scrape single website
python production_scraper.py --config configs/websites/kurdsat.yaml --website kurdsat

# Scrape all websites (parallel)
python production_scraper.py --config websites.yaml --all --parallel --workers 3

# Run tests
pytest test_scraper_framework.py -v
```

---

## Core Components

### 1. ProductionScraper

**Purpose:** Main entry point that orchestrates all scraping operations.

**Key Methods:**

```python
class ProductionScraper:
    def __init__(self, config_path: str)
    def scrape_website(self, website_name: str, category: str = None, max_articles: int = None) -> ScrapeResult
    def scrape_all_websites(self, parallel: bool = True, max_workers: int = 3) -> List[ScrapeResult]
```

**Features:**
- Configuration validation on initialization
- Automatic component initialization
- Incremental scraping (avoid re-scraping)
- Rate limiting integration
- Deduplication
- Language detection & filtering

**Example:**

```python
# Initialize
scraper = ProductionScraper('websites.yaml')

# Scrape single website
result = scraper.scrape_website('kurdsat')

# Scrape all (parallel)
results = scraper.scrape_all_websites(parallel=True, max_workers=3)

# View statistics
for result in results:
    print(f"{result.website}: {result.articles_scraped} articles, "
          f"{result.sentences_extracted} sentences in {result.duration:.1f}s")
```

### 2. ConfigValidator

**Purpose:** Validates YAML configuration against schema.

**Key Features:**
- Required field validation
- Type checking (strings, numbers, booleans, lists, dicts)
- URL validation
- Range validation (wait times, page counts)
- Selector format validation
- Warning for potential issues

**Example:**

```python
from config_validator import ConfigValidator

validator = ConfigValidator()

# Validate config
with open('websites.yaml') as f:
    config_text = f.read()

is_valid, errors, warnings = validator.validate_config_string(config_text)

if not is_valid:
    print("Errors:")
    for error in errors:
        print(f"  - {error}")
```

### 3. ScraperMonitor

**Purpose:** Tracks scraping performance and health metrics.

**Key Features:**
- Success/failure rates
- Article/sentence counts
- Performance metrics (duration)
- Error tracking
- Alert thresholds
- JSON export

**Example:**

```python
from scraper_monitor import ScraperMonitor, ScrapeResult

monitor = ScraperMonitor(log_dir='logs')

# Record result
result = ScrapeResult(
    website='kurdsat',
    category='politics',
    success=True,
    articles_scraped=15,
    sentences_extracted=450,
    duration_seconds=45.2
)

monitor.log_scrape(result)

# Generate report
report = monitor.generate_report()
print(report)

# Export metrics
monitor.export_metrics('metrics.json')
```

### 4. LanguageDetector

**Purpose:** Detect and filter content by language.

**Supported Languages:**
- Kurdish Sorani (ckb)
- Kurdish Kurmanji (kmr)
- Arabic (ar)
- Persian (fa)
- English (en)

**Example:**

```python
from advanced_features import LanguageDetector

detector = LanguageDetector()

# Detect language
text = "هەواڵی نوێ لە کوردستان"
lang = detector.detect(text)  # Returns 'ckb'

# Detect with confidence
lang, confidence = detector.detect_with_confidence(text)
print(f"{lang} ({confidence:.2f})")

# Filter articles
articles = [
    {'title': 'هەواڵی یەکەم', 'content': '...'},
    {'title': 'Breaking News', 'content': '...'}
]

kurdish_articles = detector.filter_by_language(articles, ['ckb'])
```

### 5. ArticleDeduplicator

**Purpose:** Detect and prevent duplicate articles using multiple strategies.

**Strategies:**
- URL exact match
- Title similarity (fuzzy matching)
- Content similarity

**Example:**

```python
from advanced_features import ArticleDeduplicator

dedup = ArticleDeduplicator('article_dedup.db')

# Check if article is duplicate
article = {
    'url': 'https://example.com/article1',
    'title': 'Breaking News',
    'content': 'Article content...'
}

is_dup, reason = dedup.is_duplicate(
    article,
    article['url'],
    article['title'],
    article['content']
)

if is_dup:
    print(f"Duplicate detected: {reason}")
else:
    print("Unique article")

# Get statistics
stats = dedup.get_stats()
print(f"Unique: {stats['unique_articles']}, "
      f"Duplicates: {stats['duplicates_detected']}")
```

### 6. RateLimiter

**Purpose:** Control request rate to prevent IP blocking.

**Example:**

```python
from advanced_features import RateLimiter

limiter = RateLimiter(max_requests_per_minute=30)

for url in urls:
    limiter.wait_if_needed()  # Enforces rate limit
    scrape(url)

# Get statistics
stats = limiter.get_stats()
print(f"Current rate: {stats['current_rate']}, "
      f"Remaining capacity: {stats['remaining_capacity']}")
```

### 7. RedisCache

**Purpose:** Cache scraped content for dramatic performance improvement.

**Features:**
- Page HTML caching
- Article list caching
- Configurable TTL (time-to-live)
- Automatic expiration
- Key namespacing

**Example:**

```python
from advanced_features import RedisCache

cache = RedisCache(
    host='localhost',
    port=6379,
    ttl_hours=24
)

# Cache page HTML
url = 'https://example.com/article'
html = driver.page_source
cache.set_page_html(url, html)

# Retrieve cached HTML
cached_html = cache.get_page_html(url)
if cached_html:
    print("Cache hit!")
else:
    print("Cache miss - scraping required")

# Invalidate cache
cache.invalidate('*')  # Clear all
```

### 8. RetryHandler

**Purpose:** Automatic retry on failures with configurable strategy.

**Example:**

```python
from advanced_features import RetryHandler

retry = RetryHandler(
    max_attempts=3,
    delay_seconds=2.0,
    retry_on_empty=True
)

# Execute with retry
result, success, attempts = retry.execute_with_retry(
    scrape_function,
    url,
    category='politics'
)

if success:
    print(f"Succeeded on attempt {attempts}")
else:
    print(f"Failed after {attempts} attempts")

# Get statistics
stats = retry.get_stats()
print(f"Success rate: {stats['success_rate']}")
```

### 9. ProxyRotator

**Purpose:** Rotate through proxies to bypass IP blocking.

**Strategies:**
- Round-robin (sequential)
- Random

**Example:**

```python
from advanced_features import ProxyRotator

# Create proxy file
# proxies.txt:
# http://proxy1.example.com:8080
# http://user:pass@proxy2.example.com:3128
# socks5://proxy3.example.com:1080

rotator = ProxyRotator('proxies.txt', rotation_strategy='round_robin')

# Get next proxy
proxy = rotator.get_next_proxy()

# For Selenium
selenium_config = rotator.get_selenium_proxy_config(proxy)

# For FlareSolverr
flare_config = rotator.get_flaresolverr_proxy_config(proxy)

# Mark success/failure
rotator.mark_success(proxy)
# or
rotator.mark_failure(proxy)

# Get statistics
stats = rotator.get_stats()
print(f"Total proxies: {stats['total_proxies']}")
print(f"Success rate: {stats['overall_success_rate']}")
```

---

## Configuration Guide

### Configuration File Structure

```yaml
# Website Configuration
name: "Website Name"
base_url: "https://example.com"
enabled: true  # Optional: disable without deleting config

# Selectors (CSS or XPath)
selectors:
  article_list: "div.article-card"
  article_link: "a.article-link"
  article_title: "h1.title"
  article_content:
    - "div.content"  # Fallback chain
    - "article.main"
    - "div.text"

# Categories
categories:
  politics:
    url: "https://example.com/politics"
    enabled: true
  
  economy:
    url: "https://example.com/economy"
    enabled: false  # Skip this category

# Advanced Features
rate_limiting:
  enabled: true
  max_requests_per_minute: 30

caching:
  enabled: true
  redis_host: "localhost"
  redis_port: 6379
  ttl_hours: 24

retry:
  enabled: true
  max_attempts: 3
  delay_seconds: 2.0

proxy:
  enabled: true
  file: "proxies.txt"
  strategy: "round_robin"  # or "random"

# URL Filtering
url_filtering:
  template: "rudaw"  # Use preset template
  # OR
  preset: "standard"  # Use preset patterns
  # OR
  whitelist:  # Manual patterns
    - "https://example.com/sorani/*"
  blacklist:
    - "*cdn.example.com*"

# Pagination
pagination:
  type: "pagination"  # or scroll, load_more, etc.
  pages: 5
  delay: 2.0

# Wait Strategies
wait:
  selector: "div.content"
  timeout: 10

collection_wait:
  selector: "div.article-list"
  timeout: 15

article_wait: 3.0  # Simple delay in seconds
```

### Configuration Options

#### Selector Types

**1. Simple CSS Selector (String)**

```yaml
selectors:
  article_title: "h1.title"
```

**2. Fallback Chain (List)**

```yaml
selectors:
  article_content:
    - "div.content-main"  # Try first
    - "article.content"   # Fallback
    - "div.article-body"  # Last resort
```

**3. XPath Selector (Dict)**

```yaml
selectors:
  article_title:
    type: "xpath"
    value: "//h1[@class='title']"
```

**4. Multiple Elements (Dict)**

```yaml
selectors:
  tags:
    selector: "span.tag"
    multiple: true
    join: ", "  # Join with comma
```

#### Pagination Types

**1. Standard Pagination (Page Parameter)**

```yaml
pagination:
  type: "pagination"
  pages: 5
  page_param: "page"  # URL: ?page=1, ?page=2, etc.
  delay: 2.0
```

**2. URL Template**

```yaml
pagination:
  type: "url_template"
  pages: 5
  # URL: /page/1/, /page/2/, etc.
```

**3. Infinite Scroll**

```yaml
pagination:
  type: "scroll"
  scrolls: 10
  delay: 1.5
```

**4. Load More Button**

```yaml
pagination:
  type: "load_more"
  clicks: 5
  load_more_button: "button.load-more"
  delay: 2.0
```

#### Wait Strategies

**1. Simple Delay**

```yaml
wait: 3.0  # Wait 3 seconds
```

**2. Wait for Element**

```yaml
wait:
  selector: "div.content"
  timeout: 10
```

**3. Wait for Element with Condition**

```yaml
wait:
  selector: "div.article-list"
  condition: "count"  # visible, clickable, etc.
  count: 5
  timeout: 15
  fallback_wait: 3.0  # If wait fails
```

#### URL Filtering Options

**Option 1: Template (Simplest)**

```yaml
url_filtering:
  template: "rudaw"  # Use preset template
```

**Option 2: Template + Custom Patterns (Recommended)**

```yaml
url_filtering:
  template: "rudaw"  # Base patterns from template
  whitelist:  # Add site-specific patterns
    - "https://www.rudaw.net/sorani/sports/*"
  blacklist:
    - "*tracker.example.com*"
```

**Option 3: Preset**

```yaml
url_filtering:
  preset: "standard"  # Use standard blocking patterns
```

**Option 4: Preset + Custom Patterns**

```yaml
url_filtering:
  preset: "standard"
  blacklist:
    - "*custom-tracker.com*"
```

**Option 5: Manual (Full Control)**

```yaml
url_filtering:
  whitelist:
    - "https://example.com/sorani/*"
    - "https://example.com/kurdish/*"
  blacklist:
    - "*cdn.example.com*"
    - "*ads.example.com*"
    - "*?utm_*"
```

---

## Advanced Features

### Feature 1: Rate Limiting

**Purpose:** Control request rate to prevent IP blocking.

**Configuration:**

```yaml
rate_limiting:
  enabled: true
  max_requests_per_minute: 30  # 30 requests per minute
```

**Benefits:**
- Prevents IP bans
- Respects server resources
- Configurable per website

**Usage:**

```python
# Automatic - no code changes needed
# Scraper automatically enforces rate limits
scraper = ProductionScraper('config.yaml')
scraper.scrape_website('kurdsat')  # Rate limited automatically
```

### Feature 2: Redis Caching

**Purpose:** Cache scraped content for 60x faster re-runs.

**Configuration:**

```yaml
caching:
  enabled: true
  redis_host: "localhost"
  redis_port: 6379
  redis_db: 0
  ttl_hours: 24  # Cache for 24 hours
```

**Benefits:**
- 60x faster re-runs (first run: 60 min, cached: <1 min)
- Reduces server load
- Automatic expiration

**Setup:**

```bash
# Install Redis
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt-get install redis-server
# macOS: brew install redis

# Start Redis
redis-server

# Install Python client
pip install redis
```

**Usage:**

```python
# Automatic - no code changes needed
# First run: scrapes and caches
result1 = scraper.scrape_website('kurdsat')  # ~60 seconds

# Second run (within 24h): uses cache
result2 = scraper.scrape_website('kurdsat')  # <1 second
```

### Feature 3: Retry Logic

**Purpose:** Automatic retry on failures with exponential backoff.

**Configuration:**

```yaml
retry:
  enabled: true
  max_attempts: 3  # Retry up to 3 times
  delay_seconds: 2.0  # Wait 2 seconds between retries
  retry_on_empty: true  # Retry if result is empty
```

**Benefits:**
- Handles transient network errors
- Exponential backoff prevents server overload
- Automatic crash recovery

**Usage:**

```python
# Automatic - no code changes needed
# Scraper automatically retries on failure
result = scraper.scrape_website('kurdsat')
# Attempt 1: Network error → Wait 2s → Retry
# Attempt 2: Timeout → Wait 2s → Retry
# Attempt 3: Success!
```

### Feature 4: Proxy Rotation

**Purpose:** Rotate through proxies to bypass IP blocking.

**Configuration:**

```yaml
proxy:
  enabled: true
  file: "proxies.txt"
  strategy: "round_robin"  # or "random"
```

**Setup:**

Create `proxies.txt`:

```
# HTTP proxy
http://proxy1.example.com:8080

# SOCKS5 proxy
socks5://proxy2.example.com:1080

# Authenticated proxy
http://user:pass@proxy3.example.com:3128
```

**Benefits:**
- Bypass IP blocking
- Distribute load across proxies
- Automatic failure tracking

**Usage:**

```python
# Automatic - no code changes needed
# Scraper automatically rotates proxies
result = scraper.scrape_website('kurdsat')
# Request 1: Uses proxy1
# Request 2: Uses proxy2
# Request 3: Uses proxy3
# Request 4: Uses proxy1 (round-robin)
```

---

## API Reference

### ProductionScraper

```python
class ProductionScraper:
    """Main scraper orchestrator"""
    
    def __init__(self, config_path: str):
        """
        Initialize scraper with configuration
        
        Args:
            config_path: Path to YAML configuration file
        
        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If config file not found
        """
    
    def scrape_website(
        self,
        website_name: str,
        category: str = None,
        max_articles: int = None
    ) -> ScrapeResult:
        """
        Scrape a single website
        
        Args:
            website_name: Website identifier from config
            category: Optional category filter
            max_articles: Maximum articles to scrape
        
        Returns:
            ScrapeResult with metrics
        """
    
    def scrape_all_websites(
        self,
        parallel: bool = True,
        max_workers: int = 3
    ) -> List[ScrapeResult]:
        """
        Scrape all configured websites
        
        Args:
            parallel: Whether to use parallel scraping
            max_workers: Number of parallel workers
        
        Returns:
            List of ScrapeResult objects
        """
```

### ScrapeResult

```python
@dataclass
class ScrapeResult:
    """Result of a scrape operation"""
    
    website: str              # Website name
    success: bool             # Whether scrape succeeded
    articles_scraped: int     # Number of articles scraped
    sentences_extracted: int  # Number of sentences extracted
    duration: float          # Duration in seconds
    error: Optional[str]     # Error message if failed
```

### ConfigValidator

```python
class ConfigValidator:
    """Validates YAML configuration"""
    
    def validate_config(
        self,
        config: Dict,
        is_single_website: bool = False
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate configuration dictionary
        
        Args:
            config: Configuration dictionary
            is_single_website: True if config is single website
        
        Returns:
            (is_valid, errors, warnings)
        """
```

### ScraperMonitor

```python
class ScraperMonitor:
    """Monitor scraping performance"""
    
    def __init__(
        self,
        log_dir: str = 'logs',
        alert_thresholds: Optional[Dict] = None
    ):
        """
        Initialize monitor
        
        Args:
            log_dir: Directory for log files
            alert_thresholds: Custom alert thresholds
        """
    
    def log_scrape(self, result: ScrapeResult):
        """
        Log scrape result
        
        Args:
            result: ScrapeResult object
        """
    
    def generate_report(self) -> str:
        """Generate performance report"""
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
```

---

## Best Practices

### 1. Configuration Management

**✅ DO:**
- Validate configuration before scraping
- Use templates for common patterns
- Keep website-specific patterns minimal
- Document custom selectors

**❌ DON'T:**
- Hardcode configuration in code
- Duplicate patterns across websites
- Skip validation

**Example:**

```python
# ✅ Good
from config_validator import validate_config_file

if not validate_config_file('websites.yaml'):
    print("Configuration invalid!")
    sys.exit(1)

config = safe_load_yaml('websites.yaml')

# ❌ Bad
config = yaml.load(open('websites.yaml'))  # Unsafe!
# No validation
```

### 2. Error Handling

**✅ DO:**
- Use error handler for all scraping operations
- Review error summaries regularly
- Configure appropriate retry attempts
- Log errors with context

**❌ DON'T:**
- Ignore errors silently
- Retry indefinitely
- Use bare except blocks

**Example:**

```python
# ✅ Good
from error_handler import ScraperErrorHandler

handler = ScraperErrorHandler(max_retries=3)

result = handler.safe_scrape(
    scrape_function,
    url,
    context={'website': 'kurdsat', 'category': 'politics'}
)

# ❌ Bad
try:
    result = scrape_function(url)
except:  # Bare except!
    pass  # Silent failure!
```

### 3. Rate Limiting

**✅ DO:**
- Enable rate limiting for all websites
- Start conservative (20-30 req/min)
- Monitor for 429 errors
- Adjust based on website capacity

**❌ DON'T:**
- Scrape without rate limiting
- Set unrealistic limits (>100 req/min)
- Ignore 429/blocking responses

**Example:**

```yaml
# ✅ Good
rate_limiting:
  enabled: true
  max_requests_per_minute: 30  # Conservative

# ❌ Bad
rate_limiting:
  enabled: false  # No rate limiting!
```

### 4. Caching Strategy

**✅ DO:**
- Enable caching for development/testing
- Use appropriate TTL (24h for news)
- Monitor cache hit rates
- Invalidate stale cache

**❌ DON'T:**
- Cache production data indefinitely
- Use same cache for dev and prod
- Forget to install/start Redis

**Example:**

```python
# ✅ Good
cache = RedisCache(ttl_hours=24)  # 24h expiration

# Check cache first
cached = cache.get_page_html(url)
if cached:
    html = cached
else:
    html = scrape_page(url)
    cache.set_page_html(url, html)

# ❌ Bad
cache = RedisCache(ttl_hours=8760)  # 1 year TTL!
```

### 5. Monitoring

**✅ DO:**
- Monitor all production scraping
- Set alert thresholds
- Export metrics regularly
- Review performance trends

**❌ DON'T:**
- Run production without monitoring
- Ignore alerts
- Skip metric collection

**Example:**

```python
# ✅ Good
monitor = ScraperMonitor(
    log_dir='logs',
    alert_thresholds={
        'failure_rate': 0.2,
        'min_sentences': 10
    }
)

monitor.log_scrape(result)
monitor.export_metrics('metrics.json')

# ❌ Bad
# No monitoring at all!
result = scrape()  # What if it fails?
```

### 6. Security

**✅ DO:**
- Always use `safe_load_yaml()`
- Sanitize XPath selectors
- Use environment variables for credentials
- Rotate user agents

**❌ DON'T:**
- Use `yaml.load()` (code execution risk!)
- Hardcode credentials
- Use same user agent always
- Trust user input directly

**Example:**

```python
# ✅ Good
from security_utils import safe_load_yaml, sanitize_xpath

config = safe_load_yaml('websites.yaml')  # Safe
xpath = sanitize_xpath(user_xpath)  # Sanitized

# ❌ Bad
config = yaml.load(open('websites.yaml'))  # UNSAFE!
xpath = user_xpath  # Injection risk!
```

---

## Troubleshooting

### Common Issues

#### 1. Configuration Validation Fails

**Error:**
```
❌ [kurdsat] Missing required field: 'base_url'
```

**Solution:**
```yaml
# Add missing field
kurdsat:
  name: "Kurdsat"
  base_url: "https://kurdsat.tv"  # Add this
  categories:
    politics:
      url: "https://kurdsat.tv/politics"
```

#### 2. Redis Connection Error

**Error:**
```
❌ Redis connection failed: ConnectionRefusedError
```

**Solution:**
```bash
# Start Redis server
redis-server

# Or disable caching
caching:
  enabled: false
```

#### 3. Rate Limit Exceeded

**Error:**
```
⏳ Rate limit reached (30 req/min). Waiting 5.2s...
```

**Solution:**
```yaml
# Increase limit (if website allows)
rate_limiting:
  max_requests_per_minute: 60  # Increase

# Or accept the wait (recommended)
```

#### 4. Proxy Connection Failed

**Error:**
```
⚠️ High failure rate for proxy proxy1.example.com:8080 (75.0%)
```

**Solution:**
```
# Check proxy file
cat proxies.txt

# Test proxy manually
curl --proxy http://proxy1.example.com:8080 https://google.com

# Remove failed proxy from list
# Or disable proxy rotation
proxy:
  enabled: false
```

#### 5. Empty Results

**Error:**
```
⚠️ LOW SENTENCE COUNT: kurdsat.politics got only 0 sentences
```

**Solution:**
```python
# Check selectors
# Enable debug mode
scraper.scrape_website('kurdsat', debug=True)

# Verify selectors in browser console
document.querySelectorAll('div.article-card')  # Should find elements
```

#### 6. Timeout Errors

**Error:**
```
TimeoutException: Element not found after 10s
```

**Solution:**
```yaml
# Increase timeout
wait:
  selector: "div.content"
  timeout: 30  # Increase from 10

# Or add fallback
wait:
  selector: "div.content"
  timeout: 10
  fallback_wait: 5.0  # Fallback delay
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run scraper
scraper = ProductionScraper('config.yaml')
result = scraper.scrape_website('kurdsat')

# Check logs
# logs/scraper.log - text format
# logs/scraper.json.log - JSON format
```

### Testing

```bash
# Run all tests
pytest test_scraper_framework.py -v

# Run specific test
pytest test_scraper_framework.py::TestConfigValidator -v

# Run with coverage
pytest test_scraper_framework.py --cov=scrapers --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## Examples

### Example 1: Basic Scraping

```python
from production_scraper import ProductionScraper

# Initialize
scraper = ProductionScraper('configs/websites/kurdsat.yaml')

# Scrape
result = scraper.scrape_website('kurdsat')

# Results
print(f"Success: {result.success}")
print(f"Articles: {result.articles_scraped}")
print(f"Sentences: {result.sentences_extracted}")
print(f"Duration: {result.duration:.1f}s")
```

### Example 2: Parallel Scraping

```python
from production_scraper import ProductionScraper

# Initialize with multiple websites
scraper = ProductionScraper('websites.yaml')

# Scrape all in parallel (3 workers)
results = scraper.scrape_all_websites(
    parallel=True,
    max_workers=3
)

# Summary
total_articles = sum(r.articles_scraped for r in results)
total_sentences = sum(r.sentences_extracted for r in results)

print(f"Total articles: {total_articles}")
print(f"Total sentences: {total_sentences}")
```

### Example 3: With All Features

```python
from production_scraper import ProductionScraper
from scraper_monitor import ScraperMonitor

# Initialize components
scraper = ProductionScraper('config.yaml')
monitor = ScraperMonitor(log_dir='logs')

# Scrape with all features
# - Rate limiting: 30 req/min
# - Redis caching: 24h TTL
# - Retry logic: 3 attempts
# - Proxy rotation: Round-robin
results = scraper.scrape_all_websites()

# Log results
for result in results:
    monitor.log_scrape(result)

# Generate report
report = monitor.generate_report()
print(report)

# Export metrics
monitor.export_metrics('metrics.json')
```

### Example 4: Custom Error Handling

```python
from production_scraper import ProductionScraper
from error_handler import ScraperErrorHandler

# Initialize
scraper = ProductionScraper('config.yaml')
error_handler = ScraperErrorHandler(max_retries=5)

# Custom scraping with error handling
def scrape_with_custom_logic():
    result = error_handler.safe_scrape(
        scraper.scrape_website,
        'kurdsat',
        context={'custom': 'data'}
    )
    return result

# Scrape
result = scrape_with_custom_logic()

# Check errors
if error_handler.has_critical_errors():
    print("Critical errors detected!")
    error_handler.print_summary()
```

### Example 5: Configuration Wizard

```python
from config_wizard import ConfigWizard

# Interactive configuration creation
wizard = ConfigWizard()

# Run wizard
wizard.run()

# Wizard will:
# 1. Ask for website name, URL
# 2. Auto-detect selectors
# 3. Test configuration
# 4. Save to file

# Output: configs/websites/mywebsite.yaml
```

### Example 6: Language Detection

```python
from advanced_features import LanguageDetector

detector = LanguageDetector()

articles = [
    {
        'title': 'هەواڵی یەکەم',
        'content': 'ناوەرۆکی کوردی...'
    },
    {
        'title': 'Breaking News',
        'content': 'English content...'
    },
    {
        'title': 'الأخبار',
        'content': 'محتوى عربي...'
    }
]

# Filter for Kurdish only
kurdish_articles = detector.filter_by_language(articles, ['ckb'])

print(f"Total: {len(articles)}, Kurdish: {len(kurdish_articles)}")
```

### Example 7: Deduplication

```python
from advanced_features import ArticleDeduplicator

dedup = ArticleDeduplicator('article_dedup.db')

articles = [
    {'url': 'https://example.com/1', 'title': 'News 1', 'content': '...'},
    {'url': 'https://example.com/1', 'title': 'News 1', 'content': '...'},  # Duplicate
    {'url': 'https://example.com/2', 'title': 'News 2', 'content': '...'}
]

unique_articles = []
for article in articles:
    is_dup, reason = dedup.is_duplicate(
        article,
        article['url'],
        article['title'],
        article['content']
    )
    
    if not is_dup:
        unique_articles.append(article)

print(f"Original: {len(articles)}, Unique: {len(unique_articles)}")
```

---

## Additional Resources

### Documentation Files

| Document | Purpose |
|----------|---------|
| `README.md` | Overview and quick reference |
| `USAGE_DOCUMENTATION.md` | This file - complete usage guide |
| `docs/PRODUCTION_READINESS.md` | Production deployment guide |
| `docs/SCRAPER_QUICK_START.md` | Quick start tutorial |
| `docs/URL_FILTERING_EASY_GUIDE.md` | URL filtering guide |
| `docs/ADVANCED_FEATURES.md` | Advanced features deep dive |

### Code Examples

- `production_scraper.py` - Main scraper implementation
- `integration_example.py` - Complete integration example
- `test_scraper_framework.py` - Test suite with examples

### Tools

- `config_validator.py` - Configuration validation CLI
- `config_wizard.py` - Interactive configuration creation
- `analyze_url_waste.py` - URL filtering analysis

---

## Support

For questions or issues:

1. Check this documentation
2. Review `README.md` for quick reference
3. Check `docs/` directory for detailed guides
4. Review code examples in repository
5. Check logs in `logs/` directory

---

**Happy Scraping!** 🚀
