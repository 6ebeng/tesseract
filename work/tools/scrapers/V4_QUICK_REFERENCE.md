# Config V4 Quick Reference

## Structure Comparison

### OLD (V3)

```yaml
defaults:
  type: 'pagination'
  pages: 5
  delay: 2

selectors:
  article_list: 'a.link'
  article_link: 'a' # ❌ Removed
  article_content: '.content' # ❌ Removed
  article_paragraphs: ['.content p', 'p'] # ❌ Removed

wait:
  type: 'manual' # ❌ Changed
  seconds: 2 # ❌ Changed

categories:
  politics:
    enabled: true # ❌ Implicit now
    type: 'pagination' # ❌ Inherited
    url: '...'
    pages: 5 # ❌ Inherited
    page_param: 'page' # ❌ Not needed
```

### NEW (V4)

```yaml
pagination: # ✅ Renamed from 'defaults'
  type: 'pagination'
  pages: 5
  delay: 2

selectors:
  article_list: 'a.link'
  article_title: ['h1', 'h2']
  article_body: ['.content p', 'p'] # ✅ Merged content+paragraphs

wait:
  selector: null # ✅ Clear intent
  timeout: 2 # ✅ Renamed from 'seconds'

categories:
  politics:
    url: '...'
    # ✅ Inherits pagination and selectors
```

## Field Mapping

| Old Field             | New Field                   | Notes                         |
| --------------------- | --------------------------- | ----------------------------- |
| `defaults`            | `pagination`                | More explicit name            |
| `article_link`        | _(removed)_                 | Not needed                    |
| `article_content`     | `article_body`              | Merged with paragraphs        |
| `article_paragraphs`  | `article_body`              | Merged with content           |
| `wait.type`           | _(removed)_                 | Implicit from selector        |
| `wait.seconds`        | `wait.timeout`              | Clearer name                  |
| `wait.selector`       | `wait.selector`             | Now required (can be null)    |
| `category.enabled`    | _(removed)_                 | Implicit (enabled by default) |
| `category.type`       | `category.pagination.type`  | Nested override               |
| `category.pages`      | `category.pagination.pages` | Nested override               |
| `category.page_param` | _(removed)_                 | Not needed                    |

## Wait Strategy

### Old

```yaml
wait:
  type: 'manual' # Confusing - what does manual mean?
  seconds: 2
```

### New

```yaml
wait:
  selector: null # Clear: no selector = manual delay
  timeout: 2 # Renamed for clarity
```

Or with selector:

```yaml
wait:
  selector: '.article-list' # Wait for this element
  timeout: 3
```

## Pagination Override

### Old

```yaml
categories:
  politics:
    enabled: true
    type: 'pagination'
    pages: 5
    url: '...'

  economy:
    enabled: true
    type: 'pagination' # Must repeat everything!
    pages: 10 # Just want to change this
    url: '...'
```

### New

```yaml
categories:
  politics:
    url: '...'
    # Inherits pagination: { type: 'pagination', pages: 5 }

  economy:
    url: '...'
    pagination:
      pages: 10 # Only override what's different
```

## Selector Override

### Old

```yaml
categories:
  politics:
    enabled: true
    type: 'pagination'
    url: '...'
    # Uses website selectors

  opinion:
    enabled: true
    type: 'pagination'
    url: '...'
    # Want different selectors but had to configure everything
```

### New

```yaml
categories:
  politics:
    url: '...'
    # Inherits website selectors

  opinion:
    url: '...'
    selectors: # Override just selectors
      article_list: 'a[href*="/opinions/"]'
      article_title: ['h2.opinion-title', 'h1']
```

## Complete Pagination Types

### Standard Pagination

```yaml
pagination:
  type: 'pagination'
  pages: 5
  delay: 2
```

### Infinite Scroll

```yaml
pagination:
  type: 'infinite_scroll'
  scrolls: 20
  delay: 2
```

### Click Load More

```yaml
pagination:
  type: 'click_load_more'
  clicks: 10
  delay: 2
  load_more_button: '.load-more-btn'
```

## Migration Checklist

When updating a config to V4:

- [ ] Rename `defaults` → `pagination`
- [ ] Remove `article_link` from selectors
- [ ] Merge `article_content` + `article_paragraphs` → `article_body`
- [ ] Change `wait.type/seconds` → `wait.selector/timeout`
- [ ] Remove `enabled` from categories
- [ ] Remove `type`, `pages`, `page_param` from categories
- [ ] Add `pagination:` or `selectors:` to categories only if overriding
- [ ] Validate with `validate_config_v4.py`

## Validation

Run validation script:

```bash
python validate_config_v4.py
```

Should show:

```
✅ VALID - Perfect V4 structure!
```

For all configs.
