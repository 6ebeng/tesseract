# run_training.ps1 - Complete Options Reference

## Available Modes

### Generation Modes

- **`ImprovedGenerate`** - Generate training data with parallel processing and augmentation

  ```powershell
  .\run_training.ps1 -Mode ImprovedGenerate -TrainingProfile Best -ParallelJobs 5 -OutputDirOverride "Z:\training_output_best"
  ```

- **`Generate`** - Legacy sequential training data generation

  ```powershell
  .\run_training.ps1 -Mode Generate -TrainingProfile Fast
  ```

- **`ImprovedGenerateTrain`** - Generate training data and train model in one command

  ```powershell
  .\run_training.ps1 -Mode ImprovedGenerateTrain -TrainingProfile Best -ParallelJobs 5
  ```

- **`GenerateTrain`** - Legacy generate and train pipeline
  ```powershell
  .\run_training.ps1 -Mode GenerateTrain
  ```

### Training Mode

- **`Train`** - Train model from existing ground truth data

  ```powershell
  .\run_training.ps1 -Mode Train -TrainingProfile Best -OutputDirOverride "Z:\training_output_best" -MaxIters 2000
  ```

- **`Train` with Batch Processing** - Efficiently process large datasets on network drives

  ```powershell
  # Process large datasets in batches for optimal performance
  .\run_training.ps1 -Mode Train -TrainingProfile Best `
      -OutputDirOverride "Z:\training_output_best" `
      -UseBatchProcessing -BatchSize 500 -BatchWorkers 22
  ```

  **Batch Processing Features:**

  - Copies file sets (TIF + GT + BOX) in batches to local SSD for fast processing
  - TRUE parallel LSTMF generation using GNU Parallel
  - Automatic resume capability (skips already processed files)
  - Real-time progress with worker IDs and timestamps
  - Pre-validation ensures only complete file sets are processed
  - Incremental network transfer after each batch

  **Parameters:**

  - `-UseBatchProcessing` - Enable batch processing mode
  - `-BatchSize <int>` - Number of file sets per batch (default: 5000, recommend: 500 for optimal performance)
    - Each set = 3 files (TIF + GT + BOX)
    - BatchSize 100 = 300 files, BatchSize 500 = 1500 files
  - `-BatchWorkers <int>` - Parallel workers (default: 22, max: CPU threads)

  **Recommended Settings:**

  - **Batch Size**: 500 file sets (1500 files) for optimal balance
  - **Workers**: 22 on 24-thread CPU (90% utilization, leaves 2 for system)
  - **Performance**: 100-340 file sets/min with 22 workers
  - **Typical Time**: 5-15 minutes to process 1500+ complete file sets

### Testing Modes

- **`SmokeTest`** - Quick test with auto-detect profile

  ```powershell
  .\run_training.ps1 -Mode SmokeTest
  ```

- **`SmokeTestBest`** - Test using Best profile model

  ```powershell
  .\run_training.ps1 -Mode SmokeTestBest -ImagePath "samples\test.png"
  ```

- **`SmokeTestFast`** - Test using Fast profile model

  ```powershell
  .\run_training.ps1 -Mode SmokeTestFast -ImagePath "samples\test.png"
  ```

- **`Eval`** - Comprehensive evaluation with real ground truth
  ```powershell
  .\run_training.ps1 -Mode Eval -EvalPSMs "6,11,7,13" -TrainingProfile Best
  ```

### Corpus Management

- **`BuildCorpus`** - Build training corpus from text files

  ```powershell
  .\run_training.ps1 -Mode BuildCorpus -UseFixer -CorpusMinCount 2
  ```

- **`ExpandCorpus`** - Expand existing corpus with additional sources

  ```powershell
  .\run_training.ps1 -Mode ExpandCorpus
  ```

- **`ScrapeCorpus`** - Scrape Kurdish websites for corpus data
  ```powershell
  .\run_training.ps1 -Mode ScrapeCorpus -ScraperAll -ScraperWorkers 5 -ScraperFresh
  ```

### Utility Modes

- **`Bootstrap`** - Download base models and set up environment

  ```powershell
  .\run_training.ps1 -Mode Bootstrap
  ```

- **`DownloadFonts`** - Download additional Kurdish/Arabic fonts

  ```powershell
  .\run_training.ps1 -Mode DownloadFonts
  ```

