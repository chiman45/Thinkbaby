from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routes import router
import contract_wrapper
import event_indexer


app = FastAPI(
    title="Fake News Verification Backend",
    description="Decentralized fake news verification protocol backend",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.on_event("startup")
async def startup():
    """
    Startup checks and verification.
    """
    print("\n" + "="*60)
    print("🚀 FAKE NEWS VERIFICATION BACKEND - SEPOLIA MODE")
    print("="*60)
    
    # Print configuration
    print(f"\n📋 Configuration:")
    print(f"   RPC URL: {settings.sepolia_rpc_url[:50]}...")
    print(f"   BACKEND CONTRACT: {settings.contract_address}")
    
    # Check Web3 connection
    try:
        is_connected = contract_wrapper.w3.is_connected()
        if not is_connected:
            print("\n❌ ERROR: Cannot connect to Sepolia RPC")
            print("   Check SEPOLIA_RPC_URL in .env file")
            raise Exception("Failed to connect to Sepolia RPC")
        
        print(f"\n✅ Connected to Sepolia RPC")
        
        # Get and verify chain ID
        chain_id = contract_wrapper.w3.eth.chain_id
        print(f"⛓️  Chain ID: {chain_id}")
        
        if chain_id != 11155111:
            print(f"\n❌ ERROR: Wrong network!")
            print(f"   Expected: Sepolia (11155111)")
            print(f"   Got: {chain_id}")
            raise Exception(f"Wrong network: {chain_id}")
        
        # Print wallet info
        wallet_address = contract_wrapper.account.address
        print(f"\n👛 Backend Wallet:")
        print(f"   Address: {wallet_address}")
        
        # Check wallet balance
        balance = contract_wrapper.w3.eth.get_balance(wallet_address)
        balance_eth = contract_wrapper.w3.from_wei(balance, 'ether')
        print(f"   Balance: {balance_eth} ETH")
        
        if balance_eth < 0.1:
            print(f"\n⚠️  WARNING: Low wallet balance!")
            print(f"   Current: {balance_eth} ETH")
            print(f"   Recommended: 0.5+ ETH")
            print(f"   Get Sepolia ETH from: https://sepoliafaucet.com/")
        
        # Verify contract address loaded from env
        print(f"\n📝 Smart Contract:")
        print(f"   Address: {settings.contract_address}")
        print(f"   Loaded from: .env file")
        
        # Test contract connectivity
        try:
            test_hash = "0x" + "0" * 64
            test_bytes = bytes.fromhex(test_hash[2:])
            contract_wrapper.contract.functions.claimExists(test_bytes).call()
            print(f"   Status: ✅ Contract accessible")
        except Exception as e:
            print(f"   Status: ⚠️  Contract call failed: {str(e)[:50]}")
        
        # Check and register backend wallet role
        print(f"\n🔐 Backend Wallet Role Check:")
        print(f"   Wallet: {wallet_address}")
        
        try:
            backend_role = contract_wrapper.contract.functions.getRole(wallet_address).call()
            print(f"   Current Role: {backend_role} (0=None, 1=User, 2=Validator)")
            
            if backend_role == 0:
                print(f"\n⚠️  Backend wallet not registered. Auto-registering as User...")
                
                # Build transaction
                tx = contract_wrapper.contract.functions.registerAsUser().build_transaction({
                    'from': wallet_address,
                    'nonce': contract_wrapper.w3.eth.get_transaction_count(wallet_address),
                    'gas': 300000,
                    'gasPrice': contract_wrapper.w3.eth.gas_price
                })
                
                # Sign transaction
                signed_tx = contract_wrapper.account.sign_transaction(tx)
                
                # Send transaction
                tx_hash = contract_wrapper.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                print(f"   Transaction sent: {tx_hash.hex()}")
                
                # Wait for confirmation
                receipt = contract_wrapper.w3.eth.wait_for_transaction_receipt(tx_hash)
                
                if receipt['status'] == 1:
                    print(f"   ✅ Backend wallet registered as User")
                    print(f"   Block: {receipt['blockNumber']}")
                    print(f"   Gas used: {receipt['gasUsed']}")
                else:
                    print(f"   ❌ Registration transaction failed")
                    raise Exception("Backend wallet registration failed")
            else:
                print(f"   ✅ Backend wallet already registered")
            
            print(f"   ✅ Backend wallet ready for claim registration")
            
        except Exception as e:
            print(f"   ❌ Role check/registration failed: {str(e)}")
            print(f"\n⚠️  WARNING: Backend wallet may not be able to register claims")
            print(f"   Manual registration may be required")
        
        print("\n" + "="*60)
        print("✅ BACKEND READY FOR SEPOLIA TRANSACTIONS")
        print("="*60 + "\n")
        
        # Index claims from blockchain events
        print("🔄 Indexing claims from blockchain...")
        event_indexer.index_claims_from_events(force_refresh=True)
        print("✅ Event indexing complete\n")
        
    except Exception as e:
        print(f"\n❌ STARTUP FAILED: {str(e)}")
        print("\nPlease check:")
        print("  1. .env file exists and is configured")
        print("  2. SEPOLIA_RPC_URL is valid")
        print("  3. BACKEND_PRIVATE_KEY is valid")
        print("  4. CONTRACT_ADDRESS is correct")
        print("  5. Wallet has Sepolia ETH")
        print("\n" + "="*60 + "\n")
        raise


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
