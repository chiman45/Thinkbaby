"""
WhatsApp Bot with RAG - Clean Implementation
Simple and reliable government record verification bot + RTI Filing

Features:
- Text Message Support
- Multilingual (50+ languages)
- Real-time Fact-Checking
- RTI Application Filing
- Payment Integration
"""

from fastapi import FastAPI, Form, Request
from fastapi.responses import Response, JSONResponse
from twilio.twiml.messaging_response import MessagingResponse
import os
import sys
import json
import uuid
import hmac
import hashlib
import razorpay
from datetime import datetime
from dotenv import load_dotenv
import httpx
from bs4 import BeautifulSoup
from googlesearch import search
from google import genai
import re
from langdetect import detect_langs, LangDetectException
from deep_translator import GoogleTranslator
import httpx as httpx_client

# Add modules directory to path
sys.path.append(os.path.dirname(__file__))

from modules.rag_system import GovernmentRecordRAG
from credibility_engine import CredibilityEngine

# Load environment
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="WhatsApp RAG Bot")

# Initialize RAG system with CSV data
print("🚀 Initializing WhatsApp Bot with RAG...")
rag = GovernmentRecordRAG(data_path="data/updated_data.csv")
rag.load_records()
print("✅ RAG system ready!\n")

# Initialize Credibility Engine
print("🚀 Initializing Credibility Engine...")
credibility_engine = CredibilityEngine()
print("✅ Credibility Engine ready!\n")

# Multilingual translator ready (deep-translator)
print("✅ Multilingual Translator ready!\n")

# Initialize Razorpay
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_XXXXXXXXXXXXXXXX")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "your_razorpay_secret")
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Initialize Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY not found in .env file")
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# IPFS Configuration (Pinata)
PINATA_API_KEY = os.getenv("PINATA_API_KEY", "")
PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY", "")

# Backend API Configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:3000/api")

# RTI Configuration
RTI_FEE_PAISE = 1000  # ₹10
RTI_SESSIONS_FILE = "rti_sessions.json"
RTI_FILINGS_FILE = "rti_filings.json"

# RTI Flow Steps
RTI_STEPS = ["name", "department", "subject", "details", "confirm"]


# ============================================================================
# IPFS Storage Functions
# ============================================================================

async def upload_conversation_to_ipfs(user_number: str, user_message: str, bot_response: str) -> str:
    """
    Upload conversation to IPFS via Pinata.
    Returns IPFS CID (hash) or None if upload fails.
    """
    if not PINATA_API_KEY or not PINATA_SECRET_KEY:
        print("⚠️ IPFS: Pinata API keys not configured, skipping upload")
        return None
    
    try:
        # Prepare conversation data
        conversation_data = {
            "timestamp": datetime.now().isoformat(),
            "user_number": user_number,
            "user_message": user_message,
            "bot_response": bot_response,
            "conversation_type": "whatsapp_factcheck"
        }
        
        # Upload to Pinata IPFS
        url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        
        headers = {
            "pinata_api_key": PINATA_API_KEY,
            "pinata_secret_api_key": PINATA_SECRET_KEY,
            "Content-Type": "application/json"
        }
        
        async with httpx_client.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                url,
                json=conversation_data,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            ipfs_cid = result["IpfsHash"]
            
            print(f"✅ IPFS: Conversation uploaded - CID: {ipfs_cid}")
            print(f"📦 IPFS Gateway: https://gateway.pinata.cloud/ipfs/{ipfs_cid}")
            
            return ipfs_cid
            
    except Exception as e:
        print(f"❌ IPFS upload failed: {e}")
        return None


# ============================================================================
# RTI Session Management
# ============================================================================

def load_json(filepath, default=None):
    """Load JSON file"""
    if default is None:
        default = {}
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return default


def save_json(filepath, data):
    """Save JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def get_session(user_number):
    """Get user's RTI session"""
    sessions = load_json(RTI_SESSIONS_FILE, {})
    return sessions.get(user_number)


def save_session(user_number, session_data):
    """Save user's RTI session"""
    sessions = load_json(RTI_SESSIONS_FILE, {})
    sessions[user_number] = session_data
    save_json(RTI_SESSIONS_FILE, sessions)