- **`Clean`** - Clean up generated files

  ```powershell
  .\run_training.ps1 -Mode Clean -Deep
  ```

- **`All`** - Full pipeline: corpus → generate → train → evaluate
  ```powershell
  .\run_training.ps1 -Mode All -TrainingProfile Best -ParallelJobs 5
  ```

## Training Profiles

### Best Profile (Recommended for Production)

- **Duration**: 2-3 days (generation + training)
- **Parameters**:
  - Font sizes: 16, 18, 20, 22 pt (4 values)
  - DPI: 200, 300, 400 (3 values)
  - Leading: 20, 22, 26 px (3 values)
  - Char spacing: 0.5, 1.0, 1.5 (3 values)
  - Exposures: -2, -1, 0, 1, 2 (5 values)
  - Augmentation: 5 variants per image
- **Total images**: ~87,480 per 9 fonts = ~9,720 per font
- **Use case**: Maximum accuracy for production deployment

### Fast Profile (Quick Testing)

- **Duration**: 2-3 hours (generation + training)
- **Parameters**:
  - Font sizes: 16, 20 pt (2 values)
  - DPI: 200, 400 (2 values)
  - Leading: 22, 26 px (2 values)
  - Char spacing: 0.8, 1.2 (2 values)
  - Exposures: -1, 0, 1 (3 values)
  - Augmentation: 3 variants per image
- **Total images**: ~9,720 per 9 fonts = ~1,080 per font
- **Use case**: Rapid prototyping and testing

## Common Parameters

### Training Tunables

- **`-MaxIters <int>`** - Maximum training iterations (default: 1500)
- **`-DebugInterval <int>`** - Debug output interval (default: 0)
- **`-OEM <1|2|3>`** - OCR Engine Mode
- **`-PSM <3-13>`** - Page Segmentation Mode
- **`-TrainingExtraArgs <string>`** - Additional training arguments
- **`-ForceMinimal`** - Build minimal traineddata
- **`-LatinDigits`** - Include Latin digits (0-9) in training
- **`-PuncsExtra <string>`** - Additional punctuation characters
- **`-TrainUseRealEval`** - Use real evaluation data during training

### Data Generation Overrides

- **`-CorpusFileOverride <path>`** - Custom corpus file
- **`-FontsDirOverride <path>`** - Custom fonts directory
- **`-OutputDirOverride <path>`** - Custom output directory (e.g., "Z:\training_output_best")
- **`-GroundTruthDir <path>`** - Custom ground truth directory
- **`-FontSize <int>`** - Single font size override
- **`-FontSizes <string>`** - Comma-separated font sizes (e.g., "16,18,20")
- **`-DPI <int>`** - Single DPI override
- **`-DPIs <string>`** - Comma-separated DPI values (e.g., "200,300,400")
- **`-Margin <int>`** - Image margin in pixels
- **`-Leading <int>`** - Line spacing override
- **`-LeadingList <string>`** - Comma-separated leading values
- **`-CharSpacing <int>`** - Character spacing override
- **`-CharSpacings <string>`** - Comma-separated spacing values
- **`-Exposures <string>`** - Exposure levels (e.g., "-2 -1 0 1 2")
- **`-EnableAug`** - Enable augmentation
- **`-AugVariants <int>`** - Number of augmentation variants
- **`-MaxPages <int>`** - Maximum pages to generate
- **`-CharsPerPage <int>`** - Characters per page

### Parallel Processing

- **`-ParallelJobs <int>`** - Number of parallel workers (0 = sequential, recommended: 3-5)
  ```powershell
  .\run_training.ps1 -Mode ImprovedGenerate -ParallelJobs 5 -TrainingProfile Best
  ```

### Corpus Builder Options

- **`-UseFixer`** - Apply Kurdish character normalization/fixing
- **`-CorpusMinCount <int>`** - Minimum character frequency to include

### Scraper Options

- **`-ScraperAll`** - Scrape all enabled websites
- **`-ScraperWebsites <string>`** - Specific websites to scrape (space-separated)
- **`-ScraperWorkers <int>`** - Number of parallel scraper workers (default: 3)
- **`-ScraperFresh`** - Clear deduplication database before scraping

### Evaluation Options

