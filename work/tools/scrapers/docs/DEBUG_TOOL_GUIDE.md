# Debug Test Tool - Quick Reference

**File:** `work/tools/test_debug.py`

A comprehensive debugging tool for the Generic Scraper that allows detailed inspection and testing of websites and categories.

---

## 🚀 Quick Start

```bash
# Basic debug (shows config + runs scrape)
python3 test_debug.py rudaw

# Debug specific category
python3 test_debug.py rudaw --category kurdistan
```

---

## 📋 Debug Modes

### 1. Configuration Inspection

**Show website configuration:**

```bash
python3 test_debug.py rudaw --config-only
```

**Output:**

- ✅ Website name, base URL, enabled status
- ✅ Click-through navigation settings
- ✅ FlareSolverr settings
- ✅ Language detection config
- ✅ Wait configurations (wait, collection_wait, article_wait)
- ✅ Default selectors
- ✅ All categories with status and settings

**Show category configuration:**

```bash
python3 test_debug.py rudaw --category kurdistan --config-only
```

**Output:**

- ✅ Category URL and enabled status
- ✅ Pagination type and settings
- ✅ Wait configurations (merged with website defaults)
- ✅ Selectors (merged with website defaults, shows overrides)

---

### 2. Selector Testing

**Test if selectors work:**

```bash
python3 test_debug.py rudaw --category kurdistan --test-selectors
```

**What it does:**

1. Navigates to category URL
2. Tests `article_list` selector (counts articles found)
3. Shows sample article URLs
4. Navigates to first article
5. Tests `article_title` selector (extracts title)
6. Tests `article_body` selector (extracts content)

**Output:**

```
🧪 TESTING SELECTORS: rudaw / kurdistan
🌐 Navigating to: https://rudaw.net/sorani/kurdistan

📋 Testing article_list selector...
   Selector: article.card
   ✅ Found 20 article elements

   📎 Sample article links:
      1. https://rudaw.net/sorani/kurdistan/article-1
      2. https://rudaw.net/sorani/kurdistan/article-2
      ...

📄 Testing article page selectors...
   Navigating to: https://rudaw.net/sorani/kurdistan/article-1

   Testing article_title: h1
   ✅ Title: هەواڵی سەرەکی...

   Testing article_body: div.article__body
   ✅ Body: 1543 chars
   Preview: ناوەرۆکی هەواڵ لێرە...
```

**Use Cases:**

- ✅ Verify selectors find elements
- ✅ Debug selector issues before full scrape
- ✅ See what content is extracted

---

### 3. Pagination Testing

**Test pagination without extracting articles:**

```bash
python3 test_debug.py rudaw --category kurdistan --pagination-only
```

**What it does:**

1. Navigates to category URL
2. Tests pagination based on type:
   - **url_template:** Navigates to each page URL, counts articles
   - **infinite_scroll:** Scrolls N times, shows article count increase
   - **click_load_more:** Clicks button N times, shows article count increase

**Output for url_template:**

```
🔄 TESTING PAGINATION: rudaw / kurdistan
📄 Pagination Type: url_template

🔢 Testing URL template pagination (3 pages)...

   Page 1/3: https://rudaw.net/sorani/kurdistan
   ✅ Found 20 articles

   Page 2/3: https://rudaw.net/sorani/kurdistan?page=2
   ✅ Found 20 articles

   Page 3/3: https://rudaw.net/sorani/kurdistan?page=3
   ✅ Found 20 articles
```

**Output for click_load_more:**

```
🖱️  Testing load more button (5 clicks)...
   Button selector: a.load-more-button

   Click 1/5
   Articles: 10 → 19 (+9)

   Click 2/5
   Articles: 19 → 28 (+9)
   ...
```

**Custom page limit:**

```bash
python3 test_debug.py rudaw --category kurdistan --pagination-only --max-pages 5
```

**Use Cases:**

- ✅ Verify pagination works
- ✅ Count total articles available
- ✅ Debug pagination issues

---

### 4. Wait Strategy Debugging

**Test wait configurations:**

```bash
python3 test_debug.py rudaw --category kurdistan --debug-waits
```

**What it does:**

1. Tests collection page load wait
   - Shows which wait config is used (collection_wait, wait, or default)
   - Measures actual page load time
2. Tests article page load wait
   - Shows which wait config is used (article_wait, wait, or default)
   - Measures actual page load time

**Output:**

