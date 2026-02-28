# 🔥 ThinkBaby - AI + Bot + IVR Layer

Web3-based decentralized fake news verification protocol for hackathon.

**Track:** Web3 | **Team Role:** AI + Bot + IVR Lead

---

## 📋 Overview

This repository contains the **AI + Bot + IVR layer** for the ThinkBaby fake news verification system. It handles:

- ✅ **Claim Extraction** using AI-powered analysis
- ✅ **Risk Scoring** (0-100 scale)
- ✅ **Hash Generation** (keccak256 compatible with Solidity)
- ✅ **Backend API Integration** (connects to blockchain via REST API)
- ✅ **WhatsApp Bot** (Twilio integration)
- ✅ **IVR Voice System** (Speech-to-text verification)

---

## 🏗️ Architecture

```
User
  ↓
WhatsApp Bot / IVR / Website
  ↓
AI + Bot Layer (THIS REPO)
  ↓
Backend API
  ↓
Smart Contract (Ethereum Sepolia)
  ↓
Blockchain
```

**Important:** This layer does NOT interact with blockchain directly. All blockchain operations go through the Backend API.

---

## 📁 Project Structure

```
thinkbaby/
├── modules/
│   ├── claimExtractor.js      # AI claim analysis & risk scoring
│   ├── hashGenerator.js       # keccak256 hash generation
│   └── backendClient.js       # Backend API integration
├── bots/
│   └── whatsapp-bot.js        # WhatsApp bot handler (Twilio)
├── ivr/
│   └── ivr-handler.js         # IVR voice handler (Twilio)
├── utils/
│   └── formatter.js           # Response formatting
├── config/
│   └── env.js                 # Environment configuration
├── index.js                   # Main entry point & tests
├── package.json               # Dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Backend API (provided by backend team)
BACKEND_API_URL=http://localhost:3000/api

# Twilio Credentials (get from https://console.twilio.com/)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

### 3. Test the System

```bash
npm start
```

This will run system tests to verify all modules are working.

### 4. Start WhatsApp Bot

```bash
npm run whatsapp
```

Bot will run on `http://localhost:3001`

**Twilio Webhook URL:** `http://your-url/webhook/whatsapp`

### 5. Start IVR Handler

```bash
npm run ivr
```

IVR will run on `http://localhost:3002`

**Twilio Voice Webhook URL:** `http://your-url/ivr/incoming`

---

## 🔧 Module Documentation

### 1️⃣ Claim Extractor (`modules/claimExtractor.js`)

Analyzes messages to extract claims and calculate risk scores.

```javascript
const { analyzeMessage } = require('./modules/claimExtractor');

const result = await analyzeMessage('Government giving ₹5000 to students');

// Output:
{
  claims: ["Government giving ₹5000 to students"],
  riskScore: 82,
  explanation: "High-risk content detected. Contains government-related claims...",
  timestamp: "2026-02-28T10:30:00.000Z"
}
```

**Risk Scoring Logic:**
- Base: 50 (neutral)
- Urgent language: +15
- Financial claims: +20
- Government claims: +10
- Viral patterns: +25
- All caps: +10
- Excessive punctuation: +10

### 2️⃣ Hash Generator (`modules/hashGenerator.js`)

Generates keccak256 hashes compatible with Solidity smart contracts.

```javascript
const { generateClaimHash } = require('./modules/hashGenerator');

const hash = generateClaimHash('Government scheme announced');

// Output: "0x1234abcd..." (keccak256 hash)
```

**Important:** Hash must match exactly with Solidity `keccak256(abi.encodePacked(string))`.

### 3️⃣ Backend Client (`modules/backendClient.js`)

Integrates with backend REST API.

```javascript
const { 
  submitClaimToBackend,
  getClaimResult,
  voteTrue,
  voteFalse
} = require('./modules/backendClient');

// Submit new claim
await submitClaimToBackend(claimHash, claimText);

// Get result
const result = await getClaimResult(claimHash);
// { trueVotes: 5, falseVotes: 2, status: "Likely True" }

// Vote
await voteTrue(claimHash);
await voteFalse(claimHash);
```

### 4️⃣ WhatsApp Bot (`bots/whatsapp-bot.js`)

Handles WhatsApp messages via Twilio.

**Flow:**
1. User sends message
2. Bot analyzes message
3. Generates claim hash
4. Checks if claim exists in blockchain
5. If not exists → submits claim
6. Fetches result
7. Returns formatted report

**Commands:**
- `hi` / `hello` / `start` → Welcome message
- `help` → Help instructions
- Any other text → Claim verification

### 5️⃣ IVR Handler (`ivr/ivr-handler.js`)

Handles voice calls via Twilio.

