# Batch Processing Guide for Network Drives

## Problem

Processing 30,594 TIF files directly from Z: network drive is extremely slow (0-1 files/min) due to network latency.

## Solution

Use batch processing: copy small batches to local SSD, process fast, move results back.

## Quick Start

### Option 1: Use the batch processor script (RECOMMENDED)

```powershell
# Run this command from PowerShell:
wsl -d Ubuntu -- bash -c "chmod +x /mnt/c/tesseract/work/batch_lstmf_processor.sh && /mnt/c/tesseract/work/batch_lstmf_processor.sh"
```

### Option 2: Use run_training.ps1 with batch parameters

```powershell
.\run_training.ps1 -Mode Train -TrainingProfile Best -OutputDirOverride "Z:\training_output_best" -UseBatchProcessing -BatchSize 5000
```

## How It Works

1. **Copy** 5,000 TIF + GT files to `C:\tesseract\work\batch_processing` (~10-15 GB)
2. **Process** locally with 22 parallel workers (200-300 files/min on SSD!)
3. **Move** LSTMF files back to Z:\training_output_best\tmp
4. **Delete** local TIF/GT files to free space
5. **Repeat** for next batch until all 30,594 files processed

## Performance

- **Batch processing time**: 6-9 minutes per 5,000 files
- **Total batches**: 7 (30,594 ÷ 5,000)
- **Total time**: 42-63 minutes for all files
- **Disk space**: 10-20 GB max (only one batch at a time)

## Customization

Change batch size (trade-off between speed and disk space):

```powershell
# Smaller batches (less disk space, more overhead)
.\run_training.ps1 -Mode Train -TrainingProfile Best -OutputDirOverride "Z:\training_output_best" -UseBatchProcessing -BatchSize 2500

# Larger batches (faster, more disk space)
.\run_training.ps1 -Mode Train -TrainingProfile Best -OutputDirOverride "Z:\training_output_best" -UseBatchProcessing -BatchSize 10000
```

## Monitoring Progress

The script shows real-time progress:

```
📦 Batch 1: files 1-5000
  ✓ Batch done in 428s (generated: 4987, moved: 4987)
  📊 Progress: 5000/30594 (16%) | Speed: 175/min | ETA: 24m
```

## Troubleshooting

**If batch processing doesn't activate:**
Use the standalone script instead:

```bash
wsl -d Ubuntu -- bash /mnt/c/tesseract/work/batch_lstmf_processor.sh
```

**If you run out of disk space:**
Reduce batch size to 2000-3000 files

**If Z: drive not mounted:**
The script auto-mounts it, but you can manually mount:

```bash
wsl -d Ubuntu -- sudo mount -t drvfs 'Z:' /mnt/z -o metadata,uid=1000,gid=1000
```
