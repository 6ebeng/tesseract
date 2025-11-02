# Phase 7 WSL Ubuntu Command Reference

All commands should be run in WSL Ubuntu environment.

## Quick Setup

```bash
# Navigate to project
cd /mnt/c/tesseract

# Check Python version
python3 --version  # Should be 3.8+
```

---

### Source Discovery & Validation

### 1. Check Your Existing Scraper System

```bash
cd /mnt/c/tesseract/work/tools/scrapers

# See available websites (13+ sites)
python3 generic_scraper.py --list

# Read documentation
cat PRODUCTION_SCRAPER_USAGE.md
cat README.md

# Scrape from specific site
python3 generic_scraper.py --website rudaw --category people
```

### 2. Validate a Sample

```bash
cd /mnt/c/tesseract

# Validate single file
python3 work/tools/validate_source_quality.py samples/your_sample.txt

# Validate all samples
python3 work/tools/validate_source_quality.py samples/*.txt
```

### 4. Analyze Unicode Characters

```bash
cd /mnt/c/tesseract

# Analyze specific file
python3 work/analyze_unicode_chars.py work/corpus/some_file.txt

# Check existing news corpus (high quality example)
python3 work/analyze_unicode_chars.py work/corpus/ckb_scraped_filtered.training_text

# Check Wikipedia (bad example - 0.1% ZWNJ)
python3 work/analyze_unicode_chars.py work/corpus/ckb_wikipedia_bio_filtered.training_text
```

---

## Corpus Building (After Finding Good Sources)

### 5. Blend Multiple Sources

```bash
cd /mnt/c/tesseract

# Blend 2 sources to achieve target ZWNJ
python3 work/tools/blend_corpus.py \
    --sources work/corpus/source1.txt work/corpus/source2.txt \
    --output work/corpus/ckb_phase7.training_text \
    --target-zwnj 8.0

# Use equal proportions instead of weighted
python3 work/tools/blend_corpus.py \
    --sources work/corpus/source1.txt work/corpus/source2.txt \
    --output work/corpus/ckb_phase7.training_text \
    --equal
```

### 6. Apply Character Fixer

```bash
cd /mnt/c/tesseract/work

# Fix a corpus file
python3 kurdish_character_fixer.py \
    --input corpus/source_raw.txt \
    --output corpus/source_fixed.txt
```

---

## Training Pipeline (WSL Commands)

### 7. Build Balanced Corpus

From PowerShell (calls WSL internally):
```powershell
.\run_training.ps1 -Mode BuildCorpus -UseFixer -KeepRTLControls `
    -BalanceDigits -BalanceLatinDigits -BalancePuncs -CorpusMinCount 1
```

Or directly in WSL:
```bash
cd /mnt/c/tesseract/work
bash execute_ckb_training.sh build-corpus
```

### 8. Generate Training Data & Train

From PowerShell:
```powershell
.\run_training.ps1 -Mode GenerateTrain -LatinDigits
```

Or in WSL:
```bash
cd /mnt/c/tesseract/work
bash execute_ckb_training.sh generate-train
```

### 9. Evaluate Model

From PowerShell:
```powershell
# Quick test
.\run_training.ps1 -Mode SmokeTestBest

# Full PSM sweep
.\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13"
```

---

## File Management

### Create Sample File

```bash
cd /mnt/c/tesseract

# Create a test sample
cat > samples/test_sample.txt << 'EOF'
[Paste your Kurdish text here]
EOF

# Validate it
python3 work/tools/validate_source_quality.py samples/test_sample.txt
```

### List Files

```bash
cd /mnt/c/tesseract

# List samples
ls -lh samples/

# List corpus files
ls -lh work/corpus/*.txt

# Check disk usage
du -sh work/corpus/
du -sh work/training_output/
```

---

## Example Workflow

### Complete Source Validation Workflow

```bash
cd /mnt/c/tesseract

# Step 1: Get search links
python3 work/tools/source_finder.py

# Step 2: (Manual) Visit websites, copy 100-200 sentences
# Save as: samples/rudaw_biography_sample.txt

# Step 3: Validate the sample
python3 work/tools/validate_source_quality.py samples/rudaw_biography_sample.txt

# Step 4: If ACCEPT, document it
echo "Rudaw Biography | 8.5% | ACCEPT | 150 sentences" >> phase7_source_tracking.md

# Step 5: Acquire full text (manual or scrape)
# Save as: work/corpus/rudaw_biography_full.txt

# Step 6: Validate full corpus
python3 work/tools/validate_source_quality.py work/corpus/rudaw_biography_full.txt

# Step 7: Blend with existing news corpus
python3 work/tools/blend_corpus.py \
    --sources work/corpus/ckb_scraped_filtered.training_text \
              work/corpus/rudaw_biography_full.txt \
    --output work/corpus/ckb_phase7_blended.training_text \
    --target-zwnj 8.0

# Step 8: Validate blended result
python3 work/tools/validate_source_quality.py work/corpus/ckb_phase7_blended.training_text
```

---

## Troubleshooting

### Check if tools are working

```bash
cd /mnt/c/tesseract

# Test validator
python3 work/tools/validate_source_quality.py work/corpus/ckb_scraped_filtered.training_text | head -20

# Test unicode analyzer
python3 work/analyze_unicode_chars.py work/corpus/ckb_scraped_filtered.training_text | head -20

# Test source finder
python3 work/tools/source_finder.py | head -30
```

### Check Python dependencies

```bash
python3 -c "import re, sys, pathlib; print('OK')"
```

---

## Quick Reference Card

```bash
# Navigate to project
cd /mnt/c/tesseract

# Get search links
python3 work/tools/source_finder.py

# Validate sample
python3 work/tools/validate_source_quality.py samples/your_sample.txt

# Analyze ZWNJ
python3 work/analyze_unicode_chars.py work/corpus/file.txt

# Blend corpora
python3 work/tools/blend_corpus.py --sources file1.txt file2.txt --output blended.txt

# Train model (from PowerShell)
.\run_training.ps1 -Mode GenerateTrain -LatinDigits

# Evaluate (from PowerShell)
.\run_training.ps1 -Mode SmokeTestBest
```

---

## Key Reminders

1. **ZWNJ 6-10% is mandatory** - Validate BEFORE acquiring full text
2. **News corpus: 9.33% ZWNJ** - Excellent quality (use as reference)
3. **Wikipedia: 0.11% ZWNJ** - Rejected (too low)
4. **Target: 500-1,000 biographical sentences** with 7-9% blended ZWNJ
5. **Expected result: 71.69% → 76%+** on mgk.tif

---

## Documentation

- **Phase 7 Plan:** `/mnt/c/tesseract/PHASE7_IMPROVEMENT_PLAN.md`
- **Quick Start:** `/mnt/c/tesseract/PHASE7_QUICKSTART.md`
- **Source Tracking:** `/mnt/c/tesseract/phase7_source_tracking.md`
- **Samples README:** `/mnt/c/tesseract/samples/README.md`
