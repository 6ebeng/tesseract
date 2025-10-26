# Quick Start Guide: Adding New Websites & Categories

## For the Refactored Scraper System

---

## 🎯 Example 1: Adding a Brand New Website (3 minutes!)

### Scenario: Adding "KurdistanPost.com"

**Step 1: Add to `websites.yaml`** (2 minutes)

```yaml
kurdistanpost:
  name: 'Kurdistan Post'
  base_url: 'https://kurdistanpost.com'
  scraper_class: 'GenericScraper' # Use generic scraper
  enabled: true

  categories:
    politics:
      enabled: true
      type: 'pagination'
      url: 'https://kurdistanpost.com/category/politics'
      pages: 5

    economy:
      enabled: true
      url: 'https://kurdistanpost.com/category/economy'
      pages: 3

    health:
      enabled: true
      url: 'https://kurdistanpost.com/category/health'
      pages: 3

    culture:
      enabled: true
      url: 'https://kurdistanpost.com/category/culture'
      pages: 3

  selectors:
    article_list: 'div.post'
    article_link: 'a.post-link'
    article_title: 'h1.title'
    article_content: 'div.content'
    article_paragraphs: 'div.content p'
```

**Step 2: Test it** (1 minute)

```bash
cd work/tools
python3 test_scrapers_v2.py --website kurdistanpost
```

**Done! 🎉**

---

## 🎯 Example 2: Adding New Category to Existing Website (30 seconds!)

### Scenario: Add "Technology" category to Rudaw

**Edit `websites.yaml`:**

```yaml
rudaw:
  # ... existing config ...
  categories:
    kurdistan:
      enabled: true
      url: 'https://rudaw.net/sorani/kurdistan'
      scrolls: 20

    economy:
      enabled: true
      url: 'https://rudaw.net/sorani/business'
      pages: 3

    # ... existing categories ...

    technology: # NEW!
      enabled: true
      url: 'https://rudaw.net/sorani/tech'
      pages: 3
```

**Test:**

```bash
python3 test_scrapers_v2.py --website rudaw --category technology
```

**Done! 🎉**

---

## 🎯 Example 3: Temporarily Disable Category (5 seconds!)

### Scenario: Economy category is broken, disable it until fixed

**Edit `websites.yaml`:**

```yaml
rudaw:
  categories:
    economy:
      enabled: false # Just change this!
      # ... rest of config stays the same ...
```

**No code changes needed! Next run will skip it automatically.**

---

## 🎯 Example 4: Website Has Special Pagination

### Scenario: New site uses "Load More" button instead of page numbers

**Add to `websites.yaml`:**

```yaml
specialsite:
  name: 'Special Site'
  base_url: 'https://specialsite.com'
  scraper_class: 'GenericScraper'
  enabled: true

  categories:
    news:
      enabled: true
      type: 'load_more' # Different pagination type!
      url: 'https://specialsite.com/news'
      clicks: 5 # Click "Load More" 5 times

  selectors:
    article_list: 'article'
    article_link: 'a'
    load_more_button: 'button#load-more' # Selector for button
```

**Generic scraper handles it automatically!**

---

## 🎯 Example 5: Website Needs Custom Logic

### Scenario: Website has complex JavaScript rendering that generic scraper can't handle

**Step 1: Create custom scraper** (`scrapers/implementations/complexsite_scraper.py`)

```python
from scrapers.base.scraper_base import ConfigurableScraper, ScraperResult
from selenium.webdriver.common.by import By
import time


class ComplexsiteScraper(ConfigurableScraper):
    """
    Custom scraper for sites with complex requirements.
    Inherits configuration system but adds custom logic.
    """

    def _scrape_category(self, category_name: str, category_config: Dict, **kwargs):
        """Custom scraping logic"""
        articles = []

        # Your custom logic here
        # But still use config for URLs, selectors, etc.
        url = category_config['url']
        pages = category_config.get('pages', 3)

        # Example: Handle complex JavaScript
        self.init_driver()
        self.safe_get(url)

        # Wait for JavaScript to load
        time.sleep(5)

        # Execute custom JavaScript
        self.driver.execute_script("""
            // Your custom JS here
            window.loadAllContent();
        """)

        # Then use standard extraction
        article_elements = self.driver.find_elements(
            By.CSS_SELECTOR,
            self.selectors['article_list']
        )

        for elem in article_elements:
            # ... extract articles ...
            pass

        return ScraperResult(
            source=self.name,
            category=category_name,
            articles=articles,
            sentence_count=len(articles),
            success=True
        )
```

