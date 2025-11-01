# 📚 Phase 2: Wikipedia Corpus Expansion - Detailed Plan

**Phase:** 2 of 4 (Option D Hybrid Approach)  
**Start Date:** October 9, 2025  
**Duration:** 2-3 days  
**Goal:** Extract 50,000+ words from Kurdish Wikipedia to reach 85-90% accuracy

---

## 🎯 Objectives

### Primary Goal

Expand training corpus from **14,456 words** to **50,000-100,000 words** through automated Kurdish Wikipedia extraction.

### Target Metrics

| Metric           | Current | Phase 2 Target | Ultimate Goal |
| ---------------- | ------- | -------------- | ------------- |
| **Corpus Words** | 14,456  | 60,000+        | 80,000+       |
| **ZWNJ Count**   | 8,309   | 35,000+        | 50,000+       |
| **ZWNJ %**       | 7.77%   | 7-10%          | 7-10%         |
| **Accuracy**     | 66-70%  | 85-90%         | 95%+          |
| **CER**          | 30-33%  | 10-15%         | ≤5%           |

---

## 📋 Phase 2 Task Breakdown

### Task 2.1: Download Kurdish Wikipedia Dump

**Duration:** 30 minutes  
**Difficulty:** Easy

#### What is Kurdish Wikipedia?

- **URL:** https://ckb.wikipedia.org (Central Kurdish / Sorani)
- **Size:** ~30,000+ articles
- **Script:** Arabic script (same as our training data)
- **Quality:** Professionally written, properly formatted

#### Download Options

**Option A: Official Wikimedia Dumps (Recommended)**

```powershell
# Download latest Kurdish Wikipedia dump
$dumpUrl = "https://dumps.wikimedia.org/ckbwiki/latest/ckbwiki-latest-pages-articles.xml.bz2"
$outputFile = "C:\tesseract\work\corpus\wikipedia\ckbwiki-latest-pages-articles.xml.bz2"

# Create directory
New-Item -ItemType Directory -Force -Path "C:\tesseract\work\corpus\wikipedia"

# Download (approximately 50-100 MB compressed)
Invoke-WebRequest -Uri $dumpUrl -OutFile $outputFile

# Check file size
Get-ChildItem $outputFile | Select-Object Name, Length, LastWriteTime
```

**Option B: Use Wikipedia API (Smaller, faster)**

```python
# For quick testing with latest articles
import requests

def get_recent_articles(count=100):
    url = "https://ckb.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'list': 'recentchanges',
        'rctype': 'new|edit',
        'rclimit': count,
        'format': 'json'
    }
    response = requests.get(url, params=params)
    return response.json()
```

#### Verification

```powershell
# After download, verify file
if (Test-Path "C:\tesseract\work\corpus\wikipedia\ckbwiki-latest-pages-articles.xml.bz2") {
    Write-Host "✅ Wikipedia dump downloaded successfully"
    Get-ChildItem "C:\tesseract\work\corpus\wikipedia\*.bz2" |
        Select-Object Name, @{N='Size(MB)';E={[math]::Round($_.Length/1MB,2)}}
} else {
    Write-Host "❌ Download failed"
}
```

---

### Task 2.2: Extract and Clean Text

**Duration:** 1-2 hours  
**Difficulty:** Medium

#### Extract from XML Dump

We need to:

1. Decompress .bz2 file
2. Parse XML structure
3. Extract article text
4. Remove wiki markup
5. Clean and normalize

#### Python Script: `extract_wikipedia.py`

