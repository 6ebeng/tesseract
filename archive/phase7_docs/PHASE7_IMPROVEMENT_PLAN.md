# Phase 7: Accuracy Improvement Plan

**Date:** November 1, 2025  
**Goal:** Improve biographical text accuracy from 71.69% → 76%+  
**Current Status:** Planning & Source Discovery

---

## Critical Success Factor: ZWNJ Density ✅

**Phase 6 Discovery:** ZWNJ (U+200C) density is THE quality metric for Kurdish OCR training.

### Target Metrics

```
✅ News corpus:        9.331% ZWNJ → 76.9% accuracy
⚠️ Wikipedia:         0.106% ZWNJ → FAILED (unusable)
🎯 Target for Phase 7: 6-10% ZWNJ → Expected: 76%+ accuracy
```

**Rule:** ANY corpus with <6% ZWNJ will fail. ALWAYS validate ZWNJ density BEFORE training!

---

## Strategy: Find High-Quality Biographical Sources

### Source Requirements (NON-NEGOTIABLE)

1. **ZWNJ Density:** 6-10% minimum (validate with `analyze_unicode_chars.py`)
2. **Domain:** Biographical, historical, or literary Kurdish text
3. **Size:** 500-1,000 sentences minimum
4. **Script Purity:** 85%+ Kurdish script (minimize Latin/Arabic)
5. **Quality:** Natural Kurdish text (not machine-translated)

### Potential Source Types

#### 1. Kurdish Literature & Books 📚

**Target:**
- Classic Kurdish novels and poetry
- Modern Kurdish literature
- Kurdish history books
- Academic publications in Kurdish

**Where to find:**
- Kurdish digital libraries
- Kurdish publishing houses (Aras, Ranj, etc.)
- Google Books (Kurdish section)
- Archive.org (Kurdish texts)
- University repositories

**Validation required:** Extract sample → check ZWNJ → proceed if >6%

#### 2. Kurdish Academic Journals 🎓

**Target:**
- Kurdish language research papers
- Historical studies in Kurdish
- Literary analysis in Kurdish

**Where to find:**
- Kurdistan universities (Salahaddin, Sulaimani, Duhok)
- Kurdish Studies journals
- ResearchGate (Kurdish authors)

**Validation required:** Must check ZWNJ density per paper

#### 3. Kurdish News Archives (Biographical Sections) 📰

**Target:**
- Obituaries
- Biography sections
- Historical profiles
- Cultural heritage articles

**Where to find:**
- Kurdistan24 archives
- Rudaw archives
- NRT archives
- K24 archives

**Note:** Already have news corpus (9.331% ZWNJ) but need MORE biographical articles specifically

#### 4. Kurdish Wikipedia (IF Fixed) 🔧

**Current status:** 0.106% ZWNJ (UNUSABLE)

**Option C approach:**
- Build Kurdish compound word dictionary
- Apply morphological rules to insert ZWNJ
- Validate against natural text
- Only use if synthetic ZWNJ matches natural patterns

**Timeline:** 1-2 weeks development
**Risk:** Synthetic may not match natural usage

---

## Phase 7 Workflow

### Step 1: Source Discovery & Validation (Week 1-2)

**Actions:**
1. Research and identify potential sources
2. Extract 100-sentence samples from each source
3. Run ZWNJ analysis: `python work/analyze_unicode_chars.py sample.txt`
4. Accept only sources with >6% ZWNJ
5. Document source metadata (domain, ZWNJ%, size)

**Tool:** `work/tools/validate_source_quality.py` (to be created)

**Deliverable:** List of validated sources with ZWNJ metrics

### Step 2: Corpus Acquisition (Week 2-3)

**Actions:**
1. Download/scrape validated sources
2. Extract text content
3. Clean and normalize
4. Apply Kurdish character fixer
5. Build new corpus file: `ckb_phase7.training_text`

**Tools:**
- Existing scrapers in `work/tools/scrapers/`
- `work/kurdish_character_fixer.py`

**Deliverable:** `work/corpus/ckb_phase7.training_text` (500-1000 sentences)

### Step 3: Corpus Quality Validation (Week 3)

**Critical checks:**
1. ZWNJ density: 6-10% ✅
2. Script purity: >85% Kurdish
3. Sentence length: 5-50 words
4. Vocabulary overlap with mgk.tif domain
5. No encoding issues

