from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
import contract_wrapper
import ai_connector
import ipfs
from utils import hash_claim
from service_layer import generate_snapshot_hash
import time


router = APIRouter()


# In-memory storage for feed (hackathon mode)
# Maps claimHash -> claim metadata
claim_registry = {}


class ClaimRequest(BaseModel):
    text: str
    
    @validator('text')
    def validate_text(cls, v):
        stripped = v.strip()
        if len(stripped) < 10:
            raise ValueError("Claim must be at least 10 characters")
        if len(v) > 10000:
            raise ValueError("Claim too long (max 10,000 characters)")
        return v


class RegisterClaimRequest(BaseModel):
    claimHash: str
    newsContent: str
    submitterAddress: Optional[str] = None
    
    @validator('newsContent')
    def validate_content(cls, v):
        stripped = v.strip()
        if len(stripped) < 10:
            raise ValueError("Content must be at least 10 characters")
        if len(v) > 10000:
            raise ValueError("Content too long (max 10,000 characters)")
        return v


class AnalyzeRequest(BaseModel):
    claimHash: str
    callerAddress: Optional[str] = None


@router.post("/claims/register-content")
async def register_claim_content(request: RegisterClaimRequest):
    """
    Store claim content to IPFS after wallet registration.
    Called by frontend after successful on-chain registration.
    """
    claim_hash = request.claimHash
    
    # Verify claim exists on-chain
    if not contract_wrapper.claim_exists(claim_hash):
        raise HTTPException(
            status_code=400,
            detail="Claim not registered on-chain. Register via wallet first."
        )
    
    # Check if already stored in registry
    if claim_hash in claim_registry:
        existing = claim_registry[claim_hash]
        return {
            "claimHash": claim_hash,
            "contentCID": existing["contentCID"],
            "blockNumber": existing["blockNumber"],
            "claimSubmitter": existing["claimSubmitter"]
        }
    
    # Build claim content object
    claim_content = {
        "claimHash": claim_hash,
        "newsContent": request.newsContent,
        "submitter": request.submitterAddress or "unknown",
        "timestamp": int(time.time())
    }
    
    # Upload to IPFS
    try:
        content_cid = await ipfs.upload_to_pinata(claim_content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"IPFS upload failed: {str(e)}"
        )
    
    # Get current block number
    votes = contract_wrapper.get_votes(claim_hash)
    block_number = votes["block_number"]
    
    # Store in registry
    claim_registry[claim_hash] = {
        "claimHash": claim_hash,
        "contentCID": content_cid,
        "claimSubmitter": request.submitterAddress or "unknown",
        "blockNumber": block_number,
        "timestamp": int(time.time())
    }
    
    return {
        "claimHash": claim_hash,
        "contentCID": content_cid,
        "blockNumber": block_number,
        "claimSubmitter": request.submitterAddress or "unknown"
    }


@router.post("/analyze-claim")
async def analyze_claim_endpoint(request: AnalyzeRequest):
    """
    Analyze a claim using claimHash.
    Fetches content from IPFS, gets blockchain data, runs AI analysis.
    No credibility computation, no finalStatus, no threshold logic.
    """
    claim_hash = request.claimHash
    
    # 1. Check if claim exists on-chain
    exists = contract_wrapper.claim_exists(claim_hash)
    
    if not exists:
        raise HTTPException(
            status_code=404,
            detail="Claim not found on blockchain"
        )
    
    # 2. Get claim content from registry
    if claim_hash not in claim_registry:
        raise HTTPException(
            status_code=404,
            detail="Claim content not found. Content must be registered via /claims/register-content"
        )
    
    claim_metadata = claim_registry[claim_hash]
    content_cid = claim_metadata["contentCID"]
    
    # 3. Fetch claim text from IPFS
    try:
        claim_content = await ipfs.fetch_from_pinata(content_cid)
        news_content = claim_content.get("newsContent", "")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch content from IPFS: {str(e)}"
        )
    
    # 4. Fetch votes from blockchain
    user_votes = contract_wrapper.get_votes(claim_hash)
    validator_votes = contract_wrapper.get_validator_votes(claim_hash)
    block_number = user_votes["block_number"]
    
    # 5. Get AI analysis (claim text only)
    ai_output = await ai_connector.analyze_claim(news_content)
    
    # 6. Build snapshot (no credibility, no finalStatus)
    snapshot = {
        "claimHash": claim_hash,
        "newsContent": news_content,
        "userVotes": {
            "true": user_votes["true_votes"],
            "false": user_votes["false_votes"]
        },
        "validatorVotes": {
            "true": validator_votes["true_votes"],
            "false": validator_votes["false_votes"]
        },
        "blockNumber": block_number,
        "aiOutput": ai_output
    }
    
    # 7. Generate snapshot hash (deterministic)
    snapshot_hash = generate_snapshot_hash(snapshot)
    
    # 8. Attempt IPFS upload (non-blocking)
    snapshot_cid = None
    try:
        snapshot_cid = await ipfs.upload_to_pinata(snapshot)
    except Exception as e:
        print(f"Snapshot IPFS upload failed (non-blocking): {e}")
    
    # 9. Get role metadata if caller provided
    caller_role = None
    has_voted = False
    claim_submitter = claim_metadata["claimSubmitter"]
    
    if request.callerAddress:
        caller_role = contract_wrapper.get_role(request.callerAddress)
        has_voted = contract_wrapper.has_address_voted(claim_hash, request.callerAddress)
    
    # 10. Build final response (raw vote counts only)
    return {
        "claimHash": claim_hash,
        "newsContent": news_content,
        "userTrueVotes": user_votes["true_votes"],
        "userFalseVotes": user_votes["false_votes"],
        "validatorTrueVotes": validator_votes["true_votes"],
        "validatorFalseVotes": validator_votes["false_votes"],
        "blockNumber": block_number,
        "aiOutput": ai_output,
        "snapshotHash": snapshot_hash,
        "snapshotCID": snapshot_cid,
        "callerRole": caller_role,
        "hasVoted": has_voted,
        "claimSubmitter": claim_submitter,
        "timestamp": int(time.time())
    }


