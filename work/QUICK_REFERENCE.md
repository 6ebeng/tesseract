# BATCH 3 SCRAPER - QUICK REFERENCE

## ✅ Integration Complete!

**File**: `expand_corpus_batch3_reliable.py`
**Line count**: ~1,109 lines
**Scrapers**: 11 total

## 🎯 What's New

### Rudaw Specialized (Line 779)

- 4 categories: Economy, Health, Sport, **Culture**
- Expected: ~800 sentences

### Kurdistan24 Specialized (Line 880)

- 7 categories: **Economy**, Health, Sport, Culture, **Artistic**, Technology, **Social**
- Uses FlareSolverr (bypass Cloudflare)
- Expected: ~1,050 sentences

## 📊 Expected Results

**Total sentences**: 14,550+
**Increase**: 210% from baseline
**Topic categories**: 9 (Political, Sport, Economy, Health, Science, Tech, Culture, Art, Social)

## 🚀 How to Run

### Step 1: Start FlareSolverr

```powershell
wsl -d Ubuntu -- sudo docker start flaresolverr
```

### Step 2: Execute Collection

```powershell
.\run_training.ps1 -Mode ExpandCorpus
```

**Runtime**: 110-150 minutes

### Step 3: Check Output

File: `work/corpus/kurdish_expanded_batch3.txt`

## 🔍 All 11 Scrapers

1. ✅ Kurdsat (political) - 30 clicks
2. ✅ Rudaw (political) - 20 scrolls
3. ✅ Khak TV (political) - 10 pages
4. ✅ NRT TV (political) - 15 clicks
5. ✅ Awene (political) - 10 pages
6. ✅ Kurdistan24 (political) - 10 pages + FlareSolverr
7. ✅ Xendan (political) - 10 pages
8. ✅ Xendan Specialized - Sport/Economy/Tech (5 pages/cat)
9. ✅ Kurdsat Specialized - Health/Science/Tech (20 articles/cat)
10. ✅ **Rudaw Specialized** - Economy/Health/Sport/Culture (10 scrolls/cat)
11. ✅ **K24 Specialized** - 7 categories (5 pages/cat + FlareSolverr) ⭐

## 🎨 New Vocabulary Categories

- **Economy**: Gold prices, finance, investments (3 sources now!)
- **Artistic**: Film festivals, theater, art competitions
- **Social**: Political forces, marriage stats, traffic accidents
- **Enhanced Medical**: Thalassemia, blood tests, early screening

---

**Status**: READY TO EXECUTE ✅
**Date**: October 21, 2025