**Flow:**
1. User calls
2. System prompts for claim
3. Speech-to-text conversion
4. Analyzes claim
5. Returns voice verdict (under 12 seconds)

**Voice Responses:**
- "This claim appears to be true."
- "This claim appears to be false."
- "This claim is currently under review."

---

## 🔌 API Endpoints

### WhatsApp Bot Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhook/whatsapp` | Twilio webhook for incoming messages |
| GET | `/health` | Health check |

### IVR Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ivr/incoming` | Twilio webhook for incoming calls |
| POST | `/ivr/process-claim` | Process spoken claim |
| POST | `/ivr/status` | Call status callback |
| GET | `/health` | Health check |

---

## 📊 Example Outputs

### WhatsApp Response

```
🔍 Claim Analysis

📝 Claim: Government giving ₹5000 to students

🤖 AI Risk Score: 82%

📊 Community Votes:
✅ True: 3
❌ False: 12

📋 Status: Likely False

💡 Explanation:
High-risk content detected. Contains government-related claims requiring verification. Contains financial claims. Verify through official sources.

---
⚡ Powered by ThinkBaby - Web3 Fact Verification
```

### IVR Voice Response

> "This claim appears to be false. Please verify from official sources."

---

## 🧪 Testing

### Test Individual Modules

```javascript
// Test claim extraction
const { analyzeMessage } = require('./modules/claimExtractor');
const result = await analyzeMessage('Test claim');

// Test hash generation
const { generateClaimHash } = require('./modules/hashGenerator');
const hash = generateClaimHash('Test claim');

// Test backend connection
const { healthCheck } = require('./modules/backendClient');
const isHealthy = await healthCheck();
```

### Test WhatsApp Bot (without Twilio)

```javascript
const { handleWhatsAppMessage } = require('./bots/whatsapp-bot');
const response = await handleWhatsAppMessage('Government scheme', '+1234567890');
console.log(response);
```

### Test IVR (without Twilio)

```javascript
const { processVoiceClaim } = require('./ivr/ivr-handler');
const response = await processVoiceClaim('Breaking news about prize');
console.log(response);
```

---

## 🔒 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NODE_ENV` | Environment (development/production) | No | development |
| `BACKEND_API_URL` | Backend API endpoint | Yes | http://localhost:3000/api |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | Yes | - |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | Yes | - |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp number | No | +14155238886 |
| `TWILIO_PHONE_NUMBER` | Twilio phone number for IVR | Yes | - |
| `WHATSAPP_BOT_PORT` | WhatsApp bot port | No | 3001 |
| `IVR_PORT` | IVR port | No | 3002 |

---

## 🌐 Deployment

### Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create thinkbaby-bot

# Set environment variables
heroku config:set BACKEND_API_URL=https://your-backend.com/api
heroku config:set TWILIO_ACCOUNT_SID=your_sid
heroku config:set TWILIO_AUTH_TOKEN=your_token

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Deploy to Railway/Render

1. Connect GitHub repository
2. Set environment variables in dashboard
3. Deploy automatically on push

---

## 🛠️ Troubleshooting

### WhatsApp Bot Not Responding

1. Check Twilio webhook URL is correct
2. Verify `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`
3. Check backend API is running
4. View logs: `heroku logs --tail`

### IVR Not Working

1. Check Twilio voice webhook URL
2. Verify phone number configuration
3. Test with Twilio debugger

### Backend Connection Failed

1. Check `BACKEND_API_URL` in `.env`
2. Test backend health: `curl http://backend-url/api/health`
3. Verify backend is running

---

## 📝 TODO / Future Enhancements

- [ ] Integrate OpenAI/Gemini for advanced claim extraction
- [ ] Add conversation history storage (MongoDB)
- [ ] Implement rate limiting
- [ ] Add multi-language support
- [ ] Create web dashboard for analytics
- [ ] Add user authentication

---

## 👥 Team

- **AI + Bot + IVR Lead:** (You)
- **Backend Developer:** Integrates smart contract
- **Blockchain Developer:** Writes & deploys smart contract
- **Frontend Developer:** Builds website UI

---

## 📜 License

MIT License - Built for Hackathon MVP

---

## 🎯 Hackathon Tips

✅ **Keep it simple** - This is an MVP  
✅ **Modular code** - Easy to debug and demo  
✅ **Error handling** - Graceful failures  
✅ **Clear logs** - Easy to troubleshoot  
✅ **Good documentation** - Judges love it!

---

## 📧 Support

For issues or questions, check logs first:

```bash
# WhatsApp Bot logs
npm run whatsapp

# IVR logs
npm run ivr
```

---

**Built with ❤️ for Web3 Hackathon**
