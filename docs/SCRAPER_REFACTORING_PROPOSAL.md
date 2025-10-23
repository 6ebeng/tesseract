# Scraper Architecture Refactoring & Optimization

## Proposal for Enhanced Maintainability and Scalability

---

## 📋 Current Architecture Analysis

### Strengths:

✅ Base class abstraction with SimpleQC
✅ Consistent driver management
✅ Standard error handling
✅ Quality control integration

### Pain Points:

❌ Hard-coded category URLs in each scraper
❌ Duplicate pagination logic across scrapers
❌ No unified configuration management
❌ Manual scraper registration in test scripts
❌ Mixed concerns (scraping + business logic)
❌ Difficult to add new categories without code changes
❌ No easy way to disable/enable specific categories
❌ Limited metadata tracking (dates, sources, categories)

---

## 🎯 Proposed Architecture

### 1. Configuration-Driven Design

**Create: `scrapers/config/websites.yaml`**

```yaml
# Website configurations - Easy to add new sites!
websites:
  kurdsat:
    name: 'Kurdsat'
    base_url: 'https://kurdsat.tv'
    scraper_class: 'KurdsatScraper'
    enabled: true
    features:
      - scroll_pagination
      - dynamic_content

    # Default wait times (in seconds) - can be overridden per category
    wait_times:
      page_load: 3 # Wait after page load
      after_scroll: 2 # Wait after each scroll
      after_click: 1 # Wait after button clicks
      element_timeout: 10 # Max wait for elements to appear
      between_articles: 0.5 # Delay between processing articles

    # Default selectors for most categories
    # Supports: CSS, XPath, and fallback chains
    selectors:
      article_list:
        type: 'css' # or "xpath"
        value: 'div.post-card'
      article_link: 'a.post-link' # Shorthand (defaults to CSS)

      # Fallback chain: try multiple selectors until one succeeds
      article_title:
        - type: 'css'
          value: 'h1.entry-title'
        - type: 'xpath'
          value: "//h1[@class='title']"
        - 'h1' # Shorthand fallback

      article_content:
        - 'div.entry-content'
        - 'div.article-body'
        - 'article > div'

      article_paragraphs: 'div.entry-content p'

    categories:
      politics:
        enabled: true
        type: 'scroll'
        url: 'https://kurdsat.tv/cat/politics'
        clicks: 3
        # Uses default selectors

      health:
        enabled: true
        type: 'pagination'
        url: 'https://kurdsat.tv/cat/health'
        pages: 3
        # Different collection page structure
        selectors:
          article_list: 'article.health-post' # Category-specific
          article_link: 'a'
          # Article page uses default selectors

      science:
        enabled: true
        type: 'pagination'
        url: 'https://kurdsat.tv/cat/science'
        pages: 3
        # Science section has completely different structure
        # Mix of CSS and XPath selectors
        selectors:
          # Collection page selectors
          article_list:
            type: 'xpath'
            value: "//div[@class='science-grid-item']"
          article_link: 'a.sci-link' # CSS shorthand
          pagination_next: 'a.next'
          # Article page selectors
          article_title:
            type: 'xpath'
            value: "//h1[contains(@class, 'science-title')]"
          article_content: 'div.science-body'
          article_paragraphs: 'div.science-body > p'

      technology:
        enabled: true
        type: 'infinite_scroll' # Another pagination type!
        url: 'https://kurdsat.tv/cat/tech'
        scrolls: 10
        scroll_pause: 3 # Wait 3 seconds between scrolls
        # Tech section uses AJAX loading - needs custom wait times
        wait_times:
          after_scroll: 4 # Slower site, wait longer
          element_timeout: 15 # AJAX can be slow
        selectors:
          article_list: 'div.tech-card'
          article_link: 'a'
          loading_indicator: 'div.loading-spinner' # Wait for this to disappear
        wait_for:
          # Wait for specific element before continuing
          element: 'div.tech-card'
          condition: 'visible' # visible, invisible, clickable, present
          timeout: 15

      opinion:
        enabled: true
        type: 'pagination'
        url: 'https://kurdsat.tv/cat/opinion'
        pages: 3
        # Opinion articles have different structure
        # Use fallback chains for reliability
        selectors:
          article_list: 'div.opinion-article'
          article_link: 'a.read-more'

          # Try multiple selectors for title (different layouts)
          article_title:
            - 'h1.opinion-headline'
            - type: 'xpath'
              value: "//h1[contains(@class, 'headline')]"
            - 'h1' # Last resort

          # Try multiple selectors for content
          article_content:
            - 'div.opinion-text'
            - 'div.article-body'
            - 'article > div.content'

          article_paragraphs: 'div.opinion-text p'
          author_info: 'div.author-bio' # Extra field for opinions

  rudaw:
    name: 'Rudaw'
    base_url: 'https://rudaw.net'
    scraper_class: 'RudawScraper'
    enabled: true
    features:
      - page_pagination
      - static_content

    # Rudaw is fast, use shorter wait times
    wait_times:
      page_load: 2
      after_click: 0.5
      element_timeout: 8
      between_articles: 0.3

    # Default selectors (can be overridden per category)
    selectors:
      article_list: 'article.card'
      article_link: 'a.article-link'
      article_title: 'h1'
      article_content: 'div.article__body'
      article_paragraphs: 'div.article__body p'
      pagination_next: 'a.next-page'

    categories:
      kurdistan:
        enabled: true
        type: 'scroll' # Different pagination type!
        url: 'https://rudaw.net/sorani/kurdistan'
        scrolls: 20
        # Uses default selectors

      economy:
        enabled: true
        type: 'pagination'
        url: 'https://rudaw.net/sorani/business'
        pages: 3
        # Override selectors for this category
        selectors:
          article_list: 'div.business-article' # Different structure
          article_link: 'a.business-link'
          pagination_next: 'a.page-next'

      health:
        enabled: true
        type: 'pagination'
        url: 'https://rudaw.net/sorani/health'
        pages: 3
        # Uses default selectors

      sport:
        enabled: true
        type: 'load_more' # Different pagination type!
        url: 'https://rudaw.net/sorani/sport'
        clicks: 5
        # Override selectors for sport section
        selectors:
          article_list: 'div.sport-card'
          article_link: 'a'
          load_more_button: 'button.load-more-sports'
          article_title: 'h2.sport-title' # Different on article page
          article_content: 'div.sport-content'

      culture:
        enabled: true
        type: 'pagination'
        url: 'https://rudaw.net/sorani/culture'
        pages: 3
        # Uses default selectors

      interview:
        enabled: true
        type: 'pagination'
        url: 'https://rudaw.net/sorani/interviews'
        pages: 3
        # Override selectors for interview section
        selectors:
          article_list: 'div.interview-card'
          article_title: 'h1.interview-question'
          article_content: 'div.interview-body'
          article_paragraphs: 'div.interview-body div.answer'

  # Easy to add new websites!
  newsite:
    name: 'NewWebsite'
    base_url: 'https://newwebsite.com'
    scraper_class: 'GenericScraper' # Uses generic implementation
    enabled: false # Disable during development

    categories:
      politics:
        enabled: true
        url: 'https://newwebsite.com/politics'
        pages: 3

  # Example: Maximum category variation
  kurdistan24:
    name: 'Kurdistan24'
    base_url: 'https://www.kurdistan24.net'
    scraper_class: 'GenericScraper'
    enabled: true

    # Default selectors (used by most categories)
    selectors:
      article_list: 'div.article-item'
      article_link: 'a.article-link'
      article_title: 'h1.article-title'
      article_content: 'div.article-content'
      article_paragraphs: 'div.article-content p'
      article_date: 'time'

    categories:
      # 1. Standard pagination with defaults
      news:
        enabled: true
        type: 'pagination'
        url: 'https://www.kurdistan24.net/ckb/news'
        pages: 5
        # Uses all default selectors

      # 2. Infinite scroll with loading indicator
      economy:
        enabled: true
        type: 'infinite_scroll'
        url: 'https://www.kurdistan24.net/ckb/economy'
        scrolls: 15
        scroll_pause: 1.5
        wait_times:
          after_scroll: 2.5 # Override: economy section loads slower
          element_timeout: 12
        wait_for:
          element: 'div.spinner'
          condition: 'invisible' # Wait for spinner to disappear
          timeout: 10
        selectors:
          loading_indicator: 'div.spinner' # Wait for this to disappear
          article_list: 'article.economy-card'

      # 3. Load more with completely different structure
      sport:
        enabled: true
        type: 'load_more'
        url: 'https://www.kurdistan24.net/ckb/sport'
        clicks: 8
        selectors:
          load_more_button:
            type: 'xpath'
            value: "//button[@id='load-more-sports']"
          article_list: 'div.sport-item'
          article_link: 'a.sport-link'
          article_title: 'h2.sport-headline'
          article_content: 'div.sport-body'
          article_paragraphs: 'div.sport-body > p'

      # 4. Numbered pages with URL pattern
      culture:
        enabled: true
        type: 'numbered_pages'
        url: 'https://www.kurdistan24.net/ckb/culture'
        pages: 4
        page_pattern: '{url}/page-{page}' # Custom URL format
        selectors:
          article_list: 'div.culture-post'

      # 5. Standard scroll with partial overrides
      health:
        enabled: true
        type: 'scroll'
        url: 'https://www.kurdistan24.net/ckb/health'
        scrolls: 10
        selectors:
          article_list: 'article.health-article'
          article_title: 'h1.health-title'
          # Other selectors inherited from defaults

      # 6. Pagination with extra fields
      opinion:
        enabled: true
        type: 'pagination'
        url: 'https://www.kurdistan24.net/ckb/opinion'
        pages: 3
        selectors:
          # Multiple fallback selectors for different article layouts
          article_title:
            - 'h1.opinion-title'
            - type: 'xpath'
              value: "//h1[@class='title']"
            - 'h1'

          article_content:
            - 'div.opinion-body'
            - 'div.article-content'
            - 'article > div'

          article_author:
            - 'div.author-name'
            - 'span.byline'
            - type: 'xpath'
              value: "//span[contains(@class, 'author')]"

          article_author_bio: 'div.author-bio'
          article_category: 'span.opinion-tag'

      # 7. Mixed content with filtering
      multimedia:
        enabled: true
        type: 'scroll'
        url: 'https://www.kurdistan24.net/ckb/multimedia'
        scrolls: 12
        selectors:
          article_list: 'div.media-item'
          article_link: 'a.media-link'
          # Filter to only text articles, skip videos
          exclude_pattern: 'video-'

      # 8. Interview category (like opinion but different selectors)
      interview:
        enabled: true
        type: 'pagination'
        url: 'https://www.kurdistan24.net/ckb/interview'
        pages: 2
        selectors:
          article_list: 'div.interview-card'
          article_title: 'h2.interview-title'
          article_author: 'span.interviewee'
          article_date: 'div.interview-date'
```

