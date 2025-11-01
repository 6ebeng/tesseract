#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Clean up temporary files, test scripts, and unnecessary documentation from the project.

.DESCRIPTION
    This script removes:
    1. Temporary and obsolete training files
    2. Test/debug scripts that are no longer needed
    3. Old documentation that has been archived
    4. Duplicate/superseded corpus files
    5. Temporary build artifacts

.PARAMETER DryRun
    If specified, shows what would be deleted without actually deleting.

.PARAMETER KeepTests
    If specified, keeps test scripts in work/ directory.

.EXAMPLE
    .\cleanup_temp_files.ps1 -DryRun
    Shows what would be deleted without actually deleting.

.EXAMPLE
    .\cleanup_temp_files.ps1
    Performs the cleanup.
#>

param(
    [switch]$DryRun,
    [switch]$KeepTests
)

$ErrorActionPreference = 'Stop'

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "TEMPORARY FILES CLEANUP" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN MODE] - No files will be deleted" -ForegroundColor Yellow
    Write-Host ""
}

$deletedCount = 0
$keptCount = 0

function Remove-ItemSafely {
    param(
        [string]$Path,
        [string]$Description
    )
    
    if (Test-Path $Path) {
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would delete: $Description" -ForegroundColor Yellow
            $script:keptCount++
        } else {
            Write-Host "  ✓ Deleting: $Description" -ForegroundColor Green
            Remove-Item -Path $Path -Recurse -Force -ErrorAction SilentlyContinue
            $script:deletedCount++
        }
        return $true
    }
    return $false
}

# ==============================================================================
# Phase 1: Remove Obsolete Documentation (Now in archive/)
# ==============================================================================

Write-Host "===== Phase 1: Obsolete Documentation =====" -ForegroundColor Cyan
Write-Host ""

$obsoleteDocs = @(
    # Phase 6 Batch docs (now in archive/batches/)
    "PHASE6_BATCH3_RESULTS.md",
    "PHASE6_BATCH3_SCRAPED_CORPUS.md",
    "PHASE6_BATCH4_FINAL_RESULTS.md",
    "PHASE6_BATCH4_QUICKSTART.md",
    "PHASE6_BATCH4_TRAINING_STATUS.md",
    
    # Work directory docs (cleanup summaries - no longer needed)
    "work\CLEANUP_OPINION_FILES.md",
    "work\CLEANUP_SUMMARY.md",
    "work\KURDISTAN24_FLARESOLVERR_STATUS.md",
    "work\OPINION_CATEGORIES_FINAL_SUMMARY.md",
    
    # Scraper integration guide (superseded by docs/SCRAPER_QUICK_START.md)
    "SCRAPER_INTEGRATION_GUIDE.md"
)

foreach ($doc in $obsoleteDocs) {
    $fullPath = Join-Path $PSScriptRoot $doc
    Remove-ItemSafely -Path $fullPath -Description $doc
}

# ==============================================================================
# Phase 2: Remove Test and Debug Scripts
# ==============================================================================

if (-not $KeepTests) {
    Write-Host ""
    Write-Host "===== Phase 2: Test and Debug Scripts =====" -ForegroundColor Cyan
    Write-Host ""

    $testScripts = @(
        # Old test scripts in work/
        "work\test_chrome_driver.py",
        "work\test_curl_verbose.sh",
        "work\test_env.sh",
        "work\test_flaresolverr_api.sh",
        "work\test_kurdistan24.py",
        "work\test_legacy_imports.py",
        "work\test_legacy_lvinpress.py",
        "work\test_lvinpress.py",
        "work\test_lvinpress_full.py",
        "work\test_lvinpress_page_source.py",
        "work\test_new_lvinpress_selector.py",
        "work\debug_lvinpress_selectors.py",
        
        # Analysis scripts that were one-time use
        "work\analyze_project_cleanup.py",
        "work\check_phase4_quality.py",
        
        # Batch check scripts (superseded)
        "work\corpus\check_batch2.py",
        "work\corpus\check_batch3.py",
        "work\corpus\create_batch4.py"
    )

    foreach ($script in $testScripts) {
        $fullPath = Join-Path $PSScriptRoot $script
        Remove-ItemSafely -Path $fullPath -Description $script
    }
}

# ==============================================================================
# Phase 3: Remove Temporary Training Files
# ==============================================================================

Write-Host ""
Write-Host "===== Phase 3: Temporary Training Files =====" -ForegroundColor Cyan
Write-Host ""

$tempTrainingFiles = @(
    # Old phase models (superseded by current ckb.traineddata)
    "work\ckb_phase4.lstm",
    "work\ckb_phase4.lstm-number-dawg",
    "work\ckb_phase4.lstm-punc-dawg",
    "work\ckb_phase4.lstm-recoder",
    "work\ckb_phase4.lstm-unicharset",
    "work\ckb_phase4.lstm-word-dawg",
    "work\ckb_phase4.version",
    "work\ckb_phase4_zwnj.lstm-unicharset",
    
    # Temp files
    "work\ckb_with_zwnj.traineddata.__tmp__",
    "work\ckb_with_zwnj.traineddata",
    
    # Old base models (superseded)
    "work\fas_check.lstm",
    "work\fas_check.lstm-number-dawg",
    "work\fas_check.lstm-punc-dawg",
    "work\fas_check.lstm-recoder",
    "work\fas_check.lstm-unicharset",
    "work\fas_check.lstm-word-dawg",
    "work\fas_check.version"
)

