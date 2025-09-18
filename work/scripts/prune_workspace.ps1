Param(
    [switch]$Delete
)

# Safe pruning script: moves known test/unnecessary files to work/.trash first.
$Root = Split-Path -Parent $PSScriptRoot | Split-Path -Parent
$Work = Join-Path $Root 'work'
$Trash = Join-Path $Work '.trash'
New-Item -ItemType Directory -Force -Path $Trash | Out-Null

Write-Host "Pruning workspace (safe mode). Files will be moved to: $Trash" -ForegroundColor Yellow

# Candidate paths to prune (adjust as needed)
$Candidates = @(
    'work/font-install-test',
    'work/font-test',
    'work/ocr-test',
    'work/syntax-test',
    'work/test-images',
    'work/tmp',
    'work/tessdata_tmp',
    'work/output/*',
    'work/ground-truth-auto',
    'work/ground-truth-batch',
    'work/ground-truth-corpus',
    'work/ground-truth-quick',
    'work/ground-truth-robust',
    'work/ground-truth-system',
    'work/ground-truth-workaround'
)

# Exclusions (never move/delete)
$Exclusions = @(
    'tessdata',
    'work/corpus',
    'work/fonts',
    'work/training',
    'work/docs',
    'work/scripts',
    'work/ground-truth',
    'work/ground-truth-final'
)

function IsExcluded($Path) {
    foreach ($ex in $Exclusions) {
        if ($Path -like (Join-Path $Root $ex) -or $Path -like (Join-Path $Root $ex + '*')) { return $true }
    }
    return $false
}

foreach ($pattern in $Candidates) {
    $full = Join-Path $Root $pattern
    Get-ChildItem -LiteralPath $full -Force -ErrorAction SilentlyContinue | ForEach-Object {
        if (-not (IsExcluded $_.FullName)) {
            $dest = Join-Path $Trash ($_.FullName.Substring($Root.Length).TrimStart('\\', '/'))
            New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
            Write-Host ("Moving: {0}" -f $_.FullName) -ForegroundColor Gray
            Move-Item -Force -Path $_.FullName -Destination $dest
        }
    }
}

if ($Delete) {
    Write-Host "Deleting trash contents..." -ForegroundColor Red
    Remove-Item -Recurse -Force -LiteralPath $Trash
    New-Item -ItemType Directory -Force -Path $Trash | Out-Null
    Write-Host "Trash emptied." -ForegroundColor Green
}
else {
    Write-Host "Review pruned files in: $Trash. Re-run with -Delete to permanently remove." -ForegroundColor Yellow
}