**Key Features Demonstrated:**

- **5 different pagination types**: pagination, infinite_scroll, load_more, numbered_pages, scroll
- **Partial overrides**: Health category overrides only 2 selectors
- **Complete overrides**: Sport category has entirely different structure
- **Extra fields**: Opinion/Interview add author information
- **Custom behaviors**: Multimedia excludes video content
- **URL patterns**: Culture uses custom page URL format
- **Loading indicators**: Economy waits for spinner to disappear
      technology:
        enabled: true
        url: "https://newwebsite.com/tech"
        pages: 2
  selectors:
  article_list: "div.article"
  article_link: "a"
  article_title: "h1"
  article_content: "div.content"

````

**Benefits:**
- ✅ Add new websites without writing code
- ✅ Enable/disable categories via config
- ✅ Easy to adjust scraping parameters
- ✅ Centralized selector management
- ✅ Version control friendly

---

## 🔧 Category-Specific Configuration System

### Philosophy: Simple Defaults + Flexible Overrides

The configuration system follows a **three-tier resolution hierarchy**:

1. **Category-specific selectors** (highest priority) - When a category needs unique selectors
2. **Website default selectors** (medium priority) - Shared across most categories on the site
3. **Common defaults** (fallback) - Standard HTML patterns

This approach enables:
- ✅ **80% of categories**: Just specify URL, inherit all defaults
- ✅ **15% of categories**: Override 1-3 selectors for minor differences
- ✅ **5% of categories**: Complete custom configuration for unique structures

### Supported Pagination Types

Each category can specify its own pagination behavior:

| Type | Description | Use Case |
|------|-------------|----------|
| `pagination` | Traditional page numbers | Static sites with page=N URLs |
| `scroll` | Scroll to load more | Simple infinite scroll |
| `infinite_scroll` | Advanced scroll with loading | AJAX-based content loading |
| `load_more` | Click button to load | Sites with "Load More" buttons |
| `numbered_pages` | URL pattern pages | Sites with /page-1, /page-2 format |

### Wait Times and Timing Configuration

Different websites have different loading speeds. The system supports **three levels of wait configuration**:

#### 1. Global Default Wait Times (in code)
```python
DEFAULT_WAIT_TIMES = {
    'page_load': 3,          # Wait after navigating to page
    'after_scroll': 2,       # Wait after scrolling
    'after_click': 1,        # Wait after clicking buttons
    'element_timeout': 10,   # Max wait for elements to appear
    'between_articles': 0.5, # Delay between article scraping
}
````

#### 2. Website-Level Wait Times (in YAML)

Override defaults for the entire website:

```yaml
rudaw:
  name: 'Rudaw'
  base_url: 'https://rudaw.net'

  # Rudaw is fast - use shorter waits
  wait_times:
    page_load: 2
    after_scroll: 1.5
    after_click: 0.5
    element_timeout: 8
    between_articles: 0.3
```

#### 3. Category-Level Wait Times (in YAML)

Override for specific categories that load differently:

```yaml
kurdsat:
  name: 'Kurdsat'

  # Default wait times for most categories
  wait_times:
    page_load: 3
    after_scroll: 2
    element_timeout: 10

  categories:
    politics:
      type: 'scroll'
      url: 'https://kurdsat.tv/politics'
      # Uses website defaults

    technology:
      type: 'infinite_scroll'
      url: 'https://kurdsat.tv/tech'
      # Override: tech section is slower
      wait_times:
        after_scroll: 4 # Tech loads slowly
        element_timeout: 15 # Give AJAX time to complete
```

### Wait Strategies: Manual vs Selector-Based

#### Strategy 1: Manual Wait Times

Simple time-based delays:

```yaml
categories:
  news:
    type: 'scroll'
    url: 'https://site.com/news'
    scrolls: 10
    wait_times:
      after_scroll: 3 # Always wait 3 seconds
```

**Pros:** Simple, predictable  
**Cons:** May be too slow or too fast

#### Strategy 2: Wait for Selector (Recommended)

Wait for specific elements to appear/disappear:

```yaml
categories:
  news:
    type: 'scroll'
    url: 'https://site.com/news'
    scrolls: 10
    wait_for:
      element: 'div.loading-spinner'
      condition: 'invisible' # Wait until spinner disappears
      timeout: 10 # Max 10 seconds
      fallback_wait: 1 # If element not found, wait 1 second anyway
```

**Pros:** Adaptive, faster when site is fast, waits when needed  
**Cons:** Requires correct selector

**How it works:**

1. **Try selector-based wait first** (priority)
2. **If selector found**: Wait for condition (up to timeout)
3. **If selector not found or timeout**: Use fallback_wait
4. **Result**: Always waits, but intelligently

#### Strategy 3: Combined (Best Practice)

Use both for maximum reliability:

```yaml
categories:
  economy:
    type: 'infinite_scroll'
    url: 'https://site.com/economy'
    scrolls: 15

    # Baseline manual waits (used as fallback)
    wait_times:
      page_load: 2 # Used if no wait_for specified
      after_scroll: 1.5 # Used if no wait_for specified
      element_timeout: 12

    # Smart selector-based wait (priority)
    wait_for:
      element: 'div.ajax-loader'
      condition: 'invisible'
      timeout: 10
      fallback_wait: 2 # If wait_for fails, use this instead of wait_times
```

**Wait Priority Flow:**

```
1. Check if 'wait_for' is configured
   ├─ YES: Try selector-based wait
   │   ├─ Selector found & condition met → Continue
   │   └─ Failed → Use wait_for.fallback_wait
   │
   └─ NO: Use wait_times.page_load (manual wait)
```

**Best of both worlds:**

- ✅ Fast sites: Selector-based wait completes quickly
- ✅ Slow sites: Selector-based wait adapts automatically
- ✅ Broken selectors: Fallback wait ensures script doesn't hang
- ✅ No selector config: Manual waits work as before

### Wait Conditions

The `wait_for.condition` field supports multiple strategies:

| Condition      | Description                 | Use Case                              |
| -------------- | --------------------------- | ------------------------------------- |
| `visible`      | Element is visible on page  | Wait for content to appear            |
| `invisible`    | Element is hidden/removed   | Wait for loading spinner to disappear |
| `present`      | Element exists in DOM       | Check if element loaded               |
| `clickable`    | Element can be clicked      | Wait before clicking button           |
| `count`        | Specific number of elements | Wait for N articles to load           |
| `text_present` | Text appears in element     | Wait for content to populate          |

### Complete Wait Configuration Examples

#### Example 1: Fast Static Site (Manual Waits Only)

```yaml
xendan:
  name: 'Xendan'
  base_url: 'https://xendan.org'

  # Fast site - minimal manual waits, no wait_for needed
  wait_times:
    page_load: 1.5
    after_click: 0.3
    element_timeout: 5
    between_articles: 0.1

  categories:
    news:
      type: 'pagination'
      url: 'https://xendan.org/news'
      pages: 5
      # Uses wait_times.page_load (1.5s) - no wait_for configured
