from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, validator
from typing import Optional
import contract_wrapper
import ai_connector
import ipfs
from utils import hash_claim
from service_layer import generate_snapshot_hash
import event_indexer
import time


router = APIRouter()


# In-memory storage for IPFS CIDs and claim content (backward compatibility)
# Maps claimHash -> CID, metadata, and ORIGINAL CONTENT
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


class RegisterClaimFullRequest(BaseModel):
    newsContent: str
    submitterAddress: str
    
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


class AIAnalysisRequest(BaseModel):
    content: str
    
    @validator('content')
    def validate_content(cls, v):
        stripped = v.strip()
        if not stripped:
            raise ValueError("Content cannot be empty")
        if len(v) > 10000:
            raise ValueError("Content too long (max 10,000 characters)")
        return v


@router.post("/api/ai-analysis")
async def ai_analysis_endpoint(request: AIAnalysisRequest):
    """
    Standalone AI analysis endpoint.
    Accepts content and returns Credibility Engine analysis.
    
    This endpoint does NOT require blockchain interaction.
    It's a direct pass-through to the AI service.
    
    CRITICAL: Validates content to prevent analyzing placeholder text.
    """
    try:
        # Validate content
        if not request.content or not request.content.strip():
            raise HTTPException(
                status_code=400,
                detail="Content is required and cannot be empty"
            )
        
        # Block placeholder text from being analyzed
        placeholder_patterns = [
            "[Content not available",
            "[content not available",
            "Content not available",
            "claim registered externally"
        ]
        
        content_lower = request.content.lower().strip()
        for pattern in placeholder_patterns:
            if pattern.lower() in content_lower:
                print(f"🚫 BLOCKED: Attempt to analyze placeholder text")
                raise HTTPException(
                    status_code=400,
                    detail="Cannot analyze placeholder content. Claim content is not available."
                )
        
        # Minimum content length check
        if len(request.content.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Content too short for meaningful analysis (minimum 10 characters)"
            )
        
        print(f"\n{'='*60}")
        print(f"🤖 AI ANALYSIS REQUEST RECEIVED")
        print(f"{'='*60}")
        print(f"📝 Content: {request.content[:100]}...")
        print(f"📝 Content length: {len(request.content)} chars")
        print(f"✅ Content validation passed")
        print(f"📤 Sending to Credibility Engine...")
        
        # Call Credibility Engine
        ai_result = await ai_connector.analyze_claim(request.content)
        
        print(f"✅ AI Analysis complete")
        print(f"   Label: {ai_result['ai_label']}")
        print(f"   Risk Score: {ai_result['risk_score']}")
        print(f"   Confidence: {ai_result.get('confidence', 'N/A')}")
        print(f"   Flags: {len(ai_result.get('flags', []))} detected")
        print(f"{'='*60}\n")
        
        # Return AI result
        return {
            "success": True,
            "analysis": {
                "ai_label": ai_result["ai_label"],
                "risk_score": ai_result["risk_score"],
                "summary": ai_result["summary"],
                "confidence": ai_result.get("confidence"),
                "flags": ai_result.get("flags"),
                "sources_found": ai_result.get("sources_found"),
                "risk_level": ai_result.get("risk_level")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ AI Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(e)}"
        )


