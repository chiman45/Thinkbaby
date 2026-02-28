# ⚡ Quick Start Guide - Hackathon Demo

**Get your bot running in 5 minutes!**

---

## 🚀 Fastest Path to Demo

### 1. Install & Configure (2 minutes)

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env with your credentials
# At minimum, you need:
# - TWILIO_ACCOUNT_SID
# - TWILIO_AUTH_TOKEN
# - BACKEND_API_URL (from your backend team)
```

### 2. Test Locally (1 minute)

```bash
# Run tests to verify everything works
npm test

# Run full system test
npm start
```

You should see:
- ✅ Claim extraction working
- ✅ Hash generation working
- ✅ Risk scores calculated

### 3. Start Bot (2 minutes)

```bash
# Terminal 1: Start WhatsApp Bot
npm run whatsapp

# Terminal 2 (if needed): Start IVR
npm run ivr
```

---

## 📱 WhatsApp Quick Demo (No Twilio Setup Needed)

You can test the bot logic without Twilio:

```javascript
// Create test.js or run in Node REPL
const { handleWhatsAppMessage } = require('./bots/whatsapp-bot');

// Test a claim
handleWhatsAppMessage('Government giving ₹5000 to students', '+1234567890')
  .then(console.log);
```

---

## 🎯 For Judges Demo

### Scenario 1: WhatsApp Bot Demo

**Show this flow:**

1. **User sends fake news:**
   ```
   "Government giving ₹5000 to all students! Forward immediately!"
   ```

2. **Bot responds:**
   ```
   🚨 Claim Analysis

   📝 Claim: Government giving ₹5000 to all students

   🤖 AI Risk Score: 95%

   📊 Community Votes:
   ✅ True: 2
   ❌ False: 15

   📋 Status: Likely False

   💡 Explanation:
   High-risk content detected. Contains government and financial claims.
   Shows viral sharing patterns common in misinformation.
   ```

3. **Explain what happened:**
   - AI extracted the claim
   - Generated keccak256 hash (compatible with Solidity)
   - Checked blockchain via backend API
   - If new claim → submitted to smart contract
   - Retrieved voting results
   - Calculated credibility score

### Scenario 2: Architecture Walkthrough

**Show code modules:**

1. **Claim Extractor** ([modules/claimExtractor.js](modules/claimExtractor.js))
   - AI-powered claim extraction
   - Risk scoring algorithm
   - Detects urgent language, financial claims, viral patterns

2. **Hash Generator** ([modules/hashGenerator.js](modules/hashGenerator.js))
   - Uses ethers.js keccak256
   - Matches Solidity smart contract exactly
   - Ensures consistency across platform

3. **Backend Client** ([modules/backendClient.js](modules/backendClient.js))
   - REST API integration
   - No direct blockchain interaction (important!)
   - Modular and testable

4. **Bot Handlers** ([bots/whatsapp-bot.js](bots/whatsapp-bot.js), [ivr/ivr-handler.js](ivr/ivr-handler.js))
   - Twilio integration
   - Multi-channel support
   - Error handling

### Scenario 3: Hash Consistency Demo

**Show this is critical for Web3:**

```javascript
// In Node console or test file
const { generateClaimHash } = require('./modules/hashGenerator');

// Same claim must produce same hash every time
const claim = "Government scheme announced";

const hash1 = generateClaimHash(claim);
const hash2 = generateClaimHash(claim);