- **`-EvalPSMs <string>`** - PSM modes to test (comma-separated, e.g., "6,11,7,13")
- **`-EvalUseGTLexicon`** - Use ground truth lexicon for evaluation
- **`-EvalPrep <string>`** - Preprocessing options
- **`-EvalHOCRLines`** - Extract lines from HOCR output
- **`-EvalHOCRPSM <int>`** - PSM mode for HOCR extraction
- **`-EvalUserWordsCorpus`** - Use corpus as user words
- **`-EvalDisableDAWGs`** - Disable DAWG files during evaluation

### General Options

- **`-NoClear`** - Don't clear screen before running
- **`-Deep`** - Deep clean (removes more files)
- **`-ImagePath <path>`** - Path to test image for smoke tests
- **`-SkipEval`** - Skip evaluation in All mode

## Example Workflows

### 1. Complete Training Pipeline (Best Quality)

```powershell
# Step 1: Download fonts
.\run_training.ps1 -Mode DownloadFonts

# Step 2: Build corpus
.\run_training.ps1 -Mode BuildCorpus -UseFixer -CorpusMinCount 2

# Step 3: Generate training data (parallel, on Z: drive)
.\run_training.ps1 -Mode ImprovedGenerate -TrainingProfile Best -ParallelJobs 5 -OutputDirOverride "Z:\training_output_best"

# Step 4: Train model
.\run_training.ps1 -Mode Train -TrainingProfile Best -OutputDirOverride "Z:\training_output_best" -MaxIters 2000 -LatinDigits

# Step 5: Evaluate
.\run_training.ps1 -Mode Eval -TrainingProfile Best -EvalPSMs "6,11,7,13"
```

### 2. Quick Test Workflow (Fast Profile)

```powershell
# All-in-one: build corpus, generate, train, evaluate
.\run_training.ps1 -Mode All -TrainingProfile Fast -ParallelJobs 3
```

### 3. Resume Training After Interruption

```powershell
# Training data already exists on Z:, just train
.\run_training.ps1 -Mode Train -TrainingProfile Best -OutputDirOverride "Z:\training_output_best"
```

### 4. Batch Processing Large Datasets (Network Drives)

```powershell
# Process large datasets efficiently with batch mode
.\run_training.ps1 -Mode Train -TrainingProfile Best `
    -OutputDirOverride "Z:\training_output_best" `
    -UseBatchProcessing -BatchSize 500 -BatchWorkers 22

# Output shows real-time progress with timestamp clustering (proof of parallel execution):
#   📦 Batch 1: Processing file sets 1 to 500
#   Found 1523 complete file sets (TIF+GT+BOX)
#   📋 Copying 500 file sets (1500 files: TIF+GT+BOX for each set)...
#   ⚡ Processing with 22 workers using GNU Parallel...
#   [W1 18:30:17] ✓ ckb.NotoKufiArabic-Bold.exp0 (fas)
#   [W2 18:30:17] ✓ ckb.NotoKufiArabic-Bold.exp1 (fas)
#   [W3 18:30:18] ✓ ckb.NotoKufiArabic-Bold.exp2 (ara)
#   [W4 18:30:18] ✓ ckb.NotoKufiArabic-Bold.exp3 (fas)
#   ...
#   Batch completed in 180s (processed: 500 file sets, generated: 498 LSTMF)
```

**How Batch Processing Works:**

1. **Validation Phase**: Pre-scans to find complete file sets (TIF + GT + BOX together)
2. **Copy Phase**: Copies batch of file sets (3 files each) to local SSD atomically
3. **Process Phase**: Launches GNU Parallel workers for TRUE parallel processing
4. **Transfer Phase**: Moves generated LSTMF files to network
5. **Cleanup Phase**: Removes local copies to free space
6. **Resume Phase**: Automatically skips already-processed file sets

**Key Features:**

- **File Set Integrity**: TIF+GT+BOX files always copied and processed together
- **GNU Parallel Execution**: Real parallel processing (timestamps cluster within 1-2 seconds)
- **Basename-based Processing**: Works with complete sets only
- **Automatic Resume**: Can interrupt and restart without losing progress

**Performance Tips:**

- **Verify Parallel Execution**: Watch timestamps - should cluster within 1-2 seconds
  - ✅ GOOD: `[W1 18:30:17] [W2 18:30:17] [W3 18:30:18]` (parallel working)
  - ❌ BAD: `[W1 19:47:18] [W2 19:49:05]` (sequential - 2 min gaps)
