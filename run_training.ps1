param(
    [switch]$NoClear,
    [ValidateSet('Clean','GenerateTrain','HybridBuild','HybridOCR','Train','SmokeTest')]
    [string]$Mode = '',
    [switch]$Deep = $false,
    [string]$ImagePath = ''
)

if (-not $NoClear) {
    try { Clear-Host } catch { }
}

# PowerShell interface to run Kurdish OCR tasks via WSL
# Minimal menu that calls WSL bash scripts in this workspace (script now lives at repo root)

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       KURDISH OCR - TRAINING/BUILD LAUNCHER         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

function Convert-ToWslPath([string]$winPath) {
    if ($winPath -match '^([A-Za-z]):\\') {
        $drive = $matches[1].ToLower()
        $rest = $winPath.Substring(2) -replace '\\\\', '/' -replace '\\', '/'
        return "/mnt/$drive$rest"
    }
    return ($winPath -replace '\\', '/')
}

# Resolve key paths based on this script's location
$projectRootWin = Split-Path -Path $PSCommandPath -Parent
$workDirWin = Join-Path $projectRootWin 'work'
$workDirWsl = Convert-ToWslPath $workDirWin

# Ensure Ubuntu WSL is available
try {
    $null = wsl -d Ubuntu -- echo "test" 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Ubuntu not accessible" }
}
catch {
    Write-Host "Error: Ubuntu is not available in WSL." -ForegroundColor Red
    Write-Host "Please ensure Ubuntu is installed and running in WSL." -ForegroundColor Yellow
    exit 1
}

function Convert-ToWslPath([string]$winPath) {
    if ($winPath -match '^([A-Za-z]):\\') {
        $drive = $matches[1].ToLower()
        $rest = $winPath.Substring(2) -replace '\\\\', '/' -replace '\\', '/'
        return "/mnt/$drive$rest"
    }
    return ($winPath -replace '\\', '/')
}

function Invoke-Cleanup([bool]$deep) {
    $deepFlag = if ($deep) { '1' } else { '0' }
    Write-Host "`nRunning cleanup (DEEP=$deepFlag)..." -ForegroundColor Yellow
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl' && DEEP=$deepFlag chmod +x cleanup_unnecessary_files.sh && DEEP=$deepFlag ./cleanup_unnecessary_files.sh"
}

function Invoke-GenerateTrain {
    Write-Host "\nGenerating training data..." -ForegroundColor Yellow
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl' && chmod +x generate_ckb_training_data.sh && ./generate_ckb_training_data.sh"; $code = $LASTEXITCODE
    if ($code -ne 0) { throw "Data generation failed (exit $code)." }
    $trainScriptWin = Join-Path $workDirWin 'execute_ckb_training.sh'
    $trainScriptWsl = Convert-ToWslPath $trainScriptWin
    if (-not (Test-Path $trainScriptWin)) { throw "Training script not found at $trainScriptWin" }
    Write-Host "\nStarting training to build ckb.traineddata..." -ForegroundColor Yellow
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl' && chmod +x '$trainScriptWsl' && '$trainScriptWsl'"; $trainCode = $LASTEXITCODE
    if ($trainCode -ne 0) { throw "Training failed (exit $trainCode)." }
}

function Get-GroundTruthDir([string]$baseWin) {
    $cands = @(
        'training_output/ground_truth','ground-truth','ground-truth-robust',
        'ground-truth-system','ground-truth-final','ground-truth-workaround','ground-truth-corpus'
    )
    foreach ($rel in $cands) {
        $p = Join-Path $baseWin $rel
        if (Test-Path $p) { return $p }
    }
    return $null
}

