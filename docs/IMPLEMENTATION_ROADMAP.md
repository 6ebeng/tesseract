# Implementation Roadmap

## Step-by-Step Migration to Refactored Architecture

---

## 🎯 Overview

**Goal:** Migrate from hard-coded scrapers to configuration-driven architecture
**Timeline:** 4 weeks (part-time)
**Risk:** Low (parallel migration, old system remains as fallback)

---

## 📅 Phase 1: Foundation (Week 1)

### Day 1-2: Setup New Structure

**Create directory structure:**

```
work/tools/scrapers/
├── base/
│   ├── __init__.py
│   ├── scraper_base.py          # Enhanced base classes
│   └── quality_control.py       # QC utilities
├── config/
│   ├── websites.yaml            # Main configuration
│   ├── websites.dev.yaml        # Development config
│   └── websites.prod.yaml       # Production config
├── implementations/
│   ├── __init__.py
│   └── generic_scraper.py       # Generic implementation
├── plugins/
│   ├── __init__.py
│   └── special_handling.py      # Custom logic plugins
├── utils/
│   ├── __init__.py
│   └── helpers.py               # Utility functions
└── registry.py                  # Auto-discovery system
```

**Tasks:**

- [x] Create directory structure
- [ ] Implement `ScraperBase` class
- [ ] Implement `ConfigurableScraper` class
- [ ] Implement `GenericScraper` class
- [ ] Create basic `websites.yaml` template
- [ ] Implement `ScraperRegistry` class

**Deliverable:** Working foundation with generic scraper

---

### Day 3-4: Migrate 2 Simple Scrapers

**Choose:** Khak + GovKrd (simplest scrapers)

**Steps for each:**

1. Analyze current scraper code
2. Extract URLs and selectors
3. Create YAML configuration
4. Test with generic scraper
5. Compare results with old scraper
6. Document any issues

**Example for GovKrd:**

```yaml
govkrd:
  name: 'GovKrd'
  base_url: 'https://gov.krd'
  scraper_class: 'GenericScraper'
  enabled: true

  categories:
    political:
      enabled: true
      type: 'pagination'
      url: 'https://gov.krd/kurdish/articles'
      pages: 3

  selectors:
    article_list: 'div.article'
    article_link: 'a.title-link'
    article_title: 'h1'
    article_content: 'div.content'
    article_paragraphs: 'div.content p'
```

**Success criteria:**

- Generic scraper gets ≥90% of sentences as old scraper
- No crashes or errors
- Code is simpler (30 lines YAML vs 200 lines Python)

---

### Day 5: Create Test Infrastructure

**Implement:**

```python
# test_scrapers_v2.py
"""
Enhanced test suite with comparison mode
"""

def test_with_comparison(website_name):
    """Test new scraper and compare with old one"""

    # Run old scraper
    old_scraper = OldScraperClass()
    old_results = old_scraper.scrape_political(pages=1)
    old_count = len(old_results)

    # Run new scraper
    new_scraper = registry.get_scraper(website_name)
    new_result = new_scraper.scrape_political(pages=1)
    new_count = new_result.sentence_count

    # Compare
    difference = abs(old_count - new_count)
    percentage = (difference / old_count * 100) if old_count > 0 else 0

    print(f"Old: {old_count} sentences")
    print(f"New: {new_count} sentences")
    print(f"Diff: {difference} ({percentage:.1f}%)")

    # Pass if within 10% of old scraper
    return percentage <= 10
```

**Tasks:**

- [ ] Implement comparison test
- [ ] Create test report generator
- [ ] Add CI/CD integration
- [ ] Document test process

---

## 📅 Phase 2: Core Migration (Week 2)

### Day 6-8: Migrate Medium Complexity Scrapers

**Choose:** Sekokurd, Awene, Xendan, NRT (4 scrapers)

**Process per scraper:**

1. Create YAML config (15 min)
2. Test with generic scraper (5 min)
3. Run comparison test (5 min)
4. Fix any issues (30 min)
5. Document edge cases (15 min)

**Expected issues:**

