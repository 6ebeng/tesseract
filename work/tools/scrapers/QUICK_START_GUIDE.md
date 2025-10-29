# Production Scraper - Quick Start Guide

**⚡ Get started in 5 minutes!**

---

## 1️⃣ Installation (1 minute)

```bash
# Navigate to scrapers directory
cd work/tools/scrapers

# Install dependencies
pip install -r requirements.txt

# Optional: Install Redis for caching (60x speed boost)
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt-get install redis-server
# macOS: brew install redis
```

---

## 2️⃣ Validate Configuration (30 seconds)

```bash
# Validate your config file
python config_validator.py configs/websites/kurdsat.yaml
```

**Expected Output:**

```
✅ kurdsat.yaml is VALID
```

---

## 3️⃣ Run Your First Scrape (2 minutes)

```python
from production_scraper import ProductionScraper

# Initialize scraper
scraper = ProductionScraper('configs/websites/kurdsat.yaml')

# Scrape single website
result = scraper.scrape_website('kurdsat')

# View results
print(f"✅ Scraped {result.articles_scraped} articles")
print(f"📝 Extracted {result.sentences_extracted} sentences")
print(f"⏱️  Duration: {result.duration:.1f}s")
```

---

## 4️⃣ Command Line Usage

```bash
# Single website
python production_scraper.py --config configs/websites/kurdsat.yaml --website kurdsat

# All websites (parallel)
python production_scraper.py --config websites.yaml --all --parallel --workers 3
```

---

## 5️⃣ Enable Advanced Features (1 minute)

Add to your `config.yaml`:

```yaml
# Rate limiting (prevent IP blocking)
rate_limiting:
  enabled: true
  max_requests_per_minute: 30

# Redis caching (60x faster re-runs)
caching:
  enabled: true
  redis_host: localhost
  redis_port: 6379
  ttl_hours: 24

# Automatic retry on failures
retry:
  enabled: true
  max_attempts: 3
  delay_seconds: 2.0

# Proxy rotation (bypass blocking)
proxy:
  enabled: true
  file: proxies.txt
  strategy: round_robin
```

---

## 📊 Monitor Performance

```python
from scraper_monitor import ScraperMonitor

monitor = ScraperMonitor(log_dir='logs')

# Scrape
result = scraper.scrape_website('kurdsat')

# Log result
monitor.log_scrape(result)

# Generate report
print(monitor.generate_report())

# Export metrics
monitor.export_metrics('metrics.json')
```

---

## 🧪 Run Tests

```bash
# Run all tests
pytest test_scraper_framework.py -v

# Quick smoke test
pytest test_scraper_framework.py::TestConfigValidator -v
```

---

## 📖 Key Concepts

### Configuration Structure

```yaml
name: 'Website Name'
base_url: 'https://example.com'

selectors:
  article_list: 'div.article'
  article_link: 'a'
  article_title: 'h1'
  article_content: 'div.content'

categories:
  politics:
    url: 'https://example.com/politics'
  economy:
    url: 'https://example.com/economy'
```

### Selector Types

```yaml
# Simple CSS selector
article_title: "h1.title"

# Fallback chain
article_content:
  - "div.content-main"
  - "article.content"
  - "div.text"

# XPath selector
article_title:
  type: "xpath"
  value: "//h1[@class='title']"

# Multiple elements
tags:
  selector: "span.tag"
  multiple: true
  join: ", "
```

### URL Filtering

```yaml
# Option 1: Use template (simplest)
url_filtering:
  template: "rudaw"

# Option 2: Template + custom patterns (recommended)
url_filtering:
  template: "rudaw"
  whitelist:
    - "https://example.com/custom/*"

# Option 3: Manual (full control)
url_filtering:
  whitelist:
    - "https://example.com/sorani/*"
  blacklist:
    - "*cdn.example.com*"
```

---

## 🚨 Common Issues

### 1. Configuration Invalid

```bash
# Always validate first!
python config_validator.py config.yaml
```

### 2. Redis Not Running

```bash
# Start Redis
redis-server

# Or disable caching
caching:
  enabled: false
```

### 3. Empty Results

```python
# Enable debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

# Check selectors in browser console
document.querySelectorAll('div.article')
```

### 4. Rate Limited

```yaml
# Increase delay
rate_limiting:
  max_requests_per_minute: 20 # Lower = slower but safer
```

---

## 📚 Next Steps

1. ✅ **Read Full Documentation**: `USAGE_DOCUMENTATION.md`
2. ✅ **Review Examples**: `integration_example.py`
3. ✅ **Configure Your Website**: Use `config_wizard.py`
4. ✅ **Set Up Monitoring**: Review `scraper_monitor.py`
5. ✅ **Enable Advanced Features**: See `docs/ADVANCED_FEATURES.md`

---

## 🎯 Most Common Commands

```bash
# Validate config
python config_validator.py config.yaml

# Run scraper
python production_scraper.py --config config.yaml --website kurdsat

# Run tests
pytest test_scraper_framework.py -v

# Create new config
python config_wizard.py

# Monitor performance
tail -f logs/scraper.log
```

---

## 💡 Pro Tips

1. **Always validate** configuration before scraping
2. **Start with rate limiting** enabled (30 req/min)
3. **Use Redis caching** for development (60x faster)
4. **Monitor regularly** - check `logs/` directory
5. **Use templates** for URL filtering (less code)

---

## 🆘 Need Help?

- 📖 Full Documentation: `USAGE_DOCUMENTATION.md`
- 🚀 Quick Reference: `README.md`
- 📂 Examples: `integration_example.py`
- 📊 Logs: `logs/scraper.log`

---

**Ready to scrape!** 🚀

**Estimated Setup Time:** 5 minutes  
**Estimated First Scrape:** 2 minutes  
**Total:** ~7 minutes from zero to first results!
