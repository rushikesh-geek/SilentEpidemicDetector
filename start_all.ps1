# Silent Epidemic Detector - Quick Start
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Silent Epidemic Detector - Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if ports are available
Write-Host "Checking ports..." -ForegroundColor Yellow

$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

if ($port8000) {
    Write-Host "⚠️  Port 8000 is in use. Stopping process..." -ForegroundColor Yellow
    Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
    Start-Sleep -Seconds 2
}

if ($port3000) {
    Write-Host "⚠️  Port 3000 is in use. Stopping process..." -ForegroundColor Yellow
    Get-NetTCPConnection -LocalPort 3000 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
    Start-Sleep -Seconds 2
}

Write-Host "✅ Ports available" -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "Starting Backend Server..." -ForegroundColor Cyan
$backendPath = "D:\MumbaiHackss\backend"
Set-Location $backendPath
$env:PYTHONPATH = $backendPath

$backendJob = Start-Job -ScriptBlock {
    param($path, $python)
    Set-Location $path
    $env:PYTHONPATH = $path
    & $python -m uvicorn main:app --host 0.0.0.0 --port 8000
} -ArgumentList $backendPath, "C:/Python313/python.exe"

Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✅ Backend running at http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend started but health check inconclusive" -ForegroundColor Yellow
    Write-Host "   Continuing anyway..." -ForegroundColor Yellow
}

Write-Host ""

# Start Frontend
Write-Host "Starting Frontend Server..." -ForegroundColor Cyan
$frontendPath = "D:\MumbaiHackss\frontend"
Set-Location $frontendPath

$frontendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    npm run dev
} -ArgumentList $frontendPath

Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

Write-Host "✅ Frontend running at http://localhost:3000" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host " 🎉 System is running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Dashboard:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "📚 API Docs:   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "❤️  Health:     http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Yellow
Write-Host ""

# Keep script running and show logs
try {
    while ($true) {
        $backendOutput = Receive-Job $backendJob -Keep
        $frontendOutput = Receive-Job $frontendJob -Keep
        
        if ($backendOutput) {
            Write-Host "[BACKEND] " -NoNewline -ForegroundColor Blue
            Write-Host $backendOutput
        }
        
        if ($frontendOutput) {
            Write-Host "[FRONTEND] " -NoNewline -ForegroundColor Magenta
            Write-Host $frontendOutput
        }
        
        Start-Sleep -Seconds 1
        
        # Check if jobs are still running
        if ($backendJob.State -ne 'Running') {
            Write-Host "❌ Backend stopped unexpectedly" -ForegroundColor Red
            break
        }
        if ($frontendJob.State -ne 'Running') {
            Write-Host "❌ Frontend stopped unexpectedly" -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host ""
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -Force -ErrorAction SilentlyContinue
    Write-Host "✅ All servers stopped" -ForegroundColor Green
}
