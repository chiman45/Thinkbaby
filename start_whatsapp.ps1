# Start WhatsApp Bot
Write-Host "🚀 Starting WhatsApp Bot..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "✅ Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
}

# Start the bot
Write-Host "📱 Starting WhatsApp bot on port 3001..." -ForegroundColor Cyan
Write-Host ""
python -m uvicorn bots.whatsapp_bot:app --host 0.0.0.0 --port 3001 --reload
