#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Clean up training artifacts and temporary files to reclaim disk space.

.DESCRIPTION
    This script removes:
    1. Old training checkpoints (keeping only the final models)
    2. Temporary LSTMF files in training_output/tmp
    3. Ground truth files (already used for training)
    4. Old logs (keeping recent ones)
    
    This can free up several GB of disk space.

.PARAMETER DryRun
    If specified, shows what would be deleted without actually deleting.

.PARAMETER KeepCheckpoints
    If specified, keeps all checkpoint files (not recommended - uses ~8GB).

.EXAMPLE
    .\cleanup_training_artifacts.ps1 -DryRun
    Shows what would be deleted without actually deleting.

.EXAMPLE
    .\cleanup_training_artifacts.ps1
    Performs the cleanup.
#>

param(
    [switch]$DryRun,
    [switch]$KeepCheckpoints
)

$ErrorActionPreference = 'Stop'

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "TRAINING ARTIFACTS CLEANUP" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN MODE] - No files will be deleted" -ForegroundColor Yellow
    Write-Host ""
}

$deletedCount = 0
$freedSpace = 0

function Remove-ItemSafely {
    param(
        [string]$Path,
        [string]$Description
    )
    
    if (Test-Path $Path) {
        $size = (Get-Item $Path -ErrorAction SilentlyContinue).Length
        if ($size -eq $null) {
            # Directory - calculate size
            $size = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | 
                     Measure-Object -Property Length -Sum).Sum
        }
        
        $sizeMB = [math]::Round($size / 1MB, 2)
        
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would delete: $Description (${sizeMB} MB)" -ForegroundColor Yellow
        } else {
            Write-Host "  ✓ Deleting: $Description (${sizeMB} MB)" -ForegroundColor Green
            Remove-Item -Path $Path -Recurse -Force -ErrorAction SilentlyContinue
            $script:deletedCount++
        }
        $script:freedSpace += $size
        return $true
    }
    return $false
}

# ==============================================================================
# Phase 1: Remove Old Training Checkpoints
# ==============================================================================

if (-not $KeepCheckpoints) {
    Write-Host "===== Phase 1: Old Training Checkpoints =====" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Note: Keeping final models, removing intermediate checkpoints" -ForegroundColor Gray
    Write-Host ""

    $checkpointDir = Join-Path $PSScriptRoot "work\training_output\model\checkpoint_backup_phase4"
    if (Test-Path $checkpointDir) {
        $checkpoints = Get-ChildItem -Path $checkpointDir -File
        $totalSize = ($checkpoints | Measure-Object -Property Length -Sum).Sum
        $totalSizeMB = [math]::Round($totalSize / 1MB, 2)
        
        Write-Host "  Found $($checkpoints.Count) checkpoint files (${totalSizeMB} MB)" -ForegroundColor White
        
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would delete entire checkpoint directory" -ForegroundColor Yellow
            $script:freedSpace += $totalSize
        } else {
            Write-Host "  ✓ Deleting checkpoint directory..." -ForegroundColor Green
            Remove-Item -Path $checkpointDir -Recurse -Force -ErrorAction SilentlyContinue
            $script:deletedCount += $checkpoints.Count
            $script:freedSpace += $totalSize
        }
    } else {
        Write-Host "  ⊘ No checkpoint directory found" -ForegroundColor Gray
    }
}

# ==============================================================================
# Phase 2: Remove Temporary LSTMF Files
# ==============================================================================

Write-Host ""
Write-Host "===== Phase 2: Temporary LSTMF Files =====" -ForegroundColor Cyan
Write-Host ""

