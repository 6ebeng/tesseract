param(
    [switch]$NoClear,
    [ValidateSet('Clean', 'Generate', 'GenerateTrain', 'Train', 'SmokeTest', 'SmokeTestBest', 'SmokeTestFast', 'Bootstrap', 'BuildCorpus', 'ExpandCorpus', 'Eval', 'All')]
    [string]$Mode = '',
    [switch]$Deep = $false,
    [string]$ImagePath = '',
    # Training tunables
    [int]$MaxIters,
    [int]$DebugInterval,
    [int]$OEM,
    [int]$PSM,
    [string]$TrainingExtraArgs,
    [switch]$ForceMinimal,
    [switch]$LatinDigits,
    [string]$PuncsExtra,
    [switch]$TrainUseRealEval,
    [string]$Exposures,
    # Data generation overrides
    [string]$CorpusFileOverride,
    [string]$FontsDirOverride,
    [string]$OutputDirOverride,
    [int]$FontSize,
    [string]$FontSizes,
    [int]$DPI,
    [string]$DPIs,
    [int]$Margin,
    [int]$Leading,
    [string]$LeadingList,
    [int]$CharSpacing,
    [string]$CharSpacings,
    [switch]$EnableAug,
    [int]$AugVariants,
    [int]$MaxPages,
    [int]$CharsPerPage,
    # Corpus builder options
    [switch]$UseFixer,
    [int]$CorpusMinCount,
    # All-mode options
    [switch]$SkipEval,
    [string]$EvalPSMs,
    [switch]$EvalUseGTLexicon,
    [string]$EvalPrep,
    [switch]$EvalHOCRLines,
    [int]$EvalHOCRPSM,
    [switch]$EvalUserWordsCorpus,
    [switch]$EvalDisableDAWGs
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
    if ($LatinDigits) { $parts += "LATIN_DIGITS='1'" }
    if ($PuncsExtra) { $parts += "PUNCS_EXTRA='$(Escape-ShellSingleQuotes $PuncsExtra)'" }
    if ($TrainUseRealEval) { $parts += "IMPORT_REAL_EVAL='1'" }
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
    if ($ForceMinimal) { $parts += "FORCE_MINIMAL='1'" }
    if ($parts.Count -gt 0) { return ($parts -join ' ') + ' ' } else { return '' }
}

