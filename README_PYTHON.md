# 🐍 ThinkBaby - Python Version

Web3-based decentralized fake news verification protocol - **AI + Bot + IVR Layer**

**Language:** Python 3.8+ | **Framework:** FastAPI | **Team Role:** AI + Bot + IVR Lead

---

## 🔥 Your Credentials (Already Configured!)

```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_WHATSAPP_NUMBER=+14155238886
```

✅ These are already in your `.env` file!

---

## 🚀 Quick Start (Python)

### 1. Install Python Dependencies

```powershell
# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Test the System

```powershell
# Run quick tests
python test_python.py

# Run full system test
python main.py
```

### 3. Start WhatsApp Bot

```powershell
# Method 1: Use PowerShell script
.\start_whatsapp.ps1

# Method 2: Direct command
python -m uvicorn bots.whatsapp_bot:app --host 0.0.0.0 --port 3001 --reload
```

Bot runs on: `http://localhost:3001`

**Twilio Webhook:** `http://your-url/webhook/whatsapp`

### 4. Start IVR Handler

```powershell
# Method 1: Use PowerShell script
.\start_ivr.ps1

# Method 2: Direct command
python -m uvicorn ivr.ivr_handler:app --host 0.0.0.0 --port 3002 --reload
```

IVR runs on: `http://localhost:3002`

**Twilio Voice Webhook:** `http://your-url/ivr/incoming`

---

## 📁 Project Structure (Python)

```
thinkbaby/
├── modules/
│   ├── claim_extractor.py     # ✅ AI claim analysis (Python)
│   ├── hash_generator.py      # ✅ keccak256 hashing (web3.py)
│   └── backend_client.py      # ✅ FastAPI backend integration
├── bots/
│   └── whatsapp_bot.py        # ✅ WhatsApp handler (FastAPI + Twilio)
├── ivr/
│   └── ivr_handler.py         # ✅ IVR voice handler (FastAPI + Twilio)
├── utils/
│   └── formatter.py           # ✅ Response formatting
├── main.py                    # ✅ Main entry point & tests
├── test_python.py             # ✅ Quick test suite
├── requirements.txt           # ✅ Python dependencies
├── .env                       # ✅ Your credentials (configured!)
├── start_whatsapp.ps1         # ✅ Start WhatsApp bot script
├── start_ivr.ps1              # ✅ Start IVR script
└── README_PYTHON.md           # ✅ This file
```

---

## 🔧 Module Documentation (Python)

### 1️⃣ Claim Extractor (`modules/claim_extractor.py`)

```python
from modules.claim_extractor import analyze_message

result = analyze_message("Government giving ₹5000 to students")

# Output:
{
    "claims": ["Government giving ₹5000 to students"],
    "riskScore": 82,
    "explanation": "High-risk content detected...",
    "timestamp": "2026-02-28T..."
}
```

### 2️⃣ Hash Generator (`modules/hash_generator.py`)

```python
from modules.hash_generator import generate_claim_hash

hash = generate_claim_hash("Government scheme announced")

# Output: "0x42beac..." (keccak256 hash)
```

**Critical:** Compatible with Solidity `keccak256(abi.encodePacked(string))`

### 3️⃣ Backend Client (`modules/backend_client.py`)

```python
from modules.backend_client import (
    submit_claim_to_backend,
    get_claim_result,
    vote_true,
    vote_false
)

# Submit claim
submit_claim_to_backend(claim_hash, claim_text)

# Get result
result = get_claim_result(claim_hash)
# {"trueVotes": 5, "falseVotes": 2, "status": "Likely True"}

# Vote
vote_true(claim_hash)
vote_false(claim_hash)
```

### 4️⃣ WhatsApp Bot (`bots/whatsapp_bot.py`)

FastAPI endpoint: `/webhook/whatsapp`

**Flow:**
1. Receive message from Twilio
2. Analyze with `analyze_message()`
3. Generate hash with `generate_claim_hash()`
4. Check blockchain via backend
5. Submit if new claim
6. Return formatted report

### 5️⃣ IVR Handler (`ivr/ivr_handler.py`)

FastAPI endpoint: `/ivr/incoming`

**Flow:**
1. User calls Twilio number
2. Twilio converts speech to text
3. Process claim (same as WhatsApp)
4. Generate short voice response
5. Speak result (< 12 seconds)

---

## 🌐 Backend Integration (FastAPI)

Your backend developer should create these endpoints:

### Required Endpoints

```python
# FastAPI Backend (your backend team's code)
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/submitClaim")
async def submit_claim(claimHash: str, claimText: str):
    # Submit to smart contract
    return {"success": True, "txHash": "0x..."}

@app.get("/api/getClaimResult")
async def get_claim_result(claimHash: str):
    # Read from smart contract
    return {
        "exists": True,
        "trueVotes": 5,
        "falseVotes": 2,
        "status": "Likely True"
    }

@app.post("/api/voteTrue")
async def vote_true(claimHash: str, voterAddress: str = None):
    # Record vote on blockchain
    return {"success": True}

@app.post("/api/voteFalse")
async def vote_false(claimHash: str, voterAddress: str = None):
    # Record vote on blockchain
    return {"success": True}

@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

### Your Backend URL

Update in `.env`:
```env
BACKEND_API_URL=http://localhost:8000/api
```

Or if deployed:
```env
BACKEND_API_URL=https://your-backend.com/api
```

---

## 🧪 Testing (Python)

### Test Individual Modules

```python
# Test claim extraction
from modules.claim_extractor import analyze_message
result = analyze_message("Test claim")