```

**Wait Flow:**

```
Page Load → wait_times.page_load (1.5s) → Scrape
```

#### Example 2: Slow Dynamic Site (Selector-Based Waits + Fallback)

```yaml
nrt:
  name: 'NRT'
  base_url: 'https://nrttv.com'

  # Baseline manual waits (used as fallback)
  wait_times:
    page_load: 5 # Fallback if no wait_for
    after_scroll: 3 # Fallback if no wait_for
    element_timeout: 15
    between_articles: 1

  categories:
    politics:
      type: 'scroll'
      url: 'https://nrttv.com/politics'
      scrolls: 10

      # Smart wait (priority) - tries this first
      wait_for:
        element: 'div.article-loaded'
        condition: 'visible'
        timeout: 15
        fallback_wait: 4 # If selector fails, use this (not wait_times)
```

**Wait Flow:**

```
Page Load:
1. Try wait_for (selector: div.article-loaded, visible, 15s timeout)
   ├─ Success → Continue immediately when visible
   └─ Failed → Use fallback_wait (4s)

After Scroll:
1. Try wait_for (selector: div.article-loaded, visible, 15s timeout)
   ├─ Success → Continue immediately when visible
   └─ Failed → Use fallback_wait (4s)

Note: wait_times.after_scroll (3s) is NOT used because wait_for is configured
```

#### Example 3: AJAX-Heavy Site with Loading Indicators

```yaml
kurdistan24:
  name: 'Kurdistan24'
  base_url: 'https://kurdistan24.net'

  # Baseline waits (fallback only)
  wait_times:
    page_load: 3
    element_timeout: 12

  categories:
    economy:
      type: 'infinite_scroll'
      url: 'https://kurdistan24.net/economy'
      scrolls: 15

      # Smart wait for spinner (priority)
      wait_for:
        element: 'div.spinner'
        condition: 'invisible' # Wait for spinner to disappear
        timeout: 10
        fallback_wait: 2 # If spinner selector fails
```

**Wait Flow:**

```
After Each Scroll:
1. Try wait_for:
   ├─ Find spinner element
   ├─ Wait until invisible (max 10s)
   │  ├─ Spinner disappears in 0.5s → Continue (fast!)
   │  ├─ Spinner disappears in 8s → Continue (adapted!)
   │  └─ Timeout after 10s → Use fallback_wait (2s)
   └─ Spinner not found → Use fallback_wait (2s)

Result: Adapts to actual loading speed automatically
```

#### Example 4: Multiple Wait Conditions

```yaml
sharpress:
  name: 'Sharpress'
  base_url: 'https://sharpress.net'

  # Manual waits (fallback only, since wait_for is used)
  wait_times:
    page_load: 4
    between_articles: 1 # Critical for Chrome driver stability

  categories:
    politics:
      type: 'scroll'
      url: 'https://sharpress.net/politics'
      scrolls: 10

      # Multiple smart wait strategies (executed in order)
      wait_for:
        # Step 1: Wait for loading indicator to disappear
        - element: 'div.loading'
          condition: 'invisible'
          timeout: 10
          fallback_wait: 2

        # Step 2: Wait for minimum article count
        - element: 'article.post'
          condition: 'count'
          count: 10 # Wait until at least 10 articles loaded
          timeout: 15
          fallback_wait: 1

        # Step 3: Wait for content to populate
        - element: 'div.content'
          condition: 'text_present'
          timeout: 5
          fallback_wait: 1
```

**Wait Flow:**

```
After Each Scroll:
1. Wait condition 1: div.loading invisible
   ├─ Try: Find spinner and wait until invisible (max 10s)
   └─ Fail → fallback_wait: 2s

2. Wait condition 2: article.post count >= 10
   ├─ Try: Check article count every 0.5s (max 15s)
   └─ Fail → fallback_wait: 1s

3. Wait condition 3: div.content has text
   ├─ Try: Check if text present (max 5s)
   └─ Fail → fallback_wait: 1s

Total: Adapts between 0.1s (instant) to 30s (all timeouts + fallbacks)
```

### Wait Time Resolution Hierarchy

**Priority (highest to lowest):**

1. Category-level `wait_times` → Most specific
2. Website-level `wait_times` → Moderate specificity
3. Global defaults in code → Fallback

**Example resolution:**

```yaml
# Global default: page_load = 3

rudaw:
  wait_times:
    page_load: 2 # Override global

  categories:
    economy:
      # Uses: page_load = 2 (from website)
      wait_times:
        after_scroll: 1.5

    technology:
      # Uses: page_load = 4 (category override)
      wait_times:
        page_load: 4
        after_scroll: 3
```

### Wait Strategy Priority: Selector vs Manual

**The system uses a TWO-TIER PRIORITY system for each wait point:**

#### Priority 1: Selector-Based Wait (if configured)

If `wait_for` is configured, use it:

```yaml
wait_for:
  element: 'div.spinner'
  condition: 'invisible'
  timeout: 10
  fallback_wait: 2 # Used if selector fails
```

**Behavior:**

- ✅ **Selector found & condition met**: Continue immediately (adaptive!)
- ❌ **Selector not found or timeout**: Use `fallback_wait`

#### Priority 2: Manual Wait (if no wait_for)

If `wait_for` is NOT configured, use manual wait:

```yaml
wait_times:
  page_load: 3 # Used as fallback
```

**Behavior:**

- Always waits the specified time (fixed delay)

#### Complete Priority Flow Diagram

```
┌─────────────────────────────────────┐
│  Need to wait (page load, scroll,  │
│  click, etc.)                       │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌──────────────┐
        │ wait_for     │
        │ configured?  │
        └──────┬───────┘
               │
       ┌───────┴────────┐
       │                │
     YES               NO
       │                │
       ▼                ▼
┌──────────────┐  ┌─────────────────┐
│ Try selector │  │ Use wait_times  │
│ based wait   │  │ (manual delay)  │
└──────┬───────┘  └─────────────────┘
       │
       ▼
┌──────────────┐
│ Selector     │
│ found &      │
│ condition    │
│ met?         │
└──────┬───────┘
       │
   ┌───┴────┐
   │        │
  YES      NO
   │        │
   │        ▼
   │   ┌─────────────────┐
   │   │ Use fallback_   │
   │   │ wait from       │
   │   │ wait_for config │
   │   └─────────────────┘
   │
   ▼
┌──────────────┐
│  Continue    │
└──────────────┘
```

#### Configuration Examples by Priority

**Example 1: Selector-based wait (Priority 1)**

```yaml
categories:
  news:
    type: 'scroll'
    url: 'https://site.com/news'
    wait_times:
      after_scroll: 3 # NOT USED (wait_for configured)

    wait_for: # USED (priority)
      element: 'div.spinner'
      condition: 'invisible'
      timeout: 10
      fallback_wait: 2
```

**Result:** Uses `wait_for`, ignores `wait_times.after_scroll`

**Example 2: Manual wait (Priority 2)**

```yaml
categories:
  news:
    type: 'scroll'
    url: 'https://site.com/news'
    wait_times:
      after_scroll: 3 # USED (no wait_for)
```

**Result:** Uses `wait_times.after_scroll` (3s fixed delay)

**Example 3: Mixed (some actions use selector, others use manual)**

```yaml
categories:
  news:
    type: 'scroll'
    url: 'https://site.com/news'

    wait_times:
      page_load: 2 # USED (no wait_for for initial load)
      between_articles: 1 # USED (no wait_for for this action)

    wait_for: # USED for after_scroll only
      element: 'div.spinner'
      condition: 'invisible'
      timeout: 10
      fallback_wait: 1.5
```

**Result:**

- Initial page load: Uses `wait_times.page_load` (2s)
- After each scroll: Uses `wait_for` (adaptive)
- Between articles: Uses `wait_times.between_articles` (1s)

### Why This Design?

✅ **Adaptive Performance**: Selector-based waits adapt to actual loading speed  
✅ **Reliability**: Fallback waits ensure script doesn't hang on broken selectors  
✅ **Backward Compatible**: Sites without `wait_for` use familiar manual waits  
✅ **Best Practices**: Encourages selector-based waits (faster, smarter)  
✅ **Gradual Migration**: Can add `wait_for` to slow categories incrementally

### Selector Types: CSS vs XPath

The system supports both **CSS selectors** and **XPath expressions**, giving you flexibility based on the website structure.

#### Configuration Formats

**Single Selector - Shorthand (defaults to CSS):**

```yaml
selectors:
  article_title: 'h1.title'
  article_content: 'div.content'
```

**Single Selector - Explicit format:**

```yaml
selectors:
  article_title:
    type: 'css'
    value: 'h1.title'
  article_content:
    type: 'xpath'
    value: "//div[@class='content']"
```

**Fallback Chain - Multiple Selectors (NEW!):**

```yaml
selectors:
  # Try selectors in order until one succeeds
  article_title:
    - type: 'css'
      value: 'h1.main-title' # Try this first
    - type: 'xpath'
      value: "//h1[@class='title']" # Try this second
    - 'h1' # Try this third (shorthand CSS)

  article_content:
    - 'div.article-body' # Try first
    - 'div.entry-content' # Try second
    - 'article > div' # Try third
    - type: 'xpath'
      value: "//article//div[@class='text']" # Try fourth
