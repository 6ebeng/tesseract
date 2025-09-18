# PowerShell script to run Kurdish OCR training
# This script launches the training pipeline in WSL

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        KURDISH OCR TRAINING LAUNCHER                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if WSL is available
$wslCheck = wsl -l 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: WSL is not installed or not available." -ForegroundColor Red
    Write-Host "Please install WSL and Ubuntu first." -ForegroundColor Yellow
    exit 1
}

# Check if Ubuntu is installed (handle spacing in WSL output)
$ubuntuFound = $false
foreach ($line in $wslCheck) {
    if ($line -match "Ubuntu") {
        $ubuntuFound = $true
        break
    }
}

if (-not $ubuntuFound) {
    Write-Host "Error: Ubuntu is not installed in WSL." -ForegroundColor Red
    Write-Host "Please install Ubuntu in WSL first." -ForegroundColor Yellow
    exit 1
}

# Start Ubuntu if it's stopped
Write-Host "Checking Ubuntu status..." -ForegroundColor Gray
$wslStatus = wsl -l -v | Select-String "Ubuntu"
if ($wslStatus -match "Stopped") {
    Write-Host "Starting Ubuntu..." -ForegroundColor Yellow
    wsl -d Ubuntu -- echo "Ubuntu started"
}

Write-Host "Select training option:" -ForegroundColor Blue
Write-Host "1. Full Training Pipeline (Recommended)" -ForegroundColor White
Write-Host "   - Prepares data from fonts and corpus" -ForegroundColor Gray
Write-Host "   - Runs complete training" -ForegroundColor Gray
Write-Host "   - Creates ckb_custom.traineddata" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Data Preparation Only" -ForegroundColor White
Write-Host "   - Only generates training data" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Use Existing Master Training Script" -ForegroundColor White
Write-Host "   - Opens interactive training menu" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Fast & Robust WSL Training" -ForegroundColor White
Write-Host "   - Uses fonts folder + Sorani corpus" -ForegroundColor Gray
Write-Host "   - Adds shear/augmentation for accuracy" -ForegroundColor Gray
Write-Host "   - Trains moderate iterations for speed" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`nStarting Full Training Pipeline..." -ForegroundColor Yellow
        Write-Host "This will generate training data and create a custom model." -ForegroundColor Gray
        Write-Host ""
        
        # Make scripts executable and run full pipeline
        wsl -d Ubuntu -- bash -c "chmod +x /mnt/c/tesseract/work/scripts/*.sh && cd /mnt/c/tesseract/work/scripts && bash full_training_pipeline.sh"
    }
    "2" {
        Write-Host "`nStarting Data Preparation..." -ForegroundColor Yellow
        Write-Host "This will only generate training data from fonts and corpus." -ForegroundColor Gray
        Write-Host ""
        
        # Make scripts executable and run data preparation
        wsl -d Ubuntu -- bash -c "chmod +x /mnt/c/tesseract/work/scripts/*.sh && cd /mnt/c/tesseract/work/scripts && bash prepare_training_data.sh"
    }
    "3" {
        Write-Host "`nStarting Master Training Script..." -ForegroundColor Yellow
        Write-Host "This will open the interactive training menu." -ForegroundColor Gray
        Write-Host ""
        
        # Run master training script
        wsl -d Ubuntu -- bash -c "chmod +x /mnt/c/tesseract/work/scripts/*.sh && cd /mnt/c/tesseract/work/scripts && bash master_training.sh"
    }
    "4" {
        Write-Host "`nStarting Fast & Robust WSL Training..." -ForegroundColor Yellow
        Write-Host "This uses local fonts + Sorani corpus with augmentation." -ForegroundColor Gray
        Write-Host ""
        
        # Run updated WSL script
        wsl -d Ubuntu -- bash -c "chmod +x /mnt/c/tesseract/work/scripts/wsl_train_ckb.sh && cd /mnt/c/tesseract/work/scripts && bash wsl_train_ckb.sh"
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Training process completed." -ForegroundColor Green
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
