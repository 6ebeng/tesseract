# Corpus Builder Enhancements v3.0

## Overview

Enhanced corpus builder with comprehensive quality filtering for Kurdish Sorani OCR training.

## New Features (v3.0)

### 1. **Sentence Length Filtering**

```powershell
.\run_training.ps1 -Mode BuildCorpus -MinLength 30 -MaxLength 200
```

- **MinLength**: Minimum sentence length (default: 10 chars)
- **MaxLength**: Maximum sentence length (default: 500 chars)
- **Optimal range**: 30-150 chars for OCR training
- **Reason**: Filters out noise (too short) and unwieldy text (too long)

### 2. **Character Set Purity Validation**

```powershell
.\run_training.ps1 -Mode BuildCorpus -MaxNonKurdish 20.0
```

- **MaxNonKurdish**: Max % of non-Kurdish characters allowed (default: 30%)
- **Kurdish Extended Set**: TARGET_CHARS + Arabic digits + punctuation + common Arabic loanwords
- **Reason**: Removes heavily corrupted or non-Kurdish text

### 3. **ZWNJ Pattern Validation** (Experimental)

```powershell
.\run_training.ps1 -Mode BuildCorpus -ValidateZWNJPatterns
```

- Validates ZWNJ appears in proper Kurdish linguistic contexts
- Patterns checked:
  - Compound words: `word + ZWNJ + word`
  - Verb prefixes: `دە‌`, `بە‌`, `ئێ‌`, `دا‌`, `نا‌`
- **Reason**: Filters random/incorrect ZWNJ placement

### 4. **Multi-Metric Quality Scoring**

Combines 4 factors into overall quality score (0-10):

- **ZWNJ Density** (40%): 6-10% optimal for Kurdish OCR
- **Sentence Length** (25%): 30-150 chars optimal
- **Character Set Purity** (25%): Higher Kurdish % is better
- **ZWNJ Pattern Correctness** (10%): Valid linguistic patterns

### 5. **Enhanced Statistics Dashboard**

Now reports:

- Quality metrics: average quality score, sentence length
- Filter breakdown: by length, charset, ZWNJ, patterns
- ZWNJ quality assessment: ✅ EXCELLENT / ⚠️ ACCEPTABLE / ❌ LOW
- All filter settings used

## Usage Examples

### Balanced Build (Recommended)

```powershell
.\run_training.ps1 -Mode BuildCorpus `
    -UseFixer `
    -MinZWNJ 3.0 `
    -TargetZWNJ 8.0 `
    -MinLength 30 `
    -MaxLength 200 `
    -MaxNonKurdish 20.0
```

### Strict Quality Build

```powershell
.\run_training.ps1 -Mode BuildCorpus `
    -UseFixer `
    -MinZWNJ 5.0 `
    -TargetZWNJ 9.0 `
    -MinLength 40 `
    -MaxLength 150 `
    -MaxNonKurdish 15.0 `
    -ValidateZWNJPatterns
```

### Permissive Build (More Data)

```powershell
.\run_training.ps1 -Mode BuildCorpus `
    -UseFixer `
    -MinZWNJ 1.0 `
    -TargetZWNJ 6.0 `
    -MinLength 20 `
    -MaxLength 300 `
    -MaxNonKurdish 35.0
```

## Parameter Reference

| Parameter               | Type   | Default | Description                                    |
| ----------------------- | ------ | ------- | ---------------------------------------------- |
| `-UseFixer`             | switch | off     | Apply kurdish_character_fixer.py normalization |
| `-MinZWNJ`              | double | 0.0     | Min ZWNJ % threshold (filter)                  |
| `-TargetZWNJ`           | double | 0.0     | Target ZWNJ % (oversampling)                   |
| `-MinLength`            | int    | 10      | Min sentence length in chars                   |
| `-MaxLength`            | int    | 500     | Max sentence length in chars                   |
| `-MaxNonKurdish`        | double | 30.0    | Max % non-Kurdish chars allowed                |
| `-ValidateZWNJPatterns` | switch | off     | Enable ZWNJ pattern validation                 |
| `-NoPreserveArabic`     | switch | off     | Convert Arabic to Kurdish                      |
| `-PreserveLatinDigits`  | switch | off     | Keep 0-9 (don't convert to ٠-٩)                |
| `-CorpusMinCount`       | int    | 1000    | Min char count for balancing                   |

## Quality Score Components

### ZWNJ Density Score (40% weight)

- **10.0**: 6-10% density (optimal for Kurdish)
- **5.0-8.0**: 3-6% or 10-15% (acceptable)
- **0.0-5.0**: <3% or >15% (poor quality)

### Length Score (25% weight)

- **10.0**: 30-150 chars (optimal for OCR)
- **5.0-10.0**: 10-30 or 150-200 chars (acceptable)
- **0.0-5.0**: <10 or >200 chars (poor quality)

### Purity Score (25% weight)

- **10.0**: 100% Kurdish/acceptable chars
- **7.0**: 70% Kurdish (with MaxNonKurdish=30%)
- **0.0**: All non-Kurdish chars

### Pattern Score (10% weight)

- **10.0**: ZWNJ in valid Kurdish contexts or no ZWNJ
- **0.0**: Invalid/random ZWNJ placement

## Output Statistics Example

```
Sources: 2 files
Lines (raw): 224,890

Quality Filtering:
  Filtered by length: 15,234
  Filtered by character set: 8,456
  Filtered by ZWNJ: 198,322
  Total filtered: 222,012

Lines (after filtering): 2,878
Lines (quality oversampled): 1,245
Lines (final): 4,123

