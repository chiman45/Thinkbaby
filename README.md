# Truth Protocol

A decentralized fake news verification system combining blockchain consensus, AI analysis, and community voting to combat misinformation.

## Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Voting Logic](#voting-logic)
- [Truth Matrix](#truth-matrix)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Folder Structure](#folder-structure)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)
- [License](#license)

## Project Overview

### What is Truth Protocol?

Truth Protocol is a Web3-based decentralized platform for verifying news claims through a combination of:

- Blockchain-based immutable claim registry
- AI-powered credibility analysis
- Community-driven voting consensus
- Role-based validation system

### Problem Statement

Misinformation spreads rapidly through social media and messaging platforms. Traditional fact-checking is centralized, slow, and often biased. Truth Protocol addresses this by:

- Creating an immutable record of claims on blockchain
- Enabling transparent community verification
- Providing AI-assisted risk assessment
- Preventing vote manipulation through on-chain validation

### Why Blockchain?

Blockchain provides:

- Immutable claim storage
- Transparent voting records
- Decentralized consensus mechanism
- Censorship resistance
- Cryptographic proof of submissions and votes

### System Goals

1. Enable rapid claim verification through community consensus
2. Provide AI-assisted credibility scoring for informed voting
3. Maintain transparent, auditable verification history
4. Prevent manipulation through role-based access control
5. Create a decentralized alternative to centralized fact-checkers

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   MetaMask   │  │  WalletConnect│  │  Web Wallet  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React + TypeScript + Vite                           │  │
│  │  - Wallet Integration (ethers.js)                    │  │
│  │  - State Management (TanStack Query)                 │  │
│  │  - UI Components (shadcn/ui + Radix)                 │  │
│  │  - Animations (Framer Motion)                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   Smart Contract Layer   │  │    Backend API Layer     │
│  ┌────────────────────┐  │  │  ┌────────────────────┐  │
│  │  ClaimRegistry.sol │  │  │  │  FastAPI + Python  │  │
│  │  - Role System     │  │  │  │  - AI Analysis     │  │
│  │  - Voting Logic    │  │  │  │  - IPFS Gateway    │  │
│  │  - Event Emission  │  │  │  │  - Contract Read   │  │
│  └────────────────────┘  │  │  └────────────────────┘  │
│   Ethereum Sepolia       │  │                          │
└──────────────────────────┘  └──────────────────────────┘
            │                              │
            │                              ▼
            │                  ┌──────────────────────────┐
            │                  │   AI Analysis Engine     │
            │                  │  ┌────────────────────┐  │
            │                  │  │ Credibility Engine │  │
            │                  │  │ - Source Scoring   │  │
            │                  │  │ - Linguistic Check │  │
            │                  │  │ - Anomaly Detect   │  │
            │                  │  │ - RAG Matching     │  │
            │                  │  └────────────────────┘  │
            │                  └──────────────────────────┘
            │                              │
            └──────────────┬───────────────┘
                           ▼
                ┌──────────────────────────┐
                │      IPFS Storage        │
                │  ┌────────────────────┐  │
                │  │  Pinata Gateway    │  │
                │  │  - Claim Content   │  │
                │  │  - Analysis Data   │  │
                │  └────────────────────┘  │
                └──────────────────────────┘
```

### Frontend Architecture

**Tech Stack:**
- React 18.3 with TypeScript
- Vite for build tooling
- TailwindCSS for styling
- shadcn/ui + Radix UI for components
- Framer Motion for animations

**State Management:**
- TanStack Query for server state
- React Context for wallet state
- Local state for UI interactions

**Wallet Integration:**
- ethers.js v6 for blockchain interaction
- MetaMask and WalletConnect support
- Custom WalletContext for connection management

**Contract Interaction Layer:**
```typescript
WalletContext
    ↓
ethers.js Provider/Signer
    ↓
Contract Instance (ABI + Address)
    ↓
Transaction Signing
    ↓
Blockchain (Sepolia)
```

**IPFS Integration:**
- Content stored via backend Pinata gateway
- CID retrieval for claim content
- Fallback handling for IPFS failures

**AI Analysis UI Layer:**
- TruthMatrix component for visualization
- Risk score circular progress indicators
- Mini meters for credibility and confidence
- Structured explanation display

### Backend Architecture

**Framework:**
- FastAPI (Python 3.10+)
- Uvicorn ASGI server
- Pydantic for data validation

**AI Analysis Pipeline:**
```
Claim Content
    ↓
Credibility Engine
    ├─ Source Credibility (25%)
    ├─ Linguistic Analysis (20%)
    ├─ Numerical Anomaly (15%)
    ├─ RAG Matching (20%)
    ├─ Temporal Analysis (10%)
    └─ Community Consensus (10%)
    ↓
Weighted Composite Score
    ↓
Verdict Classification
    ↓
Response (JSON)
```

**IPFS Content Retrieval:**
- Pinata gateway for content upload/fetch
- Non-blocking IPFS operations
- Graceful fallback on failures

**Endpoint Flow (analyze-claim):**
```
POST /api/ai-analysis
    ↓
Validate Request (Pydantic)
    ↓
Extract Claim Content
    ↓
Call Credibility Engine
    ├─ Multi-layer scoring
    ├─ Flag detection
    └─ Verdict generation
    ↓
Format Response
    ↓
Return JSON
```

**Error Handling Strategy:**
- Pydantic validation for request data
- Try-catch blocks for external services
- Graceful degradation for IPFS failures
- Detailed logging for debugging
- HTTP status codes for client errors

### Smart Contract Architecture

**Role System:**
```solidity
enum Role {
    None,      // 0 - Unregistered
    User,      // 1 - Can vote and submit claims
    Validator  // 2 - Trusted validators (future: weighted votes)
}
```

**Voting Mechanism:**
- Role-based voting functions
- One vote per address per claim
- Separate counters for user and validator votes
- Submitter cannot vote on own claim

**Custom Errors:**
```solidity
error NotRegistered(address caller);
error AlreadyVoted(address voter);
error ClaimNotFound(bytes32 claimHash);
error SubmitterCannotVote(address submitter);
```

**Event Emissions:**
```solidity
event ClaimRegistered(bytes32 indexed claimHash, address indexed submitter);
event Voted(address indexed voter, bytes32 indexed claimHash, bool vote);
event RoleAssigned(address indexed user, Role role);
```

**On-Chain Storage Structure:**
```solidity
struct Claim {
    address submitter;
    uint256 trueVotes;
    uint256 falseVotes;
    uint256 validatorTrueVotes;
    uint256 validatorFalseVotes;
    bool exists;
}

mapping(bytes32 => Claim) public claims;
mapping(address => Role) public roles;
mapping(bytes32 => mapping(address => bool)) public hasVoted;
```

### Data Flow

**Claim Registration:**
```
User Wallet
    ↓
Frontend: Hash claim content (keccak256)
    ↓
Frontend: Call contract.registerClaim(hash)
    ↓
Smart Contract: Store claim with submitter
    ↓
Frontend: Call backend /claims/register-content
    ↓
Backend: Upload content to IPFS
    ↓
Backend: Store CID in registry
```

**Voting Flow:**
```
User Wallet
    ↓
Frontend: Fetch role from contract
    ↓
Frontend: Validate (not submitter, not voted)
    ↓
Frontend: Call contract.voteTrue() or voteFalse()
    ↓
Smart Contract: Validate and record vote
    ↓
Frontend: Refetch vote counts
    ↓
UI: Update vote display
```

**AI Analysis Flow:**
```
User clicks "Analyze"
    ↓
Frontend: Fetch claim content from backend
    ↓
Frontend: Call /api/ai-analysis with content
    ↓
Backend: Pass to Credibility Engine
    ↓
Credibility Engine: Multi-layer analysis
    ↓
Backend: Return structured result
    ↓
Frontend: Display in Truth Matrix
```

## Key Features

### Decentralized Claim Registry

- Immutable on-chain storage of claim hashes
- Cryptographic proof of submission time and submitter
- Transparent voting history
- Event-based indexing for efficient retrieval

### Role-Based Access Control

- User role: Can submit claims and vote
- Validator role: Trusted validators (future weighted voting)
- On-chain role verification before actions
- Role assignment via wallet transactions

### AI-Powered Analysis

- Multi-layer credibility scoring (6 layers)
- Source verification against trusted domains
- Linguistic manipulation detection
- Numerical anomaly identification
- RAG-based fact matching
- Temporal analysis for breaking news

### Community Voting

- One vote per wallet per claim
- Separate tracking for user and validator votes
- Real-time vote count updates
- Submitter restriction to prevent self-voting

### IPFS Content Storage

- Decentralized content storage via Pinata
- Content addressable by CID
- Fallback handling for gateway failures
- Non-blocking operations

## Voting Logic

### Role-Based Voting

Users must be registered with a role before voting:

```typescript
// Check role on-chain
const role = await contract.getRole(walletAddress);

if (role === 0) {
  // Not registered - cannot vote
  throw new Error("Please register as User or Validator");
}

if (role === 1) {
  // User - use standard voting functions
  await contract.voteTrue(claimHash);
  // or
  await contract.voteFalse(claimHash);
}

if (role === 2) {
  // Validator - use validator voting functions
  await contract.voteTrueValid(claimHash);
  // or
  await contract.voteFalseValid(claimHash);
}
```

### Validator-Only Enforcement

The smart contract enforces role requirements:

```solidity
function voteTrue(bytes32 claimHash) external {
    if (roles[msg.sender] == Role.None) {
        revert NotRegistered(msg.sender);
    }
    // ... voting logic
}
```

### One Vote Per Claim

Each address can only vote once per claim:

```solidity
if (hasVoted[claimHash][msg.sender]) {
    revert AlreadyVoted(msg.sender);
}
hasVoted[claimHash][msg.sender] = true;
```

### Submitter Restrictions

Claim submitters cannot vote on their own claims:

```solidity
if (claims[claimHash].submitter == msg.sender) {
    revert SubmitterCannotVote(msg.sender);
}
```

Frontend validates this before transaction:

```typescript
const submitter = await contract.getClaimSubmitter(claimHash);
if (submitter.toLowerCase() === walletAddress.toLowerCase()) {
  throw new Error("You cannot vote on your own claim");
}
```

## Truth Matrix

The Truth Matrix combines AI analysis with on-chain consensus to provide comprehensive claim verification.

### Risk Score

**Range:** 0-100% (higher = more risky)

**Calculation:**
```
Risk Score = 1.0 - Credibility Score
```

**Visual Representation:**
- Circular progress indicator
- Color-coded (green = low risk, orange = medium, red = high)
- Animated fill proportional to percentage
- Gradient stroke with subtle glow

### Credibility Score

**Range:** 0-100% (higher = more credible)

**Weighted Composite:**
```
Credibility = 
    Source Score (25%) +
    Linguistic Score (20%) +
    Numerical Score (15%) +
    RAG Match Score (20%) +
    Temporal Score (10%) +
    Community Score (10%)
```

**Layers:**

1. **Source Score (25%):**
   - Tier 1 domains (government, Reuters, AP): 92%
   - Tier 2 domains (major news): 72%
   - Unknown sources: 35%

2. **Linguistic Score (20%):**
   - Detects clickbait patterns
   - Identifies urgency manipulation
   - Flags scheme impersonation
   - Checks for excessive caps/punctuation

3. **Numerical Score (15%):**
   - Identifies implausible amounts
   - Detects universal benefit claims
   - Flags extreme percentages

4. **RAG Match Score (20%):**
   - Matches against known fraud database
   - Verifies against official schemes
   - Keyword overlap analysis

5. **Temporal Score (10%):**
   - Breaking news flagged as unverified
   - Recycled old news detection
   - Date extraction and validation

6. **Community Score (10%):**
   - Blockchain vote consensus
   - Validator votes weighted 3x
   - Minimum 5 votes required

### Confidence

**Range:** 0-100%

**Calculation:**
```
Confidence = Platt Scaling + Source Boost
```

- Higher confidence with more evidence sources
- Calibrated using sigmoid transformation
- Increases with number of verified sources

### Signals

Detected red flags and indicators:

**Common Signals:**
- No verified source
- Clickbait language detected
- Urgency manipulation
- Scheme impersonation suspected
- Implausible amount
- Breaking news unverified
- No database match
- Insufficient community votes

### Verdict Classification

**Thresholds:**
- **TRUE** (≥72% credibility): Low risk, verified sources
- **UNCERTAIN** (48-71%): Medium risk, needs more evidence
- **FALSE** (<48%): High/critical risk, likely misinformation
- **BREAKING**: Unverified breaking news (pending verification)
- **UNVERIFIED**: No database match, no verified sources

### How AI + On-Chain Consensus Combine

**Complementary Verification:**

1. **AI Analysis (Immediate):**
   - Provides instant risk assessment
   - Identifies manipulation patterns
   - Flags suspicious content
   - Suggests verification needs

2. **On-Chain Consensus (Over Time):**
   - Community validation
   - Distributed verification
   - Transparent vote history
   - Immutable record

**Combined Display:**
```
┌─────────────────────────────────────┐
│         Truth Matrix                │
├─────────────────┬───────────────────┤
│  AI Analysis    │  On-Chain Votes   │
│                 │                   │
│  Risk: 32%      │  True: 68%        │
│  Cred: 68%      │  False: 32%       │
│  Conf: 67%      │                   │
│                 │  12 total votes   │
└─────────────────┴───────────────────┘
```

**Decision Making:**
- High AI risk + High false votes = Likely false
- Low AI risk + High true votes = Likely true
- Conflicting signals = Needs more investigation

## Installation

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- MetaMask or compatible Web3 wallet
- Sepolia testnet ETH

### Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your configuration
npm run dev
```

Frontend runs on `http://localhost:5173`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs on `http://localhost:8000`

### Smart Contract

Contract is already deployed on Sepolia testnet:

```
Contract Address: 0x4b69CC960F55B22714991Fd9De17115F72cC630b
Network: Ethereum Sepolia (Chain ID: 11155111)
```

ABI is located in `backend/abi.json`

## Environment Variables

### Frontend (.env.local)

```bash
# Vite requires VITE_ prefix for client-side variables
VITE_CONTRACT_ADDRESS=0x4b69CC960F55B22714991Fd9De17115F72cC630b
VITE_API_URL=http://localhost:8000
```

### Backend (.env)

```bash
# Blockchain Configuration
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
CONTRACT_ADDRESS=0x4b69CC960F55B22714991Fd9De17115F72cC630b
BACKEND_PRIVATE_KEY=your_wallet_private_key_here

# IPFS Configuration
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key
PINATA_GATEWAY=https://gateway.pinata.cloud

# AI Service (Optional - for fallback)
AI_SERVICE_URL=https://your-ai-service.com/analyze

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Required Services

**Infura (RPC Provider):**
1. Sign up at https://infura.io
2. Create a new project
3. Copy Sepolia endpoint URL

**Pinata (IPFS Gateway):**
1. Sign up at https://pinata.cloud
2. Generate API keys
3. Copy API key and secret

**Sepolia Testnet ETH:**
1. Get free testnet ETH from faucets:
   - https://sepoliafaucet.com
   - https://www.infura.io/faucet/sepolia

## Deployment

### Frontend Deployment (Vercel/Netlify)

**Vercel:**
```bash
npm install -g vercel
cd frontend
vercel
```

**Environment Variables:**
- Set `VITE_CONTRACT_ADDRESS` in Vercel dashboard
- Set `VITE_API_URL` to your backend URL

**Netlify:**
```bash
cd frontend
npm run build
# Upload dist/ folder to Netlify
```

### Backend Deployment (Railway/Render)

**Railway:**
1. Connect GitHub repository
2. Select backend folder as root
3. Set environment variables in dashboard
4. Deploy automatically on push

**Render:**
1. Create new Web Service
2. Connect repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

**Docker (Optional):**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist

- [ ] Update contract address in environment variables
- [ ] Configure CORS for production domains
- [ ] Set up SSL/TLS certificates
- [ ] Enable rate limiting on backend
- [ ] Configure CDN for frontend assets
- [ ] Set up monitoring and logging
- [ ] Test wallet connections on production
- [ ] Verify IPFS gateway accessibility

## Folder Structure

```
truth-protocol/
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── ui/            # shadcn/ui components
│   │   │   ├── TruthMatrix.tsx # AI analysis visualization
│   │   │   ├── VoteButtons.tsx # Voting interface
│   │   │   └── RoleRegistration.tsx # Role management
│   │   ├── context/           # React context providers
│   │   │   └── WalletContext.tsx # Wallet connection state
│   │   ├── pages/             # Route components
│   │   │   ├── Index.tsx      # Landing page
│   │   │   ├── CheckNews.tsx  # Claim submission
│   │   │   ├── ClaimFeed.tsx  # All claims list
│   │   │   └── ClaimDetail.tsx # Single claim view
│   │   ├── services/          # API integration
│   │   │   └── api.ts         # Backend API client
│   │   ├── utils/             # Utility functions
│   │   │   ├── constants.ts   # Contract ABI and address
│   │   │   ├── hash.ts        # Claim hashing logic
│   │   │   └── helpers.ts     # General helpers
│   │   └── main.tsx           # Application entry point
│   ├── public/                # Static assets
│   └── package.json           # Dependencies
│
├── backend/                    # Python FastAPI backend
│   ├── main.py                # Application entry point
│   ├── routes.py              # API endpoint definitions
│   ├── config.py              # Configuration management
│   ├── contract_wrapper.py    # Web3 contract interaction
│   ├── ai_connector.py        # AI analysis integration
│   ├── ipfs.py                # IPFS/Pinata integration
│   ├── event_indexer.py       # Blockchain event indexing
│   ├── service_layer.py       # Business logic
│   ├── utils.py               # Utility functions
│   ├── abi.json               # Smart contract ABI
│   └── requirements.txt       # Python dependencies
│
├── credibility_engine.py       # AI credibility scoring engine
├── .env.example               # Environment variables template
└── README.md                  # This file
```

### Key Directories

**frontend/src/components/:**
- Reusable React components
- UI library components (shadcn/ui)
- Feature-specific components (TruthMatrix, VoteButtons)

**frontend/src/context/:**
- React Context providers for global state
- WalletContext manages wallet connection and user state

**frontend/src/pages/:**
- Route-level components
- Each page corresponds to a URL route

**frontend/src/services/:**
- API integration layer
- Abstracts backend communication

**backend/:**
- FastAPI application
- Contract interaction via web3.py
- IPFS integration
- AI analysis pipeline

## Known Limitations

### Testnet Deployment

- Currently deployed on Ethereum Sepolia testnet
- Testnet ETH required for transactions
- Testnet may experience downtime or resets
- Not suitable for production use

### No Claim Editing

- Claims are immutable once registered
- Cannot update or delete submitted claims
- Typos or errors require new submission
- Design choice for integrity and auditability

### No Weighted Validator Scoring

- All validator votes currently have equal weight
- No reputation-based vote weighting
- Future enhancement planned

### IPFS Dependency

- Content retrieval depends on IPFS gateway availability
- Pinata gateway may experience downtime
- No redundant gateway fallback currently implemented

### Rate Limiting

- No rate limiting on backend endpoints
- Vulnerable to spam or DoS attacks
- Should be implemented before mainnet deployment

### Single Contract Instance

- All claims stored in one contract
- No sharding or scaling mechanism
- May face gas limits with high volume

## Future Improvements

### Reputation Weighting

**Planned Enhancement:**
- Track validator accuracy over time
- Weight votes based on historical performance
- Penalize malicious or inaccurate validators
- Reward consistent accurate validators

**Implementation:**
```solidity
struct ValidatorStats {
    uint256 correctVotes;
    uint256 totalVotes;
    uint256 reputationScore;
}

mapping(address => ValidatorStats) public validatorStats;
```

### Governance Layer

**Planned Features:**
- Community-driven parameter updates
- Validator approval/removal voting
- Threshold adjustment proposals
- Protocol upgrade governance

**Governance Token:**
- ERC-20 token for voting power
- Earned through participation
- Staked for validator status

### Validator Staking

**Economic Security:**
- Validators stake tokens to participate
- Slashing for malicious behavior
- Rewards for accurate verification
- Minimum stake requirement

**Staking Mechanism:**
```solidity
function stakeAsValidator() external payable {
    require(msg.value >= MINIMUM_STAKE, "Insufficient stake");
    validatorStakes[msg.sender] = msg.value;
    roles[msg.sender] = Role.Validator;
}
```

### Mainnet Deployment

**Production Readiness:**
- Comprehensive security audit
- Gas optimization
- Rate limiting implementation
- Multi-gateway IPFS redundancy
- Monitoring and alerting
- Incident response plan

**Deployment Targets:**
- Ethereum Mainnet
- Polygon for lower fees
- Optimism/Arbitrum for L2 scaling

### Additional Enhancements

**Multi-Language Support:**
- Internationalization (i18n)
- Support for non-English claims
- Localized UI

**Mobile Application:**
- React Native mobile app
- WalletConnect integration
- Push notifications for votes

**Advanced AI Features:**
- Image/video verification
- Deep fake detection
- Source link verification
- Automated fact-checking

**Analytics Dashboard:**
- Claim statistics
- Voting patterns
- Validator performance metrics
- Network health monitoring

**API for Third-Party Integration:**
- Public API for claim verification
- Webhook notifications
- Browser extension
- Social media integration

## License

MIT License

Copyright (c) 2026 Truth Protocol

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