```
⏱️  DEBUGGING WAIT STRATEGIES: rudaw / kurdistan

🌐 Navigating to: https://rudaw.net/sorani/kurdistan

1️⃣  Testing collection page load wait...
   collection_wait config: {'selector': 'article.card', 'timeout': 5}
   ✅ Page loaded in 2.34s

2️⃣  Testing article page load wait...
   Navigating to: https://rudaw.net/sorani/kurdistan/article-1
   article_wait config: 3
   ✅ Article loaded in 1.87s
```

**Use Cases:**

- ✅ Verify wait configs are applied
- ✅ Optimize wait times
- ✅ Debug slow page loads

---

### 5. Full Debug Scraping

**Run full scrape with detailed logging:**

```bash
python3 test_debug.py rudaw --category kurdistan
```

**What it does:**

1. Shows configuration (like --config-only)
2. Runs full scraping process
3. Shows results summary

**Output:**

```
🔍 DEBUGGING CATEGORY: rudaw / kurdistan
[configuration details...]

🚀 FULL DEBUG SCRAPE: rudaw
   Category: kurdistan

📂 Scraping category: kurdistan
[scraping process with normal logging...]

📊 DEBUG RESULTS
⏱️  Duration: 45.23s
📝 Sentences Extracted: 127

📄 Sample Sentences (first 5):
   1. ئەم هەواڵە سەبارەت بە...
   2. لە کوردستان...
   ...
```

**Custom article limit:**

```bash
python3 test_debug.py rudaw --category kurdistan --max-articles 5
```

**Scrape entire website (all categories):**

```bash
python3 test_debug.py rudaw --max-articles 3
```

---

## 🎛️ Control Options

### Headful Mode (See Browser in Action)

```bash
python3 test_debug.py rudaw --category kurdistan --headful
```

**What it does:**

- Shows browser window (not headless)
- Watch pagination, clicking, scrolling
- Great for visual debugging

**Use Cases:**

- ✅ See what's happening
- ✅ Debug click/scroll issues
- ✅ Verify page loads correctly

---

### Screenshots

```bash
python3 test_debug.py rudaw --category kurdistan --screenshots
```

**What it does:**

- Saves screenshots at key points:
  - `page_loaded` - After navigating to page
  - `article_list_error` - If article list selector fails
  - `article_page` - After navigating to article
  - `title_error`, `body_error` - If selectors fail
  - `pagination_error` - If pagination fails
  - etc.
- Screenshots saved to `debug_screenshots/` directory
- Filename format: `{website}_{event}_{timestamp}.png`

**Use Cases:**

- ✅ Visual debugging without headful mode
- ✅ Capture errors for later analysis
- ✅ Compare different configurations

---

### Verbose Logging

```bash
python3 test_debug.py rudaw --category kurdistan --verbose
```

**What it does:**

- Enables DEBUG level logging
- Shows all internal operations
- Detailed Selenium operations

**Use Cases:**

- ✅ Deep debugging
- ✅ See all driver operations
- ✅ Trace execution flow

---

## 🔥 Combined Options

**Ultimate debug mode:**

```bash
python3 test_debug.py rudaw --category kurdistan \
  --test-selectors \
  --headful \
  --screenshots \
  --verbose
```

**Quick selector test with visuals:**

```bash
python3 test_debug.py rudaw --category kurdistan --test-selectors --headful
```

**Pagination test with screenshots:**

```bash
python3 test_debug.py rudaw --category kurdistan --pagination-only --screenshots --max-pages 5
```

**Full debug with all controls:**

```bash
python3 test_debug.py rudaw --category kurdistan --max-articles 3 --headful --screenshots --verbose
```

---

## 📊 Common Use Cases

### Use Case 1: New Website Not Working

```bash
# 1. Check configuration
python3 test_debug.py newsite --config-only

# 2. Test selectors
python3 test_debug.py newsite --category news --test-selectors --headful

# 3. If selectors fail, watch in browser
python3 test_debug.py newsite --category news --test-selectors --headful --screenshots

# 4. Once selectors work, test pagination
python3 test_debug.py newsite --category news --pagination-only --headful

# 5. Finally, test full scrape
python3 test_debug.py newsite --category news --max-articles 3 --verbose
```

---

### Use Case 2: Category Returns No Articles

```bash
# 1. Check category config
python3 test_debug.py website --category problematic --config-only

# 2. Test if article_list selector finds anything
python3 test_debug.py website --category problematic --test-selectors --headful

# 3. If found, test pagination
python3 test_debug.py website --category problematic --pagination-only
```

---

