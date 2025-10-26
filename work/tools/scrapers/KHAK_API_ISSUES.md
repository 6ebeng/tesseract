# Khak TV Scraper - Investigation Report

**Date**: October 24, 2025
**Status**: ⚠️ **WEBSITE API ISSUES - Cannot scrape at this time**

## Summary

Khak TV website (khaktv.net) is currently experiencing backend API failures that prevent content extraction. The site uses modern JavaScript (Nuxt.js) for client-side rendering, and the API endpoints are returning 500 Internal Server Error.

## Investigation Details

### Website Architecture

- **Framework**: Nuxt.js (Vue.js-based)
- **Rendering**: Client-Side Rendering (CSR) - requires JavaScript execution
- **Content Delivery**: API-driven (content loaded via AJAX calls)

### Error Details

When accessing article pages:

```
500 Internal Server Error
[POST] "https://api.khaktv.net/api/items/meilisearch/feature/khak-tv/related-items?features=article&related=1&relatedLimit=4&lang=ku": 500 Internal Server Error

Error: Method App\Http\Controllers\Api\Front\MeilisearchItemController::relatedItems does not exist.
```

### Test Results

**Article List Page**: ✅ Working

- Successfully loads: `https://www.khaktv.net/article?group=5&page=1`
- Found **59 article links** across 5 pages
- Pagination working correctly

**Individual Articles**: ❌ Broken

- Tested articles: `/article/28`, `/article/29`, `/article/30`
- All return **500 Internal Server Error**
- Page renders error message instead of content
- No `<main>`, `<p>`, or content elements present

### Legacy Scraper Comparison

Legacy `khak_scraper.py` also faced this issue:

- Expected selectors: `main`, `.html-content p`, `.content p`
- Expected structure: `<main>` element with raw text (no `<p>` tags)
- Pagination: Query parameter `?group=5&page={page}`

### Configuration Status

The V4.0 config is **correctly configured**:

```yaml
pagination:
  type: 'url_template'
  page_param: 'page'

selectors:
  article_list: 'a[href*="/article/"]' # ✅ Works
  article_body: ['main', '.html-content p', '.content p', 'p'] # ❌ Cannot test

categories:
  politics:
    url: 'https://www.khaktv.net/article?group=5' # ✅ List works
  culture:
    url: 'https://www.khaktv.net/article?group=6'
```

## Root Cause

**Backend Infrastructure Issue**:

- Laravel API controller missing method: `MeilisearchItemController::relatedItems`
- This is a **server-side programming error**, not a scraper configuration issue
- The website developers need to fix their API endpoints

## Recommendation

**Action**: Mark Khak TV as temporarily disabled until website fixes their API

**Options**:

1. **Wait for fix**: Monitor the website and retry in a few days/weeks
2. **Contact website**: Report the 500 error to Khak TV technical team
3. **Skip for now**: Focus on other working websites (4/12 already working)

## Comparison with Working Sites

| Website  | Status        | Content Type | Pagination                |
| -------- | ------------- | ------------ | ------------------------- |
| Kurdsat  | ✅ Working    | News         | click_load_more           |
| Awene    | ✅ Working    | News         | url_template (page_param) |
| Balinde  | ✅ Working    | Poetry       | url_template (path)       |
| GovKRD   | ✅ Working    | Government   | url_template (page_param) |
| **Khak** | ❌ API Issues | News/TV      | N/A - Can't test          |

## Next Steps

1. Disable Khak in config (set `enabled: false`)
2. Move to next website (Lvinpress, NRT, Rudaw, etc.)
3. Periodically check Khak TV for API fix
4. Re-enable when website is fixed

## Technical Notes

- HTTP status: **200 OK** (website is up)
- Article listing: **Works** (pagination functional)
- Article content: **500 errors** (backend broken)
- Scraper config: **Correct** (ready when website fixes API)
