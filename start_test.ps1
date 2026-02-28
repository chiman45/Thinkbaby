# Quick Test Script - Start Everything
Write-Host "🧪 Starting Test WhatsApp Bot with Ollama" -ForegroundColor Green
Write-Host ""

# Check if Ollama is running
Write-Host "Checking Ollama status..." -ForegroundColor Yellow
$ollamaRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Ollama is running!" -ForegroundColor Green
        $ollamaRunning = $true
    }
} catch {
    Write-Host "❌ Ollama is NOT running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start Ollama first:" -ForegroundColor Yellow
    Write-Host "  1. Open a new terminal" -ForegroundColor Cyan
    Write-Host "  2. Run: ollama serve" -ForegroundColor Cyan
    Write-Host ""
    
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit
    }
}

Write-Host ""

# Check if virtual environment exists
if (Test-Path ".venv") {
    Write-Host "✅ Activating virtual environment..." -ForegroundColor Yellow
    .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️  No virtual environment found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📱 Starting test WhatsApp bot on port 3001..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open another terminal" -ForegroundColor Cyan
Write-Host "  2. Run: ngrok http 3001" -ForegroundColor Cyan
Write-Host "  3. Copy the HTTPS URL from ngrok" -ForegroundColor Cyan
Write-Host "  4. Configure Twilio webhook with that URL + /webhook/whatsapp" -ForegroundColor Cyan
Write-Host "  5. Send WhatsApp message to test!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the test server
python test_whatsapp_llm.py