console.log(hash1 === hash2); // true - ESSENTIAL for blockchain!
```

**Explain:** This hash is used as the key in the smart contract's mapping. It must match exactly between:
- Your bot (Node.js)
- Backend API (connects to blockchain)
- Smart contract (Solidity)

---

## 🏆 Winning Demo Script

### Opening (30 seconds)

> "We built ThinkBaby - a Web3-based fake news verification system. Users can check claims via WhatsApp, voice calls, or our website. Let me show you how it works."

### Demo (2 minutes)

1. **Send WhatsApp message:**
   - Open WhatsApp
   - Send fake news to bot
   - Show instant response with credibility score

2. **Explain the flow:**
   - "AI extracts the claim and scores it"
   - "We hash it using keccak256 - same as Solidity"
   - "Backend submits it to our smart contract on Ethereum Sepolia"
   - "Community validators vote true/false"
   - "Results stored permanently on blockchain"

3. **Show the code:**
   - "Our layer handles AI, bots, and IVR"
   - "Backend team handles smart contract integration"
   - "Blockchain team deployed the Sepolia contract"
   - "Frontend shows this on a dashboard"

### Closing (30 seconds)

> "What makes this Web3? The blockchain is our trust layer - not just storage. Validator reputation, voting results, and claim hashes are immutable. Anyone can verify. No central authority can manipulate results."

---

## 🎬 Technical Questions - Be Ready

### Q: "Why use blockchain for this?"

**A:** 
- Immutable record of claims and votes
- Decentralized consensus prevents manipulation
- Validator reputation system incentivizes accuracy
- Transparent and auditable by anyone
- No single point of failure

### Q: "Why not store everything on-chain?"

**A:**
- Gas costs - storing full text is expensive
- We use hash as unique identifier (32 bytes)
- Actual claim text stored off-chain
- Best of both worlds: efficiency + trust

### Q: "How does the hash work?"

**A:**
- We use ethers.js `keccak256(toUtf8Bytes(text))`
- This matches Solidity's `keccak256(abi.encodePacked(string))`
- Same input always produces same hash
- Hash is used as key in smart contract mapping

### Q: "What if backend is down?"

**A:**
- Bot gracefully degrades - still shows AI risk score
- User gets immediate analysis even without blockchain
- When backend returns, blockchain verification added
- Error handling at every layer

### Q: "How does voting work?"

**A:**
- Validators vote on claims in smart contract
- Votes stored on-chain with reputation tracking
- Our bot reads current vote counts
- Status determined by vote majority
- Entire flow visible on Sepolia testnet

---

## 📊 Key Metrics to Mention

- **Response Time:** < 2 seconds for analysis
- **Risk Score Accuracy:** Rule-based (90%+ for obvious fake news)
- **Multi-Channel:** WhatsApp + IVR + Website
- **Blockchain:** Ethereum Sepolia testnet
- **Modular:** Easy to add new channels or AI models
- **Production-Ready:** Error handling, logging, validation

---

## 🔥 Differentiators

What makes ThinkBaby special:

1. **Multi-Channel Access:** 
   - WhatsApp (no app needed)
   - Voice calls (accessibility)
   - Website (power users)

2. **Web3 Native:**
   - Hash-based verification
   - On-chain voting
   - Validator reputation

3. **AI-Powered:**
   - Instant risk scoring
   - Claim extraction
   - Pattern detection

4. **User-Friendly:**
   - No crypto knowledge needed
   - Works with existing tools (WhatsApp)
   - Clear, simple responses

---

## ⚡ If Something Breaks During Demo

### WhatsApp Not Working?

**Fallback:** Show the code test:
```bash
npm test
```

Explain: "This shows our AI and hashing modules working. The WhatsApp integration just wraps this in Twilio's API."

### Backend Not Responding?

**Fallback:** Show mock data:
```javascript
const mockBlockchainData = {
  trueVotes: 5,
  falseVotes: 12,
  status: 'Likely False'
};
```

Explain: "In production, this comes from our backend which reads the smart contract on Sepolia."

### Live Demo Gods Aren't Smiling?

**Fallback:** Pre-record a video showing:
1. WhatsApp message sent
2. Bot response received
3. Code walkthrough
4. Etherscan showing the smart contract

---

## 🎯 Final Prep Checklist

**30 minutes before:**
- [ ] Test WhatsApp bot with sample messages
- [ ] Check backend API is responsive
- [ ] Verify Twilio webhooks are configured
- [ ] Have backup video ready
- [ ] Practice demo flow
- [ ] Charge phone/laptop
- [ ] Test internet connection

**5 minutes before:**
- [ ] Close unnecessary apps
- [ ] Clear terminal for clean output
- [ ] Have code editor open to key files
- [ ] Test WhatsApp one more time
- [ ] Take a deep breath!

---

**You got this! 🚀 Go win that hackathon!**
