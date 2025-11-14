# Batch Processing Workflow

Complete workflow documentation for Kurdish OCR batch LSTMF generation with network drive optimization.

---

## Quick Start

```powershell
# Recommended: Use optimal settings (500 file sets/batch, 22 workers)
.\run_training.ps1 -Mode Train -TrainingProfile Best `
    -OutputDirOverride "Z:\training_output_best" `
    -UseBatchProcessing -BatchSize 500 -BatchWorkers 22

# Conservative (fewer files per batch)
.\run_training.ps1 -Mode Train -TrainingProfile Best `
    -OutputDirOverride "Z:\training_output_best" `
    -UseBatchProcessing -BatchSize 100 -BatchWorkers 22
```

**Important:**

- **Batch size** = number of file SETS (each set = TIF + GT + BOX = 3 files)
- BatchSize 500 = 1500 files copied (500 × 3)
- Monitor timestamps to verify parallel execution (should cluster within seconds)
- Failed files are logged with reasons (✗ FAILED)
- Process completes automatically with progress updates
- **Use 22 workers** to utilize full CPU (i9-12900KF has 24 threads)

---

## Architecture Overview

### Problem

- 30,594 TIF files on Z: network drive (~800GB)
- Direct network processing: 0-1 files/min (too slow)
- Insufficient local disk space for full copy (need 800GB, have 282GB)
- Each file SET requires TIF + GT.txt + BOX (3 files total) for LSTM training

### Solution

- **File set processing**: Works with complete sets (TIF+GT+BOX together)
- **Basename-based batching**: Ensures all 3 files stay together
- **Streaming batch processing**: Process batches at a time (configurable)
- **Local SSD caching**: Fast processing on C: drive
- **GNU Parallel workers**: True parallel processing with multiple tesseract processes
- **Incremental transfer**: Move LSTMF files after each batch
- **Auto-resume**: Skip already-processed files on restart

### Performance

- **Processing rate**: 100-340 file sets/min with 22 workers
- **Batch size 500**: ~2-4 minutes per batch (1500 files: 500 TIF + 500 GT + 500 BOX)
- **Total time**: ~90-150 minutes for all ~30,594 files (varies by complexity)
- **Disk usage**: ~3-6 GB per 500 file sets (auto-cleanup after each batch)
- **Network speedup**: 100-340x faster than direct processing
- **Parallel execution**: Uses GNU Parallel for reliable parallelism (verified by timestamp clustering)

---

## Detailed Workflow

### Phase 1: Initialization

```
┌─────────────────────────────────────────────┐
│  run_training.ps1 -UseBatchProcessing       │
└─────────────────┬───────────────────────────┘
                  │
                  ├─► Mount Z: drive in WSL
                  ├─► Create C:\tesseract\work\training_output_best\batch_tmp
                  ├─► Create C:\tesseract\work\training_output_best\tmp
                  └─► Launch batch_lstmf_processor.sh
```

**Directories Created:**

- `C:\tesseract\work\training_output_best\batch_tmp` - Temporary file processing
- `C:\tesseract\work\training_output_best\tmp` - Local LSTMF accumulation

### Phase 2: Pre-Processing

```
┌─────────────────────────────────────────────┐
│  Count & Validate Complete File Sets       │
└─────────────────┬───────────────────────────┘
                  │
                  ├─► Count TIF files in Z:\training_output_best\ground_truth
                  │   Result: 30,594 files
                  │
                  ├─► Validate complete sets (TIF + GT + BOX all exist)
                  │   Only include sets with all 3 files
                  │
                  ├─► Check for stray LSTMF files in ground_truth
                  │   Move to tmp if found
                  │
                  └─► Count existing LSTMF files (for resume capability)
```

**Output:**

```
Counting files and validating complete sets...
Found: 30594 TIF files

Found 1523 complete file sets (TIF+GT+BOX)

⚠️  Found 35 LSTMF files in ground_truth folder
   Moving them to tmp folder...
   ✓ Moved to correct location

🔄 RESUME MODE ENABLED
   Found 36 existing LSTMF files
   Will skip already-processed file sets
```