foreach ($file in $tempTrainingFiles) {
    $fullPath = Join-Path $PSScriptRoot $file
    Remove-ItemSafely -Path $fullPath -Description $file
}

# ==============================================================================
# Phase 4: Remove Old Corpus Files
# ==============================================================================

Write-Host ""
Write-Host "===== Phase 4: Old Corpus Files =====" -ForegroundColor Cyan
Write-Host ""

$oldCorpusFiles = @(
    # Large Wikipedia dump (no longer needed after extraction)
    "work\corpus\ckbwiki-latest-pages-articles.xml",
    "work\corpus\ckbwiki-latest-pages-articles.xml.bz2",
    
    # Old batch corpus files (archived)
    "work\corpus\ckb_high_zwnj.training_text",
    
    # Cleanup scripts (one-time use)
    "work\corpus\clean_all_corpus.py",
    "work\corpus\clean_corpus.sh"
)

foreach ($file in $oldCorpusFiles) {
    $fullPath = Join-Path $PSScriptRoot $file
    Remove-ItemSafely -Path $fullPath -Description $file
}

# ==============================================================================
# Phase 5: Remove Old Database Files
# ==============================================================================

Write-Host ""
Write-Host "===== Phase 5: Old Database Files =====" -ForegroundColor Cyan
Write-Host ""

# Keep the main dedup DB in root, but remove duplicates
$oldDatabases = @(
    "work\article_dedup.db"
)

foreach ($db in $oldDatabases) {
    $fullPath = Join-Path $PSScriptRoot $db
    if (Test-Path $fullPath) {
        # Check if main DB exists
        $mainDB = Join-Path $PSScriptRoot "article_dedup.db"
        if (Test-Path $mainDB) {
            Remove-ItemSafely -Path $fullPath -Description $db
        }
    }
}

# ==============================================================================
# Phase 6: Clean Empty Directories
# ==============================================================================

Write-Host ""
Write-Host "===== Phase 6: Empty Directories =====" -ForegroundColor Cyan
Write-Host ""

$dirsToCheck = @(
    "work\logs",
    "logs",
    "cache"
)

foreach ($dir in $dirsToCheck) {
    $fullPath = Join-Path $PSScriptRoot $dir
    if (Test-Path $fullPath) {
        $items = Get-ChildItem -Path $fullPath -Force
        if ($items.Count -eq 0) {
            if ($DryRun) {
                Write-Host "  [DRY RUN] Would delete empty directory: $dir" -ForegroundColor Yellow
            } else {
                Write-Host "  ✓ Removing empty directory: $dir" -ForegroundColor Green
                Remove-Item -Path $fullPath -Force
                $deletedCount++
            }
        } else {
            Write-Host "  ⊘ Keeping non-empty directory: $dir ($($items.Count) items)" -ForegroundColor Gray
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

if ($DryRun) {
    Write-Host "✅ DRY RUN COMPLETE - No files were actually deleted" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Files that would be deleted: $keptCount" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To execute the cleanup, run:" -ForegroundColor Cyan
    Write-Host "  .\cleanup_temp_files.ps1" -ForegroundColor White
} else {
    Write-Host "✅ CLEANUP COMPLETE" -ForegroundColor Green
    Write-Host ""
    Write-Host "Files deleted: $deletedCount" -ForegroundColor Green
}

if ($KeepTests) {
    Write-Host ""
    Write-Host "Note: Test scripts were kept (--KeepTests flag)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "===== Files Kept (Important) =====" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentation:" -ForegroundColor White
Write-Host "  ✓ README.md                         - Main project documentation" -ForegroundColor Gray
Write-Host "  ✓ UNICODE_CHARACTER_ANALYSIS.md     - ZWNJ/Tatweel analysis" -ForegroundColor Gray
Write-Host "  ✓ ZWNJ_TATWEEL_SUMMARY.md           - Executive summary" -ForegroundColor Gray
Write-Host "  ✓ PHASE6_COMPLETE.md                - Phase 6 final summary" -ForegroundColor Gray
Write-Host "  ✓ docs/                             - All documentation" -ForegroundColor Gray
Write-Host "  ✓ archive/                          - Historical records" -ForegroundColor Gray
Write-Host ""
Write-Host "Training Files:" -ForegroundColor White
Write-Host "  ✓ tessdata/best/ckb.traineddata     - Production model" -ForegroundColor Gray
Write-Host "  ✓ tessdata/fast/ckb.traineddata     - Fast model" -ForegroundColor Gray
Write-Host "  ✓ work/corpus/ckb_phase6_batch4.training_text  - Current corpus" -ForegroundColor Gray
Write-Host "  ✓ work/corpus/ckb_scraped_filtered.training_text - News corpus" -ForegroundColor Gray
Write-Host ""
Write-Host "Scripts:" -ForegroundColor White
Write-Host "  ✓ run_training.ps1                  - Training pipeline" -ForegroundColor Gray
Write-Host "  ✓ work/tools/                       - Scraper framework" -ForegroundColor Gray
Write-Host "  ✓ work/analyze_unicode_chars.py     - Unicode analysis tool" -ForegroundColor Gray
Write-Host "  ✓ work/verify_ckb_traineddata.py    - Model verification" -ForegroundColor Gray
Write-Host ""

Write-Host "=====================================================================" -ForegroundColor Cyan
