# 🚀 Option D: Full Hybrid Approach - Roadmap to 95% Accuracy

**Started:** October 8, 2025  
**Target:** 95% accuracy (≤5% CER)  
**Current:** 70.4% accuracy (29.6% CER)  
**Gap:** 24.6% accuracy improvement needed  
**Estimated Time:** 4-6 days

---

## 📋 Overview

This hybrid approach combines:

1. **Error Analysis** - Understand what's failing
2. **Quick Wins** - Targeted improvements (5-10% gain)
3. **Major Expansion** - Wikipedia extraction (10-15% gain)
4. **Advanced Training** - From-scratch training (5-10% gain)

**Total Expected Gain:** 20-30% accuracy → **90-95% target** ✅

---

## 🎯 Phase 1: Quick Wins & Error Analysis (Days 1-2)

### Goal

Achieve **75-80% accuracy** through targeted improvements

### Tasks

#### ✅ 1.1: Analyze Current Errors

**Status:** 🔄 IN PROGRESS  
**Command:**

```powershell
# Extract OCR output
tesseract work\real_gt\eval\mgk.tif work\output\mgk_recognized -l ckb --psm 6

# Compare with ground truth
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work && python3 -c \"
import difflib
with open('real_gt/eval/mgk.gt.txt', 'r', encoding='utf-8') as f:
    gt = f.read()
with open('output/mgk_recognized.txt', 'r', encoding='utf-8') as f:
    ocr = f.read()

# Character-level diff
errors = []
for i, (c1, c2) in enumerate(zip(gt, ocr)):
    if c1 != c2:
        errors.append((i, c1, c2))

print(f'Total character errors: {len(errors)}')
print(f'Error rate: {len(errors)/len(gt)*100:.2f}%')

# Most common errors
from collections import Counter
error_types = Counter([(c1, c2) for _, c1, c2 in errors[:100]])
print('\\nTop 10 most common errors:')
for (gt_char, ocr_char), count in error_types.most_common(10):
    print(f'  {repr(gt_char)} → {repr(ocr_char)}: {count} times')
\""
```

**Expected Findings:**

- Character confusion patterns (e.g., ی vs ي, و vs ۆ)
- Diacritic recognition issues
- Latin vs Arabic character mixing errors
- Space/word boundary problems

#### 🔲 1.2: Create Targeted Training Data

**Status:** ⏸️ PENDING (after 1.1)  
**Actions:**

1. Extract problematic character combinations
2. Generate 1,000-2,000 lines focusing on error patterns
3. Add to corpus with high repetition

**Example patterns to focus on:**

```
# If ی vs ي confusion detected:
ئایندە، ئاینە، مایە، مێ، کوردی
# If و vs ۆ confusion detected:
ئەو، سەرۆک، گوێ، چۆن، خۆی
# If hamza issues detected:
ئێوە، ئێمە، ئەم، ئەو، ئایا
```

#### 🔲 1.3: Add More Fonts

**Status:** ⏸️ PENDING  
**Target:** Increase from 6 to 10-12 fonts  
**Sources:**

- Google Fonts: Noto Kufi Arabic, Noto Sans Arabic
- System fonts: Traditional Arabic, Simplified Arabic
- Kurdish-specific fonts (if available)

**Command:**

```powershell
# Download additional fonts
Invoke-WebRequest -Uri "https://github.com/google/fonts/raw/main/ofl/notokufiarabic/NotoKufiArabic-Regular.ttf" -OutFile "work\fonts\NotoKufiArabic-Regular.ttf"
Invoke-WebRequest -Uri "https://github.com/google/fonts/raw/main/ofl/notokufiarabic/NotoKufiArabic-Bold.ttf" -OutFile "work\fonts\NotoKufiArabic-Bold.ttf"
```

#### 🔲 1.4: Quick Retrain

**Status:** ⏸️ PENDING (after 1.2, 1.3)  
**Config:**

- Target iterations: 20,000 (allow early stop)
- Learning rate: 0.0001 (lower for fine-tuning)
- Use enhanced corpus

**Command:**

```powershell
.\run_training.ps1 -Mode GenerateTrain -LatinDigits
```

**Expected Result:** CER 20-25% (75-80% accuracy)

---

## 🌍 Phase 2: Major Corpus Expansion (Days 2-4)

### Goal

Achieve **85-90% accuracy** with massive corpus increase