```python
#!/usr/bin/env python3
"""
Extract clean Kurdish text from Wikipedia dump.
Handles: XML parsing, wiki markup removal, text cleaning
"""

import sys
import bz2
import xml.etree.ElementTree as ET
from pathlib import Path
import re
from typing import Iterator, Tuple

class WikipediaExtractor:
    def __init__(self, dump_path: str, output_path: str):
        self.dump_path = Path(dump_path)
        self.output_path = Path(output_path)

    def extract_text_from_dump(self) -> Iterator[Tuple[str, str]]:
        """
        Extract (title, text) from Wikipedia dump.
        Yields articles one by one for memory efficiency.
        """
        print(f"📖 Opening Wikipedia dump: {self.dump_path}")

        # Handle both .bz2 and plain .xml
        if self.dump_path.suffix == '.bz2':
            f = bz2.open(self.dump_path, 'rt', encoding='utf-8')
        else:
            f = open(self.dump_path, 'r', encoding='utf-8')

        try:
            # Streaming XML parser (memory efficient)
            context = ET.iterparse(f, events=('start', 'end'))
            context = iter(context)
            event, root = next(context)

            title = None
            text = None
            in_page = False
            article_count = 0

            for event, elem in context:
                tag = elem.tag.split('}')[1] if '}' in elem.tag else elem.tag

                if event == 'start' and tag == 'page':
                    in_page = True
                    title = None
                    text = None

                elif event == 'end' and in_page:
                    if tag == 'title':
                        title = elem.text
                    elif tag == 'text':
                        text = elem.text
                    elif tag == 'page':
                        if title and text:
                            article_count += 1
                            if article_count % 100 == 0:
                                print(f"  Processed {article_count} articles...", end='\r')
                            yield (title, text)

                        # Clear to save memory
                        in_page = False
                        root.clear()

            print(f"\n✅ Extracted {article_count} articles")

        finally:
            f.close()

    def clean_wiki_markup(self, text: str) -> str:
        """Remove Wikipedia markup and get clean text."""
        if not text:
            return ""

        # Remove templates {{...}}
        text = re.sub(r'\{\{[^}]+\}\}', '', text)

        # Remove file/image links [[File:...]] [[پەڕگە:...]]
        text = re.sub(r'\[\[(File|Image|پەڕگە):[^\]]+\]\]', '', text, flags=re.IGNORECASE)

        # Convert links [[text]] or [[link|text]] to just text
        text = re.sub(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]', r'\1', text)

        # Remove external links [http://...]
        text = re.sub(r'\[http[^\]]+\]', '', text)

        # Remove refs <ref>...</ref>
        text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
        text = re.sub(r'<ref[^>]*\/>', '', text)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Remove section headers == text ==
        text = re.sub(r'={2,}[^=]+={2,}', '', text)

        # Remove lists * or #
        text = re.sub(r'^\s*[\*#]+\s*', '', text, flags=re.MULTILINE)

        # Remove table markup {| ... |}
        text = re.sub(r'\{\|.*?\|\}', '', text, flags=re.DOTALL)

        # Clean up whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        return text.strip()

    def is_valid_sentence(self, sentence: str) -> bool:
        """Check if sentence is valid for training."""
        # Minimum length
        if len(sentence) < 10:
            return False

        # Must contain Kurdish characters
        kurdish_chars = set('ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنوۆهھەیێ')
        if not any(c in kurdish_chars for c in sentence):
            return False

        # Not too much Latin (some is OK for mixed text)
        latin_count = sum(1 for c in sentence if 'A' <= c <= 'Z' or 'a' <= c <= 'z')
        if latin_count > len(sentence) * 0.3:  # Max 30% Latin
            return False

        # Not too many numbers
        digit_count = sum(1 for c in sentence if c.isdigit())
        if digit_count > len(sentence) * 0.5:
            return False

        return True

    def extract_sentences(self, text: str, min_words: int = 5, max_words: int = 30) -> list:
        """Extract sentences within word count range."""
        # Split on sentence boundaries
        sentences = re.split(r'[.!?؟۔]\s+', text)

        valid_sentences = []
        for sent in sentences:
            sent = sent.strip()
            word_count = len(sent.split())

            if min_words <= word_count <= max_words and self.is_valid_sentence(sent):
                valid_sentences.append(sent)

        return valid_sentences

    def process_dump(self, max_words: int = 100000, min_quality: float = 0.5):
        """
        Main processing pipeline.

        Args:
            max_words: Stop after extracting this many words
            min_quality: Quality threshold (0-1)
        """
        output_file = self.output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)

        total_words = 0
        total_sentences = 0
        articles_used = 0

        with open(output_file, 'w', encoding='utf-8') as out:
            for title, wiki_text in self.extract_text_from_dump():
                # Skip special pages
                if ':' in title:  # Skip Wikipedia:, Template:, Category:, etc.
                    continue

                # Clean wiki markup
                clean_text = self.clean_wiki_markup(wiki_text)

                if not clean_text:
                    continue

                # Extract good sentences
                sentences = self.extract_sentences(clean_text)

                if not sentences:
                    continue

                articles_used += 1

                # Write sentences
                for sent in sentences:
                    out.write(sent + '\n')
                    total_sentences += 1
                    total_words += len(sent.split())

                    # Check if we've reached target
                    if total_words >= max_words:
                        break

                if total_words >= max_words:
                    break

        # Summary
        print(f"\n{'='*70}")
        print(f"📊 EXTRACTION SUMMARY")
        print(f"{'='*70}")
        print(f"Articles processed: {articles_used:,}")
        print(f"Sentences extracted: {total_sentences:,}")
        print(f"Total words: {total_words:,}")
        print(f"Average words/sentence: {total_words/total_sentences:.1f}")
        print(f"Output file: {output_file}")
        print(f"{'='*70}")

        return total_words, total_sentences


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 extract_wikipedia.py <dump.xml.bz2> <output.txt> [max_words]")
        print("Example: python3 extract_wikipedia.py ckbwiki.xml.bz2 ckb_wikipedia.txt 50000")
        sys.exit(1)

    dump_path = sys.argv[1]
    output_path = sys.argv[2]
    max_words = int(sys.argv[3]) if len(sys.argv) > 3 else 50000

    print(f"🚀 Kurdish Wikipedia Extractor")
    print(f"   Dump: {dump_path}")
    print(f"   Output: {output_path}")
    print(f"   Target: {max_words:,} words")
    print()

    extractor = WikipediaExtractor(dump_path, output_path)
    extractor.process_dump(max_words=max_words)

    print("\n✅ Extraction complete!")


if __name__ == '__main__':
    main()
```

