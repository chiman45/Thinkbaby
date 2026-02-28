# Fake News Verification Backend

Decentralized fake news verification protocol backend for hackathon.

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required values:
- `SEPOLIA_RPC_URL`: Infura/Alchemy Sepolia endpoint
- `CONTRACT_ADDRESS`: Your deployed smart contract address
- `BACKEND_PRIVATE_KEY`: Private key for backend wallet (needs Sepolia ETH)
- `AI_SERVICE_URL`: Your teammate's AI service endpoint
- `PINATA_API_KEY`: Pinata API key
- `PINATA_SECRET_KEY`: Pinata secret key
- `CORS_ORIGINS`: Frontend URLs (comma-separated)

### 4. Update ABI

Replace `abi.json` with your actual smart contract ABI.

### 5. Get Sepolia ETH

Get test ETH for your backend wallet:
- https://sepoliafaucet.com/
- https://www.alchemy.com/faucets/ethereum-sepolia

Recommended: 0.5+ ETH for testing

## Run

```bash
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

API docs: http://localhost:8000/docs

## API Endpoints

### POST /claims/register

Register a new claim.

**Request:**
```json
{
  "text": "Your claim text here"
}
```

**Response (new claim):**
```json
{
  "status": "registered",
  "claim_hash": "0xabc123...",
  "tx_hash": "0xdef456...",
  "ipfs_cid": "QmXyz789...",
  "ai_analysis": {
    "ai_label": "False",
    "risk_score": 0.85,
    "summary": "Analysis summary"
  },
  "message": "Claim registered successfully. Transaction pending confirmation."
}
```

**Response (already exists):**
```json
{
  "status": "exists",
  "claim_hash": "0xabc123...",
  "message": "Claim already registered",
  "data": {
    "exists": true,
    "timestamp": 1234567890
  }
}
```

### GET /claims/{claim_hash}

Get claim data from blockchain.

**Response:**
```json
{
  "claim_hash": "0xabc123...",
  "on_chain_data": {
    "exists": true,
    "timestamp": 1234567890
  }
}
```

### GET /health

Health check.

**Response:**
```json
{
  "status": "ok",
  "service": "fake-news-verification-backend"
}
```

## Architecture

```
backend/
├── main.py              # FastAPI app
├── routes.py            # API endpoints
├── blockchain.py        # Web3 interaction
├── ai_connector.py      # AI service integration
├── ipfs.py             # Pinata IPFS upload
├── utils.py            # Text normalization + hashing
├── config.py           # Environment config
├── abi.json            # Smart contract ABI
├── .env                # Environment variables
└── requirements.txt    # Python dependencies
```

## Flow

1. User submits claim text
2. Backend normalizes text: `" ".join(text.lower().strip().split())`
3. Generate keccak256 hash: `Web3.keccak(text=normalized_text).hex()`
4. Check if claim exists on-chain
5. If not exists:
   - Call AI service for analysis
   - Upload to IPFS (Pinata)
   - Register claim on-chain (hash only, no CID)
   - Return tx_hash immediately (no receipt waiting)
6. Frontend polls GET /claims/{hash} to verify registration

## Important Notes

- **Hash matching:** Frontend and backend MUST use identical normalization
- **Transaction confirmation:** Backend returns tx_hash immediately, frontend must poll to verify
- **Race conditions:** Handled gracefully (re-checks claimExists if registerClaim reverts)
- **AI fallback:** Returns "Uncertain" if AI service fails
- **IPFS failure:** Registration aborted if IPFS upload fails
- **CID storage:** CID returned in response but NOT stored on-chain

## Testing

Test hash matching with frontend:

```python
from utils import normalize_text, hash_claim

# Test cases
test_cases = [
    "Hello World",
    "Multiple   spaces",
    "Newline\ntest",
    "  Leading and trailing  "
]

for text in test_cases:
    normalized = normalize_text(text)
    hash_value = hash_claim(text)
    print(f"Input: {repr(text)}")
    print(f"Normalized: {normalized}")
    print(f"Hash: {hash_value}\n")
```

Compare hashes with frontend to ensure matching.

## Troubleshooting

**"Cannot connect to Sepolia RPC"**
- Check SEPOLIA_RPC_URL in .env
- Verify Infura/Alchemy API key is valid

**"Low wallet balance"**
- Get more Sepolia ETH from faucet
- Backend needs ETH for gas fees

**"IPFS upload failed"**
- Check Pinata API keys
- Verify Pinata account is active

**"AI unavailable"**
- Check AI_SERVICE_URL
- Verify teammate's AI service is running
- Backend will use fallback values

**Transaction reverts**
- Check contract is deployed correctly
- Verify ABI matches contract
- Check claim doesn't already exist