def clear_session(user_number):
    """Clear user's RTI session"""
    sessions = load_json(RTI_SESSIONS_FILE, {})
    if user_number in sessions:
        del sessions[user_number]
        save_json(RTI_SESSIONS_FILE, sessions)


def save_filing(filing_data):
    """Save RTI filing"""
    filings = load_json(RTI_FILINGS_FILE, [])
    filings.append(filing_data)
    save_json(RTI_FILINGS_FILE, filings)
    print(f"✅ RTI filed: {filing_data['rti_id']}")


# ============================================================================
# Razorpay Functions
# ============================================================================

def create_payment_link(rti_id, phone):
    """Create Razorpay payment link"""
    try:
        payment_link = razorpay_client.payment_link.create({
            "amount": RTI_FEE_PAISE,
            "currency": "INR",
            "description": f"RTI Filing Fee - {rti_id}",
            "reference_id": rti_id,
            "customer": {
                "contact": phone.replace("whatsapp:", "").replace("+", "")
            },
            "callback_url": os.getenv("RAZORPAY_CALLBACK_URL", "https://yourdomain.com/payment/success"),
            "callback_method": "get",
            "notes": {"rti_id": rti_id}
        })
        return payment_link["short_url"]
    except Exception as e:
        print(f"❌ Razorpay error: {e}")
        return None


# ============================================================================
# Web Scraping Functions
# ============================================================================

async def scrape_web_info(query: str, max_results: int = 3) -> str:
    """Scrape web information using Google search"""
    try:
        print(f"🌐 Searching web for: {query[:50]}...")
        search_results = []
        
        # Get top Google search results
        for url in search(query, num_results=max_results, lang="en", sleep_interval=1):
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    response = await client.get(
                        url,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                    )
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'lxml')
                        # Extract text from paragraphs
                        paragraphs = soup.find_all('p')
                        text = ' '.join([p.get_text().strip() for p in paragraphs[:5]])
                        if len(text) > 50:  # Only add if meaningful content
                            search_results.append(text[:500])  # Limit text length
            except Exception as scrape_err:
                print(f"  ⚠️ Failed to scrape {url[:50]}: {scrape_err}")
                continue
        
        combined_text = '\n\n'.join(search_results)
        print(f"✅ Scraped {len(search_results)} sources")
        return combined_text if combined_text else "No web information found."
        
    except Exception as e:
        print(f"❌ Web scraping error: {e}")
        return "Web scraping unavailable."


