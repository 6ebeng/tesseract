# 🚀 Quick Reference Guide - Rudaw Scraper

## ⚡ TL;DR - Production Commands

```bash
# Standard scraping (maximum performance with whitelist)
cd /mnt/c/tesseract/work/tools/scrapers
python3 generic_scraper.py --config configs --website rudaw --category kurdistan

# Scrape multiple categories
for category in kurdistan business culture; do
    python3 generic_scraper.py --config configs --website rudaw --category $category
done

# Test with debug mode
python3 test_debug.py rudaw --category kurdistan --max-articles 2
```

## 🎯 Current Configuration (PRODUCTION READY)

**File**: `configs/rudaw.yaml`

```yaml
# Maximum performance - whitelist-only approach
url_filtering:
  whitelist:
    - 'https://www.rudaw.net/sorani/*'
    - 'https://www.rudaw.net/sorani/kurdistan/*'
    - 'https://www.rudaw.net/sorani/business/*'
    - 'https://www.rudaw.net/sorani/culture/*'
  blacklist: []
```

**Performance**: 10-20x faster, 95%+ fewer requests, only HTML loads

## 📊 What's Blocked vs Allowed

### ❌ BLOCKED (Everything Except Whitelist)

- Images (`.jpg`, `.png`, `.gif`, `.svg`)
- CSS files (`.css`)
- Fonts (`.woff`, `.woff2`, `.ttf`)
- JavaScript (`.js`)
- Tracking (`google-analytics.com`, `facebook.com/tr`)
- Ads (`doubleclick.net`)
- Social media embeds
- Video/audio files
- **All external resources**

### ✅ ALLOWED (Whitelist Only)

- Rudaw category pages (`/sorani/kurdistan`)
- Rudaw article pages (`/sorani/kurdistan/2710202522`)
- **Only HTML content**

## 🔧 Common Modifications

### Add New Category

```yaml
url_filtering:
  whitelist:
    - 'https://www.rudaw.net/sorani/*'
    - 'https://www.rudaw.net/sorani/NEWCATEGORY/*' # Add here
```

### Switch to Blacklist-Only (More Flexible)

```yaml
url_filtering:
  whitelist: [] # Empty = allow all
  blacklist:
    - '*.facebook.com'
    - '*.google-analytics.com'
```

### Disable Filtering

```yaml
# Comment out entire section
# url_filtering:
#   whitelist: []
#   blacklist: []
```

## 📈 Performance Expectations

| Scenario              | Articles | Time       | Network     | Speed Gain |
| --------------------- | -------- | ---------- | ----------- | ---------- |
| Test (2 articles)     | 2        | ~5s        | ~100 KB     | 20x faster |
| Small (50 articles)   | 50       | ~30-60s    | ~10-20 MB   | 15x faster |
| Medium (200 articles) | 200      | ~2-5 min   | ~50-100 MB  | 12x faster |
| Large (1000 articles) | 1000     | ~10-15 min | ~200-300 MB | 10x faster |

## 🐛 Troubleshooting

### No Sentences Extracted

```bash
# Check if whitelist is too restrictive
# Try with blacklist-only approach instead
```

### Slow Performance

```bash
# Verify whitelist is enabled in rudaw.yaml
# Check debug_urls: false (should be disabled)
```

### Chrome Errors

```bash
# Performance logs don't work in headless
# This is expected - use log parsing instead
```

## 📚 Documentation

- **RUDAW_OPTIMIZATION_SUMMARY.md** - Complete optimization guide
- **URL_FILTERING.md** - URL filtering system documentation
- **URL_DEBUGGING_GUIDE.md** - Advanced debugging techniques
- **ADVANCED_FEATURES.md** - Rate limiting, caching, retry, proxy

## ✅ Checklist - Before Production Run

- [ ] `debug_urls: false` in `rudaw.yaml`
- [ ] Whitelist patterns cover all needed categories
- [ ] Redis server running (for caching)
- [ ] Test with `--max-articles 2` first
- [ ] Verify sentences extracted successfully

## 🎓 Key Concepts

**Whitelist-Only** = Block everything except whitelist (maximum performance)  
**Blacklist-Only** = Allow everything except blacklist (more flexible)  
**Default** = Block images/CSS/tracking (balanced)

**Current Status**: ✅ Whitelist-only for maximum performance

---

**Last Updated**: January 27, 2025  
**Status**: Production Ready
