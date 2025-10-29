# URL Filtering Status - Kurdish News Scrapers

**Last Updated:** 2025-10-28

## Overview

All site configs now have the `url_filtering` section. This document tracks which sites have populated whitelist/blacklist rules vs. empty placeholders.

---

## ✅ Fully Configured (6/14)

### 1. **Rudaw** (`rudaw.yaml`)

- **Whitelist:** 6 patterns
  - Core content: `www.rudaw.net/arabic/`, `www.rudaw.net/sorani/`
  - Assets: `assets.rudaw.net/`, `static.rudaw.net/`
  - CDN: `cdnjs.cloudflare.com/`
- **Blacklist:** 1 pattern
  - `www.googletagmanager.com` (analytics)
- **Notes:** Production-ready with debug mode enabled for ongoing refinement

### 2. **Kurdistan24** (`kurdistan24.yaml`)

- **Whitelist:** 2 patterns
  - `www.kurdistan24.net/ckb/`
  - `static.kurdistan24.net/`
- **Blacklist:** None
- **Notes:** Uses FlareSolverr; basic filtering in place

### 3. **AvaNews** (`avanews.yaml`)

- **Whitelist:** 10 patterns
  - Core content: `/kurdistan`, `/news/`, `/business`, `/culture`, `/environment`, `/health`, `/opinion`
  - Next.js: `/_next/static/`
  - API: `/api/`
  - Embedded: `facebook.com/plugins/video.php`, `youtube.com/embed/`
- **Blacklist:** 7 patterns
  - Analytics: Google Analytics, GTM, DoubleClick
  - Telemetry: Cloudflare Insights, Zaraz, RUM
- **Notes:** Configured 2025-10-28 based on 2-article debug run (119 URLs)

### 4. **Awene** (`awene.yaml`) ✨ NEW

- **Whitelist:** 15 patterns
  - Core content: `/part?section=`, `/detail?article=`, `/culture`, `/aburi`
  - ASP.NET: `/WebResource.axd`
  - Assets: `/menu/`, `/bootstrapjs/`, CSS files
  - Social: Facebook comments/feedback, Twitter widgets
- **Blacklist:** 6 patterns
  - Analytics: Google Analytics, GTM
  - Social tracking: ShareThis, Facebook Connect
- **Notes:** Configured 2025-10-28 (62 URLs analyzed); selector fix needed for content extraction

### 5. **GovKrd** (`govkrd.yaml`) ✨ NEW

- **Whitelist:** 15 patterns
  - Government: `/ka/activities/`, press releases, categories
  - Assets: `/scripts/`, `/css/`, `/fonts/`
  - Security: Incapsula, reCAPTCHA (kept for anti-bot protection)
  - CDNs: jQuery, Bootstrap, Cloudflare, Google Fonts
- **Blacklist:** 4 patterns
  - Analytics: Google Analytics, DoubleClick, GTM
- **Notes:** Configured 2025-10-28 (39 URLs analyzed); 18 sentences extracted successfully

### 6. **NRT** (`nrt.yaml`) ✨ NEW

- **Whitelist:** 10 patterns
  - Core content: `/kurd`, `/detail/`
  - Assets: `/js/`, `/css/`, `/wene/`, various UI frameworks
  - ASP.NET: WebResource, ScriptResource
  - Google CSE: Custom search engine
- **Blacklist:** 4 patterns
  - Analytics: Google Analytics, GTM
  - Tracking: Alexa Metrics, AddThis
- **Notes:** Configured 2025-10-28 (45 URLs analyzed); 7 sentences extracted

---

## ⚠️ Needs Population (8/14)

These configs have empty `whitelist: []` and `blacklist: []` placeholders:

### News Sites

1. **Balinde** (`balinde.yaml`) - `balinde.com` (poetry site)
2. **Khak** (`khak.yaml`)
3. **Kurdsat** (`kurdsat.yaml`)
4. **Lvinpress** (`lvinpress.yaml`)
5. **Sekokurd** (`sekokurd.yaml`)
6. **Sharpress** (`sharpress.yaml`)
7. **Xendan** (`xendan.yaml`)
8. **Yariga** (`yariga.yaml`)

---

## Recommended Next Steps

### Phase 1: High-Priority Sites (Capture URLs)

Run debug scraping for these remaining active sites:

```powershell
# Balinde (poetry/literature)
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work/tools/scrapers && python3 generic_scraper.py --config configs --website balinde --max-articles 2 --category kurdish_poetry"

# Remaining sites (check which are active/accessible)
# Khak, Kurdsat, Lvinpress, Sekokurd, Sharpress, Xendan, Yariga
```

**Completed:**

- ✅ Awene (62 URLs, 6 whitelist + 6 blacklist)
- ✅ GovKrd (39 URLs, 15 whitelist + 4 blacklist)
- ✅ NRT (45 URLs, 10 whitelist + 4 blacklist)