**Step 2: Reference it in config**

```yaml
complexsite:
  name: 'Complex Site'
  base_url: 'https://complexsite.com'
  scraper_class: 'ComplexsiteScraper' # Use your custom scraper
  enabled: true
  # ... rest of config ...
```

**Best of both worlds: Configuration + Custom logic when needed!**

---

## 🎯 Example 6: Different Quality Control per Website

### Scenario: Poetry site needs different word count limits than news sites

**Add to `websites.yaml`:**

```yaml
balinde:
  name: 'Balinde'
  base_url: 'https://balinde.com'
  scraper_class: 'GenericScraper'
  enabled: true

  # Custom quality control settings!
  quality_control:
    min_words: 5 # Poetry lines are shorter
    max_words: 40 # Allow longer lines
    min_kurdish_ratio: 0.6 # Slightly lower threshold

  categories:
    poetry:
      enabled: true
      url: 'https://balinde.com/category/kurdishpoem'
      pages: 3

    articles:
      enabled: true
      url: 'https://balinde.com/category/articles'
      pages: 3
```

**Each website can have its own QC rules!**

---

## 🎯 Example 7: Batch Operations

### Scenario: Enable/disable multiple categories at once

**Before migration:**

```python
# Need to edit code in 5 different scraper files
# Risk of errors, inconsistencies
```

**After migration:**

```bash
# Use search & replace in YAML
# Find: "enabled: true"
# Replace: "enabled: false"
# In: health categories only
```

**Or use a script:**

```python
# scripts/toggle_categories.py
import yaml

def disable_category(category_name):
    with open('websites.yaml', 'r') as f:
        config = yaml.safe_load(f)

    for website in config['websites'].values():
        specialized = website.get('categories', {}).get('specialized', {})
        if category_name in specialized:
            specialized[category_name]['enabled'] = False

    with open('websites.yaml', 'w') as f:
        yaml.dump(config, f)

# Disable all "health" categories across all sites
disable_category('health')
```

---

## 🎯 Example 8: Environment-Specific Configurations

### Scenario: Different settings for development vs production

**Create `websites.dev.yaml`:**

```yaml
# Development config - faster, less data
rudaw:
  categories:
    political:
      pages: 1 # Just 1 page in dev
    specialized:
      economy:
        pages: 1
      health:
        enabled: false # Skip in dev
```

**Create `websites.prod.yaml`:**

```yaml
# Production config - full scraping
rudaw:
  categories:
    political:
      pages: 10 # Full 10 pages
    specialized:
      economy:
        pages: 5
      health:
        enabled: true
```

**Run with environment flag:**

```bash
# Development
python3 scrape.py --config websites.dev.yaml

# Production
python3 scrape.py --config websites.prod.yaml
```

---

## 🎯 Example 9: A/B Testing Scraping Strategies

### Scenario: Test different pagination approaches for same site

**Strategy A: Scroll-based**

```yaml
# websites_strategy_a.yaml
kurdsat:
  categories:
    political:
      type: 'scroll'
      clicks: 3
```

**Strategy B: Page-based**

```yaml
# websites_strategy_b.yaml
kurdsat:
  categories:
    political:
      type: 'pagination'
      pages: 3
```

**Test both:**

```bash
python3 scrape.py --config strategy_a.yaml --output results_a.json
python3 scrape.py --config strategy_b.yaml --output results_b.json
python3 compare_results.py results_a.json results_b.json
```

---

## 🎯 Example 10: Using CSS and XPath Selectors

### Scenario: Website with complex structure needs mixed selectors

**CSS for simple selections:**

```yaml
newsite:
  name: 'New Kurdish Site'
  base_url: 'https://newsite.com'

  selectors:
    # CSS - simple and readable
    article_list: 'div.article-card'
    article_link: 'a'
    article_date: 'time'
    article_paragraphs: 'div.content > p'
```

**XPath for complex selections:**