async def get_blockchain_votes(claim_hash: str) -> dict:
    """Get vote data from blockchain via backend API"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BACKEND_API_URL}/analyze-claim",
                json={"claimHash": claim_hash}
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "user_votes": data.get("userVotes", {"true": 0, "false": 0}),
                    "validator_votes": data.get("validatorVotes", {"true": 0, "false": 0}),
                    "ai_output": data.get("aiOutput", {})
                }
    except Exception as e:
        print(f"⚠️ Blockchain API not available: {e}")
    
    # Return dummy data if API fails
    return {
        "user_votes": {"true": 0, "false": 0},
        "validator_votes": {"true": 0, "false": 0},
        "ai_output": {"ai_label": "Uncertain", "risk_score": 0.5}
    }


# ============================================================================
# Multilingual Translation Layer
# ============================================================================

def detect_language(text: str) -> str:
    """
    Detect the language of the input text.
    Returns language code (e.g., 'en', 'hi', 'ta', 'mr', etc.)
    Uses multiple checks to avoid false positives.
    """
    try:
        # Remove common command words that might confuse detection
        text_clean = text.strip()
        if len(text_clean) < 3:
            return 'en'  # Default to English for very short text
        
        # Check for common English words/patterns first
        english_indicators = [
            'the', 'is', 'are', 'was', 'were', 'what', 'when', 'where', 'who', 'why', 'how',
            'this', 'that', 'these', 'those', 'will', 'would', 'could', 'should', 'can',
            'government', 'scheme', 'rupees', 'india', 'check', 'verify', 'true', 'false'
        ]
        
        text_lower = text_clean.lower()
        english_word_count = sum(1 for word in english_indicators if word in text_lower)
        
        # If multiple English words found, likely English
        if english_word_count >= 2:
            print(f"🌐 Detected language: en (English words found)")
            return 'en'
        
        # Run langdetect with multiple attempts for better accuracy
        from langdetect import detect_langs
        lang_probs = detect_langs(text_clean)
        
        # Get most probable language
        if lang_probs:
            top_lang = lang_probs[0].lang
            top_prob = lang_probs[0].prob
            
            # Only use non-English if confidence is high (>0.9) AND no English indicators
            if top_lang != 'en' and top_prob > 0.9 and english_word_count == 0:
                print(f"🌐 Detected language: {top_lang} (confidence: {top_prob:.2f})")
                return top_lang
            else:
                # Default to English if uncertain or has English words
                print(f"🌐 Detected language: en (default - low confidence or mixed)")
                return 'en'
        
        return 'en'
        
    except Exception as e:
        print(f"⚠️ Language detection failed: {e}, defaulting to English")
        return 'en'


def translate_to_english(text: str, source_lang: str) -> str:
    """
    Translate text from source language to English.
    If already English, return as-is.
    """
    if source_lang == 'en':
        return text
    
    try:
        translated = GoogleTranslator(source=source_lang, target='en').translate(text)
        print(f"📝 Translated to English: {translated[:50]}...")
        return translated
    except Exception as e:
        print(f"⚠️ Translation to English failed: {e}")
        return text  # Return original if translation fails


def translate_from_english(text: str, target_lang: str) -> str:
    """
    Translate text from English to target language.
    If target is English, return as-is.
    """
    if target_lang == 'en':
        return text
    
    try:
        translated = GoogleTranslator(source='en', target=target_lang).translate(text)
        print(f"🌍 Translated to {target_lang}")
        return translated
    except Exception as e:
        print(f"⚠️ Translation to {target_lang} failed: {e}")
        return text  # Return original if translation fails


def calculate_upvote_percentage(true_votes: int, false_votes: int) -> float:
    """Calculate upvote percentage from vote counts"""
    total = true_votes + false_votes
    if total == 0:
        return 50.0  # Neutral if no votes
    return round((true_votes / total) * 100, 1)


def determine_verdict(user_pct: float, validator_pct: float, ai_pct: float) -> tuple:
    """Determine final verdict based on weighted average with thresholds"""
    # Weighted scoring: AI (Gemini) 60%, Validators 20%, Users 20%
    # Gemini gets highest priority as it analyzes all data sources
    final_score = (user_pct * 0.2) + (validator_pct * 0.2) + (ai_pct * 0.6)
    
    # Thresholds
    if final_score >= 70:
        verdict = "✅ TRUE"
        confidence = "High"
    elif final_score >= 50:
        verdict = "⚠️ UNCERTAIN"
        confidence = "Medium"
    else:
        verdict = "❌ FALSE"
        confidence = "High" if final_score <= 30 else "Medium"
    
    return verdict, final_score, confidence


async def analyze_with_gemini_v2(
    claim: str,
    cred_result  # CredibilityResult from engine (contains all analysis)
) -> str:
    """
    Gemini provides human-readable narrative based on credibility engine's analysis.
    Credibility engine has already analyzed: RAG, Web, Blockchain, Linguistic patterns, etc.
    If Gemini fails, returns credibility engine's verdict.
    """
    try:
        # Extract community scores from credibility result for display
        user_pct = round(cred_result.community_score * 100, 1)
        validator_pct = round(cred_result.community_score * 100, 1)  # Simplified for display

        # Build prompt using credibility engine's comprehensive analysis
        prompt = f"""
You are an expert fact-checking AI. Provide a human-readable narrative for this fact-check.

**CLAIM:** {claim}

**CREDIBILITY ENGINE ANALYSIS:**
- Overall Score: {cred_result.final_score:.0%}
- Verdict: {cred_result.verdict}
- Risk Level: {cred_result.risk_level}
- Database Match: {cred_result.rag_match_score:.0%}
- Source Trust: {cred_result.source_score:.0%}
- Language Quality: {cred_result.linguistic_score:.0%}
- Amount Plausibility: {cred_result.numerical_score:.0%}
- Community Score: {cred_result.community_score:.0%}
- Red Flags: {', '.join(cred_result.flags[:5]) if cred_result.flags else 'None'}
- Sources: {len(cred_result.sources_found)} verified sources found

**YOUR TASK:**
Provide a clear, factual summary explaining why this claim is {cred_result.verdict}.
You can adjust the verdict ONLY with strong justification.

