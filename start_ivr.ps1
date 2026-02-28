# Start IVR Handler
Write-Host "🚀 Starting IVR Handler..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "✅ Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
}

# Start the IVR
Write-Host "📞 Starting IVR handler on port 3002..." -ForegroundColor Cyan
Write-Host ""
python -m uvicorn ivr.ivr_handler:app --host 0.0.0.0 --port 3002 --reload
