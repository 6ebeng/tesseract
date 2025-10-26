# Click-Through Navigation Feature

## Overview

The **click-through navigation** feature allows the scraper to handle websites with anti-scraping protection that requires session state preservation. Instead of directly navigating to article URLs, it clicks article links from the list page and uses the browser's back button for efficient navigation.

## When to Use

Use `click_through_navigation: true` when:

1. **Direct URL access fails** - Website returns 500 errors or blocks when accessing article URLs directly
2. **Session state required** - Website checks referrer headers or requires clicking from list page
3. **JavaScript click tracking** - Website validates that users clicked through their navigation
4. **Anti-bot protection** - Nuxt.js, Next.js, or similar frameworks with strict navigation validation

## Configuration

### Basic Setup

```yaml
name: 'Example Site'
base_url: 'https://example.com'
enabled: true

# Enable click-through navigation
click_through_navigation: true

categories:
  news:
    url: 'https://example.com/news'
    type: 'infinite_scroll'

    # Important: Configure wait times
    article_wait: 3 # Wait after clicking article (for content to load)
    back_delay: 0.5 # Wait after back button (much faster - page is cached!)

    selectors:
      article_list: 'a.article-link' # Must be clickable elements
      article_title: 'h1.title'
      article_body: 'div.content p'
```

### Configuration Options

| Option                     | Type    | Default | Description                                            |
| -------------------------- | ------- | ------- | ------------------------------------------------------ |
| `click_through_navigation` | boolean | `false` | Enable click-through mode                              |
| `article_wait`             | number  | `2`     | Seconds to wait after clicking article (for page load) |
| `back_delay`               | number  | `0.5`   | Seconds to wait after back button (can be very short!) |

## How It Works

### Traditional Mode (disabled)

```
1. Load list page
2. Extract article URLs
3. Navigate to article[0] → Wait → Extract
4. Navigate to article[1] → Wait → Extract
5. Navigate to article[2] → Wait → Extract
```

### Click-Through Mode (enabled)

```
1. Load list page
2. Extract article elements (not URLs)
3. Click article[0] → Wait → Extract → Back (fast!)
4. Click article[1] → Wait → Extract → Back (fast!)
5. Click article[2] → Wait → Extract → Back (fast!)
```

### Key Benefits

1. **Session Preservation** - Maintains cookies, referrer, and navigation state
2. **Browser Cache** - Back button uses cached list page (much faster!)
3. **Anti-Bot Bypass** - Mimics real user behavior (clicking through pages)
4. **Smart Indexing** - Handles stale element references automatically

## Performance Optimization

### Back Button Speed

The browser's back button is **much faster** than reloading:

- **Page reload**: 2-5 seconds
- **Back button**: 0.2-0.5 seconds (cached!)

Configure `back_delay` appropriately:

```yaml
# Fast sites
back_delay: 0.2

# Medium sites
back_delay: 0.5

# Slow sites (lots of JavaScript)
back_delay: 1.0
```

### Article Wait Time

Configure `article_wait` based on site rendering speed:

```yaml
# Static HTML sites
article_wait: 1

# Standard JavaScript sites
article_wait: 2-3

# Heavy SPA frameworks (Nuxt.js, Next.js)
article_wait: 5-8
```

## Example: Khak TV

Khak TV requires click-through navigation because:

- Nuxt.js with anti-bot protection
- Direct URLs return 500 Internal Server Error
- Must click from list page to establish session

Configuration:

```yaml
name: 'Khak TV'
base_url: 'https://www.khaktv.net'
enabled: true
click_through_navigation: true

categories:
  politics:
    url: 'https://www.khaktv.net/article?group=5'
    type: 'url_template'
    page_param: 'page'

    article_wait: 8 # Nuxt.js needs time to render
    back_delay: 0.3 # Back button is fast!

    selectors:
      article_list: 'div.grid.grid-cols-1 > div.w-full.h-full> a[href*="/article/"]'
      article_title: ['div.py-6 > div.flex > h2.text-xl']
      article_body:
        selector: 'div.html-content > p'
        multiple: true
        delimiter: '\n'
```

