# Start Backend Server
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Silent Epidemic Detector - Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any process on port 8000
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "Stopping existing process on port 8000..." -ForegroundColor Yellow
    Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
    Start-Sleep -Seconds 2
}

Set-Location -Path "D:\MumbaiHackss\backend"
$env:PYTHONPATH = "D:\MumbaiHackss\backend"

Write-Host "Backend API:     http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs:        http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Health Check:    http://localhost:8000/health" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

C:/Python313/python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