#### Run Extraction

```powershell
# Create the extraction script
# (Save above Python code to work/tools/extract_wikipedia.py)

# Run extraction
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/extract_wikipedia.py \
    /mnt/c/tesseract/work/corpus/wikipedia/ckbwiki-latest-pages-articles.xml.bz2 \
    /mnt/c/tesseract/work/corpus/ckb_wikipedia.txt \
    50000

# Expected output:
# 📖 Opening Wikipedia dump: ...
# Processed 100 articles...
# Processed 200 articles...
# ...
# ✅ Extracted 500 articles
#
# ======================================================================
# 📊 EXTRACTION SUMMARY
# ======================================================================
# Articles processed: 500
# Sentences extracted: 8,500
# Total words: 52,000
# Average words/sentence: 6.1
# ======================================================================
```

---

### Task 2.3: Quality Filtering

**Duration:** 30 minutes  
**Difficulty:** Easy

Apply additional quality checks to ensure clean training data.

#### Script: `filter_wikipedia_quality.py`

```python
#!/usr/bin/env python3
"""Filter Wikipedia extracted text for quality."""

import sys
from collections import Counter
import unicodedata

def analyze_text_quality(text: str) -> dict:
    """Analyze text and return quality metrics."""
    # Character distribution
    total_chars = len(text)
    zwnj_count = text.count('\u200c')

    # Count character types
    arabic_script = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    latin = sum(1 for c in text if ('A' <= c <= 'Z') or ('a' <= c <= 'z'))
    digits = sum(1 for c in text if c.isdigit())
    spaces = sum(1 for c in text if c.isspace())

    return {
        'total_chars': total_chars,
        'zwnj_count': zwnj_count,
        'zwnj_pct': (zwnj_count / total_chars * 100) if total_chars > 0 else 0,
        'arabic_pct': (arabic_script / total_chars * 100) if total_chars > 0 else 0,
        'latin_pct': (latin / total_chars * 100) if total_chars > 0 else 0,
        'digit_pct': (digits / total_chars * 100) if total_chars > 0 else 0,
        'space_pct': (spaces / total_chars * 100) if total_chars > 0 else 0,
    }

def filter_quality(input_file: str, output_file: str, min_zwnj_pct: float = 4.0):
    """Filter lines that don't meet quality standards."""

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Input: {len(lines):,} lines")

    good_lines = []
    stats = {
        'too_short': 0,
        'low_zwnj': 0,
        'too_much_latin': 0,
        'too_much_digits': 0,
        'good': 0,
    }

    for line in lines:
        line = line.strip()

        # Too short
        if len(line) < 20:
            stats['too_short'] += 1
            continue

        metrics = analyze_text_quality(line)

        # Check ZWNJ percentage (important for Kurdish!)
        if metrics['zwnj_pct'] < min_zwnj_pct:
            stats['low_zwnj'] += 1
            continue

        # Too much Latin
        if metrics['latin_pct'] > 30:
            stats['too_much_latin'] += 1
            continue

        # Too many digits
        if metrics['digit_pct'] > 40:
            stats['too_much_digits'] += 1
            continue

        stats['good'] += 1
        good_lines.append(line)

    # Write filtered output
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in good_lines:
            f.write(line + '\n')

    print(f"\nFiltering Results:")
    print(f"  Too short: {stats['too_short']:,}")
    print(f"  Low ZWNJ: {stats['low_zwnj']:,}")
    print(f"  Too much Latin: {stats['too_much_latin']:,}")
    print(f"  Too many digits: {stats['too_much_digits']:,}")
    print(f"  ✅ Good: {stats['good']:,}")
    print(f"\nOutput: {output_file}")

    return stats

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 filter_wikipedia_quality.py <input.txt> <output.txt> [min_zwnj_pct]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    min_zwnj_pct = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0

    filter_quality(input_file, output_file, min_zwnj_pct)
```

