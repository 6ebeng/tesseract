# Generic Scraper V5.0 - Complete Features Guide

**Last Updated:** 2025-10-25

## 🎯 Overview

The Generic Scraper is a YAML-driven web scraping framework that supports all major pagination types, anti-scraping protection, and flexible content extraction with intelligent defaults and fallback mechanisms.

---

## 📋 Table of Contents

1. [Basic Structure](#basic-structure)
2. [Pagination Types](#pagination-types)
3. [Selector System](#selector-system)
4. [Wait Strategies](#wait-strategies)
5. [Click-Through Navigation](#click-through-navigation)
6. [Advanced Features](#advanced-features)
7. [Configuration Examples](#configuration-examples)

---

## Basic Structure

### Minimal Configuration

```yaml
name: 'Website Name'
base_url: 'https://example.com'
enabled: true

selectors:
  article_list: 'a.article-link'
  article_title: 'h1'
  article_body: '.content p'

categories:
  news:
    url: 'https://example.com/news'
```

### Full Configuration

```yaml
name: 'Website Name'
base_url: 'https://example.com'
enabled: true # Website-level enable/disable

# Optional: Click-through navigation
click_through_navigation: true

# Optional: Language filtering
language_detection:
  enabled: true
  filter: ['ckb']

# Universal pagination (applies to all categories)
pagination:
  type: 'url_template'
  pages: 10
  delay: 2
  page_param: 'page'

# Universal selectors (inherited by all categories)
selectors:
  article_list: 'a[href*="/article/"]'
  article_title: ['h1', 'h2']
  article_body:
    selector: ['div.content p', 'p']
    multiple: true
    delimiter: '\n'

# Default wait (fallback for both page types)
wait:
  selector: null
  timeout: 3

# Collection page specific wait
collection_wait:
  selector: 'ul.articles'
  timeout: 5

# Article page specific wait
article_wait:
  selector: 'div.article-content'
  timeout: 3

categories:
  news:
    url: 'https://example.com/news'
    # Inherits all above settings

  opinion:
    url: 'https://example.com/opinion'
    enabled: false # Category-level disable
    selectors:
      article_list: 'h2 > a' # Override for this category
```

---

## Pagination Types

### 1. URL Template (`url_template` / `pagination`)

Navigates through pages by appending page numbers to URL.

```yaml
pagination:
  type: 'url_template'
  pages: 10
  delay: 2
  page_param: 'page' # Appends ?page=2, ?page=3, etc.

categories:
  news:
    url: 'https://example.com/news'
    # Will load: /news, /news?page=2, /news?page=3, ...
```

**Alternative: Path template**

```yaml
pagination:
  type: 'url_template'
  pages: 10
  delay: 2
  path: '/page/{page}' # For URLs like /news/page/2

categories:
  news:
    url: 'https://example.com/news'
    # Will load: /news, /news/page/2, /news/page/3, ...
```

### 2. Infinite Scroll (`infinite_scroll`)

Scrolls down the page to load more content.

```yaml
pagination:
  type: 'infinite_scroll'
  scrolls: 20 # Number of scroll actions
  delay: 2 # Wait between scrolls

categories:
  news:
    url: 'https://example.com/news'
```

### 3. Click Load More (`click_load_more`)

Clicks a "load more" button to reveal additional articles.

```yaml
pagination:
  type: 'click_load_more'
  clicks: 10 # Number of times to click
  delay: 2 # Wait between clicks
  load_more_button: 'a.load-more' # Button selector

categories:
  news:
    url: 'https://example.com/news'
```

### 4. Category-Level Override

```yaml
pagination:
  type: 'url_template'
  pages: 5
  page_param: 'page'

categories:
  news:
    url: 'https://example.com/news'
    # Uses url_template (inherits)

  breaking:
    url: 'https://example.com/breaking'
    pagination:
      type: 'infinite_scroll' # Override for this category
      scrolls: 15
      delay: 2
```

---

## Selector System

### Selector Formats

#### 1. Simple String

```yaml
selectors:
  article_list: 'a.article-link'
```

#### 2. Array (Fallback Chain)

Tries each selector until one returns results.

```yaml
selectors:
  article_list: ['a.article-link', 'div.post > a', 'h2 > a']
  article_title: ['h1', 'h2', '.title']
```

#### 3. Dict with Options

```yaml
selectors:
  article_body:
    selector: 'div.content p' # Can also be array
    multiple: true # Extract all matching elements
    delimiter: '\n' # Join with delimiter, then split
```

#### 4. XPath Support

Automatically detected when selector starts with `//`.

```yaml
selectors:
  article_list: '//div[@class="article"]/a'
  article_body: '//div[contains(@class, "content")]//p'
```

### Advanced Selector Examples

#### Multiple Elements with Delimiter

```yaml
selectors:
  article_body:
    selector: ['div.content > div.paragraph', 'div.content p']
    multiple: true
    delimiter: '\n'
```

**How it works:**

1. Extracts all matching elements
2. Joins text with `\n`
3. Splits back by `\n`
4. Filters: strips whitespace, removes empty, min 20 chars

#### Category-Specific Selectors

```yaml
selectors:
  # Universal selectors
  article_list: 'a.article'
  article_title: 'h1'

categories:
  opinion:
    url: 'https://example.com/opinion'
    selectors:
      # Override only article_list for this category
      article_list: 'h2.opinion-title > a'
      # article_title still uses 'h1' (inherited)
```

---

## Wait Strategies

### Wait Configuration Hierarchy

**Priority (highest to lowest):**

For collection pages:

1. Category `collection_wait`
2. Website `collection_wait`
3. Category `wait`
4. Website `wait`
5. Default (3 seconds)

For article pages:

1. Category `article_wait`
2. Website `article_wait`
3. Category `wait`
4. Website `wait`
5. Default (3 seconds)

### Wait Types

#### 1. Default Wait (Fallback)

```yaml
wait:
  selector: null # No selector wait, just delay
  timeout: 3
```

#### 2. Collection Page Wait

```yaml
collection_wait:
  selector: 'ul.articles' # Wait for this element
  timeout: 5
```

#### 3. Article Page Wait

```yaml
article_wait:
  selector: 'div.article-content'
  timeout: 3
```

Or simple number format:

```yaml
article_wait: 3 # Just wait 3 seconds
```

### Complete Wait Example

```yaml
# Default for both types
wait:
  selector: null
  timeout: 3

# Override for collection pages
collection_wait:
  selector: 'ul.posts-items'
  timeout: 5

# Override for article pages
article_wait:
  selector: 'div.entry-content'
  timeout: 3

categories:
  breaking:
    url: 'https://example.com/breaking'
    # Category-specific override
    article_wait: 8 # Slow-loading articles
```

---

## Click-Through Navigation

For websites with anti-scraping protection that requires session state preservation.

### When to Use

- Direct URL access returns 500 errors
- Website requires clicking from list page
- JavaScript click tracking validation
- Nuxt.js, Next.js with strict navigation

### Configuration

```yaml
name: 'Protected Site'
base_url: 'https://example.com'
enabled: true

# Enable click-through mode
click_through_navigation: true

pagination:
  type: 'url_template'
  pages: 5
  page_param: 'page'

selectors:
  article_list: 'a.article-link' # Must be clickable!
  article_title: 'h1'
  article_body: 'div.content p'

# Important: Configure wait times
article_wait: 8 # Wait for article to load after click
back_delay: 0.3 # Wait after back button (fast - page is cached!)

categories:
  news:
    url: 'https://example.com/news'
```

### How It Works

1. Load collection page
2. Extract article elements (not URLs)
3. Click first article → wait → extract → back button
4. Click second article → wait → extract → back button
5. Repeat for all articles

**Benefits:**

- Preserves session state and cookies
- Browser back button is **instant** (page cached)
- Mimics real user behavior
- Bypasses anti-bot protection

**See:** `docs/click_through_navigation.md` for full documentation

---

## Advanced Features

### 1. FlareSolverr (Cloudflare Bypass)

```yaml
flaresolverr:
  enabled: true
  url: 'http://localhost:8191'
  max_timeout: 60000

selectors:
  # Uses BeautifulSoup instead of Selenium
  article_list: 'a.article'
```

### 2. Enable/Disable Control

```yaml
# Disable entire website
enabled: false

categories:
  news:
    url: 'https://example.com/news'
    enabled: false # Disable specific category

  politics:
    url: 'https://example.com/politics'
    # enabled: true (default)
```

### 3. Mixed Selector Types

```yaml
selectors:
  # XPath
  article_list: '//div[@class="post"]/a'

  # CSS with fallback
  article_title: ['h1.title', 'h2.heading', '.article-title']

  # Dict with multiple + delimiter
  article_body:
    selector: ['div.content p', 'article p']
    multiple: true
    delimiter: '\n'
```

---

## Configuration Examples

### Example 1: Simple Blog

```yaml
name: 'Simple Blog'
base_url: 'https://blog.example.com'
enabled: true

pagination:
  type: 'url_template'
  pages: 5
  page_param: 'page'

selectors:
  article_list: 'a.post-link'
  article_title: 'h1'
  article_body: '.content p'

categories:
  articles:
    url: 'https://blog.example.com/articles'
```

### Example 2: News Site with Multiple Categories

```yaml
name: 'News Site'
base_url: 'https://news.example.com'
enabled: true

pagination:
  type: 'infinite_scroll'
  scrolls: 20
  delay: 2

selectors:
  article_list: ['a.article-link', 'div.post > a']
  article_title: ['h1', 'h2.title']
  article_body:
    selector: ['div.article-content p', '.content p']
    multiple: true
    delimiter: '\n'

wait:
  selector: null
  timeout: 3

collection_wait:
  selector: 'div.articles-list'
  timeout: 5

categories:
  politics:
    url: 'https://news.example.com/politics'

  economy:
    url: 'https://news.example.com/economy'
    pagination:
      scrolls: 30 # Override for this category

  opinion:
    url: 'https://news.example.com/opinion'
    selectors:
      article_list: 'h2.opinion-title > a'
```

### Example 3: Protected Site with Click-Through

```yaml
name: 'Protected Site'
base_url: 'https://protected.example.com'
enabled: true

click_through_navigation: true

pagination:
  type: 'url_template'
  pages: 10
  page_param: 'page'

selectors:
  article_list: 'div.article-card > a'
  article_title: 'div.article-header > h1'
  article_body:
    selector: 'div.article-body > p'
    multiple: true
    delimiter: '\n'

collection_wait:
  selector: 'div.articles-grid'
  timeout: 5

article_wait:
  selector: 'div.article-body'
  timeout: 8

back_delay: 0.5

categories:
  news:
    url: 'https://protected.example.com/news'
```

---

## Testing

### Test Single Website

```bash
python3 test_suite.py yariga --max-articles 5
```

### Test Multiple Websites

```bash
python3 test_suite.py yariga avanews rudaw --max-articles 10
```

### Test All Enabled Websites

```bash
python3 test_suite.py --enabled-only --max-articles 5
```

### List All Websites

```bash
python3 test_suite.py --list
```

---

## Best Practices

### 1. Start Simple

```yaml
# Minimal working config
selectors:
  article_list: 'a.article'
  article_title: 'h1'
  article_body: '.content p'

categories:
  news:
    url: 'https://example.com/news'
```

### 2. Add Fallbacks

```yaml
# Add fallback selectors
selectors:
  article_list: ['a.article', 'div.post > a', 'h2 > a']
  article_title: ['h1', 'h2', '.title']
```

### 3. Optimize Waits

```yaml
# Fast sites: short waits
wait:
  selector: null
  timeout: 2

# Slow sites: use collection_wait
collection_wait:
  selector: 'ul.articles'
  timeout: 5

# Heavy SPA: longer article_wait
article_wait: 8
```

### 4. Use Universal Settings

```yaml
# Define once at website level
pagination:
  type: 'url_template'
  pages: 5

# Applies to all categories
categories:
  news: { url: '...' }
  sports: { url: '...' }
  opinion: { url: '...' }
```

---

## Troubleshooting

### No Articles Found

1. Check `article_list` selector matches clickable links
2. Add fallback selectors
3. Increase `collection_wait` timeout
4. Check if site requires click-through navigation

### No Content Extracted

1. Check `article_body` selector matches content elements
2. Increase `article_wait` timeout
3. Try delimiter format for multiple elements
4. Check if site uses FlareSolverr

### Slow Scraping

1. Reduce delays: `delay: 1`, `back_delay: 0.3`
2. Use `collection_wait` with selector instead of timeout
3. Reduce number of pages/scrolls/clicks

---

## Version History

### V5.0 (2025-10-25)

- ✅ Added `collection_wait` and `article_wait` separation
- ✅ Added `back_delay` for click-through optimization
- ✅ Test suite with selective website testing
- ✅ Improved wait strategy documentation

### V4.0 (2025-10-24)

- ✅ Click-through navigation for anti-scraping sites
- ✅ Delimiter support for content extraction
- ✅ XPath selector support
- ✅ Universal pagination system
- ✅ Intelligent defaults and fallbacks
