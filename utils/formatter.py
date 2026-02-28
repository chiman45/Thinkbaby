"""
Response Formatter Utility (Python)
Formats responses for WhatsApp, IVR, and other channels
"""

from typing import Dict, List


def format_whatsapp_report(analysis: Dict, blockchain_result: Dict) -> str:
    """
    Format credibility report for WhatsApp
    
    Args:
        analysis: Analysis result from claim_extractor
        blockchain_result: Result from get_claim_result
        
    Returns:
        Formatted WhatsApp message
    """
    claims = analysis.get("claims", [])
    risk_score = analysis.get("riskScore", 0)
    explanation = analysis.get("explanation", "")
    
    true_votes = blockchain_result.get("trueVotes", 0)
    false_votes = blockchain_result.get("falseVotes", 0)
    status = blockchain_result.get("status", "Under Review")
    
    claim_text = claims[0] if claims else "Unable to extract claim"
    
    # Determine emoji based on risk score
    if risk_score >= 80:
        emoji = "🚨"
    elif risk_score >= 60:
        emoji = "⚠️"
    elif risk_score >= 40:
        emoji = "🔎"
    else:
        emoji = "✅"
    
    # Determine final status
    final_status = status
    if status == "Under Review":
        total_votes = true_votes + false_votes
        if total_votes > 0:
            final_status = "Likely True" if true_votes > false_votes else "Likely False"
    
    report = f"""{emoji} *Claim Analysis*

📝 *Claim:* {claim_text}

🤖 *AI Risk Score:* {risk_score}%

📊 *Community Votes:*
✅ True: {true_votes}
❌ False: {false_votes}

📋 *Status:* {final_status}

💡 *Explanation:*
{explanation}

---
⚡ Powered by ThinkBaby - Web3 Fact Verification"""
    
    return report


def format_ivr_response(analysis: Dict, blockchain_result: Dict) -> str:
    """
    Format voice response for IVR (keep under 12 seconds)
    
    Args:
        analysis: Analysis result from claim_extractor
        blockchain_result: Result from get_claim_result
        
    Returns:
        Short voice script
    """
    risk_score = analysis.get("riskScore", 0)
    true_votes = blockchain_result.get("trueVotes", 0)
    false_votes = blockchain_result.get("falseVotes", 0)
    status = blockchain_result.get("status", "Under Review")
    
    total_votes = true_votes + false_votes
    
    # Short and clear responses for voice
    if status == "True" or (true_votes > false_votes and total_votes >= 3):
        return "This claim appears to be true based on community verification."
    elif status == "False" or (false_votes > true_votes and total_votes >= 3):
        return "This claim appears to be false. Please verify from official sources."
    elif risk_score >= 70:
        return "High risk detected. This claim is currently under review. We recommend verifying from official sources."
    else:
        return "This claim is currently under review by our community. Check back later for results."


def format_sms_response(analysis: Dict, blockchain_result: Dict) -> str:
    """
    Format short SMS response
    
    Args:
        analysis: Analysis result
        blockchain_result: Blockchain result
        
    Returns:
        SMS text (under 160 chars)
    """
    risk_score = analysis.get("riskScore", 0)
    true_votes = blockchain_result.get("trueVotes", 0)
    false_votes = blockchain_result.get("falseVotes", 0)
    
    if true_votes > false_votes:
        return f"✅ Likely TRUE (Votes: {true_votes}/{false_votes}) | Risk: {risk_score}%"
    elif false_votes > true_votes:
        return f"❌ Likely FALSE (Votes: {true_votes}/{false_votes}) | Risk: {risk_score}%"
    else:
        return f"🔍 Under Review | Risk Score: {risk_score}% | Votes: {true_votes}/{false_votes}"


def format_error_message(error_type: str = "general") -> str:
    """
    Format error message for users
    
    Args:
        error_type: Type of error
        
    Returns:
        User-friendly error message
    """
    errors = {
        "api_down": "⚠️ Our verification system is temporarily unavailable. Please try again in a few minutes.",
        "invalid_message": "❌ Unable to analyze this message. Please send a clear factual claim.",
        "rate_limit": "⏳ Too many requests. Please wait a moment before trying again.",
        "general": "❌ Something went wrong. Please try again later."
    }
    
    return errors.get(error_type, errors["general"])


def format_welcome_message() -> str:
    """
    Format welcome message for new users
    
    Returns:
        Welcome message
    """
    return """👋 Welcome to ThinkBaby!

I help verify claims using AI and blockchain-based community consensus.

📱 *How to use:*
1. Send me any claim or message
2. I'll analyze it for misinformation
3. Get instant credibility report

🚀 Try it now - send me any news or claim to verify!"""


def format_help_message() -> str:
    """
    Format help message
    
    Returns:
        Help instructions
    """
    return """❓ *ThinkBaby Help*

*What I do:*
🔍 Analyze claims for fake news
🤖 AI-powered risk assessment
⛓️ Blockchain-based verification
👥 Community voting system

*How to use:*
Just send me any claim or news message, and I'll verify it!

*Examples:*
"Government giving ₹5000 to students"
"New cryptocurrency launched by Tesla"

Need help? Visit: thinkbaby.io"""


# Example usage
if __name__ == "__main__":
    # Test formatting
    test_analysis = {
        "claims": ["Government giving ₹5000 to students"],
        "riskScore": 82,
        "explanation": "High-risk content detected."
    }
    
    test_blockchain = {
        "trueVotes": 3,
        "falseVotes": 12,
        "status": "Likely False"
    }
    
    report = format_whatsapp_report(test_analysis, test_blockchain)
    print(report)
