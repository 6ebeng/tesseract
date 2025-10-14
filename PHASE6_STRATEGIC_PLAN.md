# Phase 6: Strategic Plan for Accuracy Improvement

**Date**: October 13, 2024, 4:45 PM  
**Current Status**: 72.19% accuracy (Phase 4 Farsi checkpoint, BCER 0.195)  
**Target**: 80-85% accuracy (enables effective ZWNJ rule-based recovery)

---

## Current Situation Analysis

### What We Have ✅

**Best Model**: Phase 4 Farsi checkpoint

- **Accuracy**: 72.19% (CER 0.2781)
- **Improvement**: +0.5% from Phase 4 baseline
- **Corpus**: 3,321 high-quality lines
- **ZWNJ density**: 9.46%
- **Status**: Deployed to tessdata/best/ckb.traineddata

### What We Learned ❌

**Phase 5 Failed Because:**

1. Wikipedia corpus too informal/varied (lower quality)
2. ZWNJ density dropped to 6.79% (-28%)
3. Dilution effect: 55% of corpus was low-quality Wikipedia
4. Training produced Phase 3 model (no improvement)

**Key Insight**: Quality > Quantity. 3,321 curated lines (72.19%) > 7,395 mixed lines (71.69%)

### Gap to Target 🎯

**Current**: 72.19%  
**Target**: 80-85%  
**Gap**: 7.81-12.81 percentage points

**Research-based estimates:**

- 5,000 high-quality lines → 75-78% accuracy
- 8,000 high-quality lines → 80-84% accuracy
- 10,000+ high-quality lines → 85-90% accuracy

**Needed**: +4,679 to 6,679 HIGH-QUALITY lines (not Wikipedia)

---

## Phase 6 Strategy: Incremental Quality Expansion

### Core Principle

**"Quality-First Incremental Growth"**

Instead of mass-scraping Wikipedia (failed in Phase 5), we:

1. Add small batches (500 lines) of HIGH-QUALITY text
2. Train and evaluate after EACH batch
3. Only keep batches that improve accuracy
4. Stop when accuracy plateaus or target is reached

### Success Criteria

**Minimum acceptable**: 75% accuracy (+2.81%)  
**Good outcome**: 78% accuracy (+5.81%)  
**Excellent outcome**: 80%+ accuracy (+7.81%+)  
**Ultimate goal**: 85% accuracy (optimal for ZWNJ rules)

---

## Phase 6 Plan: Three-Pronged Approach

### Prong 1: High-Quality News Sources 📰 (Primary)

**Rationale**: Professional journalism = formal, edited, consistent quality

**Sources to scrape:**

1. **Rudaw** (rudaw.net/sorani) - Major Kurdish news
2. **BasNews** (basnews.com) - Independent news
3. **NRT** (nrttv.com) - TV network news
4. **K24** (k24.tv) - News network
5. **KurdPress** (kurdpress.com) - News agency

**Target**: 2,000-3,000 lines from news articles

**Quality filters:**