```

**How Fallback Chains Work:**

1. System tries first selector
2. If element found AND not empty → Use it ✅
3. If element not found OR empty → Try next selector
4. Repeat until selector succeeds or chain exhausted
5. If all fail → Return empty/None

**Why Use Fallback Chains?**

- ✅ Different article layouts on same website
- ✅ Website redesigns (old + new structure)
- ✅ Multiple content types (news vs opinion vs interview)
- ✅ Graceful degradation
- ✅ Higher success rate

#### Real-World Fallback Examples

**Example 1: News Site with Multiple Layouts**

```yaml
nrt:
  name: 'NRT'
  selectors:
    # Collection page - single selector
    article_list: 'article.post'
    article_link: 'a'

    # Article page - fallback chain (different layouts)
    article_title:
      - 'h1.article-headline' # New layout
      - 'h1.post-title' # Old layout
      - type: 'xpath'
        value: "//div[@class='header']//h1" # Alternative
      - 'h1' # Last resort

    article_content:
      - 'div.article__body' # New layout
      - 'div.entry-content' # Old layout
      - 'div.post-content' # Alternative
      - type: 'xpath'
        value: "//article//div[contains(@class, 'content')]"

    article_author:
      - 'span.author-name' # Primary
      - 'div.byline' # Alternative
      - type: 'xpath'
        value: "//span[contains(text(), 'نووسەر:')]/following-sibling::span"
```

**Example 2: Mixed Content Types**

```yaml
rudaw:
  categories:
    # Regular news uses default selectors
    kurdistan:
      url: 'https://rudaw.net/kurdistan'
      type: 'scroll'

    # Opinion has different structure - use fallbacks
    opinion:
      url: 'https://rudaw.net/opinion'
      type: 'pagination'
      selectors:
        article_title:
          - 'h1.opinion-headline'
          - 'h1.interview-title' # Sometimes interviews
          - 'h1'

        article_content:
          - 'div.opinion-body'
          - 'div.interview-body'
          - 'div.article-content'

        # Always try to find author
        article_author:
          - 'span.opinion-author'
          - 'div.author-name'
          - type: 'xpath'
            value: "//div[@class='meta']//span[@class='name']"
          - type: 'xpath'
            value: "//span[contains(text(), 'by')]/following-sibling::span"
```

**Example 3: Website Redesign Transition**

```yaml
khak:
  name: 'Khak News'
  selectors:
    # Website is transitioning from old to new design
    # Support both during migration period
    article_list:
      - 'div.article-card-v2' # New design
      - 'div.post-card' # Old design

    article_title:
      - 'h1.article-title-new' # New design
      - 'h1.entry-title' # Old design
      - 'h1' # Fallback

    article_content:
      - 'div.article-body-v2' # New design
      - 'div.post-content' # Old design

    article_date:
      - 'time.published-date' # New design
      - 'span.date' # Old design
      - type: 'xpath'
        value: '//time[@datetime]' # Look for any time element
```

**Example 4: Kurdish Text Matching with Fallbacks**

```yaml
awene:
  name: 'Awene'
  categories:
    politics:
      selectors:
        # Try specific Kurdish class names first
        article_content:
          - 'div.ناوەرۆک-وتار' # Kurdish class name
          - 'div.article-body-ku' # Kurdish suffix
          - 'div.article-body' # Generic
          - type: 'xpath'
            value: "//div[contains(@lang, 'ku')]" # Has Kurdish lang
          - type: 'xpath'
            value: "//article//div[contains(., 'هەواڵ')]" # Contains Kurdish text

        article_author:
          - type: 'xpath'
            value: "//span[contains(text(), 'نووسەر:')]" # "Author:" in Kurdish
          - 'span.author'
          - type: 'xpath'
            value: "//div[@class='meta']/span[1]" # First span in meta
```

**Mixed approach (best practice):**

```yaml
khak:
  name: 'Khak'
  base_url: 'https://khak.news'

  selectors:
    # CSS for simple selections
    article_list: 'div.article-card'
    article_link: 'a'
    article_date: 'time'

    # XPath for complex selections
    article_title:
      type: 'xpath'
      value: "//h1[not(contains(@class, 'advertisement'))]"

    # CSS for direct children
    article_paragraphs: 'div.article-body > p'

    # XPath for attribute matching
    load_more_button:
      type: 'xpath'
      value: "//button[@data-action='load-more' and not(@disabled)]"

  categories:
    politics:
      enabled: true
      url: 'https://khak.news/politics'
      type: 'pagination'
      pages: 3
      selectors:
        # Override with XPath for complex structure
        article_list:
          type: 'xpath'
          value: "//section[@id='politics']//article[not(contains(@class, 'sponsored'))]"
```

#### Selector Helper Methods

| Scenario                     | Recommended | Example                                      |
| ---------------------------- | ----------- | -------------------------------------------- |
| Simple class/ID selection    | **CSS**     | `div.article`                                |
| Direct child selection       | **CSS**     | `div.content > p`                            |
| Attribute-based selection    | **CSS**     | `a[href*='news']`                            |
| Complex hierarchy navigation | **XPath**   | `//div[@id='main']//article[position()>1]`   |
| Text content matching        | **XPath**   | `//h1[contains(text(), 'Breaking')]`         |
| Parent/sibling navigation    | **XPath**   | `//a[@class='link']/parent::div`             |
| Multiple conditions          | **XPath**   | `//div[@class='post' and @data-type='news']` |
| Positional selection         | **XPath**   | `//article[last()]` or `//li[position()>3]`  |

#### CSS Selector Examples

```yaml
# Simple selections
article_list: 'article'
article_title: 'h1'
article_link: 'a.read-more'

# Class combinations
article_item: 'div.post.featured'

# Direct children
article_paragraphs: 'div.content > p'

# Attribute selectors
external_links: "a[target='_blank']"
news_links: "a[href*='/news/']"

# Pseudo-selectors
first_article: 'article:first-child'
even_items: 'div.item:nth-child(even)'
```

#### XPath Selector Examples

```yaml
# Text matching
article_title:
  type: 'xpath'
  value: "//h1[contains(text(), 'خه‌به‌ر')]"

# Attribute conditions
featured_articles:
  type: 'xpath'
  value: "//article[@data-featured='true']"

# Multiple conditions
news_posts:
  type: 'xpath'
  value: "//div[@class='post' and @data-category='news']"

# Parent navigation
article_container:
  type: 'xpath'
  value: "//a[@class='permalink']/parent::div"

# Sibling navigation
next_button:
  type: 'xpath'
  value: "//div[@class='current-page']/following-sibling::a[1]"

# Position-based
last_paragraph:
  type: 'xpath'
  value: "//div[@class='content']/p[last()]"

# Complex hierarchy
nested_content:
  type: 'xpath'
  value: "//div[@id='main']//section[@class='articles']//article[position()>1]/div[@class='body']"
```

#### Real-World Example: Mixed Selectors

```yaml
khak:
  name: 'Khak'
  base_url: 'https://khak.news'

  selectors:
    # CSS for simple selections
    article_list: 'div.article-card'
    article_link: 'a'
    article_date: 'time'

    # XPath for complex selections
    article_title:
      type: 'xpath'
      value: "//h1[not(contains(@class, 'advertisement'))]"

    # CSS for direct children
    article_paragraphs: 'div.article-body > p'

    # XPath for attribute matching
    load_more_button:
      type: 'xpath'
      value: "//button[@data-action='load-more' and not(@disabled)]"

  categories:
    politics:
      enabled: true
      url: 'https://khak.news/politics'
      type: 'pagination'
      pages: 3
      selectors:
        # Override with XPath for complex structure
        article_list:
          type: 'xpath'
          value: "//section[@id='politics']//article[not(contains(@class, 'sponsored'))]"
```

#### Selector Helper Methods

The scraper will provide helper methods to find elements:

```python
def find_element(self, selector_config, context=None):
    """Find element using CSS or XPath"""
    if isinstance(selector_config, str):
        # Shorthand - defaults to CSS
        return (context or self.driver).find_element(By.CSS_SELECTOR, selector_config)

    selector_type = selector_config.get('type', 'css')
    selector_value = selector_config['value']

    if selector_type == 'css':
        return (context or self.driver).find_element(By.CSS_SELECTOR, selector_value)
    elif selector_type == 'xpath':
        return (context or self.driver).find_element(By.XPATH, selector_value)

def find_elements(self, selector_config, context=None):
    """Find multiple elements using CSS or XPath"""
    if isinstance(selector_config, str):
        return (context or self.driver).find_elements(By.CSS_SELECTOR, selector_config)

    selector_type = selector_config.get('type', 'css')
    selector_value = selector_config['value']

    if selector_type == 'css':
        return (context or self.driver).find_elements(By.CSS_SELECTOR, selector_value)
    elif selector_type == 'xpath':
        return (context or self.driver).find_elements(By.XPATH, selector_value)
```

### Selector Override Examples

**Scenario 1: Different collection page structure**