@router.get("/feed")
async def get_feed():
    """
    Get all registered claims for feed display.
    Returns list of claims with raw vote counts only.
    No AI calls, no IPFS fetch, no credibility computation.
    """
    feed_items = []
    
    for claim_hash, metadata in claim_registry.items():
        try:
            # Get current vote counts from blockchain
            user_votes = contract_wrapper.get_votes(claim_hash)
            validator_votes = contract_wrapper.get_validator_votes(claim_hash)
            
            feed_items.append({
                "claimHash": claim_hash,
                "contentCID": metadata["contentCID"],
                "claimSubmitter": metadata["claimSubmitter"],
                "timestamp": metadata["timestamp"],
                "blockNumber": metadata["blockNumber"],
                "userTrueVotes": user_votes["true_votes"],
                "userFalseVotes": user_votes["false_votes"],
                "validatorTrueVotes": validator_votes["true_votes"],
                "validatorFalseVotes": validator_votes["false_votes"]
            })
        except Exception as e:
            # Log error and skip this claim - do not crash entire feed
            print(f"ERROR: Failed to fetch votes for claim {claim_hash}: {str(e)}")
            continue
    
    # Sort by timestamp descending (newest first)
    feed_items.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "claims": feed_items,
        "total": len(feed_items)
    }



@router.get("/claims/{claim_hash}/detail")
async def get_claim_detail(claim_hash: str, caller_address: Optional[str] = None):
    """
    Get claim detail page data WITHOUT running AI.
    Returns claim text and raw vote counts only.
    AI analysis must be triggered separately via POST /analyze-claim.
    """
    # Validate hash format
    if not claim_hash.startswith('0x') or len(claim_hash) != 66:
        raise HTTPException(
            status_code=400,
            detail="Invalid hash format. Expected 0x followed by 64 hex characters."
        )
    
    try:
        bytes.fromhex(claim_hash[2:])
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid hash format. Hash must contain only hexadecimal characters."
        )
    
    # Check if claim exists on-chain
    exists = contract_wrapper.claim_exists(claim_hash)
    
    if not exists:
        raise HTTPException(
            status_code=404,
            detail="Claim not found on blockchain"
        )
    
    # Get claim content from registry
    if claim_hash not in claim_registry:
        raise HTTPException(
            status_code=404,
            detail="Claim content not found. Content must be registered via /claims/register-content"
        )
    
    claim_metadata = claim_registry[claim_hash]
    content_cid = claim_metadata["contentCID"]
    
    # Fetch claim text from IPFS
    try:
        claim_content = await ipfs.fetch_from_pinata(content_cid)
        news_content = claim_content.get("newsContent", "")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch content from IPFS: {str(e)}"
        )
    
    # Get vote data using wrapper
    user_votes = contract_wrapper.get_votes(claim_hash)
    validator_votes = contract_wrapper.get_validator_votes(claim_hash)
    
    # Get role metadata if caller provided
    caller_role = None
    has_voted = False
    
    if caller_address:
        caller_role = contract_wrapper.get_role(caller_address)
        has_voted = contract_wrapper.has_address_voted(claim_hash, caller_address)
    
    return {
        "claimHash": claim_hash,
        "newsContent": news_content,
        "contentCID": content_cid,
        "claimSubmitter": claim_metadata["claimSubmitter"],
        "timestamp": claim_metadata["timestamp"],
        "blockNumber": claim_metadata["blockNumber"],
        "userTrueVotes": user_votes["true_votes"],
        "userFalseVotes": user_votes["false_votes"],
        "validatorTrueVotes": validator_votes["true_votes"],
        "validatorFalseVotes": validator_votes["false_votes"],
        "callerRole": caller_role,
        "hasVoted": has_voted
    }


@router.get("/claims/{claim_hash}")
async def get_claim(claim_hash: str):
    """
    Get claim data from blockchain.
    Returns raw vote counts only, no credibility computation.
    """
    # Validate hash format
    if not claim_hash.startswith('0x') or len(claim_hash) != 66:
        raise HTTPException(
            status_code=400,
            detail="Invalid hash format. Expected 0x followed by 64 hex characters."
        )
    
    try:
        bytes.fromhex(claim_hash[2:])
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid hash format. Hash must contain only hexadecimal characters."
        )
    
    # Get vote data using wrapper
    exists = contract_wrapper.claim_exists(claim_hash)
    user_votes = contract_wrapper.get_votes(claim_hash)
    validator_votes = contract_wrapper.get_validator_votes(claim_hash)
    
    return {
        "claim_hash": claim_hash,
        "exists": exists,
        "user_true_votes": user_votes["true_votes"],
        "user_false_votes": user_votes["false_votes"],
        "validator_true_votes": validator_votes["true_votes"],
        "validator_false_votes": validator_votes["false_votes"],
        "block_number": user_votes["block_number"]
    }


@router.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {
        "status": "ok",
        "service": "fake-news-verification-backend"
    }
