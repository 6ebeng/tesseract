# URL Tracking Feature

## Overview

The URL tracking feature in `test_debug.py` helps you identify all network requests made when scraping a website. This is essential for creating accurate whitelist/blacklist rules that block unwanted third-party services (analytics, ads, tracking) without breaking website functionality.

## Table of Contents

1. [Quick Start](#quick-start)
2. [How It Works](#how-it-works)
3. [Usage](#usage)
4. [Understanding the Output](#understanding-the-output)
5. [Creating Filter Rules](#creating-filter-rules)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)

## Quick Start

```bash
# Track URLs when scraping a category
cd work/tools
python3 test_debug.py rudaw --category kurdistan --track-urls

# With headful browser (recommended for first time)
python3 test_debug.py rudaw --category kurdistan --track-urls --headful
```

The tool will display:

- All URLs fetched during scraping
- Categorization by type (scripts, images, stylesheets, etc.)
- First-party vs third-party domains
- Suggested whitelist/blacklist patterns
- JSON report saved to file

## How It Works

### Network Request Interception

The URL tracking uses Chrome DevTools Protocol to intercept all network requests:

1. **Enable Network Tracking**: Activates Chrome's performance logging
2. **Collect Requests**: Captures all HTTP/HTTPS requests during scraping
3. **Categorize URLs**: Groups by type (script, stylesheet, image, xhr, etc.)
4. **Analyze Domains**: Identifies first-party vs third-party
5. **Generate Suggestions**: Creates whitelist/blacklist patterns

### Request Categories

Tracked request types:

- **script**: JavaScript files
- **stylesheet**: CSS files
- **image**: Images (PNG, JPG, GIF, etc.)
- **xhr**: AJAX/fetch requests
- **font**: Web fonts
- **document**: HTML documents
- **media**: Audio/video
- **other**: Everything else

### Domain Classification

**First-Party**: Same domain as the website being scraped

- Example: If scraping `rudaw.net`, requests to `www.rudaw.net` are first-party

**Third-Party**: Different domain from main website

- Usually: Analytics, ads, social media, CDNs
- Example: `google-analytics.com`, `facebook.net`, `doubleclick.net`

## Usage

### Basic Usage

```bash
# Track URLs for a category
python3 test_debug.py WEBSITE --category CATEGORY --track-urls

# Examples
python3 test_debug.py rudaw --category kurdistan --track-urls
python3 test_debug.py nrt --category news --track-urls
python3 test_debug.py kurdsat --category politics --track-urls
```

### With Other Options

```bash
# Headful mode (see browser)
python3 test_debug.py rudaw --category kurdistan --track-urls --headful

# Verbose logging
python3 test_debug.py rudaw --category kurdistan --track-urls --verbose

# Screenshots + URL tracking
python3 test_debug.py rudaw --category kurdistan --track-urls --screenshots

# All combined
python3 test_debug.py rudaw --category kurdistan --track-urls --headful --verbose --screenshots
```

### Full Website Tracking

```bash
# Track all categories (takes longer)
python3 test_debug.py rudaw --track-urls

# Limit articles per category
python3 test_debug.py rudaw --track-urls --max-articles 2
```

## Understanding the Output

### Overview Section

```
📊 Overview:
   Total Requests: 127
   First-Party: 45 requests
   Third-Party: 82 requests from 15 domains
   Base Domain: rudaw.net
```

**Interpretation:**

- **Total Requests**: All HTTP/HTTPS requests made
- **First-Party**: Requests to main website domain
- **Third-Party**: External services (often blockable)
- **Base Domain**: Main website being scraped

### Requests by Type

```
📋 Requests by Type:
   SCRIPT           38 total (25 third-party)
   STYLESHEET       12 total (5 third-party)
   IMAGE            41 total (30 third-party)
   XHR              15 total (10 third-party)
```

**Interpretation:**

- Shows breakdown by resource type
- Third-party count helps identify tracking/ads
- High third-party script count = lots of analytics/tracking

### Third-Party Domains

```
🌍 Third-Party Domains (15):
      25x  googletagmanager.com
      18x  google-analytics.com
      12x  facebook.net
       8x  doubleclick.net
```

**Interpretation:**

- Sorted by request count (most active first)
- High count = heavily used (analytics, tracking)
- Common patterns:
  - `google*`: Analytics, ads, tag managers
  - `facebook*`, `twitter*`: Social tracking
  - `doubleclick*`: Advertising
  - `*cdn*`, `*static*`: Content delivery (usually needed)

### Suggested Patterns

#### Blacklist Patterns (Block These)

```
💡 Suggested Blacklist Patterns (Third-Party Services):
   # Analytics/Tracking (3 domains):
   '*.googletagmanager.com'
   '*.google-analytics.com'

   # Advertising (2 domains):
   '*.doubleclick.net'

   # Social Media (4 domains):
   '*.facebook.net'
   '*.twitter.com'
```

**Categories:**

- **Analytics/Tracking**: Usually safe to block
  - Google Analytics, Tag Manager, Mixpanel, etc.
- **Advertising**: Safe to block (improves speed)
  - DoubleClick, AdSense, ad networks
- **Social Media**: Block if not needed
  - Facebook Pixel, Twitter widgets, etc.
- **Other**: Review manually

#### Whitelist Patterns (Keep These)

```
💡 Suggested Whitelist Patterns (Main Content):
   '*.rudaw.net'  # Main website
   # CDN/Media (2 domains):
   '*.rudaw-cdn.net'
   '*.rudaw-static.com'
```

**Categories:**

- **Main Domain**: Always whitelist
- **CDN/Media**: Usually needed for images/videos
  - Look for: `cdn`, `static`, `media`, `assets` in domain
- **First-Party Subdomains**: Usually needed

#### Path-Based Patterns

```
💡 Path-Based Patterns:
   # Block common tracking paths:
   '*/analytics/*'
   '*/tracking/*'
   '*/pixel/*'
   '*/beacon/*'
   '*/collect*'
```

**Usage:**

- Generic patterns that work across domains
- Block tracking endpoints regardless of domain
- Safer than domain-based (less likely to break things)

## Creating Filter Rules

### Step 1: Analyze Output

Review the URL tracking output and identify:

1. **Must Block**: Analytics, ads, social tracking
2. **Must Keep**: Main domain, CDNs for content
3. **Maybe Block**: Review case-by-case

### Step 2: Create URLFilter

```python
from network_features import URLFilter, SessionManager

# Based on rudaw.net tracking results
url_filter = URLFilter(
    whitelist=[
        '*.rudaw.net',           # Main website
        '*.rudaw-cdn.net',       # CDN for images/videos
        '*.rudaw-static.com',    # Static assets
    ],
    blacklist=[
        # Analytics/Tracking
        '*.googletagmanager.com',
        '*.google-analytics.com',
        '*.facebook.net',
        '*.twitter.com',

        # Advertising
        '*.doubleclick.net',
        '*.adsystem.com',

        # Path-based
        '*/analytics/*',
        '*/tracking/*',
        '*/pixel/*',
        '*/beacon/*',
    ]
)
```

### Step 3: Integrate with SessionManager

```python
# Use URLFilter with SessionManager
session = SessionManager(
    url_whitelist=url_filter.whitelist,
    url_blacklist=url_filter.blacklist,
    cache_enabled=True,
    retry_enabled=True
)

# Make requests (filtered automatically)
response = session.get('https://rudaw.net/kurdish/kurdistan')
```

### Step 4: Test Your Filter

```python
# Test a URL
allowed, reason = url_filter.is_allowed('https://rudaw.net/article/123')
print(f"Allowed: {allowed}, Reason: {reason}")
# Output: Allowed: True, Reason: Matched whitelist pattern: *.rudaw.net

allowed, reason = url_filter.is_allowed('https://google-analytics.com/collect')
print(f"Allowed: {allowed}, Reason: {reason}")
# Output: Allowed: False, Reason: Matched blacklist pattern: *.google-analytics.com
```

### Step 5: Run Scraper and Verify

```bash
# Run scraper with filter
python3 run_scraper.py rudaw --category kurdistan

# Check if content is still extracted correctly
# If not, adjust whitelist (may need more CDN domains)
```

## Advanced Usage

### Multiple Category Tracking

Track different categories to get complete picture:

```bash
# Track multiple categories
python3 test_debug.py rudaw --category kurdistan --track-urls
python3 test_debug.py rudaw --category iraq --track-urls
python3 test_debug.py rudaw --category world --track-urls

# Compare results to find common patterns
```

### Analyzing JSON Reports

The tool saves detailed reports in JSON format:

```python
import json
from collections import defaultdict

# Load report
with open('url_tracking_rudaw_20240115_143022.json') as f:
    data = json.load(f)

# Analyze by type
print(f"Total requests: {data['summary']['total_requests']}")
for req_type, count in data['summary']['request_types'].items():
    print(f"{req_type}: {count}")

# Get all third-party domains
third_party = defaultdict(int)
for request_type, urls in data['requests'].items():
    for url_info in urls:
        if url_info['third_party']:
            third_party[url_info['domain']] += 1

# Sort by frequency
for domain, count in sorted(third_party.items(), key=lambda x: x[1], reverse=True):
    print(f"{count:4}x {domain}")
```

### Comparing Different Websites

```python
# Compare tracking profiles
websites = ['rudaw', 'nrt', 'kurdsat']

for website in websites:
    print(f"\n{website.upper()}:")
    # Run tracking
    # Analyze third-party domains
    # Compare patterns
```

### Creating Site-Specific Filters

```python
# Different filters for different websites
filters = {
    'rudaw': URLFilter(
        whitelist=['*.rudaw.net', '*.rudaw-cdn.net'],
        blacklist=['*.google-analytics.com', '*.facebook.net']
    ),
    'nrt': URLFilter(
        whitelist=['*.nrt.tv', '*.nrt-media.net'],
        blacklist=['*.googletagmanager.com', '*.twitter.com']
    ),
}

# Use appropriate filter per website
session = SessionManager(
    url_whitelist=filters[website].whitelist,
    url_blacklist=filters[website].blacklist
)
```

## Troubleshooting

### No URLs Tracked

**Problem**: URL tracking shows 0 requests

**Solutions:**

1. Make sure you're using Chrome (not Firefox)
2. Check if website loaded successfully
3. Try with `--headful` to see what's happening
4. Enable `--verbose` to see error messages

```bash
python3 test_debug.py rudaw --category kurdistan --track-urls --headful --verbose
```

### Website Breaks with Filter

**Problem**: Scraper fails after adding filter

**Causes:**

1. Blocked CDN domain needed for content
2. Blocked API endpoints
3. Too aggressive whitelist

**Solutions:**

1. Review CDN domains in tracking output
2. Add CDN domains to whitelist:
   ```python
   whitelist=[
       '*.rudaw.net',
       '*.rudaw-cdn.net',  # Add this
       '*.cloudflare.com',  # Or this
   ]
   ```
3. Test with blacklist-only first:
   ```python
   url_filter = URLFilter(blacklist=['*.google-analytics.com'])
   # No whitelist = allow everything except blacklist
   ```

### Too Many False Positives

**Problem**: Blacklist blocks legitimate content

**Solutions:**

1. Review domains manually before adding
2. Use path-based patterns instead:
   ```python
   blacklist=[
       '*/analytics/*',  # Path-based (safer)
       # Instead of '*.example.com'  # Domain-based (riskier)
   ]
   ```
3. Check for CDN keywords: `cdn`, `static`, `media`, `assets`
4. Test filter incrementally:

   ```python
   # Start small
   blacklist=['*.google-analytics.com']

   # Add one at a time
   blacklist=['*.google-analytics.com', '*.doubleclick.net']

   # Test after each addition
   ```

### Different Results Each Time

**Problem**: URL tracking shows different domains

**Causes:**

1. Website loads different content based on:
   - Time of day
   - User interaction
   - Geographic location
   - A/B testing

**Solutions:**

1. Run tracking multiple times
2. Track during different times
3. Use `--headful` and interact with page
4. Combine results from multiple runs:
   ```python
   # Merge multiple reports
   all_domains = set()
   for report in ['report1.json', 'report2.json', 'report3.json']:
       with open(report) as f:
           data = json.load(f)
           # Extract domains
           # Add to all_domains
   ```

### Tracking Fails Silently

**Problem**: No errors but no URLs tracked

**Solutions:**

1. Enable verbose logging:
   ```bash
   python3 test_debug.py rudaw --track-urls --verbose
   ```
2. Check Chrome version (needs recent version)
3. Verify ChromeDriver is up to date
4. Try with `--headful` to see browser console

## Best Practices

### 1. Always Test with Headful First

```bash
# First run with --headful to see what's happening
python3 test_debug.py rudaw --category kurdistan --track-urls --headful
```

### 2. Start Conservative, Expand Gradually

```python
# Start with obvious tracking
blacklist=['*.google-analytics.com', '*.googletagmanager.com']

# Test scraper

# Add more if needed
blacklist.extend(['*.facebook.net', '*.doubleclick.net'])

# Test again
```

### 3. Always Whitelist CDNs

```python
# CDN patterns to look for
cdn_keywords = ['cdn', 'static', 'media', 'assets', 'content']

# Always include in whitelist if found
whitelist=['*.rudaw.net', '*.rudaw-cdn.net', '*.rudaw-static.com']
```

### 4. Use Path Patterns for Generic Blocking

```python
# Safer than domain blocking
blacklist=[
    '*/analytics/*',
    '*/tracking/*',
    '*/pixel/*',
    '*/beacon/*',
    '*/collect*',
    '*/gtag/*',
]
```

### 5. Document Your Filters

```python
# Add comments explaining patterns
url_filter = URLFilter(
    whitelist=[
        '*.rudaw.net',        # Main website
        '*.rudaw-cdn.net',    # Image/video CDN
    ],
    blacklist=[
        '*.google-analytics.com',  # GA tracking (25 requests)
        '*.facebook.net',          # FB pixel (12 requests)
        '*/analytics/*',           # Generic tracking paths
    ]
)
```

### 6. Save Reports for Documentation

```bash
# Save with descriptive name
python3 test_debug.py rudaw --category kurdistan --track-urls
# Creates: url_tracking_rudaw_20240115_143022.json

# Rename for clarity
mv url_tracking_rudaw_20240115_143022.json url_tracking_rudaw_kurdistan_baseline.json
```

### 7. Test Multiple Scenarios

```bash
# Different categories
python3 test_debug.py rudaw --category kurdistan --track-urls
python3 test_debug.py rudaw --category iraq --track-urls

# Different article counts
python3 test_debug.py rudaw --category kurdistan --track-urls --max-articles 1
python3 test_debug.py rudaw --category kurdistan --track-urls --max-articles 10

# Different times of day
# (websites may load different ads/tracking)
```

## Examples

### Example 1: Basic Tracking

```bash
cd work/tools
python3 test_debug.py rudaw --category kurdistan --track-urls
```

**Output:**

```
🌐 NETWORK REQUEST TRACKING SUMMARY
================================================================================

📊 Overview:
   Total Requests: 87
   First-Party: 32 requests
   Third-Party: 55 requests from 12 domains
   Base Domain: rudaw.net

🌍 Third-Party Domains (12):
      18x  google-analytics.com
      12x  googletagmanager.com
       8x  facebook.net
       ...

💡 Suggested Blacklist Patterns:
   '*.google-analytics.com'
   '*.googletagmanager.com'
   '*.facebook.net'

📁 URL tracking report saved: url_tracking_rudaw_20240115_143022.json
```

### Example 2: Full Website with Verbose

```bash
python3 test_debug.py nrt --track-urls --verbose --max-articles 2
```

### Example 3: With Filter Applied

```python
# Create filter from tracking results
url_filter = URLFilter(
    whitelist=['*.nrt.tv'],
    blacklist=[
        '*.google-analytics.com',
        '*.googletagmanager.com',
        '*/analytics/*'
    ]
)

# Use in scraper
session = SessionManager(
    url_whitelist=url_filter.whitelist,
    url_blacklist=url_filter.blacklist
)

# Verify filter works
stats = url_filter.get_stats()
print(f"Blocked: {stats['blocked']}")
print(f"Allowed: {stats['allowed']}")
```

## See Also

- [NETWORK_FEATURES.md](NETWORK_FEATURES.md) - Complete network features guide
- [network_features.py](../work/tools/network_features.py) - Implementation
- [test_debug.py](../work/tools/test_debug.py) - Debug tool source
- [demo_url_tracking.py](../work/tools/demo_url_tracking.py) - Usage examples
