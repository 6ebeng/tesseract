# Work area (WSL)

This folder contains all scripts and data used for generating ground truth and training the Kurdish `ckb` model for Tesseract.

Key scripts:

- `generate_ckb_training_data.sh`: renders synthetic ground-truth from the corpus using local fonts.
- `execute_ckb_training.sh`: runs the LSTM fine-tuning pipeline and exports `ckb.traineddata`.
- `verify_ckb_traineddata.py`: checks that a traineddata covers Kurdish characters.
- `tools/eval_real_cer.py`: computes real-world CER on `real_gt/eval` image+gt pairs and writes `output/real_metrics.csv`.

Data layout:

- `corpus/ckb.training_text`: main corpus used to render text.
- `corpus/ckb.training_text.final`: final built corpus produced by the corpus builder (recommended).
- `tools/corpus_build.py`: builds high-quality balanced corpus with character normalization
- `kurdish_character_fixer.py`: normalizes Kurdish text (ه‌→ە, ھ→ه, quote normalization, etc.)
- Optional curated additions the generator will auto-include when present:
  - `corpus/ckb_core_coverage.txt`, `corpus/ckb_extra_sentences.txt`, `corpus/ckb_formats_ner.txt`
  - `corpus/ckb_latin.training_text`, `corpus/ckb_latin_core_coverage.txt`, `corpus/ckb_latin_extra_sentences.txt`, `corpus/ckb_latin_formats_ner.txt`
  - `corpus/ckb_mixed.training_text` (Arabic + Latin in same lines)
- `fonts/`: TTF files used to render images.
- `training_output/`: generated artifacts (ground truth, tmp, model output). Ignored by Git.

Run everything from Windows using the repo launcher:

```powershell
# Build high-quality corpus with normalization
./run_training.ps1 -Mode BuildCorpus -UseFixer -StripZWNJ -MinLength 20 -MaxLength 300 -MaxNonKurdish 10.0 -CorpusMinCount 1

# Generate training data and train model
./run_training.ps1 -Mode GenerateTrain
```

### Corpus Building Options

The corpus builder (`tools/corpus_build.py`) supports advanced quality filtering:

- `-UseFixer`: Apply Kurdish character normalization (ه‌→ە, ھ→ه, quotes, etc.)
- `-StripZWNJ`: Remove ZWNJ after ه‌→ە conversion (recommended for clean corpus)
- `-MinLength 20`: Minimum sentence length (default: 10)
- `-MaxLength 300`: Maximum sentence length (default: 500)
- `-MaxNonKurdish 10.0`: Max % of non-Kurdish characters (default: 30%)
- `-CorpusMinCount 1`: Minimum character count threshold

**Example - High Quality Corpus:**

```powershell
./run_training.ps1 -Mode BuildCorpus -UseFixer -StripZWNJ -MinLength 20 -MaxLength 300 -MaxNonKurdish 10.0 -CorpusMinCount 1
```

**Results:**

- ~20,830 high-quality sentences
- 0% ZWNJ density (clean text)
- 99.998% character purity
- Average quality score: 9.51/10.0

**Character Normalization:**

- ه‌ → ە (converts old ZWNJ workaround to proper Kurdish letter)
- ھ → ه (Arabic HEH DOACHASHMEE to standard HEH)
- Quote normalization (" → «, " → »)
- Punctuation standardization

Or run individual steps inside WSL by `cd` into this folder.

Real eval (optional):

- Put a few real images and their matching `.gt.txt` under `real_gt/eval/`.
- Then run: `python3 tools/eval_real_cer.py` (from this folder in WSL) to get average CER.

Real GT for training (optional):

- You can place additional real pages under `real_gt/train/`. When training runs with `IMPORT_REAL_EVAL=1` (toggle exposed in the Windows driver via `-TrainUseRealEval`), both `real_gt/train/` and `real_gt/eval/` will be imported as `real_*.tif/gt.txt` into the GT set, and boxes will be bootstrapped automatically. If you want to strictly hold out eval, leave `-TrainUseRealEval` off or keep pages only in `real_gt/eval/`.

Useful generation flags in the Windows driver (`run_training.ps1`): `-MaxPages`, `-CharsPerPage`, `-EnableAug`, `-AugVariants`, `-Exposures`.
Training flags: `-MaxIters`, `-DebugInterval`, `-ForceMinimal`, `-LatinDigits`, `-PuncsExtra`, `-TrainUseRealEval`.
