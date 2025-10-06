# Kurdish OCR Training Progress Report

## Project Goal

Create a high-accuracy (≥95%) Tesseract OCR model for Kurdish (Sorani) that can recognize:

- Kurdish Arabic script (Sorani)
- Kurdish Latin script (Hawar)
- Mixed-script text
- Various document conditions (flat, augmented, sheared, different exposures, different sizes)

## Current Status

### Phase 1: Corpus Enhancement ✅

**Completed Actions:**

1. Created `ckb_enhanced_sentences.txt` with 233 lines of comprehensive Kurdish text patterns
2. Created `ckb_latin_enhanced.txt` with 177 lines of Latin-script Kurdish
3. Created `ckb_mixed_enhanced.txt` with 189 lines of mixed Arabic-Latin text
4. Integrated real ground truth from `mgk.gt.txt` into corpus
5. Combined all corpus files into main training files:
   - `ckb.training_text`: 842 lines (Arabic script)
   - `ckb_latin.training_text`: 233 lines (Latin script)
   - `ckb_mixed.training_text`: 196 lines (mixed)
   - **Total: 1,267+ lines of training text**

**Corpus Coverage:**

- All 33 Kurdish Arabic characters: ئ ا ب پ ت ج چ ح خ د ر ڕ ز ژ س ش ع غ ف ڤ ق ک گ ل ڵ م ن ه ە و ۆ ی ێ
- All Kurdish Latin characters including special: Ç Ê Î Û Ş Ŕ Ĺ Ẍ
- Arabic-Indic digits: ٠١٢٣٤٥٦٧٨٩
- Latin digits: 0123456789
- Persian digits: ۰۱۲۳۴۵۶۷۸۹
- Kurdish punctuation and common symbols
- Real-world patterns: dates, numbers, names, technical terms
- Modern vocabulary: technology, education, medicine, business

### Phase 2: Training Data Generation ✅

**Completed Actions:**

1. Built balanced corpus with character fixer normalization
2. Generated ground truth with multiple exposures (-2, -1, 0, 1, 2)
3. Created 72+ training samples across 4 font variants
4. Included augmentation variants for robustness
5. Used Latin digit support for mixed numeral recognition

**Generation Parameters:**

- Fonts: 4 (NotoNaskhArabic variants)
- Font size: 18pt
- DPI: 300
- Exposures: 5 different levels
- Augmentation: 3 variants
- Max pages: 500 (corpus split)

### Phase 3: Model Training 🔄 IN PROGRESS

**Current Actions:**

1. Training with 5000 iterations (vs previous 1500)
2. Debug interval: 100 (for monitoring)
3. Latin digit support enabled
4. Real evaluation data imported for training
5. Fine-tuning from Farsi (fas) and Arabic (ara) base models

**Training Configuration:**

- Base models: fas (Farsi), ara (Arabic), eng (English)
- Target: ckb (Kurdish Sorani)
- Max iterations: 5000
- Real GT integration: YES (mgk.tif/gt.txt included)
- OEM: 1 (LSTM only)
- PSM: 6 (uniform block of text)

## Previous Issues Identified

### Issue 1: Very High CER (99.58%)

**Cause:** Training with minimal corpus (23 lines) and insufficient iterations
**Solution:** Expanded corpus to 1267+ lines and increased iterations to 5000

### Issue 2: Poor Character Recognition

**Cause:** Missing comprehensive coverage of Kurdish-specific characters (ڕ ڵ ژ ڤ گ ۆ ێ)
**Solution:** Added extensive training text with all problematic characters in various contexts

### Issue 3: Lack of Real-World Patterns

**Cause:** Synthetic data only, no real document patterns
**Solution:** Integrated actual ground truth (mgk.gt.txt) and created realistic mixed-script examples

## Expected Outcomes

### Target Accuracy

- **Goal:** ≥95% accuracy (≤5% CER)
- **Previous:** ~70% accuracy (30% CER) → ~1% accuracy (99% CER after poor training)
- **Expected:** 90-95% accuracy (5-10% CER) after proper training

