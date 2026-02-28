"""
ThinkBaby - AI + Bot + IVR Layer (Python)
Main entry point for the application
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.claim_extractor import analyze_message
from modules.hash_generator import generate_claim_hash, verify_hash_match
from modules.backend_client import (
    submit_claim_to_backend,
    get_claim_result,
    health_check
)

# Print banner
print("")
print("╔════════════════════════════════════════════════════════════╗")
print("║                                                            ║")
print("║              🔥 THINKBABY - AI LAYER 🔥                   ║")
print("║                 (Python Version)                           ║")
print("║                                                            ║")
print("║   Web3 Decentralized Fake News Verification Protocol      ║")
print("║                                                            ║")
print("╚════════════════════════════════════════════════════════════╝")
print("")


async def run_system_test():
    """Test function to verify all modules are working"""
    print("🧪 Running system tests...\n")
    
    try:
        # Test 1: Claim Extraction
        print("✅ Test 1: Claim Extraction Module")
        test_message = "Government giving ₹5000 to all students. Forward this immediately!"
        analysis = analyze_message(test_message)
        print(f"   Claims: {analysis['claims']}")
        print(f"   Risk Score: {analysis['riskScore']}")
        print(f"   Explanation: {analysis['explanation']}")
        print("")
        
        # Test 2: Hash Generation
        print("✅ Test 2: Hash Generator Module")
        claim_hash = generate_claim_hash(analysis['claims'][0])
        print(f"   Hash: {claim_hash}")
        print("")
        
        # Test 3: Backend API Health
        print("✅ Test 3: Backend API Connection")
        backend_healthy = health_check()
        if backend_healthy:
            print("   ✅ Backend is reachable")
        else:
            print("   ⚠️  Backend is not reachable (this is OK if backend is not running yet)")
        print("")
        
        # Test 4: Configuration
        print("✅ Test 4: Configuration")
        print(f"   Backend URL: {os.getenv('BACKEND_API_URL')}")
        print(f"   Twilio SID: {os.getenv('TWILIO_ACCOUNT_SID')[:10]}...")
        print(f"   WhatsApp Port: {os.getenv('WHATSAPP_BOT_PORT', 3001)}")
        print(f"   IVR Port: {os.getenv('IVR_PORT', 3002)}")
        print("")
        
        print("✅ All tests completed!\n")
    
    except Exception as e:
        print(f"❌ Test failed: {e}\n")


async def process_claim(message_text: str):
    """Example: Process a claim end-to-end"""
    print(f"\n📝 Processing claim: {message_text}")
    print("─" * 60)
    
    try:
        # Step 1: Analyze
        analysis = analyze_message(message_text)
        print("✅ Analysis complete")
        print(f"   Risk Score: {analysis['riskScore']}")
        
        # Step 2: Generate hash
        claim_hash = generate_claim_hash(analysis['claims'][0])
        print(f"✅ Hash generated: {claim_hash}")
        
        # Step 3: Submit to backend (if backend is available)
        backend_healthy = health_check()
        if backend_healthy:
            submit_result = submit_claim_to_backend(claim_hash, analysis['claims'][0])
            print(f"✅ Submitted to backend: {submit_result.get('success')}")
            
            # Step 4: Get result
            result = get_claim_result(claim_hash)
            print("✅ Blockchain result:")
            print(f"   True Votes: {result.get('trueVotes', 0)}")
            print(f"   False Votes: {result.get('falseVotes', 0)}")
            print(f"   Status: {result.get('status', 'Under Review')}")
        else:
            print("⚠️  Backend not available - skipping blockchain interaction")
        
        print("─" * 60)
        print("✅ Claim processed successfully\n")
    
    except Exception as e:
        print(f"❌ Error processing claim: {e}")


def display_instructions():
    """Display usage instructions"""
    print("📚 Usage Instructions:\n")
    print("1️⃣  Start WhatsApp Bot:")
    print("    python -m uvicorn bots.whatsapp_bot:app --host 0.0.0.0 --port 3001")
    print("    Or: cd bots && python whatsapp_bot.py")
    print("    Then configure Twilio webhook to: http://your-url/webhook/whatsapp\n")
    
    print("2️⃣  Start IVR Handler:")
    print("    python -m uvicorn ivr.ivr_handler:app --host 0.0.0.0 --port 3002")
    print("    Or: cd ivr && python ivr_handler.py")
    print("    Then configure Twilio voice webhook to: http://your-url/ivr/incoming\n")
    
    print("3️⃣  Run this test file:")
    print("    python main.py\n")
    
    print("📖 For more information, see README.md\n")


async def main():
    """Main function"""
    display_instructions()
    
    # Run tests
    await run_system_test()
    
    # Example: Process a test claim
    await process_claim("Breaking: New government scheme announced! Everyone gets free money!")
    
    print("🎯 Tip: To start the WhatsApp bot or IVR:")
    print("   cd bots && python whatsapp_bot.py  (for WhatsApp bot)")
    print("   cd ivr && python ivr_handler.py    (for IVR handler)\n")


if __name__ == "__main__":
    asyncio.run(main())