#### Run Filtering

```powershell
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/filter_wikipedia_quality.py \
    /mnt/c/tesseract/work/corpus/ckb_wikipedia.txt \
    /mnt/c/tesseract/work/corpus/ckb_wikipedia_filtered.txt \
    4.0
```

---

### Task 2.4: Deduplicate and Merge with Existing Corpus

**Duration:** 15 minutes  
**Difficulty:** Easy

Remove duplicates and merge Wikipedia text with existing training corpus.

#### Script: `merge_corpus.py`

```python
#!/usr/bin/env python3
"""Merge Wikipedia corpus with existing training data, removing duplicates."""

def load_corpus(file_path: str) -> set:
    """Load corpus as set of lines."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def merge_corpora(existing_file: str, wikipedia_file: str, output_file: str, backup=True):
    """Merge two corpora, removing duplicates."""

    print("📚 Loading existing corpus...")
    existing = load_corpus(existing_file)
    print(f"   Existing: {len(existing):,} unique lines")

    print("📚 Loading Wikipedia corpus...")
    wikipedia = load_corpus(wikipedia_file)
    print(f"   Wikipedia: {len(wikipedia):,} unique lines")

    # Find new lines
    new_lines = wikipedia - existing
    print(f"\n✨ New unique lines: {len(new_lines):,}")

    # Merge
    merged = existing | wikipedia
    print(f"📦 Total unique lines: {len(merged):,}")

    # Backup existing
    if backup:
        backup_file = existing_file + '.backup_phase2'
        import shutil
        shutil.copy(existing_file, backup_file)
        print(f"💾 Backup saved: {backup_file}")

    # Write merged corpus
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in sorted(merged):  # Sort for consistency
            f.write(line + '\n')

    print(f"✅ Merged corpus saved: {output_file}")

    # Calculate word count
    total_words = sum(len(line.split()) for line in merged)
    print(f"📊 Total words: {total_words:,}")

    return len(merged), total_words

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print("Usage: python3 merge_corpus.py <existing.txt> <wikipedia.txt> <output.txt>")
        sys.exit(1)

    merge_corpora(sys.argv[1], sys.argv[2], sys.argv[3])
```

#### Run Merge

```powershell
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/merge_corpus.py \
    /mnt/c/tesseract/work/corpus/ckb.training_text \
    /mnt/c/tesseract/work/corpus/ckb_wikipedia_filtered.txt \
    /mnt/c/tesseract/work/corpus/ckb.training_text

# Expected output:
# 📚 Loading existing corpus...
#    Existing: 5,261 unique lines
# 📚 Loading Wikipedia corpus...
#    Wikipedia: 7,500 unique lines
#
# ✨ New unique lines: 6,200
# 📦 Total unique lines: 11,461
# 💾 Backup saved: ckb.training_text.backup_phase2
# ✅ Merged corpus saved: ckb.training_text
# 📊 Total words: 65,000
```

---

### Task 2.5: Verify Corpus Quality

**Duration:** 15 minutes  
**Difficulty:** Easy