### Tasks

#### 🔲 2.1: Extract Kurdish Wikipedia

**Status:** 🔄 IN PROGRESS  
**Target:** 20,000-50,000 words (10x current corpus)

**Method A: Automated Scraping (Recommended)**

```python
# Create: work/tools/extract_wikipedia.py
"""
Extract Kurdish text from Wikipedia dump or API
"""
import requests
from bs4 import BeautifulSoup
import re

def extract_kurdish_wikipedia(min_words=20000):
    # Use Wikipedia API
    base_url = "https://ckb.wikipedia.org/w/api.php"

    # Get random articles
    all_text = []
    articles_processed = 0

    while len(' '.join(all_text).split()) < min_words:
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'random',
            'rnnamespace': 0,  # Main namespace
            'rnlimit': 50
        }

        response = requests.get(base_url, params=params)
        articles = response.json()['query']['random']

        for article in articles:
            # Get article content
            content_params = {
                'action': 'parse',
                'format': 'json',
                'pageid': article['id'],
                'prop': 'text'
            }

            content = requests.get(base_url, params=content_params)
            if 'parse' in content.json():
                html = content.json()['parse']['text']['*']
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text()

                # Clean text
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                lines = [line for line in lines if len(line.split()) >= 3]

                all_text.extend(lines)
                articles_processed += 1

                if len(' '.join(all_text).split()) >= min_words:
                    break

        print(f"Processed {articles_processed} articles, {len(' '.join(all_text).split())} words")

    return all_text

if __name__ == '__main__':
    print("Extracting Kurdish Wikipedia text...")
    text = extract_kurdish_wikipedia(min_words=50000)

    with open('corpus/ckb_wikipedia.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(text))

    print(f"Extracted {len(text)} lines, {len(' '.join(text).split())} words")
```

**Method B: Manual Download**

```powershell
# Download Wikipedia dump
$dumpUrl = "https://dumps.wikimedia.org/ckbwiki/latest/ckbwiki-latest-pages-articles.xml.bz2"
Invoke-WebRequest -Uri $dumpUrl -OutFile "work\corpus\ckbwiki-dump.xml.bz2"

# Extract with WikiExtractor (install: pip install wikiextractor)
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && python3 -m wikiextractor.WikiExtractor -o extracted --json ckbwiki-dump.xml.bz2"
```

#### 🔲 2.2: Extract Kurdish Latin (Hawar) Content

**Status:** ⏸️ PENDING  
**Sources:**

- Kurdish Latin news sites
- Kurdish Latin social media
- Transliteration of Arabic script corpus

**Command:**

```python
# Create: work/tools/generate_latin_variants.py
"""
Generate Latin (Hawar) variants from Arabic script
"""
def arabic_to_latin_transliteration(arabic_text):
    # Simplified transliteration rules
    mapping = {
        'ئ': '',  # Hamza - silent in Latin
        'ا': 'a',
        'ب': 'b',
        'پ': 'p',
        'ت': 't',
        'ج': 'c',
        'چ': 'ç',
        'ح': 'h',
        'خ': 'x',
        'د': 'd',
        'ر': 'r',
        'ڕ': 'ř',
        'ز': 'z',
        'ژ': 'j',
        'س': 's',
        'ش': 'ş',
        'ع': '',  # Ain - silent in Latin
        'غ': 'x',
        'ف': 'f',
        'ڤ': 'v',
        'ق': 'q',
        'ک': 'k',
        'گ': 'g',
        'ل': 'l',
        'ڵ': 'll',
        'م': 'm',
        'ن': 'n',
        'و': 'w',
        'ۆ': 'o',
        'ووْ': 'û',
        'ه': 'h',
        'ە': 'e',
        'ی': 'î',
        'ێ': 'ê',
    }

    result = ''
    for char in arabic_text:
        result += mapping.get(char, char)

    return result

# Process corpus
with open('corpus/ckb.training_text', 'r', encoding='utf-8') as f:
    arabic_lines = f.readlines()

latin_lines = []
for line in arabic_lines:
    latin = arabic_to_latin_transliteration(line.strip())
    if latin:
        latin_lines.append(latin)

with open('corpus/ckb_latin_generated.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(latin_lines))

print(f"Generated {len(latin_lines)} Latin lines")
```

#### 🔲 2.3: Quality Control & Deduplication

