#!/usr/bin/env pwsh
# Enhanced Training Monitor for 50K Iteration Training
# Monitors progress, estimates completion, displays stats

param(
    [switch]$Continuous,
    [int]$RefreshSeconds = 60
)

$WorkDir = "C:\tesseract\work"
$LogDir = "$WorkDir\training_output\logs"
$ModelDir = "$WorkDir\training_output\model"

function Get-TrainingStatus {
    param([string]$LogFile, [string]$ModelName)
    
    if (-not (Test-Path $LogFile)) {
        return @{
            Model = $ModelName
            Status = "Not Started"
            Iteration = 0
            MaxIter = 0
            BCER = "N/A"
            Progress = 0
            TimeElapsed = "N/A"
            TimeRemaining = "N/A"
            ETA = "N/A"
        }
    }
    
    $content = Get-Content $LogFile -Tail 100 -ErrorAction SilentlyContinue
    if (-not $content) {
        return @{
            Model = $ModelName
            Status = "Starting"
            Iteration = 0
            MaxIter = 0
            BCER = "N/A"
            Progress = 0
        }
    }
    
    # Find latest iteration line
    $iterLines = $content | Where-Object { $_ -match 'At iteration (\d+)/(\d+)/\d+.*BCER.*?=\s*([\d.]+)%' }
    
    if ($iterLines) {
        $lastLine = $iterLines[-1]
        if ($lastLine -match 'At iteration (\d+)/(\d+)/\d+.*BCER.*?=\s*([\d.]+)%') {
            $currentIter = [int]$matches[1]
            $maxIter = [int]$matches[2]
            $bcer = [double]$matches[3]
            $progress = [math]::Round(($currentIter / $maxIter) * 100, 2)
            
            # Try to find start time from log
            $startLines = Get-Content $LogFile -Head 50 -ErrorAction SilentlyContinue
            $startTime = $null
            foreach ($line in $startLines) {
                if ($line -match '(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})') {
                    $startTime = [DateTime]::ParseExact($matches[1], "yyyy-MM-dd HH:mm:ss", $null)
                    break
                }
            }
            
            $status = @{
                Model = $ModelName
                Status = "Training"
                Iteration = $currentIter
                MaxIter = $maxIter
                BCER = "$bcer%"
                Progress = $progress
            }
            
            if ($startTime) {
                $elapsed = (Get-Date) - $startTime
                $status.TimeElapsed = "{0:hh\:mm\:ss}" -f $elapsed
                
                if ($currentIter -gt 0) {
                    $iterPerSec = $currentIter / $elapsed.TotalSeconds
                    $remainingIter = $maxIter - $currentIter
                    $remainingSec = $remainingIter / $iterPerSec
                    $remaining = [TimeSpan]::FromSeconds($remainingSec)
                    $eta = (Get-Date).AddSeconds($remainingSec)
                    
                    $status.TimeRemaining = "{0:hh\:mm\:ss}" -f $remaining
                    $status.ETA = $eta.ToString("MMM dd, HH:mm")
                }
            }
            
            return $status
        }
    }
    
    # Check if completed
    $finishedLine = $content | Where-Object { $_ -match 'Finished!' }
    if ($finishedLine) {
        $bcerMatch = $finishedLine | Where-Object { $_ -match 'BCER.*?=\s*([\d.]+)' }
        $finalBCER = if ($bcerMatch -and $bcerMatch -match 'BCER.*?=\s*([\d.]+)') { 
            "$($matches[1])%" 
        } else { 
            "N/A" 
        }
        
        return @{
            Model = $ModelName
            Status = "✅ Completed"
            Iteration = "Done"
            MaxIter = "N/A"
            BCER = $finalBCER
            Progress = 100
            TimeElapsed = "N/A"
            TimeRemaining = "Completed"
            ETA = "Done"
        }
    }
    
    return @{
        Model = $ModelName
        Status = "Running"
        Iteration = "Unknown"
        MaxIter = "50000"
        BCER = "N/A"
        Progress = 0
    }
}