Final verification before training.

```powershell
# Run verification script
wsl -d Ubuntu -- python3 << 'PYTHON'
text = open('/mnt/c/tesseract/work/corpus/ckb.training_text', 'r', encoding='utf-8').read()

# Basic stats
lines = [l.strip() for l in text.split('\n') if l.strip()]
words = text.split()
chars = len(text)
zwnj = text.count('\u200c')

print("📊 Enhanced Corpus Statistics")
print("="*60)
print(f"Lines: {len(lines):,}")
print(f"Words: {len(words):,}")
print(f"Characters: {chars:,}")
print(f"ZWNJ count: {zwnj:,}")
print(f"ZWNJ percentage: {(zwnj/chars*100):.2f}%")
print()

# Character distribution
arabic = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
latin = sum(1 for c in text if ('A' <= c <= 'Z') or ('a' <= c <= 'z'))

print(f"Script Distribution:")
print(f"  Arabic script: {(arabic/chars*100):.1f}%")
print(f"  Latin script: {(latin/chars*100):.1f}%")
print()

# Kurdish specific characters
kurdish_chars = 'ڕڵێۆەگچژڤھ'
for ch in kurdish_chars:
    count = text.count(ch)
    print(f"  {ch}: {count:,} times")
print("="*60)
print("✅ Corpus ready for training!")
PYTHON
```

---

### Task 2.6: Retrain with Expanded Corpus

**Duration:** 3-4 hours  
**Difficulty:** Easy (automated)

```powershell
# Full training with expanded Wikipedia corpus
.\run_training.ps1 -Mode GenerateTrain -MaxIters 50000 -LatinDigits -MaxPages 100 -CharsPerPage 3000

# Monitor progress
wsl -d Ubuntu -- python3 /mnt/c/tesseract/show_progress.py
```

---

### Task 2.7: Evaluate Results

**Duration:** 30 minutes  
**Difficulty:** Easy

```powershell
# Run comprehensive evaluation
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"

# Analyze results
$results = Import-Csv "C:\tesseract\work\output\real_metrics.csv"
$best = $results | Where-Object { $_.image -eq 'mgk.tif' } |
    Sort-Object { [double]$_.cer } |
    Select-Object -First 1

Write-Host "📊 Phase 2 Results:"
Write-Host "   CER: $($best.cer) ($(100 - [double]$best.cer * 100)% accuracy)"
Write-Host "   PSM: $($best.psm)"
```

---

## 📊 Expected Results

### Corpus Growth

| Metric     | Phase 1 | Phase 2 Target | Actual |
| ---------- | ------- | -------------- | ------ |
| Lines      | 5,261   | 12,000+        | TBD    |
| Words      | 14,456  | 65,000+        | TBD    |
| ZWNJ Count | 8,309   | 40,000+        | TBD    |
| ZWNJ %     | 7.77%   | 7-10%          | TBD    |

### Accuracy Improvement

| Metric          | Baseline | Phase 1 | Phase 2 Target |
| --------------- | -------- | ------- | -------------- |
| **CER**         | 29.60%   | ~33%    | **10-15%**     |
| **Accuracy**    | 70.40%   | ~67%    | **85-90%**     |
| **Improvement** | -        | -3%     | **+15-20%**    |

---

## 🚨 Potential Issues & Solutions

### Issue 1: Download Fails

**Problem:** Wikipedia dump download times out or fails  
**Solution:** Use mirror sites or API approach for smaller dataset

### Issue 2: Too Much Latin/English

**Problem:** Wikipedia articles contain borrowed terms  
**Solution:** Apply stricter Latin percentage filter (max 20%)

### Issue 3: Low ZWNJ Percentage

**Problem:** Extracted text has less than 5% ZWNJ  
**Solution:** Use Kurdish character fixer to add ZWNJs where needed

### Issue 4: Duplicate Content

**Problem:** Same sentences appear multiple times  
**Solution:** Deduplication script removes exact duplicates

### Issue 5: Training Takes Too Long

**Problem:** 100K words = 6+ hours training  
**Solution:** Start with 50K words, evaluate, then expand if needed

---

## 🎯 Success Criteria

### Minimum Acceptable (Phase 2 Complete):

