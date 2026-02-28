"""
Simple Test Suite (Python)
Run quick tests on individual modules
"""

import sys
import os
import asyncio

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.claim_extractor import analyze_message
from modules.hash_generator import generate_claim_hash, verify_hash_match

print("🧪 Running Simple Tests\n")


async def test_claim_extractor():
    """Test the claim extraction module"""
    print("Test 1: Claim Extractor")
    print("─" * 60)
    
    test_cases = [
        "Government giving ₹5000 to all students! Forward immediately!",
        "Breaking news: New cryptocurrency launched by Elon Musk",
        "Scientists discover cure for common cold",
        "Normal weather report for tomorrow"
    ]
    
    for text in test_cases:
        result = analyze_message(text)
        print(f"\nInput: \"{text}\"")
        print(f"Risk Score: {result['riskScore']}%")
        print(f"Claims: {', '.join(result['claims'])}")
    
    print("\n")


def test_hash_generator():
    """Test the hash generation module"""
    print("Test 2: Hash Generator")
    print("─" * 60)
    
    claim1 = "Government giving ₹5000 to students"
    claim2 = "Government giving ₹5000 to students"  # Same
    claim3 = "Government giving Rs 5000 to students"  # Different
    
    hash1 = generate_claim_hash(claim1)
    hash2 = generate_claim_hash(claim2)
    hash3 = generate_claim_hash(claim3)
    
    print(f"\nClaim 1: \"{claim1}\"")
    print(f"Hash 1: {hash1}")
    print(f"\nClaim 2: \"{claim2}\"")
    print(f"Hash 2: {hash2}")
    print(f"\nSame hash? {'✅ YES' if hash1 == hash2 else '❌ NO'}")
    
    print(f"\nClaim 3: \"{claim3}\"")
    print(f"Hash 3: {hash3}")
    print(f"Same as hash1? {'✅ YES' if hash1 == hash3 else '❌ NO'}\n")


async def run_tests():
    """Run all tests"""
    await test_claim_extractor()
    test_hash_generator()
    print("✅ All tests completed!\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