function Show-TrainingDashboard {
    Clear-Host
    
    Write-Host "╔════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         KURDISH OCR - TRAINING MONITOR (50K Iterations)              ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📅 Current Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
    Write-Host ""
    
    # Check generation status
    $boxCount = (Get-ChildItem "$WorkDir\training_output\ground_truth\*.box" -ErrorAction SilentlyContinue | Measure-Object).Count
    $lstmfCount = (Get-ChildItem "$WorkDir\training_output\ground_truth\*.lstmf" -ErrorAction SilentlyContinue | Measure-Object).Count
    
    Write-Host "📦 Generation Status:" -ForegroundColor Green
    Write-Host "   Box Files: $boxCount / 54" -ForegroundColor $(if ($boxCount -eq 54) { "Green" } else { "Yellow" })
    Write-Host "   LSTMF Files: $lstmfCount / 54" -ForegroundColor $(if ($lstmfCount -eq 54) { "Green" } else { "Yellow" })
    Write-Host ""
    
    # Training status for all three models
    Write-Host "🏋️  Training Status:" -ForegroundColor Green
    Write-Host ""
    
    $models = @(
        @{ Name = "Farsi (fas)"; Log = "$LogDir\training_fas.log" }
        @{ Name = "Arabic (ara)"; Log = "$LogDir\training_ara.log" }
        @{ Name = "English (eng)"; Log = "$LogDir\training_eng.log" }
    )
    
    $allStatus = @()
    foreach ($model in $models) {
        $status = Get-TrainingStatus -LogFile $model.Log -ModelName $model.Name
        $allStatus += $status
        
        $statusColor = switch ($status.Status) {
            "✅ Completed" { "Green" }
            "Training" { "Cyan" }
            "Running" { "Yellow" }
            default { "Gray" }
        }
        
        Write-Host "  ┌─ $($status.Model)" -ForegroundColor $statusColor
        Write-Host "  │  Status: $($status.Status)" -ForegroundColor $statusColor
        
        if ($status.Status -eq "Training") {
            Write-Host "  │  Progress: $($status.Iteration) / $($status.MaxIter) ($($status.Progress)%)" -ForegroundColor $statusColor
            Write-Host "  │  BCER: $($status.BCER)" -ForegroundColor $statusColor
            
            if ($status.TimeElapsed) {
                Write-Host "  │  Elapsed: $($status.TimeElapsed)" -ForegroundColor $statusColor
            }
            if ($status.TimeRemaining -and $status.TimeRemaining -ne "N/A") {
                Write-Host "  │  Remaining: $($status.TimeRemaining)" -ForegroundColor $statusColor
            }
            if ($status.ETA -and $status.ETA -ne "N/A") {
                Write-Host "  │  ETA: $($status.ETA)" -ForegroundColor $statusColor
            }
            
            # Progress bar
            $barWidth = 50
            $filled = [math]::Floor($barWidth * $status.Progress / 100)
            $empty = $barWidth - $filled
            $bar = "█" * $filled + "░" * $empty
            Write-Host "  │  [$bar] $($status.Progress)%" -ForegroundColor $statusColor
        } elseif ($status.Status -eq "✅ Completed") {
            Write-Host "  │  Final BCER: $($status.BCER)" -ForegroundColor Green
        }
        
        Write-Host "  └─" -ForegroundColor $statusColor
        Write-Host ""
    }
    
    # Overall progress
    $completedModels = ($allStatus | Where-Object { $_.Status -eq "✅ Completed" }).Count
    $trainingModels = ($allStatus | Where-Object { $_.Status -eq "Training" }).Count
    
    Write-Host "📊 Overall Progress:" -ForegroundColor Magenta
    Write-Host "   Completed Models: $completedModels / 3" -ForegroundColor $(if ($completedModels -eq 3) { "Green" } else { "Yellow" })
    Write-Host "   Training Models: $trainingModels" -ForegroundColor Cyan
    Write-Host ""
    
    # Check for output models
    $bestModel = Test-Path "$ModelDir\ckb_from_fas.traineddata"
    $fastModel = Test-Path "$ModelDir\ckb_from_fas_fast.traineddata"
    
    if ($bestModel -or $fastModel) {
        Write-Host "✅ Output Models:" -ForegroundColor Green
        if ($bestModel) {
            $size = [math]::Round((Get-Item "$ModelDir\ckb_from_fas.traineddata").Length / 1MB, 2)
            Write-Host "   ckb_from_fas.traineddata ($size MB)" -ForegroundColor Green
        }
        if ($fastModel) {
            $size = [math]::Round((Get-Item "$ModelDir\ckb_from_fas_fast.traineddata").Length / 1MB, 2)
            Write-Host "   ckb_from_fas_fast.traineddata ($size MB)" -ForegroundColor Green
        }
        Write-Host ""
    }
    
    # Corpus stats
    Write-Host "📚 Corpus Statistics:" -ForegroundColor Blue
    $ckbLines = (Get-Content "$WorkDir\corpus\ckb.training_text" -ErrorAction SilentlyContinue | Measure-Object).Count
    $latinLines = (Get-Content "$WorkDir\corpus\ckb_latin.training_text" -ErrorAction SilentlyContinue | Measure-Object).Count
    $mixedLines = (Get-Content "$WorkDir\corpus\ckb_mixed.training_text" -ErrorAction SilentlyContinue | Measure-Object).Count
    
    Write-Host "   Arabic Script: $ckbLines lines" -ForegroundColor Blue
    Write-Host "   Latin Script: $latinLines lines" -ForegroundColor Blue
    Write-Host "   Mixed Script: $mixedLines lines" -ForegroundColor Blue
    Write-Host "   Total: $($ckbLines + $latinLines + $mixedLines) lines" -ForegroundColor Blue
    Write-Host ""
    
    if ($Continuous) {
        Write-Host "🔄 Auto-refresh enabled (every $RefreshSeconds seconds)" -ForegroundColor Yellow
        Write-Host "   Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
    } else {
        Write-Host "💡 Tip: Run with -Continuous to auto-refresh" -ForegroundColor DarkGray
        Write-Host "   Example: .\monitor_training.ps1 -Continuous -RefreshSeconds 60" -ForegroundColor DarkGray
    }
}

# Main execution
if ($Continuous) {
    while ($true) {
        Show-TrainingDashboard
        Start-Sleep -Seconds $RefreshSeconds
    }
} else {
    Show-TrainingDashboard
}
