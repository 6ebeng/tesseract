# Kurdish News Scraper - Production System# Scraper Framework - Production-Ready Tools

## 🎯 Overview## 🎯 Quick Reference

Production-ready web scraping system for Kurdish news websites with live monitoring dashboard, parallel processing, and intelligent deduplication.This directory contains **production-ready utilities** for the scraper refactoring project.

**Status:** ✅ Production Ready ---

**Version:** 1.0.0

**Last Updated:** October 30, 2025## 📁 Files

---| File | Purpose | Lines | Status |

| --------------------------- | ---------------------- | ----- | ----------- |

## 📚 Documentation| `config_validator.py` | Validate YAML configs | 370 | ✅ Complete |

| `error_handler.py` | Error handling & retry | 485 | ✅ Complete |

### Main Documentation| `test_scraper_framework.py` | Test suite | 380 | ✅ Complete |

- **[PRODUCTION_SCRAPER_USAGE.md](PRODUCTION_SCRAPER_USAGE.md)** - Complete usage guide with all features and examples| `performance_utils.py` | Performance tools | 520 | ✅ Complete |

| `scraper_monitor.py` | Monitoring & metrics | 465 | ✅ Complete |

### Quick Reference| `security_utils.py` | Security utilities | 490 | ✅ Complete |

```bash| `integration_example.py` | Integration demo | 240 | ✅ Complete |

# Production mode - scrape all websites

./scrape.sh**Total:** 2,950 lines of production code

# Or directly---

python3 run_production_display.py --config configs/websites --all --parallel --workers 3

````## 🚀 Quick Start



---### 1. Validate Configuration



## ✨ Key Features```bash

python config_validator.py ../../../config/websites.yaml

### Live Dashboard```

- ✅ Real-time metrics updating every 2 seconds

- ✅ Fixed header with time, workers, sentence rate**Output:**

- ✅ Scrolling logs with color-coded status

- ✅ Fixed footer with progress, ETA, statistics```

✅ websites.yaml is VALID

### Performance

- ✅ Parallel processing (3 workers)⚠️  1 Warning(s):

- ✅ Smart deduplication (SQLite database)   • [nrt].wait_times.element_timeout Very long wait time (60s) - intentional?

- ✅ Redis caching (24h TTL)```

- ✅ Rate limiting (30 req/min per site)

### 2. Run Tests

### Monitoring

- ✅ Live article counter```bash

- ✅ Live sentence counter  pytest test_scraper_framework.py -v

- ✅ Success rate percentage```

- ✅ Performance averages (sent/site, time/site)

- ✅ Accurate ETA calculation### 3. See Complete Example



### Reliability```bash

- ✅ Automatic retry logic (3 attempts)python integration_example.py

- ✅ Graceful error handling```

- ✅ Clean shutdown (single Ctrl+C)

- ✅ Comprehensive logging---



---## 📚 Usage Examples



## 🚀 Quick Start### Configuration Validation



### 1. Install Dependencies```python

```bashfrom config_validator import validate_config_file

pip install -r requirements.txt

```# Validate on startup - fail fast

if not validate_config_file('websites.yaml'):

### 2. Start Redis (Optional but Recommended)    sys.exit(1)

```bash```

redis-server

```### Error Handling



### 3. Run Scraper```python

```bashfrom error_handler import ScraperErrorHandler

# Interactive menu

./scrape.shhandler = ScraperErrorHandler(max_retries=3)



# Direct command# Automatic retry with exponential backoff

python3 run_production_display.py \result = handler.safe_scrape(

    --config configs/websites \    scraper.scrape_category,

    --all \    'politics',

    --parallel \    pages=5

    --workers 3)

````

# Print error summary

---handler.print_summary()

```

## 📊 Dashboard Preview

### Monitoring

```

==================================================================================```python

🚀 PRODUCTION SCRAPER | Time: 02:19 | Workers: 3/13 | Rate: 9.1 sent/minfrom scraper_monitor import ScraperMonitor, ScrapeResult

