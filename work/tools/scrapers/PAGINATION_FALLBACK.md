# Pagination Fallback Pattern Documentation

**Version**: 2.0  
**Date**: October 24, 2025  
**Feature**: Website-level defaults with category-level overrides

---

## Overview

The scraper configuration now supports a **fallback pattern** where pagination settings can be defined at the website level and selectively overridden per category. This eliminates repetition and makes configurations more maintainable.

## Configuration Hierarchy

Settings are resolved in this order (highest to lowest priority):

1. **Category-specific settings** (explicit override)
2. **Website default pagination** (shared defaults)
3. **Hard-coded fallbacks** (last resort)

---

## Website-Level Defaults

Define common pagination behavior once:

```yaml
name: 'Example News Site'
base_url: 'https://example.com'

# Default pagination for ALL categories
pagination:
  type: 'pagination' # Standard page-by-page
  pages: 5 # Scrape 5 pages by default

selectors:
  article_list: 'article a'
  # ... other selectors
```

---

## Category Configurations

### Example 1: Use All Defaults

```yaml
categories:
  politics:
    enabled: true
    url: 'https://example.com/politics'
    # Inherits: type: pagination, pages: 5
```

**Result**: Scrapes 5 pages using standard pagination

---

### Example 2: Override Page Count Only

```yaml
categories:
  sports:
    enabled: true
    url: 'https://example.com/sports'
    pages: 10 # Override just this setting
    # Inherits: type: pagination
```

**Result**: Scrapes 10 pages using standard pagination

---

### Example 3: Different Pagination Type

```yaml
categories:
  breaking:
    enabled: true
    url: 'https://example.com/breaking'
    type: 'infinite_scroll' # Completely different
    scrolls: 20
```

**Result**: Uses infinite scroll instead of pagination

---

### Example 4: Load More Button

```yaml
categories:
  opinion:
    enabled: true
    url: 'https://example.com/opinion'
    type: 'click_load_more'
    clicks: 8
    load_more_button:
      type: 'xpath'
      value: '//button[contains(text(), "Load More")]'
```

**Result**: Clicks "Load More" button 8 times

---

## Pagination Types

### 1. Standard Pagination (`type: pagination`)

**Website Default:**

```yaml
pagination:
  type: 'pagination'
  pages: 5
```

**Category Override:**

```yaml
categories:
  news:
    url: '...'
    pages: 10 # Override page count
```

---

### 2. Infinite Scroll (`type: infinite_scroll`)

**Website Default:**

```yaml
pagination:
  type: 'infinite_scroll'
  scrolls: 20
```

**Category Override:**

```yaml
categories:
  tech:
    url: '...'
    scrolls: 15 # Fewer scrolls for this category
```

---

### 3. Click Load More (`type: click_load_more`)

**Website Default:**

```yaml
pagination:
  type: 'click_load_more'
  clicks: 10
  load_more_button: 'button.load-more'
```

**Category Override:**

```yaml
categories:
  features:
    url: '...'
    clicks: 5 # Fewer clicks
    load_more_button:
      type: 'xpath'
      value: '//button[@class="special-button"]'
```

---

## Real-World Examples

### Kurdsat TV (Mixed Pagination)

```yaml
name: 'Kurdsat TV'

# Most categories use standard pagination
pagination:
  type: 'pagination'
  pages: 3

categories:
  # News is special - uses load more button
  news:
    url: 'https://kurdsat.tv/ckb/news'
    type: 'click_load_more' # Override
    clicks: 5
    load_more_button:
      type: 'xpath'
      value: '//button[contains(text(), "زیاتر ببینە")]'

  # Health uses defaults
  health:
    url: 'https://kurdsat.tv/ckb/categories/8'
    # Inherits: type: pagination, pages: 3

  # Opinion needs more pages
  opinion:
    url: 'https://news.kurdsat.tv/ckb/opinions'
    pages: 5 # Override page count only
    # Inherits: type: pagination
```

---

### Rudaw (Uniform Infinite Scroll)