### Phase 2: Analyze Tracked URLs

Check `work/tools/scrapers/tracked_urls_<site>_<category>.txt` files for:

- **Whitelists:**
  - Article/category URL patterns
  - Static asset domains (CSS, JS, images)
  - API endpoints
  - Embedded media sources
- **Blacklists:**
  - Google Analytics (`analytics.google.com`, `googletagmanager.com`, `doubleclick.net`)
  - Social media tracking pixels
  - Ad networks
  - Unnecessary third-party scripts

### Phase 3: Apply Patterns

Update each `url_filtering` section using patterns from tracked URLs.

---

## Common Kurdish News Site Patterns

### Typical Whitelist Entries

```yaml
whitelist:
  # Core content (adjust domain per site)
  - 'example.com/kurdish/'
  - 'example.com/sorani/'
  - 'example.com/news/'
  - 'example.com/politics/'

  # Static assets
  - 'static.example.com/'
  - 'assets.example.com/'
  - 'cdn.example.com/'

  # Common CDNs
  - 'cdnjs.cloudflare.com/'
  - 'fonts.googleapis.com/'
  - 'fonts.gstatic.com/'

  # Embedded media
  - 'youtube.com/embed/'
  - 'facebook.com/plugins/'
```

### Typical Blacklist Entries

```yaml
blacklist:
  # Analytics
  - 'analytics.google.com'
  - 'www.googletagmanager.com'
  - 'stats.g.doubleclick.net'
  - 'www.google-analytics.com'

  # Social tracking
  - 'facebook.com/tr'
  - 'twitter.com/i/adsct'

  # Ad networks
  - 'doubleclick.net'
  - 'googlesyndication.com'

  # Telemetry
  - 'cloudflareinsights.com'
  - '/cdn-cgi/zaraz/'
  - '/cdn-cgi/rum'
```

---

## Template Example Files

### Reference Configs

- `TEMPLATE.yaml` - Has empty placeholder (ready for examples)
- `MINIMAL_EXAMPLE.yaml` - Has empty placeholder
- `INVALID_EXAMPLE.yaml` - Has empty placeholder

**Decision Needed:** Should template files show example patterns or remain empty?

---

## Automation Opportunity

Consider creating a helper script to:

1. Batch-enable `debug_urls` for all configs
2. Run 1-2 article scrapes per site
3. Analyze tracked URL files
4. Suggest whitelist/blacklist patterns
5. Generate YAML snippets for review

**Location:** `work/tools/scrapers/tools/populate_url_filters.py`

---

## Notes

- **AvaNews Pattern:** Next.js sites need `/_next/static/` whitelisted for page rendering
- **Embedded Media:** Facebook video embeds (`/plugins/video.php`) and YouTube (`/embed/`) are common
- **Cloudflare Sites:** Most use `/cdn-cgi/` for various features; block only telemetry paths (`/zaraz/`, `/rum`)
- **FlareSolverr Sites:** May have different patterns due to anti-bot measures (e.g., Kurdistan24)

---

## Quick Reference

| Site        | Domain          | Status  | Whitelist | Blacklist | Priority | Notes                    |
| ----------- | --------------- | ------- | --------- | --------- | -------- | ------------------------ |
| Rudaw       | rudaw.net       | ✅ Done | 6         | 1         | -        | Production-ready         |
| Kurdistan24 | kurdistan24.net | ✅ Done | 2         | 0         | -        | FlareSolverr             |
| AvaNews     | ava.news        | ✅ Done | 10        | 7         | -        | Next.js site             |
| Awene       | awene.com       | ✅ Done | 15        | 6         | -        | Needs selector fix       |
| GovKrd      | gov.krd         | ✅ Done | 15        | 4         | -        | Government, 18 sentences |
| NRT         | nrttv.com       | ✅ Done | 10        | 4         | -        | 7 sentences extracted    |
| Balinde     | balinde.com     | ⚠️ TODO | 0         | 0         | Medium   | Poetry site              |
| Khak        | (unknown)       | ⚠️ TODO | 0         | 0         | Low      |                          |
| Kurdsat     | (unknown)       | ⚠️ TODO | 0         | 0         | Low      |                          |
| Lvinpress   | (unknown)       | ⚠️ TODO | 0         | 0         | Low      |                          |
| Sekokurd    | (unknown)       | ⚠️ TODO | 0         | 0         | Low      |                          |
| Sharpress   | (unknown)       | ⚠️ TODO | 0         | 0         | Low      |                          |
| Xendan      | (unknown)       | ⚠️ TODO | 0         | 0         | Low      |                          |
| Yariga      | (unknown)       | ⚠️ TODO | 0         | 0         | Low      |                          |
