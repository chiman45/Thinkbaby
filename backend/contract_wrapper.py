"""
Contract wrapper functions for clean blockchain interaction.
All contract calls should go through these functions.
"""
import json
from web3 import Web3
from eth_account import Account
from config import settings
from utils import hash_to_bytes32


# Initialize Web3
w3 = Web3(Web3.HTTPProvider(settings.sepolia_rpc_url))

# Load account
account = Account.from_key(settings.backend_private_key)

# Load contract
with open("abi.json", "r") as f:
    contract_abi = json.load(f)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(settings.contract_address),
    abi=contract_abi
)


def claim_exists(claim_hash: str) -> bool:
    """Check if claim exists on-chain."""
    hash_bytes = hash_to_bytes32(claim_hash)
    return contract.functions.claimExists(hash_bytes).call()


def get_votes(claim_hash: str) -> dict:
    """
    Get total vote counts (validator + user votes combined).
    Returns dict with true_votes, false_votes, block_number.
    """
    hash_bytes = hash_to_bytes32(claim_hash)
    block_number = w3.eth.block_number
    
    if not claim_exists(claim_hash):
        return {
            "true_votes": 0,
            "false_votes": 0,
            "block_number": block_number
        }
    
    true_votes, false_votes = contract.functions.getVotes(hash_bytes).call()
    
    return {
        "true_votes": int(true_votes),
        "false_votes": int(false_votes),
        "block_number": block_number
    }


def get_validator_votes(claim_hash: str) -> dict:
    """
    Get validator-only vote counts.
    For hackathon: same as total votes (no separate validator tracking).
    """
    return get_votes(claim_hash)


def get_role(wallet_address: str) -> str:
    """
    Get role of wallet address.
    For hackathon: returns 'user' (no role system in contract).
    """
    return "user"


def has_address_voted(claim_hash: str, voter_address: str) -> bool:
    """
    Check if address has voted on claim.
    For hackathon: not implemented in contract, returns False.
    """
    return False


def get_claim_submitter(claim_hash: str) -> str:
    """
    Get address that submitted claim.
    For hackathon: returns backend wallet (all claims registered by backend).
    """
    return account.address


def register_claim_tx(claim_hash: str) -> str:
    """
    Register claim on blockchain (backend-controlled mode only).
    Returns transaction hash immediately.
    """
    hash_bytes = hash_to_bytes32(claim_hash)
    nonce = w3.eth.get_transaction_count(account.address, 'pending')
    
    txn = contract.functions.registerClaim(hash_bytes).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 150000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 11155111
    })
    
    signed_txn = account.sign_transaction(txn)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    return tx_hash.hex()