```yaml
economy:
  type: 'pagination'
  url: 'https://site.com/economy'
  pages: 3
  selectors:
    article_list: 'div.business-card' # Override collection selector
    article_link: 'a.bus-link'
    # Article page uses default selectors
```

**Scenario 2: Different article page structure**

```yaml
sport:
  type: 'pagination'
  url: 'https://site.com/sport'
  pages: 3
  selectors:
    # Collection page uses defaults
    article_title: 'h2.sport-headline' # Override article page
    article_content: 'div.sport-body'
    article_paragraphs: 'div.sport-body p'
```

**Scenario 3: Completely different structure**

```yaml
multimedia:
  type: 'load_more'
  url: 'https://site.com/media'
  clicks: 5
  selectors:
    # Collection page
    article_list: 'div.media-card'
    article_link: 'a.media-link'
    load_more_button: 'button.load-media'
    # Article page
    article_title: 'h1.media-title'
    article_content: 'div.media-text'
    article_paragraphs: 'div.media-text > p'
```

**Scenario 4: Extra fields for specific categories**

```yaml
opinion:
  type: 'pagination'
  url: 'https://site.com/opinion'
  pages: 3
  selectors:
    article_author: 'div.author-name' # Extra field
    article_author_bio: 'div.author-bio' # Extra field
    article_category: 'span.opinion-tag'
    # Standard selectors inherited
```

### Implementation Example

The `get_selector()` method handles both CSS and XPath:

```python
def get_selector(self, selector_name: str, category_config: Dict = None):
    """
    Three-tier selector resolution supporting both CSS and XPath:
    1. Category-specific (highest priority)
    2. Website default
    3. Common default (lowest priority)

    Returns: Dict with 'type' and 'value', or string (defaults to CSS)
    """
    # 1. Check category-specific selectors
    if category_config and 'selectors' in category_config:
        if selector_name in category_config['selectors']:
            selector = category_config['selectors'][selector_name]
            return self._normalize_selector(selector)

    # 2. Fall back to website default
    if selector_name in self.selectors:
        selector = self.selectors[selector_name]
        return self._normalize_selector(selector)

    # 3. Fall back to common defaults (always CSS)
    defaults = {
        'article_list': 'article',
        'article_link': 'a',
        'article_title': 'h1',
        'article_content': 'div.content',
        'article_paragraphs': 'div.content p',
    }
    default_value = defaults.get(selector_name, '')
    return {'type': 'css', 'value': default_value}

def _normalize_selector(self, selector):
    """
    Convert selector to standard format
    Supports: string, dict, or list (fallback chain)
    """
    if isinstance(selector, str):
        # Shorthand - defaults to CSS
        return {'type': 'css', 'value': selector}
    elif isinstance(selector, dict) and 'type' in selector:
        # Explicit format (single selector)
        return {
            'type': selector.get('type', 'css'),
            'value': selector.get('value', '')
        }
    elif isinstance(selector, list):
        # Fallback chain - normalize each selector in the list
        normalized_chain = []
        for sel in selector:
            if isinstance(sel, str):
                normalized_chain.append({'type': 'css', 'value': sel})
            elif isinstance(sel, dict):
                normalized_chain.append({
                    'type': sel.get('type', 'css'),
                    'value': sel.get('value', '')
                })
        return normalized_chain
    return {'type': 'css', 'value': ''}

def find_element(self, selector_config, context=None):
    """
    Find single element using CSS or XPath
    Supports fallback chains - tries each selector until one succeeds
    """
    selector = self._normalize_selector(selector_config)
    ctx = context or self.driver

    # Handle fallback chain
    if isinstance(selector, list):
        for sel in selector:
            try:
                if sel['type'] == 'xpath':
                    elem = ctx.find_element(By.XPATH, sel['value'])
                else:
                    elem = ctx.find_element(By.CSS_SELECTOR, sel['value'])

                # Check if element has content (not empty)
                if elem and (elem.text.strip() or elem.get_attribute('innerHTML').strip()):
                    return elem
            except NoSuchElementException:
                continue  # Try next selector in chain
            except Exception:
                continue  # Try next selector in chain

        # All selectors in chain failed
        raise NoSuchElementException(f"None of the selectors in chain succeeded")

    # Single selector
    if selector['type'] == 'xpath':
        return ctx.find_element(By.XPATH, selector['value'])
    else:
        return ctx.find_element(By.CSS_SELECTOR, selector['value'])

def find_elements(self, selector_config, context=None):
    """
    Find multiple elements using CSS or XPath
    Supports fallback chains - tries each selector until one returns results
    """
    selector = self._normalize_selector(selector_config)
    ctx = context or self.driver

    # Handle fallback chain
    if isinstance(selector, list):
        for sel in selector:
            try:
                if sel['type'] == 'xpath':
                    elems = ctx.find_elements(By.XPATH, sel['value'])
                else:
                    elems = ctx.find_elements(By.CSS_SELECTOR, sel['value'])

                # Return if we found elements
                if elems and len(elems) > 0:
                    return elems
            except Exception:
                continue  # Try next selector in chain

        # All selectors in chain failed, return empty list
        return []

    # Single selector
    if selector['type'] == 'xpath':
        return ctx.find_elements(By.XPATH, selector['value'])
    else:
        return ctx.find_elements(By.CSS_SELECTOR, selector['value'])

def extract_text_with_fallback(self, selector_config, context=None, default='') -> str:
    """
    Extract text from element using fallback chain
    Returns text from first successful selector, or default if all fail
    """
    try:
        elem = self.find_element(selector_config, context)
        return elem.text.strip() if elem else default
    except NoSuchElementException:
        return default
    except Exception:
        return default

def get_wait_time(self, wait_type: str, category_config: Dict = None) -> float:
    """
    Three-tier wait time resolution:
    1. Category-specific (highest priority)
    2. Website default
    3. Global default (lowest priority)
    """
    # 1. Check category-specific wait times
    if category_config and 'wait_times' in category_config:
        if wait_type in category_config['wait_times']:
            return category_config['wait_times'][wait_type]

    # 2. Fall back to website default
    if hasattr(self, 'wait_times') and wait_type in self.wait_times:
        return self.wait_times[wait_type]

    # 3. Fall back to global defaults
    defaults = {
        'page_load': 3,
        'after_scroll': 2,
        'after_click': 1,
        'element_timeout': 10,
        'between_articles': 0.5,
    }
    return defaults.get(wait_type, 1)

def wait_for_condition(self, wait_config: Dict, category_config: Dict = None):
    """
    Smart wait based on element conditions
    Supports: visible, invisible, present, clickable, count, text_present

    Priority: Try selector-based wait first, fallback to manual wait if fails
    """
    if not wait_config:
        return

    # Handle multiple wait conditions
    wait_configs = wait_config if isinstance(wait_config, list) else [wait_config]

    for config in wait_configs:
        element_selector = config.get('element')
        condition = config.get('condition', 'visible')
        timeout = config.get('timeout', 10)
        fallback_wait = config.get('fallback_wait', 0)

        # Flag to track if selector wait succeeded
        selector_wait_succeeded = False

        try:
            selector = self.get_selector(element_selector, category_config)
            by = By.XPATH if selector['type'] == 'xpath' else By.CSS_SELECTOR
            locator = (by, selector['value'])

            if condition == 'visible':
                WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located(locator)
                )
                selector_wait_succeeded = True
            elif condition == 'invisible':
                WebDriverWait(self.driver, timeout).until(
                    EC.invisibility_of_element_located(locator)
                )
                selector_wait_succeeded = True
            elif condition == 'present':
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                selector_wait_succeeded = True
            elif condition == 'clickable':
                WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable(locator)
                )
                selector_wait_succeeded = True
            elif condition == 'count':
                expected_count = config.get('count', 1)
                WebDriverWait(self.driver, timeout).until(
                    lambda d: len(d.find_elements(*locator)) >= expected_count
                )
                selector_wait_succeeded = True
            elif condition == 'text_present':
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                WebDriverWait(self.driver, timeout).until(
                    lambda d: len(d.find_element(*locator).text.strip()) > 0
                )
                selector_wait_succeeded = True
        except TimeoutException:
            # Selector wait timed out - use fallback manual wait
            if fallback_wait > 0:
                time.sleep(fallback_wait)
        except NoSuchElementException:
            # Element not found - use fallback manual wait
            if fallback_wait > 0:
                time.sleep(fallback_wait)
        except Exception as e:
            # Any other error - use fallback manual wait
            if fallback_wait > 0:
                time.sleep(fallback_wait)

def find_element(self, selector_config, context=None):
    """Find single element using CSS or XPath"""
    selector = self._normalize_selector(selector_config)
    ctx = context or self.driver

    if selector['type'] == 'xpath':
        return ctx.find_element(By.XPATH, selector['value'])
    else:
        return ctx.find_element(By.CSS_SELECTOR, selector['value'])

def find_elements(self, selector_config, context=None):
    """Find multiple elements using CSS or XPath"""
    selector = self._normalize_selector(selector_config)
    ctx = context or self.driver

    if selector['type'] == 'xpath':
        return ctx.find_elements(By.XPATH, selector['value'])
    else:
        return ctx.find_elements(By.CSS_SELECTOR, selector['value'])
```