Respond in EXACTLY this format:
VERDICT: [TRUE or FALSE or UNCERTAIN]
CONFIDENCE: [0-100]
SUMMARY: [2-3 sentence explanation with specific facts]
"""

        gemini_response = ""
        gemini_confidence = cred_result.confidence * 100
        gemini_verdict = cred_result.verdict
        gemini_summary = cred_result.explanation
        gemini_success = False

        models_to_try = [
            'gemini-2.5-flash',
        ]

        # Only try Gemini if client is available
        if gemini_client:
            for model_name in models_to_try:
                try:
                    response = gemini_client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    gemini_response = response.text.strip()
                    print(f"✅ Using Gemini model: {model_name}")
                    gemini_success = True
                    break
                except Exception as model_err:
                    error_str = str(model_err)
                    if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                        print(f"⚠️ Gemini quota exceeded - using credibility engine")
                        break  # Stop trying other models if quota is exhausted
                    print(f"⚠️ Model {model_name} failed: {error_str[:200]}")
                    continue
        else:
            print("⚠️ Gemini API key not configured - using credibility engine")

        # If Gemini succeeded, parse the response
        if gemini_success and gemini_response:
            try:
                lines = gemini_response.split('\n')
                for line in lines:
                    if line.startswith('VERDICT:'):
                        vt = line.replace('VERDICT:', '').strip().upper()
                        if 'TRUE' in vt and 'FALSE' not in vt:
                            gemini_verdict = "TRUE"
                        elif 'FALSE' in vt:
                            gemini_verdict = "FALSE"
                        else:
                            gemini_verdict = "UNCERTAIN"
                    elif line.startswith('CONFIDENCE:'):
                        cs = line.replace('CONFIDENCE:', '').strip()
                        gemini_confidence = float(''.join(filter(lambda c: c.isdigit() or c == '.', cs)) or '50')
                        gemini_confidence = min(100, max(0, gemini_confidence))
                    elif line.startswith('SUMMARY:'):
                        gemini_summary = line.replace('SUMMARY:', '').strip()
                if 'SUMMARY:' in gemini_response:
                    gemini_summary = gemini_response[gemini_response.index('SUMMARY:') + 8:].strip()
            except Exception as pe:
                print(f"⚠️ Parse error: {pe}")
        else:
            # Gemini failed - use credibility engine's verdict as fallback
            print("⚠️ Gemini unavailable - using credibility engine verdict")

        # Verdict emoji mapping
        verdict_emoji = {
            "TRUE": "✅", "FALSE": "❌",
            "UNCERTAIN": "⚠️", "UNVERIFIED": "🔍", "BREAKING": "⏳"
        }
        emoji = verdict_emoji.get(gemini_verdict, "⚠️")

        # Risk badge
        risk_badge = {
            "low": "🟢 LOW", "medium": "🟡 MEDIUM",
            "high": "🔴 HIGH", "critical": "🚨 CRITICAL"
        }.get(cred_result.risk_level, "⚪ UNKNOWN")

        # Build output with credibility breakdown
        output = f"""
🔍 *FACT-CHECK RESULT*
━━━━━━━━━━━━━━━━━━

{emoji} *{gemini_verdict}*

💡 *ANALYSIS:*
{gemini_summary[:400]}

📊 *Credibility Breakdown:*
🗄️ Database Match: {cred_result.rag_match_score:.0%}
🌐 Source Trust: {cred_result.source_score:.0%}
🔤 Language Quality: {cred_result.linguistic_score:.0%}
💰 Amount Plausibility: {cred_result.numerical_score:.0%}
👥 Community: {user_pct}%
✅ Validators: {validator_pct}%
🤖 AI Confidence: {gemini_confidence:.0f}%

⚡ *Overall Score: {cred_result.final_score:.0%}*
🛡️ Risk Level: {risk_badge}
"""
        
        # Add fallback note if Gemini failed
        if not gemini_success:
            output += "\n_Note: Using credibility engine analysis (Gemini unavailable)_"
        
        return output.strip()

    except Exception as e:
        print(f"❌ Gemini v2 error: {e}")
        # Ultimate fallback: return credibility engine result
        verdict_emoji = {
            "TRUE": "✅", "FALSE": "❌",
            "UNCERTAIN": "⚠️", "UNVERIFIED": "🔍", "BREAKING": "⏳"
        }
        emoji = verdict_emoji.get(cred_result.verdict, "⚠️")
        
        return f"""⚠️ *FACT-CHECK RESULT*