- **Batch Size**: 500 file sets recommended for optimal performance
- **Workers**: Set to 90% of CPU threads (22 on 24-thread CPU)
- **Expected Speed**: 100-340 file sets/min with 22 workers
- **Monitor Failed Files**: Logged with reasons (missing GT, model failures)

### 5. Test Trained Model

```powershell
# Quick smoke test
.\run_training.ps1 -Mode SmokeTestBest -ImagePath "samples\kurdish_text.png"

# Comprehensive evaluation
.\run_training.ps1 -Mode Eval -TrainingProfile Best -EvalPSMs "6,11,7,13"
```

## Batch Processing Deep Dive

### When to Use Batch Processing

✅ **Use batch processing when:**

- Processing 10,000+ ground truth files
- Files are on network drive (high latency)
- Direct processing is slow (< 10 files/min)
- Limited local disk space (cannot copy all files)

❌ **Don't use batch processing when:**

- Files already on local SSD
- Dataset is small (< 1000 files)
- Plenty of local disk space

### Configuration Guide

**Batch Size Selection:**

```powershell
# Small batches (100-200) - Quick testing and verification
-BatchSize 100  # 100 file sets = 300 files, ~1-3 GB space, 30-60 sec processing

# Medium batches (500) - RECOMMENDED for production
-BatchSize 500  # 500 file sets = 1500 files, ~5-15 GB space, 2-5 min processing

# Large batches (1000+) - Maximum throughput (requires more disk space)
-BatchSize 1000  # 1000 file sets = 3000 files, ~10-30 GB space, 3-10 min processing
```

**Worker Count:**

```powershell
# Conservative (50% CPU)
-BatchWorkers 12  # On 24-thread CPU

# Balanced (75% CPU)
-BatchWorkers 18  # On 24-thread CPU

# Aggressive (90% CPU) - Recommended
-BatchWorkers 22  # On 24-thread CPU, leaves 2 threads for system
```

### Output Interpretation

**Success Example (Parallel Execution Working):**

```
📦 Batch 1: Processing file sets 1 to 500
   Found 1523 complete file sets (TIF+GT+BOX)
   📥 Copying to local SSD...
   📋 Copying 500 file sets (1500 files: TIF+GT+BOX for each set)...
   ✓ Ready: 500 TIF files, 500 GT files, 500 BOX files
   ⚡ Processing with 22 workers using GNU Parallel...
   Started at: 18:30:15
   Processing 500 file sets...
   [W1 18:30:17] ✓ ckb.font1.exp0 (fas)
   [W2 18:30:17] ✓ ckb.font1.exp1 (fas)
   [W3 18:30:18] ✓ ckb.font1.exp2 (ara)
   [W4 18:30:18] ✓ ckb.font1.exp3 (fas)
   [W5 18:30:18] ✓ ckb.font1.exp4 (fas)
   ...
   [W22 18:30:19] ✓ ckb.font1.exp21 (fas)
   ... waiting for remaining jobs to complete
   Finished at: 18:33:45
   📊 Generated 498 LSTMF files in LOCAL_TMP
   📤 Moving 498 LSTMF files to network...
   ✅ Moved to network. Total in network: 498
   ✓ Batch completed in 210s (processed: 500 file sets, generated: 498 LSTMF)
   📊 Models: FAS=450 | ARA=48 | ENG=0 | Total=498
   📊 Progress: 498 / 1523 (33%) | Speed: 142 file sets/min | ETA: 7 min
```

**Key Metrics:**

- **Timestamp clustering**: Multiple workers completing within SAME second = parallel working ✅
  - Example: `[W1 18:30:17] [W2 18:30:17] [W3 18:30:18]` - all within 1-2 seconds
- **Speed**: Should see 100-340 file sets/min with 22 workers
- **File Sets vs Files**: BatchSize 500 = 500 sets = 1500 total files (TIF+GT+BOX)
- **Model distribution**: Most files use FAS (Persian), some ARA (Arabic), rare ENG
- **Failures**: Normal to have 1-2% failures, watch for patterns

**Parallel Verification (CRITICAL):**

```
✅ PARALLEL WORKING (timestamps cluster):
   [W1 18:30:17] ✓ file1 (fas)
   [W2 18:30:17] ✓ file2 (fas)    ← Same second as W1
   [W3 18:30:18] ✓ file3 (ara)    ← 1 second later
   [W4 18:30:18] ✓ file4 (fas)    ← Same second as W3

❌ SEQUENTIAL (timestamps minutes apart):
   [W1 19:47:18] ✓ file1 (fas)
   [W2 19:49:05] ✓ file2 (fas)    ← 2 MINUTES later - NOT parallel!
   [W3 19:51:22] ✓ file3 (ara)    ← 2 MINUTES later - sequential execution
```

