"""
Backend API Integration Layer (Python)
Handles all communication with the FastAPI backend
Backend API interacts with the smart contract on Ethereum Sepolia
"""

import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend URL from environment or use default
BACKEND_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000/api')

# Request timeout (10 seconds)
REQUEST_TIMEOUT = 10


def submit_claim_to_backend(claim_hash: str, claim_text: str = "") -> Dict:
    """
    Submit a new claim to the backend (and blockchain)
    
    Args:
        claim_hash: The keccak256 hash of the claim
        claim_text: The original claim text (optional, for backend storage)
        
    Returns:
        Response from backend
    """
    try:
        print(f"[API Request] POST /submitClaim")
        
        response = requests.post(
            f"{BACKEND_URL}/submitClaim",
            json={
                "claimHash": claim_hash,
                "claimText": claim_text
            },
            timeout=REQUEST_TIMEOUT
        )
        
        print(f"[API Response] {response.status_code}")
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json(),
            "message": "Claim submitted successfully"
        }
    
    except Exception as e:
        return handle_api_error("submit_claim_to_backend", e)


def vote_true(claim_hash: str, voter_address: Optional[str] = None) -> Dict:
    """
    Vote TRUE for a claim
    
    Args:
        claim_hash: The keccak256 hash of the claim
        voter_address: Address of the voter (optional)
        
    Returns:
        Response from backend
    """
    try:
        print(f"[API Request] POST /voteTrue")
        
        response = requests.post(
            f"{BACKEND_URL}/voteTrue",
            json={
                "claimHash": claim_hash,
                "voterAddress": voter_address
            },
            timeout=REQUEST_TIMEOUT
        )
        
        print(f"[API Response] {response.status_code}")
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json(),
            "message": "Vote TRUE recorded"
        }
    
    except Exception as e:
        return handle_api_error("vote_true", e)


def vote_false(claim_hash: str, voter_address: Optional[str] = None) -> Dict:
    """
    Vote FALSE for a claim
    
    Args:
        claim_hash: The keccak256 hash of the claim
        voter_address: Address of the voter (optional)
        
    Returns:
        Response from backend
    """
    try:
        print(f"[API Request] POST /voteFalse")
        
        response = requests.post(
            f"{BACKEND_URL}/voteFalse",
            json={
                "claimHash": claim_hash,
                "voterAddress": voter_address
            },
            timeout=REQUEST_TIMEOUT
        )
        
        print(f"[API Response] {response.status_code}")
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json(),
            "message": "Vote FALSE recorded"
        }
    
    except Exception as e:
        return handle_api_error("vote_false", e)


def get_claim_result(claim_hash: str) -> Dict:
    """
    Get the voting results for a claim
    
    Args:
        claim_hash: The keccak256 hash of the claim
        
    Returns:
        Claim result with vote counts and status
    """
    try:
        print(f"[API Request] GET /getClaimResult")
        
        response = requests.get(
            f"{BACKEND_URL}/getClaimResult",
            params={"claimHash": claim_hash},
            timeout=REQUEST_TIMEOUT
        )
        
        print(f"[API Response] {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "success": True,
            "data": data,
            "exists": data.get("exists", False),
            "trueVotes": data.get("trueVotes", 0),
            "falseVotes": data.get("falseVotes", 0),
            "status": data.get("status", "Under Review")
        }
    
    except Exception as e:
        return handle_api_error("get_claim_result", e)


def get_reputation(validator_address: str) -> Dict:
    """
    Get reputation score for a validator
    
    Args:
        validator_address: Ethereum address of the validator
        
    Returns:
        Reputation data
    """
    try:
        print(f"[API Request] GET /getReputation")
        
        response = requests.get(
            f"{BACKEND_URL}/getReputation",
            params={"validatorAddress": validator_address},
            timeout=REQUEST_TIMEOUT
        )
        
        print(f"[API Response] {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "success": True,
            "data": data,
            "reputation": data.get("reputation", 0)
        }
    
    except Exception as e:
        return handle_api_error("get_reputation", e)


def claim_exists(claim_hash: str) -> bool:
    """
    Check if a claim already exists in the system
    
    Args:
        claim_hash: The keccak256 hash of the claim
        
    Returns:
        True if claim exists
    """
    try:
        result = get_claim_result(claim_hash)
        return result.get("success", False) and result.get("exists", False)
    except Exception as e:
        print(f"Error checking claim existence: {e}")
        return False


def health_check() -> bool:
    """
    Health check for backend API
    
    Returns:
        True if backend is reachable
    """
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=3)
        return response.status_code == 200
    except Exception as e:
        print(f"Backend health check failed: {e}")
        return False


def handle_api_error(function_name: str, error: Exception) -> Dict:
    """
    Centralized error handler for API calls
    """
    print(f"[{function_name}] Error: {str(error)}")
    
    if isinstance(error, requests.exceptions.HTTPError):
        return {
            "success": False,
            "error": str(error),
            "statusCode": error.response.status_code
        }
    elif isinstance(error, requests.exceptions.Timeout):
        return {
            "success": False,
            "error": "Backend server not responding. Please try again later.",
            "statusCode": 503
        }
    else:
        return {
            "success": False,
            "error": str(error),
            "statusCode": 500
        }


# Example usage
if __name__ == "__main__":
    # Test health check
    print("Testing backend connection...")
    is_healthy = health_check()
    print(f"Backend healthy: {is_healthy}")
