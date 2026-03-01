import httpx
from config import settings
import sys
import os

# Add root directory to path for credibility_engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from credibility_engine import CredibilityEngine
    CREDIBILITY_ENGINE_AVAILABLE = True
    print("✅ Credibility Engine loaded successfully")
except ImportError as e:
    print(f"⚠️  Credibility Engine not available: {e}")
    CREDIBILITY_ENGINE_AVAILABLE = False


async def analyze_claim(text: str, source_url: str = None, votes_data: dict = None) -> dict:
    """
    Call AI analysis using the Credibility Engine.
    Falls back to external AI service if engine is not available.
    
    Args:
        text: The claim text to analyze
        source_url: Optional source URL for credibility scoring
        votes_data: Optional blockchain votes data
    """
    # Try using the Credibility Engine first
    if CREDIBILITY_ENGINE_AVAILABLE:
        try:
            print(f"🤖 Using Credibility Engine for analysis...")
            engine = CredibilityEngine()
            
            # Call the engine with all available context
            result = await engine.score(
                claim=text,
                source_url=source_url,
                rag_context=None,  # Can be integrated with RAG system later
                web_context=None,  # Can be integrated with web search later
                votes_data=votes_data
            )
            
            # Convert to expected format
            return {
                "ai_label": result.verdict,
                "risk_score": 1.0 - result.final_score,  # Invert: engine uses 1.0=credible, we use 1.0=risky
                "summary": result.explanation,
                "confidence": result.confidence,
                "flags": result.flags,
                "sources_found": result.sources_found,
                "risk_level": result.risk_level,
                "processing_ms": result.processing_ms,
                "scores": {
                    "source": result.source_score,
                    "linguistic": result.linguistic_score,
                    "numerical": result.numerical_score,
                    "rag_match": result.rag_match_score,
                    "temporal": result.temporal_score,
                    "community": result.community_score
                }
            }
        except Exception as e:
            print(f"⚠️  Credibility Engine failed: {e}")
            print(f"Falling back to external AI service...")
    
    # Fallback to external AI service
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
        # Final fallback
        print(f"❌ All AI services failed: {e}")
        return {
            "ai_label": "Uncertain",
            "risk_score": 0.5,
            "summary": "AI analysis unavailable"
        }