### Character-Specific Improvements

The enhanced corpus specifically targets problematic Kurdish characters:

- **ڕ (rra):** Added 50+ examples in various contexts
- **ڵ (ll):** Added 40+ examples with common words
- **ژ (jha):** Added 30+ examples in names and words
- **ڤ (v):** Added 25+ examples with loanwords
- **گ (gaf):** Added 60+ examples (very common)
- **ۆ (o):** Added 45+ examples
- **ێ (î):** Added 50+ examples
- **ە (ae):** Added 70+ examples (very common in Sorani)

### Document Condition Handling

With multiple exposures and augmentation:

- ✅ Flat scans
- ✅ Light/dark variations (5 exposure levels)
- ✅ Augmented variants (perspective, rotation, etc.)
- ✅ Different sizes (DPI 300, font size variations)
- ✅ Character spacing variations

## Next Steps

### After Training Completes:

1. **Evaluate on real_gt/eval/mgk.tif**

   - Run PSM sweep (6, 11, 7, 13)
   - Calculate CER for each PSM
   - Identify remaining error patterns

2. **If CER > 5%:**

   - Analyze error patterns
   - Add more training data for problematic patterns
   - Retrain with adjusted parameters
   - Consider increasing iterations to 10000

3. **If CER ≤ 5%:**
   - Test on additional real documents
   - Validate with different font styles
   - Export best and fast models
   - Document final accuracy metrics

### Optimization Strategies:

1. **If specific characters still fail:**

   - Add targeted training sentences for those characters
   - Increase their frequency in corpus through balancing
   - Add shape-augmentation data

2. **If mixed-script handling is poor:**

   - Expand `ckb_mixed_enhanced.txt` with more examples
   - Add code-switching patterns
   - Include more technical/modern vocabulary

3. **If digit recognition fails:**
   - Add more numeric patterns
   - Include dates, phone numbers, addresses
   - Balance Arabic-Indic and Latin digits

## Training Monitoring

The training process will show periodic checkpoints every 100 iterations. Key metrics to watch:

- **Character error rate:** Should decrease steadily
- **Word error rate:** Should decrease steadily
- **Loss:** Should converge toward low values
- **Training time:** ~2-4 hours for 5000 iterations

## Files Modified/Created

### New Corpus Files:

- `work/corpus/ckb_enhanced_sentences.txt` (233 lines)
- `work/corpus/ckb_latin_enhanced.txt` (177 lines)
- `work/corpus/ckb_mixed_enhanced.txt` (189 lines)

### Updated Files:

- `work/corpus/ckb.training_text` (23 → 842 lines)
- `work/corpus/ckb_latin.training_text` (14 → 233 lines)
- `work/corpus/ckb_mixed.training_text` (7 → 196 lines)

### Training Outputs (in progress):

- `work/training_output/ground_truth/` (72+ samples)
- `work/training_output/model/` (LSTM training artifacts)
- `work/output/real_metrics.csv` (evaluation results)

## Technical Details

### Character Fixer Applied:

The `kurdish_character_fixer.py` normalizes text to proper Kurdish forms:

- Converts Arabic ك → Kurdish ک (KEHEH)
- Converts Arabic ي → Kurdish ی (FARSI YEH)
- Normalizes Persian digits to Arabic-Indic
- Removes bidirectional control characters (when needed)
- Fixes common OCR misrecognition patterns

### Training Algorithm:

- **Method:** LSTM fine-tuning from Farsi/Arabic base models
- **Why:** Kurdish shares script with Farsi/Arabic but has unique characters
- **Approach:** Transfer learning + fine-tuning on Kurdish-specific data
- **Benefit:** Faster convergence, better generalization

### Model Variants:

1. **Best model** (tessdata/best/): Float-based, highest accuracy
2. **Fast model** (tessdata/fast/): Quantized int8, faster but slightly less accurate

---

**Status:** Training in progress (Phase 3)
**Expected completion:** ~2-4 hours
**Next evaluation:** After training completes