**Command:**
```bash
python work/analyze_unicode_chars.py work/corpus/ckb_phase7.training_text
```

**Expected output:**
```
ZWNJ: 7-9%
Tatweel: ~0.025%
Total sentences: 500-1000
Kurdish script: >85%
```

**Deliverable:** Validation report confirming quality

### Step 4: Balanced Corpus Building (Week 3)

**Approach:** Blend Phase 7 sources with existing high-quality corpus

**Composition:**
```
News corpus (existing):      1,279 sentences (9.331% ZWNJ)
Phase 7 biographical:        500-1000 sentences (6-10% ZWNJ)
Total:                       ~2,000-2,300 sentences
Expected blended ZWNJ:       7-9%
```

**Command:**
```powershell
.\run_training.ps1 -Mode BuildCorpus -UseFixer -KeepRTLControls `
    -BalanceDigits -BalanceLatinDigits -BalancePuncs -CorpusMinCount 1
```

**Deliverable:** `work/corpus/ckb.training_text` (balanced corpus)

### Step 5: Training (Week 4)

**Command:**
```powershell
.\run_training.ps1 -Mode GenerateTrain -LatinDigits
```

**Expected timeline:**
- Data generation: 2-4 hours
- Training: 8-12 hours
- Total: ~16 hours

**Deliverable:** New trained models in `work/training_output/model/`

### Step 6: Evaluation (Week 4)

**Test cases:**
1. mgk.tif (biographical) - Target: >76%
2. News images - Maintain: >76%
3. PSM sweep (6,11,7,13) - Find optimal mode

**Commands:**
```powershell
# Quick test on mgk.tif
.\run_training.ps1 -Mode SmokeTestBest

# Comprehensive PSM evaluation
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

**Success criteria:**
- mgk.tif: >76% accuracy (improvement from 71.69%)
- News: ≥76% accuracy (maintain current level)
- Blended ZWNJ: 7-9%

**Deliverable:** Performance report comparing Phase 6 vs Phase 7

---

## Tools to Create

### 1. Source Quality Validator

**File:** `work/tools/validate_source_quality.py`

**Purpose:** Quick ZWNJ validation for source evaluation

**Features:**
- Check ZWNJ density
- Check script purity (Kurdish vs Latin/Arabic)
- Check sentence length distribution
- Report vocabulary coverage
- Accept/reject decision with reasoning

**Usage:**
```bash
python work/tools/validate_source_quality.py sample.txt
```

**Output:**
```
✅ ACCEPT: 8.5% ZWNJ, 92% Kurdish script
⚠️ REVIEW: 5.2% ZWNJ (below 6% threshold)
❌ REJECT: 0.3% ZWNJ (unusable)
```

### 2. Use Your Existing Scraper System

**Location:** `work/tools/scrapers/`

**Already have:** Production-ready scraper for 13+ Kurdish news websites

**Usage:**
```bash
cd work/tools/scrapers

# See available websites
python3 generic_scraper.py --list

# Read documentation
cat PRODUCTION_SCRAPER_USAGE.md
cat README.md

# Scrape specific website/category
python3 generic_scraper.py --website rudaw --category culture
```

**For Phase 7:** Look for biographical sections in existing news sites

### 3. Corpus Blending Tool

**File:** `work/tools/blend_corpus.py`

**Purpose:** Intelligently blend multiple corpus sources

**Features:**
- Balance by domain (news vs biography)
- Balance by ZWNJ density
- Deduplication
- Quality reporting

**Usage:**
```bash
python work/tools/blend_corpus.py \
    --news work/corpus/ckb_news.txt \
    --bio work/corpus/ckb_phase7.txt \
    --output work/corpus/ckb.training_text \
    --target-zwnj 8.0
```

---

## Risk Mitigation

### Risk 1: Can't find sources with adequate ZWNJ

**Probability:** 40%

**Mitigation:**
1. Expand search to Kurdish books (Archive.org, Google Books)
2. Consider Option C (synthetic ZWNJ enhancement)
3. Accept current model as v1.0, improve in v2.0

### Risk 2: Sources have domain mismatch

**Probability:** 30%

**Mitigation:**
1. Validate vocabulary overlap with mgk.tif
2. Mix multiple biographical domains
3. Test incrementally (add 100 sentences, evaluate, repeat)

### Risk 3: Training doesn't improve accuracy

**Probability:** 20%