- ✅ Corpus size: 50,000+ words
- ✅ ZWNJ percentage: 6-10%
- ✅ CER: <20% (>80% accuracy)
- ✅ Improvement from Phase 1: +10% accuracy

### Good Result (Phase 2 Success):

- ✅ Corpus size: 65,000+ words
- ✅ ZWNJ percentage: 7-9%
- ✅ CER: <15% (>85% accuracy)
- ✅ Ready for Phase 3

### Exceptional Result (Ahead of Schedule):

- ✅ Corpus size: 80,000+ words
- ✅ ZWNJ percentage: 7-8%
- ✅ CER: <12% (>88% accuracy)
- ✅ May skip Phase 3, go directly to Phase 4

---

## 📅 Timeline

### Day 1 (October 9)

- ☐ Morning (2 hours): Download Wikipedia dump + Extract text
- ☐ Afternoon (2 hours): Filter quality + Merge corpus
- ☐ Evening (4 hours): Start training

### Day 2 (October 10)

- ☐ Morning: Training completes
- ☐ Afternoon: Evaluation + Analysis
- ☐ Decision: Proceed to Phase 3 or iterate Phase 2

---

## 🔄 Iteration Plan

**If CER is 15-20% after Phase 2:**
→ Add more Wikipedia content (target 100K words)
→ Apply targeted error analysis
→ Quick retrain (3-4 hours)

**If CER is 10-15%:**
→ Phase 2 complete, proceed to Phase 3
→ Focus on advanced training techniques

**If CER is <10%:**
→ Exceptional! Skip Phase 3
→ Go directly to Phase 4 (fine-tuning for 95%)

---

## 📝 Phase 2 Checklist

### Preparation

- [ ] Verify internet connection for download
- [ ] Ensure 500MB free disk space
- [ ] Check Python has required libraries (bz2, xml)
- [ ] Backup current corpus

### Execution

- [ ] Download Wikipedia dump
- [ ] Extract text from dump
- [ ] Apply quality filters
- [ ] Merge with existing corpus
- [ ] Verify corpus statistics
- [ ] Run training (3-4 hours)
- [ ] Evaluate results

### Verification

- [ ] ZWNJ percentage 6-10%
- [ ] Corpus size 50K+ words
- [ ] No duplicate lines
- [ ] Training completes without errors
- [ ] CER improves by 10%+

---

## 🎓 Alternative: Quick Wikipedia API Approach

If full dump is too large or complex:

```python
#!/usr/bin/env python3
"""Quick Wikipedia extraction via API (no dump needed)."""

import requests
import time

def get_wikipedia_articles(count=500):
    """Get recent Wikipedia articles via API."""

    url = "https://ckb.wikipedia.org/w/api.php"
    articles = []

    # Get list of random articles
    for batch in range(count // 50):
        params = {
            'action': 'query',
            'list': 'random',
            'rnnamespace': 0,  # Main namespace only
            'rnlimit': 50,
            'format': 'json'
        }

        response = requests.get(url, params=params)
        data = response.json()

        # Get content for each article
        for page in data['query']['random']:
            page_id = page['id']

            # Get article content
            content_params = {
                'action': 'query',
                'pageids': page_id,
                'prop': 'extracts',
                'explaintext': True,
                'format': 'json'
            }

            content_response = requests.get(url, params=content_params)
            content_data = content_response.json()

            extract = content_data['query']['pages'][str(page_id)].get('extract', '')
            if extract and len(extract) > 100:
                articles.append(extract)

            time.sleep(0.1)  # Rate limiting

        print(f"Fetched {len(articles)} articles...", end='\r')

    return articles

# Usage
articles = get_wikipedia_articles(500)
with open('ckb_wikipedia_quick.txt', 'w', encoding='utf-8') as f:
    for article in articles:
        # Extract sentences
        sentences = article.split('.')
        for sent in sentences:
            sent = sent.strip()
            if 20 < len(sent) < 300:
                f.write(sent + '\n')

print(f"✅ Extracted {len(articles)} articles to ckb_wikipedia_quick.txt")
```

---

**Next Phase:** Phase 3 - Advanced Training (if needed)  
**Documentation:** See PHASE3_ADVANCED_TRAINING.md

**Status:** 📋 READY TO START  
**Estimated Completion:** October 10-11, 2025