### Use Case 3: Slow Scraping

```bash
# 1. Debug wait strategies
python3 test_debug.py website --category slow --debug-waits

# 2. Test with shorter waits (modify config, then test)
python3 test_debug.py website --category slow --max-articles 1 --verbose
```

---

### Use Case 4: Pagination Not Working

```bash
# 1. Test pagination with visual debugging
python3 test_debug.py website --category news --pagination-only --headful

# 2. If url_template, test with max-pages
python3 test_debug.py website --category news --pagination-only --max-pages 3 --verbose

# 3. If click_load_more, watch button clicks
python3 test_debug.py website --category news --pagination-only --headful --screenshots
```

---

### Use Case 5: Click-Through Navigation Issues

```bash
# 1. Check click-through is enabled
python3 test_debug.py khak --config-only

# 2. Test with headful to see clicks
python3 test_debug.py khak --category politics --headful --max-articles 3

# 3. Capture screenshots of each step
python3 test_debug.py khak --category politics --screenshots --max-articles 3
```

---

## 📝 Output Files

### Screenshots

- **Location:** `debug_screenshots/`
- **Format:** `{website}_{event}_{timestamp}.png`
- **Examples:**
  - `rudaw_page_loaded_20251025_143022.png`
  - `rudaw_article_page_20251025_143025.png`
  - `rudaw_selector_test_error_20251025_143030.png`

### Logs

- Printed to console (stdout)
- Can redirect to file: `python3 test_debug.py rudaw > debug.log 2>&1`

---

## 🎯 Tips & Best Practices

### 1. Start Simple

```bash
# First, check config
python3 test_debug.py website --config-only

# Then, test selectors
python3 test_debug.py website --category news --test-selectors
```

### 2. Use Headful for Visual Issues

```bash
# If selectors fail, watch what happens
python3 test_debug.py website --category news --test-selectors --headful
```

### 3. Use Screenshots for Remote Debugging

```bash
# Can't use headful on server? Use screenshots
python3 test_debug.py website --category news --test-selectors --screenshots
```

### 4. Limit Articles During Development

```bash
# Don't scrape 100 articles while testing
python3 test_debug.py website --category news --max-articles 2
```

### 5. Combine Test Modes

```bash
# Test selectors AND pagination in one run
python3 test_debug.py website --category news --test-selectors --headful
# Then manually test pagination
python3 test_debug.py website --category news --pagination-only --headful
```

---

## 🆚 Debug Tool vs Test Suite

| Feature                | `test_debug.py`         | `test_suite.py`     |
| ---------------------- | ----------------------- | ------------------- |
| **Purpose**            | Development debugging   | Production testing  |
| **Target**             | Single website/category | All websites        |
| **Output**             | Detailed debug info     | Pass/fail summary   |
| **Headful**            | ✅ Supported            | ❌ Headless only    |
| **Screenshots**        | ✅ Supported            | ❌ Not available    |
| **Selector Testing**   | ✅ Dedicated mode       | ❌ Only full scrape |
| **Pagination Testing** | ✅ Dedicated mode       | ❌ Only full scrape |
| **Wait Debugging**     | ✅ Dedicated mode       | ❌ Not available    |
| **Speed**              | Slow (detailed)         | Fast (bulk)         |
| **Use When**           | Developing/debugging    | Testing all sites   |

---

## 🔧 Troubleshooting

### Problem: "Website not found"

```bash
# List available websites
python3 test_debug.py --help  # Check usage
cd work/tools/scrapers/configs
ls *.yaml  # See all configs
```

### Problem: Screenshots not saving

```bash
# Check directory exists
ls -la debug_screenshots/

# Ensure --screenshots flag is used
python3 test_debug.py website --category news --test-selectors --screenshots
```

### Problem: Selectors not found

```bash
# Use headful to see page
python3 test_debug.py website --category news --test-selectors --headful

# Check actual page structure in browser
# Update selectors in config file
```

### Problem: Too slow

```bash
# Reduce articles
python3 test_debug.py website --category news --max-articles 1

# Reduce pages
python3 test_debug.py website --category news --pagination-only --max-pages 2
```

---

## 📚 See Also

- **`test_suite.py`** - Run tests on all websites
- **`FEATURES_V5.md`** - Complete feature guide
- **`TEMPLATE.yaml`** - Configuration template
- **`click_through_navigation.md`** - Click-through guide

---

**Remember:** This tool is for **debugging during development**. Use `test_suite.py` for production testing of all websites.
