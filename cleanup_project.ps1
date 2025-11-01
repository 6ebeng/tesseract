# Project Cleanup Script
# Moves obsolete files to archive/ and removes test/debug scripts

param(
    [switch]$DryRun = $false,
    [switch]$DeleteTests = $false
)

$ErrorActionPreference = 'Stop'

Write-Host "`n=====================================================================" -ForegroundColor Cyan
Write-Host "PROJECT CLEANUP SCRIPT" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`n[DRY RUN MODE] - No files will be moved or deleted`n" -ForegroundColor Yellow
}

# Create archive structure
$archiveDirs = @(
    "archive\phase1-5",
    "archive\batches",
    "archive\experiments",
    "archive\old_corpus",
    "archive\scripts"
)

foreach ($dir in $archiveDirs) {
    $fullPath = Join-Path $PSScriptRoot $dir
    if (-not (Test-Path $fullPath)) {
        Write-Host "Creating directory: $dir" -ForegroundColor Green
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        }
    }
}

# Function to move files
function Move-ToArchive {
    param(
        [string]$SourcePattern,
        [string]$DestinationFolder,
        [string]$Description
    )
    
    $files = Get-ChildItem -Path $PSScriptRoot -Filter $SourcePattern -File -ErrorAction SilentlyContinue
    if ($files) {
        Write-Host "`n$Description ($($files.Count) files):" -ForegroundColor Yellow
        foreach ($file in $files) {
            $destPath = Join-Path $PSScriptRoot $DestinationFolder
            Write-Host "  → $($file.Name)" -ForegroundColor Gray
            if (-not $DryRun) {
                Move-Item -Path $file.FullName -Destination $destPath -Force
            }
        }
    }
}

# Function to delete files
function Remove-Files {
    param(
        [string]$Path,
        [string]$Filter,
        [string]$Description
    )
    
    $files = Get-ChildItem -Path $Path -Filter $Filter -Recurse -File -ErrorAction SilentlyContinue
    if ($files) {
        Write-Host "`n$Description ($($files.Count) files):" -ForegroundColor Yellow
        foreach ($file in $files) {
            Write-Host "  ✗ $($file.FullName.Replace($PSScriptRoot, '.'))" -ForegroundColor Red
            if (-not $DryRun) {
                Remove-Item -Path $file.FullName -Force
            }
        }
    }
}

Write-Host "`n===== Phase 1: Archive Obsolete Documentation =====" -ForegroundColor Cyan

# Move Phase 1-5 documentation
Move-ToArchive "PHASE1_*.md" "archive\phase1-5" "Phase 1 docs"
Move-ToArchive "PHASE2_*.md" "archive\phase1-5" "Phase 2 docs"
Move-ToArchive "PHASE3_*.md" "archive\phase1-5" "Phase 3 docs"
Move-ToArchive "PHASE4_*.md" "archive\phase1-5" "Phase 4 docs"
Move-ToArchive "PHASE5_*.md" "archive\phase1-5" "Phase 5 docs"

# Move Phase 6 Batch 1-4 documentation
Move-ToArchive "PHASE6_BATCH1_*.md" "archive\batches" "Phase 6 Batch 1 docs"
Move-ToArchive "PHASE6_BATCH2_*.md" "archive\batches" "Phase 6 Batch 2 docs"
Move-ToArchive "PHASE6_BATCH3_*.md" "archive\batches" "Phase 6 Batch 3 docs"
Move-ToArchive "PHASE6_BATCH4_*.md" "archive\batches" "Phase 6 Batch 4 docs"

# Move Batch 2-3 exploration docs
Move-ToArchive "BATCH2_*.md" "archive\experiments" "Batch 2 exploration"
Move-ToArchive "BATCH3_*.md" "archive\experiments" "Batch 3 exploration"

# Move Option/Hybrid exploration docs
Move-ToArchive "OPTION*.md" "archive\experiments" "Option exploration"
Move-ToArchive "HYBRID*.md" "archive\experiments" "Hybrid exploration"

# Move superseded docs
$supersededDocs = @(
    "TRAINING_STATUS.md",
    "TRAINING_STATUS_NOW.md",
    "TRAINING_PROGRESS.md",
    "COMPLETE_GUIDE.md",
    "guideline.md",
    "QUICK_REFERENCE.md",
    "ENCODING_ISSUES_RESOLVED.md",
    "ZWNJ_PROBLEM_ANALYSIS.md",
    "IMPROVE_ACCURACY_NOW.md",
    "ROOT_CAUSE_SOLUTION.md"
)

Write-Host "`nSuperseded documentation:" -ForegroundColor Yellow
foreach ($doc in $supersededDocs) {
    $file = Join-Path $PSScriptRoot $doc
    if (Test-Path $file) {
        Write-Host "  → $doc" -ForegroundColor Gray
        if (-not $DryRun) {
            Move-Item -Path $file -Destination (Join-Path $PSScriptRoot "archive\experiments") -Force
        }
    }
}

Write-Host "`n===== Phase 2: Clean Up Scripts =====" -ForegroundColor Cyan

