"""
Claim Extraction Module (Python)
Analyzes messages to extract claims, calculate risk scores, and generate explanations
"""

import re
from datetime import datetime
from typing import List, Dict, Optional
import requests


def analyze_message(message_text: str) -> Dict:
    """
    Analyzes a message to extract claims and calculate risk
    
    Args:
        message_text: The text message to analyze
        
    Returns:
        Dictionary with claims, risk score, and explanation
    """
    try:
        # Input validation
        if not message_text or not message_text.strip():
            raise ValueError("Message text cannot be empty")
        
        # Perform analysis
        analysis = perform_analysis(message_text)
        
        return {
            "claims": analysis["claims"],
            "riskScore": analysis["risk_score"],
            "explanation": analysis["explanation"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        print(f"Error in analyze_message: {e}")
        raise Exception(f"Claim extraction failed: {str(e)}")


def perform_analysis(text: str) -> Dict:
    """
    Performs the actual analysis logic
    Can be extended to call external AI APIs (OpenAI, Google Gemini, etc.)
    """
    # Normalize text
    normalized_text = text.strip().lower()
    
    # Extract claims
    claims = extract_claims(text)
    
    # Calculate risk score
    risk_score = calculate_risk_score(normalized_text, claims)
    
    # Generate explanation
    explanation = generate_explanation(normalized_text, risk_score, claims)
    
    return {
        "claims": claims,
        "risk_score": risk_score,
        "explanation": explanation
    }


def extract_claims(text: str) -> List[str]:
    """
    Extracts atomic claims from text
    For MVP: Splits by sentences, can be enhanced with AI
    """
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    # For MVP, treat each sentence as a potential claim
    # In production, use NLP/LLM to extract actual factual claims
    return sentences[:3]  # Limit to top 3 claims


def calculate_risk_score(text: str, claims: List[str]) -> int:
    """
    Calculates risk score (0-100) based on content analysis
    """
    base_risk = 50  # Start at neutral
    
    # High-risk keywords and patterns
    urgent_keywords = ['immediately', 'urgent', 'breaking', 'alert', 'warning']
    financial_keywords = ['money', 'cash', 'prize', 'won', 'lottery', 'reward', '₹', '$', 'rs']
    government_keywords = ['government', 'minister', 'official', 'scheme', 'policy']
    unverified_phrases = ['forward this', 'share immediately', 'before it\'s deleted', 
                          'they don\'t want you to know']
    
    # Check for urgent language
    if any(keyword in text for keyword in urgent_keywords):
        base_risk += 15
    
    # Check for financial claims
    if any(keyword in text for keyword in financial_keywords):
        base_risk += 20
    
    # Check for government-related claims
    if any(keyword in text for keyword in government_keywords):
        base_risk += 10
    
    # Check for viral sharing patterns
    if any(phrase in text for phrase in unverified_phrases):
        base_risk += 25
    
    # Check for all caps (shouting)
    caps_count = sum(1 for c in text if c.isupper())
    caps_ratio = caps_count / len(text) if len(text) > 0 else 0
    if caps_ratio > 0.5:
        base_risk += 10
    
    # Check for excessive punctuation
    excessive_punctuation = len(re.findall(r'[!?]{2,}', text))
    if excessive_punctuation > 2:
        base_risk += 10
    
    # Ensure score is within 0-100 range
    return min(max(round(base_risk), 0), 100)


def generate_explanation(text: str, risk_score: int, claims: List[str]) -> str:
    """
    Generates explanation for the risk assessment
    """
    explanations = []
    
    if risk_score >= 80:
        explanations.append("High-risk content detected.")
    elif risk_score >= 60:
        explanations.append("Moderate risk detected.")
    elif risk_score >= 40:
        explanations.append("Some suspicious elements found.")
    else:
        explanations.append("Content appears relatively neutral.")
    
    # Add specific findings
    if any(keyword in text for keyword in ['government', 'minister']):
        explanations.append("Contains government-related claims requiring verification.")
    
    if any(keyword in text for keyword in ['₹', 'rs', 'money', 'prize']):
        explanations.append("Contains financial claims. Verify through official sources.")
    
    if any(phrase in text for phrase in ['forward', 'share']):
        explanations.append("Shows viral sharing patterns common in misinformation.")
    
    if len(explanations) == 1:
        explanations.append("Recommend verification through official sources and fact-checking websites.")
    
    return " ".join(explanations)


def call_ai_api(text: str) -> Optional[Dict]:
    """
    Optional: Call external AI API for advanced analysis
    Uncomment and configure when AI API is available
    """
    # Example for OpenAI, Google Gemini, or custom AI service
    # api_key = os.getenv('AI_API_KEY')
    # api_url = os.getenv('AI_API_URL')
    
    # response = requests.post(
    #     api_url,
    #     json={
    #         'prompt': f'Analyze this message for fake news risk and extract claims:\n\n{text}',
    #         'max_tokens': 200
    #     },
    #     headers={
    #         'Authorization': f'Bearer {api_key}',
    #         'Content-Type': 'application/json'
    #     }
    # )
    
    # return response.json()
    pass


# Example usage
if __name__ == "__main__":
    test_message = "Government giving ₹5000 to all students! Forward immediately!"
    result = analyze_message(test_message)
    print(f"Claims: {result['claims']}")
    print(f"Risk Score: {result['riskScore']}%")
    print(f"Explanation: {result['explanation']}")
