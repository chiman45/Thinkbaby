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
    Get validator-only vote counts from contract.
    """
    hash_bytes = hash_to_bytes32(claim_hash)
    block_number = w3.eth.block_number
    
    if not claim_exists(claim_hash):
        return {
            "true_votes": 0,
            "false_votes": 0,
            "block_number": block_number
        }
    
    validator_true, validator_false = contract.functions.getValidatorVotes(hash_bytes).call()
    
    return {
        "true_votes": int(validator_true),
        "false_votes": int(validator_false),
        "block_number": block_number
    }


def get_role(wallet_address: str) -> int:
    """
    Get role of wallet address from contract.
    Returns: 0 = None, 1 = User, 2 = Validator
    """
    checksum_address = Web3.to_checksum_address(wallet_address)
    role = contract.functions.getRole(checksum_address).call()
    return int(role)


def has_address_voted(claim_hash: str, voter_address: str) -> bool:
    """
    Check if address has voted on claim.
    """
    hash_bytes = hash_to_bytes32(claim_hash)
    checksum_address = Web3.to_checksum_address(voter_address)
    return contract.functions.hasAddressVoted(hash_bytes, checksum_address).call()


def get_claim_submitter(claim_hash: str) -> str:
    """
    Get address that submitted claim from contract.
    """
    hash_bytes = hash_to_bytes32(claim_hash)
    submitter = contract.functions.getClaimSubmitter(hash_bytes).call()
    return submitter


def get_claim_registered_events(from_block=0, to_block='latest'):
    """
    Query all ClaimRegistered events from blockchain.
    Returns list of decoded events with claimHash and submitter.
    """
    event_filter = contract.events.ClaimRegistered.create_filter(
        fromBlock=from_block,
        toBlock=to_block
    )
    
    events = event_filter.get_all_entries()
    
    decoded_events = []
    for event in events:
        decoded_events.append({
            'claimHash': '0x' + event['args']['claimHash'].hex(),
            'submitter': event['args']['submitter'],
            'blockNumber': event['blockNumber'],
            'transactionHash': event['transactionHash'].hex()
        })
    
    return decoded_events