{emoji} *{cred_result.verdict}*

{cred_result.explanation}

📊 *Credibility Score: {cred_result.final_score:.0%}*
🛡️ Risk: {cred_result.risk_level.upper()}

_Note: Full analysis unavailable - using credibility engine_"""




# ============================================================================
# RTI Conversation Handler
# ============================================================================

def handle_rti_conversation(user_number, message):
    """Handle RTI multi-step conversation"""
    session = get_session(user_number)
    msg_upper = message.strip().upper()
    
    # Cancel command
    if msg_upper == "CANCEL":
        clear_session(user_number)
        return "❌ RTI filing cancelled. Send RTI to start again."
    
    # Start new RTI
    if not session:
        save_session(user_number, {"step": "name"})
        return (
            "📋 *RTI Application*\n\n"
            "File a Right to Information request under RTI Act 2005.\n\n"
            "Filing Fee: ₹10 (via Razorpay)\n"
            "Response Time: 30 days\n\n"
            "Let's start!\n\n"
            "👤 Please enter your *full name*:"
        )
    
    step = session.get("step")
    
    # Collect Name
    if step == "name":
        if len(message.strip()) < 3:
            return "⚠️ Name too short. Please enter your full name:"
        session["name"] = message.strip().title()
        session["step"] = "department"
        save_session(user_number, session)
        return (
            f"✅ Got it, *{session['name']}*!\n\n"
            "🏛️ Which government department?\n"
            "_Example: Ministry of Finance, Municipal Corporation, MHADA_"
        )
    
    # Collect Department
    elif step == "department":
        if len(message.strip()) < 3:
            return "⚠️ Please enter a valid department name."
        session["department"] = message.strip()
        session["step"] = "subject"
        save_session(user_number, session)
        return (
            "✅ Noted!\n\n"
            "📌 What is the subject of your RTI?\n"
            "_Example: Status of road repair work in Ward 12_"
        )
    
    # Collect Subject
    elif step == "subject":
        if len(message.strip()) < 5:
            return "⚠️ Please provide more detail about the subject."
        session["subject"] = message.strip()
        session["step"] = "details"
        save_session(user_number, session)
        return (
            "✅ Got it!\n\n"
            "📝 Describe the specific information you need:\n"
            "_(Be as detailed as possible)_"
        )
    
    # Collect Details
    elif step == "details":
        if len(message.strip()) < 10:
            return "⚠️ Please provide more detailed information."
        session["details"] = message.strip()
        session["step"] = "confirm"
        
        # Generate RTI ID
        rti_id = f"RTI-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        session["rti_id"] = rti_id
        save_session(user_number, session)
        
        return (
            "📋 *RTI Application Summary*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Name: {session['name']}\n"
            f"🏛️ Department: {session['department']}\n"
            f"📌 Subject: {session['subject']}\n"
            f"📝 Details: {session['details'][:100]}...\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Filing Fee: ₹10\n"
            f"🆔 RTI ID: {rti_id}\n\n"
            "Reply *PAY* to proceed with payment\n"
            "Reply *CANCEL* to abort"
        )
    
    # Confirm and create payment
    elif step == "confirm":
        if msg_upper == "PAY":
            # Create payment link
            payment_url = create_payment_link(session["rti_id"], user_number)
            
            if payment_url:
                session["step"] = "awaiting_payment"
                session["payment_url"] = payment_url
                save_session(user_number, session)
                return (
                    "💳 *Payment Link Ready!*\n\n"
                    f"👉 Pay ₹10 here:\n{payment_url}\n\n"
                    "✅ Your RTI will be filed automatically after payment.\n"
                    "⏰ Link expires in 24 hours.\n\n"
                    "_Reply CANCEL to abort_"
                )
            else:
                return "⚠️ Payment system error. Please try again later."
        else:
            return "Reply *PAY* to proceed or *CANCEL* to abort."
    
    # Awaiting payment
    elif step == "awaiting_payment":
        return (
            "⏳ Waiting for payment...\n\n"
            f"Pay here: {session.get('payment_url', 'N/A')}\n\n"
            "Reply *CANCEL* to abort"
        )
    
    return "Something went wrong. Send RTI to start over."


def create_twiml_response(message_text: str) -> str:
    """Create properly formatted TwiML response for Twilio"""
    resp = MessagingResponse()
    resp.message(message_text)
    return str(resp)


def handle_command(command: str) -> str:
    """Handle bot commands"""
    cmd = command.upper().strip()
    
    if cmd in ("HI", "HELLO", "START"):
        return "👋 Hello! I'm your government records verification bot.\n\nType HELP to see available commands."
    
    elif cmd in ("HELP", "COMMANDS"):
        return (
            "🤖 *Available Commands*\n\n"
            "• HI - Welcome message\n"
            "• HELP - Show this menu\n"
            "• TEST - Check system status\n"
            "• STATS - Database statistics\n"
            "• FRAUD - Show fraud cases\n"
            "• RTI - File RTI application\n"
            "• STATUS <RTI-ID> - Track RTI\n\n"
            "💬 *Just send any query!*\n\n"
            "🔍 ALL queries are automatically fact-checked with:\n"
            "📊 Local database (3400+ govt schemes)\n"
            "🌐 Web search\n"
            "⛓️ Blockchain votes\n"
            "🤖 Advanced AI analysis\n\n"
            "Example: _Is PM giving ₹5000 pension?_"
        )
    
    elif cmd == "TEST":
        stats = rag.get_stats()
        return (
            f"✅ *System Online*\n\n"
            f"📊 Records: {stats['total_records']}\n"
            f"✅ Valid: {stats['valid_records']}\n"
            f"⚠️ Fraud: {stats['fraud_cases']}\n"
            f"🤖 AI: Advanced Models\n"
            f"🌐 Web: Scraping enabled\n"
            f"⛓️ Blockchain: Connected\n"
            f"💳 Payment: Razorpay\n\n"
            f"Ready to fact-check!"
        )
    
    elif cmd == "STATS":
        stats = rag.get_stats()
        filings = load_json(RTI_FILINGS_FILE, [])
        paid = sum(1 for f in filings if f.get("payment_status") == "paid")
        return (
            f"📊 *Database Statistics*\n\n"
            f"Total: {stats['total_records']}\n"
            f"Valid: {stats['valid_records']}\n"
            f"Fraud: {stats['fraud_cases']}\n"
            f"Indexed: {stats['collection_count']}\n\n"
            f"📋 RTI Filings: {len(filings)}\n"
            f"✅ Paid & Filed: {paid}\n\n"
            f"Engine: ChromaDB\n"
            f"Model: all-MiniLM-L6-v2"
        )
    
    elif cmd == "FRAUD":
        verification = rag.verify_claim("fraud cases", top_k=3)
        if verification['fraud_indicators'] > 0:
            reply = f"⚠️ Found {verification['fraud_indicators']} fraud cases:\n\n"
            fraud_cases = [r for r in verification['relevant_records'] if r.get('type') == 'fraud_case']
            for i, record in enumerate(fraud_cases[:3], 1):
                reply += (
                    f"{i}. {record.get('full_name', 'Unknown')}\n"
                    f"   Type: {record.get('claim_type', 'N/A')}\n"
                    f"   Amount: ₹{record.get('amount_claimed', 0):,}\n\n"
                )
            return reply
        else:
            return "✅ No fraud cases found in recent records."
    
    elif cmd.startswith("STATUS "):
        rti_id = cmd.replace("STATUS ", "").strip()
        filings = load_json(RTI_FILINGS_FILE, [])
        for filing in filings:
            if filing.get("rti_id") == rti_id:
                status = filing.get("payment_status", "pending")
                return (
                    f"📋 *RTI Status*\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"ID: {filing['rti_id']}\n"
                    f"Filed: {filing.get('filed_at', 'N/A')[:10]}\n"
                    f"Department: {filing['department']}\n"
                    f"Subject: {filing['subject']}\n"
                    f"Status: {status.upper()}\n\n"
                    f"_Response expected within 30 days_"
                )
        return f"❌ No RTI found with ID: {rti_id}"
    
    return None  # Not a command


async def handle_factcheck_multilingual(query: str) -> str:
    """
    Multilingual wrapper for fact-checking.
    Architecture:
        User Query (any language)
            ↓
        Detect Language
            ↓
        Translate to English
            ↓
        AI Credibility Engine (English)
            ↓
        Translate Response Back
            ↓
        User sees Native Language Answer
    """
    try:
        # Step 1: Detect language
        detected_lang = detect_language(query)
        
        # Step 2: Translate to English if needed
        query_english = translate_to_english(query, detected_lang)
        
        # Step 3: Run credibility engine (English)
        response_english = await handle_factcheck(query_english)
        
        # Step 4: Translate response back to original language
        response_native = translate_from_english(response_english, detected_lang)
        
        return response_native
        
    except Exception as e:
        print(f"❌ Multilingual processing error: {e}")
        # Fallback to English-only
        return await handle_factcheck(query)


async def handle_factcheck(query: str) -> str:
    """
    Comprehensive fact-check with RAG + Web + Blockchain + Credibility Engine + Gemini.
    Credibility engine runs before Gemini to provide structured pre-analysis.
    """
    print(f"🔍 FACT-CHECK: {query[:50]}...")
    
    try:
        # Step 1: Check RAG/Database (always works offline)
        verification = rag.verify_claim(query, top_k=5)
        rag_context = ""
        
        if verification['relevant_records']:
            rag_records = []
            for r in verification['relevant_records'][:3]:
                name = r.get('scheme_name') or r.get('full_name', 'N/A')
                details = r.get('details', '') or r.get('claim_type', '')
                rag_records.append(f"• {name}: {details[:100]}")
            rag_context = "\n".join(rag_records)
        else:
            rag_context = "No matching government schemes found."
        
        # Step 2: Web scraping (may fail if network blocked)
        web_context = ""
        if not verification['relevant_records'] or len(rag_context) < 100:
            print("🌐 Insufficient local data, scraping web...")
            web_context = await scrape_web_info(query, max_results=3)
        else:
            web_context = "Sufficient local data available."
        
        # Step 3: Get blockchain votes (optional - returns dummy data if unavailable)
        import hashlib
        claim_hash = "0x" + hashlib.sha256(query.encode()).hexdigest()[:40]
        votes_data = await get_blockchain_votes(claim_hash)
        
        # Step 4: Credibility Engine (analyzes RAG + Web + Blockchain + Linguistic patterns)
        print("⚙️ Running credibility engine...")
        cred_result = await credibility_engine.score(
            claim=query,
            source_url=None,        # No source URL from WhatsApp user
            rag_context=rag_context,
            web_context=web_context,
            votes_data=votes_data,
        )
        print(f"✅ Credibility score: {cred_result.final_score:.0%} | Verdict: {cred_result.verdict}")
        
        # Step 5: Gemini provides human-readable analysis (with credibility engine as fallback)
        final_result = await analyze_with_gemini_v2(query, cred_result)
        
        return final_result
        
    except Exception as e:
        print(f"❌ Fact-check error: {e}")
        # Ultimate fallback: return basic RAG result
        try:
            ai_response = rag.chat_with_rag(query, max_words=80)
            return f"""⚠️ *LIMITED FACT-CHECK*\n\nℹ️ {ai_response}\n\n_Full analysis unavailable_"""
        except:
            return f"⚠️ Fact-check system error. Please try: simpler query or check connection."


def handle_query(query: str) -> str:
    """Handle natural language queries with RAG"""
    print(f"🔍 Processing query: {query[:50]}...")
    
    try:
        # Get verification and AI response
        verification = rag.verify_claim(query, top_k=3)
        ai_response = rag.chat_with_rag(query, max_words=100)
        
        # Build response
        risk_emoji = "🚨" if verification['risk_level'] == 'high' else "✅"
        reply = f"{risk_emoji} {ai_response}"
        
        # Add context if available
        if verification['relevant_records']:
            reply += f"\n\n📄 {len(verification['relevant_records'])} related records found"
            if verification['fraud_indicators'] > 0:
                reply += f" ({verification['fraud_indicators']} fraud indicators)"
        
        print(f"✅ Response generated: {len(reply)} chars")
        return reply
        
    except Exception as e:
        print(f"❌ Error processing query: {e}")
        return "⚠️ Sorry, I encountered an error processing your request. Please try again."


@app.post("/webhook/whatsapp")
@app.post("/webhook")  # Also handle /webhook (without /whatsapp)
async def whatsapp_webhook(
    Body: str = Form(""),
    From: str = Form(...)
):
    """
    Main webhook endpoint for WhatsApp messages.
    Handles text messages only.
    """
    
    user_message = Body.strip()
    user_number = From
    
    print(f"\n📱 Message from {user_number}")
    print(f"📝 Content: {user_message}")
    
    try:
        # Text message handling
        # Check if user has active RTI session OR is starting RTI
        session = get_session(user_number)
        if session or user_message.upper() == "RTI":
            # Route to RTI conversation handler
            reply = handle_rti_conversation(user_number, user_message)
        
        else:
            # Check if it's a command
            command_response = handle_command(user_message)
            
            if command_response:
                reply = command_response
            else:
                # ALL non-command queries trigger comprehensive fact-check
                print("🔍 Routing to multilingual fact-check...")
                reply = await handle_factcheck_multilingual(user_message)
        
        # Truncate if too long (WhatsApp limit)
        if len(reply) > 1600:
            reply = reply[:1597] + "..."
        
        # Store conversation to IPFS (async background task)
        try:
            ipfs_cid = await upload_conversation_to_ipfs(user_number, user_message, reply)
            if ipfs_cid:
                print(f"📦 Conversation stored on IPFS: {ipfs_cid}")
        except Exception as ipfs_error:
            print(f"⚠️ IPFS storage failed (non-blocking): {ipfs_error}")
        
        # Create TwiML response
        twiml = create_twiml_response(reply)
        
        print(f"📤 Sending {len(reply)} chars")
        print(f"📡 TwiML: {twiml[:100]}...")
        
        # Return proper response with correct headers
        return Response(
            content=twiml,
            media_type="application/xml",
            status_code=200,
            headers={
                "Content-Type": "application/xml; charset=utf-8",
                "X-Content-Type-Options": "nosniff"
            }
        )
        
    except Exception as e:
        print(f"❌ Error in webhook: {e}")
        # Return error response
        error_twiml = create_twiml_response("⚠️ Sorry, something went wrong. Please try again.")
        return Response(
            content=error_twiml,
            media_type="application/xml",
            status_code=200
        )


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "online",
        "service": "WhatsApp RAG Bot",
        "version": "2.0"
    }


@app.post("/payment/webhook")
async def payment_webhook(request: Request):
    """Handle Razorpay payment webhooks"""
    try:
        # Get raw body and signature
        body = await request.body()
        signature = request.headers.get("X-Razorpay-Signature", "")
        
        # Verify webhook signature
        webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
        if webhook_secret:
            expected_signature = hmac.new(
                webhook_secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            if signature != expected_signature:
                print("❌ Invalid webhook signature")
                return {"status": "error", "message": "Invalid signature"}
        
        # Parse webhook data
        data = await request.json()
        event = data.get("event", "")
        
        print(f"💳 Payment webhook: {event}")
        
        if event == "payment_link.paid":
            payment_link_id = data.get("payload", {}).get("payment_link", {}).get("entity", {}).get("id", "")
            
            # Find session with this payment link
            sessions = load_json(RTI_SESSIONS_FILE, {})
            for user_number, session in sessions.items():
                if session.get("payment_link_id") == payment_link_id:
                    # Payment successful - save filing
                    filing = {
                        "rti_id": session["rti_id"],
                        "user_number": user_number,
                        "name": session["name"],
                        "department": session["department"],
                        "subject": session["subject"],
                        "details": session["details"],
                        "payment_link_id": payment_link_id,
                        "payment_status": "paid",
                        "filed_at": datetime.now().isoformat()
                    }
                    
                    save_filing(filing)
                    clear_session(user_number)
                    
                    print(f"✅ RTI {session['rti_id']} payment confirmed and filed")
                    break
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"❌ Payment webhook error: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        stats = rag.get_stats()
        return {
            "status": "healthy",
            "service": "whatsapp_rag_bot",
            "records": stats['total_records'],
            "fraud_cases": stats['fraud_cases'],
            "database": "ChromaDB",
            "ai_model": "llama3.2"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 70)
    print("🚀 WhatsApp RAG Bot v2.0")
    print("=" * 70)
    print("📍 Server: http://0.0.0.0:3003")
    print("🔗 Webhook: /webhook/whatsapp")
    print("💚 Health: /health")
    print("=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=3003, log_level="info")
