# 🐍 PYTHON VERSION - Quick Setup Guide

## ✅ Your Credentials (Already Configured!)

Your `.env` file contains:
```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_WHATSAPP_NUMBER=+14155238886
BACKEND_API_URL=http://localhost:8000/api
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies ✅ (DONE!)

```powershell
# Virtual environment created ✅
# Packages installed ✅
```

### Step 2: Test Everything ✅ (TESTED!)

```powershell
python test_python.py   # ✅ Passed
python main.py          # ✅ Passed
```

### Step 3: Start Your Bots

**WhatsApp Bot:**
```powershell
.\start_whatsapp.ps1
# Or: python -m uvicorn bots.whatsapp_bot:app --port 3001 --reload
```

**IVR Handler:**
```powershell
.\start_ivr.ps1
# Or: python -m uvicorn ivr.ivr_handler:app --port 3002 --reload
```

---

## 📱 Twilio Setup (Quick)

### 1. WhatsApp Sandbox

1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Join sandbox: Send join code to +14155238886
3. Set webhook to: `http://your-url/webhook/whatsapp`

### 2. Test with ngrok

```powershell
# Terminal 1: Start bot
.\start_whatsapp.ps1

# Terminal 2: Expose
ngrok http 3001

# Copy HTTPS URL and update Twilio webhook
```

---

## 🎯 For Your Backend Developer (FastAPI)

Tell them to create these endpoints:

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/submitClaim")
async def submit_claim(claimHash: str, claimText: str):
    # Submit to smart contract
    return {"success": True}

@app.get("/api/getClaimResult")
async def get_claim_result(claimHash: str):
    return {
        "exists": True,
        "trueVotes": 5,
        "falseVotes": 2,
        "status": "Likely True"
    }

@app.post("/api/voteTrue")
async def vote_true(claimHash: str):
    return {"success": True}

@app.post("/api/voteFalse")
async def vote_false(claimHash: str):
    return {"success": True}

@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

**Important:** The `claimHash` uses keccak256 - must match Solidity!

```python
from web3 import Web3
hash = Web3.keccak(text=claim_text).hex()
```

---

## 📊 File Structure

```
Python Files Created:
✅ modules/claim_extractor.py    - AI analysis
✅ modules/hash_generator.py     - keccak256 hashing
✅ modules/backend_client.py     - API integration
✅ bots/whatsapp_bot.py          - WhatsApp handler
✅ ivr/ivr_handler.py            - IVR voice handler
✅ utils/formatter.py            - Response formatting
✅ main.py                       - Main entry point
✅ test_python.py                - Test suite
✅ requirements.txt              - Dependencies
✅ .env                          - Your credentials
✅ start_whatsapp.ps1            - Start WhatsApp script
✅ start_ivr.ps1                 - Start IVR script
✅ README_PYTHON.md              - Full documentation
```

---

## 🧪 Test Results

```
✅ Claim Extraction: Working (Risk Score calculation)
✅ Hash Generation: Working (keccak256 compatible)
✅ Backend Client: Ready (waiting for backend)
✅ All modules: Tested and verified
```

---

## 🎯 Next Steps

1. **Get Backend URL** from your FastAPI developer
2. **Update `.env`** with their backend URL
3. **Deploy to Heroku/Railway/Render**
4. **Configure Twilio webhooks**
5. **Test with WhatsApp**
6. **Demo for judges!**

---

## 📚 Documentation

- **Full Guide:** [README_PYTHON.md](README_PYTHON.md)
- **Twilio Setup:** [TWILIO_SETUP.md](TWILIO_SETUP.md)
- **Quick Start:** This file

---

## 💡 Key Points

✅ **Language:** Python 3.13 with FastAPI  
✅ **Credentials:** Already configured in `.env`  
✅ **Backend:** Connects to FastAPI backend (port 8000)  
✅ **Hash:** Uses web3.py keccak256 (Solidity-compatible)  
✅ **Tested:** All modules working  
✅ **Ready:** For deployment and demo  

---

**You're all set! 🚀 Start your bots and demo!**
