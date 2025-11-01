# Phase 6 Batch 4 - Quick Start Guide

**Goal**: Break the 71.69% plateau by adding biographical/formal text  
**Target**: 73-75% accuracy on mgk.tif (+2-4%)  
**Strategy**: Domain diversification (biography instead of more news)

---

## 🎯 Quick Action Plan (4-5 hours)

### Step 1: Scrape Wikipedia Biographies (2 hours)

```bash
# Navigate to scrapers directory
cd C:\tesseract\work\tools\scrapers

# Option A: Use existing scraper with Wikipedia URLs
# Add Wikipedia to scraper_config.yaml or create new config

# Option B: Quick Python script for Wikipedia
python3 << 'EOF'
import requests
from bs4 import BeautifulSoup
import re

# Kurdish Wikipedia biography categories
urls = [
    "https://ckb.wikipedia.org/wiki/پۆل:کەسایەتییەکانی_کوردستان",
    "https://ckb.wikipedia.org/wiki/پۆل:نووسەرانی_کورد",
    "https://ckb.wikipedia.org/wiki/پۆل:سیاسەتمەدارانی_کورد"
]

sentences = []
for url in urls:
    # Scrape and extract sentences
    # ... scraping logic here ...
    pass

# Save to file
with open('wikipedia_bio.txt', 'w', encoding='utf-8') as f:
    for sent in sentences:
        f.write(sent + '\n')
EOF
```

### Step 2: Filter for Quality (1 hour)

```bash
# Use existing filter with biography-focused parameters
cd C:\tesseract\work\tools\scrapers

# Modify filter_corpus.py for biography style
python3 filter_corpus.py \
    --input wikipedia_bio.txt \
    --output ../../corpus/ckb_wikipedia_bio_filtered.training_text \
    --zwnj-min 5.0 \
    --zwnj-max 12.0 \
    --length-min 12 \
    --length-max 40 \
    --purity-min 90.0
```

### Step 3: Create Batch 4 Corpus (5 minutes)

```bash
cd C:\tesseract\work\corpus

# Combine Batch 3 + 500 biographical sentences
cat ckb_phase6_batch3.training_text > ckb_phase6_batch4.training_text
head -500 ckb_wikipedia_bio_filtered.training_text >> ckb_phase6_batch4.training_text

# Verify
wc -l ckb_phase6_batch4.training_text
# Should be: 5,686 lines (5,186 + 500)

# Check quality
python3 -c "
lines = [l.strip() for l in open('ckb_phase6_batch4.training_text', 'r', encoding='utf-8') if l.strip()]
total_chars = sum(len(l) for l in lines)
zwnj = sum(l.count('\u200c') for l in lines)
words = sum(len(l.split()) for l in lines)
print(f'Batch 4: {len(lines):,} sentences')
print(f'Avg Words: {words/len(lines):.2f}')
print(f'ZWNJ Density: {(zwnj/total_chars)*100:.2f}%')
"
```

### Step 4: Train Batch 4 (45 minutes)

```powershell
cd C:\tesseract

# Train with new corpus
.\run_training.ps1 -Mode GenerateTrain -CorpusFileOverride work\corpus\ckb_phase6_batch4.training_text

# Training will take ~45 minutes
# Monitor: Get-Content work\logs\generate_training_latest.log -Wait
```

### Step 5: Evaluate (10 minutes)

```powershell
# Evaluate on mgk.tif
.\run_training.ps1 -Mode Eval

# Check results
Get-Content work\output\real_metrics.csv | Select-Object -Last 5
```

### Step 6: Compare Results (5 minutes)

```bash
# Expected outcomes:
# Best case:    75-76% (+4-5% from 71.69%)
# Expected:     73-74% (+2-3% from 71.69%)
# Conservative: 72-73% (+1-2% from 71.69%)

# If improvement seen: Continue with Batch 5 (more biography)
# If no improvement:   Analyze what went wrong, adjust strategy
```

---

## 🔍 Alternative: Quick Wikipedia Scraper

If Wikipedia scraping is complex, use this simpler approach:

```python
#!/usr/bin/env python3
"""Quick Kurdish Wikipedia biography scraper"""

import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path

def extract_sentences(text):
    """Extract sentences from Kurdish text"""
    # Split on sentence boundaries (. ! ؟)
    sentences = re.split(r'[.!؟]+', text)

    # Filter and clean
    result = []
    for sent in sentences:
        sent = sent.strip()

        # Must have Kurdish characters and reasonable length
        if len(sent) > 30 and '\u0600' <= sent[0] <= '\u06FF':
            result.append(sent)

    return result

def scrape_wiki_page(url):
    """Scrape a single Wikipedia page"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get main content
        content = soup.find('div', {'id': 'mw-content-text'})
        if not content:
            return []

        # Extract paragraphs
        paragraphs = content.find_all('p')

        sentences = []
        for p in paragraphs:
            text = p.get_text()
            sentences.extend(extract_sentences(text))

        return sentences
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def main():
    # Example Wikipedia pages (biography category)
    urls = [
        "https://ckb.wikipedia.org/wiki/جەلال_تاڵەبانی",
        "https://ckb.wikipedia.org/wiki/مەسعود_بارزانی",
        "https://ckb.wikipedia.org/wiki/شێخ_مەحمود_حەفید",
        # Add more biography URLs here
    ]

    all_sentences = []
    for url in urls:
        print(f"Scraping: {url}")
        sentences = scrape_wiki_page(url)
        all_sentences.extend(sentences)
        print(f"  Extracted: {len(sentences)} sentences")

    # Save to file
    output = Path('wikipedia_bio_raw.txt')
    with open(output, 'w', encoding='utf-8') as f:
        for sent in all_sentences:
            f.write(sent + '\n')

    print(f"\nTotal: {len(all_sentences)} sentences")
    print(f"Saved to: {output}")

if __name__ == '__main__':
    main()
```

Save as `quick_wiki_scraper.py` and run:

```bash
cd C:\tesseract\work\tools\scrapers
python3 quick_wiki_scraper.py
```

---

## 📊 Expected Quality Metrics

### Target for Wikipedia Biographies

| Metric              | Target Range | Notes                            |
| ------------------- | ------------ | -------------------------------- |
| **ZWNJ Density**    | 6-10%        | Higher than news (5%), match mgk |
| **Avg Length**      | 15-35 words  | Longer than news (14w), like mgk |
| **Kurdish Purity**  | >95%         | Similar to news                  |
| **Acceptance Rate** | 2-5%         | Better than news (1.61%)         |

### After Filtering (Expected)

From 10,000 raw sentences → 200-500 high-quality sentences

---

## ⚠️ Common Issues & Solutions

### Issue 1: Not Enough Sentences

**Problem**: Filtered corpus has <300 sentences  
**Solution**:

- Lower ZWNJ requirement (4-12% instead of 5-10%)
- Scrape more Wikipedia pages (50-100 biographies)
- Include related categories (history, culture, religion)

### Issue 2: Too Much Latin Script

**Problem**: Kurdish purity <90%  
**Solution**:

- Filter more aggressively (require 95%+)
- Skip technical/scientific articles
- Focus on literary/historical content

### Issue 3: Sentences Too Short

**Problem**: Avg length <12 words  
**Solution**:

- Increase min-length parameter (15-20 words)
- Skip list items, focus on paragraphs
- Extract from article bodies, not info boxes

---

## 🎯 Success Criteria

**Batch 4 will be considered successful if:**

✅ **Accuracy**: 72.5%+ on mgk.tif (+0.8% minimum improvement)  
✅ **Corpus Quality**: 400+ biographical sentences with 6-10% ZWNJ  
✅ **Training**: Smooth convergence, no errors  
✅ **Domain Balance**: 80% news + 20% biography mix

**If successful → Proceed to Batch 5 with more biography**  
**If failed → Analyze and adjust strategy**

---

## 🚀 Quick Command Summary

```bash
# 1. Scrape
cd C:\tesseract\work\tools\scrapers
python3 quick_wiki_scraper.py

# 2. Filter
python3 filter_corpus.py --input wikipedia_bio_raw.txt --zwnj-min 5 --length-min 12

# 3. Combine
cd C:\tesseract\work\corpus
cat ckb_phase6_batch3.training_text > ckb_phase6_batch4.training_text
head -500 ckb_wikipedia_bio_filtered.training_text >> ckb_phase6_batch4.training_text

# 4. Train
cd C:\tesseract
.\run_training.ps1 -Mode GenerateTrain -CorpusFileOverride work\corpus\ckb_phase6_batch4.training_text

# 5. Evaluate
.\run_training.ps1 -Mode Eval
```

---

**Ready to start?** Run the commands above to begin Batch 4!

**Estimated time**: 4-5 hours (mostly automated)  
**Expected result**: Break through the 71.69% plateau  
**Risk**: Low (can always revert to Batch 3 if needed)
