# Kurdish Corpus Expansion - Modular Architecture

## 📁 Project Structure

```
tools/
├── scrapers/                      # Scraper package
│   ├── __init__.py               # Package initialization
│   ├── base_scraper.py           # Base classes and utilities
│   ├── config.py                 # Configuration settings
│   ├── kurdsat_scraper.py        # Kurdsat TV scraper
│   ├── rudaw_scraper.py          # Rudaw scraper (TODO)
│   ├── khak_scraper.py           # Khak TV scraper (TODO)
│   ├── nrt_scraper.py            # NRT TV scraper (TODO)
│   ├── awene_scraper.py          # Awene scraper (TODO)
│   ├── kurdistan24_scraper.py    # Kurdistan24 scraper (TODO)
│   ├── xendan_scraper.py         # Xendan scraper (TODO)
│   └── sekokurd_scraper.py       # Sekokurd scraper (TODO)
├── expand_corpus_modular.py      # Main orchestrator
├── test_scrapers.py              # Test & verification tool
└── expand_corpus_batch3_reliable.py  # Legacy monolithic script
```

## 🎯 Design Principles

### 1. **Modularity**

- Each news source has its own scraper class
- Scrapers inherit from `BaseScraper` base class
- Easy to add, remove, or modify individual scrapers

### 2. **Maintainability**

- Clear separation of concerns
- Configuration separated from code
- Reusable utility functions in base class

### 3. **Testability**

- `test_scrapers.py` verifies each scraper independently
- Quick identification of broken scrapers
- Sample output for verification

### 4. **Extensibility**

- Abstract base class defines interface
- Easy to add new scrapers following the pattern
- Plugin-like architecture

## 🔧 Core Components

### BaseScraper Class

Base class providing common functionality:

```python
class BaseScraper(ABC):
    - init_driver()           # Initialize Selenium WebDriver
    - cleanup()               # Resource cleanup
    - add_sentence(text)      # Add sentence with QC
    - wait_for_element()      # Wait for element to load
    - safe_get(url)           # Retry-enabled URL loading
    - scrape_political()      # Abstract method (must implement)
    - scrape_specialized()    # Optional override
    - get_stats()             # Get scraping statistics
```

### SimpleQC Class

Quality control for Kurdish text:

- Word count validation (10-30 words)
- Kurdish character ratio check (>70%)
- Filters out non-Kurdish content

### Configuration

Centralized in `scrapers/config.py`:

- Scraper enable/disable flags
- Parameters for each scraper
- Quality control settings
- Output file paths

## 📝 How to Add a New Scraper

### Step 1: Create Scraper Class

Create `scrapers/new_source_scraper.py`:

```python
from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import time

class NewSourceScraper(BaseScraper):
    def __init__(self):
        super().__init__("NewSource")
        self.base_url = "https://newsource.com"

    def scrape_political(self, pages=10):
        """Scrape political news"""
        print(f"\n📰 Scraping {self.name} Political ({pages} pages)...")

        try:
            self.init_driver()
            articles_found = 0

            for page in range(1, pages + 1):
                url = f"{self.base_url}/news?page={page}"
                if not self.safe_get(url):
                    continue

                # Extract content
                titles = self.driver.find_elements(By.CSS_SELECTOR, "h2.title a")
                for title in titles:
                    text = title.text.strip()
                    if self.add_sentence(text):
                        articles_found += 1

                print(f"   Page {page}/{pages}: {articles_found} sentences")

            self.stats['political'] = articles_found
            print(f"✅ {self.name}: {articles_found} sentences")
            return articles_found

        except Exception as e:
            print(f"⚠️  {self.name} error: {e}")
            return 0

    def scrape_specialized(self, articles_per_category=20):
        """Scrape specialized categories (optional)"""
        # Implementation here
        pass
```

### Step 2: Update Configuration

Add to `scrapers/config.py`:

```python
SCRAPER_CONFIGS = {
    # ... existing scrapers ...
    'newsource': {
        'enabled': True,
        'political': {'pages': 10},
        'specialized': {'articles_per_category': 20},
        'categories': ['Category1', 'Category2']
    }
}
```

### Step 3: Register in Orchestrator

Update `expand_corpus_modular.py`:

```python
from scrapers.new_source_scraper import NewSourceScraper

def main():
    orchestrator = CorpusExpansionOrchestrator()
    # ... existing registrations ...
    orchestrator.register_scraper(NewSourceScraper, 'newsource')
    orchestrator.run_all()
```

### Step 4: Add to Test Suite

Update `test_scrapers.py`:

```python
from scrapers.new_source_scraper import NewSourceScraper

scrapers_to_test = [
    # ... existing tests ...
    (NewSourceScraper, True, True),
]
```

## 🧪 Testing Scrapers

### Quick Test (Single Scraper)

```bash
# Test just Kurdsat scraper
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/test_scrapers.py
```

### Full Test (All Scrapers)

Once all scrapers are implemented:

```bash
wsl -d Ubuntu -- timeout 600 python3 /mnt/c/tesseract/work/tools/test_scrapers.py
```

### Test Output