$tmpDir = Join-Path $PSScriptRoot "work\training_output\tmp"
if (Test-Path $tmpDir) {
    $lstmfFiles = Get-ChildItem -Path $tmpDir -Filter "*.lstmf" -Recurse
    
    if ($lstmfFiles.Count -gt 0) {
        $totalSize = ($lstmfFiles | Measure-Object -Property Length -Sum).Sum
        $totalSizeMB = [math]::Round($totalSize / 1MB, 2)
        
        Write-Host "  Found $($lstmfFiles.Count) LSTMF files (${totalSizeMB} MB)" -ForegroundColor White
        
        foreach ($file in $lstmfFiles) {
            $sizeMB = [math]::Round($file.Length / 1MB, 2)
            if ($DryRun) {
                $script:freedSpace += $file.Length
            } else {
                Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
                $script:freedSpace += $file.Length
            }
        }
        
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would delete $($lstmfFiles.Count) LSTMF files" -ForegroundColor Yellow
        } else {
            Write-Host "  ✓ Deleted $($lstmfFiles.Count) LSTMF files (${totalSizeMB} MB)" -ForegroundColor Green
            $script:deletedCount += $lstmfFiles.Count
        }
    } else {
        Write-Host "  ⊘ No LSTMF files found" -ForegroundColor Gray
    }
}

# ==============================================================================
# Phase 3: Remove Ground Truth Files (Already Used)
# ==============================================================================

Write-Host ""
Write-Host "===== Phase 3: Ground Truth Files =====" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: These were used to generate training data and can be regenerated" -ForegroundColor Gray
Write-Host ""

$gtDir = Join-Path $PSScriptRoot "work\training_output\ground_truth"
if (Test-Path $gtDir) {
    $gtFiles = Get-ChildItem -Path $gtDir -File -Recurse
    $totalSize = ($gtFiles | Measure-Object -Property Length -Sum).Sum
    $totalSizeMB = [math]::Round($totalSize / 1MB, 2)
    
    Write-Host "  Found $($gtFiles.Count) ground truth files (${totalSizeMB} MB)" -ForegroundColor White
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would delete ground truth directory" -ForegroundColor Yellow
        $script:freedSpace += $totalSize
    } else {
        Write-Host "  ✓ Deleting ground truth directory..." -ForegroundColor Green
        Remove-Item -Path $gtDir -Recurse -Force -ErrorAction SilentlyContinue
        $script:deletedCount += $gtFiles.Count
        $script:freedSpace += $totalSize
    }
} else {
    Write-Host "  ⊘ No ground truth directory found" -ForegroundColor Gray
}

# ==============================================================================
# Phase 4: Remove Temporary Normalized Corpus Files
# ==============================================================================

Write-Host ""
Write-Host "===== Phase 4: Temporary Normalized Files =====" -ForegroundColor Cyan
Write-Host ""

$tempFiles = @(
    "work\training_output\tmp\*.norm",
    "work\training_output\tmp\*.nfc",
    "work\training_output\tmp\ara.lstm",
    "work\training_output\tmp\eng.lstm",
    "work\training_output\tmp\fas.lstm",
    "work\training_output\tmp\list.all",
    "work\training_output\tmp\list.eval",
    "work\training_output\tmp\list.train"
)

foreach ($pattern in $tempFiles) {
    $fullPath = Join-Path $PSScriptRoot $pattern
    $files = Get-ChildItem -Path $fullPath -ErrorAction SilentlyContinue
    
    foreach ($file in $files) {
        $sizeMB = [math]::Round($file.Length / 1MB, 2)
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would delete: $($file.Name) (${sizeMB} MB)" -ForegroundColor Yellow
            $script:freedSpace += $file.Length
        } else {
            Write-Host "  ✓ Deleting: $($file.Name) (${sizeMB} MB)" -ForegroundColor Green
            Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
            $script:deletedCount++
            $script:freedSpace += $file.Length
        }
    }
}

# ==============================================================================
# Phase 5: Remove Old Model Files from work/ root
# ==============================================================================

Write-Host ""
Write-Host "===== Phase 5: Old Model Files in work/ =====" -ForegroundColor Cyan
Write-Host ""

$oldModels = @(
    "work\ckb.lstm",
    "work\ckb.lstm-number-dawg",
    "work\ckb.lstm-punc-dawg",
    "work\ckb.lstm-recoder",
    "work\ckb.lstm-unicharset",
    "work\ckb.lstm-word-dawg",
    "work\ckb.version",
    "work\fas_base.lstm",
    "work\fas_base.lstm-number-dawg",
    "work\fas_base.lstm-punc-dawg",
    "work\fas_base.lstm-recoder",
    "work\fas_base.lstm-unicharset",
    "work\fas_base.lstm-word-dawg",
    "work\fas_base.version"
)