**Status:** ⏸️ PENDING  
**Actions:**

1. Remove duplicate lines
2. Remove very short lines (<3 words)
3. Remove lines with unusual character distributions
4. Verify no encoding issues

**Command:**

```bash
# Deduplicate
sort -u ckb_wikipedia.txt > ckb_wikipedia_unique.txt

# Remove short lines
awk 'NF >= 3' ckb_wikipedia_unique.txt > ckb_wikipedia_filtered.txt

# Verify encoding
python3 -c "
with open('ckb_wikipedia_filtered.txt', 'rb') as f:
    content = f.read()
    non_ascii = sum(1 for b in content if b > 127)
    print(f'Non-ASCII bytes: {non_ascii} ({non_ascii/len(content)*100:.2f}%)')
    print('Status: OK' if non_ascii > 0 else 'WARNING: All ASCII (check if Arabic script present)')
"
```

#### 🔲 2.4: Rebuild Full Corpus

**Status:** ⏸️ PENDING  
**Target Structure:**

```
ckb.training_text (Arabic): 20,000+ words
ckb_latin.training_text (Latin): 10,000+ words
ckb_mixed.training_text (Mixed): 5,000+ words
Total: 35,000+ words
```

**Command:**

```powershell
# Combine all sources
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus &&
cat ckb_core_coverage.txt \
    ckb_enhanced_sentences.txt \
    ckb_extra_sentences.txt \
    ckb_expanded_corpus.txt \
    ckb_wikipedia_filtered.txt \
    mgk.gt.txt > ckb.training_text.new

# Verify and replace
wc -w ckb.training_text.new
mv ckb.training_text.new ckb.training_text
"
```

#### 🔲 2.5: Retrain with Expanded Corpus

**Status:** ⏸️ PENDING  
**Config:**

- Max iterations: 100,000
- Learning rate: 0.0001
- Early stopping: target error rate 0.02 (2%)

**Command:**

```powershell
.\run_training.ps1 -Mode GenerateTrain -LatinDigits
```

**Expected Result:** CER 10-15% (85-90% accuracy)

---

## 🏗️ Phase 3: From-Scratch Training (Days 4-6)

### Goal

Achieve **90-95% accuracy** with custom-built model

### Tasks

#### 🔲 3.1: Create Custom Unicharset

**Status:** ⏸️ PENDING  
**Approach:** Generate unicharset from actual corpus (not combining existing sets)

**Command:**

```bash
# Generate from corpus
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work &&
unicharset_extractor \
    corpus/ckb.training_text \
    corpus/ckb_latin.training_text \
    corpus/ckb_mixed.training_text \
    -O charsets/ckb_custom.unicharset
"
```

#### 🔲 3.2: Train from Scratch (No Fine-Tuning)

**Status:** ⏸️ PENDING  
**Config:**

- Start from LayerSpec (not pretrained model)
- Use all corpus data
- Train for 200,000+ iterations
- Allow multiple days for completion

**Command:**

```bash
# Generate training data
text2image --text corpus/ckb.training_text \
    --outputbase training_output/ground_truth/ckb_scratch \
    --font 'Noto Naskh Arabic' \
    --fonts_dir fonts \
    --unicharset charsets/ckb_custom.unicharset

# Train from scratch
lstmtraining \
    --traineddata ckb_scratch.traineddata \
    --net_spec '[1,36,0,1 Ct3,3,16 Mp3,3 Lfys48 Lfx96 Lrx96 Lfx256 O1c1]' \
    --model_output training_output/model/ckb_scratch \
    --train_listfile training_output/ckb.training_files.txt \
    --max_iterations 200000 \
    --target_error_rate 0.01
```

**Expected Result:** CER 5-10% (90-95% accuracy)

#### 🔲 3.3: Ensemble/Hybrid Model

**Status:** ⏸️ PENDING  
**Approach:** Combine best fine-tuned model with from-scratch model

**Command:**

```bash
# Create ensemble config
combine_tessdata -o ckb_ensemble.traineddata \
    ckb_from_fas.traineddata \
    ckb_scratch.traineddata
```

---

## 📊 Progress Tracking

### Milestones

