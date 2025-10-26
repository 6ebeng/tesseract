# Kurdistan24 Scraper - Special Requirements

**Date**: October 24, 2025
**Status**: ⚠️ **REQUIRES FLARESOLVERR** - Cloudflare protection active

## Summary

Kurdistan24 (kurdistan24.net) uses **Cloudflare bot protection** which blocks standard Selenium/browser automation. The legacy scraper successfully bypassed this using **FlareSolverr**, a special proxy service that solves Cloudflare challenges.

## Technical Requirements

### FlareSolverr

- **Service**: FlareSolverr proxy
- **URL**: `http://localhost:8191`
- **Purpose**: Bypass Cloudflare JavaScript challenge & CAPTCHA
- **Installation**: Docker container or standalone service
- **Status**: ⚠️ **NOT RUNNING** (not detected on port 8191)

### Architecture Difference

**Legacy Scraper**:

- Used **BeautifulSoup + requests** (not Selenium)
- Routed all requests through FlareSolverr API
- FlareSolverr handled browser automation & Cloudflare bypass
- Returned HTML to Python for parsing

**Current Generic Scraper**:

- Uses **Selenium** directly
- No FlareSolverr integration
- Gets blocked by Cloudflare

## Legacy Scraper Details

### Selectors (Verified Working)

```yaml
# Article list page
article_list:
  - <article> tags
  - <h3> titles
  - Links: a[href*='/ckb/story/'], a[href*='/ckb/opinion/']

# Article detail page
article_title: h1
article_content: div.reader-content p
```

### Pagination

```
Format: ?page={page}
Example: https://www.kurdistan24.net/ckb/list/category/9?page=2
```

### Categories (Kurdish)

- **Politics (سیاسی)**: `/list/category/9`
- **Economy (ئابووری)**: `/list/category/12`
- **Culture (کولتوور)**: `/list/category/10`
- **Health (تەندروستی)**: `/category/4`
- **Science & Tech**: `/category/7`
- **Opinion (وتار)**: `/list/opinions`
- **Interview (هەڤپەیڤین)**: `/list/type/3`

## Testing Results

### Without FlareSolverr

**Selenium Test**: ❌ **BLOCKED**

```
Result: Cloudflare challenge page
Message: "Checking if the site connection is secure"
Status: Cannot access content
```

### With FlareSolverr (Legacy Method)

**BeautifulSoup + FlareSolverr**: ✅ **WORKING** (in legacy)

```
Session creation: ✅ Success
Page retrieval: ✅ Success
Content extraction: ✅ Success
Sentences extracted: Hundreds per run
```

## Implementation Options

### Option 1: Add FlareSolverr Support to Generic Scraper ⭐ **RECOMMENDED**

**Pros**:

- Enables Kurdistan24 scraping
- Can be reused for other Cloudflare-protected sites
- Maintains V4.0 architecture

**Cons**:

- Requires FlareSolverr service running
- Added complexity
- Slower than direct Selenium

**Implementation**:

```python
# In generic_scraper.py
class GenericScraper:
    def __init__(self, ...):
        self.flaresolverr_url = os.getenv('FLARESOLVERR_URL', 'http://localhost:8191')

    def _safe_get(self, url):
        if self.use_flaresolverr:
            return self._flaresolverr_get(url)
        else:
            return super()._safe_get(url)

    def _flaresolverr_get(self, url):
        response = requests.post(f'{self.flaresolverr_url}/v1', json={
            "cmd": "request.get",
            "url": url,
            "session": self.session_id,
            "maxTimeout": 60000
        })
        # Parse and set as page content
```

**Config**:

```yaml
# kurdistan24.yaml
flaresolverr:
  enabled: true
  url: 'http://localhost:8191'
```

### Option 2: Keep Legacy Scraper for Kurdistan24

**Pros**:

- Already working
- No changes needed
- Fast to deploy

**Cons**:

- Maintains two systems
- Duplicated code
- Not integrated with V4.0

### Option 3: Skip Kurdistan24 for Now

**Pros**:

- Focus on other 11 websites first
- Revisit later
- Simpler deployment

**Cons**:

- Missing valuable Kurdish content source
- Have to implement eventually

## Recommendation

**Immediate**: **Option 3** - Skip for now

- Mark as `enabled: false` in config
- Document FlareSolverr requirement
- Focus on testing remaining 7 websites

**Future**: **Option 1** - Add FlareSolverr support

- After all other sites are working
- Implement as optional feature
- Provides solution for Cloudflare-protected sites

## FlareSolverr Setup (For Future)

### Docker Installation

```bash
docker run -d \
  --name flaresolverr \
  -p 8191:8191 \
  -e LOG_LEVEL=info \
  ghcr.io/flaresolverr/flaresolverr:latest
```

### Testing FlareSolverr

```bash
# Check if running
curl http://localhost:8191

# Test with Kurdistan24
curl -X POST http://localhost:8191/v1 \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://www.kurdistan24.net/ckb/list/category/9",
    "maxTimeout": 60000
  }'
```

## Current Status Summary

| Item                    | Status                          |
| ----------------------- | ------------------------------- |
| Config file             | ✅ Correct selectors documented |
| FlareSolverr service    | ❌ Not running                  |
| Generic scraper support | ❌ Not implemented              |
| Legacy scraper          | ✅ Working (archived)           |
| Website accessibility   | ❌ Blocked by Cloudflare        |
| Recommended action      | ⏸️ Skip for now                 |

## Next Steps

1. Mark Kurdistan24 as disabled (`enabled: false`)
2. Document FlareSolverr requirement clearly
3. Move to test other websites (Lvinpress, NRT, Rudaw, etc.)
4. After 11 websites working, implement FlareSolverr support
5. Re-enable Kurdistan24 with FlareSolverr integration

---

**Note**: Kurdistan24 is a major Kurdish news source. While we're skipping it now for practical reasons, implementing FlareSolverr support should be a priority for future development.