foreach ($model in $oldModels) {
    $fullPath = Join-Path $PSScriptRoot $model
    if (Test-Path $fullPath) {
        $file = Get-Item $fullPath
        $sizeMB = [math]::Round($file.Length / 1MB, 2)
        
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would delete: $($file.Name) (${sizeMB} MB)" -ForegroundColor Yellow
            $script:freedSpace += $file.Length
        } else {
            Write-Host "  ✓ Deleting: $($file.Name) (${sizeMB} MB)" -ForegroundColor Green
            Remove-Item -Path $fullPath -Force -ErrorAction SilentlyContinue
            $script:deletedCount++
            $script:freedSpace += $file.Length
        }
    }
}

# ==============================================================================
# Summary
# ==============================================================================

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "CLEANUP SUMMARY" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$freedSpaceMB = [math]::Round($freedSpace / 1MB, 2)
$freedSpaceGB = [math]::Round($freedSpace / 1GB, 2)

if ($DryRun) {
    Write-Host "✅ DRY RUN COMPLETE - No files were actually deleted" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Space that would be freed: ${freedSpaceMB} MB (${freedSpaceGB} GB)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To execute the cleanup, run:" -ForegroundColor Cyan
    Write-Host "  .\cleanup_training_artifacts.ps1" -ForegroundColor White
} else {
    Write-Host "✅ CLEANUP COMPLETE" -ForegroundColor Green
    Write-Host ""
    Write-Host "Files deleted: $deletedCount" -ForegroundColor Green
    Write-Host "Space freed: ${freedSpaceMB} MB (${freedSpaceGB} GB)" -ForegroundColor Green
}

if ($KeepCheckpoints) {
    Write-Host ""
    Write-Host "Note: Checkpoints were kept (--KeepCheckpoints flag)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "===== Files Kept (Important) =====" -ForegroundColor Cyan
Write-Host ""
Write-Host "Production Models:" -ForegroundColor White
Write-Host "  ✓ tessdata/best/ckb.traineddata     - Production model (best quality)" -ForegroundColor Gray
Write-Host "  ✓ tessdata/fast/ckb.traineddata     - Fast model (faster inference)" -ForegroundColor Gray
Write-Host ""
Write-Host "Training Output (Final Models):" -ForegroundColor White
Write-Host "  ✓ work/training_output/model/ckb.best.traineddata" -ForegroundColor Gray
Write-Host "  ✓ work/training_output/model/ckb.fast.traineddata" -ForegroundColor Gray
Write-Host "  ✓ work/training_output/model/ckb_from_*.traineddata" -ForegroundColor Gray
Write-Host ""
Write-Host "Training Logs:" -ForegroundColor White
Write-Host "  ✓ work/training_output/logs/*.log   - Training logs" -ForegroundColor Gray
Write-Host "  ✓ work/training_output/model/metrics.csv - Performance metrics" -ForegroundColor Gray
Write-Host ""
Write-Host "Corpus Data:" -ForegroundColor White
Write-Host "  ✓ work/corpus/*.training_text        - Training corpus files" -ForegroundColor Gray
Write-Host ""
Write-Host "Analysis Tools:" -ForegroundColor White
Write-Host "  ✓ work/analyze_unicode_chars.py     - Unicode analysis tool" -ForegroundColor Gray
Write-Host "  ✓ work/analyze_mgk_unicode.py       - Ground truth analysis" -ForegroundColor Gray
Write-Host "  ✓ work/analyze_mgk_special_chars.py - Character analysis" -ForegroundColor Gray
Write-Host ""

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 TIP: To regenerate training data if needed:" -ForegroundColor Cyan
Write-Host "   .\run_training.ps1 -Mode GenerateTrain" -ForegroundColor White
Write-Host ""
