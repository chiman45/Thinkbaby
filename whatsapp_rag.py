"""
WhatsApp Bot with RAG - Clean Implementation
Simple and reliable government record verification bot + RTI Filing
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

# Add modules directory to path
sys.path.append(os.path.dirname(__file__))

from modules.rag_system import GovernmentRecordRAG

# Load environment
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="WhatsApp RAG Bot")

# Initialize RAG system
print("🚀 Initializing WhatsApp Bot with RAG...")
rag = GovernmentRecordRAG()
rag.load_records()
print("✅ RAG system ready!\n")

# Initialize Razorpay
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_XXXXXXXXXXXXXXXX")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "your_razorpay_secret")
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# RTI Configuration
RTI_FEE_PAISE = 1000  # ₹10
RTI_SESSIONS_FILE = "rti_sessions.json"
RTI_FILINGS_FILE = "rti_filings.json"

# RTI Flow Steps
RTI_STEPS = ["name", "department", "subject", "details", "confirm"]


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
            "💬 Or just ask me anything about government records!"
        )
    
    elif cmd == "TEST":
        stats = rag.get_stats()
        return (
            f"✅ *System Online*\n\n"
            f"📊 Records: {stats['total_records']}\n"
            f"✅ Valid: {stats['valid_records']}\n"
            f"⚠️ Fraud: {stats['fraud_cases']}\n"
            f"🤖 AI: llama3.2\n"
            f"💳 Payment: Razorpay\n\n"
            f"Ready to help!"
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
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """Main webhook endpoint for WhatsApp messages"""
    
    user_message = Body.strip()
    user_number = From
    
    print(f"\n📱 Message from {user_number}")
    print(f"📝 Content: {user_message}")
    
    try:
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
                # Handle as natural language query
                reply = handle_query(user_message)
        
        # Truncate if too long (WhatsApp limit)
        if len(reply) > 1600:
            reply = reply[:1597] + "..."
        
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
