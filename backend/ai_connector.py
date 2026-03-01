import httpx
from config import settings
import sys
import os

# Add parent directory to import credibility_engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from credibility_engine import CredibilityEngine

# Initialize credibility engine
credibility_engine = CredibilityEngine()


async def analyze_claim(text: str, source_url: str = None, rag_context: str = None, 
                       web_context: str = None, votes_data: dict = None) -> dict:
    """
    Analyze claim using the integrated Credibility Engine.
    Falls back to external AI service if credibility engine fails.
    
    Returns AI analysis in the format expected by the frontend:
    {
        "ai_label": str,      # Verdict: TRUE, FALSE, UNCERTAIN, etc.
        "risk_score": float,  # 0.0 - 1.0 (inverted from credibility score)
        "summary": str        # Human-readable explanation
    }
    """
    try:
        # Use Credibility Engine for analysis
        print(f"🔍 Analyzing claim with Credibility Engine...")
        print(f"   Claim: {text[:100]}...")
        
        result = await credibility_engine.score(
            claim=text,
            source_url=source_url,
            rag_context=rag_context,
            web_context=web_context,
            votes_data=votes_data
        )
        
        # Convert credibility result to expected format
        # Risk score is inverted: high credibility = low risk
        risk_score = 1.0 - result.final_score
        
        # Map verdict to ai_label
        verdict_map = {
            "TRUE": "Likely True",
            "FALSE": "Likely False",
            "UNCERTAIN": "Uncertain",
            "UNVERIFIED": "Unverified",
            "BREAKING": "Breaking News"
        }
        
        ai_label = verdict_map.get(result.verdict, "Uncertain")
        
        # Build summary with key metrics
        summary = f"{result.explanation} | "
        summary += f"Confidence: {result.confidence:.0%} | "
        summary += f"Risk: {result.risk_level.upper()}"
        
        if result.flags:
            top_flags = result.flags[:3]
            summary += f" | Signals: {', '.join(top_flags)}"
        
        analysis_result = {
            "ai_label": ai_label,
            "risk_score": round(risk_score, 3),
            "summary": summary
        }
        
        print(f"✅ Credibility Engine Analysis:")
        print(f"   Verdict: {result.verdict}")
        print(f"   AI Label: {ai_label}")
        print(f"   Risk Score: {risk_score:.2%}")
        print(f"   Summary: {summary[:100]}...")
        
        return analysis_result
    
    except Exception as e:
        print(f"⚠️ Credibility Engine failed, trying external AI service: {e}")
        
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
        
        except Exception as fallback_error:
            # Both systems failed - return safe fallback
            print(f"❌ AI service also failed: {fallback_error}")
            return {
                "ai_label": "Uncertain",
                "risk_score": 0.5,
                "summary": "AI analysis unavailable - both credibility engine and external service failed"
            }