- ZWNJ density: 8-12% (similar to Phase 4's 9.46%)
- Sentence length: 10-25 words (formal style)
- Kurdish script: >85% (minimal Latin mixing)
- Article date: Recent (2020-2024)
- Categories: Politics, culture, sports, economy (diverse)

**Expected improvement**: +2-4% accuracy (74-76%)

### Prong 2: Official/Government Documents 📜 (Secondary)

**Rationale**: Highest formality, consistent terminology

**Sources:**

1. **Kurdistan Regional Government** (gov.krd) - Official announcements
2. **Kurdistan Parliament** - Legislative texts
3. **Ministry websites** - Official communications
4. **Legal documents** - Laws, regulations, contracts
5. **Academic papers** - Kurdish universities

**Target**: 500-1,000 lines from official texts

**Quality filters:**

- ZWNJ density: 10-15% (formal documents have high ZWNJ usage)
- Sentence length: 15-35 words (formal, complex)
- Technical terminology: Legal, administrative, academic
- Formatting: Clean, no tables/lists

**Expected improvement**: +1-2% accuracy (75-77%)

### Prong 3: Kurdish Literature 📚 (Tertiary)

**Rationale**: High-quality prose, diverse vocabulary

**Sources:**

1. **Classic literature** - Digitized Kurdish novels/poetry
2. **Modern literature** - Contemporary Kurdish writers
3. **Translated works** - High-quality translations into Kurdish
4. **Children's books** - Simple but correct Kurdish
5. **Short stories** - Diverse styles and topics

**Target**: 1,000-1,500 lines from literature

**Quality filters:**

- ZWNJ density: 6-10% (literature varies)
- Sentence length: 8-30 words (narrative style)
- Published works: Books, not blog posts
- Editing: Professional editing/publishing

**Expected improvement**: +1-2% accuracy (76-78%)

---

## Phase 6 Execution Plan

### Step 1: Build Infrastructure (Day 1) 🛠️

**Create scraping tools:**

```python
# tools/scrape_kurdish_news.py
# - Extract from Rudaw, BasNews, NRT
# - Clean HTML, extract text
# - Filter by ZWNJ density, length, script purity
# - Remove duplicates
# - Output: kurdish_news_batch1.txt (500 lines)

# tools/corpus_quality_checker.py
# - Measure ZWNJ density
# - Check sentence length distribution
# - Detect script purity (Kurdish %)
# - Grade quality 1-5 stars
# - Output: quality_report.json
```

**Create evaluation pipeline:**

```bash
# workflow/incremental_training.sh
# 1. Backup current corpus (3,321 lines)
# 2. Add new batch (500 lines)
# 3. Train model (use Phase 4 Farsi checkpoint as starting point)
# 4. Evaluate accuracy on mgk.tif
# 5. If improved: keep batch, continue
# 6. If worse: discard batch, try different source
```

### Step 2: Extract News Corpus (Day 2-3) 📰

**Action**: Scrape 3 major news sites

**Process:**

1. **Rudaw**: Extract 1,000 articles → filter → 800 lines
2. **BasNews**: Extract 800 articles → filter → 600 lines
3. **NRT**: Extract 600 articles → filter → 400 lines
4. **Total**: 1,800 lines (target 8-12% ZWNJ)

**Quality check:**

- Manual review of 50 random samples
- Verify ZWNJ density in target range
- Check for HTML artifacts, encoding issues
- Remove duplicates with Phase 4 corpus

**Deliverable**: `corpus/kurdish_news.txt` (1,800 high-quality lines)

### Step 3: Incremental Training - Batch 1 (Day 4) 🔄

**Batch 1: First 500 news lines**

```bash
# Add to Phase 4 corpus
cat corpus/ckb_phase4.training_text > corpus/ckb_phase6_batch1.txt
head -500 corpus/kurdish_news.txt >> corpus/ckb_phase6_batch1.txt

# Result: 3,821 lines (3,321 + 500)

# Train
cp corpus/ckb_phase6_batch1.txt corpus/ckb.training_text
./run_training.ps1 -Mode GenerateTrain

# Evaluate
cd work && python3 tools/eval_real_cer.py
```

**Decision criteria:**

- **If accuracy ≥ 72.5%** (+0.31%): ✅ Keep batch, proceed to Batch 2
- **If accuracy 72.0-72.4%**: ⚠️ Marginal, review quality, maybe keep
- **If accuracy < 72.0%**: ❌ Discard batch, try different news source

### Step 4: Incremental Training - Batch 2-5 (Day 5-8) 🔄

**Repeat process for 4 more batches:**

- **Batch 2**: Lines 501-1,000 (news) → Target: 4,321 lines, 73-74% accuracy
- **Batch 3**: Lines 1,001-1,500 (news) → Target: 4,821 lines, 74-75% accuracy
- **Batch 4**: Lines 1,501-1,800 (news) + 200 official → Target: 5,521 lines, 75-76% accuracy
- **Batch 5**: 300 official + 200 literature → Target: 6,021 lines, 76-77% accuracy

**Expected progress:**

```
Batch 1 (3,821 lines): 72.5% (+0.31%)
Batch 2 (4,321 lines): 73.5% (+1.31%)
Batch 3 (4,821 lines): 74.5% (+2.31%)
Batch 4 (5,521 lines): 75.5% (+3.31%)
Batch 5 (6,021 lines): 76.5% (+4.31%)
```

### Step 5: Push to 80% (Day 9-12) 🎯

**If Batch 5 reaches 76-77%:**

Add 3-4 more batches focusing on official/literature:

- **Batch 6**: 500 official documents → 6,521 lines, 77-78%
- **Batch 7**: 500 literature → 7,021 lines, 78-79%
- **Batch 8**: 500 mixed (news+official) → 7,521 lines, 79-80%
- **Batch 9**: 500 high-ZWNJ content → 8,021 lines, 80%+

**Target**: 80% accuracy with ~8,000 high-quality lines

### Step 6: ZWNJ Rules Retry (Day 13-14) 🎯

**Once accuracy ≥ 80%:**

1. **Generate fresh OCR** with 80% model
2. **Apply improved ZWNJ rules**:

   - Pattern 1: Insert ZWNJ after ه + consonant
   - Pattern 2: Insert ZWNJ in common words (ئەوەی, دەبێ, etc.)
   - Pattern 3: Context-aware insertion (verb conjugations)

3. **Measure ZWNJ recovery**:

   - **Target**: 60-75% recovery (vs 7.8% at 71.69%)
   - **Baseline**: 294 true ZWNJs in mgk.tif

4. **Expected outcome**:
   - Character accuracy: 80%
   - ZWNJ recovery: 60-75% (176-220 out of 294)
   - **Combined quality**: Production-ready OCR

---

## Alternative: Phase 6B (If News Sources Insufficient)

### If news scraping fails or quality is poor:

**Pivot to manual curation:**

1. **Hire Kurdish speaker** (Upwork, Fiverr) - $50-100

   - Task: Manually type 2,000 high-quality Kurdish sentences
   - Requirements: Proper ZWNJ usage, formal style, diverse topics
   - Quality: 9-12% ZWNJ density, professional writing

2. **Use GPT-4 generation** (experimental):

   - Prompt: "Generate formal Kurdish sentences with proper ZWNJ usage"
   - Filter: Only keep sentences with 8-12% ZWNJ
   - Verify: Manual review by Kurdish speaker
   - Risk: May have grammatical errors or unnatural phrasing

3. **Keyboard crowd-sourcing**:
   - Create simple web form for Kurdish speakers
   - Ask community to contribute quality sentences
   - Incentive: Credit in project, small reward
   - Review: Manual quality check before adding

---

## Risk Mitigation

### Risk 1: News websites block scraping

**Mitigation:**

- Use respectful scraping (rate limiting, User-Agent)
- Try RSS feeds first (official API-like)
- Manual copy-paste if necessary (slower but reliable)
- Pre-downloaded archives (archive.org)

### Risk 2: Quality still insufficient

**Mitigation:**

- Stricter quality filters (10-12% ZWNJ only)
- Manual review of every batch before adding
- Create "gold standard" sample (100 perfect lines)
- Measure similarity to gold standard

### Risk 3: Accuracy plateaus before 80%

**Mitigation:**

- Accept plateau level (e.g., 77-78%)
- Try ZWNJ rules anyway (may work at 78%)
- Focus on post-processing instead of base accuracy
- Investigate training hyperparameters (learning rate, iterations)

### Risk 4: Training time too long

**Mitigation:**

- Use smaller batches (250 lines instead of 500)
- Train only until convergence (early stopping)
- Use fast evaluation (subset of test images)
- Parallel experiments (try multiple batches simultaneously)

---

## Success Metrics

### Phase 6 Success Criteria

**Minimum (acceptable):**

- ✅ Reach 75% accuracy (+2.81%)
- ✅ Add 1,500+ high-quality lines
- ✅ Maintain ZWNJ density 8-12%
- ✅ Enable 40-50% ZWNJ recovery

**Target (good):**

- ✅ Reach 78% accuracy (+5.81%)
- ✅ Add 3,000+ high-quality lines
- ✅ Maintain ZWNJ density 9-12%
- ✅ Enable 55-65% ZWNJ recovery

**Stretch (excellent):**

- ✅ Reach 80%+ accuracy (+7.81%+)
- ✅ Add 5,000+ high-quality lines
- ✅ Maintain ZWNJ density 9-12%
- ✅ Enable 65-75% ZWNJ recovery

### Timeline

**Estimated**: 10-14 days (depends on scraping efficiency)

- **Days 1-3**: Infrastructure + news scraping
- **Days 4-8**: Incremental training (5 batches)
- **Days 9-12**: Push to 80% (if needed)
- **Days 13-14**: ZWNJ rules retry

**Fast track**: If news sources excellent, could reach 80% by Day 8

---

## Phase 6 Deliverables

### Code/Tools

- `tools/scrape_kurdish_news.py` - News scraper
- `tools/scrape_kurdish_official.py` - Official documents scraper
- `tools/corpus_quality_checker.py` - Quality measurement
- `workflow/incremental_training.sh` - Automated training pipeline

### Corpus Files

- `corpus/kurdish_news.txt` - 1,800 news lines
- `corpus/kurdish_official.txt` - 500-1,000 official lines
- `corpus/kurdish_literature.txt` - 1,000-1,500 literature lines
- `corpus/ckb_phase6.training_text` - Final Phase 6 corpus (7,500-8,000 lines)

### Models

- `ckb_phase6_batch1.traineddata` through `ckb_phase6_batch9.traineddata`
- `ckb_phase6_final.traineddata` - Best performing model (target 80%)

### Documentation

- `PHASE6_PROGRESS.md` - Detailed progress tracking
- `PHASE6_RESULTS.md` - Final results and analysis
- `CORPUS_SOURCES.md` - Documentation of all sources used

---

## Conclusion

**Phase 6 Strategy**: Quality-first incremental expansion

**Key differences from Phase 5:**

- ✅ Professional sources (news, official, literature) NOT Wikipedia
- ✅ Small batches (500 lines) with evaluation after each
- ✅ Only keep batches that improve accuracy
- ✅ Target 8-12% ZWNJ density (maintain Phase 4's 9.46%)
- ✅ Strict quality filters and manual review

**Expected outcome**: 80% accuracy with ~8,000 high-quality lines, enabling 60-75% ZWNJ recovery

**Timeline**: 10-14 days

**Ready to start Phase 6?** First step is creating the scraping tools and extracting news corpus.