```yaml
newsite:
  selectors:
    # XPath - exclude sponsored content
    article_list:
      type: 'xpath'
      value: "//div[@class='article' and not(contains(@class, 'sponsored'))]"

    # XPath - text matching for Kurdish
    kurdish_articles:
      type: 'xpath'
      value: "//article[contains(., 'هەواڵ')]"

    # XPath - find active "Load More" button
    load_more_button:
      type: 'xpath'
      value: "//button[@data-action='load' and not(@disabled)]"
```

**Mixed approach (best practice):**

```yaml
khak:
  name: 'Khak News'
  base_url: 'https://khak.news'

  selectors:
    # CSS for simple selections
    article_list: 'article.post'
    article_link: 'a.permalink'
    article_date: 'time'

    # XPath for complex conditions
    article_title:
      type: 'xpath'
      value: "//h1[not(contains(@class, 'ad'))]"

    valid_articles:
      type: 'xpath'
      value: "//article[@data-type='news' and not(@data-sponsored='true')]"

  categories:
    politics:
      enabled: true
      url: 'https://khak.news/politics'
      type: 'pagination'
      pages: 3
      selectors:
        # Override with XPath for position-based selection
        main_article:
          type: 'xpath'
          value: "//section[@id='politics']//article[1]"

        # CSS for other elements
        article_paragraphs: 'div.article-body > p'
```

**When to use each:**

| Need                | Use   | Example                           |
| ------------------- | ----- | --------------------------------- |
| Class selection     | CSS   | `div.article`                     |
| ID selection        | CSS   | `#main-content`                   |
| Direct children     | CSS   | `div > p`                         |
| Attribute equals    | CSS   | `a[href='/news']`                 |
| Text contains       | XPath | `//h1[contains(text(), 'خەبەر')]` |
| Multiple conditions | XPath | `//div[@class='x' and @type='y']` |
| Parent navigation   | XPath | `//a/parent::div`                 |
| Position selection  | XPath | `//article[last()]`               |

**Finding selectors in browser:**

```bash
# Open browser DevTools (F12)
# For CSS:
$$("div.article-card")  # Test in console

# For XPath:
$x("//div[@class='article-card']")  # Test in console
```

---

## 🎯 Example 11: Configuring Wait Times for Slow Sites

### Scenario: Website loads slowly, needs custom wait times

**Problem: Default wait times cause missed content**

```yaml
# Default waits (too fast for slow site)
slowsite:
  name: 'Slow News Site'
  base_url: 'https://slowsite.com'

  categories:
    news:
      type: 'scroll'
      url: 'https://slowsite.com/news'
      scrolls: 10
      # Using defaults: 2s after scroll (not enough!)
```

**Solution 1: Increase website-level wait times**

```yaml
slowsite:
  name: 'Slow News Site'
  base_url: 'https://slowsite.com'

  # Apply to all categories
  wait_times:
    page_load: 5 # Wait 5s after page load
    after_scroll: 4 # Wait 4s after each scroll
    after_click: 2 # Wait 2s after clicks
    element_timeout: 15 # Max 15s for elements
    between_articles: 1 # 1s between articles

  categories:
    news:
      type: 'scroll'
      url: 'https://slowsite.com/news'
      scrolls: 10
      # Uses website wait times
```

**Solution 2: Category-specific wait times**

```yaml
slowsite:
  name: 'Slow News Site'

  # Fast categories use these
  wait_times:
    page_load: 3
    after_scroll: 2

  categories:
    news:
      type: 'scroll'
      url: 'https://slowsite.com/news'
      scrolls: 10
      # Uses website defaults (fast)

    economy:
      type: 'scroll'
      url: 'https://slowsite.com/economy'
      scrolls: 10
      # Override: economy is slower
      wait_times:
        page_load: 6
        after_scroll: 5
        element_timeout: 20
```

**Solution 3: Wait for specific elements (best!)**

```yaml
slowsite:
  categories:
    economy:
      type: 'scroll'
      url: 'https://slowsite.com/economy'
      scrolls: 10

      # Manual wait as baseline
      wait_times:
        after_scroll: 2

      # Smart wait for loading spinner
      wait_for:
        element: 'div.loading-spinner'
        condition: 'invisible' # Wait until spinner gone
        timeout: 15 # Max 15 seconds
        fallback_wait: 3 # If no spinner found, wait 3s
```

**Solution 4: Multiple wait conditions**

