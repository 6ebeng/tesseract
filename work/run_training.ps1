# PowerShell script to run Kurdish OCR training
# This script launches the training pipeline in WSL

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        KURDISH OCR TRAINING LAUNCHER                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if WSL Ubuntu is available by testing direct access
try {
    $testResult = wsl -d Ubuntu -- echo "test" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Ubuntu not accessible"
    }
}
catch {
    Write-Host "Error: Ubuntu is not available in WSL." -ForegroundColor Red
    Write-Host "Please ensure Ubuntu is installed and running in WSL." -ForegroundColor Yellow
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
Write-Host "5. CTC Encoding Diagnosis & Fix" -ForegroundColor Green
Write-Host "   - Analyzes 'Compute CTC targets failed' errors" -ForegroundColor Gray
Write-Host "   - Provides working solution using existing models" -ForegroundColor Gray
Write-Host "   - Tests your current Kurdish models" -ForegroundColor Gray
Write-Host ""
Write-Host "6. UTF-8 Enabled Kurdish Training" -ForegroundColor Cyan
Write-Host "   - Complete UTF-8 encoding support" -ForegroundColor Gray
Write-Host "   - Kurdish unicharset generation" -ForegroundColor Gray
Write-Host "   - Enhanced model with proper character encoding" -ForegroundColor Gray
Write-Host ""
Write-Host "7. Simple UTF-8 LSTM Training" -ForegroundColor Yellow
Write-Host "   - Creates proper LSTMF files with UTF-8" -ForegroundColor Gray
Write-Host "   - Validates UTF-8 training pipeline" -ForegroundColor Gray
Write-Host "   - Simplified training approach" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Enter your choice (1-7)"

switch ($choice) {
    "1" {
        Write-Host "`nStarting Full Training Pipeline..." -ForegroundColor Yellow
        Write-Host "This will generate training data and create a custom model." -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "=== PHASE 1: DATA PREPARATION ===" -ForegroundColor Cyan
        # Use our working training script
        if (Test-Path "final_ckb_train.sh") {
            Write-Host "Using optimized CKB training script..." -ForegroundColor Green
            wsl -d Ubuntu -- bash -c "chmod +x /mnt/c/tesseract/work/final_ckb_train.sh && /mnt/c/tesseract/work/final_ckb_train.sh"
        }
        elseif (Test-Path "quick_train_ckb.sh") {
            Write-Host "Using quick CKB training script..." -ForegroundColor Green  
            wsl -d Ubuntu -- bash -c "chmod +x /mnt/c/tesseract/work/quick_train_ckb.sh && /mnt/c/tesseract/work/quick_train_ckb.sh"
        }
        else {
            Write-Host "Training script not found! Please check the scripts directory." -ForegroundColor Red
        }
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
        wsl -d Ubuntu -- bash -c "chmod +x /mnt/c/tesseract/work/scripts/master_training.sh && /mnt/c/tesseract/work/scripts/master_training.sh"
    }
    "4" {
        Write-Host "`nStarting Fast & Robust WSL Training..." -ForegroundColor Yellow
        Write-Host "This uses local fonts + Sorani corpus with augmentation." -ForegroundColor Gray
        Write-Host ""
        
        # Run updated WSL script
        wsl -d Ubuntu -- bash -c "chmod +x /mnt/c/tesseract/work/scripts/wsl_train_ckb.sh && cd /mnt/c/tesseract/work/scripts && bash wsl_train_ckb.sh"
    }
    "5" {
        Write-Host "`nStarting CTC Encoding Diagnosis..." -ForegroundColor Green
        Write-Host "This will analyze the CTC error and provide the working solution." -ForegroundColor Gray
        Write-Host ""
        
        # Run CTC diagnosis script
        wsl -d Ubuntu -- bash -c "chmod +x /mnt/c/tesseract/work/scripts/ctc_diagnosis.sh && bash /mnt/c/tesseract/work/scripts/ctc_diagnosis.sh"
    }
    "6" {
        Write-Host "`nStarting UTF-8 Enabled Kurdish Training..." -ForegroundColor Cyan
        Write-Host "This ensures proper UTF-8 encoding for all Kurdish characters." -ForegroundColor Gray
        Write-Host ""
        
        # Run UTF-8 training script
        wsl -d Ubuntu -- bash -c "chmod +x /mnt/c/tesseract/work/scripts/utf8_ckb_training.sh && bash /mnt/c/tesseract/work/scripts/utf8_ckb_training.sh"
    }
    "7" {
        Write-Host "`nStarting Simple UTF-8 LSTM Training..." -ForegroundColor Yellow
        Write-Host "This creates proper LSTMF files and validates UTF-8 support." -ForegroundColor Gray
        Write-Host ""
        
        # Run simple UTF-8 LSTM script
        wsl -d Ubuntu -- bash -c "chmod +x /mnt/c/tesseract/work/scripts/simple_utf8_lstm.sh && bash /mnt/c/tesseract/work/scripts/simple_utf8_lstm.sh"
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
