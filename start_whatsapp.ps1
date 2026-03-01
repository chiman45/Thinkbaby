# Start WhatsApp Bot with RAG
Write-Host "🚀 Starting WhatsApp RAG Bot v2.0..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (Test-Path ".venv") {
    Write-Host "✅ Activating virtual environment..." -ForegroundColor Yellow
    .\.venv\Scripts\Activate.ps1
} elseif (Test-Path "venv") {
    Write-Host "✅ Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
}

# Kill any process on port 3003
Write-Host "🔧 Freeing port 3003..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 3003 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 1

# Start the bot
Write-Host "📱 Starting WhatsApp RAG bot on port 3003..." -ForegroundColor Cyan
Write-Host "🔗 Webhook: /webhook or /webhook/whatsapp" -ForegroundColor Cyan
Write-Host "💚 Health: http://localhost:3003/health" -ForegroundColor Cyan
Write-Host ""
python whatsapp_rag.py