# Test hash generation
from modules.hash_generator import generate_claim_hash
hash = generate_claim_hash("Test claim")

# Test backend connection
from modules.backend_client import health_check
is_healthy = health_check()
```

### Run Test Suite

```powershell
python test_python.py
```

### Run Full System Test

```powershell
python main.py
```

---

## 📊 Example Output

### WhatsApp Response

```
🚨 Claim Analysis

📝 Claim: Government giving ₹5000 to students

🤖 AI Risk Score: 82%

📊 Community Votes:
✅ True: 3
❌ False: 12

📋 Status: Likely False

💡 Explanation:
High-risk content detected. Contains government-related claims...

---
⚡ Powered by ThinkBaby - Web3 Fact Verification
```

---

## 🔌 API Endpoints (Python/FastAPI)

### WhatsApp Bot

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhook/whatsapp` | Twilio webhook for messages |
| GET | `/health` | Health check |
| GET | `/` | Service info |

### IVR Handler

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ivr/incoming` | Twilio webhook for calls |
| POST | `/ivr/process-claim` | Process spoken claim |
| POST | `/ivr/status` | Call status callback |
| GET | `/health` | Health check |
| GET | `/` | Service info |

---

## 🚀 Deployment (Python)

### Option 1: Heroku

```powershell
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Create Procfile
echo "web: uvicorn bots.whatsapp_bot:app --host 0.0.0.0 --port $PORT" > Procfile

# Deploy
heroku create thinkbaby-python
heroku config:set TWILIO_ACCOUNT_SID=your_twilio_account_sid
heroku config:set TWILIO_AUTH_TOKEN=your_twilio_auth_token
heroku config:set BACKEND_API_URL=https://your-backend.com/api
git push heroku main
```

### Option 2: Railway/Render

1. Connect GitHub repository
2. Set Python runtime
3. Add environment variables
4. Deploy automatically

### Option 3: Local with ngrok

```powershell
# Terminal 1: Start WhatsApp bot
python -m uvicorn bots.whatsapp_bot:app --port 3001

# Terminal 2: Expose with ngrok
ngrok http 3001

# Copy ngrok URL and update Twilio webhook
# https://xxxxx.ngrok.io/webhook/whatsapp
```

---

## 📝 Requirements

### Python Version
- Python 3.8 or higher

### Key Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `twilio` - Twilio SDK
- `web3` - Ethereum/keccak256
- `requests` - HTTP client
- `python-dotenv` - Environment variables

### Install All
```powershell
pip install -r requirements.txt
```

---

## 🎯 For Your Backend Developer

Tell your FastAPI backend developer:

### 1. Required Endpoints

They need to create:
- `POST /api/submitClaim` - Submit claim to smart contract
- `GET /api/getClaimResult` - Get voting results
- `POST /api/voteTrue` - Vote true
- `POST /api/voteFalse` - Vote false
- `GET /api/health` - Health check

### 2. Hash Format

The `claimHash` you send is:
```python
from web3 import Web3
hash = Web3.keccak(text=claim_text).hex()
# Example: "0x42beac3951b925fd..."
```

This MUST match their Solidity smart contract:
```solidity
bytes32 claimHash = keccak256(abi.encodePacked(claimText));
```

### 3. Response Format

They should return:
```json
{
  "exists": true,
  "trueVotes": 5,
  "falseVotes": 2,
  "status": "Likely True"
}
```

---

## 🐛 Troubleshooting (Python)

### Import Errors

```powershell
# Make sure you're in virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### ModuleNotFoundError

```powershell
# Run from project root
cd d:\Programing\Projects\Thinkbaby
python main.py
```

### Port Already in Use

```powershell
# Find process using port
netstat -ano | findstr :3001

# Kill process
taskkill /PID <process_id> /F
```

### Web3 Installation Issues

```powershell
# Install build tools if needed
pip install web3 --no-cache-dir
```

---

## 📚 Quick Commands Reference

```powershell
# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Test
python test_python.py
python main.py

# Run WhatsApp Bot
.\start_whatsapp.ps1
# Or: python -m uvicorn bots.whatsapp_bot:app --port 3001 --reload

# Run IVR
.\start_ivr.ps1
# Or: python -m uvicorn ivr.ivr_handler:app --port 3002 --reload

# Check logs
# Logs appear in terminal where you started the service
```

---

## ✅ What's Ready

- [x] Python 3.8+ modules
- [x] FastAPI servers for WhatsApp & IVR
- [x] Twilio integration (Python SDK)
- [x] keccak256 hashing (web3.py)
- [x] Backend API client
- [x] Your credentials configured
- [x] Test suites
- [x] PowerShell start scripts
- [x] Complete documentation

---

## 🎯 Next Steps

1. **Install dependencies:** `pip install -r requirements.txt`
2. **Test:** `python test_python.py`
3. **Get backend URL** from your FastAPI backend developer
4. **Update `.env`** with backend URL
5. **Deploy** to Heroku/Railway/Render
6. **Configure Twilio webhooks**
7. **Demo!** 🚀

---

## 💡 Tips for Hackathon

- Use ngrok for local development
- Test with Twilio sandbox first
- Have backend developer's API ready
- Practice the demo flow
- Explain Web3 integration clearly
- Show the keccak256 hash matching

---

**Built with Python 🐍 for Web3 Hackathon**

Good luck! 🔥
