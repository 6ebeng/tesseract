# 🚀 Migration Guide - Quick Start

**Status**: Ready to begin migration  
**Pilot Sites**: Kurdsat, NRT  
**Estimated Time**: 2-4 hours for pilot

---

## ✅ What's Ready

1. ✅ **GenericScraper** - `generic_scraper.py` (700 lines)
2. ✅ **Configuration** - `websites.yaml` (2 sites configured)
3. ✅ **All Framework Components** - 19 production files
4. ✅ **Complete Documentation** - 7 comprehensive guides

---

## 🎯 Step-by-Step Migration (Pilot)

### Step 1: Install Dependencies (5 min)

```bash
cd c:\tesseract\work\tools\scrapers

# Install all required packages
pip install -r requirements.txt
```

**Packages installed**:

- selenium (web automation)
- PyYAML (configuration)
- Flask (dashboard)
- pytest (testing)
- And 15+ more dependencies

---

### Step 2: Validate Configuration (2 min)

```bash
# Validate YAML syntax and structure
python cli_tools.py validate websites.yaml
```

**Expected Output**:

```
🔍 Validating configuration: websites.yaml

✅ YAML syntax valid

📝 Checking website: kurdsat
   ✅ name: Kurdsat TV
   ✅ base_url: https://kurdsat.tv
   ✅ selectors: present

📝 Checking website: nrt
   ✅ name: NRT News
   ✅ base_url: https://www.nrttv.com
   ✅ selectors: present

============================================================
✅ Configuration is valid!
   Websites: 2
```

---

### Step 3: Test Selectors (10 min)

Test if selectors work on live pages:

```bash
# Test Kurdsat selectors
python cli_tools.py test-selector "https://kurdsat.tv/ckb/news" "a[href*='/ckb/news/']"

# Test NRT selectors
python cli_tools.py test-selector "https://www.nrttv.com/ku/news/kurdistan" "article.post"

# Save screenshots for verification
python cli_tools.py test-selector "https://kurdsat.tv/ckb/news" "a[href*='/ckb/news/']" --screenshot
```

**What to check**:

- ✅ Elements found (count > 0)
- ✅ Correct elements highlighted
- ✅ No timeout errors

**If selectors fail**:

```bash
# Debug the page structure
python cli_tools.py debug "https://kurdsat.tv/ckb/news" --verbose

# Adjust selectors in websites.yaml based on output
```

---

### Step 4: Run First Migration Test (30 min)

#### A. Test Kurdsat (Single Category)

```bash
# Test just one category first
python generic_scraper.py --website kurdsat --category news --max-articles 5
```

**Expected Output**:

```
======================================================================
🌐 Scraping Website: Kurdsat TV
======================================================================

📂 Categories to scrape: news

📂 Scraping Category: news
   URL: https://kurdsat.tv/ckb/news
   Found 25 article links
   ✅ Extracted 75 sentences from 5 articles

✅ Website scraping complete!
   Articles: 5
   Sentences: 75
   Duplicates skipped: 0
   Duration: 45.2s
```

#### B. Test Full Kurdsat (All Categories)

```bash
# Test all categories (limited articles)
python generic_scraper.py --website kurdsat --max-articles 3
```

**What to verify**:

- Articles scraped successfully
- Sentences extracted
- No major errors
- Reasonable execution time

---

### Step 5: Compare with Old Scraper (15 min)

Run old scraper for comparison:

```bash
cd c:\tesseract\work

# Old scraper (Kurdsat only)
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 -c '
import sys
sys.path.insert(0, \"tools\")
from scrapers.kurdsat_scraper import KurdsatScraper

scraper = KurdsatScraper()
pol = scraper.scrape_political(clicks=5)
spec = scraper.scrape_specialized(articles_per_category=3)
print(f\"Old Scraper - Political: {pol}, Specialized: {spec}, Total: {pol + spec}\")
'"
```

**Compare results**:
| Metric | Old Scraper | New Scraper | Notes |
|--------|-------------|-------------|-------|
| Sentences | ~XXX | ~XXX | Should be similar |
| Duration | ~XX min | ~XX min | New should be faster |
| Errors | Manual check | Auto-logged | Check dashboard |

---

### Step 6: Test NRT (30 min)

Repeat process for NRT:

```bash
# Single category
python generic_scraper.py --website nrt --category kurdistan --max-articles 5

# All categories
python generic_scraper.py --website nrt --max-articles 3
```

---

### Step 7: Monitor with Dashboard (15 min)

Start the admin dashboard to monitor scraping:

```bash
cd c:\tesseract\work\tools\scrapers\dashboard
python app.py
```

Open browser: **http://localhost:5000**

**Dashboard shows**:

- Total articles scraped
- Articles per website
- Recent activity feed
- Error logs
- Performance charts

Keep dashboard running during next tests.

---

### Step 8: Run Parallel Test (10 min)

Test scraping both sites in parallel:

```bash
cd c:\tesseract\work\tools\scrapers

# Create test script
python -c "
from generic_scraper import GenericScraper

scraper = GenericScraper('websites.yaml')

# Scrape Kurdsat
print('\\n🌐 Scraping Kurdsat...')
result1 = scraper.scrape_website('kurdsat', max_articles=5)

# Scrape NRT
print('\\n🌐 Scraping NRT...')
result2 = scraper.scrape_website('nrt', max_articles=5)

print(f'\\n✅ Pilot Complete!')
print(f'   Kurdsat: {result1.articles_scraped} articles, {result1.sentences_extracted} sentences')
print(f'   NRT: {result2.articles_scraped} articles, {result2.sentences_extracted} sentences')
"
```