Write-Host "Select an option:" -ForegroundColor Blue
Write-Host "1. Cleanup workspace (remove tests/.md)" -ForegroundColor White
Write-Host "2. Generate training data (fonts + corpus) and Train" -ForegroundColor White
Write-Host "3. Train now (skip generation)" -ForegroundColor White
Write-Host "4. Smoke test trained ckb model" -ForegroundColor White
Write-Host "5. Verify ckb.traineddata covers Kurdish chars" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        $deep = Read-Host "Deep cleanup? This removes generated directories (y/N)"
        $deepFlag = if ($deep -match '^(y|yes)$') { '1' } else { '0' }
        Write-Host "`nRunning cleanup (DEEP=$deepFlag)..." -ForegroundColor Yellow
        # Pass DEEP flag into WSL
        wsl -d Ubuntu -- bash -lc "cd '$workDirWsl' && DEEP=$deepFlag chmod +x cleanup_unnecessary_files.sh && DEEP=$deepFlag ./cleanup_unnecessary_files.sh"
    }
    "2" {
        Write-Host "\nGenerating training data..." -ForegroundColor Yellow
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl' && chmod +x generate_ckb_training_data.sh && ./generate_ckb_training_data.sh"; $code = $LASTEXITCODE
        if ($code -ne 0) { Write-Host "Data generation failed (exit $code)." -ForegroundColor Red; break }
        # Ensure training script exists before attempting to run
        $trainScriptWin = Join-Path $workDirWin 'execute_ckb_training.sh'
        $trainScriptWsl = Convert-ToWslPath $trainScriptWin
        if (-not (Test-Path $trainScriptWin)) {
            Write-Host "Training script not found at $trainScriptWin" -ForegroundColor Red
            Write-Host "Please update your workspace or re-run after the script is created." -ForegroundColor Yellow
            break
        }
        Write-Host "\nStarting training to build ckb.traineddata..." -ForegroundColor Yellow
        wsl -d Ubuntu -- bash -lc "cd '$workDirWsl' && chmod +x '$trainScriptWsl' && '$trainScriptWsl'"; $trainCode = $LASTEXITCODE
        if ($trainCode -ne 0) { Write-Host "Training failed (exit $trainCode). See logs above." -ForegroundColor Red; break }

        # Optional smoke test right after training
        $doSmoke = Read-Host "Run a quick smoke test now? (y/N)"
        if ($doSmoke -match '^(y|yes)$') {
            # Find a ground-truth folder and test image automatically
            function Get-GroundTruthDir {
                param([string]$baseWin)
                $cands = @(
                    'training_output/ground_truth', 'ground-truth', 'ground-truth-robust',
                    'ground-truth-system', 'ground-truth-final', 'ground-truth-workaround', 'ground-truth-corpus'
                )
                foreach ($rel in $cands) {
                    $p = Join-Path $baseWin $rel
                    if (Test-Path $p) { return $p }
                }
                return $null
            }
            $gtDirWin = Get-GroundTruthDir -baseWin $workDirWin
            if ($gtDirWin) {
                $firstTif = Get-ChildItem -Path $gtDirWin -Filter *.tif -File | Select-Object -First 1
                if ($firstTif) {
                    $imgWsl = Convert-ToWslPath $firstTif.FullName
                    Write-Host "\n[Smoke] OCR: $($firstTif.Name) using ckb..." -ForegroundColor Yellow
                    wsl -d Ubuntu -- bash -lc "tesseract --tessdata-dir /mnt/c/tesseract/tessdata '$imgWsl' stdout -l ckb --psm 6 | head -n 8"
                }
                else {
                    Write-Host "No .tif files found under $gtDirWin" -ForegroundColor DarkYellow
                }
            }
            else {
                Write-Host "Ground-truth directory not found for smoke test." -ForegroundColor DarkYellow
            }
        }
    }
    "3" {
        # Train only (skip generation)
        $trainScriptWin = Join-Path $workDirWin 'execute_ckb_training.sh'
        $trainScriptWsl = Convert-ToWslPath $trainScriptWin
        if (-not (Test-Path $trainScriptWin)) {
            Write-Host "Training script not found at $trainScriptWin" -ForegroundColor Red
            break
        }
        Write-Host "\nStarting training to build ckb.traineddata..." -ForegroundColor Yellow
        wsl -d Ubuntu -- bash -lc "cd '$workDirWsl' && chmod +x '$trainScriptWsl' && '$trainScriptWsl'"; $trainCode = $LASTEXITCODE
        if ($trainCode -ne 0) { Write-Host "Training failed (exit $trainCode). See logs above." -ForegroundColor Red; break }
    }
    "4" {
        # Smoke test trained ckb model
        function Get-GroundTruthDir {
            param([string]$baseWin)
            $cands = @(
                'training_output/ground_truth', 'ground-truth', 'ground-truth-robust',
                'ground-truth-system', 'ground-truth-final', 'ground-truth-workaround', 'ground-truth-corpus'
            )
            foreach ($rel in $cands) {
                $p = Join-Path $baseWin $rel
                if (Test-Path $p) { return $p }
            }
            return $null
        }
        $gtDirWin = Get-GroundTruthDir -baseWin $workDirWin
        $defaultImg = $null
        if ($gtDirWin) {
            $firstTif = Get-ChildItem -Path $gtDirWin -Filter *.tif -File | Select-Object -First 1
            if ($firstTif) { $defaultImg = $firstTif.FullName }
        }
        $imagePath = Read-Host ("Enter image path for smoke test (Windows path)." + (if ($defaultImg) { " Default: $defaultImg" } else { "" }))
        if (-not $imagePath -and $defaultImg) { $imagePath = $defaultImg }
        if (-not (Test-Path $imagePath)) { Write-Host "File not found." -ForegroundColor Red; break }
        $imgWsl = Convert-ToWslPath $imagePath
        Write-Host "\nRunning smoke test with ckb model..." -ForegroundColor Yellow
        wsl -d Ubuntu -- bash -lc "tesseract --tessdata-dir /mnt/c/tesseract/tessdata '$imgWsl' stdout -l ckb --psm 6 | head -n 12"
    }
    "5" {
        # Verify ckb.traineddata unicharset coverage against Kurdish letters
        $traineddataDefault = Join-Path (Join-Path $projectRootWin 'tessdata') 'ckb.traineddata'
        if (-not (Test-Path $traineddataDefault)) {
            $traineddataDefault = Join-Path (Join-Path $workDirWin 'hybrid_build') 'ckb.traineddata'
        }
    $tdPrompt = "Enter path to ckb.traineddata (Windows path)." + $(if (Test-Path $traineddataDefault) { " Default: $traineddataDefault" } else { "" })
        $tdWin = Read-Host $tdPrompt
        if (-not $tdWin -and (Test-Path $traineddataDefault)) { $tdWin = $traineddataDefault }
        if (-not (Test-Path $tdWin)) { Write-Host "ckb.traineddata not found." -ForegroundColor Red; break }
        $tdWsl = Convert-ToWslPath $tdWin
        Write-Host "\nVerifying Kurdish unicharset coverage..." -ForegroundColor Yellow
        $scriptWsl = Convert-ToWslPath (Join-Path $workDirWin 'verify_ckb_traineddata.py')
        # Prefer Python3 in WSL and ensure combine_tessdata is accessible there
        wsl -d Ubuntu -- bash -lc "cd '$workDirWsl' && python3 '$scriptWsl' --traineddata '$tdWsl' --out output/verify_report.json"; $vcode = $LASTEXITCODE
        if ($vcode -eq 0) {
            Write-Host "\nVerification PASSED: all required characters are present." -ForegroundColor Green
        } elseif ($vcode -eq 2) {
            Write-Host "\nVerification FAILED: missing required characters. See work/output/verify_report.json" -ForegroundColor Red
        } else {
            Write-Host "\nVerification ERROR: environment or tool issue. Check output logs." -ForegroundColor Red
        }
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host "\nDone." -ForegroundColor Green