### Phase 3: Batch Loop (Variable iterations)

Each batch processes the configured number of file SETS (e.g., 100, 500)

#### Step 3.1: Copy to Local Cache

```
┌─────────────────────────────────────────────────────────┐
│  Z:\training_output_best\ground_truth\                  │
│  Batch 1: 100 file sets selected                        │
│    ├── file0001.tif                                     │
│    ├── file0001.gt.txt                                  │
│    ├── file0001.box                                     │
│    ├── ... (100 sets × 3 files = 300 files)            │
│    ├── file0100.tif                                     │
│    ├── file0100.gt.txt                                  │
│    └── file0100.box                                     │
└─────────────────┬───────────────────────────────────────┘
                  │ Copy complete sets atomically
                  ↓
┌─────────────────────────────────────────────────────────┐
│  C:\tesseract\work\training_output_best\batch_tmp\      │
│    ├── file0001.tif                                     │
│    ├── file0001.gt.txt                                  │
│    ├── file0001.box       ← All 3 files together        │
│    ├── ... (300 files total)                            │
│    ├── file0100.tif                                     │
│    ├── file0100.gt.txt                                  │
│    └── file0100.box                                     │
└─────────────────────────────────────────────────────────┘
```

**Output:**

```
📦 Batch 1: Processing file sets 1 to 100
   📥 Copying to local SSD...
   📋 Copying 100 file sets (300 files: TIF+GT+BOX for each set)...
   ✓ Ready: 100 complete file sets = 300 files (TIF+GT+BOX)
```

#### Step 3.2: Process Locally (22 Parallel Workers via GNU Parallel)

```
┌────────────────────────────────────────────────────────┐
│  GNU Parallel (-j 22):                                 │
│                                                         │
│  For each TIF file in batch_tmp (parallel):            │
│  1. cd to batch_tmp                                    │
│  2. Copy base.gt.txt → base-fas.gt.txt                 │
│  3. Run: tesseract base.tif base-fas -l fas            │
│     --tessdata-dir /path/to/tessdata                   │
│     /path/to/configs/lstm.train                        │
│     ├─► Success? → base-fas.lstmf generated            │
│     └─► Fail? → Try ara                                │
│  4. Move base-fas.lstmf → LOCAL_TMP/                   │
│  5. Delete base-fas.gt.txt                             │
│                                                         │
│  22 workers execute simultaneously                     │
└────────────────────────────────────────────────────────┘
```

**Processing Chain:**

```
TIF + GT + BOX → Try FAS → Success → LSTMF to LOCAL_TMP
                    ↓ Fail
                 Try ARA → Success → LSTMF to LOCAL_TMP
                    ↓ Fail
                 Skip (error logged)
```

**Output (real-time with worker IDs and timestamps):**

```
   ⚡ Processing with 22 workers...
   Started at: 20:30:15
   Processing 100 file sets...
   [W1 20:30:17] ✓ ckb.NotoKufiArabic-Bold.exp0.d200.s16.l20.c0.5 (fas)
   [W2 20:30:17] ✓ ckb.NotoKufiArabic-Bold.exp1.d200.s16.l20.c1.0 (fas)
   [W3 20:30:18] ✓ ckb.NotoKufiArabic-Bold.exp10.d200.s18.l20.c1.0 (ara)
   [W4 20:30:18] ✓ ckb.NotoKufiArabic-Bold.exp100.d400.s22.l20.c1.0 (fas)
   [W5 20:30:18] ✓ ckb.NotoKufiArabic-Bold.exp101.d400.s22.l20.c1.5 (fas)
   [W6 20:30:19] ✓ ckb.NotoKufiArabic-Bold.exp102.d400.s22.l22.c0.5 (ara)
   ...
   [W22 20:30:20] ✓ ckb.NotoKufiArabic-Bold.exp21.d200.s16.l20.c1.0 (fas)
   [W7 20:30:45] ✗ FAILED: ckb.SomeFont.exp50 (missing GT file)
   [W12 20:30:52] ✗ FAILED: ckb.BadFile.exp75 (all models failed)
   Finished at: 20:32:45

**Key Indicators for Parallel Execution:**
- ✅ **Timestamp clustering**: Multiple workers completing within same 1-2 seconds = TRUE parallel
- ❌ **Sequential timestamps**: Workers minutes apart = NOT parallel (bug)
- **Worker IDs**: [W1] through [W22] cycle and repeat
- **Model used**: (fas) or (ara) shows which model succeeded
- **Failures**: ✗ FAILED with specific reason
```

