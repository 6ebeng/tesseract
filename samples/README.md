# Phase 7 Samples Directory

This directory is for storing sample texts from potential Kurdish biographical sources.

## Purpose

Before acquiring full text from a source, extract a 100-200 sentence sample and validate its ZWNJ density here.

## Workflow

1. **Find Source:** Use `python work/tools/source_finder.py` for search links
2. **Extract Sample:** Copy 100-200 sentences to a file
3. **Save Here:** `samples/source_name_sample.txt`
4. **Validate:** `python work/tools/validate_source_quality.py samples/source_name_sample.txt`
5. **Check Result:**
   - ✅ **ACCEPT** (6-10% ZWNJ) → Acquire full text
   - ⚠️ **REVIEW** (borderline) → Check issues
   - ❌ **REJECT** (<6% ZWNJ) → Skip this source
6. **Document:** Update `phase7_source_tracking.md`

## Example

```bash
# Save sample text
# File: samples/archive_org_biography_sample.txt

# Validate it
python work/tools/validate_source_quality.py samples/archive_org_biography_sample.txt

# Output will show:
# ✅ ACCEPT: 8.5% ZWNJ, 92% Kurdish script
# or
# ❌ REJECT: 0.3% ZWNJ (unusable)
```

## Quick Commands

```bash
# Validate one sample
python work/tools/validate_source_quality.py samples/your_sample.txt

# Validate all samples at once
python work/tools/validate_source_quality.py samples/*.txt
```

## What to Look For

**Good sources (ACCEPT):**

- ZWNJ: 6-10%
- Kurdish script: >85%
- Domain: Biographical, historical, literary
- Quality: Natural Kurdish text

**Bad sources (REJECT):**

- ZWNJ: <6% (too low - will degrade model)
- Lots of Latin/English text
- Machine-translated text
- Wikipedia Kurdish (0.1% ZWNJ - corrupted)

## Target

Find **3-5 validated sources** with:

- Total: 500-1,000 biographical sentences
- ZWNJ: 7-9% (blended)
- Quality: >85% Kurdish script

Expected result: **mgk.tif accuracy 71.69% → 76%+**

---

**Remember:** ALWAYS validate BEFORE acquiring full text (saves time!)
