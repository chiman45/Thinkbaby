# 🧪 TEST WhatsApp Bot with Ollama

**Purpose:** Quick test to verify WhatsApp → ngrok → your server → Ollama is working

**Once this works, we'll integrate the full claim verification system!**

---

## 🚀 Quick Setup (5 Steps)

### Step 1: Install Ollama (if needed)

```powershell
# Download from: https://ollama.com/download
# Or if already installed, just start it:
ollama serve
```

### Step 2: Pull a Model

```powershell
# Recommended: llama3.2 (small and fast)
ollama pull llama3.2

# Or other options:
# ollama pull llama3
# ollama pull mistral
# ollama pull phi3
```

### Step 3: Start Test Server

```powershell
# Make sure virtual environment is active
.\.venv\Scripts\Activate.ps1

# Start the test server
python test_whatsapp_llm.py
```

**Server runs on:** `http://localhost:3001`

### Step 4: Start ngrok

```powershell
# In a NEW PowerShell window
ngrok http 3001
```

**You'll see something like:**
```
Forwarding  https://abc123.ngrok.io -> http://localhost:3001
```

**Copy the HTTPS URL:** `https://abc123.ngrok.io`

### Step 5: Configure Twilio Webhook

1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Scroll to **Sandbox Configuration**
3. Set "When a message comes in" to:
   ```
   https://abc123.ngrok.io/webhook/whatsapp
   ```
   (Replace `abc123` with your actual ngrok URL)
4. Click **Save**

---

## 📱 Test It!

### Send WhatsApp Message

1. Open WhatsApp
2. Send to: **+14155238886**
3. Send: `join <your-sandbox-code>`
4. Then try:
   - `hi` → Get welcome message
   - `test` → Verify everything is working
   - `What is fake news?` → Chat with Ollama
   - Any question → Ollama will respond!

---

## ✅ What This Tests

```
User (WhatsApp)
    ↓
Twilio (+14155238886)
    ↓
Internet
    ↓
ngrok (https://abc123.ngrok.io)
    ↓
Your Computer (localhost:3001)
    ↓
test_whatsapp_llm.py
    ↓
Ollama (localhost:11434)
    ↓
Response back to user!
```

---

## 🔍 Expected Flow

### 1. Send "hi"
**Response:**
```
👋 Hello! I'm your test bot powered by Ollama!

This is a TEST to verify WhatsApp → ngrok → your server is working.

Try asking me anything!
```

### 2. Send "test"
**Response:**
```
✅ TEST SUCCESSFUL!

Your WhatsApp bot is working perfectly:
✓ Twilio received your message
✓ Forwarded to ngrok tunnel
✓ Reached your local server
✓ Connected to Ollama

Everything is ready! 🎉
```

### 3. Send any question
**Response:** Ollama AI will respond with real conversation!

---

## 🐛 Troubleshooting

### Error: "Ollama is not running"

**Fix:**
```powershell
# Start Ollama in a terminal
ollama serve
```

### Error: "Model not found"

**Fix:**
```powershell
# Pull the model
ollama pull llama3.2
```

### WhatsApp not responding

**Check:**
1. Is test server running? `http://localhost:3001/health`
2. Is ngrok running? Should show forwarding URL
3. Is Twilio webhook correct? Should be `https://xxx.ngrok.io/webhook/whatsapp`
4. Did you join sandbox? Send `join xxx-xxx` first

### Check Server Status

Open browser: `http://localhost:3001/health`

**Should see:**
```json
{
  "server": "✅ Running",
  "ollama": "✅ Running",
  "model": "llama3.2"
}
```

---

## 📊 Terminal Output

When working correctly, you'll see:

```
============================================================
📱 WhatsApp Message Received
From: whatsapp:+1234567890
Message: What is fake news?
============================================================

[Ollama] Sending: What is fake news?
[Ollama] Response: Fake news refers to false or misleading information...

✅ Sent response: Fake news refers to false or misleading...
```

---

## 🎯 Once This Works

When you confirm WhatsApp chat is working:

1. ✅ You have: Twilio → ngrok → your server working
2. ✅ You have: Ollama LLM responding
3. ✅ Next step: Integrate full claim verification system
4. ✅ Replace simple chat with: claim analysis, hash generation, blockchain integration

---

## 🔄 Next Steps (After Testing)

Once this test works, we'll:

1. **Keep the working flow:** Twilio → ngrok → your server
2. **Replace test logic** with full system:
   - Claim extraction
   - Risk scoring
   - Hash generation
   - Backend API calls
   - Blockchain verification
3. **Keep Ollama** (optional) for advanced claim analysis
4. **Deploy** to production (Heroku/Railway)

---

## 🛑 Stop Test Server

When done testing:

```powershell
# Press Ctrl+C in the terminal running test_whatsapp_llm.py
# Press Ctrl+C in the terminal running ngrok
# Press Ctrl+C in the terminal running ollama serve
```

---

## 📝 Files Created for Testing

- `test_whatsapp_llm.py` - Test server with Ollama
- `TEST_SETUP.md` - This guide

**These are temporary for testing only!**

After confirmation, we'll use the full Python system:
- `bots/whatsapp_bot.py` - Full WhatsApp handler
- `modules/claim_extractor.py` - AI analysis
- `modules/hash_generator.py` - Blockchain hashing
- `modules/backend_client.py` - API integration

---

## 💡 Pro Tips

- Use `llama3.2` - it's smaller and faster for testing
- Keep all 3 terminals open: server, ngrok, ollama
- ngrok URL changes each restart (free tier)
- Update Twilio webhook each ngrok restart
- Watch server terminal for real-time logs

---

**Ready to test? Let's go! 🚀**

```powershell
# Terminal 1: Ollama
ollama serve

# Terminal 2: Test Server
python test_whatsapp_llm.py

# Terminal 3: ngrok
ngrok http 3001
```

Then configure Twilio and send a WhatsApp message!
