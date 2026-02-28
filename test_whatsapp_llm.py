"""
SIMPLE TEST FILE - WhatsApp Bot with Ollama
This is just for testing WhatsApp → ngrok → your server → Ollama → response flow
Once verified, we'll integrate the full claim verification system
"""

import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

app = FastAPI(title="Test WhatsApp Bot with Ollama")

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"  # Change this to your installed model

def chat_with_ollama(user_message: str, max_words: int = 100) -> str:
    """
    Send message to Ollama and get response
    WhatsApp limit: 1600 characters via Twilio
    """
    try:
        print(f"[Ollama] Sending: {user_message}")
        
        # Add instruction to keep response SHORT and focused
        prompt = f"{user_message}\n\nIMPORTANT: Answer in {max_words} words or less. Give only main points, be direct and concise."
        
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
            ollama_response = result.get("response", "No response from Ollama")
            
            # Truncate to 800 chars for conciseness
            if len(ollama_response) > 800:
                ollama_response = ollama_response[:797] + "..."
            
            print(f"[Ollama] Response ({len(ollama_response)} chars): {ollama_response[:100]}...")
            return ollama_response
        else:
            return f"Error: Ollama returned status {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return "⚠️ Error: Ollama is not running. Start it with: ollama serve"
    except Exception as e:
        print(f"[Ollama] Error: {e}")
        return f"Error communicating with Ollama: {str(e)}"


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    request: Request = None
):
    """
    Simple webhook for WhatsApp messages
    Sends to Ollama and returns response
    """
    try:
        user_message = Body.strip()
        from_number = From
        
        print(f"\n{'='*60}")
        print(f"📱 WhatsApp Message Received")
        print(f"From: {from_number}")
        print(f"Message: {user_message}")
        print(f"{'='*60}\n")
        
        # Handle simple commands
        if user_message.lower() in ['hi', 'hello', 'start']:
            response_text = """👋 Test Bot (Ollama)

Ask me anything!

Examples:
• What is fake news?
• Tell me a joke
• Any question

Type 'test' to verify connection 🚀"""
        
        elif user_message.lower() == 'test':
            response_text = """✅ TEST SUCCESSFUL!

✓ Twilio → ngrok → Server → Ollama
✓ All systems working!

Ready to go! 🎉"""
        
        else:
            # Send to Ollama for real conversation
            response_text = chat_with_ollama(user_message)
        
        # Ensure response fits WhatsApp limit (1600 chars)
        if len(response_text) > 1600:
            response_text = response_text[:1597] + "..."
        
        # Send response via Twilio
        twiml_response = MessagingResponse()
        twiml_response.message(response_text)
        
        twiml_str = str(twiml_response)
        print(f"✅ Sent response ({len(response_text)} chars): {response_text[:100]}...")
        print(f"📤 TwiML: {twiml_str}\n")
        
        return Response(content=twiml_str, media_type="application/xml")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        
        twiml_response = MessagingResponse()
        twiml_response.message(f"⚠️ Error: {str(e)}")
        
        return Response(content=str(twiml_response), media_type="application/xml")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "🚀 Test WhatsApp Bot with Ollama",
        "webhook": "/webhook/whatsapp",
        "instructions": [
            "1. Start Ollama: ollama serve",
            "2. Pull model: ollama pull llama3.2",
            "3. Start this server: python test_whatsapp_llm.py",
            "4. Start ngrok: ngrok http 3001",
            "5. Configure Twilio webhook with ngrok URL",
            "6. Send WhatsApp message to test!"
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
    print("🧪 TEST WhatsApp Bot with Ollama")
    print("="*60)
    print("\n📋 Setup Instructions:\n")
    print("1. Make sure Ollama is running:")
    print("   ollama serve")
    print("")
    print("2. Pull a model (if not already):")
    print("   ollama pull llama3.2")
    print("   (or: llama3, llama2, mistral, etc.)")
    print("")
    print("3. This server will start on port 3003")
    print("")
    print("4. In another terminal, start ngrok:")
    print("   ngrok http 3003")
    print("")
    print("5. Copy the ngrok HTTPS URL")
    print("")
    print("6. Configure Twilio webhook:")
    print("   URL: https://xxxx.ngrok.io/webhook/whatsapp")
    print("")
    print("7. Send a WhatsApp message to +14155238886")
    print("")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=3003)
