param(
    [switch]$NoClear,
    [ValidateSet('Clean', 'Generate', 'GenerateTrain', 'Train', 'SmokeTest')]
    [string]$Mode = '',
    [switch]$Deep = $false,
    [string]$ImagePath = '',
    # Training tunables
    [int]$MaxIters,
    [int]$DebugInterval,
    [int]$OEM,
    [int]$PSM,
    [string]$TrainingExtraArgs,
    # Data generation overrides
    [string]$CorpusFileOverride,
    [string]$FontsDirOverride,
    [string]$OutputDirOverride,
    [int]$FontSize,
    [int]$DPI,
    [int]$Margin,
    [int]$Leading
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

# Escape a string for safe single-quoted bash usage
function Escape-ShellSingleQuotes([string]$s) {
    if (-not $s) { return '' }
    # Replace single quote with: '"'"' (close, dbl-quote, single, dbl-quote, open)
    return ($s -replace "'", '''"''"''')
}

# Build env string for training
function Get-TrainEnvPrefix() {
    $parts = @()
    if ($MaxIters) { $parts += "MAX_ITERS='${MaxIters}'" }
    if ($DebugInterval) { $parts += "DEBUG_INTERVAL='${DebugInterval}'" }
    # Only set OEM/PSM if valid values are explicitly provided
    if ($OEM -in 1, 2, 3) { $parts += "OEM='${OEM}'" }
    if ($PSM -ge 3 -and $PSM -le 13) { $parts += "PSM='${PSM}'" }
    # Ensure lstm.train is discoverable in WSL. Allow Windows env override, else default to repo's tessdata/configs.
    try {
        if ($env:LSTM_TRAIN_CONFIG) {
            $parts += "LSTM_TRAIN_CONFIG='$(Escape-ShellSingleQuotes (Convert-ToWslPath $env:LSTM_TRAIN_CONFIG))'"
        }
        else {
            $repoCfgWin = Join-Path (Join-Path $projectRootWin 'tessdata') 'configs\lstm.train'
            if (Test-Path $repoCfgWin) {
                $parts += "LSTM_TRAIN_CONFIG='$(Escape-ShellSingleQuotes (Convert-ToWslPath $repoCfgWin))'"
            }
        }
    }
    catch { }
    if ($TrainingExtraArgs) {
        $escaped = Escape-ShellSingleQuotes $TrainingExtraArgs
        $parts += "TRAINING_EXTRA_ARGS='${escaped}'"
    }
    if ($parts.Count -gt 0) { return ($parts -join ' ') + ' ' } else { return '' }
}

# Build env string for generation
function Get-GenEnvPrefix() {
    $parts = @()
    if ($CorpusFileOverride) { $parts += "CORPUS_FILE_OVERRIDE='$(Escape-ShellSingleQuotes (Convert-ToWslPath $CorpusFileOverride))'" }
    if ($FontsDirOverride) { $parts += "FONTS_DIR_OVERRIDE='$(Escape-ShellSingleQuotes (Convert-ToWslPath $FontsDirOverride))'" }
    if ($OutputDirOverride) { $parts += "OUTPUT_DIR_OVERRIDE='$(Escape-ShellSingleQuotes (Convert-ToWslPath $OutputDirOverride))'" }
    if ($FontSize) { $parts += "FONT_SIZE='${FontSize}'" }
    if ($DPI) { $parts += "DPI='${DPI}'" }
    if ($Margin) { $parts += "MARGIN='${Margin}'" }
    if ($Leading) { $parts += "LEADING='${Leading}'" }
    if ($parts.Count -gt 0) { return ($parts -join ' ') + ' ' } else { return '' }
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

# (moved non-interactive Mode handler below function definitions)


function Invoke-Cleanup([bool]$deep) {
    $deepFlag = if ($deep) { '1' } else { '0' }
    Write-Host "`nRunning cleanup (DEEP=$deepFlag)..." -ForegroundColor Yellow
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; sed -i 's/\r$//' cleanup_unnecessary_files.sh 2>/dev/null || true; chmod +x cleanup_unnecessary_files.sh; DEEP=$deepFlag bash ./cleanup_unnecessary_files.sh"
}

function Invoke-GenerateTrain {
    Write-Host "`nGenerating training data..." -ForegroundColor Yellow
    # Normalize line endings (CRLF->LF) to avoid $'\r' errors in WSL
    $genEnv = Get-GenEnvPrefix
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; sed -i 's/\r$//' generate_ckb_training_data.sh 2>/dev/null || true; sed -i 's/\r$//' execute_ckb_training.sh 2>/dev/null || true"
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; chmod +x generate_ckb_training_data.sh; $($genEnv)bash generate_ckb_training_data.sh"; $code = $LASTEXITCODE
    if ($code -ne 0) {
        # Fallback: check from Windows if ground-truth files exist
        $gtDirWin = Join-Path $workDirWin 'training_output\ground_truth'
        $tifCount = 0; $boxCount = 0
        if (Test-Path $gtDirWin) {
            $tifCount = (Get-ChildItem -Path $gtDirWin -Filter *.tif -File -ErrorAction SilentlyContinue | Measure-Object).Count
            $boxCount = (Get-ChildItem -Path $gtDirWin -Filter *.box -File -ErrorAction SilentlyContinue | Measure-Object).Count
        }
        if ($tifCount -gt 0 -and $boxCount -gt 0) {
            Write-Host "Generation exited with code $code, but found $tifCount TIF and $boxCount BOX files. Continuing..." -ForegroundColor Yellow
        }
        else {
            throw "Data generation failed (exit $code) and no ground-truth was found."
        }
    }
    # Proceed to training (unattended pipeline)
    Invoke-Train
}

# Generate only (no training)
function Invoke-GenerateOnly {
    Write-Host "`nGenerating training data (only)..." -ForegroundColor Yellow
    $genEnv = Get-GenEnvPrefix
    # Preflight (Windows side)
    $genScriptWin = Join-Path $workDirWin 'generate_ckb_training_data.sh'
    if (-not (Test-Path $genScriptWin)) { throw "Missing script: $genScriptWin" }
    $fontsDirWin = Join-Path $workDirWin 'fonts'
    if (-not (Test-Path $fontsDirWin)) { Write-Host "Warning: fonts directory not found at $fontsDirWin" -ForegroundColor DarkYellow }
    $corpusFileWin = Join-Path (Join-Path $workDirWin 'corpus') 'ckb.training_text'
    if (-not (Test-Path $corpusFileWin)) { Write-Host "Warning: corpus file not found at $corpusFileWin" -ForegroundColor DarkYellow }
    # Preflight (WSL tools)
    wsl -d Ubuntu -- bash -lc "command -v text2image >/dev/null 2>&1"; $t2i = $LASTEXITCODE
    if ($t2i -ne 0) {
        Write-Host "Error: text2image not found in WSL PATH. Install tesseract-ocr-dev." -ForegroundColor Red
        Write-Host "Tip (WSL): sudo apt-get update; sudo apt-get install -y tesseract-ocr-dev" -ForegroundColor DarkYellow
        throw "Missing dependency: text2image"
    }
    # Normalize line endings (CRLF->LF) to avoid $'\r' errors in WSL
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; sed -i 's/\r$//' generate_ckb_training_data.sh 2>/dev/null || true"
    # Run generation; keep output visible, but capture exit code
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; chmod +x generate_ckb_training_data.sh; $($genEnv)bash generate_ckb_training_data.sh"; $code = $LASTEXITCODE
    if ($code -ne 0) {
        # Fallback: check from Windows if ground-truth files exist
        $gtDirWin = Join-Path $workDirWin 'training_output\ground_truth'
        $tifCount = 0; $boxCount = 0
        if (Test-Path $gtDirWin) {
            $tifCount = (Get-ChildItem -Path $gtDirWin -Filter *.tif -File -ErrorAction SilentlyContinue | Measure-Object).Count
            $boxCount = (Get-ChildItem -Path $gtDirWin -Filter *.box -File -ErrorAction SilentlyContinue | Measure-Object).Count
        }
        if ($tifCount -gt 0 -and $boxCount -gt 0) {
            Write-Host "Generation exited with code $code, but found $tifCount TIF and $boxCount BOX files. Treating as success..." -ForegroundColor Yellow
        }
        else {
            throw "Data generation failed (exit $code) and no ground-truth was found."
        }
    }
    Write-Host "`nGeneration completed successfully (no training executed)." -ForegroundColor Green
}

# Train only helper
function Invoke-Train {
    $trainScriptWin = Join-Path $workDirWin 'execute_ckb_training.sh'
    $trainScriptWsl = Convert-ToWslPath $trainScriptWin
    if (-not (Test-Path $trainScriptWin)) { throw "Training script not found at $trainScriptWin" }
    Write-Host "`nStarting training to build ckb.traineddata..." -ForegroundColor Yellow
    # Normalize line endings and run training script with env
    $trainEnv = Get-TrainEnvPrefix
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; sed -i 's/\r$//' '$trainScriptWsl' 2>/dev/null || true; chmod +x '$trainScriptWsl'; $($trainEnv)bash '$trainScriptWsl'"; $trainCode = $LASTEXITCODE
    if ($trainCode -ne 0) { throw "Training failed (exit $trainCode)." }
    Write-Host "`nTraining complete." -ForegroundColor Green
}

function Get-GroundTruthDir([string]$baseWin) {
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

# If Mode is provided, run non-interactively (placed after function definitions)
if ($Mode) {
    switch ($Mode) {
        'Clean' {
            Invoke-Cleanup -deep:$Deep
            Write-Host "`nDone." -ForegroundColor Green
            exit 0
        }
        'Generate' {
            try {
                Invoke-GenerateOnly
                exit 0
            }
            catch {
                Write-Host $_ -ForegroundColor Red
                exit 1
            }
        }
        'GenerateTrain' {
            try {
                # Unattended pipeline: generate then train
                Invoke-GenerateTrain
                Write-Host "`nGeneration + training completed successfully." -ForegroundColor Green
                exit 0
            }
            catch {
                Write-Host $_ -ForegroundColor Red
                exit 1
            }
        }
        'Train' {
            try {
                Invoke-Train
            }
            catch {
                Write-Host $_ -ForegroundColor Red
                exit $LASTEXITCODE
            }
            exit 0
        }
        'SmokeTest' {
            $gtDirWin = Get-GroundTruthDir -baseWin $workDirWin
            if (-not $gtDirWin) { Write-Host "Ground-truth directory not found for smoke test." -ForegroundColor DarkYellow; exit 2 }
            $firstTif = Get-ChildItem -Path $gtDirWin -Filter *.tif -File | Select-Object -First 1
            if (-not $firstTif) { Write-Host "No .tif files found under $gtDirWin" -ForegroundColor DarkYellow; exit 2 }
            $imgWsl = Convert-ToWslPath $firstTif.FullName
            # Choose tessdata dir with ckb.traineddata
            $tdWinCandidates = @(
                (Join-Path $projectRootWin 'tessdata'),
                (Join-Path $projectRootWin 'tessdata_best')
            )
            $tessdataWin = 'C:\tesseract\tessdata'
            foreach ($td in $tdWinCandidates) {
                $ckb = Join-Path $td 'ckb.traineddata'
                if (Test-Path $ckb) { $tessdataWin = $td; break }
            }
            if (-not (Test-Path (Join-Path $tessdataWin 'ckb.traineddata'))) {
                Write-Host "ckb.traineddata not found in $tessdataWin. Run option 2 (Generate+Train) first or place the model there." -ForegroundColor Yellow
                exit 2
            }
            $tessdataWsl = Convert-ToWslPath $tessdataWin
            wsl -d Ubuntu -- bash -lc "echo 'Using tessdata dir: $tessdataWsl'; tesseract --psm 6 --tessdata-dir '$tessdataWsl' -l ckb '$imgWsl' stdout 2>&1 | head -n 15"; exit $LASTEXITCODE
        }
        default {
            Write-Host "Unknown Mode: $Mode" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "Select an option:" -ForegroundColor Blue
Write-Host "1. Cleanup workspace (remove tests/.md)" -ForegroundColor White
Write-Host "2. Generate training data (then optionally Train)" -ForegroundColor White
Write-Host "3. Train now (skip generation)" -ForegroundColor White
Write-Host "4. Smoke test trained ckb model" -ForegroundColor White
Write-Host "5. Verify ckb.traineddata covers Kurdish chars" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        # Use a separate variable name to avoid clashing with script param [switch]$Deep (variables are case-insensitive)
        $deepInput = Read-Host "Deep cleanup? This removes generated directories (y/N)"
        $deepBool = if ($deepInput -match '^(y|yes)$') { $true } else { $false }
        # Reuse the cleanup helper which handles the WSL invocation
        Invoke-Cleanup -deep:$deepBool
    }
    "2" {
        # Generate, then ask user whether to start training
        try {
            Invoke-GenerateOnly
            $start = Read-Host "Start training now? (y/N)"
            if ($start -match '^(y|yes)$') {
                Invoke-Train
            }
            else {
                Write-Host "Training skipped by user." -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host $_ -ForegroundColor Red
        }
    }
    "3" {
        # Train only (skip generation)
        try {
            Invoke-Train
        }
        catch {
            Write-Host "Training failed. See logs above." -ForegroundColor Red
        }
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
        $smokePrompt = "Enter image path for smoke test (Windows path)." + $(if ($defaultImg) { " Default: $defaultImg" } else { "" })
        $imagePath = Read-Host $smokePrompt
        if (-not $imagePath -and $defaultImg) { $imagePath = $defaultImg }
        if (-not (Test-Path $imagePath)) { Write-Host "File not found." -ForegroundColor Red; break }
        $imgWsl = Convert-ToWslPath $imagePath
        # Pick a tessdata dir with ckb.traineddata if available
        $tdWinCandidates = @(
            (Join-Path $projectRootWin 'tessdata'),
            (Join-Path $projectRootWin 'tessdata_best')
        )
        $tessdataWin = 'C:\tesseract\tessdata'
        foreach ($td in $tdWinCandidates) {
            $ckb = Join-Path $td 'ckb.traineddata'
            if (Test-Path $ckb) { $tessdataWin = $td; break }
        }
        if (-not (Test-Path (Join-Path $tessdataWin 'ckb.traineddata'))) {
            Write-Host "ckb.traineddata not found in $tessdataWin. Run option 2 (Generate+Train) first or place the model there." -ForegroundColor Yellow
            break
        }
        $tessdataWsl = Convert-ToWslPath $tessdataWin
        Write-Host "`nRunning smoke test with ckb model..." -ForegroundColor Yellow
        wsl -d Ubuntu -- bash -lc "echo 'Using tessdata dir: $tessdataWsl'; tesseract --tessdata-dir '$tessdataWsl' -l ckb --psm 6 '$imgWsl' stdout 2>&1 | head -n 15"
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
        Write-Host "`nVerifying Kurdish unicharset coverage..." -ForegroundColor Yellow
        $scriptWsl = Convert-ToWslPath (Join-Path $workDirWin 'verify_ckb_traineddata.py')
        # Prefer Python3 in WSL and ensure combine_tessdata is accessible there
        wsl -d Ubuntu -- bash -lc "cd '$workDirWsl' && python3 '$scriptWsl' --traineddata '$tdWsl' --out output/verify_report.json"; $vcode = $LASTEXITCODE
        if ($vcode -eq 0) {
            Write-Host "`nVerification PASSED: all required characters are present." -ForegroundColor Green
        }
        elseif ($vcode -eq 2) {
            Write-Host "`nVerification FAILED: missing required characters. See work/output/verify_report.json" -ForegroundColor Red
        }
        else {
            Write-Host "`nVerification ERROR: environment or tool issue. Check output logs." -ForegroundColor Red
        }
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nDone." -ForegroundColor Green
