# Decentralized Claim Registry (Sepolia)

Minimal blockchain layer for fake-news claim verification:
- deterministic `keccak256` claim hashes
- on-chain claim registration
- wallet-based true/false voting
- public vote reads

No token, NFT, DAO, admin controls, or backend voting.

## Contract Versions

- `contracts/ClaimRegistry.sol` (V1): open voting, no role separation
- `contracts/ClaimRegistryV2.sol` (V2): on-chain role checks (`User` vs `Validator`)

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

## V2 Contract (Role-Enforced)

Path: `contracts/ClaimRegistryV2.sol`

Role registration:
- `registerAsUser()`
- `registerAsValidator()`
- `getRole(address _account) returns (Role)`

Claim flow:
- `registerClaim(bytes32 _claimHash)` (User only)
- `claimExists(bytes32 _claimHash) returns (bool)`
- `getClaimSubmitter(bytes32 _claimHash) returns (address)`

Voting flow:
- `voteTrue(bytes32 _claimHash)` (Validator only)
- `voteFalse(bytes32 _claimHash)` (Validator only)
- `voteTrueValid(bytes32 _claimHash)` (alias)
- `voteFalseFake(bytes32 _claimHash)` (alias)
- `hasAddressVoted(bytes32 _claimHash, address _voter) returns (bool)`
- `getVotes(bytes32 _claimHash) returns (uint256 trueVotes, uint256 falseVotes)`
- `getValidatorVotes(bytes32 _claimHash) returns (uint256 validatorTrueVotes, uint256 validatorFalseVotes)`

V2 behavior:
- One role per wallet (`None`, `User`, `Validator`)
- Only users can register claims
- Only validators can vote
- Claim submitter cannot vote on their own claim
- Double voting prevented

## Deploy via Remix (Sepolia)

1. Open [Remix](https://remix.ethereum.org/).
2. Create `contracts/ClaimRegistryV2.sol` (or V1 if needed) and paste code from this repo.
3. Solidity compiler:
   - version: `0.8.20` (or any `^0.8.x` compatible)
   - compile contract
4. Deploy & Run:
   - environment: `Injected Provider - MetaMask`
   - network: `Sepolia`
   - deploy `ClaimRegistryV2`
5. Copy:
   - deployed contract address
   - ABI (from Remix compilation artifacts)

Share ABI + address with backend/frontend teammates.

## V2 Quick Test Script (Remix)

1. Wallet A: call `registerAsUser()`
2. Wallet A: call `registerClaim(hash)`
3. Wallet B: call `registerAsValidator()`
4. Wallet B: call `voteTrue(hash)` (or `voteTrueValid(hash)`)
5. Wallet C: call `registerAsValidator()`, then `voteFalse(hash)` (or `voteFalseFake(hash)`)
6. Call `getVotes(hash)` => should be `(1,1)`
7. Optional: call `getValidatorVotes(hash)` => should be `(1,1)`
8. Negative checks:
   - Wallet A attempts vote => revert (`NotValidator` / `SubmitterCannotVote`)
   - Wallet B votes same hash again => revert (`AlreadyVoted`)
   - Duplicate claim registration => revert (`ClaimAlreadyExists`)

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