**Usage in scraping methods:**

```python
def _scrape_with_pagination(self, base_url: str, category: str, category_config: Dict, pages: int):
    """Uses dynamic selector resolution and wait times"""
    articles = []

    for page in range(1, pages + 1):
        page_url = self._construct_page_url(base_url, page, category_config)

        if not self.safe_get(page_url):
            break

        # Smart wait: Try selector-based wait first, fallback to manual wait
        if 'wait_for' in category_config:
            # Priority 1: Wait for specific element/condition
            self.wait_for_condition(category_config['wait_for'], category_config)
        else:
            # Priority 2: Fallback to manual page load wait
            page_load_wait = self.get_wait_time('page_load', category_config)
            time.sleep(page_load_wait)

        # Get article links using category-specific selectors
        article_selector = self.get_selector('article_list', category_config)
        link_selector = self.get_selector('article_link', category_config)

        # find_elements automatically handles CSS vs XPath
        article_elements = self.find_elements(article_selector)

        for elem in article_elements[:15]:
            try:
                link = self.find_element(link_selector, context=elem)
                url = link.get_attribute('href')

                if url:
                    article_data = self.extract_article_data(url, category, category_config)
                    if article_data:
                        articles.append(article_data)

                        # Wait between articles if configured
                        between_wait = self.get_wait_time('between_articles', category_config)
                        if between_wait > 0:
                            time.sleep(between_wait)
            except:
                continue

        # Wait before next page (manual wait)
        time.sleep(self.get_wait_time('page_load', category_config))

    return articles

def _scrape_with_scroll(self, url: str, category: str, category_config: Dict, scrolls: int):
    """Scroll with adaptive wait times"""
    articles = []

    if not self.safe_get(url):
        return articles

    # Initial page load: selector-based wait first, manual fallback
    if 'wait_for' in category_config:
        self.wait_for_condition(category_config['wait_for'], category_config)
    else:
        time.sleep(self.get_wait_time('page_load', category_config))

    # Perform scrolls
    for i in range(scrolls):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Smart wait after each scroll
        if 'wait_for' in category_config:
            # Priority 1: Wait for loading indicator or content
            self.wait_for_condition(category_config['wait_for'], category_config)
        else:
            # Priority 2: Fallback to manual scroll wait
            scroll_wait = self.get_wait_time('after_scroll', category_config)
            time.sleep(scroll_wait)

    # Extract articles using category-specific selectors
    article_selector = self.get_selector('article_list', category_config)
    link_selector = self.get_selector('article_link', category_config)

    article_elements = self.find_elements(article_selector)

    for elem in article_elements:
        try:
            link = self.find_element(link_selector, context=elem)
            url = link.get_attribute('href')

            if url:
                article_data = self.extract_article_data(url, category, category_config)
                if article_data:
                    articles.append(article_data)

                    # Wait between articles
                    between_wait = self.get_wait_time('between_articles', category_config)
                    if between_wait > 0:
                        time.sleep(between_wait)
        except:
            continue

    return articles

def _scrape_with_load_more(self, url: str, category: str, category_config: Dict, clicks: int):
    """Load more with wait for button availability"""
    articles = []

    if not self.safe_get(url):
        return articles

    # Initial page load: selector-based wait first, manual fallback
    if 'wait_for' in category_config:
        self.wait_for_condition(category_config['wait_for'], category_config)
    else:
        time.sleep(self.get_wait_time('page_load', category_config))

    # Get load more button selector
    load_more_selector = self.get_selector('load_more_button', category_config)

    # Click load more button multiple times
    for i in range(clicks):
        try:
            button = self.find_element(load_more_selector)
            button.click()

            # Smart wait after click
            if 'wait_for' in category_config:
                # Priority 1: Wait for loading indicator to disappear
                self.wait_for_condition(category_config['wait_for'], category_config)
            else:
                # Priority 2: Fallback to manual click wait
                click_wait = self.get_wait_time('after_click', category_config)
                time.sleep(click_wait)
        except:
            break

    # Extract all loaded articles
    article_selector = self.get_selector('article_list', category_config)
    link_selector = self.get_selector('article_link', category_config)

    article_elements = self.find_elements(article_selector)

    for elem in article_elements:
        try:
            link = self.find_element(link_selector, context=elem)
            url = link.get_attribute('href')

            if url:
                article_data = self.extract_article_data(url, category, category_config)
                if article_data:
                    articles.append(article_data)

                    between_wait = self.get_wait_time('between_articles', category_config)
                    if between_wait > 0:
                        time.sleep(between_wait)
        except:
            continue

    return articles
```

### Benefits

✅ **Simplicity**: Most categories need zero custom configuration  
✅ **Flexibility**: Any category can override any selector  
✅ **Maintainability**: Changes to defaults affect all inheriting categories  
✅ **Clarity**: Config file clearly shows what's custom vs default  
✅ **Scalability**: Easy to add new pagination types and behaviors  
✅ **Selector Flexibility**: Mix CSS and XPath based on website structure

### Quick Reference: CSS vs XPath Decision Tree

```
Need to select elements?
│
├─ Simple class/ID?                    → Use CSS: "div.article"
├─ Direct child?                       → Use CSS: "div.content > p"
├─ Attribute equals?                   → Use CSS: "a[href='/news']"
│
├─ Contains text?                      → Use XPath: "//h1[contains(text(), 'News')]"
├─ Multiple AND conditions?            → Use XPath: "//div[@class='x' and @data-type='y']"
├─ Navigate to parent?                 → Use XPath: "//a[@class='link']/parent::div"
├─ Position-based (last, nth)?         → Use XPath: "//article[last()]"
├─ Complex hierarchy with conditions?  → Use XPath: "//div[@id='main']//article[position()>1]"
│
└─ Not sure?                           → Try CSS first, use XPath if CSS can't do it
```

### Common Kurdish Text Matching with XPath

Since you're scraping Kurdish news sites, here are useful XPath patterns:

```yaml
# Find articles with Kurdish keywords
kurdish_politics:
  type: 'xpath'
  value: "//article[contains(., 'سیاسی')]"

# Exclude advertisements in Kurdish
clean_articles:
  type: 'xpath'
  value: "//div[@class='post' and not(contains(., 'ڕیکلام'))]"

# Find specific categories
health_news:
  type: 'xpath'
  value: "//article[.//span[@class='category' and contains(text(), 'تەندروستی')]]"

# Find articles by author
author_articles:
  type: 'xpath'
  value: "//div[@class='article'][.//span[@class='author' and text()='نووسەر']]"
```

---

### 2. Enhanced Base Architecture

**Create: `scrapers/base/scraper_base.py`**