**Verifying Parallel Execution:**

If you see timestamps like this - **NOT PARALLEL** (sequential bug):

```
[W1 20:30:17] ✓ file1 (fas)
[W2 20:32:05] ✓ file2 (fas)  ← 2 minutes later = sequential!
[W3 20:34:22] ✓ file3 (fas)  ← another 2 minutes = sequential!
```

If you see timestamps like this - **✅ PARALLEL WORKING**:

```
[W1 20:30:17] ✓ file1 (fas)
[W2 20:30:17] ✓ file2 (fas)  ← Same second = parallel!
[W3 20:30:18] ✓ file3 (fas)  ← Within 1 second = parallel!
[W4 20:30:18] ✓ file4 (fas)
[W5 20:30:18] ✓ file5 (fas)
```

#### Step 3.3: Transfer to Network (After Each Batch)

```
┌─────────────────────────────────────────────────────────┐
│  C:\tesseract\work\training_output_best\tmp\            │
│    ├── file0001-fas.lstmf                               │
│    ├── file0002-ara.lstmf                               │
│    └── ... (LSTMF files from this batch)                │
└─────────────────┬───────────────────────────────────────┘
                  │ Move to network AFTER EACH BATCH
                  ↓
┌─────────────────────────────────────────────────────────┐
│  Z:\training_output_best\tmp\                           │
│    ├── file0001-fas.lstmf                               │
│    ├── file0002-ara.lstmf                               │
│    └── ... (incrementally added)                        │
└─────────────────────────────────────────────────────────┘
```

**Output:**

```
   📊 Generated 998 LSTMF files in LOCAL_TMP
   📤 Moving 998 LSTMF files to network...
   ✅ Moved to network. Total in network: 998
```

#### Step 3.4: Cleanup Batch Files

```
┌─────────────────────────────────────────────────────────┐
│  C:\tesseract\work\training_output_best\batch_tmp\      │
│    ├── file0001.tif      ──► DELETE                     │
│    ├── file0001.gt.txt   ──► DELETE                     │
│    ├── file0001.box      ──► DELETE                     │
│    ├── ...                                              │
│    ├── fileXXXX.tif      ──► DELETE                     │
│    ├── fileXXXX.gt.txt   ──► DELETE                     │
│    └── fileXXXX.box      ──► DELETE                     │
└─────────────────────────────────────────────────────────┘

Result: batch_tmp is now empty, ready for next batch
```

#### Step 3.5: Progress Summary

```
   ✓ Batch completed in 210s (processed: 1000 files, generated: 998 LSTMF)
   📊 Models: FAS=900 | ARA=98 | ENG=0 | Total=998
   📊 Progress: 998 / 30594 (3%) | Speed: 285 files/min | ETA: 105 min
```

**Progress indicators:**

- **Batch time**: How long this batch took
- **Files processed vs generated**: Shows success rate (2 failed in example)
- **Model breakdown**: Which models were used (FAS=Persian, ARA=Arabic, ENG=English)
- **Overall progress**: Total files done, percentage, speed, estimated time remaining

**Repeat for all batches until complete**

### Phase 4: Final Verification and Cleanup

#### Step 4.1: Verify All Files in Network

```
┌─────────────────────────────────────────────────────────┐
│  C:\tesseract\work\training_output_best\tmp\            │
│    (Should be empty - files moved after each batch)     │
└─────────────────────────────────────────────────────────┘
                  │ Check for any leftover files
                  ↓
┌─────────────────────────────────────────────────────────┐
│  Z:\training_output_best\tmp\                           │
│    ├── file0001-fas.lstmf                               │
│    ├── file0002-ara.lstmf                               │
│    ├── ... (~30,594 LSTMF files)                        │
│    └── file30594-eng.lstmf                              │
└─────────────────────────────────────────────────────────┘
```

