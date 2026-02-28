"""
IVR (Interactive Voice Response) Handler (Python/FastAPI)
Handles voice calls via Twilio
Converts speech to text, verifies claims, and responds with voice
"""

import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.claim_extractor import analyze_message
from modules.hash_generator import generate_claim_hash
from modules.backend_client import submit_claim_to_backend, get_claim_result, claim_exists
from utils.formatter import format_ivr_response, format_error_message

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="ThinkBaby IVR Handler")

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


async def process_voice_claim(claim_text: str) -> str:
    """
    Process voice claim - core logic
    
    Args:
        claim_text: The transcribed claim text
        
    Returns:
        Voice response text
    """
    try:
        # Analyze the claim
        print("[IVR] Analyzing claim...")
        analysis = analyze_message(claim_text)
        
        if not analysis.get("claims") or len(analysis["claims"]) == 0:
            return "Sorry, I could not extract a verifiable claim from your input."
        
        # Generate hash
        main_claim = analysis["claims"][0]
        claim_hash = generate_claim_hash(main_claim)
        print(f"[IVR] Generated hash: {claim_hash}")
        
        # Check if claim exists
        exists = claim_exists(claim_hash)
        
        if not exists:
            # Submit new claim
            print("[IVR] Submitting new claim...")
            await submit_claim_to_backend(claim_hash, main_claim)
        
        # Get blockchain result
        print("[IVR] Fetching verification result...")
        blockchain_result = get_claim_result(claim_hash)
        
        if not blockchain_result.get("success"):
            return "Sorry, our verification system is temporarily unavailable. Please try again later."
        
        # Format voice response (short and clear)
        voice_response = format_ivr_response(
            analysis,
            blockchain_result.get("data", blockchain_result)
        )
        
        print(f"[IVR] Response generated: {voice_response}")
        return voice_response
    
    except Exception as e:
        print(f"[IVR] Error in process_voice_claim: {e}")
        return "An error occurred while processing your claim. Please try again."


@app.post("/ivr/incoming")
async def ivr_incoming(request: Request):
    """
    Main IVR handler - Entry point for incoming calls
    Provides voice menu and initiates claim verification
    """
    try:
        print("[IVR] Incoming call received")
        
        response = VoiceResponse()
        
        # Welcome message
        response.say(
            "Welcome to ThinkBaby, your AI-powered fact verification service.",
            voice="Polly.Joanna",
            language="en-US"
        )
        
        # Gather speech input
        gather = Gather(
            input='speech',
            timeout=5,
            speech_timeout='auto',
            action='/ivr/process-claim',
            method='POST',
            language='en-US'
        )
        
        gather.say(
            "Please speak the claim or news you want to verify. Speak clearly after the beep.",
            voice="Polly.Joanna"
        )
        
        response.append(gather)
        
        # If no input received
        response.say(
            "We did not receive your input. Please call back and try again. Goodbye.",
            voice="Polly.Joanna"
        )
        
        return Response(content=str(response), media_type="application/xml")
    
    except Exception as e:
        print(f"[IVR] Error in incoming handler: {e}")
        return handle_ivr_error()


@app.post("/ivr/process-claim")
async def ivr_process_claim(
    SpeechResult: str = Form(default=""),
    CallSid: str = Form(default=""),
    From: str = Form(default="")
):
    """
    Process the spoken claim
    Analyzes speech input and returns verification result
    """
    try:
        print(f"[IVR] Processing claim from {From}: \"{SpeechResult}\"")
        
        response = VoiceResponse()
        
        # Check if speech was captured
        if not SpeechResult or not SpeechResult.strip():
            response.say(
                "Sorry, I could not understand your claim. Please try again. Goodbye.",
                voice="Polly.Joanna"
            )
            return Response(content=str(response), media_type="application/xml")
        
        # Acknowledge receipt
        response.say(
            "Analyzing your claim. Please wait.",
            voice="Polly.Joanna"
        )
        
        # Process the claim
        response_message = await process_voice_claim(SpeechResult)
        
        # Speak the result (keep under 12 seconds)
        response.say(
            response_message,
            voice="Polly.Joanna",
            language="en-US"
        )
        
        # Closing message
        response.say(
            "Thank you for using ThinkBaby. Goodbye.",
            voice="Polly.Joanna"
        )
        
        return Response(content=str(response), media_type="application/xml")
    
    except Exception as e:
        print(f"[IVR] Error processing claim: {e}")
        return handle_ivr_error()


@app.post("/ivr/status")
async def ivr_status(
    CallStatus: str = Form(...),
    CallSid: str = Form(...)
):
    """Status callback - Track call status (optional)"""
    print(f"[IVR] Call {CallSid} status: {CallStatus}")
    return {"status": "ok"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "IVR Handler",
        "python": True
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ThinkBaby IVR Handler",
        "incoming_webhook": "/ivr/incoming",
        "process_webhook": "/ivr/process-claim",
        "health": "/health"
    }


def handle_ivr_error():
    """Handle IVR errors with user-friendly voice response"""
    response = VoiceResponse()
    response.say(
        "Sorry, we encountered a technical issue. Please try again later. Goodbye.",
        voice="Polly.Joanna"
    )
    return Response(content=str(response), media_type="application/xml")


# Run with: uvicorn ivr_handler:app --host 0.0.0.0 --port 3002 --reload
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("IVR_PORT", 3002))
    print(f"✅ IVR server running on port {port}")
    print(f"📞 Incoming call webhook: http://localhost:{port}/ivr/incoming")
    uvicorn.run(app, host="0.0.0.0", port=port)
