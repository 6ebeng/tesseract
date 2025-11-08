# Improved Training Data Generation with Multi-Scale + Augmentation
# This script generates better training data for improved accuracy

param(
    [switch]$DownloadFonts,    # Download additional fonts first
    [switch]$Generate,         # Generate improved training data
    [switch]$All               # Do both: download fonts + generate
)

$ErrorActionPreference = 'Stop'

Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  IMPROVED TRAINING DATA GENERATION" -ForegroundColor Cyan
Write-Host "  Multi-Scale + Augmentation for Better Accuracy" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Check if we're in work directory
$workDir = "c:\tesseract\work"
if (-not (Test-Path $workDir)) {
    Write-Host "`n❌ Error: Work directory not found at $workDir" -ForegroundColor Red
    exit 1
}

# Display current fonts
$fontCount = (Get-ChildItem "$workDir\fonts\*.ttf" -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "`nCurrent font count: $fontCount" -ForegroundColor Yellow

if ($fontCount -lt 10) {
    Write-Host "⚠️  Warning: Only $fontCount fonts available." -ForegroundColor Yellow
    Write-Host "   Recommended: 15+ fonts for best accuracy" -ForegroundColor Yellow
    $DownloadFonts = $true
}

# Download fonts if requested or needed
if ($DownloadFonts -or $All) {
    Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  STEP 1: Downloading Additional Fonts" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work && chmod +x download_kurdish_fonts.sh && ./download_kurdish_fonts.sh"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n⚠️  Font download had issues, but continuing with available fonts..." -ForegroundColor Yellow
    } else {
        Write-Host "`n✅ Font download complete" -ForegroundColor Green
    }
    
    $fontCount = (Get-ChildItem "$workDir\fonts\*.ttf" -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "`nUpdated font count: $fontCount" -ForegroundColor Green
}

# Generate improved training data if requested
if ($Generate -or $All -or (-not $DownloadFonts)) {
    Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  STEP 2: Generating Improved Training Data" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎨 Multi-Scale Parameters:" -ForegroundColor Yellow
    Write-Host "   • Font sizes: 16, 18, 20, 22 pt" -ForegroundColor White
    Write-Host "   • DPI: 200, 300, 400" -ForegroundColor White
    Write-Host "   • Exposures: -2, -1, 0, 1, 2" -ForegroundColor White
    Write-Host "   • Augmentation: 8 variants per image" -ForegroundColor White
    Write-Host ""
    Write-Host "⏱️  Expected time: 30-45 minutes for $fontCount fonts" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Starting generation..." -ForegroundColor Yellow
    
    # Clean old training output first
    if (Test-Path "$workDir\training_output\ground_truth") {
        Write-Host "Cleaning old training data..." -ForegroundColor Gray
        Remove-Item "$workDir\training_output\ground_truth\*" -Force -ErrorAction SilentlyContinue
    }
    
    # Run improved generation script
    wsl -d Ubuntu -- bash -c "cd /mnt/c/tesseract/work && chmod +x generate_ckb_training_data_improved.sh && ./generate_ckb_training_data_improved.sh"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n❌ Training data generation failed!" -ForegroundColor Red
        Write-Host "Check logs in: $workDir\training_output\logs" -ForegroundColor Yellow
        exit 1
    }
    
    # Verify output
    $tifCount = (Get-ChildItem "$workDir\training_output\ground_truth\*.tif" -ErrorAction SilentlyContinue | Measure-Object).Count
    $boxCount = (Get-ChildItem "$workDir\training_output\ground_truth\*.box" -ErrorAction SilentlyContinue | Measure-Object).Count
    
    Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  GENERATION COMPLETE" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ Generated .tif files: $tifCount" -ForegroundColor Green
    Write-Host "✅ Generated .box files: $boxCount" -ForegroundColor Green
    Write-Host ""
    
    if ($tifCount -gt 0 -and $boxCount -gt 0) {
        Write-Host "🎯 EXPECTED IMPROVEMENTS:" -ForegroundColor Yellow
        Write-Host "   • Multi-scale training: Better at various font sizes" -ForegroundColor White
        Write-Host "   • Multi-resolution: Handles different scan qualities" -ForegroundColor White
        Write-Host "   • Enhanced augmentation: More robust to real-world variations" -ForegroundColor White
        Write-Host "   • Expected accuracy gain: +1% to +3% on biographical text" -ForegroundColor White
        Write-Host ""
        Write-Host "🚀 NEXT STEP: Train the model" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "   Option 1 (Full training from scratch):" -ForegroundColor Yellow
        Write-Host "   cd c:\tesseract" -ForegroundColor White
        Write-Host "   .\run_training.ps1 -Mode GenerateTrain -LatinDigits" -ForegroundColor Green
        Write-Host ""
        Write-Host "   Option 2 (Quick test with existing corpus):" -ForegroundColor Yellow
        Write-Host "   wsl -d Ubuntu -- bash -c 'cd /mnt/c/tesseract/work && ./execute_ckb_training.sh'" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "❌ No training files generated! Check logs for errors." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