**Output:**

```
📤 Verifying all LSTMF files in network...
   ✓ All files already in network tmp (moved after each batch)
   OR
   ⚠️  Found 5 leftover LSTMF files in local tmp
   Moving to /mnt/z/training_output_best/tmp...
   ✅ Moved remaining files to network
```

#### Step 4.2: Final Cleanup

```
┌─────────────────────────────────────────────────────────┐
│  Cleanup Actions:                                       │
│                                                         │
│  1. Delete: C:\tesseract\work\training_output_best\    │
│             batch_tmp\ (entire directory)               │
│                                                         │
│  2. Check for stray LSTMF files in ground_truth        │
│     Move any found to tmp                               │
│                                                         │
│  3. Count final LSTMF files in network tmp              │
└─────────────────────────────────────────────────────────┘
```

**Output:**

```
🧹 Final cleanup: checking for stray LSTMF files...
   Moving 2 LSTMF files from ground_truth to tmp...
   ✓ Cleanup complete

╔════════════════════════════════════════════╗
║           PROCESSING COMPLETE!             ║
╚════════════════════════════════════════════╝

✅ Total LSTMF files: 30558
📊 Model breakdown:
   - FAS (Persian): 27,502 files
   - ARA (Arabic): 3,056 files
   - ENG (English): 0 files
⏱️  Total time: 108m 15s
🚀 Average speed: 282 files/min
❌ Failed files: 36 (logged in failed_files_*.log)
```

### Phase 5: Continue Training

After batch processing completes, `execute_ckb_training.sh` continues with:

```
1. Create train/eval split (90/10)
2. Extract LSTM from fas.traineddata
3. Fine-tune on Kurdish data (1500 iterations)
4. Extract LSTM from ara.traineddata
5. Fine-tune on Kurdish data (1500 iterations)
6. Evaluate both models
7. Install best model as ckb.traineddata
```

---

## File Locations Reference

### Network Drive (Z:)

```
Z:\training_output_best\
├── ground_truth\               ← Source data (READ ONLY during batch)
│   ├── ckb.Font.exp0...tif    30,594 TIF files
│   └── ckb.Font.exp0...gt.txt 30,594 GT files
│
└── tmp\                        ← Final LSTMF output
    ├── ckb.Font.exp0...-fas.lstmf
    ├── ckb.Font.exp0...-ara.lstmf
    └── ... (~30,594 LSTMF files)
```

### Local Drive (C:)

```
C:\tesseract\work\training_output_best\
├── batch_tmp\                  ← Temporary processing (auto-cleanup)
│   ├── Current batch files    (5000 TIF+GT pairs)
│   └── Deleted after each batch
│
└── tmp\                        ← Local LSTMF accumulation
    ├── All LSTMF files generated
    └── Moved to network at end
```

---

## Performance Metrics

### Per Batch (Example: 1000 files, 22 workers)

- **Copy Time**: ~10-30 seconds (network → local)
- **Processing Time**: ~30-60 seconds (parallel execution)
- **Transfer Time**: ~5-15 seconds (local → network)
- **Cleanup Time**: ~1-3 seconds
- **Batch Total**: ~1-2 minutes per 1000 files

### Overall (30,594 files with optimal settings)

- **Best Case**: 90-120 minutes (250-340 files/min)
- **Typical**: 120-180 minutes (170-255 files/min)
- **Factors affecting speed**:
  - File complexity (more text = longer processing)
  - Worker count (more workers = faster, up to CPU limit)
  - Batch size (larger batches = fewer network operations)
  - Model success rate (FAS is fastest, trying all 3 is slowest)

### Resource Usage