# Archive batch check scripts
$batchScripts = @(
    "work\corpus\check_batch2.py",
    "work\corpus\check_batch3.py",
    "work\corpus\create_batch4.py"
)

Write-Host "`nBatch verification scripts:" -ForegroundColor Yellow
foreach ($script in $batchScripts) {
    $file = Join-Path $PSScriptRoot $script
    if (Test-Path $file) {
        Write-Host "  → $(Split-Path $script -Leaf)" -ForegroundColor Gray
        if (-not $DryRun) {
            Move-Item -Path $file -Destination (Join-Path $PSScriptRoot "archive\scripts") -Force
        }
    }
}

# Delete test/debug scripts (if flag is set)
if ($DeleteTests) {
    Remove-Files -Path (Join-Path $PSScriptRoot "work") -Filter "test_*.py" -Description "Test scripts"
    Remove-Files -Path (Join-Path $PSScriptRoot "work") -Filter "debug_*.py" -Description "Debug scripts"
    
    # Old scrapers
    $oldScrapers = @(
        "work\tools\scrape_wikipedia_quality.py",
        "work\tools\scrape_from_urls.py"
    )
    
    Write-Host "`nOld scraper scripts:" -ForegroundColor Yellow
    foreach ($scraper in $oldScrapers) {
        $file = Join-Path $PSScriptRoot $scraper
        if (Test-Path $file) {
            Write-Host "  ✗ $(Split-Path $scraper -Leaf)" -ForegroundColor Red
            if (-not $DryRun) {
                Remove-Item -Path $file -Force
            }
        }
    }
}

Write-Host "`n===== Phase 3: Clean Up Corpus Files =====" -ForegroundColor Cyan

# Old corpus files to archive
$corpusDir = Join-Path $PSScriptRoot "work\corpus"
$oldCorpusFiles = @(
    "ckb.training_text.backup*",
    "ckb.training_text.phase*",
    "ckb.training_text.final.old",
    "ckb_phase3.txt",
    "ckb_phase4.training_text.backup",
    "ckb_phase5.training_text",
    "ckb_phase6_batch1.training_text",
    "ckb_phase6_batch2.training_text",
    "ckb_phase6_batch3.training_text",
    "kurdish_news_batch*.txt",
    "wikipedia_phase5*.txt",
    "ckb_*_coverage.txt",
    "ckb_*_enhanced*.txt",
    "ckb_*_expanded*.txt",
    "ckb_*_extra_sentences.txt",
    "ckb_*_formats_ner.txt",
    "ckb_historical.txt",
    "ckb_rejected_mixed.txt",
    "ckb_targeted_from_mgk.txt",
    "ckb_zwnj_boosted.txt",
    "ckb_zwnj_focused.training_text",
    "shaping_augment.txt",
    "zwnj_rich_words.txt"
)

foreach ($pattern in $oldCorpusFiles) {
    $files = Get-ChildItem -Path $corpusDir -Filter $pattern -File -ErrorAction SilentlyContinue
    if ($files) {
        Write-Host "`nArchiving corpus files matching '$pattern':" -ForegroundColor Yellow
        foreach ($file in $files) {
            Write-Host "  → $($file.Name)" -ForegroundColor Gray
            if (-not $DryRun) {
                Move-Item -Path $file.FullName -Destination (Join-Path $PSScriptRoot "archive\old_corpus") -Force
            }
        }
    }
}

# Debug template
$debugFile = Join-Path $PSScriptRoot "debug_template.txt"
if (Test-Path $debugFile) {
    Write-Host "`nDebug template:" -ForegroundColor Yellow
    Write-Host "  → debug_template.txt" -ForegroundColor Gray
    if (-not $DryRun) {
        Move-Item -Path $debugFile -Destination (Join-Path $PSScriptRoot "archive\experiments") -Force
    }
}

Write-Host "`n===== Cleanup Summary =====" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`n✅ DRY RUN COMPLETE - No files were actually moved" -ForegroundColor Green
    Write-Host "`nTo execute the cleanup, run:" -ForegroundColor Yellow
    Write-Host "  .\cleanup_project.ps1" -ForegroundColor White
    Write-Host "`nTo also delete test/debug scripts, run:" -ForegroundColor Yellow
    Write-Host "  .\cleanup_project.ps1 -DeleteTests" -ForegroundColor White
} else {
    Write-Host "`n✅ CLEANUP COMPLETE" -ForegroundColor Green
    Write-Host "`nFiles organized into archive/ directory" -ForegroundColor White
    
    if (-not $DeleteTests) {
        Write-Host "`nNote: Test/debug scripts were NOT deleted" -ForegroundColor Yellow
        Write-Host "To remove them, run: .\cleanup_project.ps1 -DeleteTests" -ForegroundColor White
    }
}

Write-Host "`n===== Next Steps =====" -ForegroundColor Cyan
Write-Host "1. Review archive/ directory contents" -ForegroundColor White
Write-Host "2. Update README.md with current status" -ForegroundColor White
Write-Host "3. Commit cleanup changes to git" -ForegroundColor White
Write-Host "4. Proceed with Batch 5 training" -ForegroundColor White
Write-Host "`n=====================================================================" -ForegroundColor Cyan