```yaml
ajaxsite:
  name: 'AJAX Heavy Site'

  categories:
    news:
      type: 'infinite_scroll'
      url: 'https://ajaxsite.com/news'
      scrolls: 15

      wait_times:
        after_scroll: 1 # Base wait

      # Multiple smart waits
      wait_for:
        # First, wait for spinner to disappear
        - element: 'div.spinner'
          condition: 'invisible'
          timeout: 10

        # Then, wait for articles to appear
        - element: 'article.post'
          condition: 'count'
          count: 5 # At least 5 articles loaded
          timeout: 10

        # Finally, wait for content populated
        - element: 'div.article-body'
          condition: 'text_present'
          timeout: 5
```

**Wait condition types:**

| Condition      | Description        | Example                 |
| -------------- | ------------------ | ----------------------- |
| `visible`      | Element appears    | Article cards load      |
| `invisible`    | Element disappears | Loading spinner gone    |
| `present`      | Element in DOM     | Check element exists    |
| `clickable`    | Button ready       | Load More button active |
| `count`        | N elements exist   | Wait for 10 articles    |
| `text_present` | Text in element    | Content populated       |

**Finding the right waits:**

```bash
# Test manually in browser DevTools console
# Time how long content takes to load

# After scroll, check when articles appear:
console.time('load');
window.scrollTo(0, document.body.scrollHeight);
// Watch for articles to appear
console.timeEnd('load');  // Shows: load: 3421.2ms

# Use this time + buffer for wait_times.after_scroll
# 3.4s measured → set to 4s in config
```

---

## 🎯 Example 12: XPath Multiple Nodes with Join Delimiters

### Scenario: Extract content from multiple elements and combine them

**Problem: Article content is split across multiple `<p>` tags**

```yaml
# Single selector - only gets first paragraph
article_content: 'div.content p' # Returns only first <p>
```

**Solution: Use XPath with multiple nodes**

```yaml
newsite:
  name: 'News Site'
  base_url: 'https://newsite.com'

  selectors:
    # Extract ALL paragraphs and join with newline
    article_content:
      type: 'xpath'
      value: "//div[@class='content']//p"
      multiple: true # Extract all matching nodes
      join: "\n" # Join with newline

    # Extract keywords as comma-separated
    article_keywords:
      type: 'xpath'
      value: "//ul[@class='tags']//li/text()"
      multiple: true
      join: ', ' # Join with comma-space

    # Extract quotes with spacing
    article_quotes:
      type: 'xpath'
      value: '//blockquote'
      multiple: true
      join: "\n\n" # Join with double newline

    # Extract author bio (multiple paragraphs as continuous text)
    article_author_bio:
      type: 'xpath'
      value: "//div[@class='author-bio']//p"
      multiple: true
      join: ' ' # Join with space
```

**Common join patterns:**

| Delimiter | Result             | Use Case                   |
| --------- | ------------------ | -------------------------- |
| `"\n"`    | Line by line       | Article paragraphs         |
| `"\n\n"`  | Separated sections | Quotes, major sections     |
| `", "`    | Comma-separated    | Tags, keywords, categories |
| `" "`     | Continuous text    | Multi-paragraph bios       |
| `"; "`    | Semicolon list     | Citations, attributions    |
| `" \| "`  | Pipe-separated     | Alternative sections       |

**Real-world example: Rudaw articles**

```yaml
rudaw:
  name: 'Rudaw'

  selectors:
    # Standard single-element selectors
    article_title: 'h1'
    article_date: 'time'

    # Multiple paragraphs joined with newline
    article_content:
      type: 'xpath'
      value: "//div[@class='article__body']//p"
      multiple: true
      join: "\n"

    # Extract section headings
    article_sections:
      type: 'xpath'
      value: '//article//h2 | //article//h3'
      multiple: true
      join: "\n\n"

    # Extract image captions
    article_captions:
      type: 'xpath'
      value: '//figure//figcaption'
      multiple: true
      join: "\n\n"

    # Extract keywords/tags
    article_keywords:
      type: 'xpath'
      value: "//div[@class='tags']//a/text()"
      multiple: true
      join: ', '
```

**With fallback chains:**

```yaml
kurdistan24:
  selectors:
    # Try multiple selectors, each can extract multiple nodes
    article_content:
      # First try: new layout with multiple divs
      - type: 'xpath'
        value: "//div[@class='article-body']//p"
        multiple: true
        join: "\n"

      # Second try: old layout with multiple paragraphs
      - type: 'xpath'
        value: "//div[@class='post-content']//p"
        multiple: true
        join: "\n"

      # Third try: single element fallback
      - 'div.article-content'
```