- Selector mismatches → Update YAML
- Pagination differences → Adjust config
- Special characters → Add to QC rules

**Daily targets:**

- Day 6: Sekokurd + Awene
- Day 7: Xendan + NRT
- Day 8: Testing + bug fixes

---

### Day 9-10: Migrate Complex Scrapers (Batch 1)

**Choose:** Kurdsat, Balinde (scroll/special pagination)

**Kurdsat - Scroll-based:**

```yaml
kurdsat:
  name: 'Kurdsat'
  base_url: 'https://kurdsat.tv'
  scraper_class: 'GenericScraper'
  enabled: true

  categories:
    political:
      enabled: true
      type: 'scroll' # Different type!
      url: 'https://kurdsat.tv/cat/politics'
      clicks: 3 # Number of scrolls

  selectors:
    article_list: 'div.post-card'
    article_link: 'a.post-link'
```

**Balinde - Poetry site:**

```yaml
balinde:
  name: 'Balinde'
  base_url: 'https://balinde.com'
  scraper_class: 'GenericScraper'
  enabled: true

  quality_control: # Custom QC!
    min_words: 5
    max_words: 40
    min_kurdish_ratio: 0.6
```

**Tasks:**

- [ ] Implement scroll pagination in generic scraper
- [ ] Test with Kurdsat
- [ ] Migrate Balinde with custom QC
- [ ] Verify poetry extraction quality

---

## 📅 Phase 3: Complex Cases (Week 3)

### Day 11-12: Migrate Largest Scrapers

**Choose:** Rudaw, Kurdistan24 (many categories)

**Strategy:**

1. Start with political category
2. Add specialized categories one by one
3. Test each addition
4. Use category groups if needed

**Example - Rudaw with 5+ categories:**

```yaml
rudaw:
  name: 'Rudaw'
  base_url: 'https://rudaw.net'
  scraper_class: 'GenericScraper'
  enabled: true

  categories:
    political:
      enabled: true
      url: 'https://rudaw.net/sorani/kurdistan'
      pages: 5

    specialized:
      economy:
        enabled: true
        name: 'Economy'
        url: 'https://rudaw.net/sorani/business'
        pages: 3

      health:
        enabled: true
        name: 'Health'
        url: 'https://rudaw.net/sorani/health'
        pages: 3

      # ... 3 more categories ...
```

**Tasks:**

- [ ] Migrate Rudaw (5 categories)
- [ ] Migrate Kurdistan24 (8 categories)
- [ ] Verify all categories working
- [ ] Performance testing

---

### Day 13-14: Handle Special Cases

**Choose:** Sharpress, LvinPress (driver issues, special handling)

**Sharpress - Driver restart needed:**

```python
# Create custom scraper if generic doesn't work
# scrapers/implementations/sharpress_scraper.py

class SharpressScraper(ConfigurableScraper):
    """Custom scraper with driver restart logic"""

    def _scrape_category(self, category_name, category_config, **kwargs):
        """Custom logic with driver restart between pages"""

        # Use config for URLs
        url = category_config['url']
        pages = category_config.get('pages', 3)

        articles = []

        for page in range(1, pages + 1):
            # Restart driver for each page (stability)
            if self.driver:
                self.driver.quit()
                time.sleep(1)

            self.init_driver()

            # Use configured selectors
            # ... scraping logic ...

        return ScraperResult(...)
```

**Decision tree:**

```
Does generic scraper work?
├─ Yes → Use it! (80% of cases)
└─ No → Why not?
    ├─ Complex JavaScript → Custom scraper
    ├─ Special authentication → Plugin
    ├─ Unusual pagination → Add pagination type
    └─ Driver instability → Custom scraper with fixes
```

**Tasks:**

- [ ] Attempt Sharpress with generic scraper
- [ ] If fails, create custom scraper
- [ ] Migrate LvinPress
- [ ] Document why custom scrapers needed

---

### Day 15: Phase 3 Testing

**Full test suite:**