```
======================================================================
Testing Kurdsat
======================================================================

🧪 Testing Political Scraping...
   ✅ SUCCESS: 45 sentences in 12.3s
   📄 Sample sentences:
      1. سەرۆک بارزانی: ئێمە دەمانەوێت ئاشتی لە ناوچەکەدا هەبێت...
      2. حکومەتی هەرێم: پارەی مووچە بە تەواوی دەدرێت...
      3. کۆبوونەوەی پەرلەمان بۆ دانانی بودجەی ٢٠٢٥...

🧪 Testing Specialized Scraping...
   ✅ SUCCESS: 28 sentences in 8.7s

======================================================================
TEST SUMMARY
======================================================================

Scraper              Political       Specialized     Status
----------------------------------------------------------------------
Kurdsat              ✅ 45           ✅ 28           ✅ WORKING

======================================================================
Overall: 1/1 scrapers working (100%)
======================================================================
```

## 🚀 Running Corpus Expansion

### Full Collection

```bash
wsl -d Ubuntu -- sudo docker start flaresolverr
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/expand_corpus_modular.py
```

### Expected Output

```
======================================================================
KURDISH CORPUS EXPANSION - BATCH 3 (MODULAR)
Registered scrapers: 8
======================================================================

======================================================================
SCRAPER: KURDSAT
======================================================================

📰 Running Political Scraping...
   ✅ Collected 450 sentences

📚 Running Specialized Scraping...
   ✅ Collected 180 sentences

✅ KURDSAT: 630 unique sentences in 85.3s

... (other scrapers) ...

======================================================================
COLLECTION SUMMARY
======================================================================

Scraper         Political    Specialized  Total      Time(s)    Status
----------------------------------------------------------------------
kurdsat         450          180          630        85.3       ✅
rudaw           520          240          760        92.1       ✅
...

----------------------------------------------------------------------
TOTAL           3500         2100         21750      8400.5

======================================================================
✅ TOTAL UNIQUE SENTENCES: 21750
⏱️  TOTAL TIME: 140.0 minutes
======================================================================

✅ Saved 21750 sentences to corpus/kurdish_expanded_batch3.txt
```

## 🔍 Troubleshooting

### Scraper Not Working?

1. **Run test script first**:

   ```bash
   wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/test_scrapers.py
   ```

2. **Check error messages** in test output

3. **Disable problematic scraper** in `config.py`:

   ```python
   'problematic_source': {
       'enabled': False,  # Temporarily disable
       ...
   }
   ```

4. **Fix the scraper** based on error messages

5. **Re-test** until working

### Common Issues

| Issue                 | Solution                                   |
| --------------------- | ------------------------------------------ |
| Selector not found    | Update CSS selectors in scraper            |
| Timeout errors        | Increase `PAGE_LOAD_TIMEOUT` in config     |
| Cloudflare blocking   | Use FlareSolverr (see Kurdistan24 example) |
| Quality check failing | Adjust `QC_SETTINGS` in config             |
| Memory issues         | Reduce batch sizes in config               |

## 📊 Advantages Over Monolithic Script

| Aspect             | Monolithic (Old)          | Modular (New)                   |
| ------------------ | ------------------------- | ------------------------------- |
| **File Size**      | 1,300+ lines              | ~200 lines per scraper          |
| **Testing**        | Test entire script        | Test each scraper individually  |
| **Debugging**      | Hard to isolate issues    | Easy to identify broken scraper |
| **Maintenance**    | Change affects everything | Change isolated to one scraper  |
| **Adding Sources** | Modify large file         | Create new small file           |
| **Collaboration**  | Merge conflicts           | Work on separate scrapers       |
| **Reusability**    | Copy-paste code           | Import and extend base class    |

## 🎯 Migration Path

### Phase 1: Create Base Structure ✅

- [x] Base scraper class
- [x] Configuration system
- [x] Test framework
- [x] Orchestrator

### Phase 2: Migrate Existing Scrapers

- [x] Kurdsat (example completed)
- [ ] Rudaw
- [ ] Khak TV
- [ ] NRT TV
- [ ] Awene
- [ ] Kurdistan24
- [ ] Xendan
- [ ] Sekokurd

### Phase 3: Testing & Validation

- [ ] Test all scrapers individually
- [ ] Run full collection
- [ ] Compare output with legacy script
- [ ] Verify sentence counts

### Phase 4: Deprecate Legacy

- [ ] Mark `expand_corpus_batch3_reliable.py` as deprecated
- [ ] Update PowerShell script to use modular version
- [ ] Archive legacy code

## 📝 TODO: Remaining Scrapers

To complete the migration, create these scrapers following the Kurdsat example:

1. **RudawScraper** - `scrapers/rudaw_scraper.py`
2. **KhakScraper** - `scrapers/khak_scraper.py`
3. **NRTScraper** - `scrapers/nrt_scraper.py`
4. **AweneScraper** - `scrapers/awene_scraper.py`
5. **Kurdistan24Scraper** - `scrapers/kurdistan24_scraper.py` (with FlareSolverr)
6. **XendanScraper** - `scrapers/xendan_scraper.py`
7. **SekokurdScraper** - `scrapers/sekokurd_scraper.py`

Each scraper should:

- Inherit from `BaseScraper`
- Implement `scrape_political()`
- Optionally implement `scrape_specialized()`
- Use configuration from `config.py`
- Include error handling

## 📚 Additional Resources

- **Base Scraper API**: See `scrapers/base_scraper.py` for all available methods
- **Configuration Options**: See `scrapers/config.py` for all settings
- **Testing Guide**: See `test_scrapers.py` for test framework usage
- **Legacy Code Reference**: See `expand_corpus_batch3_reliable.py` for scraping logic

---

**Status**: ✅ Framework Complete | ⏳ 1/8 Scrapers Migrated | 📝 7 Scrapers TODO
