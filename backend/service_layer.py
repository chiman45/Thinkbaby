"""
Service layer for business logic and orchestration.
"""
import json
from web3 import Web3


def compute_credibility_score(true_votes: int, false_votes: int) -> float:
    """
    Compute credibility score from vote counts.
    Returns value between 0.0 and 1.0.
    """
    total_votes = true_votes + false_votes
    
    if total_votes == 0:
        return 0.5  # Neutral when no votes
    
    return true_votes / total_votes


def compute_final_status(credibility_score: float) -> str:
    """
    Compute final status based on credibility score.
    """
    if credibility_score >= 0.7:
        return "VERIFIED"
    elif credibility_score <= 0.3:
        return "FAKE"
    else:
        return "DISPUTED"


def build_snapshot(
    claim_hash: str,
    news_content: str,
    validator_votes: dict,
    user_votes: dict,
    block_number: int,
    ai_output: dict,
    credibility_score: float,
    final_status: str
) -> dict:
    """
    Build structured snapshot object.
    """
    return {
        "claimHash": claim_hash,
        "newsContent": news_content,
        "validatorVotes": {
            "true": validator_votes["true_votes"],
            "false": validator_votes["false_votes"]
        },
        "userVotes": {
            "true": user_votes["true_votes"],
            "false": user_votes["false_votes"]
        },
        "blockNumber": block_number,
        "aiOutput": ai_output,
        "credibilityScore": credibility_score,
        "finalStatus": final_status
    }


def generate_snapshot_hash(snapshot: dict) -> str:
    """
    Generate deterministic hash of snapshot using canonical JSON serialization.
    """
    snapshot_json = json.dumps(snapshot, sort_keys=True, separators=(',', ':'))
    snapshot_bytes = snapshot_json.encode('utf-8')
    return Web3.keccak(snapshot_bytes).hex()