```bash
# Test all migrated scrapers
python3 test_scrapers_v2.py --all

# Comparison with old scrapers
python3 test_comparison.py --all

# Performance test
python3 test_performance.py --all
```

**Acceptance criteria:**

- All 12 scrapers migrated
- Results within 10% of old scrapers
- No crashes or errors
- Performance similar or better

---

## 📅 Phase 4: Enhancement & Cleanup (Week 4)

### Day 16-17: Add Advanced Features

**Implement:**

**1. Caching System:**

```python
# scrapers/utils/cache.py
class ScraperCache:
    """Cache scraped content to avoid re-scraping"""

    def __init__(self, cache_dir=".cache/scrapers"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def get(self, key: str) -> Optional[Dict]:
        """Get cached result"""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None

    def set(self, key: str, data: Dict, ttl: int = 86400):
        """Cache result with TTL"""
        cache_file = self.cache_dir / f"{key}.json"
        data['cached_at'] = time.time()
        data['ttl'] = ttl
        with open(cache_file, 'w') as f:
            json.dump(data, f)
```

**2. Rate Limiting:**

```python
# scrapers/utils/rate_limiter.py
class RateLimiter:
    """Limit requests per minute"""

    def __init__(self, requests_per_minute: int = 30):
        self.rpm = requests_per_minute
        self.requests = []

    def wait_if_needed(self):
        """Wait if rate limit exceeded"""
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [r for r in self.requests if now - r < 60]

        if len(self.requests) >= self.rpm:
            # Wait until oldest request is >1 min old
            wait_time = 60 - (now - self.requests[0])
            if wait_time > 0:
                time.sleep(wait_time)

        self.requests.append(now)
```

**3. Monitoring:**

```python
# scrapers/utils/monitor.py
class ScraperMonitor:
    """Track scraper performance and health"""

    def __init__(self):
        self.metrics = {}

    def record_scrape(self, website: str, success: bool, duration: float, sentences: int):
        """Record scraping metrics"""
        if website not in self.metrics:
            self.metrics[website] = {
                'total_scrapes': 0,
                'successes': 0,
                'failures': 0,
                'total_duration': 0,
                'total_sentences': 0
            }

        m = self.metrics[website]
        m['total_scrapes'] += 1
        m['successes'] += 1 if success else 0
        m['failures'] += 0 if success else 1
        m['total_duration'] += duration
        m['total_sentences'] += sentences

    def get_report(self) -> Dict:
        """Generate performance report"""
        report = {}
        for website, metrics in self.metrics.items():
            report[website] = {
                'success_rate': metrics['successes'] / metrics['total_scrapes'],
                'avg_duration': metrics['total_duration'] / metrics['total_scrapes'],
                'avg_sentences': metrics['total_sentences'] / metrics['total_scrapes']
            }
        return report
```

**Tasks:**

- [ ] Implement caching system
- [ ] Implement rate limiting
- [ ] Implement monitoring
- [ ] Add to configuration
- [ ] Test with real scrapers

---

### Day 18: Documentation

**Create comprehensive docs:**

1. **Architecture Overview** (`ARCHITECTURE.md`)

   - System design
   - Component diagram
   - Data flow

2. **Configuration Guide** (`CONFIG_GUIDE.md`)

   - All YAML options
   - Examples for each type
   - Best practices

3. **Adding New Websites** (`ADD_WEBSITE.md`)

   - Step-by-step guide
   - Troubleshooting
   - Examples

4. **Custom Scrapers** (`CUSTOM_SCRAPERS.md`)

   - When to create custom scraper
   - How to inherit from base
   - Plugin system

5. **API Reference** (`API.md`)
   - All classes and methods
   - Configuration options
   - Examples

**Tasks:**

- [ ] Write documentation
- [ ] Add code examples
- [ ] Create diagrams
- [ ] Review with team

---

### Day 19: Migration & Cleanup

**Migrate production system:**

1. **Backup old system:**

   ```bash
   git checkout -b backup-old-scrapers
   git add work/tools/scrapers/*.py
   git commit -m "Backup: Old scraper system"
   git push origin backup-old-scrapers
   ```

