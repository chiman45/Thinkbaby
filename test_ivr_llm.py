"""
SIMPLE TEST FILE - IVR (Voice Calls) with Ollama
This tests voice calls → ngrok → your server → Ollama → voice response
Once verified, we'll integrate the full claim verification system
"""

import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

app = FastAPI(title="Test IVR with Ollama")

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"  # Change this to your installed model

def chat_with_ollama_voice(user_message: str) -> str:
    """
    Send message to Ollama and get SHORT response for voice
    IVR limit: ~30 seconds of speech = 60-80 words MAX
    """
    try:
        print(f"[Ollama Voice] Sending: {user_message}")
        
        # CRITICAL: Very short response for voice
        prompt = f"{user_message}\n\nIMPORTANT: Answer in 40 words or less. Be extremely brief and direct. Main point only."
        
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ollama_response = result.get("response", "No response available")
            
            # STRICT limit for voice: 300 chars max (~60 words)
            if len(ollama_response) > 300:
                # Cut at sentence boundary if possible
                truncated = ollama_response[:297]
                last_period = truncated.rfind('.')
                if last_period > 100:
                    ollama_response = truncated[:last_period+1]
                else:
                    ollama_response = truncated + "..."
            
            print(f"[Ollama Voice] Response ({len(ollama_response)} chars): {ollama_response}")
            return ollama_response
        else:
            return "Sorry, I encountered an error processing your request."
    
    except requests.exceptions.ConnectionError:
        return "Sorry, the AI service is not available right now."
    except Exception as e:
        print(f"[Ollama Voice] Error: {e}")
        return "Sorry, something went wrong."


@app.post("/ivr/incoming")
async def ivr_incoming():
    """
    Handle incoming voice call
    """
    print("\n" + "="*60)
    print("📞 Incoming Voice Call")
    print("="*60 + "\n")
    
    response = VoiceResponse()
    
    # Welcome message
    response.say(
        "Hello! Welcome to the test voice bot powered by Ollama. "
        "You can ask me any question about fake news, or press 1 to hear a test message.",
        voice='Polly.Joanna'
    )
    
    # Gather user input
    gather = Gather(
        num_digits=1,
        action='/ivr/process-input',
        method='POST',
        timeout=10
    )
    gather.say(
        "Press 1 for a test message, or press 2 to ask a question.",
        voice='Polly.Joanna'
    )
    response.append(gather)
    
    # If no input
    response.say("Sorry, I didn't receive any input. Goodbye!", voice='Polly.Joanna')
    response.hangup()
    
    print(f"📤 Sent IVR welcome\n")
    
    return Response(content=str(response), media_type="application/xml")


@app.post("/ivr/process-input")
async def ivr_process_input(Digits: str = Form(None)):
    """
    Process user digit input
    """
    print(f"\n📞 Processing input: {Digits}\n")
    
    response = VoiceResponse()
    
    if Digits == "1":
        # Test message
        response.say(
            "Test successful! Your voice call is working perfectly. "
            "Twilio connected to ngrok, which forwarded to your local server. "
            "All systems are operational.",
            voice='Polly.Joanna'
        )
        response.say("Goodbye!", voice='Polly.Joanna')
        response.hangup()
        
    elif Digits == "2":
        # Ask for voice input (speech-to-text)
        response.say(
            "Please ask your question after the beep.",
            voice='Polly.Joanna'
        )
        response.record(
            action='/ivr/process-speech',
            method='POST',
            max_length=30,
            transcribe=True,
            transcribe_callback='/ivr/transcription'
        )
        
    else:
        response.say("Invalid option. Goodbye!", voice='Polly.Joanna')
        response.hangup()
    
    return Response(content=str(response), media_type="application/xml")


@app.post("/ivr/process-speech")
async def ivr_process_speech(
    RecordingUrl: str = Form(None),
    RecordingSid: str = Form(None)
):
    """
    Handle recorded speech (waiting for transcription)
    """
    print(f"\n🎤 Speech recorded: {RecordingSid}")
    print(f"Recording URL: {RecordingUrl}\n")
    
    response = VoiceResponse()
    response.say(
        "Thank you. I'm processing your question. Please wait.",
        voice='Polly.Joanna'
    )
    
    # In real scenario, we'd wait for transcription
    # For now, just acknowledge
    response.pause(length=2)
    response.say(
        "I received your question. In a production system, I would transcribe and answer it. "
        "For this test, speech to text requires additional setup.",
        voice='Polly.Joanna'
    )
    response.hangup()
    
    return Response(content=str(response), media_type="application/xml")


@app.post("/ivr/transcription")
async def ivr_transcription(
    TranscriptionText: str = Form(None),
    RecordingSid: str = Form(None)
):
    """
    Handle transcription callback
    """
    print(f"\n📝 Transcription received: {TranscriptionText}\n")
    
    if TranscriptionText:
        # Get answer from Ollama
        answer = chat_with_ollama_voice(TranscriptionText)
        print(f"✅ Generated answer: {answer}\n")
    
    # Note: This is a callback, TwiML response won't play to caller
    # We'd need to use Twilio API to continue the call
    return {"status": "ok"}


@app.post("/ivr/ask-question")
async def ivr_ask_question(Question: str = Form(...)):
    """
    Direct question endpoint (for testing)
    Use this to test Ollama responses without speech recognition
    """
    print(f"\n❓ Direct question: {Question}\n")
    
    response = VoiceResponse()
    
    # Get answer from Ollama
    answer = chat_with_ollama_voice(Question)
    
    response.say(
        f"Here's the answer: {answer}",
        voice='Polly.Joanna'
    )
    response.pause(length=1)
    response.say("Goodbye!", voice='Polly.Joanna')
    response.hangup()
    
    print(f"✅ Sent answer via voice\n")
    
    return Response(content=str(response), media_type="application/xml")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "🎙️ Test IVR with Ollama",
        "endpoints": {
            "incoming": "/ivr/incoming",
            "ask": "/ivr/ask-question"
        },
        "instructions": [
            "1. Start Ollama: ollama serve",
            "2. Start this server: python test_ivr_llm.py",
            "3. Start ngrok: ngrok http 3004",
            "4. Configure Twilio voice webhook",
            "5. Call your Twilio number!"
        ]
    }


@app.get("/health")
async def health():
    """Health check"""
    # Test Ollama connection
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        ollama_status = "✅ Running" if response.status_code == 200 else "❌ Error"
    except:
        ollama_status = "❌ Not Running"
    
    return {
        "server": "✅ Running",
        "ollama": ollama_status,
        "model": OLLAMA_MODEL
    }


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🎙️  TEST IVR (Voice Calls) with Ollama")
    print("="*60)
    print("\n📋 Setup Instructions:\n")
    print("1. Make sure Ollama is running:")
    print("   ollama serve")
    print("")
    print("2. This IVR server will start on port 3004")
    print("")
    print("3. In another terminal, start ngrok:")
    print("   ngrok http 3004")
    print("")
    print("4. Copy the ngrok HTTPS URL")
    print("")
    print("5. Configure Twilio voice webhook:")
    print("   Go to: https://console.twilio.com/")
    print("   Phone Numbers → Your Number → Voice Configuration")
    print("   Set 'A CALL COMES IN' webhook to:")
    print("   URL: https://xxxx.ngrok.io/ivr/incoming")
    print("")
    print("6. Call your Twilio number to test!")
    print("")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=3004)