```python
"""
Enhanced base scraper with plugin architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import yaml
from pathlib import Path


@dataclass
class ScrapedArticle:
    """Structured article data"""
    url: str
    title: str
    content: str
    sentences: List[str]
    category: str
    source: str
    scraped_at: datetime
    metadata: Dict = field(default_factory=dict)


@dataclass
class ScraperResult:
    """Structured scraper results"""
    source: str
    category: str
    articles: List[ScrapedArticle]
    sentence_count: int
    success: bool
    error: Optional[str] = None
    duration: float = 0.0
    metadata: Dict = field(default_factory=dict)


class ConfigurableScraper(ABC):
    """
    Enhanced base scraper with configuration support
    """

    def __init__(self, config: Dict, headless: bool = True):
        self.config = config
        self.name = config['name']
        self.base_url = config['base_url']
        self.selectors = config.get('selectors', {})
        self.sentences: Set[str] = set()
        self.articles: List[ScrapedArticle] = []
        self.driver = None
        self.headless = headless

        # Initialize QC with custom settings if provided
        qc_config = config.get('quality_control', {})
        self.qc = SimpleQC(**qc_config)

    @classmethod
    def from_config_file(cls, config_path: str, website_name: str):
        """Factory method to create scraper from config file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        website_config = config_data['websites'][website_name]
        return cls(website_config)

    def is_category_enabled(self, category_name: str) -> bool:
        """Check if category is enabled in config"""
        categories = self.config.get('categories', {})
        category_config = categories.get(category_name, {})
        return category_config.get('enabled', False)

    def get_enabled_categories(self) -> Dict[str, Dict]:
        """Get all enabled categories"""
        categories = self.config.get('categories', {})
        return {
            key: value for key, value in categories.items()
            if value.get('enabled', False)
        }

    def scrape_all_categories(self, **kwargs) -> Dict[str, ScraperResult]:
        """Scrape all enabled categories"""
        enabled_categories = self.get_enabled_categories()

        if not enabled_categories:
            return {}

        results = {}

        for cat_name, cat_config in enabled_categories.items():
            result = self._scrape_category(cat_name, cat_config, **kwargs)
            results[cat_name] = result

        return results

    def scrape_category(self, category_name: str, **kwargs) -> ScraperResult:
        """Scrape a specific category"""
        if not self.is_category_enabled(category_name):
            return ScraperResult(
                source=self.name,
                category=category_name,
                articles=[],
                sentence_count=0,
                success=False,
                error=f"Category '{category_name}' disabled in config"
            )

        category_config = self.config['categories'][category_name]
        return self._scrape_category(category_name, category_config, **kwargs)

    @abstractmethod
    def _scrape_category(self, category_name: str, category_config: Dict, **kwargs) -> ScraperResult:
        """Implementation-specific scraping logic"""
        pass

    def get_selector(self, selector_name: str, category_config: Dict = None) -> str:
        """
        Get selector with category-specific override support.
        Looks for selector in: category config -> website config -> default
        """
        # Check category-specific selectors first
        if category_config and 'selectors' in category_config:
            if selector_name in category_config['selectors']:
                return category_config['selectors'][selector_name]

        # Fall back to website default selectors
        if selector_name in self.selectors:
            return self.selectors[selector_name]

        # Fall back to common defaults
        defaults = {
            'article_list': 'article',
            'article_link': 'a',
            'article_title': 'h1',
            'article_content': 'div.content',
            'article_paragraphs': 'p',
            'pagination_next': 'a.next',
            'load_more_button': 'button.load-more'
        }

        return defaults.get(selector_name, '')

    def extract_article_data(self, article_url: str, category: str, category_config: Dict) -> Optional[ScrapedArticle]:
        """Extract article using category-specific or default selectors"""
        try:
            if not self.safe_get(article_url):
                return None

            # Extract title using category-specific selector
            title_selector = self.get_selector('article_title', category_config)
            title_elem = self.driver.find_element(By.CSS_SELECTOR, title_selector)
            title = title_elem.text.strip()

            # Extract content paragraphs using category-specific selector
            content_selector = self.get_selector('article_paragraphs', category_config)
            paragraphs = self.driver.find_elements(By.CSS_SELECTOR, content_selector)

            sentences = []
            full_content = []

            for p in paragraphs:
                text = p.text.strip()
                if not text:
                    continue

                full_content.append(text)

                # Split into sentences
                for sent in re.split(r'[.؟!]\s+', text):
                    sent = sent.strip()
                    if self.qc.check(sent):
                        sentences.append(sent)
                        self.sentences.add(sent)

            return ScrapedArticle(
                url=article_url,
                title=title,
                content='\\n'.join(full_content),
                sentences=sentences,
                category=category,
                source=self.name,
                scraped_at=datetime.now()
            )

        except Exception as e:
            print(f"      ⚠️  Failed to extract article: {self.clean_error(e)}")
            return None
```

---

### 3. Generic Scraper Implementation

**Create: `scrapers/implementations/generic_scraper.py`**

```python
"""
Generic scraper that works with most websites via configuration
"""

from ..base.scraper_base import ConfigurableScraper, ScraperResult, ScrapedArticle
from selenium.webdriver.common.by import By
import time


class GenericScraper(ConfigurableScraper):
    """
    Generic scraper using CSS selectors from config.
    Works with 80% of Kurdish news websites!
    """

    def _scrape_category(self, category_name: str, category_config: Dict, **kwargs) -> ScraperResult:
        """Generic category scraping with category-specific configuration"""
        start_time = time.time()
        articles = []

        try:
            self.init_driver()

            category_url = category_config['url']
            category_display_name = category_config.get('name', category_name)

            print(f"\n   📂 Category: {category_display_name}")

            # Get pagination type from category config
            pagination_type = category_config.get('type', 'pagination')

            # Route to appropriate pagination handler
            if pagination_type == 'scroll':
                scrolls = category_config.get('scrolls', 10)
                articles = self._scrape_with_scroll(category_url, category_name, category_config, scrolls)

            elif pagination_type == 'infinite_scroll':
                scrolls = category_config.get('scrolls', 10)
                scroll_pause = category_config.get('scroll_pause', 2)
                articles = self._scrape_with_infinite_scroll(
                    category_url, category_name, category_config, scrolls, scroll_pause
                )

            elif pagination_type == 'pagination':
                pages = category_config.get('pages', 3)
                articles = self._scrape_with_pagination(category_url, category_name, category_config, pages)

            elif pagination_type == 'load_more':
                clicks = category_config.get('clicks', 5)
                articles = self._scrape_with_load_more(category_url, category_name, category_config, clicks)

            elif pagination_type == 'numbered_pages':
                pages = category_config.get('pages', 3)
                page_pattern = category_config.get('page_pattern', '{url}/page/{page}')
                articles = self._scrape_with_numbered_pages(
                    category_url, category_name, category_config, pages, page_pattern
                )

            else:
                # Default to simple pagination
                pages = category_config.get('pages', 3)
                articles = self._scrape_with_pagination(category_url, category_name, category_config, pages)

            sentence_count = sum(len(article.sentences) for article in articles)

            return ScraperResult(
                source=self.name,
                category=category_name,
                articles=articles,
                sentence_count=sentence_count,
                success=True,
                duration=time.time() - start_time
            )

        except Exception as e:
            return ScraperResult(
                source=self.name,
                category=category_name,
                articles=[],
                sentence_count=0,
                success=False,
                error=str(e),
                duration=time.time() - start_time
            )

    def _scrape_with_pagination(self, base_url: str, category: str, category_config: Dict, pages: int) -> List[ScrapedArticle]:
        """Generic pagination scraping with category-specific selectors"""
        articles = []

        for page in range(1, pages + 1):
            # Construct page URL (most sites use ?page=N or /page/N)
            page_pattern = category_config.get('page_pattern', '{url}?page={page}')
            if page == 1:
                page_url = base_url
            else:
                page_url = page_pattern.format(url=base_url, page=page)

            if not self.safe_get(page_url):
                break

            # Get article links using category-specific selectors
            article_selector = self.get_selector('article_list', category_config)
            link_selector = self.get_selector('article_link', category_config)

            article_elements = self.driver.find_elements(By.CSS_SELECTOR, article_selector)

            for elem in article_elements[:15]:  # Limit per page
                try:
                    link = elem.find_element(By.CSS_SELECTOR, link_selector)
                    url = link.get_attribute('href')

                    if url:
                        article_data = self.extract_article_data(url, category, category_config)
                        if article_data:
                            articles.append(article_data)
                except:
                    continue

            time.sleep(2)

        return articles

    def _scrape_with_scroll(self, url: str, category: str, category_config: Dict, scrolls: int) -> List[ScrapedArticle]:
        """Generic scroll-based scraping with category-specific selectors"""
        articles = []

        if not self.safe_get(url):
            return articles

        # Perform scrolls
        for i in range(scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Check for loading indicator if specified
            loading_selector = self.get_selector('loading_indicator', category_config)
            if loading_selector:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, loading_selector))
                    )
                except:
                    pass

        # Extract articles using category-specific selectors
        article_selector = self.get_selector('article_list', category_config)
        link_selector = self.get_selector('article_link', category_config)

        article_elements = self.driver.find_elements(By.CSS_SELECTOR, article_selector)

        for elem in article_elements:
            try:
                link = elem.find_element(By.CSS_SELECTOR, link_selector)
                url = link.get_attribute('href')

                if url:
                    article_data = self.extract_article_data(url, category, category_config)
                    if article_data:
                        articles.append(article_data)
            except:
                continue

        return articles

    def _scrape_with_infinite_scroll(self, url: str, category: str, category_config: Dict,
                                     scrolls: int, scroll_pause: float) -> List[ScrapedArticle]:
        """Infinite scroll with dynamic content loading"""
        articles = []

        if not self.safe_get(url):
            return articles

        visited_urls = set()

        for i in range(scrolls):
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for content to load
            time.sleep(scroll_pause)

            # Check for loading indicator
            loading_selector = self.get_selector('loading_indicator', category_config)
            if loading_selector:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, loading_selector))
                    )
                except:
                    pass

            # Extract newly loaded articles
            article_selector = self.get_selector('article_list', category_config)
            link_selector = self.get_selector('article_link', category_config)

            article_elements = self.driver.find_elements(By.CSS_SELECTOR, article_selector)

            for elem in article_elements:
                try:
                    link = elem.find_element(By.CSS_SELECTOR, link_selector)
                    url = link.get_attribute('href')

                    if url and url not in visited_urls:
                        visited_urls.add(url)
                        article_data = self.extract_article_data(url, category, category_config)
                        if article_data:
                            articles.append(article_data)
                except:
                    continue

        return articles

    def _scrape_with_load_more(self, url: str, category: str, category_config: Dict, clicks: int) -> List[ScrapedArticle]:
        """Generic 'Load More' button scraping with category-specific selectors"""
        articles = []

        if not self.safe_get(url):
            return articles

        # Get load more button selector from category config
        load_more_selector = self.get_selector('load_more_button', category_config)

        # Click load more button multiple times
        for i in range(clicks):
            try:
                button = self.driver.find_element(By.CSS_SELECTOR, load_more_selector)
                button.click()
                time.sleep(2)

                # Wait for loading indicator if specified
                loading_selector = self.get_selector('loading_indicator', category_config)
                if loading_selector:
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.invisibility_of_element_located((By.CSS_SELECTOR, loading_selector))
                        )
                    except:
                        pass
            except:
                break

        # Extract all loaded articles
        article_selector = self.get_selector('article_list', category_config)
        link_selector = self.get_selector('article_link', category_config)

        article_elements = self.driver.find_elements(By.CSS_SELECTOR, article_selector)

        for elem in article_elements:
            try:
                link = elem.find_element(By.CSS_SELECTOR, link_selector)
                url = link.get_attribute('href')

                if url:
                    article_data = self.extract_article_data(url, category, category_config)
                    if article_data:
                        articles.append(article_data)
            except:
                continue

        return articles
```