---

### Step 9: Validate Quality (15 min)

Check that scraped content is good quality:

```bash
# Check sentences are in Kurdish/Arabic
# Check no empty or junk sentences
# Check reasonable sentence length

# View recent sentences in dashboard
# Or check corpus files directly
```

**Quality checklist**:

- [ ] Sentences in correct language (Kurdish/Arabic)
- [ ] No HTML tags in text
- [ ] Minimum 20 characters per sentence
- [ ] No duplicate sentences
- [ ] Proper encoding (Kurdish characters display correctly)

---

### Step 10: Document Findings (10 min)

Create migration log:

```bash
# Create log file
touch c:\tesseract\docs\MIGRATION_LOG.md
```

**Document**:

- What worked well
- What needed adjustment
- Selector changes made
- Performance metrics
- Issues encountered
- Lessons learned

---

## 🎯 Decision Point

After pilot testing, decide:

### ✅ If Pilot Successful:

- Sentence quality is good ✓
- Performance is acceptable ✓
- No major errors ✓
- Configuration works ✓

**→ Proceed to migrate remaining 10 websites**

### ⚠️ If Issues Found:

- Poor sentence quality
- Too many errors
- Selectors not working
- Performance too slow

**→ Pause and fix issues before continuing**

Common fixes:

1. Adjust selectors in `websites.yaml`
2. Add wait times
3. Change category types
4. Enable/disable language filtering

---

## 📋 Next Steps After Pilot

### If Successful:

1. **Migrate Batch 1** (Easy sites)

   - Rudaw
   - Khak
   - Awene
   - Estimate: 2-3 hours

2. **Migrate Batch 2** (Medium difficulty)

   - Kurdistan24
   - Xendan
   - Sekokurd
   - Estimate: 2-3 hours

3. **Migrate Batch 3** (Complex sites)

   - GovKrd
   - Sharpress
   - Lvinpress
   - Balinde
   - Estimate: 3-4 hours

4. **Full Integration Test**

   ```bash
   python production_scraper.py --all --parallel --workers 5
   ```

5. **Deploy to Production**
   - Update training scripts
   - Schedule cron jobs
   - Monitor with dashboard

---

## 🔧 Troubleshooting

### Problem: Selectors not finding elements

**Solution**:

```bash
# Debug page structure
python cli_tools.py debug "https://example.com" --verbose

# Test different selectors
python cli_tools.py test-selector "https://example.com" "div.article"
python cli_tools.py test-selector "https://example.com" "article"
python cli_tools.py test-selector "https://example.com" ".post"

# Update websites.yaml with working selector
```

### Problem: Too slow

**Solution**:

```yaml
# In websites.yaml, reduce:
pages: 3 # Instead of 10
clicks: 5 # Instead of 30
max-articles: 10 # Use --max-articles flag
```

### Problem: Language detection wrong

**Solution**:

```yaml
# Disable language filtering temporarily
language_detection:
  enabled: false

# Or adjust filter
language_detection:
  enabled: true
  filter: ['ckb', 'ar', 'en']  # Add more languages
```

### Problem: Too many errors

**Solution**:

```bash
# Check error logs in dashboard
# Or check log files
cat logs/scraper.log

# Enable verbose logging
# Edit generic_scraper.py:
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 Success Metrics

Track these metrics to validate migration:

| Metric            | Target         | How to Check      |
| ----------------- | -------------- | ----------------- |
| Sentence Quality  | 95%+ clean     | Manual review     |
| Sentence Count    | Similar to old | Compare outputs   |
| Scraping Speed    | 2-3x faster    | Time comparison   |
| Error Rate        | <5%            | Dashboard metrics |
| Deduplication     | 20-30%         | Dedup stats       |
| Language Accuracy | 95%+           | Spot check        |

---

## 🎓 Tips for Success

1. **Start Small**: Test 1 category before full website
2. **Use Dashboard**: Monitor in real-time
3. **Save Screenshots**: Helps debug selector issues
4. **Compare Outputs**: Validate against old scraper
5. **Document Changes**: Track selector adjustments
6. **Test Incrementally**: Don't migrate all 12 at once
7. **Keep Old Scrapers**: Reference for complex sites

---

## ✅ Pilot Complete Checklist

- [ ] Dependencies installed
- [ ] Configuration validated
- [ ] Selectors tested on live pages
- [ ] Kurdsat migrated successfully
- [ ] NRT migrated successfully
- [ ] Quality validated
- [ ] Performance acceptable
- [ ] Dashboard running
- [ ] Parallel test successful
- [ ] Findings documented

**When all checked → Ready for full migration! 🚀**

---

## 📞 Need Help?

**Documentation**:

- `MIGRATION_READINESS_ASSESSMENT.md` - Full assessment
- `SCRAPER_QUICK_START.md` - Quick reference
- `ADVANCED_FEATURES.md` - Feature guide
- `PRODUCTION_READINESS.md` - Framework details

**Tools**:

- `python cli_tools.py --help` - CLI reference
- `python config_wizard.py` - Interactive setup
- `http://localhost:5000` - Admin dashboard

**Debugging**:

- Check `logs/scraper.log` for errors
- Use `--verbose` flag for detailed output
- Test selectors with CLI tools first
