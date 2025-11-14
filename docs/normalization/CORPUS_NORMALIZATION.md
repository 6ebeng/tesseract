# Corpus Normalization Documentation

**Project:** Kurdish (Sorani) OCR Training - Tesseract  
**Purpose:** Comprehensive guide to corpus normalization processes  
**Last Updated:** November 14, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Normalization Pipeline](#normalization-pipeline)
3. [Normalization Tools](#normalization-tools)
4. [Character-Level Normalization](#character-level-normalization)
5. [Text Processing Rules](#text-processing-rules)
6. [Corpus Building Workflow](#corpus-building-workflow)
7. [Quality Validation](#quality-validation)
8. [Usage Examples](#usage-examples)
9. [Best Practices](#best-practices)

---

## Overview

### What is Corpus Normalization?

Corpus normalization is the process of converting raw Kurdish text into a standardized, consistent format suitable for Tesseract OCR training. This ensures:

- **Character consistency** - Unified Kurdish character forms (Sorani standard)
- **Unicode normalization** - NFC (Canonical Composition) throughout
- **ZWNJ preservation** - Critical for Kurdish word boundaries (6-10% density required)
- **Encoding cleanup** - Remove control characters, diacritics, and malformed text
- **Quality assurance** - Deduplicate, balance character distribution

### Why Normalize?

**Problem:** Kurdish text from different sources uses inconsistent characters:
- Arabic vs. Kurdish letter forms (ك vs. ک, ي vs. ی)
- Persian vs. Arabic-Indic digits (۰ vs. ٠)
- Decomposed vs. precomposed Unicode (NFD vs. NFC)
- Mixed punctuation (, vs. ،)
- Unwanted control characters (tatweel, ZWJ, bidi marks)

**Solution:** Normalization creates a **single canonical form** that:
- ✅ Improves training consistency
- ✅ Reduces model confusion
- ✅ Increases OCR accuracy (76.9% achieved with proper normalization)
- ✅ Maintains critical ZWNJ density (9.33% in production news corpus)

---

## Normalization Pipeline

### Full Pipeline Flow

```
Raw Corpus Sources
    ↓
┌─────────────────────────────────────┐
│ 1. Character Normalization          │
│    - NFC Unicode normalization      │
│    - Letter form unification        │
│    - Digit standardization          │
│    - Punctuation normalization      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. Control Character Cleanup        │
│    - Remove tatweel (U+0640)        │
│    - Remove ZWJ (U+200D)            │
│    - Remove bidi marks              │
│    - PRESERVE ZWNJ (U+200C) ⚠️      │
│    - Strip diacritics (Mn)          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. Kurdish Character Fixing         │
│    - Pattern-based corrections      │
│    - Word-level fixes               │
│    - OCR error corrections          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. Whitespace Normalization         │
│    - Collapse multiple spaces       │
│    - Trim lines                     │
│    - Preserve line breaks           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 5. Deduplication                    │
│    - Remove duplicate lines         │
│    - Preserve order                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 6. Character Balancing              │
│    - Boost rare characters          │
│    - Target minimum counts          │
│    - Balance digits/punctuation     │
└─────────────────────────────────────┘
    ↓
Normalized Training Corpus
```

### Processing Stages

| Stage | Tool | Input | Output | Purpose |
|-------|------|-------|--------|---------|
| **1. Gathering** | Manual/Scraper | Raw sources | `corpus/*.txt` | Collect text |
| **2. Validation** | `validate_source_quality.py` | Raw text | ACCEPT/REJECT | Check ZWNJ 6-10% |
| **3. Normalization** | `kurdish_character_fixer.py` | Raw text | Normalized text | Unify characters |
| **4. Building** | `corpus_build.py` | `corpus/*.txt` | `ckb.training_text.final` | Build final corpus |
| **5. Blending** | `blend_corpus.py` | Multiple sources | Blended corpus | Optimize ZWNJ |
| **6. Generation** | `generate_ckb_training_data.sh` | Final corpus | Training images | Create GT |

---

## Normalization Tools

### 1. Kurdish Character Fixer

**File:** `work/kurdish_character_fixer.py`

**Purpose:** Core normalization engine for Kurdish Sorani text

**Features:**
- Unicode NFC normalization
- Arabic → Kurdish letter form conversion
- Persian → Arabic-Indic digit conversion
- Punctuation normalization
- Control character cleanup (preserves ZWNJ!)
- Pattern-based character corrections
- Word-level fixes for common OCR errors

**Usage:**

```bash
# From file (default: preserves Arabic words)
python work/kurdish_character_fixer.py input.txt output.txt

# From stdin
cat input.txt | python work/kurdish_character_fixer.py > output.txt

# Within Python - Smart mode (default)
from kurdish_character_fixer import KurdishCharacterFixer
fixer = KurdishCharacterFixer(preserve_arabic_words=True)
fixed_text = fixer.fix_kurdish_text(raw_text)

# Within Python - Aggressive mode
fixer = KurdishCharacterFixer(preserve_arabic_words=False)
fixed_text = fixer.fix_kurdish_text(raw_text)
```

### 2. Corpus Builder

**File:** `work/tools/corpus_build.py`

**Purpose:** Build balanced final training corpus from sources

**Features:**
- Scans all `work/corpus/*.txt` files
- Applies character fixer (optional with `--fixer`)
- NFC normalization
- Line deduplication
- Character balancing for rare Kurdish letters
- Generates statistics

**Usage:**

```bash
cd /mnt/c/tesseract/work

# Basic build (preserves Arabic words - recommended)
python3 tools/corpus_build.py

# With character fixer (preserves Arabic words)
python3 tools/corpus_build.py --fixer

# With character fixer (aggressive mode - convert all Arabic chars)
python3 tools/corpus_build.py --fixer --no-preserve-arabic

# Target minimum character counts
python3 tools/corpus_build.py --fixer --min-count 5000
```

**Output:**
- `corpus/ckb.training_text.final` - Final normalized corpus
- `output/corpus_build_stats.txt` - Character statistics

### 3. Corpus Blender

**File:** `work/tools/blend_corpus.py`

**Purpose:** Intelligently blend multiple sources to achieve target ZWNJ density

**Features:**
- Analyzes ZWNJ density per source
- Calculates optimal blend ratios
- Targets specific ZWNJ percentage (default: 8.0%)
- Quality validation

**Usage:**

```bash
cd /mnt/c/tesseract/work

# Blend news + biographical to reach 8% ZWNJ
python3 tools/blend_corpus.py \
  --sources corpus/news.txt corpus/biographical.txt \
  --output corpus/blended.txt \
  --target-zwnj 8.0

# Equal proportions (no weighting)
python3 tools/blend_corpus.py \
  --sources corpus/source1.txt corpus/source2.txt \
  --output corpus/blended.txt \
  --equal
```

### 4. Source Quality Validator

**File:** `work/tools/validate_source_quality.py`

**Purpose:** Validate ZWNJ density before using a source

**Critical Rule:** **ALWAYS validate BEFORE acquiring full text!**

**Usage:**

```bash
cd /mnt/c/tesseract/work

# Validate sample
python3 tools/validate_source_quality.py sample.txt

# Expected output:
# ✅ ACCEPT: 8.5% ZWNJ (6-10% range)
# ❌ REJECT: 0.3% ZWNJ (below 6% minimum)
```

**Decision Logic:**
- **6-10% ZWNJ** → ✅ ACCEPT (proceed with source)
- **< 6% ZWNJ** → ❌ REJECT (will degrade training)
- **> 10% ZWNJ** → ⚠️ WARNING (verify quality, may be okay)

### 5. Run Training (PowerShell Launcher)

**File:** `run_training.ps1`

**Purpose:** Windows launcher for entire pipeline

**Normalization Options:**

```powershell
# Build corpus with normalization (preserves Arabic words - recommended)
.\run_training.ps1 -Mode BuildCorpus -UseFixer

# Aggressive mode (convert all Arabic characters to Kurdish)
.\run_training.ps1 -Mode BuildCorpus -UseFixer -NoPreserveArabic

# Keep RTL control characters
.\run_training.ps1 -Mode BuildCorpus -UseFixer -KeepRTLControls

# Balance digits and punctuation
.\run_training.ps1 -Mode BuildCorpus -UseFixer `
  -BalanceDigits -BalanceLatinDigits -BalancePuncs

# Set minimum character count
.\run_training.ps1 -Mode BuildCorpus -UseFixer -CorpusMinCount 5000

# Full balanced build (preserves Arabic words)
.\run_training.ps1 -Mode BuildCorpus -UseFixer `
  -BalanceDigits -BalanceLatinDigits -BalancePuncs `
  -CorpusMinCount 3000
```

---

## Character-Level Normalization

### Letter Form Unification

**Purpose:** Convert Arabic letter forms to Kurdish standard (Sorani)

#### Basic Character Mappings

| Arabic Form | Kurdish Form | Character Name |
|-------------|--------------|----------------|
| `ك` U+0643 | `ک` U+06A9 | KEHEH (not Arabic KAF) |
| `ي` U+064A | `ی` U+06CC | FARSI YEH (not Arabic YEH) |
| `ى` U+0649 | `ە` U+06D5 | AE (when misused as alef maksura) |
| `ة` U+0629 | `ە` U+06D5 | AE (not teh marbuta) |
| **`ه‌`** U+0647+U+200C | **`ە`** U+06D5 | **HEH + ZWNJ → AE (Kurdish-specific)** |

**Important Kurdish-specific rule:**
- In Kurdish, `ه` (HEH) followed by ZWNJ is commonly used where `ە` (AE) should be
- This normalization converts `ه‌` → `ە` automatically
- Example: `گه‌وره` → `گەوره` (big/great)

#### Hamza Variant Normalizations

| Arabic Form | Kurdish Form | Character Name |
|-------------|--------------|----------------|
| `آ` U+0622 | `ئا` U+0626+U+0627 | ALEF WITH MADDA ABOVE → HAMZA + ALEF |
| `أ` U+0623 | `ئا` U+0626+U+0627 | ALEF WITH HAMZA ABOVE → HAMZA + ALEF |
| `إ` U+0625 | `ئی` U+0626+U+06CC | ALEF WITH HAMZA BELOW → HAMZA + YEH |
| `ؤ` U+0624 | `ئو` U+0626+U+0648 | WAW WITH HAMZA ABOVE → HAMZA + WAW |
| `ۀ` U+06C0 | `هە` U+0647+U+06D5 | HEH WITH YEH ABOVE → HEH + AE |

#### Extra Arabic/Persian Characters (Not Used in Kurdish)

**Important:** Kurdish texts often contain Arabic words (religious terms, formal language, proper nouns). The fixer has **two modes**:

##### 1. Smart Mode (Default) - Preserves Arabic Words

Detects and preserves actual Arabic words while normalizing Kurdish text:

**Preserved:**
- Religious terms: الله، محمد، القرآن، الصلاة
- Arabic phrases: إن شاء الله، بسم الله، الحمد لله
- Words with Arabic markers: ال (definite article), ة (teh marbuta ending)
- Proper nouns with Arabic-only characters

**Normalized in Kurdish words:**

| Arabic/Persian | Kurdish Equivalent | Example |
|----------------|-------------------|---------|
| `ص` U+0635 | `س` U+0633 | Kurdish word with ص → س |
| `ض` U+0636 | `د` U+062F | Kurdish word with ض → د |
| `ط` U+0637 | `ت` U+062A | Kurdish word with ط → ت |
| `ظ` U+0638 | `ز` U+0632 | Kurdish word with ظ → ز |
| `ذ` U+0630 | `د` U+062F | Kurdish word with ذ → د |
| `ث` U+062B | `ت` U+062A | Kurdish word with ث → ت |

##### 2. Aggressive Mode - Convert All

Converts all Arabic characters to Kurdish phonetics (use only if your corpus is pure Kurdish):

| Arabic/Persian | Kurdish Equivalent | Reason |
|----------------|-------------------|---------|
| `ص` U+0635 | `س` U+0633 | SAD → SEEN (closest sound) |
| `ض` U+0636 | `د` U+062F | DAD → DAL (closest sound) |
| `ط` U+0637 | `ت` U+062A | TAH → TEH (closest sound) |
| `ظ` U+0638 | `ز` U+0632 | ZAH → ZAIN (closest sound) |
| `ذ` U+0630 | `د` U+062F | THAL → DAL (closest sound) |
| `ث` U+062B | `ت` U+062A | THEH → TEH (closest sound) |

**Example - Smart Mode (Default):**

```python
from kurdish_character_fixer import KurdishCharacterFixer

# Smart mode: preserves Arabic words
fixer = KurdishCharacterFixer(preserve_arabic_words=True)

text = "ئەمڕۆ الصلاة کردم"  # "Today I prayed"
fixed = fixer.fix_kurdish_text(text)
# Result: "ئەمڕۆ الصلاة کردم"  (الصلاة preserved)

text = "بەصرە شارێکە"  # Made-up Kurdish word with ص
fixed = fixer.fix_kurdish_text(text)
# Result: "بەسرە شارێکە"  (ص → س in Kurdish word)
```

**Example - Aggressive Mode:**

```python
# Aggressive mode: convert everything
fixer = KurdishCharacterFixer(preserve_arabic_words=False)

text = "ئەمڕۆ الصلاة کردم"
fixed = fixer.fix_kurdish_text(text)
# Result: "ئەمڕۆ السلاة کردم"  (الصلاة also converted)
```

**Usage Recommendations:**

| Corpus Type | Mode | Reason |
|-------------|------|--------|
| **News articles** | Smart (default) | Contains Arabic proper nouns, quotes |
| **Social media** | Smart (default) | Mixed Kurdish-Arabic common |
| **Religious texts** | Smart (default) | Many Arabic terms preserved |
| **Literature** | Smart (default) | May contain Arabic loanwords |
| **Pure Kurdish** | Aggressive | Only if certain corpus is 100% Kurdish |
| **Technical/Scientific** | Smart (default) | May have Arabic terminology |

**Code Example:**

```python
letter_map = {
    # Basic Kurdish forms
    '\u0643': '\u06A9',  # ك -> ک (KEHEH)
    '\u064A': '\u06CC',  # ي -> ی (FARSI YEH)
    '\u0649': '\u06D5',  # ى -> ە (AE)
    '\u0629': '\u06D5',  # ة -> ە (AE)
    # Hamza variants
    '\u0622': '\u0626\u0627',  # آ -> ئا
    '\u0623': '\u0626\u0627',  # أ -> ئا
    '\u0625': '\u0626\u06CC', # إ -> ئی
    '\u0624': '\u0626\u0648',  # ؤ -> ئو
    '\u06c0': '\u0647\u06d5',  # ۀ -> هە
}

extra_arabic_map = {
    # Extra Arabic/Persian not in Kurdish
    '\u0635': '\u0633',  # ص -> س
    '\u0636': '\u062F',  # ض -> د
    '\u0637': '\u062A',  # ط -> ت
    '\u0638': '\u0632',  # ظ -> ز
    '\u0630': '\u062F',  # ذ -> د
}
```

### Digit Standardization

**Purpose:** Convert Persian digits to Arabic-Indic (Sorani default)

| Persian Digit | Arabic-Indic | Decimal |
|---------------|--------------|---------|
| `۰` U+06F0 | `٠` U+0660 | 0 |
| `۱` U+06F1 | `١` U+0661 | 1 |
| `۲` U+06F2 | `٢` U+0662 | 2 |
| `۳` U+06F3 | `٣` U+0663 | 3 |
| `۴` U+06F4 | `٤` U+0664 | 4 |
| `۵` U+06F5 | `٥` U+0665 | 5 |
| `۶` U+06F6 | `٦` U+0666 | 6 |
| `۷` U+06F7 | `٧` U+0667 | 7 |
| `۸` U+06F8 | `٨` U+0668 | 8 |
| `۹` U+06F9 | `٩` U+0669 | 9 |

**Note:** Latin digits (0-9) are **preserved** for mixed-script text.

### Punctuation Normalization

**Purpose:** Use Arabic punctuation forms

| Latin | Arabic | Character Name |
|-------|--------|----------------|
| `,` | `،` | ARABIC COMMA |
| `?` | `؟` | ARABIC QUESTION MARK |
| `%` | `٪` | ARABIC PERCENT SIGN |
| `;` | `؛` | ARABIC SEMICOLON |

**Code Example:**

```python
punc_map = {
    ',': '،',  # ARABIC COMMA
    '?': '؟',  # ARABIC QUESTION MARK
    '%': '٪',  # ARABIC PERCENT SIGN
    ';': '؛',  # ARABIC SEMICOLON
}
```

### Control Character Handling

**CRITICAL: ZWNJ Must Be Preserved!**

| Character | Action | Reason |
|-----------|--------|--------|
| **ZWNJ** `U+200C` | ✅ **PRESERVE** | **Essential for Kurdish word boundaries!** |
| Tatweel `U+0640` | ❌ Remove | Decorative, not semantic |
| ZWJ `U+200D` | ❌ Remove | Conflicts with ZWNJ |
| LRM `U+200E` | ❌ Remove | Not needed in normalized text |
| RLM `U+200F` | ❌ Remove | Not needed in normalized text |
| Bidi controls | ❌ Remove | RTL handled by Unicode |

**Why ZWNJ is Critical:**

```
Without ZWNJ: دەگەڕێتەوە (wrong joining)
With ZWNJ:    دە‌گەڕێتەوە (correct - space invisible here)

News corpus ZWNJ:      9.33% → 76.9% accuracy ✅
Wikipedia ZWNJ:        0.11% → Training failed ❌
```

### Diacritic Removal

**Purpose:** Remove harakat (Arabic vowel marks) - Unicode category `Mn`

```python
# Strip all combining marks (diacritics)
text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
```

**Removed:**
- Fatha `َ` U+064E
- Damma `ُ` U+064F
- Kasra `ِ` U+0650
- Sukun `ْ` U+0652
- Shadda `ّ` U+0651
- Etc.

---

## Text Processing Rules

### Unicode NFC Normalization

**Applied:** Throughout entire pipeline

**Purpose:** 
- Ensure precomposed forms (e.g., `ۆ` as single codepoint, not `و` + combining)
- Stabilize character shaping across fonts
- Enable consistent comparison and deduplication

```python
import unicodedata
text = unicodedata.normalize('NFC', text)
```

**Example:**

```
Before NFC: و + ̂  (2 codepoints)
After NFC:  ۆ     (1 codepoint U+06C6)
```

### Whitespace Normalization

**Rules:**

1. **Collapse spaces/tabs to single space**
   ```python
   text = re.sub(r'[ \t]+', ' ', text)
   ```

2. **Convert other whitespace to space**
   ```python
   text = re.sub(r'[\t\x0b\x0c\r]', ' ', text)
   ```

3. **Trim spaces around newlines**
   ```python
   text = re.sub(r' *\n *', '\n', text)
   ```

4. **Collapse multiple newlines**
   ```python
   text = re.sub(r'\n\n+', '\n', text)
   ```

5. **PRESERVE line breaks** (don't join lines!)

### Line Processing

**Per-Line Operations:**

1. Strip leading/trailing whitespace
2. Skip empty lines
3. Deduplicate (preserve first occurrence)
4. Normalize internal whitespace to single spaces

**Example:**

```python
lines = []
for line in text.splitlines():
    line = line.strip()
    if line:
        line = re.sub(r'\s+', ' ', line)
        lines.append(line)
```

---

## Corpus Building Workflow

### Step-by-Step Process

#### 1. Gather Sources

```bash
# Place raw corpus files in work/corpus/
work/corpus/
├── news_scraped.txt          # News articles
├── biographical.txt          # Biographical content
├── literature.txt            # Kurdish literature
└── technical.txt             # Technical documentation
```

#### 2. Validate Each Source

```bash
cd /mnt/c/tesseract/work

# Check ZWNJ density
python3 tools/validate_source_quality.py corpus/news_scraped.txt
# ✅ ACCEPT: 9.3% ZWNJ

python3 tools/validate_source_quality.py corpus/wikipedia.txt
# ❌ REJECT: 0.1% ZWNJ - DO NOT USE!
```

**Action:**
- ✅ ACCEPT → Keep file
- ❌ REJECT → Remove or find better source

#### 3. Build Normalized Corpus

```bash
# From WSL
cd /mnt/c/tesseract/work
python3 tools/corpus_build.py --fixer --min-count 2000

# From PowerShell
.\run_training.ps1 -Mode BuildCorpus -UseFixer -CorpusMinCount 2000
```

**Output:** `work/corpus/ckb.training_text.final`

#### 4. Verify Final Corpus

```bash
cd /mnt/c/tesseract/work

# Check ZWNJ density of final corpus
python3 tools/validate_source_quality.py corpus/ckb.training_text.final

# Expected: 6-10% ZWNJ
```

#### 5. (Optional) Blend Sources for Target ZWNJ

If you have multiple domain sources and want specific ZWNJ density:

```bash
cd /mnt/c/tesseract/work

python3 tools/blend_corpus.py \
  --sources corpus/news.txt corpus/biographical.txt \
  --output corpus/blended_8pct.txt \
  --target-zwnj 8.0
```

#### 6. Generate Training Data

```bash
# From PowerShell
.\run_training.ps1 -Mode GenerateTrain -LatinDigits
```

This runs `generate_ckb_training_data.sh` which:
- Reads `corpus/ckb.training_text.final`
- Applies additional NFC normalization
- Renders images with fonts
- Creates ground truth pairs

---

## Quality Validation

### Corpus Quality Metrics

| Metric | Target | Tool | Why Important |
|--------|--------|------|---------------|
| **ZWNJ Density** | **6-10%** | `validate_source_quality.py` | **Most critical - determines accuracy** |
| Character coverage | All Kurdish letters | `corpus_build.py` stats | Ensures model learns all characters |
| Deduplication | < 5% duplicates | `corpus_build.py` | Avoid training bias |
| Sentence variety | Diverse domains | Manual review | Better generalization |
| Encoding validity | 100% UTF-8 | Automatic in tools | Prevent corruption |

### ZWNJ Validation

**Check ZWNJ density:**

```bash
cd /mnt/c/tesseract/work
python3 tools/validate_source_quality.py corpus/my_corpus.txt
```

**Output:**

```
Analyzing: corpus/my_corpus.txt

📊 Analysis Results:
   Total characters:       45,230
   ZWNJ count:             4,217
   ZWNJ density:           9.32%
   
   Status: ✅ ACCEPT
   
   This source has excellent ZWNJ density (6-10% range).
   Proceed with training!
```

### Character Distribution Check

After building corpus:

```bash
cd /mnt/c/tesseract/work

# View character statistics
cat output/corpus_build_stats.txt
```

**Look for:**
- Balanced Kurdish letter frequencies
- Sufficient digit occurrences (if needed)
- Adequate punctuation variety

### Encoding Validation

```bash
# Check file encoding
file -bi corpus/ckb.training_text.final
# Expected: text/plain; charset=utf-8

# Validate UTF-8
iconv -f utf-8 -t utf-8 corpus/ckb.training_text.final > /dev/null
echo $?
# Expected: 0 (success)
```

---

## Usage Examples

### Example 1: Basic Corpus Normalization

**Scenario:** You have a single corpus file to normalize

```bash
cd /mnt/c/tesseract/work

# 1. Validate source
python3 tools/validate_source_quality.py raw_corpus/scraped.txt
# ✅ ACCEPT: 8.7% ZWNJ

# 2. Copy to corpus directory
cp raw_corpus/scraped.txt corpus/

# 3. Build normalized corpus
python3 tools/corpus_build.py --fixer

# 4. Verify output
python3 tools/validate_source_quality.py corpus/ckb.training_text.final
# ✅ 8.5% ZWNJ (good!)
```

### Example 2: Multi-Source Blending

**Scenario:** Blend news + biographical to improve accuracy on both domains

```bash
cd /mnt/c/tesseract/work

# 1. Validate both sources
python3 tools/validate_source_quality.py corpus/news.txt
# ✅ ACCEPT: 9.3% ZWNJ

python3 tools/validate_source_quality.py corpus/biographical.txt
# ✅ ACCEPT: 7.2% ZWNJ

# 2. Blend to target 8.5% ZWNJ
python3 tools/blend_corpus.py \
  --sources corpus/news.txt corpus/biographical.txt \
  --output corpus/blended.txt \
  --target-zwnj 8.5

# 3. Replace final corpus
mv corpus/ckb.training_text.final corpus/ckb.training_text.final.backup
cp corpus/blended.txt corpus/ckb.training_text.final

# 4. Verify
python3 tools/validate_source_quality.py corpus/ckb.training_text.final
# ✅ 8.5% ZWNJ
```

### Example 3: Full Pipeline (PowerShell)

**Scenario:** Complete workflow from raw sources to training

```powershell
# 1. Validate sources first (in WSL)
wsl -d Ubuntu -- bash -lc "cd '/mnt/c/tesseract/work'; python3 tools/validate_source_quality.py corpus/source1.txt"
wsl -d Ubuntu -- bash -lc "cd '/mnt/c/tesseract/work'; python3 tools/validate_source_quality.py corpus/source2.txt"

# 2. Build normalized corpus with all options
.\run_training.ps1 -Mode BuildCorpus -UseFixer `
  -KeepRTLControls `
  -BalanceDigits `
  -BalanceLatinDigits `
  -BalancePuncs `
  -CorpusMinCount 3000

# 3. Generate training data and train
.\run_training.ps1 -Mode GenerateTrain -LatinDigits

# 4. Test
.\run_training.ps1 -Mode SmokeTestBest

# 5. Evaluate
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

### Example 4: Character Fixing Only

**Scenario:** Normalize a single file without building full corpus

```bash
cd /mnt/c/tesseract/work

# Apply fixer to single file
python kurdish_character_fixer.py input.txt output.txt

# Or use pipe
cat input.txt | python kurdish_character_fixer.py > output.txt
```

### Example 5: Diagnosis and Repair

**Scenario:** Corpus has low accuracy, need to diagnose

```bash
cd /mnt/c/tesseract/work

# 1. Check ZWNJ density
python3 tools/validate_source_quality.py corpus/ckb.training_text.final
# ❌ REJECT: 2.1% ZWNJ - TOO LOW!

# 2. Find which source is problematic
for f in corpus/*.txt; do
  echo "Checking $f..."
  python3 tools/validate_source_quality.py "$f" | grep ZWNJ
done

# Output:
# corpus/news.txt - 9.3% ZWNJ ✅
# corpus/wikipedia.txt - 0.1% ZWNJ ❌ <-- REMOVE THIS!

# 3. Remove bad source
rm corpus/wikipedia.txt

# 4. Rebuild corpus
python3 tools/corpus_build.py --fixer

# 5. Verify fix
python3 tools/validate_source_quality.py corpus/ckb.training_text.final
# ✅ ACCEPT: 9.3% ZWNJ
```

---

## Best Practices

### ✅ Do's

1. **ALWAYS validate ZWNJ density BEFORE using a source**
   - Use `validate_source_quality.py` on samples
   - Reject sources < 6% ZWNJ
   - Save time by validating early

2. **Apply character fixer during corpus building**
   - Use `--fixer` flag with `corpus_build.py`
   - Or use `-UseFixer` with PowerShell launcher
   - Ensures consistent normalization
   - Default smart mode preserves Arabic words

3. **Preserve ZWNJ characters**
   - Never remove U+200C from text
   - ZWNJ is essential for Kurdish word boundaries
   - 9.3% ZWNJ → 76.9% accuracy proven

4. **Use NFC normalization throughout**
   - Apply to all text processing stages
   - Ensures consistent character representation
   - Prevents shaping issues

5. **Deduplicate corpus**
   - Remove duplicate lines
   - Preserve order for better training
   - `corpus_build.py` does this automatically

6. **Balance character distribution**
   - Use `--min-count` to set targets
   - Boost rare Kurdish letters
   - Ensures complete character coverage

7. **Validate final corpus**
   - Check ZWNJ density (6-10%)
   - Verify character coverage
   - Review statistics

8. **Document source quality**
   - Record ZWNJ density per source
   - Track which sources work well
   - Share knowledge for future batches

### ❌ Don'ts

1. **DON'T skip ZWNJ validation**
   - Wikipedia had 0.1% ZWNJ → failed training
   - Wasted significant time
   - Always validate first!

2. **DON'T remove ZWNJ characters**
   - ZWNJ is NOT a "useless control character"
   - Removing it destroys Kurdish text semantics
   - Causes major accuracy loss

3. **DON'T mix normalized and unnormalized text**
   - Apply normalization consistently
   - Don't partially process corpus
   - Inconsistency hurts training

4. **DON'T ignore character encoding**
   - Always use UTF-8
   - Verify with `file -bi`
   - Fix encoding before processing

5. **DON'T over-deduplicate across domains**
   - Some repetition is okay for learning
   - Balance between dedup and variety
   - Focus on exact duplicates only

6. **DON'T blindly trust source quality**
   - Even "official" sources can have low ZWNJ
   - Always validate with tools
   - Quality > Authority

7. **DON'T process without backups**
   - Keep original raw sources
   - Save intermediate steps
   - Easy to revert if needed

8. **DON'T ignore normalization statistics**
   - Review `corpus_build_stats.txt`
   - Check for anomalies
   - Understand your corpus

---

## Troubleshooting

### Issue: Low Accuracy After Training

**Symptom:** Model achieves < 70% accuracy on test images

**Diagnosis:**

```bash
cd /mnt/c/tesseract/work

# Check corpus ZWNJ density
python3 tools/validate_source_quality.py corpus/ckb.training_text.final
```

**Solutions:**

| ZWNJ Density | Action |
|--------------|--------|
| < 6% | ❌ Corpus is bad - find better sources |
| 6-10% | ✅ Corpus is good - check other issues (fonts, PSM, etc.) |
| > 12% | ⚠️ Unusually high - verify source isn't synthetic |

### Issue: Character Recognition Errors

**Symptom:** Specific Kurdish characters (گ، ڕ، ژ، ڤ، ێ، ۆ، ڵ) not recognized

**Diagnosis:**

```bash
cd /mnt/c/tesseract/work

# Check character coverage
cat output/corpus_build_stats.txt | grep -E '[گڕژڤێۆڵ]'
```

**Solutions:**

1. **If characters missing from corpus:**
   - Add more diverse sources
   - Use `--min-count` to boost rare characters
   - Review source selection

2. **If characters present but misrecognized:**
   - Check font rendering
   - Verify ground truth images
   - May need font-specific fixes

### Issue: Mixed Character Forms

**Symptom:** Same word appears with different character forms (ك vs. ک)

**Solution:**

```bash
cd /mnt/c/tesseract/work

# Rebuild corpus WITH fixer
python3 tools/corpus_build.py --fixer

# The fixer will unify all forms to Kurdish standard
```

### Issue: Training Data Generation Fails

**Symptom:** `generate_ckb_training_data.sh` errors

**Check:**

1. **Corpus encoding:**
   ```bash
   file -bi corpus/ckb.training_text.final
   # Must be: text/plain; charset=utf-8
   ```

2. **Corpus not empty:**
   ```bash
   wc -l corpus/ckb.training_text.final
   # Should have thousands of lines
   ```

3. **Unicode validity:**
   ```bash
   iconv -f utf-8 -t utf-8 corpus/ckb.training_text.final > /dev/null
   echo $?
   # Should return 0
   ```

**Fix:**

```bash
# Rebuild corpus from scratch
cd /mnt/c/tesseract/work
rm corpus/ckb.training_text.final
python3 tools/corpus_build.py --fixer
```

---

## References

### Related Documentation

- **[PHASE7_COMPLETE_GUIDE.md](PHASE7_COMPLETE_GUIDE.md)** - Complete Phase 7 workflow
- **[ZWNJ_TATWEEL_SUMMARY.md](ZWNJ_TATWEEL_SUMMARY.md)** - ZWNJ analysis and importance
- **[UNICODE_CHARACTER_ANALYSIS.md](UNICODE_CHARACTER_ANALYSIS.md)** - Detailed Unicode analysis
- **[RUN_TRAINING_OPTIONS.md](RUN_TRAINING_OPTIONS.md)** - Training script options

### Key Tools

| Tool | Path | Documentation |
|------|------|---------------|
| Character Fixer | `work/kurdish_character_fixer.py` | See file comments |
| Corpus Builder | `work/tools/corpus_build.py` | See file comments |
| Corpus Blender | `work/tools/blend_corpus.py` | See file comments |
| Quality Validator | `work/tools/validate_source_quality.py` | See Phase 7 guide |
| Training Launcher | `run_training.ps1` | `Get-Help .\run_training.ps1` |

### Unicode Resources

- **Kurdish Characters:** [docs/kurdish_characters.md](docs/kurdish_characters.md)
- **ZWNJ (U+200C):** [ZWNJ_TATWEEL_SUMMARY.md](ZWNJ_TATWEEL_SUMMARY.md)
- **Unicode NFC:** [Unicode Normalization Forms](https://unicode.org/reports/tr15/)

### Source Quality Requirements

| Metric | Minimum | Optimal | Maximum |
|--------|---------|---------|---------|
| **ZWNJ Density** | **6.0%** | **8-9%** | **12.0%** |
| Encoding | UTF-8 | UTF-8 | UTF-8 |
| Duplicates | < 10% | < 5% | 0% |
| Sentence length | > 5 words | 10-20 words | Variable |

---

## Summary

### Key Takeaways

1. **ZWNJ density (6-10%) is the most critical metric** - Validate BEFORE acquiring sources
2. **Character fixer ensures consistency** - Always use `--fixer` when building corpus
3. **NFC normalization is essential** - Applied throughout entire pipeline
4. **Deduplication improves efficiency** - Automatic in corpus builder
5. **Validation prevents wasted effort** - Check quality at every stage

### Normalization Checklist

- [ ] Validate source ZWNJ density (6-10% required)
- [ ] Place sources in `work/corpus/`
- [ ] Run corpus builder with `--fixer`
- [ ] Verify final corpus ZWNJ density
- [ ] Check character coverage statistics
- [ ] Validate UTF-8 encoding
- [ ] Generate training data
- [ ] Test on real images

### Success Metrics

**Achieved with proper normalization:**
- ✅ News corpus: 9.33% ZWNJ
- ✅ Training accuracy: 76.9% on news images
- ✅ Production-ready model (Phase 6 complete)

**Failed with improper normalization:**
- ❌ Wikipedia: 0.11% ZWNJ
- ❌ Training degradation
- ❌ Wasted time and resources

---

**Status:** ✅ Production Normalization Pipeline Documented  
**Version:** 1.0  
**Last Updated:** November 14, 2025  
**Maintained by:** Tesseract Kurdish OCR Project
