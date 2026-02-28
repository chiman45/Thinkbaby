"""
Event-based indexer for blockchain claims.
Indexes ClaimRegistered events and builds Reddit-style feed.
"""
import contract_wrapper
import time
from typing import List, Dict


# Global cache for indexed claims
claims_cache: List[Dict] = []
last_indexed_block = 0
cache_timestamp = 0
CACHE_TTL = 30  # seconds


def compute_reddit_score(
    user_true: int,
    user_false: int,
    validator_true: int,
    validator_false: int
) -> int:
    """
    Compute Reddit-style weighted ranking score.
    Validator votes weighted 3x more than user votes.
    """
    validator_score = (validator_true - validator_false) * 3
    user_score = (user_true - user_false)
    return validator_score + user_score


def index_claims_from_events(force_refresh=False):
    """
    Index all claims from blockchain events.
    Builds cache with vote counts and scores.
    """
    global claims_cache, last_indexed_block, cache_timestamp
    
    # Check cache freshness
    current_time = time.time()
    if not force_refresh and claims_cache and (current_time - cache_timestamp) < CACHE_TTL:
        return claims_cache
    
    print(f"\n🔍 Indexing claims from blockchain events...")
    start_time = time.time()
    
    try:
        # Query all ClaimRegistered events
        events = contract_wrapper.get_claim_registered_events(
            from_block=0,
            to_block='latest'
        )
        
        print(f"   Found {len(events)} ClaimRegistered events")
        
        indexed_claims = []
        
        for event in events:
            claim_hash = event['claimHash']
            submitter = event['submitter']
            block_number = event['blockNumber']
            
            try:
                # Get vote counts from contract
                user_votes = contract_wrapper.get_votes(claim_hash)
                validator_votes = contract_wrapper.get_validator_votes(claim_hash)
                
                # Compute Reddit score
                score = compute_reddit_score(
                    user_votes['true_votes'],
                    user_votes['false_votes'],
                    validator_votes['true_votes'],
                    validator_votes['false_votes']
                )
                
                indexed_claims.append({
                    'claimHash': claim_hash,
                    'submitter': submitter,
                    'blockNumber': block_number,
                    'userTrueVotes': user_votes['true_votes'],
                    'userFalseVotes': user_votes['false_votes'],
                    'validatorTrueVotes': validator_votes['true_votes'],
                    'validatorFalseVotes': validator_votes['false_votes'],
                    'score': score,
                    'transactionHash': event['transactionHash']
                })
                
            except Exception as e:
                print(f"   ⚠️  Failed to index claim {claim_hash[:16]}...: {str(e)}")
                continue
        
        # Sort by Reddit score (descending)
        indexed_claims.sort(key=lambda x: x['score'], reverse=True)
        
        # Update cache
        claims_cache = indexed_claims
        last_indexed_block = contract_wrapper.w3.eth.block_number
        cache_timestamp = current_time
        
        elapsed = time.time() - start_time
        print(f"   ✅ Indexed {len(indexed_claims)} claims in {elapsed:.2f}s")
        print(f"   📊 Top score: {indexed_claims[0]['score'] if indexed_claims else 0}")
        
        return indexed_claims
        
    except Exception as e:
        print(f"   ❌ Event indexing failed: {str(e)}")
        return []


def get_cached_claims() -> List[Dict]:
    """
    Get cached claims, refresh if stale.
    """
    return index_claims_from_events(force_refresh=False)


def refresh_claim_cache(claim_hash: str):
    """
    Refresh cache for a specific claim after vote.
    """
    global claims_cache
    
    for claim in claims_cache:
        if claim['claimHash'] == claim_hash:
            try:
                # Refresh vote counts
                user_votes = contract_wrapper.get_votes(claim_hash)
                validator_votes = contract_wrapper.get_validator_votes(claim_hash)
                
                # Update claim
                claim['userTrueVotes'] = user_votes['true_votes']
                claim['userFalseVotes'] = user_votes['false_votes']
                claim['validatorTrueVotes'] = validator_votes['true_votes']
                claim['validatorFalseVotes'] = validator_votes['false_votes']
                
                # Recalculate score
                claim['score'] = compute_reddit_score(
                    user_votes['true_votes'],
                    user_votes['false_votes'],
                    validator_votes['true_votes'],
                    validator_votes['false_votes']
                )
                
                # Re-sort cache
                claims_cache.sort(key=lambda x: x['score'], reverse=True)
                
                print(f"   ✅ Refreshed cache for claim {claim_hash[:16]}...")
                return True
                
            except Exception as e:
                print(f"   ⚠️  Failed to refresh claim cache: {str(e)}")
                return False
    
    # Claim not in cache, force full refresh
    index_claims_from_events(force_refresh=True)
    return True
