# Backend V2 + IPFS Spec

This document defines how backend should build the response payload and IPFS snapshot for `ClaimRegistryV2`.

## Contract Source of Truth

- Contract: `ClaimRegistryV2`
- Contract functions used:
  - `claimExists(bytes32)`
  - `getVotes(bytes32)`
  - `getValidatorVotes(bytes32)`
  - `getClaimSubmitter(bytes32)`
  - `getRole(address)`

## Response Schema

Schema file:
- `schemas/analysis-response-v2.schema.json`

## Field Mapping

- `originalMessage`: user input text from request
- `claims[].claimText`: AI-cleaned claim text (or normalized input if single-claim flow)
- `claims[].claimHash`: `keccak256(normalized_claim_text)` from backend
- `claims[].aiRiskScore`: AI output (0-100)
- `claims[].aiConfidence`: AI output (0-1)
- `claims[].explanation`: AI output

`claims[].blockchain`:
- `contractVersion`: constant `"V2"`
- `contractAddress`: deployed V2 contract address
- `blockNumber`: `w3.eth.block_number` captured with vote read
- `existsOnChain`: `claimExists(hash)`
- `submitter`: `getClaimSubmitter(hash)` if exists, otherwise zero address
- `submitterRole`: `getRole(submitter)` mapped to `NONE|USER|VALIDATOR`
- `trueVotes`, `falseVotes`: `getVotes(hash)` if exists, else `0,0`
- `validatorTrueVotes`, `validatorFalseVotes`: `getValidatorVotes(hash)` if exists, else `0,0`
- `credibilityScore`: computed off-chain
  - formula: `trueVotes / (trueVotes + falseVotes)` when total > 0
  - if total = 0, recommended `0.5`
- `finalStatus`: computed off-chain rule
  - recommended:
    - `UNVERIFIED` if `existsOnChain == false`
    - `TRUE` if score > 0.6
    - `FALSE` if score < 0.4
    - `UNCERTAIN` otherwise

Top-level:
- `overallStatus`: aggregate from claims (single claim flow == claim finalStatus)
- `timestamp`: unix epoch seconds from backend
- `snapshot.snapshotHash`: deterministic keccak256 hash of canonical snapshot JSON
- `snapshot.ipfsCid`: CID string or `null` on upload failure
- `snapshot.ipfsPinned`: `true` when CID exists, else `false`

## Canonical Snapshot Rules

For deterministic `snapshotHash`:
1. Build one JSON object with stable key ordering.
2. Serialize with no extra whitespace.
3. UTF-8 encode and hash.

Python recommendation:
- `json.dumps(payload, sort_keys=True, separators=(",", ":"))`
- hash serialized bytes with keccak256.

## IPFS Behavior

- Upload snapshot JSON to Pinata.
- If Pinata fails:
  - do not fail request
  - return `ipfsCid: null`, `ipfsPinned: false`
  - still return `snapshotHash`

## Notes

- Backend must never store or use end-user private keys.
- Wallet-based voting remains frontend direct via MetaMask.
