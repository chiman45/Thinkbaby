"""
WhatsApp Bot Handler (Python/FastAPI)
Handles incoming WhatsApp messages via Twilio
Processes claims and returns verification results
"""

import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.claim_extractor import analyze_message
from modules.hash_generator import generate_claim_hash
from modules.backend_client import submit_claim_to_backend, get_claim_result, claim_exists
from utils.formatter import (
    format_whatsapp_report,
    format_error_message,
    format_welcome_message,
    format_help_message
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="ThinkBaby WhatsApp Bot")

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


async def handle_whatsapp_message(message_text: str, from_number: str) -> str:
    """
    Main message handler
    Process incoming WhatsApp messages
    
    Args:
        message_text: The message content
        from_number: Sender's phone number
        
    Returns:
        Response message
    """
    try:
        print(f"[WhatsApp] Message from {from_number}: {message_text}")
        
        # Handle commands
        lower_text = message_text.lower().strip()
        
        if lower_text in ['start', 'hi', 'hello']:
            return format_welcome_message()
        
        if lower_text == 'help':
            return format_help_message()
        
        # Analyze the message
        print("[WhatsApp] Analyzing message...")
        analysis = analyze_message(message_text)
        
        if not analysis.get("claims") or len(analysis["claims"]) == 0:
            return format_error_message("invalid_message")
        
        # Generate claim hash from first claim
        claim_text = analysis["claims"][0]
        claim_hash = generate_claim_hash(claim_text)
        print(f"[WhatsApp] Generated hash: {claim_hash}")
        
        # Check if claim exists in blockchain
        exists = claim_exists(claim_hash)
        
        if not exists:
            # Submit new claim to backend
            print("[WhatsApp] Submitting new claim to blockchain...")
            await submit_claim_to_backend(claim_hash, claim_text)
        
        # Get current result from blockchain
        print("[WhatsApp] Fetching blockchain result...")
        blockchain_result = get_claim_result(claim_hash)
        
        if not blockchain_result.get("success"):
            return format_error_message("api_down")
        
        # Format and return response
        report = format_whatsapp_report(
            analysis,
            blockchain_result.get("data", blockchain_result)
        )
        print("[WhatsApp] Report generated successfully")
        
        return report
    
    except Exception as e:
        print(f"[WhatsApp] Error handling message: {e}")
        return format_error_message("general")


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    request: Request = None
):
    """
    Webhook endpoint for incoming WhatsApp messages
    Twilio sends POST requests here
    """
    try:
        print(f"[Webhook] Received message: \"{Body}\" from {From}")
        
        # Process message
        response_message = await handle_whatsapp_message(Body, From)
        
        # Send response via Twilio
        twiml_response = MessagingResponse()
        twiml_response.message(response_message)
        
        return Response(content=str(twiml_response), media_type="application/xml")
    
    except Exception as e:
        print(f"[Webhook] Error: {e}")
        
        twiml_response = MessagingResponse()
        twiml_response.message(format_error_message("general"))
        
        return Response(content=str(twiml_response), media_type="application/xml")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "WhatsApp Bot",
        "python": True
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ThinkBaby WhatsApp Bot",
        "webhook": "/webhook/whatsapp",
        "health": "/health"
    }


# Run with: uvicorn whatsapp_bot:app --host 0.0.0.0 --port 3001 --reload
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("WHATSAPP_BOT_PORT", 3001))
    print(f"✅ WhatsApp Bot server running on port {port}")
    print(f"📱 Webhook URL: http://localhost:{port}/webhook/whatsapp")
    uvicorn.run(app, host="0.0.0.0", port=port)