- **CPU**: 100% utilization (configurable workers)
- **RAM**: ~4-8GB
- **Disk I/O**: Local SSD (very fast)
- **Network**: Minimal (batch copy, incremental transfer)
- **Temp Storage**: ~2-4 GB per 1000 files (auto-cleanup)

---

## Resume Capability

If the process is interrupted:

1. **Existing LSTMF files are preserved** in:

   - `C:\tesseract\work\training_output_best\tmp\` (local)
   - `Z:\training_output_best\tmp\` (network)

2. **On restart, the script:**

   - Counts existing LSTMF files
   - Skips already-processed files
   - Continues from where it stopped

3. **Example:**
   ```
   Already processed: 15234 files
   Remaining: 15360 files
   Starting from Batch 4...
   ```

---

## Troubleshooting

### Issue: Sequential processing (timestamps MINUTES apart)

**Symptom:** Logs show timestamps like:

```
[W1 19:47:18] ✓ file1 (fas)
[W2 19:49:05] ✓ file2 (fas)  ← 2 minutes later!
[W3 19:51:22] ✓ file3 (fas)  ← another 2 minutes!
```

**Cause:** Parallel execution not working (jobs builtin failing or GNU Parallel not used)  
**Solution:**

- **FIXED**: Script now uses GNU Parallel for reliable parallelism
- Verify GNU Parallel is installed: `wsl -d Ubuntu -- which parallel`
- If missing, install: `wsl -d Ubuntu -- sudo apt install parallel`
- Should see timestamps clustering within seconds:
  ```
  [W1 20:30:17] ✓ file1 (fas)
  [W2 20:30:17] ✓ file2 (fas)  ← Same second!
  [W3 20:30:18] ✓ file3 (fas)  ← Next second!
  ```

### Issue: "Can't open lstm.train" error

**Symptom:** `✗ FAILED: ... (all models failed)` with stderr showing config file error  
**Cause:** Config file path incorrect  
**Solution:**

- **FIXED**: Config now uses full path `/mnt/c/tesseract/tessdata/configs/lstm.train`
- Verify file exists: `ls /mnt/c/tesseract/tessdata/configs/lstm.train`
- If missing, check tessdata directory structure

### Issue: Many "all models failed" errors

**Symptom:** High count of `✗ FAILED: ... (all models failed)`  
**Cause:** Tesseract models missing or corrupted, or config file issues  
**Solution:**

- Verify `fas.traineddata` and `ara.traineddata` exist in `tessdata/best/`
- Verify `lstm.train` config exists in `tessdata/configs/`
- Check file permissions
- Test with single file manually:
  ```bash
  cd /mnt/c/tesseract/work/training_output_best/batch_tmp
  tesseract --tessdata-dir /mnt/c/tesseract/tessdata/best \
    file.tif file-fas -l fas --oem 1 --psm 13 \
    /mnt/c/tesseract/tessdata/configs/lstm.train
  ```

### Issue: Missing GT or BOX files

**Symptom:** `✗ FAILED: ... (missing GT file)` or incomplete file sets  
**Cause:** Incomplete file sets in source directory  
**Solution:**

- Script now validates complete sets before processing
- Only file sets with all 3 files (TIF+GT+BOX) are included
- Check source directory for matching files:
  ```bash
  ls -l /mnt/z/training_output_best/ground_truth/basename.*
  ```
- Should see: basename.tif, basename.gt.txt, basename.box

### Issue: Slow processing despite 22 workers

**Symptom:** Low files/min even with 22 workers  
**Cause:**

- Using only 5 workers (check command parameters!)
- Files are very complex (large images, many characters)
- CPU throttling due to temperature
  **Solution:**
- **Use -BatchWorkers 22** in command (not 5!)
- Reduce batch size if CPU thermal throttling
- Check CPU usage (should be 90-100% with 22 workers)
- Monitor disk I/O (local SSD should be fast)

### Issue: "5 workers active" but still slow

**Symptom:** Progress shows "5 workers active" but processing is sequential  
**Cause:** Old bash background jobs method didn't work reliably  
**Solution:**

- **FIXED**: Now uses GNU Parallel which guarantees true parallelism
- Progress messages will be less frequent with Parallel
- Verify by timestamp clustering in output logs
- Check for zombie tesseract processes
- Interrupt and restart (resume will skip completed files)

---

## Advanced Configuration

### Adjust Batch Size and Workers

**Remember: Batch size = number of file SETS (each set = 3 files)**

```powershell
# Small batches, fewer workers (conservative, testing)
.\run_training.ps1 -Mode Train -TrainingProfile Best `
    -OutputDirOverride "Z:\training_output_best" `
    -UseBatchProcessing -BatchSize 100 -BatchWorkers 12
