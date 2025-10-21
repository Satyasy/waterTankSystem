# Quick Start Script for IoT Dashboard
# Run this to automatically setup and launch the dashboard

Write-Host "🚀 IoT Water Tank Monitoring - Quick Start" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (!(Test-Path ".venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install/update dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip -q
pip install -r requirements.txt -q

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Check if CSV file exists
if (Test-Path "sensorWater.csv") {
    Write-Host "✅ Found sensorWater.csv" -ForegroundColor Green
} else {
    Write-Host "⚠️  Warning: sensorWater.csv not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 Starting Streamlit Dashboard..." -ForegroundColor Cyan
Write-Host "Dashboard will open in your browser at http://localhost:8501" -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Launch Streamlit
streamlit run dashboard.py
