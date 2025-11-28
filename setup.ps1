# Setup script for Silent Epidemic Detector
# Run this script to install all dependencies

Write-Host "=== Silent Epidemic Detector - Setup Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Install backend dependencies
Write-Host ""
Write-Host "=== Installing Backend Dependencies ===" -ForegroundColor Cyan
Set-Location "$PSScriptRoot\backend"

if (Test-Path "requirements.txt") {
    Write-Host "Installing Python packages..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Backend dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install backend dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ requirements.txt not found" -ForegroundColor Red
    exit 1
}

# Install frontend dependencies
Write-Host ""
Write-Host "=== Installing Frontend Dependencies ===" -ForegroundColor Cyan
Set-Location "$PSScriptRoot\frontend"

if (Test-Path "package.json") {
    Write-Host "Installing Node packages..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Frontend dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install frontend dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ package.json not found" -ForegroundColor Red
    exit 1
}

# Return to root
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start MongoDB: docker run -d -p 27017:27017 --name mongodb mongo:latest"
Write-Host "2. Generate data: python scripts\simulate_data.py --days 120 --outbreak 1"
Write-Host "3. Import data: python scripts\import_data.py --dir .\data"
Write-Host "4. Start backend: cd backend; python main.py"
Write-Host "5. Start frontend: cd frontend; npm run dev"
Write-Host ""