**Failure Examples:**

```
[W5 18:30:19] ✗ FAILED: ckb.problem.exp99 (missing GT file)
[W7 18:30:22] ✗ FAILED: ckb.corrupt.exp123 (all models failed)
```

**Understanding Complete File Sets:**

- Each training example requires 3 files with the SAME basename:
  - `example.tif` (image)
  - `example.gt.txt` (ground truth text)
  - `example.box` (character bounding boxes)
- Pre-validation ensures only complete sets are processed
- Example: If you have 30,000 TIF files but only 1,500 have matching GT+BOX files, only those 1,500 complete sets will be processed

### Troubleshooting

**Problem: Sequential processing (timestamps MINUTES apart)**

```
❌ Symptom: [W1 19:47:18] ... [W2 19:49:05] ... [W3 19:51:22]
   Timestamps are 2+ minutes apart instead of clustering in same second
```

- **Root Cause**: GNU Parallel not being used or failed to install
- **Solution**:
  1. Verify GNU Parallel installed: `wsl -d Ubuntu -- bash -c "which parallel"`
  2. Check batch_lstmf_processor.sh uses `parallel -j "$WORKERS"`
  3. Expected fix: Timestamps should cluster within 1-2 seconds
- **Verification**: Look for timestamps clustering: `[W1 18:30:17] [W2 18:30:17] [W3 18:30:18]`

**Problem: "Can't open lstm.train" error**

```
❌ Symptom: All files fail with "all models failed" message
   Manual test shows: Error: Can't open lstm.train
```

- **Root Cause**: Config file path was relative instead of absolute
- **Solution**: Updated batch_lstmf_processor.sh to use full path:
  ```bash
  lstm_config="/mnt/c/tesseract/tessdata/configs/lstm.train"
  ```
- **Verification**: Manual test should work:
  ```bash
  tesseract --tessdata-dir /mnt/c/tesseract/tessdata/best \
    test.tif output -l fas --oem 1 --psm 13 \
    /mnt/c/tesseract/tessdata/configs/lstm.train
  ```

**Problem: Many failures (all models failed)**

- **Symptom**: High count of `✗ FAILED: ... (all models failed)` messages
- **Solution**:
  1. Check tessdata models exist: `ls /mnt/c/tesseract/tessdata/best/fas.traineddata`
  2. Verify file formats are valid (not corrupted TIF files)
  3. Check config file path is correct (see above)

**Problem: Missing GT/BOX files**

- **Symptom**: Pre-validation shows low number of complete sets
  - Example: "Found 1523 complete file sets" from 30,594 TIF files (only 5%)
- **Solution**:
  1. Verify source directory structure
  2. Regenerate missing GT/BOX files if needed
  3. Batch processing will only process complete sets

**Problem: Slow processing despite parallel workers**

- **Symptom**: Low file sets/min rate even with 22 workers
- **Solution**:
  1. Check CPU usage (should be 90-100% with 22 workers)
  2. Files may be complex/large, reduce batch size
  3. Check disk I/O (local SSD should be fast)
  4. Verify not hitting thermal throttling

### 5. Regenerate Only Corrupted Files

```powershell
# Parallel generation will skip valid files, regenerate corrupted ones
.\run_training.ps1 -Mode ImprovedGenerate -TrainingProfile Best -ParallelJobs 5 -OutputDirOverride "Z:\training_output_best"
```

## Tips

1. **Use Z: drive** for training data if C: drive is low on space
2. **Parallel jobs**: 3-5 workers optimal for most systems
3. **Best profile**: Recommended for production deployments
4. **Fast profile**: Good for testing and rapid iteration
5. **Resumability**: All generation modes support resuming from interruptions
6. **File validation**: Corrupted files are automatically detected and regenerated

## Current Status

✅ **Available Modes**: All 16 modes implemented and working
✅ **Parallel Processing**: Fully functional with 5-worker support
✅ **File Validation**: Automatic corruption detection and repair
✅ **Profile Support**: Best and Fast profiles configured
✅ **Z: Drive Support**: Full support for network/external storage
✅ **Resumability**: All operations can be safely interrupted and resumed
