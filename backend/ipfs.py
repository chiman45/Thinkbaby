import httpx
from config import settings


async def upload_to_pinata(data: dict) -> str:
    """
    Upload JSON data to Pinata (IPFS).
    Returns CID (IPFS hash).
    Raises exception if upload fails.
    """
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    
    headers = {
        "pinata_api_key": settings.pinata_api_key,
        "pinata_secret_api_key": settings.pinata_secret_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            url,
            json=data,
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        return result["IpfsHash"]


async def fetch_from_pinata(cid: str) -> dict:
    """
    Fetch JSON data from IPFS via Pinata gateway.
    Returns parsed JSON object.
    Raises exception if fetch fails.
    """
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        return response.json()
