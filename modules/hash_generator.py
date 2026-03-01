"""
Claim Hash Generator (Python)
Generates keccak256 hashes compatible with Solidity smart contracts
"""

from web3 import Web3
from typing import List, Dict


def generate_claim_hash(claim_text: str) -> str:
    """
    Generates a keccak256 hash for a claim text
    This hash MUST match the Solidity keccak256(abi.encodePacked(string)) exactly
    
    Args:
        claim_text: The claim text to hash
        
    Returns:
        The keccak256 hash in hex format (0x...)
    """
    try:
        # Input validation
        if not claim_text or not isinstance(claim_text, str):
            raise ValueError("Claim text must be a non-empty string")
        
        # Normalize the text (trim and normalize whitespace)
        normalized_text = claim_text.strip()
        
        if not normalized_text:
            raise ValueError("Claim text cannot be empty after normalization")
        
        # Convert string to bytes (UTF-8 encoding)
        text_bytes = normalized_text.encode('utf-8')
        
        # Generate keccak256 hash (compatible with Solidity)
        hash_bytes = Web3.keccak(text=normalized_text)
        
        # Convert to hex string with '0x' prefix
        hash_hex = hash_bytes.hex()
        if not hash_hex.startswith('0x'):
            hash_hex = '0x' + hash_hex
        
        print(f"Generated hash for claim: \"{normalized_text[:50]}...\" => {hash_hex}")
        
        return hash_hex
    
    except Exception as e:
        print(f"Error generating claim hash: {e}")
        raise Exception(f"Hash generation failed: {str(e)}")


def hash_first_claim(claims: List[str]) -> str:
    """
    Generates a hash from the first claim in an array
    Useful for processing analyzed messages
    
    Args:
        claims: Array of claim strings
        
    Returns:
        The keccak256 hash of the first claim
    """
    if not isinstance(claims, list) or len(claims) == 0:
        raise ValueError("Claims array must contain at least one claim")
    
    return generate_claim_hash(claims[0])


def hash_multiple_claims(claims: List[str]) -> List[Dict[str, str]]:
    """
    Batch hash multiple claims
    
    Args:
        claims: Array of claim strings
        
    Returns:
        Array of claim-hash pairs
    """
    if not isinstance(claims, list) or len(claims) == 0:
        raise ValueError("Claims array must contain at least one claim")
    
    return [
        {"claim": claim, "hash": generate_claim_hash(claim)}
        for claim in claims
    ]


def verify_hash_match(claim1: str, claim2: str) -> bool:
    """
    Verify that two claims produce the same hash
    Useful for debugging hash consistency
    
    Args:
        claim1: First claim text
        claim2: Second claim text
        
    Returns:
        True if hashes match
    """
    hash1 = generate_claim_hash(claim1)
    hash2 = generate_claim_hash(claim2)
    
    match = hash1 == hash2
    print(f"Hash comparison: {'MATCH' if match else 'DIFFERENT'}")
    print(f"  Claim 1: \"{claim1}\" => {hash1}")
    print(f"  Claim 2: \"{claim2}\" => {hash2}")
    
    return match


# Example usage
if __name__ == "__main__":
    # Test hash generation
    claim = "Government giving ₹5000 to students"
    hash1 = generate_claim_hash(claim)
    print(f"\nClaim: {claim}")
    print(f"Hash: {hash1}")
    
    # Test consistency
    hash2 = generate_claim_hash(claim)
    print(f"\nSame hash? {hash1 == hash2}")
    
    # Test different text produces different hash
    different_claim = "Government giving Rs 5000 to students"
    hash3 = generate_claim_hash(different_claim)
    print(f"\nDifferent claim hash: {hash3}")
    print(f"Same as first? {hash1 == hash3}")