**Mitigation:**
1. Ensure ZWNJ density 7-9% (Phase 6 proved this works)
2. Validate corpus quality before training
3. If no improvement after 1 batch → stop and reassess

---

## Success Metrics

### Phase 7 Success Criteria

**Minimum viable:**
- ✅ mgk.tif: 74% accuracy (+2.3% improvement)
- ✅ News: ≥76% accuracy (maintain)
- ✅ Corpus ZWNJ: 7-9%

**Target:**
- 🎯 mgk.tif: 76% accuracy (+4.3% improvement)
- 🎯 News: ≥76% accuracy (maintain)
- 🎯 Corpus ZWNJ: 8-9%

**Stretch:**
- 🚀 mgk.tif: 78% accuracy (+6.3% improvement)
- 🚀 News: ≥77% accuracy (improve)
- 🚀 Corpus ZWNJ: 9-10%

### Key Performance Indicators

```
Current Phase 6:
- mgk.tif: 71.69%
- News: 76.9%
- Corpus ZWNJ: 5.775% (blended)

Target Phase 7:
- mgk.tif: 76%+ (↑ 4.3%)
- News: 76%+ (maintain)
- Corpus ZWNJ: 8%+ (↑ 2.2%)
```

---

## Timeline

**Total:** 4 weeks

```
Week 1: Source discovery & validation
  - Research potential sources
  - Extract samples
  - Validate ZWNJ density
  - Select best sources

Week 2: Corpus acquisition
  - Scrape/download selected sources
  - Clean and normalize
  - Apply character fixer
  - Build Phase 7 corpus

Week 3: Quality validation & blending
  - Validate corpus quality
  - Blend with existing corpus
  - Final quality checks
  - Prepare for training

Week 4: Training & evaluation
  - Generate training data
  - Train models
  - Evaluate on test cases
  - Compare Phase 6 vs Phase 7
  - Document results
```

---

## Next Steps (Immediate)

### Step 1: Create validation tool ✅

```bash
# Create source quality validator
# This will help you quickly test potential sources
```

### Step 2: Research sources 🔍

**Action items:**
- [ ] Check Archive.org for Kurdish books
- [ ] Browse Kurdish digital libraries
- [ ] Search Google Books (Kurdish)
- [ ] Check university repositories
- [ ] Explore Kurdish news biographical sections

### Step 3: Extract and validate samples 📊

**For each source:**
1. Extract 100-sentence sample
2. Save as `sample_sourcename.txt`
3. Run: `python work/analyze_unicode_chars.py sample_sourcename.txt`
4. Check ZWNJ: Accept if >6%, reject if <6%
5. Document in tracking spreadsheet

### Step 4: Build Phase 7 corpus 📚

**Once you have validated sources:**
1. Acquire full texts
2. Clean and normalize
3. Apply character fixer
4. Combine into `ckb_phase7.training_text`
5. Validate final ZWNJ density

### Step 5: Train and evaluate 🚀

**Execute training pipeline:**
```powershell
# Build balanced corpus
.\run_training.ps1 -Mode BuildCorpus -UseFixer -KeepRTLControls `
    -BalanceDigits -BalanceLatinDigits -BalancePuncs -CorpusMinCount 1

# Generate training data & train
.\run_training.ps1 -Mode GenerateTrain -LatinDigits

# Evaluate on multiple PSM modes
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

---

## References

- **Phase 6 Analysis:** [PHASE6_COMPLETE.md](PHASE6_COMPLETE.md)
- **Unicode Analysis:** [UNICODE_CHARACTER_ANALYSIS.md](UNICODE_CHARACTER_ANALYSIS.md)
- **ZWNJ Summary:** [ZWNJ_TATWEEL_SUMMARY.md](ZWNJ_TATWEEL_SUMMARY.md)
- **Production Guide:** [docs/PRODUCTION_READINESS.md](docs/PRODUCTION_READINESS.md)

---

## Conclusion

**Phase 7 Goal:** Level up accuracy by finding proper biographical sources with high ZWNJ density.

**Key insight from Phase 6:** ZWNJ density (6-10%) is more important than corpus size. One thousand high-quality biographical sentences with 8% ZWNJ will outperform 10,000 Wikipedia sentences with 0.1% ZWNJ.

**Success probability:** 50-60% if proper sources exist. If sources aren't available, deploy current model as v1.0 and revisit in v2.0.

**Next action:** Create validation tools and start source discovery! 🚀