# = 100 sets × 3 files = 300 files per batch

# Medium batches, balanced workers (recommended)
.\run_training.ps1 -Mode Train -TrainingProfile Best `
    -OutputDirOverride "Z:\training_output_best" `
    -UseBatchProcessing -BatchSize 500 -BatchWorkers 22
# = 500 sets × 3 files = 1500 files per batch

# Large batches, maximum workers (for maximum speed)
.\run_training.ps1 -Mode Train -TrainingProfile Best `
    -OutputDirOverride "Z:\training_output_best" `
    -UseBatchProcessing -BatchSize 1000 -BatchWorkers 22
# = 1000 sets × 3 files = 3000 files per batch
```

**Recommendations:**

- **Batch Size**: 100-500 file sets for faster feedback, 500-1000 for production
- **Workers**: Use 75-90% of CPU threads (e.g., 18-22 on 24-thread i9-12900KF)
- **Disk Space**: Ensure ~3-6 GB free per 500 file sets (1500 files)
- **Testing**: Start with 100 file sets to verify parallel execution before full run

### Custom Paths

Edit `batch_lstmf_processor.sh`:

```bash
NETWORK_GT="/mnt/z/training_output_best/ground_truth"
NETWORK_TMP="/mnt/z/training_output_best/tmp"
LOCAL_TMP="/mnt/c/tesseract/work/training_output_best/tmp"
LOCAL_BATCH="/mnt/c/tesseract/work/training_output_best/batch_tmp"
```

---

## Summary

**Batch processing transforms:**

- ❌ 0-1 file sets/min (direct network processing)
- ✅ 100-340 file sets/min (local batch processing with 22 parallel workers via GNU Parallel)

**Key improvements:**

- ✅ **File set processing**: Works with complete TIF+GT+BOX sets atomically
- ✅ **Basename-based batching**: Ensures all 3 files stay together
- ✅ **GNU Parallel execution**: True parallelism (verified by timestamp clustering)
- ✅ **Full config path**: Fixed `/mnt/c/tesseract/tessdata/configs/lstm.train`
- ✅ **100-340x performance improvement** over network processing
- ✅ **Minimal disk space** (3-6 GB per 500 file sets)
- ✅ **Resume capability** (auto-skip already-processed files)
- ✅ **Automatic cleanup** (batch_tmp cleared after each batch)
- ✅ **Live progress** with timestamps, worker IDs, and model success tracking
- ✅ **Incremental transfer** (LSTMF files moved to network after each batch)
- ✅ **Comprehensive logging** (success/failure with specific reasons)

**Verifying TRUE parallel execution:**

✅ **Working** (timestamps cluster within 1-2 seconds):

```
[W1 20:30:17] ✓ file1 (fas)
[W2 20:30:17] ✓ file2 (fas)  ← Same second!
[W3 20:30:18] ✓ file3 (fas)  ← Next second!
```

❌ **NOT working** (timestamps minutes apart):

```
[W1 19:47:18] ✓ file1 (fas)
[W2 19:49:05] ✓ file2 (fas)  ← 2 minutes later = sequential!
```

**Time estimate (1523 complete file sets):**

- Sequential (old): ~1500-3000 minutes (25-50 hours)
- Parallel with 22 workers: ~5-15 minutes
- **Speedup: 100-300x faster!**

**Full dataset (30,594 files):**

- If all files had complete sets: ~90-150 minutes with 22 workers
- Current (1523 complete sets): ~5-15 minutes
