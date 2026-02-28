from web3 import Web3


def normalize_text(text: str) -> str:
    """
    Normalize text using deterministic rules.
    Must match frontend normalization exactly.
    """
    return " ".join(text.lower().strip().split())


def hash_claim(text: str) -> str:
    """
    Generate keccak256 hash of normalized text.
    Returns hex string with 0x prefix.
    """
    normalized = normalize_text(text)
    return Web3.keccak(text=normalized).hex()


def validate_hash_format(hash_str: str) -> None:
    """
    Validate hash format.
    Raises ValueError if invalid.
    """
    if not hash_str.startswith('0x'):
        raise ValueError("Hash must start with 0x")
    if len(hash_str) != 66:
        raise ValueError("Hash must be exactly 66 characters (0x + 64 hex digits)")
    try:
        bytes.fromhex(hash_str[2:])
    except ValueError:
        raise ValueError("Invalid hex string")


def hash_to_bytes32(hash_str: str) -> bytes:
    """
    Convert hex hash string to bytes32 for contract call.
    """
    validate_hash_format(hash_str)
    return bytes.fromhex(hash_str[2:])