---

### 4. Scraper Registry & Auto-Discovery

**Create: `scrapers/registry.py`**

```python
"""
Auto-discovery and registration of scrapers
"""

from typing import Dict, Type, List
from pathlib import Path
import yaml
import importlib


class ScraperRegistry:
    """
    Centralized registry for all scrapers.
    Auto-discovers scrapers from config files.
    """

    def __init__(self, config_path: str = "scrapers/config/websites.yaml"):
        self.config_path = Path(config_path)
        self.scrapers: Dict[str, Type] = {}
        self._load_config()
        self._register_scrapers()

    def _load_config(self):
        """Load website configurations"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def _register_scrapers(self):
        """Auto-register scrapers from config"""
        for website_name, website_config in self.config['websites'].items():
            if not website_config.get('enabled', True):
                continue

            scraper_class_name = website_config.get('scraper_class', 'GenericScraper')

            try:
                # Try to import specific scraper
                module_name = f"scrapers.implementations.{website_name}_scraper"
                module = importlib.import_module(module_name)
                scraper_class = getattr(module, scraper_class_name)
            except (ImportError, AttributeError):
                # Fall back to generic scraper
                from .implementations.generic_scraper import GenericScraper
                scraper_class = GenericScraper

            self.scrapers[website_name] = scraper_class

    def get_scraper(self, website_name: str, **kwargs):
        """Get scraper instance for website"""
        if website_name not in self.scrapers:
            raise ValueError(f"Scraper for '{website_name}' not found")

        scraper_class = self.scrapers[website_name]
        website_config = self.config['websites'][website_name]

        return scraper_class(config=website_config, **kwargs)

    def list_enabled_websites(self) -> List[str]:
        """List all enabled websites"""
        return [
            name for name, config in self.config['websites'].items()
            if config.get('enabled', True)
        ]

    def get_website_info(self, website_name: str) -> Dict:
        """Get website configuration info"""
        return self.config['websites'].get(website_name, {})


# Global registry instance
registry = ScraperRegistry()
```

---

### 5. Enhanced Test Suite

**Create: `test_scrapers_v2.py`**

```python
"""
Enhanced test suite using registry and configuration
"""

from scrapers.registry import registry
import time


def test_scraper(website_name: str, categories: List[str] = None, **kwargs):
    """Test a single scraper"""
    print(f"\n{'='*70}")
    print(f"🧪 TESTING: {website_name.upper()}")
    print('='*70)

    try:
        scraper = registry.get_scraper(website_name)

        if categories:
            # Test specific categories
            for category in categories:
                result = scraper.scrape_category(category, **kwargs)
                print(f"{category}: {result.sentence_count} sentences")
        else:
            # Test all enabled categories
            results = scraper.scrape_all_categories(**kwargs)
            for cat_name, result in results.items():
                print(f"{cat_name}: {result.sentence_count} sentences")

        scraper.cleanup()

        return {'success': True, 'results': results}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {'success': False, 'error': str(e)}


def main():
    """Run tests on all enabled scrapers"""
    print("\\n" + "="*70)
    print("🚀 AUTO-DISCOVERED SCRAPER TEST SUITE")
    print("="*70)

    enabled_websites = registry.list_enabled_websites()
    print(f"\\nFound {len(enabled_websites)} enabled websites:")
    for website in enabled_websites:
        info = registry.get_website_info(website)
        print(f"  • {info['name']} - {info['base_url']}")

    results = []

    # Test each website
    for website_name in enabled_websites:
        result = test_scraper(
            website_name,
            categories=None,  # Test all enabled categories
            pages=1  # Minimal for quick test
        )
        results.append({
            'name': website_name,
            **result
        })

    # Summary
    print("\\n" + "="*70)
    print("📊 RESULTS")
    print("="*70)

    passed = sum(1 for r in results if r['success'])
    print(f"✅ Passed: {passed}/{len(results)}")

    total_sentences = sum(
        sum(res.sentence_count for res in r.get('results', {}).values())
        for r in results if r['success']
    )
    print(f"📝 Total Sentences: {total_sentences:,}")


if __name__ == "__main__":
    main()
```

---

### 6. Plugin System for Custom Logic

**Create: `scrapers/plugins/`**

```python
# scrapers/plugins/special_handling.py
"""
Plugins for websites with special requirements
"""

from typing import Callable, Dict


class PluginRegistry:
    """Registry for custom scraping plugins"""

    def __init__(self):
        self.plugins: Dict[str, Callable] = {}

    def register(self, website_name: str):
        """Decorator to register plugin"""
        def decorator(func: Callable):
            self.plugins[website_name] = func
            return func
        return decorator

    def get_plugin(self, website_name: str) -> Callable:
        """Get plugin for website"""
        return self.plugins.get(website_name)


# Global plugin registry
plugins = PluginRegistry()


# Example: Custom handling for Sharpress
@plugins.register('sharpress')
def sharpress_special_handling(scraper, driver, config):
    """
    Special handling for Sharpress pagination.
    This is only needed for sites that don't work with generic approach.
    """
    # Custom logic here
    pass


# Example: Custom handling for Kurdsat scrolling
@plugins.register('kurdsat')
def kurdsat_scroll_handling(scraper, driver, config):
    """Custom scroll handling for Kurdsat"""
    # Kurdsat-specific scroll logic
    pass
```

---

## 🚀 Migration Path

### Phase 1: Setup (Week 1)

1. Create new directory structure
2. Implement base classes
3. Create YAML config for 2-3 existing scrapers
4. Test generic scraper with those sites

### Phase 2: Migration (Week 2-3)

1. Migrate all scrapers to new system
2. Keep old scrapers as fallback
3. Run parallel testing

### Phase 3: Enhancement (Week 4)

1. Add new features (caching, rate limiting)
2. Implement plugin system
3. Add monitoring/metrics

### Phase 4: Cleanup

1. Remove old scrapers
2. Documentation
3. Training for new contributor

---

## 📊 Benefits Summary

### Adding New Website (Before):

1. Create new Python file (~200 lines)
2. Implement scrape_political()
3. Implement scrape_specialized()
4. Handle pagination logic
5. Define selectors
6. Register in test suite
7. Test and debug

**Time: 4-6 hours**

### Adding New Website (After):

1. Add entry to websites.yaml (~30 lines)
2. Test with generic scraper
3. (Optional) Add plugin if special handling needed

**Time: 15-30 minutes**

---

### Adding New Category (Before):

1. Find scraper file
2. Modify scrape_specialized()
3. Add URL and selectors
4. Test entire scraper

**Time: 30-60 minutes**

### Adding New Category (After):

1. Add 5 lines to websites.yaml
2. Set enabled: true

**Time: 2 minutes**

---

## 🔧 Advanced Features to Add

### 1. Rate Limiting

```yaml
rate_limiting:
  requests_per_minute: 30
  delay_between_requests: 2
```

### 2. Caching

```yaml
caching:
  enabled: true
  cache_duration: 24h
  cache_directory: '.cache/scrapers'
```

### 3. Retry Strategy

```yaml
retry:
  max_attempts: 3
  backoff_multiplier: 2
  exceptions:
    - ConnectionError
    - TimeoutError
```

### 4. Proxy Support

```yaml
proxy:
  enabled: false
  type: 'http'
  url: 'http://proxy.example.com:8080'
  rotation: true
```

### 5. Monitoring

```yaml
monitoring:
  enabled: true
  metrics:
    - success_rate
    - response_time
    - sentences_per_minute
  alerts:
    - type: email
      threshold: 'success_rate < 80%'
```

---

## 📝 Next Steps

1. **Review this proposal** - Discuss with team
2. **Prioritize features** - What's most important?
3. **Start small** - Migrate 2-3 scrapers first
4. **Iterate** - Add features based on feedback
5. **Document** - Create contributor guide

---

## 💡 Questions to Consider

1. Should we support multiple output formats (JSON, CSV, Database)?
2. Do we need authentication support for some sites?
3. Should we add multi-language support?
4. Do we need distributed scraping (multiple machines)?
5. Should we implement incremental scraping (only new articles)?

---

**This architecture makes it trivial to:**

- ✅ Add 10 new websites in 1 hour
- ✅ Enable/disable categories without code changes
- ✅ Share configurations across team
- ✅ A/B test different scraping strategies
- ✅ Maintain consistency across all scrapers
- ✅ Onboard new contributors quickly