```yaml
name: 'Rudaw News'

# All categories use infinite scroll
pagination:
  type: 'infinite_scroll'
  scrolls: 20

categories:
  kurdistan:
    url: 'https://www.rudaw.net/sorani/kurdistan'
    # Inherits all defaults

  culture:
    url: 'https://www.rudaw.net/sorani/culture'
    scrolls: 15 # Override: fewer scrolls

  business:
    url: 'https://www.rudaw.net/sorani/business'
    # Inherits all defaults
```

---

## Benefits

### 1. **DRY (Don't Repeat Yourself)**

- Define common settings once
- Reduce configuration size by 50-70%
- Fewer places to update when site changes

**Before (Repetitive):**

```yaml
categories:
  cat1: { type: 'pagination', pages: 5, ... }
  cat2: { type: 'pagination', pages: 5, ... }
  cat3: { type: 'pagination', pages: 5, ... }
```

**After (DRY):**

```yaml
pagination: { type: 'pagination', pages: 5 }
categories:
  cat1: { ... }
  cat2: { ... }
  cat3: { ... }
```

---

### 2. **Maintainability**

- Change pagination behavior globally
- Easy to identify "special" categories
- Clear separation of common vs unique settings

---

### 3. **Flexibility**

- Can mix pagination types across categories
- Progressive enhancement (override only what's needed)
- Supports migration (add defaults gradually)

---

### 4. **Clarity**

```yaml
# Clear: This category is standard
culture:
  url: '...'
  # No overrides = uses defaults

# Clear: This category is special
breaking:
  url: '...'
  type: 'infinite_scroll' # Obviously different
  scrolls: 30
```

---

## Migration Guide

### Step 1: Identify Common Patterns

Look at your categories:

```yaml
categories:
  cat1: { type: 'pagination', pages: 5, ... }
  cat2: { type: 'pagination', pages: 5, ... }
  cat3: { type: 'pagination', pages: 5, ... }
  cat4: { type: 'pagination', pages: 10, ... } # Different!
```

---

### Step 2: Extract Website Defaults

Most common settings become defaults:

```yaml
pagination:
  type: 'pagination' # Used by cat1, cat2, cat3
  pages: 5 # Used by cat1, cat2, cat3
```

---

### Step 3: Keep Only Overrides

```yaml
categories:
  cat1: { url: '...' } # Inherits defaults
  cat2: { url: '...' } # Inherits defaults
  cat3: { url: '...' } # Inherits defaults
  cat4: { url: '...', pages: 10 } # Overrides pages only
```

---

### Step 4: Handle Special Cases

```yaml
categories:
  normal:
    url: '...'
    # Uses website defaults

  special:
    url: '...'
    type: 'click_load_more' # Completely different
    clicks: 8
    load_more_button: 'button.special'
```

---

## Testing

```python
from generic_scraper import GenericScraper

scraper = GenericScraper('configs')

# Test default pagination
scraper.scrape_category('website', 'normal_category')
# Uses website defaults

# Test override
scraper.scrape_category('website', 'special_category')
# Uses category-specific settings
```

---

## Implementation Details

The scraper resolves settings using this logic:

```python
# Get pagination type
category_type = category_config.get('type')
if not category_type:
    # Fallback to website default
    pagination_defaults = website_config.get('pagination', {})
    category_type = pagination_defaults.get('type', 'pagination')

# Get pagination parameters
if category_type == 'pagination':
    pages = category_config.get('pages') or \
            website_defaults.get('pages', 5)

elif category_type == 'infinite_scroll':
    scrolls = category_config.get('scrolls') or \
              website_defaults.get('scrolls', 20)

# ... etc
```

---

## Best Practices

### ✅ Do:

- Define common pagination at website level
- Override only what's different per category
- Use descriptive comments for special cases
- Keep default settings sensible (3-5 pages, 15-20 scrolls)

### ❌ Don't:

- Repeat the same settings in every category
- Mix pagination types without good reason
- Set extreme values as defaults (100 pages, 1000 scrolls)
- Override defaults unnecessarily

---

## See Also

- `configs/TEMPLATE.yaml` - Complete configuration template
- `configs/kurdsat.yaml` - Real-world example (mixed pagination)
- `configs/rudaw.yaml` - Real-world example (uniform pagination)
- `test_pagination_fallback.py` - Test script with examples

---

**Last Updated**: October 24, 2025  
**Author**: Migration Team  
**Version**: 2.0 (Fallback Pattern)