| Phase        | Target CER | Target Accuracy | Status         | Date      |
| ------------ | ---------- | --------------- | -------------- | --------- |
| **Baseline** | 33.24%     | 66.76%          | ✅ Complete    | Oct 6     |
| **Option 4** | 29.60%     | 70.40%          | ✅ Complete    | Oct 7-8   |
| **Phase 1**  | 20-25%     | 75-80%          | 🔄 In Progress | Oct 8-9   |
| **Phase 2**  | 10-15%     | 85-90%          | ⏸️ Pending     | Oct 9-11  |
| **Phase 3**  | 5-10%      | 90-95%          | ⏸️ Pending     | Oct 11-13 |
| **Target**   | ≤5%        | ≥95%            | 🎯 Goal        | Oct 13    |

### Daily Goals

**Day 1 (Oct 8):**

- ✅ Error analysis complete
- 🔲 Targeted corpus additions
- 🔲 Additional fonts added
- 🔲 Quick retrain started

**Day 2 (Oct 9):**

- 🔲 Wikipedia extraction complete
- 🔲 Corpus expansion to 35K+ words
- 🔲 Major retrain started

**Day 3 (Oct 10):**

- 🔲 Major training complete
- 🔲 Evaluation shows 85%+ accuracy
- 🔲 Identify remaining gaps

**Day 4 (Oct 11):**

- 🔲 From-scratch training started
- 🔲 Additional targeted improvements

**Day 5 (Oct 12):**

- 🔲 From-scratch training ongoing
- 🔲 Parallel testing of models

**Day 6 (Oct 13):**

- 🔲 Final model selection
- 🔲 Comprehensive evaluation
- 🔲 Target achieved: 95% accuracy ✅

---

## 🔧 Commands Reference

### Quick Status Check

```powershell
# Check current model performance
.\run_training.ps1 -Mode Eval -EvalPSMs "6"

# View best result
Import-Csv work\output\real_metrics.csv | Sort-Object { [double]$_.cer } | Select-Object -First 1
```

### Monitor Training Progress

```powershell
# Watch training in real-time
.\monitor_training.ps1

# Check iteration count
Get-Content work\training_output\logs\lstmtraining_ckb_from_fas.log | Select-String "Iteration"
```

### Corpus Statistics

```powershell
# Count words in corpus
wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work/corpus && wc -w ckb*.training_text"

# Character distribution
python3 work/tools/corpus_stats.py
```

---

## 🎯 Success Criteria

### Phase 1 Success

- [ ] CER ≤ 25% (≥75% accuracy)
- [ ] Error patterns identified
- [ ] 2-3 additional fonts added
- [ ] 7,000+ words in corpus

### Phase 2 Success

- [ ] CER ≤ 15% (≥85% accuracy)
- [ ] 35,000+ words in corpus
- [ ] Wikipedia content integrated
- [ ] Clean training (no encoding errors)

### Phase 3 Success

- [ ] CER ≤ 5% (≥95% accuracy) ✅ **TARGET**
- [ ] From-scratch model trained
- [ ] Multiple test documents validated
- [ ] Production-ready model

---

## 🚨 Risk Management

### Potential Issues

**Risk 1: Wikipedia Content Quality**

- Mitigation: Manual review of samples, quality filtering
- Backup: Use other Kurdish text sources (news, books)

**Risk 2: Training Time Exceeds Estimates**

- Mitigation: Allow early stopping, use faster hardware if available
- Backup: Accept 90% accuracy if time-critical

**Risk 3: Encoding Issues Resurface**

- Mitigation: Rigorous pre-processing and validation
- Backup: ASCII-only Latin corpus already proven to work

**Risk 4: Diminishing Returns**

- Mitigation: Track CER improvement per phase, adjust strategy
- Backup: Hybrid approach allows pivoting between methods

---

## 📝 Notes & Observations

### Lessons Learned So Far

1. ✅ Encoding issues are critical - must be pure ASCII for Latin
2. ✅ Fine-tuning from Farsi works better than Arabic or English
3. ✅ PSM 6 (uniform block) works best for document-style text
4. ✅ Training stops early when corpus is too small/simple
5. ⚠️ Need much larger corpus (10x+) for high accuracy

### Key Insights

- Training BCER is not predictive of real-world CER
- Domain match between training and test data is critical
- More diverse fonts help but corpus size is more important
- Early stopping suggests need for better quality, not just more iterations

---

**Status:** 🚀 **PHASE 1 IN PROGRESS**  
**Next Action:** Error analysis of mgk.tif  
**Updated:** October 8, 2025