# Build env string for generation
function Get-GenEnvPrefix() {
    $parts = @()
    if ($CorpusFileOverride) { $parts += "CORPUS_FILE_OVERRIDE='$(Escape-ShellSingleQuotes (Convert-ToWslPath $CorpusFileOverride))'" }
    if ($FontsDirOverride) { $parts += "FONTS_DIR_OVERRIDE='$(Escape-ShellSingleQuotes (Convert-ToWslPath $FontsDirOverride))'" }
    if ($OutputDirOverride) { $parts += "OUTPUT_DIR_OVERRIDE='$(Escape-ShellSingleQuotes (Convert-ToWslPath $OutputDirOverride))'" }
    if ($FontSize) { $parts += "FONT_SIZE='${FontSize}'" }
    if ($FontSizes) { $parts += "FONT_SIZE_LIST='$(Escape-ShellSingleQuotes $FontSizes)'" }
    if ($DPI) { $parts += "DPI='${DPI}'" }
    if ($DPIs) { $parts += "DPI_LIST='$(Escape-ShellSingleQuotes $DPIs)'" }
    if ($Margin) { $parts += "MARGIN='${Margin}'" }
    if ($Leading) { $parts += "LEADING='${Leading}'" }
    if ($LeadingList) { $parts += "LEADING_LIST='$(Escape-ShellSingleQuotes $LeadingList)'" }
    if ($CharSpacing) { $parts += "CHAR_SPACING='${CharSpacing}'" }
    if ($CharSpacings) { $parts += "CHAR_SPACING_LIST='$(Escape-ShellSingleQuotes $CharSpacings)'" }
    if ($EnableAug) { $parts += "ENABLE_AUG='1'" }
    if ($AugVariants) { $parts += "AUG_VARIANTS='${AugVariants}'" }
    if ($Exposures) { $parts += "EXPOSURES='$(Escape-ShellSingleQuotes $Exposures)'" }
    if ($MaxPages) { $parts += "MAX_PAGES='${MaxPages}'" }
    if ($CharsPerPage) { $parts += "CHARS_PER_PAGE='${CharsPerPage}'" }
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



function Invoke-SmokeTest {
    param(
        [ValidateSet('auto', 'best', 'fast')] [string]$Variant = 'auto',
        [switch]$Interactive
    )
    # Determine image path
    $imgWin = $null
    if ($Interactive) {
        $gtDirWin = Get-GroundTruthDir -baseWin $workDirWin
        $defaultImg = $null
        if ($gtDirWin) {
            $firstTif = Get-ChildItem -Path $gtDirWin -Filter *.tif -File | Select-Object -First 1
            if ($firstTif) { $defaultImg = $firstTif.FullName }
        }
        $smokePrompt = "Enter image path for smoke test (Windows path)." + $(if ($defaultImg) { " Default: $defaultImg" } else { "" })
        $inputImg = Read-Host $smokePrompt
        if (-not $inputImg -and $defaultImg) { $imgWin = $defaultImg } else { $imgWin = $inputImg }
    }
    else {
        if ($ImagePath) { $imgWin = $ImagePath }
        if (-not $imgWin) {
            $gtDirWin = Get-GroundTruthDir -baseWin $workDirWin
            if ($gtDirWin) {
                $firstTif = Get-ChildItem -Path $gtDirWin -Filter *.tif -File | Select-Object -First 1
                if ($firstTif) { $imgWin = $firstTif.FullName }
            }
        }
    }
    if (-not $imgWin -or -not (Test-Path $imgWin)) {
        Write-Host "No input image found for smoke test. Provide -ImagePath or ensure ground-truth exists." -ForegroundColor DarkYellow
        exit 2
    }
    $imgWsl = Convert-ToWslPath $imgWin
    # Choose tessdata dir with ckb.traineddata based on variant
    $tessRoot = Join-Path $projectRootWin 'tessdata'
    $bestDir = Join-Path $tessRoot 'best'
    $fastDir = Join-Path $tessRoot 'fast'
    $tdWinCandidates = @()
    switch ($Variant) {
        'best' { $tdWinCandidates = @($bestDir) }
        'fast' { $tdWinCandidates = @($fastDir) }
        default { $tdWinCandidates = @($bestDir, $fastDir, $tessRoot) }
    }
    $tessdataWin = $null
    foreach ($td in $tdWinCandidates) {
        $ckb = Join-Path $td 'ckb.traineddata'
        if (Test-Path $ckb) { $tessdataWin = $td; break }
    }
    if (-not $tessdataWin) {
        $variantMsg = if ($Variant -eq 'best') { 'tessdata\\best' } elseif ($Variant -eq 'fast') { 'tessdata\\fast' } else { 'tessdata\\best or tessdata\\fast' }
        Write-Host "ckb.traineddata not found in $variantMsg. Run training first or place the model there." -ForegroundColor Yellow
        exit 2
    }
    $tessdataWsl = Convert-ToWslPath $tessdataWin
    Write-Host "`nRunning smoke test ($Variant) with ckb model..." -ForegroundColor Yellow
    $cmd = "echo 'Using tessdata dir: $tessdataWsl'; tesseract --tessdata-dir '$tessdataWsl' -l ckb --psm 6 '$imgWsl' stdout 2>&1 | head -n 15"
    $out = wsl -d Ubuntu -- bash -lc $cmd
    $code = $LASTEXITCODE
    if ($out) { Write-Host $out }
    else { Write-Host "(no text output)" -ForegroundColor DarkYellow }
    return $code
}

function Invoke-MigrateLegacyTessdata {
    try {
        $tessRoot = Join-Path $projectRootWin 'tessdata'
        $bestNew = Join-Path $tessRoot 'best'
        $fastNew = Join-Path $tessRoot 'fast'
        if (-not (Test-Path $bestNew)) { New-Item -ItemType Directory -Path $bestNew -Force | Out-Null }
        if (-not (Test-Path $fastNew)) { New-Item -ItemType Directory -Path $fastNew -Force | Out-Null }

        $legacyBest = Join-Path $projectRootWin 'tessdata_best'
        $legacyFast = Join-Path $projectRootWin 'tessdata_fast'
        $moved = $false
        if (Test-Path $legacyBest) {
            Get-ChildItem -Path $legacyBest -Filter *.traineddata -File -ErrorAction SilentlyContinue | ForEach-Object {
                Move-Item -Force -Path $_.FullName -Destination (Join-Path $bestNew $_.Name) -ErrorAction SilentlyContinue
                $script:moved = $true
            }
        }
        if (Test-Path $legacyFast) {
            Get-ChildItem -Path $legacyFast -Filter *.traineddata -File -ErrorAction SilentlyContinue | ForEach-Object {
                Move-Item -Force -Path $_.FullName -Destination (Join-Path $fastNew $_.Name) -ErrorAction SilentlyContinue
                $script:moved = $true
            }
        }
        if ($moved) {
            Write-Host "Migrated legacy models from tessdata_best/tessdata_fast to tessdata\\best/tessdata\\fast." -ForegroundColor DarkYellow
        }
    }
    catch { }
}

# Migrate any legacy tessdata folders into tessdata\best/fast (after functions are defined)
Invoke-MigrateLegacyTessdata


function Invoke-Cleanup([bool]$deep) {
    $deepFlag = if ($deep) { '1' } else { '0' }
    Write-Host "`nRunning cleanup (DEEP=$deepFlag)..." -ForegroundColor Yellow
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; sed -i 's/\r$//' cleanup_unnecessary_files.sh 2>/dev/null || true; chmod +x cleanup_unnecessary_files.sh; DEEP=$deepFlag bash ./cleanup_unnecessary_files.sh"
}

function Invoke-Bootstrap {
    Write-Host "`nBootstrapping WSL training environment..." -ForegroundColor Yellow
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; sed -i 's/\r$//' tools/bootstrap_wsl_training.sh 2>/dev/null || true; chmod +x tools/bootstrap_wsl_training.sh; tools/bootstrap_wsl_training.sh"; $code = $LASTEXITCODE
    if ($code -ne 0) { throw "Bootstrap failed (exit $code)." }
    Write-Host "Bootstrap complete." -ForegroundColor Green
}

function Invoke-BuildCorpus {
    Write-Host "`nBuilding balanced corpus..." -ForegroundColor Yellow
    $argsList = @('python3', 'tools/corpus_build.py')
    if ($UseFixer) { $argsList += '--fixer' }
    if ($CorpusMinCount -gt 0) { $argsList += @('--min-count', "$CorpusMinCount") }
    # Join arguments directly; no extra quoting needed for simple tokens
    $cmd = ($argsList -join ' ')
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; $cmd"; $code = $LASTEXITCODE
    if ($code -eq 2) { Write-Host "No corpus sources found; skipping corpus build." -ForegroundColor DarkYellow; return }
    if ($code -ne 0) { throw "Corpus build failed (exit $code)." }
    Write-Host "Corpus build complete (corpus/ckb.training_text.final)." -ForegroundColor Green

    # Run corpus audit (non-fatal but reported)
    Write-Host "Running corpus audit..." -ForegroundColor Yellow
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; python3 tools/corpus_audit.py --out output/corpus_audit"; $acode = $LASTEXITCODE
    if ($acode -eq 0) {
        Write-Host "Audit passed: no out-of-set characters." -ForegroundColor Green
    }
    elseif ($acode -eq 2) {
        Write-Host "Audit found out-of-set characters. See work/output/corpus_audit.json and .txt" -ForegroundColor DarkYellow
    }
}

function Invoke-ExpandCorpus {
    Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║        KURDISH CORPUS EXPANSION - BATCH 3           ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This will scrape additional Kurdish news sources:" -ForegroundColor Yellow
    Write-Host "  - NRT News (nrttv.com)" -ForegroundColor White
    Write-Host "  - Awene News (awene.com)" -ForegroundColor White
    Write-Host "  - BasNews (basnews.com/ku)" -ForegroundColor White
    Write-Host "Target: 3,000+ new high-quality sentences" -ForegroundColor Yellow
    Write-Host ""
    
    $timeout = 3600  # 1 hour timeout
    Write-Host "Running corpus expansion (timeout: ${timeout}s)..." -ForegroundColor Yellow
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; timeout $timeout python3 tools/expand_corpus_batch3_reliable.py"; $code = $LASTEXITCODE
    
    if ($code -eq 124) { 
        Write-Host "⚠️  Scraping timed out after ${timeout}s. Partial results may be saved." -ForegroundColor DarkYellow
    }
    elseif ($code -ne 0) { 
        throw "Corpus expansion failed (exit $code)." 
    }
    
    # Check if file was created
    $outputFile = Join-Path $projectRootWin "work\corpus\kurdish_expanded_batch3.txt"
    if (Test-Path $outputFile) {
        Write-Host "`n✅ Corpus expansion complete!" -ForegroundColor Green
        Write-Host "New corpus saved to: work/corpus/kurdish_expanded_batch3.txt" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "  1. Review quality: corpus/kurdish_expanded_batch3.txt" -ForegroundColor White
        Write-Host "  2. Combine with existing: corpus/ckb_phase6_batch2.training_text" -ForegroundColor White
        Write-Host "  3. Run: .\run_training.ps1 -Mode GenerateTrain" -ForegroundColor White
    }
    else {
        Write-Host "⚠️  No output file created. Check for errors above." -ForegroundColor DarkYellow
    }
}

function Invoke-EvalReal {
    Write-Host "`nEvaluating real-world CER..." -ForegroundColor Yellow
    $psmArg = ''
    if ($EvalPSMs) {
        $psmList = $EvalPSMs -replace ' ', ''
        $psmArg = " --psm-sweep '$psmList'"
    }
    $lexArg = if ($EvalUseGTLexicon) { ' --gt-lexicon' } else { '' }
    $prepArg = if ($EvalPrep) { " --prep '$(Escape-ShellSingleQuotes $EvalPrep)'" } else { '' }
    $oemArg = if ($OEM -in 1, 2, 3) { " --oem '$OEM'" } else { '' }
    $hocrArg = if ($EvalHOCRLines) { ' --hocr-lines' } else { '' }
    $hocrPsmArg = if ($EvalHOCRLines -and $EvalHOCRPSM) { " --hocr-psm '$EvalHOCRPSM'" } else { '' }
    $uwCorpusArg = if ($EvalUserWordsCorpus) { ' --user-words-corpus' } else { '' }
    $disableDawgsArg = if ($EvalDisableDAWGs) { ' --disable-dawgs' } else { '' }
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; python3 tools/eval_real_cer.py$psmArg$lexArg$prepArg$oemArg$hocrArg$hocrPsmArg$uwCorpusArg$disableDawgsArg"; $ecode = $LASTEXITCODE
    if ($ecode -ne 0) { Write-Host "Real eval returned code $ecode (no eval set or error)." -ForegroundColor DarkYellow }
    else { Write-Host "Real eval complete. See work/output/real_metrics.csv" -ForegroundColor Green }
}

function Invoke-All {
    try {
        Invoke-BuildCorpus
    }
    catch {
        Write-Host "Corpus build skipped/failed: $_" -ForegroundColor DarkYellow
    }

    # Prefer final corpus automatically if user did not override
    $prevCorpus = $CorpusFileOverride
    if (-not $CorpusFileOverride) {
        $finalWin = Join-Path (Join-Path $workDirWin 'corpus') 'ckb.training_text.final'
        if (Test-Path $finalWin) { $script:CorpusFileOverride = $finalWin }
    }

    Invoke-GenerateTrain

    # Restore corpus override
    $script:CorpusFileOverride = $prevCorpus

    if (-not $SkipEval) { Invoke-EvalReal }
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
            Write-Host "Generation exited with code $code, but found $tifCount TIF and $boxCount BOX files. Continuing..." -ForegroundColor Yellow
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
        'Bootstrap' {
            try { Invoke-Bootstrap; Write-Host "`nDone." -ForegroundColor Green; exit 0 } catch { Write-Host $_ -ForegroundColor Red; exit 1 }
        }
        'BuildCorpus' {
            try { Invoke-BuildCorpus; Write-Host "`nDone." -ForegroundColor Green; exit 0 } catch { Write-Host $_ -ForegroundColor Red; exit 1 }
        }
        'ExpandCorpus' {
            try { Invoke-ExpandCorpus; Write-Host "`nDone." -ForegroundColor Green; exit 0 } catch { Write-Host $_ -ForegroundColor Red; exit 1 }
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
        'Eval' {
            try { Invoke-EvalReal; Write-Host "`nDone." -ForegroundColor Green; exit 0 } catch { Write-Host $_ -ForegroundColor Red; exit 1 }
        }
        'All' {
            try { Invoke-All; Write-Host "`nAll pipeline completed." -ForegroundColor Green; exit 0 } catch { Write-Host $_ -ForegroundColor Red; exit 1 }
        }
        'SmokeTest' { $code = Invoke-SmokeTest -Variant auto; exit $code }
        'SmokeTestBest' { $code = Invoke-SmokeTest -Variant best; exit $code }
        'SmokeTestFast' { $code = Invoke-SmokeTest -Variant fast; exit $code }
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
Write-Host "4. Smoke test trained ckb model (auto: best→fast)" -ForegroundColor White
Write-Host "5. Smoke test (best only)" -ForegroundColor White
Write-Host "6. Smoke test (fast only)" -ForegroundColor White
Write-Host "7. Verify ckb.traineddata covers Kurdish chars" -ForegroundColor White
Write-Host "8. Build balanced corpus (uses fixer)" -ForegroundColor White
Write-Host "9. Evaluate real-world CER (real_gt/eval)" -ForegroundColor White
Write-Host "10. Bootstrap WSL training toolchain" -ForegroundColor White
Write-Host "11. All: Corpus → Generate → Train → Eval" -ForegroundColor White
Write-Host "" 

$choice = Read-Host "Enter your choice (1-11)"

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
        # Smoke test auto (best→fast)
        $null = Invoke-SmokeTest -Variant auto -Interactive
    }
    "5" {
        # Smoke test best only
        $null = Invoke-SmokeTest -Variant best -Interactive
    }
    "6" {
        # Smoke test fast only
        $null = Invoke-SmokeTest -Variant fast -Interactive
    }
    "7" {
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
    "8" {
        try {
            $script:UseFixer = $true
            Invoke-BuildCorpus
        }
        catch { Write-Host $_ -ForegroundColor Red }
    }
    "9" {
        try { Invoke-EvalReal } catch { Write-Host $_ -ForegroundColor Red }
    }
    "10" {
        try { Invoke-Bootstrap } catch { Write-Host $_ -ForegroundColor Red }
    }
    "11" {
        try { Invoke-All } catch { Write-Host $_ -ForegroundColor Red }
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nDone." -ForegroundColor Green