@router.post("/claims/register")
async def register_claim_full(raw_request: Request):
    """
    Backend-orchestrated claim registration.
    This endpoint:
    1. Generates claim hash
    2. Registers on blockchain via backend wallet
    3. Stores content in IPFS
    4. Returns claim hash
    
    This ensures atomic consistency between blockchain and backend.
    """
    from utils import hash_claim
    
    # TEMP: Log raw body for debugging
    raw_body = await raw_request.json()
    print(f"\n{'='*60}")
    print(f"🔍 RAW BODY RECEIVED:")
    print(f"{'='*60}")
    print(f"Body: {raw_body}")
    print(f"Keys: {list(raw_body.keys())}")
    print(f"{'='*60}\n")
    
    # Validate against Pydantic model
    try:
        request = RegisterClaimFullRequest(**raw_body)
    except Exception as e:
        print(f"❌ Pydantic validation failed: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=f"Invalid request body: {str(e)}"
        )
    
    # Step 1: Generate claim hash
    claim_hash = hash_claim(request.newsContent)
    
    print(f"\n{'='*60}")
    print(f"🔄 BACKEND-ORCHESTRATED REGISTRATION")
    print(f"{'='*60}")
    print(f"📝 Generated hash: {claim_hash}")
    print(f"👤 Submitter: {request.submitterAddress}")
    print(f"📄 Content length: {len(request.newsContent)} chars")
    
    # Step 2: Check if already exists
    if contract_wrapper.claim_exists(claim_hash):
        print(f"⚠️  Claim already exists on-chain")
        
        # Check if in registry
        if claim_hash in claim_registry:
            existing = claim_registry[claim_hash]
            print(f"✅ Found in registry")
            print(f"   CID: {existing['contentCID']}")
            print(f"   Block: {existing['blockNumber']}")
            print(f"{'='*60}\n")
            return {
                "claimHash": claim_hash,
                "contentCID": existing["contentCID"],
                "blockNumber": existing["blockNumber"],
                "claimSubmitter": existing["claimSubmitter"],
                "alreadyExists": True
            }
        else:
            print(f"❌ Exists on-chain but NOT in registry - DESYNC DETECTED")
            print(f"{'='*60}\n")
            raise HTTPException(
                status_code=400,
                detail="Claim exists on-chain but not in backend registry"
            )
    
    # Step 3: Register on blockchain (backend wallet signs)
    print(f"📝 Registering on blockchain...")
    try:
        hash_bytes = contract_wrapper.hash_to_bytes32(claim_hash)
        
        # Build transaction
        tx = contract_wrapper.contract.functions.registerClaim(hash_bytes).build_transaction({
            'from': contract_wrapper.account.address,
            'nonce': contract_wrapper.w3.eth.get_transaction_count(contract_wrapper.account.address),
            'gas': 200000,
            'gasPrice': contract_wrapper.w3.eth.gas_price
        })
        
        # Sign transaction
        signed_tx = contract_wrapper.account.sign_transaction(tx)
        
        # Send transaction
        tx_hash = contract_wrapper.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"   Transaction sent: {tx_hash.hex()}")
        
        # Wait for confirmation
        receipt = contract_wrapper.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] != 1:
            print(f"❌ Transaction failed")
            print(f"{'='*60}\n")
            raise HTTPException(
                status_code=500,
                detail="Blockchain transaction failed"
            )
        
        print(f"✅ Blockchain registration success")
        print(f"   Block: {receipt['blockNumber']}")
        print(f"   Gas used: {receipt['gasUsed']}")
        block_number = receipt['blockNumber']
        
    except Exception as e:
        print(f"❌ Blockchain registration failed: {str(e)}")
        print(f"{'='*60}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Blockchain registration failed: {str(e)}"
        )
    
    # Step 4: Upload to IPFS
    print(f"📤 Uploading to IPFS...")
    try:
        claim_content = {
            "claimHash": claim_hash,
            "newsContent": request.newsContent,
            "submitter": request.submitterAddress,
            "timestamp": int(time.time())
        }
        
        content_cid = await ipfs.upload_to_pinata(claim_content)
        print(f"✅ IPFS upload complete: {content_cid}")
        
    except Exception as e:
        print(f"⚠️  IPFS upload failed (non-blocking): {str(e)}")
        content_cid = None
    
    # Step 5: Store in registry WITH ORIGINAL CONTENT
    print(f"💾 Storing in registry...")
    claim_registry[claim_hash] = {
        "claimHash": claim_hash,
        "contentCID": content_cid,
        "claimSubmitter": request.submitterAddress,
        "blockNumber": block_number,
        "timestamp": int(time.time()),
        "newsContent": request.newsContent  # Store original content as fallback
    }
    print(f"✅ Stored in registry with content fallback")
    
    # Step 6: Refresh event cache
    print(f"🔄 Refreshing event cache...")
    event_indexer.index_claims_from_events(force_refresh=True)
    print(f"✅ Event cache refreshed")
    
    print(f"✅ Registration complete")
    print(f"📤 Returned to frontend: {claim_hash}")
    print(f"{'='*60}\n")
    
    return {
        "claimHash": claim_hash,
        "contentCID": content_cid,
        "blockNumber": block_number,
        "claimSubmitter": request.submitterAddress,
        "alreadyExists": False
    }


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
        print(f"⚠️  IPFS upload failed (non-blocking): {str(e)}")
        content_cid = None
    
    # Get current block number
    votes = contract_wrapper.get_votes(claim_hash)
    block_number = votes["block_number"]
    
    # Store in registry WITH ORIGINAL CONTENT
    claim_registry[claim_hash] = {
        "claimHash": claim_hash,
        "contentCID": content_cid,
        "claimSubmitter": request.submitterAddress or "unknown",
        "blockNumber": block_number,
        "timestamp": int(time.time()),
        "newsContent": request.newsContent  # Store original content as fallback
    }
    
    # Refresh event cache to include new claim
    event_indexer.index_claims_from_events(force_refresh=True)
    
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
    Get all registered claims for feed display using event indexing.
    Returns list of claims with raw vote counts and Reddit-style scores.
    No AI calls, no IPFS fetch (except for content if available).
    """
    # Get indexed claims from blockchain events
    indexed_claims = event_indexer.get_cached_claims()
    
    feed_items = []
    
    for claim in indexed_claims:
        claim_hash = claim['claimHash']
        
        # Get IPFS CID if available
        content_cid = None
        timestamp = None
        if claim_hash in claim_registry:
            content_cid = claim_registry[claim_hash].get('contentCID')
            timestamp = claim_registry[claim_hash].get('timestamp')
        
        # If no timestamp from registry, use current time
        if timestamp is None:
            timestamp = int(time.time())
        
        feed_items.append({
            "claimHash": claim_hash,
            "contentCID": content_cid,
            "claimSubmitter": claim['submitter'],
            "timestamp": timestamp,
            "blockNumber": claim['blockNumber'],
            "userTrueVotes": claim['userTrueVotes'],
            "userFalseVotes": claim['userFalseVotes'],
            "validatorTrueVotes": claim['validatorTrueVotes'],
            "validatorFalseVotes": claim['validatorFalseVotes'],
            "score": claim['score']
        })
    
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
    
    FALLBACK SYNC: If claim not in registry but exists on-chain,
    creates minimal registry entry to prevent permanent desync.
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
    
    # Check if claim exists on-chain FIRST
    exists = contract_wrapper.claim_exists(claim_hash)
    
    if not exists:
        print(f"⚠️  Claim does not exist on-chain: {claim_hash}")
        raise HTTPException(
            status_code=404,
            detail="Claim not found on blockchain"
        )
    
    print(f"✅ Claim exists on-chain: {claim_hash}")
    
    # Check if in registry
    if claim_hash not in claim_registry:
        print(f"⚠️  DESYNC DETECTED: Claim on-chain but not in registry")
        print(f"🔄 Attempting fallback sync...")
        
        # FALLBACK SYNC: Create minimal registry entry
        try:
            # Get submitter from contract
            submitter = contract_wrapper.get_claim_submitter(claim_hash)
            votes = contract_wrapper.get_votes(claim_hash)
            
            print(f"   Submitter: {submitter}")
            print(f"   Block: {votes['block_number']}")
            
            # Create minimal entry (no content, no CID)
            claim_registry[claim_hash] = {
                "claimHash": claim_hash,
                "contentCID": None,
                "claimSubmitter": submitter,
                "blockNumber": votes['block_number'],
                "timestamp": int(time.time()),
                "newsContent": None  # No content available for external claims
            }
            
            print(f"✅ Fallback sync complete - minimal entry created")
            
            # Return minimal data
            user_votes = contract_wrapper.get_votes(claim_hash)
            validator_votes = contract_wrapper.get_validator_votes(claim_hash)
            
            # Get role metadata if caller provided
            caller_role = None
            has_voted = False
            
            if caller_address:
                try:
                    caller_role = contract_wrapper.get_role(caller_address)
                    has_voted = contract_wrapper.has_address_voted(claim_hash, caller_address)
                except Exception as e:
                    print(f"⚠️  Failed to get caller role: {str(e)}")
                    caller_role = 0
                    has_voted = False
            
            return {
                "claimHash": claim_hash,
                "newsContent": "[Content not available - claim registered externally]",
                "contentCID": None,
                "claimSubmitter": submitter,
                "timestamp": int(time.time()),
                "blockNumber": votes['block_number'],
                "userTrueVotes": user_votes["true_votes"],
                "userFalseVotes": user_votes["false_votes"],
                "validatorTrueVotes": validator_votes["true_votes"],
                "validatorFalseVotes": validator_votes["false_votes"],
                "callerRole": caller_role,
                "hasVoted": has_voted
            }
            
        except Exception as e:
            print(f"❌ Fallback sync failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Claim exists on-chain but backend sync failed: {str(e)}"
            )
    
    # Normal flow: claim in registry
    claim_metadata = claim_registry[claim_hash]
    content_cid = claim_metadata["contentCID"]
    
    # Fetch claim text with proper fallback chain: IPFS → Database → Placeholder
    news_content = "[Content not available]"
    
    # Try IPFS first if CID exists
    if content_cid:
        try:
            claim_content = await ipfs.fetch_from_pinata(content_cid)
            news_content = claim_content.get("newsContent", "[Content not available]")
            print(f"✅ Content fetched from IPFS")
        except Exception as e:
            print(f"⚠️  IPFS fetch failed: {str(e)}")
            # Fall through to database fallback
    
    # Fallback to stored content in database if IPFS failed or no CID
    if news_content == "[Content not available]" and claim_metadata.get("newsContent"):
        news_content = claim_metadata["newsContent"]
        print(f"✅ Content retrieved from database fallback")
    
    # If still no content, use placeholder
    if news_content == "[Content not available]":
        print(f"⚠️  No content available from any source")
    
    # Get vote data using wrapper (safe because we checked exists)
    print(f"✅ Fetching votes for existing claim: {claim_hash}")
    user_votes = contract_wrapper.get_votes(claim_hash)
    validator_votes = contract_wrapper.get_validator_votes(claim_hash)
    
    # Get role metadata if caller provided
    caller_role = None
    has_voted = False
    
    if caller_address:
        try:
            caller_role = contract_wrapper.get_role(caller_address)
            has_voted = contract_wrapper.has_address_voted(claim_hash, caller_address)
        except Exception as e:
            print(f"⚠️  Failed to get caller role: {str(e)}")
            caller_role = 0
            has_voted = False
    
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
    Get claim content from backend storage.
    Returns stored claim text as fallback when IPFS is unavailable.
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
    
    # Check if claim exists in registry
    if claim_hash not in claim_registry:
        raise HTTPException(
            status_code=404,
            detail="Claim not found in backend storage"
        )
    
    claim_metadata = claim_registry[claim_hash]
    
    # Return stored content if available
    if claim_metadata.get("newsContent"):
        return {
            "claimHash": claim_hash,
            "newsContent": claim_metadata["newsContent"],
            "contentCID": claim_metadata.get("contentCID"),
            "claimSubmitter": claim_metadata.get("claimSubmitter"),
            "blockNumber": claim_metadata.get("blockNumber"),
            "timestamp": claim_metadata.get("timestamp")
        }
    else:
        raise HTTPException(
            status_code=404,
            detail="Claim content not available in backend storage"
        )


@router.get("/claims/{claim_hash}/blockchain")
async def get_claim_blockchain(claim_hash: str):
    """
    Get claim data from blockchain only.
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
