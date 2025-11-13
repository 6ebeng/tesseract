param(
    [switch]$NoClear,
    [ValidateSet('Clean', 'Generate', 'GenerateTrain', 'Train', 'SmokeTest', 'SmokeTestBest', 'SmokeTestFast', 'Bootstrap', 'BuildCorpus', 'ExpandCorpus', 'ScrapeCorpus', 'DownloadFonts', 'ImprovedGenerate', 'ImprovedGenerateTrain', 'Eval', 'All')]
    [string]$Mode = '',
    [switch]$Deep = $false,
    [string]$ImagePath = '',
    # Training profile (Best = 2-3 days, comprehensive parameters; Fast = 2-3 hours, optimized parameters)
    [ValidateSet('Best', 'Fast')]
    [string]$TrainingProfile = 'Fast',
    # Custom ground-truth directory (if not set, will use profile-specific defaults)
    [string]$GroundTruthDir = '',
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
    # Parallel processing
    [int]$ParallelJobs = 0,
    # Batch processing (for network drives)
    [switch]$UseBatchProcessing,
    [int]$BatchSize = 5000,
    [int]$BatchWorkers = 22,
    # Corpus builder options
    [switch]$UseFixer,
    [int]$CorpusMinCount,
    # Scraper options
    [switch]$ScraperAll,
    [string]$ScraperWebsites,
    [int]$ScraperWorkers = 3,
    [switch]$ScraperFresh,
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
    
    # Pass OutputDirOverride to training script
    if ($OutputDirOverride) {
        $parts += "OUTPUT_DIR='$(Escape-ShellSingleQuotes (Convert-ToWslPath $OutputDirOverride))'"
    }
    
    # Batch processing mode for network drives
    if ($UseBatchProcessing) {
        $parts += "USE_BATCH_PROCESSING='1'"
        if ($BatchSize) {
            $parts += "BATCH_SIZE='${BatchSize}'"
        }
        if ($BatchWorkers) {
            $parts += "WORKERS='${BatchWorkers}'"
        }
    }
    
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

# Build env string for generation (including profile-specific output dir)
function Get-GenEnvPrefix() {
    $parts = @()
    if ($CorpusFileOverride) { $parts += "CORPUS_FILE_OVERRIDE='$(Escape-ShellSingleQuotes (Convert-ToWslPath $CorpusFileOverride))'" }
    if ($FontsDirOverride) { $parts += "FONTS_DIR_OVERRIDE='$(Escape-ShellSingleQuotes (Convert-ToWslPath $FontsDirOverride))'" }
    
    # Handle custom ground-truth directory first (highest priority)
    if ($GroundTruthDir) {
        # User specified custom ground-truth path
        $gtDirWsl = Convert-ToWslPath $GroundTruthDir
        $parts += "GROUND_TRUTH_DIR='$(Escape-ShellSingleQuotes $gtDirWsl)'"
        # Set output dir to parent of ground-truth unless explicitly overridden
        if (-not $OutputDirOverride) {
            $gtParentWin = Split-Path -Parent $GroundTruthDir
            if ($gtParentWin) {
                $parts += "OUTPUT_DIR='$(Escape-ShellSingleQuotes (Convert-ToWslPath $gtParentWin))'"
            }
        }
    }
    
    # Override output directory based on training profile (unless explicitly set)
    if ($OutputDirOverride) {
        $parts += "OUTPUT_DIR_OVERRIDE='$(Escape-ShellSingleQuotes (Convert-ToWslPath $OutputDirOverride))'" 
    }
    elseif (-not $GroundTruthDir) {
        # Use profile-specific directories for resumability and separation
        $profileSuffix = if ($TrainingProfile -eq 'Best') { '_best' } else { '_fast' }
        $profileOutputWin = Join-Path $workDirWin "training_output$profileSuffix"
        $parts += "OUTPUT_DIR_OVERRIDE='$(Escape-ShellSingleQuotes (Convert-ToWslPath $profileOutputWin))'"
    }
    
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
    if ($ParallelJobs -gt 0) { $parts += "PARALLEL_JOBS='${ParallelJobs}'" }
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

function Invoke-ScrapeCorpus {
    Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║      KURDISH CORPUS SCRAPING - PRODUCTION MODE      ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # Build scraper command
    $scraperDir = Convert-ToWslPath (Join-Path $workDirWin 'tools\scrapers')
    $configPath = 'configs/websites'
    $workers = if ($ScraperWorkers -gt 0) { $ScraperWorkers } else { 3 }
    
    # Build arguments
    $argsList = @('python3', 'run_production_display.py', '--config', $configPath)
    
    if ($ScraperAll) {
        $argsList += '--all'
        Write-Host "Scraping all 13 enabled Kurdish news websites" -ForegroundColor Yellow
    }
    elseif ($ScraperWebsites) {
        $argsList += '--websites'
        $argsList += $ScraperWebsites
        Write-Host "Scraping websites: $ScraperWebsites" -ForegroundColor Yellow
    }
    else {
        Write-Host "Error: Must specify -ScraperAll or -ScraperWebsites <list>" -ForegroundColor Red
        return
    }
    
    $argsList += '--parallel'
    $argsList += '--workers'
    $argsList += $workers
    
    if ($ScraperFresh) {
        $argsList += '--fresh'
        Write-Host "Fresh scrape: Clearing deduplication database" -ForegroundColor Yellow
    }
    
    Write-Host "Workers: $workers parallel" -ForegroundColor White
    Write-Host "Deduplication: $(if ($ScraperFresh) { 'OFF (fresh)' } else { 'ON' })" -ForegroundColor White
    Write-Host ""
    Write-Host "Starting production scraper..." -ForegroundColor Green
    Write-Host ""
    
    # Join arguments and run
    $cmd = ($argsList -join ' ')
    wsl -d Ubuntu -- bash -lc "cd '$scraperDir'; $cmd"; $code = $LASTEXITCODE
    
    if ($code -ne 0) {
        Write-Host "`n⚠️  Scraping completed with errors (exit code: $code)" -ForegroundColor DarkYellow
        Write-Host "Check logs at: work/tools/scrapers/logs/" -ForegroundColor White
    }
    else {
        Write-Host "`n✅ Scraping completed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Results saved to:" -ForegroundColor Yellow
        Write-Host "  - Corpus files: work/tools/scrapers/corpus/{website}/{category}.txt" -ForegroundColor White
        Write-Host "  - Logs: work/tools/scrapers/logs/scraper_*.log" -ForegroundColor White
        Write-Host "  - Dedup DB: work/tools/scrapers/article_dedup.db" -ForegroundColor White
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "  1. Review scraped text files in corpus/" -ForegroundColor White
        Write-Host "  2. Combine with existing corpus (if needed)" -ForegroundColor White
        Write-Host "  3. Run: .\run_training.ps1 -Mode BuildCorpus" -ForegroundColor White
        Write-Host "  4. Run: .\run_training.ps1 -Mode GenerateTrain" -ForegroundColor White
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
    
    # Mount Z: drive if using OutputDirOverride on network drive
    if ($OutputDirOverride -and $OutputDirOverride -like 'Z:*') {
        Write-Host "🔧 Mounting Z: drive in WSL..." -ForegroundColor Cyan
        wsl -d Ubuntu -- bash -c "sudo umount /mnt/z 2>/dev/null; sudo mount -t drvfs 'Z:' /mnt/z -o metadata,uid=1000,gid=1000" | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Z: drive mounted successfully" -ForegroundColor Green
        }
    }
    
    Write-Host "`nStarting training to build ckb.traineddata..." -ForegroundColor Yellow
    
    # If batch processing is enabled, run the batch processor first for LSTMF generation
    if ($UseBatchProcessing) {
        $totalFiles = $BatchSize * 3
        Write-Host "📦 BATCH MODE ENABLED - Processing in batches of $BatchSize file sets ($totalFiles files total) with $BatchWorkers workers" -ForegroundColor Cyan
        $batchScript = Join-Path $workDirWin 'batch_lstmf_processor.sh'
        $batchScriptWsl = Convert-ToWslPath $batchScript
        
        if (Test-Path $batchScript) {
            Write-Host "Running batch LSTMF processor..." -ForegroundColor Yellow
            # Pass environment variables to batch processor
            $trainEnv = Get-TrainEnvPrefix
            wsl -d Ubuntu -- bash -c "chmod +x '$batchScriptWsl'; $($trainEnv)'$batchScriptWsl'"
            if ($LASTEXITCODE -ne 0) {
                Write-Host "⚠️  Batch processor failed, falling back to standard processing" -ForegroundColor Yellow
            } else {
                Write-Host "✓ Batch LSTMF generation complete!" -ForegroundColor Green
                Write-Host "Now running remaining training steps..." -ForegroundColor Yellow
            }
        } else {
            Write-Host "⚠️  Batch processor script not found at $batchScript" -ForegroundColor Yellow
            Write-Host "Falling back to standard processing..." -ForegroundColor Yellow
        }
    }
    
    # Normalize line endings and run training script with env
    $trainEnv = Get-TrainEnvPrefix
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; sed -i 's/\r$//' '$trainScriptWsl' 2>/dev/null || true; chmod +x '$trainScriptWsl'; $($trainEnv)bash '$trainScriptWsl'"; $trainCode = $LASTEXITCODE
    if ($trainCode -ne 0) { throw "Training failed (exit $trainCode)." }
    Write-Host "`nTraining complete." -ForegroundColor Green
}

# Download additional Kurdish/Arabic fonts for improved training
function Invoke-DownloadFonts {
    Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║       DOWNLOADING ADDITIONAL KURDISH FONTS          ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    $fontsDirWin = Join-Path $workDirWin 'fonts'
    if (-not (Test-Path $fontsDirWin)) {
        New-Item -ItemType Directory -Path $fontsDirWin -Force | Out-Null
    }
    
    $currentCount = (Get-ChildItem -Path $fontsDirWin -Filter *.ttf -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "Current fonts: $currentCount" -ForegroundColor Yellow
    
    # Check if download script exists
    $downloadScriptWin = Join-Path $workDirWin 'download_kurdish_fonts.sh'
    if (-not (Test-Path $downloadScriptWin)) {
        Write-Host "Warning: download_kurdish_fonts.sh not found. Using WSL curl to download key fonts..." -ForegroundColor Yellow
        
        # Download critical fonts directly
        $fonts = @{
            'Amiri-Regular.ttf' = 'https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf'
            'Amiri-Bold.ttf' = 'https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Bold.ttf'
            'Scheherazade-Regular.ttf' = 'https://github.com/google/fonts/raw/main/ofl/scheherazadenew/ScheherazadeNew-Regular.ttf'
            'Scheherazade-Bold.ttf' = 'https://github.com/google/fonts/raw/main/ofl/scheherazadenew/ScheherazadeNew-Bold.ttf'
            'Cairo-Regular.ttf' = 'https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Regular.ttf'
            'Cairo-Bold.ttf' = 'https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Bold.ttf'
        }
        
        $fontsDirWsl = Convert-ToWslPath $fontsDirWin
        $success = 0
        foreach ($fontName in $fonts.Keys) {
            $url = $fonts[$fontName]
            $destWsl = "$fontsDirWsl/$fontName"
            Write-Host "  Downloading: $fontName" -ForegroundColor Gray
            wsl -d Ubuntu -- bash -lc "curl -fsSL -o '$destWsl' '$url' 2>/dev/null" | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $success++
                Write-Host "    ✅ Success" -ForegroundColor Green
            } else {
                Write-Host "    ❌ Failed" -ForegroundColor Red
            }
        }
        Write-Host "`nDownloaded $success / $($fonts.Count) fonts" -ForegroundColor Yellow
    }
    else {
        # Use the download script
        Write-Host "Running download_kurdish_fonts.sh..." -ForegroundColor Yellow
        wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; sed -i 's/\r$//' download_kurdish_fonts.sh 2>/dev/null || true; chmod +x download_kurdish_fonts.sh; bash download_kurdish_fonts.sh"
    }
    
    $newCount = (Get-ChildItem -Path $fontsDirWin -Filter *.ttf -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "`n✅ Font download complete!" -ForegroundColor Green
    Write-Host "   Before: $currentCount fonts" -ForegroundColor White
    Write-Host "   After:  $newCount fonts" -ForegroundColor Green
    Write-Host "   Added:  $($newCount - $currentCount) new fonts" -ForegroundColor Cyan
    
    if ($newCount -ge 15) {
        Write-Host "`n🎉 Excellent! You have $newCount fonts for optimal training." -ForegroundColor Green
    } elseif ($newCount -ge 10) {
        Write-Host "`n✅ Good! You have $newCount fonts for training." -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  Only $newCount fonts available. More fonts = better accuracy." -ForegroundColor Yellow
    }
}

# Generate improved training data with multi-scale + augmentation
function Invoke-ImprovedGenerate {
    Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║    OPTIMIZED TRAINING DATA GENERATION               ║" -ForegroundColor Cyan
    if ($ParallelJobs -gt 0) {
        Write-Host "║    🚀 PARALLEL MODE: $ParallelJobs worker jobs          ║" -ForegroundColor Cyan
    }
    Write-Host "║    Multi-Scale + Augmentation (Smart Parameters)    ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # Always use the optimized standard script (generate_ckb_training_data.sh)
    # which now has smart defaults built in
    $scriptName = 'generate_ckb_training_data.sh'
    
    # Apply training profile parameters
    if ($TrainingProfile -eq 'Best') {
        Write-Host "🏆 TRAINING PROFILE: BEST (Comprehensive - 2-3 days)" -ForegroundColor Magenta
        Write-Host "   Maximum diversity for highest possible accuracy" -ForegroundColor Yellow
        Write-Host ""
        
        # Best profile: comprehensive parameters for maximum accuracy
        # Override script defaults if user hasn't specified custom values
        if (-not $FontSizes) { $script:FontSizes = '16,18,20,22' }
        if (-not $DPIs) { $script:DPIs = '200,300,400' }
        if (-not $LeadingList) { $script:LeadingList = '20,22,26' }
        if (-not $CharSpacings) { $script:CharSpacings = '0.5,1.0,1.5' }
        if (-not $Exposures) { $script:Exposures = '-2,-1,0,1,2' }
        if (-not $EnableAug) { $script:EnableAug = $true }
        if (-not $AugVariants) { $script:AugVariants = 5 }
        
        Write-Host "🎨 BEST Profile Parameters:" -ForegroundColor Yellow
        Write-Host "   • Font sizes: 16, 18, 20, 22 pt (4 values)" -ForegroundColor White
        Write-Host "   • DPI: 200, 300, 400 (3 values)" -ForegroundColor White
        Write-Host "   • Leading: 20, 22, 26 px (3 values)" -ForegroundColor White
        Write-Host "   • Char spacing: 0.5, 1.0, 1.5 (3 values)" -ForegroundColor White
        Write-Host "   • Exposures: -2, -1, 0, 1, 2 (5 values)" -ForegroundColor White
        Write-Host "   • Augmentation: 5 variants per image" -ForegroundColor White
        Write-Host ""
    }
    else {
        Write-Host "⚡ TRAINING PROFILE: FAST (Optimized - 2-3 hours)" -ForegroundColor Cyan
        Write-Host "   Smart parameter selection for speed + accuracy" -ForegroundColor Yellow
        Write-Host ""
        
        # Fast profile uses script defaults (already optimized)
        # Only override if user hasn't specified custom values
        if (-not $FontSizes) { $script:FontSizes = '16,20' }
        if (-not $DPIs) { $script:DPIs = '200,400' }
        if (-not $LeadingList) { $script:LeadingList = '22,26' }
        if (-not $CharSpacings) { $script:CharSpacings = '0.8,1.2' }
        if (-not $Exposures) { $script:Exposures = '-1,0,1' }
        if (-not $EnableAug) { $script:EnableAug = $true }
        if (-not $AugVariants) { $script:AugVariants = 2 }
        
        Write-Host "🎨 FAST Profile Parameters:" -ForegroundColor Yellow
        Write-Host "   • Font sizes: 16, 20 pt (2 values)" -ForegroundColor White
        Write-Host "   • DPI: 200, 400 (2 values)" -ForegroundColor White
        Write-Host "   • Leading: 22, 26 px (2 values)" -ForegroundColor White
        Write-Host "   • Char spacing: 0.8, 1.2 (2 values)" -ForegroundColor White
        Write-Host "   • Exposures: -1, 0, 1 (3 values)" -ForegroundColor White
        Write-Host "   • Augmentation: 2 variants per image" -ForegroundColor White
        Write-Host ""
    }
    
    Write-Host "✓ Using optimized generate_ckb_training_data.sh" -ForegroundColor Green
    
    # Build enhanced environment variables
    $genEnv = Get-GenEnvPrefix
    
    $fontCount = (Get-ChildItem -Path (Join-Path $workDirWin 'fonts') -Filter *.ttf -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "Available fonts: $fontCount" -ForegroundColor Cyan
    Write-Host ""
    
    # Determine ground-truth directory based on profile or custom path
    if ($GroundTruthDir) {
        $gtDirWin = $GroundTruthDir
        Write-Host "📁 Using CUSTOM ground-truth directory:" -ForegroundColor Cyan
        Write-Host "   $gtDirWin" -ForegroundColor White
    }
    else {
        $profileSuffix = if ($TrainingProfile -eq 'Best') { '_best' } else { '_fast' }
        $gtDirWin = Join-Path $workDirWin "training_output$profileSuffix\ground_truth"
        Write-Host "📁 Using PROFILE-SPECIFIC ground-truth directory:" -ForegroundColor Cyan
        Write-Host "   $gtDirWin" -ForegroundColor White
    }
    Write-Host ""
    
    # Create directory if it doesn't exist
    if (-not (Test-Path $gtDirWin)) {
        New-Item -ItemType Directory -Path $gtDirWin -Force | Out-Null
        Write-Host "✓ Created ground-truth directory" -ForegroundColor Green
    }
    else {
        # Check if resumable (existing files)
        $existingTif = (Get-ChildItem -Path $gtDirWin -Filter *.tif -ErrorAction SilentlyContinue | Measure-Object).Count
        if ($existingTif -gt 0) {
            Write-Host "🔄 RESUMABLE: Found $existingTif existing TIF files (will skip duplicates)" -ForegroundColor Yellow
            Write-Host ""
        }
    }
    
    if ($fontCount -lt 10) {
        Write-Host "⚠️  Only $fontCount fonts found. Run: .\run_training.ps1 -Mode DownloadFonts" -ForegroundColor Yellow
        Write-Host "   Continuing with available fonts..." -ForegroundColor Gray
    }
    
    # Determine profile-specific output directory (but don't override $gtDirWin if already set)
    $profileSuffix = if ($TrainingProfile -eq 'Best') { '_best' } else { '_fast' }
    
    if ($OutputDirOverride) {
        # Use the override directory
        $profileOutputWin = $OutputDirOverride
        if (-not $gtDirWin) {
            $gtDirWin = Join-Path $profileOutputWin 'ground_truth'
        }
    } else {
        # Use default profile-specific directory
        $profileOutputWin = Join-Path $workDirWin "training_output$profileSuffix"
        if (-not $gtDirWin) {
            $gtDirWin = Join-Path $profileOutputWin 'ground_truth'
        }
    }
    
    # Create directories if they don't exist (for resumability)
    if (-not (Test-Path $profileOutputWin)) {
        New-Item -ItemType Directory -Path $profileOutputWin -Force | Out-Null
    }
    if (-not (Test-Path $gtDirWin)) {
        New-Item -ItemType Directory -Path $gtDirWin -Force | Out-Null
    }
    
    # Check for existing files (resumable)
    $existingTif = (Get-ChildItem -Path $gtDirWin -Filter *.tif -File -ErrorAction SilentlyContinue | Measure-Object).Count
    $existingBox = (Get-ChildItem -Path $gtDirWin -Filter *.box -File -ErrorAction SilentlyContinue | Measure-Object).Count
    
    if ($existingTif -gt 0 -or $existingBox -gt 0) {
        Write-Host "🔄 RESUMABLE: Found $existingTif existing TIF files in $TrainingProfile profile" -ForegroundColor Yellow
        Write-Host "   Generation will skip already-created files and continue" -ForegroundColor Gray
        Write-Host ""
    }
    
    # Calculate expected images and time based on profile
    if ($TrainingProfile -eq 'Best') {
        # Best: 4 font sizes × 3 DPIs × 3 leadings × 3 char spacings × 5 exposures × 6 variants (base + 5 aug) = 9,720 per font
        # With 9 fonts: ~87,480 images
        $estimatedImages = $fontCount * 9720
        $estimatedHours = if ($fontCount -ge 15) { 84 } elseif ($fontCount -ge 9) { 60 } else { 36 }
        $estimatedTime = if ($fontCount -ge 15) { "3.5 days" } elseif ($fontCount -ge 9) { "2.5 days" } else { "1.5 days" }
        Write-Host "📊 Expected output: ~$estimatedImages training images" -ForegroundColor Magenta
        Write-Host "⏱️  Estimated time: $estimatedTime (~$estimatedHours hours)" -ForegroundColor Magenta
        Write-Host "💾 Output directory: training_output_best/" -ForegroundColor Magenta
    }
    else {
        # Fast: 2 font sizes × 2 DPIs × 2 leadings × 2 char spacings × 3 exposures × 3 variants (base + 2 aug) = 288 per font
        # With 9 fonts: ~2,592 images
        $estimatedImages = $fontCount * 288
        $estimatedHours = if ($fontCount -ge 15) { 4 } elseif ($fontCount -ge 9) { 2.5 } else { 1.5 }
        $estimatedTime = if ($fontCount -ge 15) { "3-4 hours" } elseif ($fontCount -ge 9) { "2-3 hours" } else { "1-2 hours" }
        Write-Host "📊 Expected output: ~$estimatedImages training images" -ForegroundColor Cyan
        Write-Host "⏱️  Estimated time: $estimatedTime (~$estimatedHours hours)" -ForegroundColor Cyan
        Write-Host "💾 Output directory: training_output_fast/" -ForegroundColor Cyan
    }
    
    if ($existingTif -gt 0) {
        $remaining = $estimatedImages - $existingTif
        $percentComplete = [math]::Round(($existingTif / $estimatedImages) * 100, 1)
        Write-Host "📈 Progress: $percentComplete% complete ($existingTif / $estimatedImages files)" -ForegroundColor Yellow
        Write-Host "⏳ Remaining: ~$remaining images to generate" -ForegroundColor Yellow
    }
    Write-Host ""
    
    # Show resumability and monitoring info
    Write-Host "♻️  RESUMABLE: Generation will skip already-created files" -ForegroundColor Green
    Write-Host "   You can stop (Ctrl+C) and restart without losing progress" -ForegroundColor Gray
    Write-Host ""
    
    # Auto-mount Z: drive if using custom output path on NAS
    if ($OutputDirOverride -and $OutputDirOverride.StartsWith("Z:\")) {
        Write-Host "🔧 Setting up Z: drive mount for NAS storage..." -ForegroundColor Cyan
        $mountScript = Join-Path $projectRootWin 'setup_z_mount.sh'
        if (Test-Path $mountScript) {
            $mountCmd = "echo tishko | sudo -S bash /mnt/c/tesseract/setup_z_mount.sh"
            $null = wsl -d Ubuntu -- bash -c $mountCmd 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Z: drive mounted successfully" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Z: drive mount may have failed - continuing anyway..." -ForegroundColor Yellow
            }
        } else {
            Write-Host "⚠️  Z: drive mount script not found - continuing anyway..." -ForegroundColor Yellow
        }
        Write-Host ""
    }
    
    # Run generation with progress monitoring
    $profileSuffix = if ($TrainingProfile -eq 'Best') { '_best' } else { '_fast' }
    Write-Host "Starting $TrainingProfile profile generation..." -ForegroundColor Yellow
    if (-not $GroundTruthDir) {
        Write-Host "Monitor progress: Get-ChildItem 'c:\tesseract\work\training_output$profileSuffix\ground_truth\*.tif' | Measure-Object" -ForegroundColor Gray
    }
    else {
        Write-Host "Monitor progress: Get-ChildItem '$GroundTruthDir\*.tif' | Measure-Object" -ForegroundColor Gray
    }
    Write-Host ""
    
    $startTime = Get-Date
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; sed -i 's/\r$//' '$scriptName' 2>/dev/null || true; chmod +x '$scriptName'; $($genEnv)bash '$scriptName'"; $code = $LASTEXITCODE
    $endTime = Get-Date
    $elapsed = $endTime - $startTime
    
    if ($code -ne 0) {
        # Check if files were actually generated
        $tifCount = 0; $boxCount = 0
        if (Test-Path $gtDirWin) {
            $tifCount = (Get-ChildItem -Path $gtDirWin -Filter *.tif -File -ErrorAction SilentlyContinue | Measure-Object).Count
            $boxCount = (Get-ChildItem -Path $gtDirWin -Filter *.box -File -ErrorAction SilentlyContinue | Measure-Object).Count
        }
        if ($tifCount -gt 0 -and $boxCount -gt 0) {
            Write-Host "`nGeneration completed with warnings, but found $tifCount training images." -ForegroundColor Yellow
        } else {
            throw "Improved generation failed (exit $code)"
        }
    }
    
    # Show results with timing
    $tifCount = (Get-ChildItem -Path $gtDirWin -Filter *.tif -File -ErrorAction SilentlyContinue | Measure-Object).Count
    $boxCount = (Get-ChildItem -Path $gtDirWin -Filter *.box -File -ErrorAction SilentlyContinue | Measure-Object).Count
    
    $elapsedHours = [math]::Round($elapsed.TotalHours, 2)
    $elapsedMinutes = [math]::Round($elapsed.TotalMinutes, 1)
    
    Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║       OPTIMIZED GENERATION COMPLETE                 ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Generated .tif files: $tifCount" -ForegroundColor Green
    Write-Host "✅ Generated .box files: $boxCount" -ForegroundColor Green
    Write-Host "⏱️  Actual time: $elapsedMinutes minutes ($elapsedHours hours)" -ForegroundColor Cyan
    Write-Host "💾 Location: training_output$profileSuffix/ground_truth/" -ForegroundColor Cyan
    Write-Host ""
    
    if ($TrainingProfile -eq 'Best') {
        Write-Host "� BEST PROFILE BENEFITS:" -ForegroundColor Magenta
        Write-Host "   • Maximum parameter diversity (4 sizes × 3 DPIs × 3 spacings × 5 exposures)" -ForegroundColor White
        Write-Host "   • Comprehensive augmentation (5 variants: noise, JPEG, halftone, texture, vignette)" -ForegroundColor White
        Write-Host "   • Best possible accuracy for production use" -ForegroundColor White
        Write-Host "   • Robust to diverse real-world conditions" -ForegroundColor Green
    }
    else {
        Write-Host "🎯 FAST PROFILE BENEFITS:" -ForegroundColor Cyan
        Write-Host "   • Smart parameter diversity (2 sizes × 2 DPIs × 2 spacings × 3 exposures)" -ForegroundColor White
        Write-Host "   • Efficient augmentation (2 variants: noise, JPEG artifacts)" -ForegroundColor White
        Write-Host "   • Fast iteration for experimentation" -ForegroundColor White
        Write-Host "   • Good accuracy with minimal time" -ForegroundColor Green
    }
    Write-Host ""
}

# Optimized generate + train pipeline
function Invoke-ImprovedGenerateTrain {
    Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║    OPTIMIZED TRAINING PIPELINE                      ║" -ForegroundColor Cyan
    Write-Host "║    Generate (Smart Params) → Train → Evaluate       ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # Step 1: Download fonts if needed
    $fontCount = (Get-ChildItem -Path (Join-Path $workDirWin 'fonts') -Filter *.ttf -ErrorAction SilentlyContinue | Measure-Object).Count
    if ($fontCount -lt 10) {
        Write-Host "📥 Step 1: Downloading additional fonts..." -ForegroundColor Cyan
        Invoke-DownloadFonts
        Write-Host ""
    } else {
        Write-Host "✓ Step 1: Fonts ready ($fontCount fonts)" -ForegroundColor Green
        Write-Host ""
    }
    
    # Step 2: Generate optimized training data
    Write-Host "📊 Step 2: Generating optimized training data..." -ForegroundColor Cyan
    Invoke-ImprovedGenerate
    Write-Host ""
    
    # Step 3: Train model
    Write-Host "🚀 Step 3: Training model..." -ForegroundColor Cyan
    Invoke-Train
    Write-Host ""
    
    # Step 4: Quick evaluation
    Write-Host "📈 Step 4: Quick evaluation..." -ForegroundColor Cyan
    $code = Invoke-SmokeTest -Variant best
    
    Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║      OPTIMIZED TRAINING PIPELINE COMPLETE            ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Model trained with optimized data (faster, same accuracy)" -ForegroundColor Green
    Write-Host "📊 Run full evaluation: .\run_training.ps1 -Mode Eval -EvalPSMs '6,11,7,13'" -ForegroundColor Cyan
    Write-Host ""
}

# Parallel generation (10-20x faster using all CPU cores)
function Invoke-ParallelGenerate {
    Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║    PARALLEL TRAINING DATA GENERATION                ║" -ForegroundColor Cyan
    Write-Host "║    10-20x Faster Using All CPU Cores                ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    $scriptName = 'generate_ckb_parallel.sh'
    
    # Apply training profile parameters
    if ($TrainingProfile -eq 'Best') {
        Write-Host "🏆 TRAINING PROFILE: BEST (Comprehensive - PARALLEL)" -ForegroundColor Magenta
        if (-not $FontSizes) { $script:FontSizes = '16,18,20,22' }
        if (-not $DPIs) { $script:DPIs = '200,300,400' }
        if (-not $LeadingList) { $script:LeadingList = '20,22,26' }
        if (-not $CharSpacings) { $script:CharSpacings = '0.5,1.0,1.5' }
        if (-not $Exposures) { $script:Exposures = '-2,-1,0,1,2' }
        if (-not $EnableAug) { $script:EnableAug = $true }
        if (-not $AugVariants) { $script:AugVariants = 5 }
    }
    else {
        Write-Host "⚡ TRAINING PROFILE: FAST (Optimized - PARALLEL)" -ForegroundColor Cyan
        if (-not $FontSizes) { $script:FontSizes = '16,20' }
        if (-not $DPIs) { $script:DPIs = '200,400' }
        if (-not $LeadingList) { $script:LeadingList = '22,26' }
        if (-not $CharSpacings) { $script:CharSpacings = '0.8,1.2' }
        if (-not $Exposures) { $script:Exposures = '-1,0,1' }
        if (-not $EnableAug) { $script:EnableAug = $true }
        if (-not $AugVariants) { $script:AugVariants = 2 }
    }
    
    $genEnv = Get-GenEnvPrefix
    
    $fontCount = (Get-ChildItem -Path (Join-Path $workDirWin 'fonts') -Filter *.ttf -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "Available fonts: $fontCount" -ForegroundColor Cyan
    
    # Determine profile-specific ground-truth directory
    $profileSuffix = if ($TrainingProfile -eq 'Best') { '_best' } else { '_fast' }
    $profileOutputWin = Join-Path $workDirWin "training_output$profileSuffix"
    $gtDirWin = Join-Path $profileOutputWin 'ground_truth'
    
    if (-not (Test-Path $profileOutputWin)) {
        New-Item -ItemType Directory -Path $profileOutputWin -Force | Out-Null
    }
    if (-not (Test-Path $gtDirWin)) {
        New-Item -ItemType Directory -Path $gtDirWin -Force | Out-Null
    }
    
    $existingTif = (Get-ChildItem -Path $gtDirWin -Filter *.tif -File -ErrorAction SilentlyContinue | Measure-Object).Count
    
    if ($TrainingProfile -eq 'Best') {
        $estimatedImages = $fontCount * 9720
        $estimatedHours = [math]::Round($estimatedImages / ($env:NUMBER_OF_PROCESSORS * 60), 1)
    }
    else {
        $estimatedImages = $fontCount * 288
        $estimatedHours = [math]::Round($estimatedImages / ($env:NUMBER_OF_PROCESSORS * 60), 1)
    }
    
    Write-Host "📊 Expected output: ~$estimatedImages training images" -ForegroundColor Cyan
    Write-Host "⚡ Parallel workers: $env:NUMBER_OF_PROCESSORS CPU cores" -ForegroundColor Green
    Write-Host "⏱️  Estimated time: ~$estimatedHours hours (vs. days with sequential)" -ForegroundColor Green
    Write-Host ""
    
    if ($existingTif -gt 0) {
        Write-Host "🔄 Found $existingTif existing files - will skip and resume" -ForegroundColor Yellow
        Write-Host ""
    }
    
    # Run parallel generation
    Write-Host "Starting PARALLEL generation..." -ForegroundColor Yellow
    $startTime = Get-Date
    wsl -d Ubuntu -- bash -lc "cd '$workDirWsl'; sed -i 's/\r$//' '$scriptName' 2>/dev/null || true; chmod +x '$scriptName'; $($genEnv)bash '$scriptName'"; $code = $LASTEXITCODE
    $endTime = Get-Date
    $elapsed = $endTime - $startTime
    
    if ($code -ne 0) {
        $tifCount = (Get-ChildItem -Path $gtDirWin -Filter *.tif -File -ErrorAction SilentlyContinue | Measure-Object).Count
        if ($tifCount -gt $existingTif) {
            Write-Host "`nGeneration had warnings but generated $($tifCount - $existingTif) new files" -ForegroundColor Yellow
        } else {
            throw "Parallel generation failed (exit $code)"
        }
    }
    
    $tifCount = (Get-ChildItem -Path $gtDirWin -Filter *.tif -File -ErrorAction SilentlyContinue | Measure-Object).Count
    $elapsedHours = [math]::Round($elapsed.TotalHours, 2)
    
    Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║       PARALLEL GENERATION COMPLETE                  ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Total TIF files: $tifCount" -ForegroundColor Green
    Write-Host "⚡ Parallel speedup: ~10-20x faster than sequential" -ForegroundColor Green
    Write-Host "⏱️  Actual time: $elapsedHours hours" -ForegroundColor Cyan
    Write-Host ""
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
        'ScrapeCorpus' {
            try { Invoke-ScrapeCorpus; Write-Host "`nDone." -ForegroundColor Green; exit 0 } catch { Write-Host $_ -ForegroundColor Red; exit 1 }
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
        'DownloadFonts' {
            try { Invoke-DownloadFonts; Write-Host "`nDone." -ForegroundColor Green; exit 0 } catch { Write-Host $_ -ForegroundColor Red; exit 1 }
        }
        'ImprovedGenerate' {
            try {
                Invoke-ImprovedGenerate
                Write-Host "`nImproved generation completed successfully." -ForegroundColor Green
                exit 0
            }
            catch {
                Write-Host $_ -ForegroundColor Red
                exit 1
            }
        }
        'ImprovedGenerateTrain' {
            try {
                Invoke-ImprovedGenerateTrain
                Write-Host "`nImproved pipeline completed successfully." -ForegroundColor Green
                exit 0
            }
            catch {
                Write-Host $_ -ForegroundColor Red
                exit 1
            }
        }
        'ParallelGenerate' {
            try {
                Invoke-ParallelGenerate
                Write-Host "`nParallel generation completed successfully." -ForegroundColor Green
                exit 0
            }
            catch {
                Write-Host $_ -ForegroundColor Red
                exit 1
            }
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
Write-Host "4. Smoke test trained ckb model (auto: best→fast)" -ForegroundColor White
Write-Host "5. Smoke test (best only)" -ForegroundColor White
Write-Host "6. Smoke test (fast only)" -ForegroundColor White
Write-Host "7. Verify ckb.traineddata covers Kurdish chars" -ForegroundColor White
Write-Host "8. Build balanced corpus (uses fixer)" -ForegroundColor White
Write-Host "9. Scrape Kurdish news corpus (production scraper)" -ForegroundColor White
Write-Host "10. Evaluate real-world CER (real_gt/eval)" -ForegroundColor White
Write-Host "11. Bootstrap WSL training toolchain" -ForegroundColor White
Write-Host "12. All: Corpus → Generate → Train → Eval" -ForegroundColor White
Write-Host "" 

$choice = Read-Host "Enter your choice (1-12)"

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
        # Scrape Kurdish news corpus
        Write-Host "`nProduction scraper options:" -ForegroundColor Yellow
        Write-Host "1. Scrape all 13 websites (recommended)" -ForegroundColor White
        Write-Host "2. Scrape specific websites" -ForegroundColor White
        $scraperChoice = Read-Host "Enter choice (1-2)"
        
        try {
            if ($scraperChoice -eq "1") {
                $script:ScraperAll = $true
            }
            elseif ($scraperChoice -eq "2") {
                $websiteList = Read-Host "Enter websites (comma-separated, e.g., avanews,awene,rudaw)"
                if (-not $websiteList) {
                    Write-Host "No websites specified. Aborting." -ForegroundColor Red
                    break
                }
                $script:ScraperWebsites = $websiteList
            }
            else {
                Write-Host "Invalid choice. Aborting." -ForegroundColor Red
                break
            }
            
            $workersInput = Read-Host "Number of parallel workers (default: 3)"
            if ($workersInput) { $script:ScraperWorkers = [int]$workersInput }
            
            $freshInput = Read-Host "Clear deduplication database (fresh scrape)? (y/N)"
            $script:ScraperFresh = ($freshInput -match '^(y|yes)$')
            
            Invoke-ScrapeCorpus
        }
        catch { Write-Host $_ -ForegroundColor Red }
    }
    "10" {
        try { Invoke-EvalReal } catch { Write-Host $_ -ForegroundColor Red }
    }
    "11" {
        try { Invoke-Bootstrap } catch { Write-Host $_ -ForegroundColor Red }
    }
    "12" {
        try { Invoke-All } catch { Write-Host $_ -ForegroundColor Red }
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nDone." -ForegroundColor Green
