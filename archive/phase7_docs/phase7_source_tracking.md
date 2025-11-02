# Phase 7 Source Tracking

**Goal:** Find 500-1,000 biographical sentences with 6-10% ZWNJ density  
**Started:** November 1, 2025  
**Status:** 🔍 Source Discovery

---

## Source Validation Log

| # | Source Name | Type | ZWNJ% | Status | Sentences | Notes |
|---|-------------|------|-------|--------|-----------|-------|
| 1 | _pending_ | - | - | 🔍 Searching | - | Looking for Kurdish books/biographies |
| 2 | | | | | | |
| 3 | | | | | | |

**Status Legend:**
- 🔍 Searching - Looking for source
- 📥 Downloading - Acquiring sample
- ✅ ACCEPT - Validated, ZWNJ 6-10%
- ⚠️ REVIEW - Borderline quality
- ❌ REJECT - ZWNJ too low (<6%)

---

## Potential Source Types

### 1. Kurdish Digital Libraries & Books 📚

**Targets:**
- [ ] Archive.org (Kurdish texts)
  - Search: "کوردی" (Kurdish) + "biography" / "history"
  - URL: https://archive.org/search.php?query=kurdish
  
- [ ] Google Books (Kurdish section)
  - Search: Kurdish biographies, Kurdish literature
  - URL: https://books.google.com/
  
- [ ] Kurdish Publishing Houses
  - Aras Publishing
  - Ranj Publishing
  - Check for digital copies or PDFs

- [ ] Project Gutenberg (Kurdish texts if available)

**Action:** Extract 100-sentence sample → validate with tool

---

### 2. Academic Sources 🎓

**Targets:**
- [ ] Kurdistan Universities
  - Salahaddin University (Erbil)
  - University of Sulaimani
  - University of Duhok
  - Check: Digital repositories, thesis archives
  
- [ ] ResearchGate (Kurdish authors)
  - Search: Papers written in Kurdish
  - Focus: History, literature, cultural studies
  
- [ ] Kurdish Studies Journals
  - Look for open-access journals
  - Download PDFs of articles in Kurdish

**Action:** Extract sample from papers → validate ZWNJ

---

### 3. News Archives (Biographical Sections) 📰

**Already have news scraper, now focus on:**

- [ ] **Kurdistan24** - Biography section
  - URL: Check for /biography or /people categories
  - Type: Political/cultural figures
  
- [ ] **Rudaw** - Obituaries & profiles
  - URL: Check archives for biographical content
  - Type: Contemporary figures
  
- [ ] **NRT** - Historical profiles
  - URL: Check history/culture sections
  - Type: Historical figures
  
- [ ] **Awene** - Cultural biographies
  - URL: Check culture section
  - Type: Writers, artists, intellectuals

**Action:** Scrape biographical articles specifically → validate

---

### 4. Wikipedia (IF Fixed with Option C) 🔧

**Current Status:** 0.106% ZWNJ (UNUSABLE)

**Option C Approach:**
- Build Kurdish compound word dictionary
- Apply morphological rules to insert ZWNJ
- Validate synthetic vs natural ZWNJ patterns
- Only use if quality matches natural text

**Priority:** LOW (pursue other sources first)

---

## Sample Validation Workflow

### Step 1: Extract Sample
```bash
# Get 100-200 sentences from source
# Save as: samples/source_name_sample.txt
```

### Step 2: Validate Quality
```bash
python work/tools/validate_source_quality.py samples/source_name_sample.txt
```

### Step 3: Document Result
```
If ACCEPT (✅):
  - Add to tracking table above
  - Note: Source name, ZWNJ%, sentence count
  - Plan: Acquire full text
  
If REVIEW (⚠️):
  - Document issues found
  - Decide: Fix issues or skip
  
If REJECT (❌):
  - Note: ZWNJ too low
  - Skip: Don't waste time acquiring full text
```

---

## Quick Commands Reference

```bash
# Create samples directory
New-Item -ItemType Directory -Path "samples" -Force

# Validate a sample
python work\tools\validate_source_quality.py samples\your_sample.txt

# Validate multiple samples at once
python work\tools\validate_source_quality.py samples\*.txt

# Analyze ZWNJ in existing corpus
python work\analyze_unicode_chars.py work\corpus\existing_file.txt
```

---

## Next Immediate Actions

### TODAY:
1. ✅ Create samples directory
2. 🔍 Search Archive.org for Kurdish biographies
3. 🔍 Search Google Books for Kurdish literature
4. 🔍 Check Kurdistan24/Rudaw for biographical sections

### THIS WEEK:
1. Extract 5-10 samples from different sources
2. Validate all samples with validator tool
3. Identify 2-3 ACCEPT sources (ZWNJ 6-10%)
4. Document results in tracking table above

### NEXT WEEK:
1. Acquire full text from validated sources
2. Clean and prepare corpus
3. Blend with existing news corpus
4. Prepare for training

---

## Success Metrics

**Target for Phase 7:**
- Find: 3-5 validated sources (✅ ACCEPT status)
- Total: 500-1,000 biographical sentences
- ZWNJ: 7-9% (blended)
- Quality: >85% Kurdish script

**Expected Result After Training:**
- mgk.tif: 76%+ accuracy (current: 71.69%)
- News: ≥76% accuracy (maintain current: 76.9%)

---

## Resources

**Tools:**
- Source Validator: `work/tools/validate_source_quality.py`
- Unicode Analyzer: `work/analyze_unicode_chars.py`
- Corpus Blender: `work/tools/blend_corpus.py`

**Documentation:**
- Quick Start: [PHASE7_QUICKSTART.md](PHASE7_QUICKSTART.md)
- Full Plan: [PHASE7_IMPROVEMENT_PLAN.md](PHASE7_IMPROVEMENT_PLAN.md)
- Phase 6 Results: [PHASE6_COMPLETE.md](PHASE6_COMPLETE.md)

---

## Notes

- **Remember:** ALWAYS validate ZWNJ density BEFORE acquiring full text
- **Rule:** Only accept sources with 6-10% ZWNJ
- **Insight:** 1,000 sentences at 8% ZWNJ > 10,000 sentences at 0.1% ZWNJ
- **Current model:** Already production-ready (76.9% on news)
- **Phase 7:** Optional improvement, only proceed if good sources found

---

**Last Updated:** November 1, 2025