2. **Deploy new system:**

   ```bash
   git checkout main
   # Copy new scraper system
   # Update import statements
   # Update test scripts
   git add .
   git commit -m "Migration: New configuration-driven scraper system"
   ```

3. **Run parallel for 1 week:**

   ```python
   # Run both systems and compare
   old_results = run_old_scrapers()
   new_results = run_new_scrapers()
   compare_and_alert_if_different(old_results, new_results)
   ```

4. **Remove old system:**
   ```bash
   # After 1 week of successful parallel operation
   git rm work/tools/scrapers/*_scraper.py  # Old scrapers
   git commit -m "Cleanup: Remove old scraper files"
   ```

**Tasks:**

- [ ] Backup old system
- [ ] Deploy new system to staging
- [ ] Run parallel testing
- [ ] Monitor for 1 week
- [ ] Switch to new system fully
- [ ] Remove old code

---

### Day 20: Team Training

**Training session:**

1. **Overview** (30 min)

   - Why we migrated
   - Benefits
   - New workflow

2. **Hands-on: Add Website** (45 min)

   - Pick a Kurdish news site
   - Create YAML config
   - Test it
   - Everyone does it!

3. **Hands-on: Add Category** (15 min)

   - Add category to existing site
   - Test it

4. **Advanced Topics** (30 min)

   - Custom scrapers
   - Plugins
   - Monitoring

5. **Q&A** (30 min)

**Materials:**

- [ ] Presentation slides
- [ ] Live demo
- [ ] Practice exercises
- [ ] Cheat sheet handout

---

## 📊 Success Metrics

### Technical Metrics

- [ ] All 12 scrapers migrated
- [ ] Results within 10% of old system
- [ ] Zero crashes in production
- [ ] Performance ≥ old system
- [ ] Test coverage > 80%

### Productivity Metrics

- [ ] Time to add website: < 30 min
- [ ] Time to add category: < 5 min
- [ ] Time to fix selector: < 10 min
- [ ] Code reduction: > 80%
- [ ] Config files: < 500 lines

### Team Metrics

- [ ] All team members trained
- [ ] 3+ successful website additions by team
- [ ] Zero blocking issues
- [ ] Positive feedback from team

---

## 🚨 Risk Management

### Risk 1: Generic Scraper Doesn't Work for Some Sites

**Mitigation:**

- Keep custom scraper option
- Plugin system for special cases
- Gradual migration (easy sites first)

### Risk 2: Performance Degradation

**Mitigation:**

- Performance testing in Phase 3
- Caching system
- Optimize hot paths

### Risk 3: Configuration Errors

**Mitigation:**

- YAML validation
- Good error messages
- Example configs
- Documentation

### Risk 4: Team Adoption

**Mitigation:**

- Clear documentation
- Hands-on training
- Quick wins (show time savings)
- Support channel

---

## 🎯 Post-Migration Goals

### Month 1

- Add 5 new Kurdish news websites
- Fine-tune configurations
- Gather feedback

### Month 2

- Implement advanced features (proxy, auth)
- Add monitoring dashboard
- Performance optimization

### Month 3

- Scale to 25+ websites
- Internationalization (other languages)
- API for external access

---

## 📝 Checklist

### Pre-Migration

- [ ] Team buy-in
- [ ] Review proposal
- [ ] Allocate resources
- [ ] Set timeline

### During Migration

- [ ] Follow roadmap
- [ ] Daily standups
- [ ] Document issues
- [ ] Regular testing

### Post-Migration

- [ ] Training complete
- [ ] Documentation finalized
- [ ] Old system removed
- [ ] Retrospective meeting

---

## 🎉 Expected Outcomes

**After 4 weeks:**

- ✅ 12 scrapers migrated to config-driven system
- ✅ 90% reduction in code
- ✅ 10x faster to add new websites
- ✅ 100x faster to modify existing scrapers
- ✅ Team trained and productive
- ✅ Foundation for scaling to 50+ websites
- ✅ Happy developers! 😊

**Questions? Issues? Contact the migration team!**