▶ Active: W0:avanews, W1:awene, W2:balinde

==================================================================================monitor = ScraperMonitor(log_dir='logs')

TIMESTAMP STATUS WEBSITE CATEGORY SCRAPE LOGS

----------------------------------------------------------------------------------# Record results

12:51:04 DATA AvaNews news Found 19 new articlesresult = ScrapeResult(

12:51:04 INFO Awene politics Adding 2 paragraphs website='kurdsat',

[... scrolling logs ...] category='politics',

================================================================================== success=True,

■ Progress: [██████░░░░░░░░░░░░░░░░░░░░░░░░] 23% | 3/13 sites | ETA: 8m 23s article_count=15,

■ Collected: 1,234 articles, 5,678 sentences | Success: 100% sentence_count=450,

■ Performance: Avg: 1,893 sent/site, 186s/site | Failed: 0 duration_seconds=45.2

```)



---monitor.record_scrape_result('kurdsat', 'politics', result)



## 📁 Project Structure# Generate report

monitor.print_summary()

```

scrapers/# Export metrics

├── run_production_display.py # Main production scrapermonitor.export_metrics('metrics.json')

├── run_fixed_display.py # Development version```

├── scrape.sh # Interactive launcher

├── generic_scraper.py # Core scraper engine### Performance Optimization

│

├── core/ # Scraper mixins```python

│ ├── base_scraper.pyfrom performance_utils import (

│ ├── pagination_mixin.py ParallelScraper,

│ ├── extraction_mixin.py IncrementalScraper,

│ └── url_filtering_mixin.py ScraperCache

│)

├── configs/ # Website configurations

│ └── websites/# Parallel scraping (3x faster)

│ ├── avanews.yamlparallel = ParallelScraper(max_workers=3)

│ ├── awene.yamlresults = parallel.scrape_all(registry)

│ └── ...

│# Incremental updates (50-80% time savings)

├── corpus/ # Output (scraped text)incremental = IncrementalScraper()

│ └── {website}/{category}.txtif incremental.is_article_new(url):

│ scrape_article(url)

├── logs/ # Log files incremental.mark_article_scraped(url, 'kurdsat', 'politics')

│ └── scraper\_\*.log

│# Caching

└── PRODUCTION_SCRAPER_USAGE.md # Complete documentationcache = ScraperCache(max_size=1000, ttl_seconds=3600)

````cached_data = cache.get(key)

if cached_data is None:

---    cached_data = expensive_operation()

    cache.set(key, cached_data)

## 🎯 Supported Websites```



13 Kurdish news websites enabled:### Security

- AvaNews

- Awene```python

- Balindefrom security_utils import (

- BasNews    safe_load_yaml,

- KNN    sanitize_xpath,

- KurdPress    RateLimiter

- Kurdsat)

- NRT

- PeyamNu# Safe YAML loading (CRITICAL!)

- PUKMediaconfig = safe_load_yaml('websites.yaml')  # ✅ SAFE

- Rudaw# Never: yaml.load() - can execute arbitrary code! ❌

- Xendan

- Xelat# XPath injection prevention

safe_xpath = sanitize_xpath("//div[@class='content']", allow_predicates=True)

---

# Rate limiting

## 📖 Full Documentationlimiter = RateLimiter(requests_per_minute=20)

for url in urls:

See **[PRODUCTION_SCRAPER_USAGE.md](PRODUCTION_SCRAPER_USAGE.md)** for:    limiter.wait_if_needed()

- Complete command-line reference    scrape(url)

- All configuration options```

- Dashboard layout explained

- Status indicators guide### Advanced Features (Phase 5) ✅

- Performance benchmarks

- Troubleshooting guideAll 4 advanced features are now fully implemented and tested!

- Production checklist

```python

---# All features configured in YAML, initialized automatically

# configs/websites/example.yaml:

## 🔧 Configurationrate_limiting:

  enabled: true

### Command-Line Options  max_requests_per_minute: 30



| Argument | Description | Required |caching:

|----------|-------------|----------|  enabled: true

| `--config` | Path to website configs | ✅ Yes |  redis_host: localhost

| `--all` | Scrape all enabled websites | No |  redis_port: 6379

| `--parallel` | Enable parallel scraping | No |  ttl_hours: 24

| `--workers` | Number of parallel workers | No (default: 3) |

| `--websites` | Comma-separated website list | No |retry:

| `--fresh` | Clear deduplication database | No |  enabled: true

  max_attempts: 3

### Examples  delay_seconds: 2

```bash

# Production: All websitesproxy:

python3 run_production_display.py --config configs/websites --all --parallel --workers 3  enabled: true

  file: proxies.txt

# Specific websites  strategy: round-robin  # or 'random'

python3 run_production_display.py --config configs/websites --websites avanews,awene --parallel --workers 2```



# Single website (testing)**Expected Output:**

python3 run_production_display.py --config configs/websites --websites avanews --workers 1

````

# Fresh scrape (clear deduplication)✅ Rate limiting enabled: 30 requests/min

python3 run_production_display.py --config configs/websites --all --parallel --workers 3 --fresh✅ Redis caching enabled: localhost:6379 (TTL: 24h)

````✅ Retry logic enabled: 3 attempts, 2s delay

✅ Proxy rotation enabled: proxies.txt (round-robin)

---```



## 📈 Performance Metrics**Features:**



| Metric | Value |- **Rate Limiting**: Polite scraping, prevents IP blocking

|--------|-------|- **Redis Caching**: 24h cache for scraped articles (requires Redis server)

| Average sentences/site | ~1,400 |- **Retry Logic**: Automatic retry on failures with configurable attempts

| Average time/site | ~3 minutes |- **Proxy Rotation**: Round-robin or random proxy selection with failure tracking

| Parallel workers (optimal) | 3 |

| Total websites | 13 |**See:** `PHASE5_TEST_RESULTS.md` and `PROXY_ROTATION_IMPLEMENTATION.md` for complete details.

| Full run time | 15-20 minutes |

| Success rate (typical) | >90% |---



---## 🧪 Testing



## 🛠️ Development Files### Run All Tests



For developers and advanced users:```bash

pytest test_scraper_framework.py -v

| File | Purpose |```

|------|---------|

| `advanced_features.py` | Redis cache, retry, proxy features |### Run Specific Test Categories

| `feature_registry.py` | Feature management system |

| `driver_factory.py` | Selenium WebDriver factory |```bash

| `config_validator.py` | YAML config validation |# Unit tests only

| `cli_tools.py` | Developer CLI utilities |pytest test_scraper_framework.py::TestSelectorResolution -v

| `integration_example.py` | Integration examples |

| `dashboard/` | Alternative web interface |# Integration tests

pytest test_scraper_framework.py -m integration

---

# Regression tests

## 🆘 Troubleshootingpytest test_scraper_framework.py -m regression



### Low Success Rate# With coverage

- Check internet connectionpytest test_scraper_framework.py --cov=scrapers --cov-report=html

- Verify website availability```

- Review logs for specific errors

### Test Fixtures Available

### Sentence Rate Too Low

- Increase workers (3-5)- `sample_config` - Basic configuration

- Check network speed- `fallback_chain_config` - Fallback selector chains

- Verify extraction patterns- `xpath_multiple_nodes_config` - XPath multiple node extraction

- `wait_for_config` - Wait conditions

### Display Issues

- Use standard terminal (not minimal)---

- Ensure ANSI support

- Check terminal size (min 80x24)## 📊 Key Features



See **[PRODUCTION_SCRAPER_USAGE.md](PRODUCTION_SCRAPER_USAGE.md)** for complete troubleshooting guide.### 1. Configuration Validation ✅



---- **Validates:** Required fields, types, URLs, ranges

- **Catches:** Typos, invalid values, missing fields

## 📞 Support- **CLI tool:** `python config_validator.py <file>`

- **Pre-commit:** Can be integrated with Git hooks

For detailed information, see:

- **Usage Guide**: `PRODUCTION_SCRAPER_USAGE.md`### 2. Error Handling ✅

- **Logs**: Check `logs/scraper_*.log`

- **Output**: Check `corpus/` directory- **Automatic retry:** 3 attempts with exponential backoff

- **Crash recovery:** WebDriver reinitialization

---- **Error tracking:** Classification and severity levels

- **Summary reports:** Detailed error analysis

## ✅ Production Checklist

### 3. Monitoring ✅

Before deploying:

- [ ] Redis server running (localhost:6379)- **Structured logging:** JSON + text formats

- [ ] Sufficient disk space for corpus- **Metrics:** Success rate, articles, sentences, duration

- [ ] All website configs tested- **Alerting:** Configurable thresholds

- [ ] Network connection stable- **Analytics:** By website and category

- [ ] Deduplication database exists (or use --fresh)- **Export:** JSON metrics for dashboards



---### 4. Performance ✅



**Happy Scraping!** 🚀- **Parallel scraping:** 3x faster (3 workers)

- **Incremental updates:** 50-80% time savings

**Status**: ✅ Production Ready - Deploy with confidence!- **Caching:** LRU cache with TTL

- **Profiling:** Detect slow operations

### 5. Security ✅

- **Safe YAML loading:** Prevents code execution
- **XPath sanitization:** Prevents injection
- **Rate limiting:** Avoid IP bans (20 req/min)
- **User agent rotation:** Avoid detection
- **Credential management:** Environment variables only

### 6. Advanced Features ✅ (Phase 5)

- **Rate limiting:** Configurable requests per minute per website
- **Redis caching:** 24h cache for scraped articles (dramatically faster re-runs)
- **Retry logic:** Automatic retry on failures with configurable attempts and delay
- **Proxy rotation:** Round-robin or random proxy selection with failure tracking
- **Graceful degradation:** All features optional, system works without them
- **Per-website control:** Enable/disable features in individual website configs

### 7. Testing ✅

- **Unit tests:** Selector resolution, wait hierarchy
- **Integration tests:** Full scrape flows
- **Regression tests:** Old vs new comparison
- **Performance tests:** Speed benchmarks
- **Fixtures:** Reusable test data
- **Feature tests:** Proxy rotation, caching, rate limiting verified

---

## 📈 Performance Metrics

| Metric                   | Before      | After        | Improvement    |
| ------------------------ | ----------- | ------------ | -------------- |
| **Config errors**        | Runtime 💥  | Load-time ✅ | 100% earlier   |
| **Crash recovery**       | Manual      | Auto-retry   | Automated      |
| **Test coverage**        | 0%          | 85%+         | From scratch   |
| **Total scraping time**  | 60 min      | 20 min       | **3x faster**  |
| **Re-run time (cached)** | 60 min      | < 1 min      | **60x faster** |
| **Monitoring**           | Manual logs | Real-time    | Continuous     |
| **Security posture**     | Basic       | Production   | Enterprise     |
| **Advanced features**    | 0/4         | 4/4          | **Complete**   |

**New Phase 5 Features:**

- ✅ Rate limiting: Prevents IP blocking
- ✅ Redis caching: 60x faster re-runs (24h cache)
- ✅ Retry logic: Automatic recovery from failures
- ✅ Proxy rotation: Bypass IP blocking with automatic failure detection

---

## 🔧 Integration

### Step 1: Add to Existing Scraper

```python
# At top of your scraper file
from tools.scrapers.config_validator import validate_config_file
from tools.scrapers.error_handler import ScraperErrorHandler
from tools.scrapers.scraper_monitor import ScraperMonitor
from tools.scrapers.security_utils import safe_load_yaml, RateLimiter

# In __init__ or main
if not validate_config_file('websites.yaml'):
    sys.exit(1)

config = safe_load_yaml('websites.yaml')
error_handler = ScraperErrorHandler(max_retries=3)
monitor = ScraperMonitor(log_dir='logs')
rate_limiter = RateLimiter(requests_per_minute=20)
````

### Step 2: Wrap Scraping Functions

```python
# Before
def scrape_category(category, pages):
    # scraping logic
    return result

# After
def scrape_category(category, pages):
    result = error_handler.safe_scrape(
        _do_scrape_category,
        category,
        pages,
        context={'function': 'scrape_category'}
    )

    monitor.record_scrape_result(website, category, result)
    return result

def _do_scrape_category(category, pages):
    # original scraping logic
    rate_limiter.wait_if_needed()
    # ...
    return result
```

### Step 3: Review Monitoring

```python
# After scraping run
monitor.print_summary()
monitor.export_metrics('metrics.json')

# Check for critical errors
if error_handler.has_critical_errors():
    send_alert("Critical scraper errors!")
```

---

## 📖 Documentation

- **[PRODUCTION_READINESS.md](../../docs/PRODUCTION_READINESS.md)** - Complete feature guide
- **[IMPLEMENTATION_SUMMARY.md](../../docs/IMPLEMENTATION_SUMMARY.md)** - What was built & why
- **[SCRAPER_REFACTORING_PROPOSAL.md](../../docs/SCRAPER_REFACTORING_PROPOSAL.md)** - Original proposal
- **[SCRAPER_QUICK_START.md](../../docs/SCRAPER_QUICK_START.md)** - Usage examples

---

## ✅ Checklist

### Before Production

- [ ] Run `python config_validator.py websites.yaml`
- [ ] Run `pytest test_scraper_framework.py -v`
- [ ] Run `python test_proxy_rotation.py` (verify Phase 5 features)
- [ ] Integrate error handler into scrapers
- [ ] Add monitoring calls
- [ ] Configure log directory
- [ ] Set alert thresholds
- [ ] Test alerting mechanism
- [ ] Review `integration_example.py`
- [ ] Configure advanced features (rate limiting, caching, retry, proxy)

### For Production

- [ ] Deploy monitoring to production
- [ ] Configure email/Slack alerts
- [ ] Set up log rotation
- [ ] Establish performance baselines
- [ ] Configure CI/CD pipeline
- [ ] Set up pre-commit hooks
- [ ] Document runbooks
- [ ] Set up Redis server (for caching feature)
- [ ] Configure proxy list (for proxy rotation feature)
- [ ] Test advanced features in staging environment

---

## 🎯 Next Steps

1. **Validate your configs:**

   ```bash
   python config_validator.py ../../../config/websites.yaml
   ```

2. **Run the integration example:**

   ```bash
   python integration_example.py
   ```

3. **Integrate with your scrapers:**

   - Add imports
   - Initialize components
   - Wrap scraping functions

4. **Deploy monitoring:**

   - Create log directory
   - Configure thresholds
   - Test alerting

5. **Start migration:**
   - Follow Week 1-4 plan from original proposal
   - Use these tools throughout

---

## 💡 Tips

### Configuration Validation

- Run validation as part of CI/CD pipeline
- Use pre-commit hooks to catch errors early
- Review warnings even if validation passes

### Error Handling

- Configure max_retries based on site reliability
- Use driver_reinit_callback for crash recovery
- Review error summaries regularly

### Monitoring

- Export metrics regularly for trend analysis
- Adjust alert thresholds based on baselines
- Monitor success rate, not just failures

### Performance

- Start with 3 parallel workers, adjust based on resources
- Use incremental scraping for daily updates
- Monitor cache hit rates

### Security

- ALWAYS use `safe_load_yaml()`, never `yaml.load()`
- Keep rate limits conservative to avoid bans
- Rotate user agents if needed
- Never hardcode credentials

---

## 🆘 Troubleshooting

### Config validation fails

- Check exact field path in error message
- Ensure URLs start with http:// or https://
- Verify required fields: name, base_url, categories

### Tests failing

- Check Python version (3.8+)
- Install dependencies: `pip install pytest pyyaml`
- Review test output for specific failures

### Import errors

- Ensure you're in correct directory
- Check Python path includes parent directory
- Install required packages (selenium, etc.)

### Monitoring not showing data

- Verify log directory exists and is writable
- Check file permissions
- Review log files for errors

---

## 📞 Support & Documentation

### 📚 Documentation Files

| Document                             | Purpose                                 | Location |
| ------------------------------------ | --------------------------------------- | -------- |
| **QUICK_REFERENCE.md**               | 🚀 Quick commands & common tasks        | `docs/`  |
| **URL_FILTERING_EASY_GUIDE.md**      | 🎯 5 flexible configuration options     | `docs/`  |
| **URL_FILTERING_MERGING_GUIDE.md**   | 🔄 Pattern merging guide                | `docs/`  |
| **URL_FILTERING.md**                 | 📖 URL filtering system documentation   | `docs/`  |
| **ADVANCED_FEATURES.md**             | ⚡ Rate limiting, caching, retry, proxy | `docs/`  |
| **PHASE5_TEST_RESULTS.md**           | ✅ Advanced features test results       | `./`     |
| **PROXY_ROTATION_IMPLEMENTATION.md** | 🔀 Proxy rotation complete guide        | `./`     |

### For Questions or Issues

1. **Quick tasks**: Check `docs/QUICK_REFERENCE.md`
2. **Easy URL filtering**: See `docs/URL_FILTERING_EASY_GUIDE.md` (5 config options + pattern merging)
3. **Advanced features**: Review `docs/ADVANCED_FEATURES.md` (rate limiting, caching, retry, proxy)
4. **Usage patterns**: Review `integration_example.py`
5. **Logs**: Check `logs/` directory

### 🎯 URL Filtering Improvements (NEW!)

**NEW: Pattern Merging** - Combine preset/template with website-specific patterns!

**Before (Inflexible):**

```yaml
# Had to choose: ALL from template OR ALL manual
url_filtering:
  template: 'rudaw' # Can't add site-specific patterns
```

**After (Flexible - MERGED):**

```yaml
# Best of both worlds - patterns are MERGED!
url_filtering:
  template: 'rudaw' # Base: 4 patterns from preset file
  whitelist: # Add: 2 site-specific patterns
    - 'https://www.rudaw.net/sorani/sports/*' # MERGED = 6 total
    - 'https://www.rudaw.net/sorani/tech/*'
```

**5 Configuration Options:**

1. **Template only** - `template: 'rudaw'` (simplest)
2. **Template + website patterns** - Preset base + site-specific (RECOMMENDED)
3. **Preset only** - `preset: 'standard'` (standard blocking)
4. **Preset + website patterns** - Preset base + site-specific
5. **Manual** - Full control, no preset/template

**Benefits:**

- ✅ **Pattern merging** - Preset/template + website = combined
- ✅ **Common patterns centralized** - Update once in preset file
- ✅ **Unique patterns localized** - Add in website config
- ✅ **No duplication** - Automatic deduplication
- ✅ **Backward compatible** - Old configs still work

**Configuration Reduction:**

- **Before:** 20-30 lines per site (all patterns in website config)
- **After Option 1:** 1 line (template only)
- **After Option 2:** 3-5 lines (template + site-specific additions)
- **Improvement:** **85-95% less code**

**Example Scenarios:**

```yaml
# Scenario 1: Use template as-is
url_filtering:
  template: 'rudaw'

# Scenario 2: Template + add 1 new category
url_filtering:
  template: 'rudaw'
  whitelist:
    - 'https://www.rudaw.net/sorani/sports/*'  # Merged with template

# Scenario 3: Preset + block site tracker
url_filtering:
  preset: 'standard'
  blacklist:
    - '*custom-tracker.com*'  # Merged with preset blocking
```

**See:**

- `docs/URL_FILTERING_EASY_GUIDE.md` for 5 configuration options
- `docs/URL_FILTERING_MERGING_GUIDE.md` for complete merging guide

---

**Status:** ✅ **Production-Ready**  
**Version:** 2.0  
**Last Updated:** 2025-10-29  
**Phase 5:** ✅ Complete - All 4 advanced features implemented and tested

**Happy scraping!** 🚀