ZWNJ Density:
  Initial: 0.458%
  Final: 8.234%
  ZWNJ count: 3,456
  Total chars: 41,953

Quality Metrics:
  Average quality score: 8.45/10.0
  Average sentence length: 87.3 chars
  ZWNJ quality: ✅ EXCELLENT (6-10%)

Filter Settings:
  Min length: 30 chars
  Max length: 200 chars
  Max non-Kurdish: 20.0%
  Min ZWNJ: 3.0%
  Target ZWNJ: 8.0%
  ZWNJ pattern validation: Disabled
```

## Implementation Details

### Character Sets

**TARGET_CHARS** (Central Kurdish/Sorani standard - 33 chars):

```
ئ ء ا ب پ ت ج چ ح خ د ر ڕ ز ژ س ش ع غ ف ڤ ق ک گ ل ڵ م ن و ۆ ه ە ی ێ
```

**DIALECT_CHARS** (Other Kurdish dialects - 4 chars):

- Southern Kurdish: **ۊ** [y], **ݩ** [ŋ]
- Hewrami: **ڎ ۉ**

**KURDISH_EXTENDED** (all acceptable chars - 89 total):

- TARGET_CHARS (33)
- DIALECT_CHARS (4)
- Arabic-Indic digits: ٠-٩
- Latin digits: 0-9
- Arabic math: ٫ ٬ % ÷ ×
- Punctuation: ، ؛ ؟ / . , ; : ! ? - ( ) [ ] { } " ' « » < >
- Whitespace and tatweel: ـ

**ARABIC_CHARS** (Persian/Arabic loanwords - 14 chars):

```
آ أ إ ث ذ ص ض ط ظ ك ؤ ة ي ى
```

**ARABIC_DIACRITICS** (acceptable diacritics - 9 chars):

```
ــَـِـُـّـْ ـًـٍـٌ
```

(Fatha, Kasra, Damma, Shadda, Sukun, Tanwin variants, Tatweel)

### ZWNJ Patterns (Validation)

1. **Compound Words**: `[\u0600-\u06FF]+\u200C[\u0600-\u06FF]+`
2. **Verb Prefixes**: `(دە|بە|ئێ|دا|نا)\u200C`

### Deduplication Logic

Enhanced ZWNJ-aware deduplication:

1. Calculate quality score for each sentence
2. For duplicates, keep the higher-quality version
3. Quality factors: ZWNJ density + length + purity + patterns

### Oversampling Algorithm

Quality-based oversampling (if `TargetZWNJ` > 0):

1. Score all sentences by overall quality
2. Sort by score (highest first)
3. Oversample top 20% (quality score > 6.0)
4. Continue until target ZWNJ density reached or safety cap hit
5. Safety cap: 3x original corpus size

## Version History

### v3.0 (Current)

- ✅ Sentence length filtering (`--min-length`, `--max-length`)
- ✅ Character set purity validation (`--max-non-kurdish`)
- ✅ ZWNJ pattern validation (`--validate-zwnj-patterns`)
- ✅ Multi-metric quality scoring (4 components)
- ✅ Enhanced statistics dashboard
- ✅ Quality-based oversampling (replaces ZWNJ-only)

### v2.2 (Previous)

- ZWNJ-aware deduplication
- Minimum ZWNJ filtering (`--min-zwnj`)
- Target ZWNJ oversampling (`--target-zwnj`)
- Basic ZWNJ statistics

### v2.0 (Original)

- Basic corpus building
- Character balancing
- Simple deduplication
- Kurdish character normalization

## Best Practices

1. **Always use `-UseFixer`**: Ensures consistent normalization
2. **Start with balanced settings**: MinZWNJ=3.0, TargetZWNJ=8.0, MinLength=30, MaxLength=200
3. **Monitor quality score**: Aim for average > 7.0
4. **Iterate if needed**: Adjust thresholds based on corpus stats
5. **Use pattern validation cautiously**: Currently experimental, may filter good data
6. **Check filtered counts**: High filtering means stricter thresholds needed

## Troubleshooting

### Issue: Too much filtering (< 5% sentences kept)

**Solution**: Relax thresholds

- Increase `MinZWNJ` → 1.0 or 0.0
- Increase `MaxNonKurdish` → 35.0 or 40.0
- Increase `MinLength` → 20 or 15
- Increase `MaxLength` → 300 or 400

### Issue: Low ZWNJ density in output (<3%)

**Solution**: Tighten ZWNJ filters

- Increase `MinZWNJ` → 4.0 or 5.0
- Increase `TargetZWNJ` → 9.0 or 10.0
- Enable `-ValidateZWNJPatterns`

### Issue: Low quality score (<6.0)

**Solution**: Stricter filtering

- Decrease `MaxNonKurdish` → 20.0 or 15.0
- Narrow length range → MinLength=40, MaxLength=150
- Increase `MinZWNJ` → 4.0

### Issue: Not enough sentences (<1000)

**Solution**: Get more source data

- Run scrapers: `.\run_training.ps1 -Mode ScrapeCorpus -ScraperAll`
- Combine multiple sources in `work/corpus/`
- Relax quality thresholds temporarily

## See Also

- `docs/normalization/NORMALIZATION_GUIDE_v2.2.md` - Character normalization
- `docs/analysis/ZWNJ_TATWEEL_SUMMARY.md` - ZWNJ importance for Kurdish OCR
- `work/kurdish_character_fixer.py` - Normalization implementation
- `work/tools/corpus_build.py` - Corpus builder source code
