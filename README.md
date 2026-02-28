# Decentralized Claim Registry (Sepolia)

Minimal blockchain layer for fake-news claim verification:
- deterministic `keccak256` claim hashes
- on-chain claim registration
- wallet-based true/false voting
- public vote reads

No token, NFT, DAO, admin controls, or backend voting.

## Contract

Path: `contracts/ClaimRegistry.sol`

Core methods:
- `registerClaim(bytes32 _claimHash)`
- `voteTrue(bytes32 _claimHash)`
- `voteFalse(bytes32 _claimHash)`
- `getVotes(bytes32 _claimHash) returns (uint256 trueVotes, uint256 falseVotes)`

Support methods:
- `claimExists(bytes32 _claimHash) returns (bool)`
- `hasAddressVoted(bytes32 _claimHash, address _voter) returns (bool)`

## Deploy via Remix (Sepolia)

1. Open [Remix](https://remix.ethereum.org/).
2. Create `contracts/ClaimRegistry.sol` and paste code from this repo.
3. Solidity compiler:
   - version: `0.8.20` (or any `^0.8.x` compatible)
   - compile contract
4. Deploy & Run:
   - environment: `Injected Provider - MetaMask`
   - network: `Sepolia`
   - deploy `ClaimRegistry`
5. Copy:
   - deployed contract address
   - ABI (from Remix compilation artifacts)

Share ABI + address with backend/frontend teammates.

## Deterministic Hashing Rules

Normalize claim text before hashing:
1. lowercase
2. trim leading/trailing spaces
3. collapse multiple spaces to a single space

Then hash normalized text with `keccak256`.

### Python (FastAPI/web3.py)

```python
import re
from web3 import Web3

def normalize_claim(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())

def claim_hash_hex(text: str) -> str:
    normalized = normalize_claim(text)
    return Web3.keccak(text=normalized).hex()
```

### JavaScript (ethers.js frontend)

```js
import { ethers } from "ethers";

export function normalizeClaim(text) {
  return text.toLowerCase().trim().replace(/\s+/g, " ");
}

export function claimHash(text) {
  return ethers.id(normalizeClaim(text)); // keccak256(utf8)
}
```

## Integration Flow

1. Backend receives raw claim text.
2. Backend normalizes + hashes claim.
3. Backend checks `claimExists(hash)`.
4. If false, backend sends `registerClaim(hash)` transaction.
5. Frontend reads `getVotes(hash)` and shows current totals.
6. User wallet votes directly:
   - `voteTrue(hash)` or `voteFalse(hash)` via MetaMask
7. Frontend refreshes `getVotes(hash)` to display on-chain result.

## Security Properties (as implemented)

- Duplicate claim registration reverts.
- Voting on non-existing claim reverts.
- Double voting by same wallet on same claim reverts.
- No admin wallet can change votes.
- Backend cannot cast votes unless it uses a wallet like any user.

## Suggested Demo Script

1. Submit claim text from UI.
2. Show normalized text + hash.
3. Register claim on Sepolia and show transaction hash.
4. Vote `true` from Wallet A.
5. Switch MetaMask account to Wallet B.
6. Vote `false` from Wallet B.
7. Refresh and show on-chain counts from `getVotes`.
8. Attempt duplicate vote from Wallet A and show revert.