**How it works:**

```
Input HTML:
<div class="content">
  <p>First paragraph</p>
  <p>Second paragraph</p>
  <p>Third paragraph</p>
</div>

Configuration:
article_content:
  type: 'xpath'
  value: "//div[@class='content']//p"
  multiple: true
  join: "\n"

Output:
"First paragraph
Second paragraph
Third paragraph"
```

**Benefits:**

- ✅ Captures complete article content
- ✅ Preserves paragraph structure
- ✅ Customizable formatting
- ✅ Works with any delimiter
- ✅ Combines with fallback chains

---

## 🎯 Example 13: Using Fallback Selector Chains

### Scenario: Website has multiple article layouts with different selectors

**Problem: Some articles use different HTML structure**

```yaml
# Single selector - fails for some articles
newsite:
  selectors:
    article_title: 'h1.main-title' # Only works for 70% of articles
```

**Solution: Use fallback chain**

```yaml
newsite:
  name: 'News Site'
  base_url: 'https://newsite.com'

  selectors:
    # Try multiple selectors in order
    article_title:
      - 'h1.main-title' # Try first (70% of articles)
      - 'h1.post-title' # Try second (20% of articles)
      - type: 'xpath'
        value: "//h1[@class='title']" # Try third (5%)
      - 'h1' # Last resort (5%)

    article_content:
      - 'div.article-body' # New layout
      - 'div.post-content' # Old layout
      - 'article > div.content' # Alternative
      - type: 'xpath'
        value: "//article//div[contains(@class, 'text')]"

    article_author:
      - 'span.author-name' # Primary
      - 'div.byline' # Alternative
      - type: 'xpath'
        value: "//span[contains(text(), 'By')]/following-sibling::span"
```

**How it works:**

1. Tries first selector
2. If element found AND not empty → Use it ✅
3. If not found OR empty → Try next selector
4. Repeat until success or chain exhausted

**Real-world example: NRT with mixed layouts**

```yaml
nrt:
  name: 'NRT'
  base_url: 'https://nrttv.com'

  selectors:
    # Collection page - single selector works
    article_list: 'article.post'
    article_link: 'a'

    # Article page - multiple layouts exist
    article_title:
      - 'h1.article-headline' # 60% of articles
      - 'h1.post-title' # 30% of articles
      - type: 'xpath'
        value: "//div[@class='header']//h1" # 8%
      - 'h1' # 2% fallback

    article_content:
      - 'div.article__body' # New design
      - 'div.entry-content' # Old design
      - 'div.post-content' # Very old
      - type: 'xpath'
        value: "//article//div[contains(@class, 'content')]"

    article_date:
      - 'time.published'
      - 'span.date'
      - type: 'xpath'
        value: '//time[@datetime]'
      - type: 'xpath'
        value: "//meta[@property='article:published_time']/@content"

  categories:
    politics:
      url: 'https://nrttv.com/politics'
      type: 'pagination'
      pages: 5
```

**Kurdish-specific fallbacks:**

```yaml
awene:
  name: 'Awene'

  selectors:
    article_content:
      - 'div.ناوەرۆک' # Kurdish class name
      - 'div.article-body-ku' # English with Kurdish suffix
      - 'div.article-body' # Generic
      - type: 'xpath'
        value: "//div[@lang='ku']" # Has Kurdish lang attribute
      - type: 'xpath'
        value: "//article//div[contains(., 'هەواڵ')]" # Contains Kurdish text

    article_author:
      - type: 'xpath'
        value: "//span[contains(text(), 'نووسەر:')]" # "Author:" in Kurdish
      - 'span.author'
      - type: 'xpath'
        value: "//div[@class='meta']/span[1]"
```

**Website redesign support:**

```yaml
khak:
  name: 'Khak News'

  # Support both old and new designs during transition
  selectors:
    article_list:
      - 'div.article-card-v2' # New design (rolling out)
      - 'div.post-card' # Old design (being replaced)

    article_title:
      - 'h1.article-title-new' # New design
      - 'h1.entry-title' # Old design
      - 'h1' # Universal fallback

    article_content:
      - 'div.article-body-v2' # New design
      - 'div.post-content' # Old design
      - 'article > div' # Structure-based
```