## Compatibility

### Works With All Pagination Types

- ✅ `infinite_scroll` - Scrolls list, then clicks articles
- ✅ `click_load_more` - Clicks "load more", then clicks articles
- ✅ `url_template` - Loads pages via URL, then clicks articles
- ✅ `pagination` - Standard pagination, then clicks articles

### Selector Requirements

The `article_list` selector must return **clickable elements**:

✅ **Good selectors**:

```yaml
article_list: 'a.article-link'              # Direct <a> tags
article_list: 'div.card > a'                # <a> inside container
article_list: 'a:has(> .card-content)'      # <a> wrapping content
```

❌ **Bad selectors**:

```yaml
article_list: 'div.article-card'  # Not clickable (unless has onclick)
article_list: 'h2.title'          # Text element, no href
```

## Troubleshooting

### No Articles Found

```
❌ No article elements found for click-through navigation
```

**Solution**: Check that `article_list` selector returns clickable elements:

```bash
# Debug selector
python3 debug_selectors.py <website> <category>
```

### Stale Element References

The scraper handles this automatically by re-extracting elements after each back button click.

### Back Button Too Slow

If back button navigation seems slow:

1. Reduce `back_delay` to `0.2` or `0.3`
2. Check if site has heavy JavaScript on list page
3. Consider if `article_wait` is too long

### Articles Skip or Repeat

This shouldn't happen - the scraper uses index-based iteration. If it does:

1. Check for JavaScript that modifies the DOM
2. Increase `back_delay` slightly
3. Report as a bug

## Limitations

1. **Selenium Only** - Click-through mode requires Selenium (not compatible with FlareSolverr mode)
2. **Slower Than Direct** - Clicking and waiting is slower than direct URL navigation
3. **Session Dependent** - If session expires, scraping stops

## Migration Guide

### Converting Existing Config

**Before** (traditional mode):

```yaml
categories:
  news:
    url: 'https://example.com/news'
    type: 'infinite_scroll'
    scrolls: 10
```

**After** (click-through mode):

```yaml
click_through_navigation: true # Add this at website level

categories:
  news:
    url: 'https://example.com/news'
    type: 'infinite_scroll'
    scrolls: 10
    article_wait: 3 # Add wait time
    back_delay: 0.5 # Add back delay (optional)
```

### Testing

1. Enable for one category first
2. Test with `max_articles=5`
3. Verify sentences extracted
4. Tune `article_wait` and `back_delay`
5. Enable for all categories

```bash
# Test click-through navigation
python3 test_website.py <website> <category> --max-articles 5
```

## Performance Comparison

### Traditional Mode (Direct Navigation)

- Article 1: 3s (navigate + load + extract)
- Article 2: 3s (navigate + load + extract)
- Article 3: 3s (navigate + load + extract)
- **Total**: 9 seconds for 3 articles

### Click-Through Mode

- Article 1: 3s (click + load + extract) + 0.5s (back)
- Article 2: 3s (click + load + extract) + 0.5s (back)
- Article 3: 3s (click + load + extract) + 0.5s (back)
- **Total**: 10.5 seconds for 3 articles

**Difference**: Slightly slower (~15%), but enables scraping of protected sites!

## Future Enhancements

Possible improvements:

- [ ] Parallel tab mode (open articles in new tabs)
- [ ] Smart caching of list page state
- [ ] Automatic back delay optimization
- [ ] Click-through mode for FlareSolverr

## Summary

Click-through navigation is a powerful feature for scraping modern websites with anti-bot protection. While slightly slower than direct navigation, it successfully bypasses session-based restrictions by mimicking real user behavior. The browser's back button provides efficient list page navigation without full page reloads.
