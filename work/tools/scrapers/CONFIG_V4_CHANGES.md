# Config Structure V4.0 - Simplified & Clarified

## Updated: 2025-10-24

## Key Changes

### 1. ❌ Removed `article_link`

- **Before:** Had both `article_list` and `article_link`
- **After:** Only `article_list` (finds all article links directly)
- **Reason:** `article_link` was redundant

### 2. ✅ Merged `article_content` + `article_paragraphs` → `article_body`

- **Before:** Separate `article_content` and `article_paragraphs`
- **After:** Single `article_body` with fallback chain
- **Reason:** Same purpose, clearer naming

### 3. ✅ Changed `wait` structure

- **Before:** `wait: { type: 'manual', seconds: 2 }`
- **After:** `wait: { selector: null, timeout: 2 }`
- **Reason:** Clearer - either wait for selector or use manual delay

### 4. ✅ Universal `pagination` section

- **Before:** `defaults:` or per-category settings
- **After:** `pagination:` at website level, categories can override
- **Reason:** More explicit and clearer fallback

## New Structure

```yaml
name: 'Website Name'
base_url: 'https://example.com'
enabled: true

language_detection:
  enabled: true
  filter: ['ckb']

# Universal pagination (applies to ALL categories unless overridden)
pagination:
  type: 'pagination' # or 'infinite_scroll', 'click_load_more'
  pages: 5
  delay: 2

# Selectors
selectors:
  article_list: 'a[href*="/articles/"]' # Find article links
  article_title: ['h1', 'h2'] # Extract title
  article_body: ['.content p', 'p'] # Extract content (merged!)

# Wait strategy
wait:
  selector: null # CSS selector or null for manual delay
  timeout: 3 # Timeout in seconds

# Categories
categories:
  category1:
    url: 'https://example.com/cat1'
    # Inherits pagination and selectors

  category2:
    url: 'https://example.com/cat2'
    pagination: # Override pagination
      pages: 10
    selectors: # Override selectors
      article_list: 'a.special'
```

## Migration Checklist

When updating configs:

- [x] ❌ Remove `article_link` from selectors
- [x] ✅ Merge `article_content` + `article_paragraphs` → `article_body`
- [x] ✅ Change `wait.type/seconds` → `wait.selector/timeout`
- [x] ✅ Change `defaults` → `pagination` at website level
- [x] ✅ Remove `enabled`, `type`, `pages`, `page_param` from categories (use inheritance)
- [x] ✅ Categories override pagination or selectors only when needed

## Updated Files

All 14 config files updated:

1. ✅ kurdsat.yaml
2. ✅ rudaw.yaml
3. ✅ govkrd.yaml
4. ✅ sekokurd.yaml
5. ✅ sharpress.yaml
6. ✅ awene.yaml
7. ✅ khak.yaml
8. ✅ xendan.yaml
9. ✅ lvinpress.yaml
10. ✅ balinde.yaml
11. ✅ kurdistan24.yaml
12. ✅ TEMPLATE.yaml (reference)
13. ✅ MINIMAL_EXAMPLE.yaml (if exists)
14. ✅ nrt.yaml (if exists)

## Example: Kurdsat

### Before (Old Structure)

```yaml
defaults:
  type: 'pagination'
  pages: 3
  delay: 2

selectors:
  article_list: 'a[href*="/articles/"]'
  article_link: 'a' # ← Redundant!
  article_content: '.article-body' # ← Separate from paragraphs
  article_paragraphs: ['.article-body p'] # ← Redundant!

wait:
  type: 'manual' # ← Confusing!
  seconds: 3

categories:
  health:
    url: '...'
    # Implicit inheritance
```

### After (New Structure)

```yaml
pagination:
  type: 'pagination'
  pages: 3
  delay: 2

selectors:
  article_list: 'a[href*="/articles/"]'
  article_body: ['.article-body p', 'p'] # ← Merged & clear!

wait:
  selector: null # ← Clear: no selector, manual delay
  timeout: 3

categories:
  health:
    url: '...'
    # Explicit inheritance from pagination above
```

## Benefits

1. **Clearer:** `article_body` vs `article_content` + `article_paragraphs`
2. **Simpler:** No redundant `article_link`
3. **Explicit:** `wait.selector` shows intent clearly
4. **Universal:** `pagination` section shows it applies to all categories
5. **Override:** Categories can still override when needed

## Next Steps

1. ✅ Update all 14 config files (DONE)
2. ⏳ Update `generic_scraper.py` to use new structure
3. ⏳ Test all websites with new structure
4. ⏳ Update documentation