**Benefits:**

- ✅ Higher success rate (95%+ vs 70%)
- ✅ Handles website redesigns gracefully
- ✅ Supports multiple content types
- ✅ No code changes needed for layout variations
- ✅ Automatic fallback to generic selectors

**Performance:**

- Fast: First selector usually succeeds (< 0.1s)
- Graceful: Falls back only when needed
- Complete: Tries all options before giving up

---

## 🎯 Example 13: Export Configuration for Team

### Scenario: Share your scraper config with team members

**Your setup:**

```yaml
# my_custom_config.yaml
# Optimized for my testing workflow
rudaw:
  categories:
    political:
      pages: 2
    specialized:
      economy:
        enabled: true
        pages: 1
      health:
        enabled: false # I don't need this
```

**Commit to Git:**

```bash
git add my_custom_config.yaml
git commit -m "My optimized test config"
git push
```

**Team member uses it:**

```bash
git pull
python3 scrape.py --config my_custom_config.yaml
```

---

## 📊 Time Comparison Summary

| Task                    | Before Refactoring            | After Refactoring             |
| ----------------------- | ----------------------------- | ----------------------------- |
| Add new website         | 4-6 hours (200 lines of code) | 15 minutes (30 lines of YAML) |
| Add new category        | 30-60 minutes (modify code)   | 2 minutes (add 5 lines YAML)  |
| Disable category        | 5 minutes (modify code, test) | 5 seconds (change one word)   |
| Change pagination       | 20 minutes (code + test)      | 1 minute (change one line)    |
| Adjust page count       | 10 minutes (find in code)     | 30 seconds (change number)    |
| Test changes            | Full test suite (30 min)      | Single scraper (2 min)        |
| Share with team         | Explain code + commit         | Share YAML file               |
| Onboard new contributor | 2-3 hours (explain code)      | 15 minutes (show YAML)        |

**Total time savings: ~90%**

---

## 🚀 Real-World Scenarios

### Sprint Goal: "Add 5 new Kurdish news websites"

**Before refactoring:**

- Developer A: 2 weeks (20 hours of coding)
- Code reviews, debugging, integration
- High risk of bugs

**After refactoring:**

- Developer A: 2-3 hours (just YAML config)
- Quick test with generic scraper
- Low risk (no code changes)

**Result: 90% time savings + higher quality**

---

### Maintenance: "Site changed their CSS classes"

**Before refactoring:**

```python
# Find the scraper file
# Find where selectors are used (multiple places)
# Update each location
# Test entire scraper
# Hope you didn't miss any
```

**After refactoring:**

```yaml
# Open websites.yaml
# Find website entry
# Update selectors section
# Test
# Done!

selectors:
  article_list: 'div.new-class' # Changed from "div.post"
```

**One change, one place, done!**

---

## 💡 Pro Tips

1. **Start with generic scraper** - 80% of sites work with it
2. **Only write custom code when necessary** - Keep it simple
3. **Use descriptive category names** - `economic-analysis` not `econ1`
4. **Comment your configs** - Help future you understand why
5. **Version your configs** - Use Git for YAML files
6. **Test incrementally** - Add one category, test, repeat
7. **Share successful configs** - Build a library
8. **Document special cases** - Note why custom scraper was needed

---

## 🎓 Training New Contributors

**Old way:**
"Read through 12 scraper files, understand the patterns, then try to add one..."

**New way:**

1. "Here's websites.yaml"
2. "Copy an existing entry"
3. "Change the URLs and names"
4. "Run the test"
5. "You're done!"

**Time to first contribution: 15 minutes instead of days**

---

## ✅ Checklist for Adding New Website

- [ ] Get website URL and explore structure
- [ ] Identify category URLs
- [ ] Find CSS selectors using browser DevTools
- [ ] Copy similar website entry from config
- [ ] Update name, URLs, selectors
- [ ] Set enabled: true
- [ ] Run test: `python3 test_scrapers_v2.py --website yoursite`
- [ ] Verify sentence count > 0
- [ ] Adjust pages/clicks if needed
- [ ] If generic scraper doesn't work, consider custom scraper
- [ ] Commit config to Git
- [ ] Done! 🎉

---

**Questions? See the full proposal in `SCRAPER_REFACTORING_PROPOSAL.md`**
