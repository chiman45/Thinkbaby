"""
IVR (Voice) Bot with RAG (Retrieval Augmented Generation)
Hackathon version - Voice-based claim verification with government records
"""

from fastapi import FastAPI, Form, Request
from twilio.twiml.voice_response import VoiceResponse, Gather
import os
from dotenv import load_dotenv
import sys

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.rag_system import GovernmentRecordRAG

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize RAG system
print("🚀 Initializing IVR Bot with RAG...")
rag = GovernmentRecordRAG()
rag.load_records()
print("✅ RAG system ready!")


def shorten_for_voice(text: str, max_chars: int = 300) -> str:
    """Shorten text for voice output (TTS limit)"""
    if len(text) <= max_chars:
        return text
    
    # Try to cut at sentence boundary
    sentences = text[:max_chars].split('.')
    if len(sentences) > 1:
        return '.'.join(sentences[:-1]) + '.'
    
    return text[:max_chars] + "..."


@app.post("/ivr/incoming")
async def incoming_call():
    """Handle incoming voice call"""
    
    print("\n📞 Incoming IVR call")
    
    response = VoiceResponse()
    
    # Welcome message
    response.say(
        "Hello! Welcome to the Government Records Verification System. "
        "I can help you verify claims and detect fraud.",
        voice="Polly.Joanna"
    )
    
    # Menu
    gather = Gather(
        num_digits=1,
        action='/ivr/process-input',
        method='POST',
        timeout=5
    )
    
    gather.say(
        "Press 1 to check system status. "
        "Press 2 to verify a claim by speaking. "
        "Press 3 to hear fraud statistics.",
        voice="Polly.Joanna"
    )
    
    response.append(gather)
    
    # If no input
    response.say("Sorry, I didn't receive any input. Goodbye!", voice="Polly.Joanna")
    
    return str(response)


@app.post("/ivr/process-input")
async def process_input(Digits: str = Form(...)):
    """Process menu selection"""
    
    print(f"🔢 User pressed: {Digits}")
    
    response = VoiceResponse()
    
    if Digits == '1':
        # System status
        stats = rag.get_stats()
        message = (f"System status: Online. "
                  f"I have access to {stats['total_records']} government records, "
                  f"including {stats['valid_records']} verified records and "
                  f"{stats['fraud_cases']} documented fraud cases. "
                  f"Ready to assist you.")
        
        response.say(shorten_for_voice(message), voice="Polly.Joanna")
        response.redirect('/ivr/incoming')
    
    elif Digits == '2':
        # Verify claim by voice
        response.say(
            "Please describe the claim or record you want to verify. "
            "For example, say: Check John Doe birth certificate. "
            "Speak after the beep.",
            voice="Polly.Joanna"
        )
        
        response.record(
            action='/ivr/process-speech',
            method='POST',
            max_length=30,
            transcribe=True,
            transcribe_callback='/ivr/transcription',
            play_beep=True
        )
    
    elif Digits == '3':
        # Fraud statistics
        verification = rag.verify_claim("fraud cases", top_k=3)
        fraud_count = verification['fraud_indicators']
        
        message = (f"Found {fraud_count} fraud cases in the database. "
                  f"Common fraud types include duplicate claims, false identities, "
                  f"and fabricated documents. "
                  f"Our system can detect these patterns automatically.")
        
        response.say(shorten_for_voice(message), voice="Polly.Joanna")
        response.redirect('/ivr/incoming')
    
    else:
        response.say("Invalid option. Please try again.", voice="Polly.Joanna")
        response.redirect('/ivr/incoming')
    
    return str(response)


@app.post("/ivr/process-speech")
async def process_speech():
    """Handle recording completion"""
    
    response = VoiceResponse()
    response.say(
        "Thank you. I'm processing your request. Please wait.",
        voice="Polly.Joanna"
    )
    
    # In real scenario, transcription callback will handle the verification
    response.pause(length=2)
    response.redirect('/ivr/incoming')
    
    return str(response)


@app.post("/ivr/transcription")
async def handle_transcription(TranscriptionText: str = Form(...)):
    """Handle speech transcription and verify claim"""
    
    print(f"\n🎙️ Transcribed: {TranscriptionText}")
    
    # This is called asynchronously after recording
    # In production, you'd store this and retrieve when user calls back
    
    # For now, verify the claim
    verification = rag.verify_claim(TranscriptionText, top_k=3)
    
    print(f"✅ Verification complete:")
    print(f"   Risk Level: {verification['risk_level']}")
    print(f"   Fraud Indicators: {verification['fraud_indicators']}")
    print(f"   Relevant Records: {len(verification['relevant_records'])}")
    
    return {"status": "processed"}


@app.post("/ivr/ask-question")
async def ask_question(question: str = Form(...)):
    """Direct question asking (for testing)"""
    
    print(f"\n❓ Question: {question}")
    
    response = VoiceResponse()
    
    # Use RAG to answer
    verification = rag.verify_claim(question, top_k=3)
    ai_response = rag.chat_with_rag(question, max_words=40)  # Shorter for voice
    
    # Add risk indicator
    if verification['risk_level'] == 'high':
        ai_response = "WARNING: Fraud indicators detected. " + ai_response
    
    # Shorten for voice
    voice_response = shorten_for_voice(ai_response, max_chars=300)
    
    response.say(voice_response, voice="Polly.Joanna")
    response.redirect('/ivr/incoming')
    
    return str(response)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = rag.get_stats()
    return {
        "status": "healthy",
        "service": "ivr_rag_bot",
        "rag_stats": stats
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting IVR Bot with RAG on port 3004")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=3004)
