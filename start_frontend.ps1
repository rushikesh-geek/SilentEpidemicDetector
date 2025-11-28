# Start Frontend Server
Write-Host "========================================" -ForegroundColor Magenta
Write-Host " Silent Epidemic Detector - Frontend" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

# Kill any process on port 3000
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    Write-Host "Stopping existing process on port 3000..." -ForegroundColor Yellow
    Get-NetTCPConnection -LocalPort 3000 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
    Start-Sleep -Seconds 2
}

Set-Location -Path "D:\MumbaiHackss\frontend"

Write-Host "Dashboard:       http://localhost:3000" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

npm run dev
