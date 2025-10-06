# Training Progress Monitor
# Shows current training iteration and recent checkpoint CER

param(
    [switch]$Continuous,
    [int]$IntervalSeconds = 60
)

function Show-TrainingProgress {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "📊 Training Progress Monitor" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # Check if training is running
    $trainingLog = "work\training_output\logs\train_ckb.log"
    
    if (Test-Path $trainingLog) {
        # Get last 30 lines to find checkpoint info
        $lastLines = Get-Content $trainingLog -Tail 50 -ErrorAction SilentlyContinue
        
        # Find latest iteration
        $iterMatch = $lastLines | Select-String "At iteration (\d+)" | Select-Object -Last 1
        if ($iterMatch) {
            $iteration = $iterMatch.Matches.Groups[1].Value
            Write-Host "🔄 Current Iteration: " -NoNewline -ForegroundColor Yellow
            Write-Host "$iteration / 20000" -ForegroundColor White
            
            $progress = [math]::Round(($iteration / 20000) * 100, 2)
            Write-Host "📈 Progress: " -NoNewline -ForegroundColor Yellow
            Write-Host "$progress%" -ForegroundColor White
        }
        
        # Find latest CER values
        Write-Host "`n📉 Recent Checkpoints:" -ForegroundColor Green
        $cerLines = $lastLines | Select-String "char train=" | Select-Object -Last 3
        foreach ($line in $cerLines) {
            if ($line -match "At iteration (\d+).*char train=([\d.]+)") {
                $iter = $Matches[1]
                $cer = $Matches[2]
                Write-Host "  Iteration $iter`: CER = $cer%" -ForegroundColor White
            }
        }
        
        # Check for best checkpoint
        $bestMatch = $lastLines | Select-String "New best BCER = ([\d.]+)" | Select-Object -Last 1
        if ($bestMatch -and $bestMatch.Matches.Groups[1].Value) {
            $bestCer = $bestMatch.Matches.Groups[1].Value
            Write-Host "`n✨ Best CER so far: " -NoNewline -ForegroundColor Cyan
            Write-Host "$bestCer%" -ForegroundColor Green
        }
        
        # Estimate time remaining
        if ($iterMatch -and $iteration -gt 0) {
            $logFile = Get-Item $trainingLog
            $timeElapsed = (Get-Date) - $logFile.CreationTime
            $iterationsLeft = 20000 - $iteration
            $avgTimePerIter = $timeElapsed.TotalSeconds / $iteration
            $timeRemaining = [timespan]::FromSeconds($avgTimePerIter * $iterationsLeft)
            
            Write-Host "`n⏱️  Estimated time remaining: " -NoNewline -ForegroundColor Yellow
            Write-Host "$([math]::Floor($timeRemaining.TotalHours))h $($timeRemaining.Minutes)m" -ForegroundColor White
        }
        
    } else {
        Write-Host "❌ Training log not found. Training may not have started yet." -ForegroundColor Red
    }
    
    # Show recent models
    Write-Host "`n📦 Latest Models:" -ForegroundColor Magenta
    $models = Get-ChildItem "work\training_output\model\*.traineddata" -ErrorAction SilentlyContinue | 
              Sort-Object LastWriteTime -Descending | 
              Select-Object -First 3
    
    foreach ($model in $models) {
        $size = [math]::Round($model.Length / 1MB, 2)
        Write-Host "  $($model.Name) " -NoNewline -ForegroundColor White
        Write-Host "($size MB) " -NoNewline -ForegroundColor Gray
        Write-Host "- $($model.LastWriteTime.ToString('HH:mm:ss'))" -ForegroundColor DarkGray
    }
    
    Write-Host "`n========================================`n" -ForegroundColor Cyan
}

# Main execution
if ($Continuous) {
    Write-Host "🔄 Continuous monitoring enabled (Ctrl+C to stop)" -ForegroundColor Yellow
    Write-Host "Refresh interval: $IntervalSeconds seconds`n" -ForegroundColor Gray
    
    while ($true) {
        Clear-Host
        Show-TrainingProgress
        Start-Sleep -Seconds $IntervalSeconds
    }
} else {
    Show-TrainingProgress
}
