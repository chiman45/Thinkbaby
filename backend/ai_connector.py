import httpx
from config import settings


async def analyze_claim(text: str) -> dict:
    """
    Call external AI service for claim analysis.
    Returns AI analysis or fallback if service fails.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.ai_service_url,
                json={"claim": text}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Validate response format
            return {
                "ai_label": data.get("ai_label", "Uncertain"),
                "risk_score": data.get("risk_score", 0.5),
                "summary": data.get("summary", "Analysis completed")
            }
    
    except Exception as e:
        # AI failure fallback
        print(f"AI service error: {e}")
        return {
            "ai_label": "Uncertain",
            "risk_score": 0.5,
            "summary": "AI unavailable"
        }
