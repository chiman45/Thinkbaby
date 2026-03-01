# ============================================================
# VOICE MESSAGE SETUP GUIDE
# ============================================================

## Prerequisites

### 1. Install FFmpeg (Required for audio processing)

**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to C:\ffmpeg
3. Add C:\ffmpeg\bin to your System PATH
4. Verify: Run `ffmpeg -version` in command prompt

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

### 2. Install Python Dependencies

Already included in requirements.txt:
- SpeechRecognition==3.10.0 (Google Speech API)
- pydub==0.25.1 (Audio processing)
- openai-whisper (Optional, more accurate fallback)

### 3. Twilio Environment Variables

Add to your .env file:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
```

## How It Works

```
User sends Voice Message on WhatsApp
    ↓
Twilio forwards to webhook with MediaUrl
    ↓
Bot downloads audio (OGG format)
    ↓
Convert OGG → WAV
    ↓
Speech Recognition (Google API)
    ↓
Transcribed Text
    ↓
Language Detection
    ↓
Credibility Engine + Gemini AI
    ↓
Send text response back to user
```

## Supported Languages

Voice messages are automatically detected and transcribed in:
- English, Hindi, Tamil, Telugu, Marathi, Bengali
- Gujarati, Kannada, Malayalam, Punjabi, Urdu
- 50+ other languages supported by Google Speech API

## Usage Example

User sends voice: "क्या PM दे रहे हैं 5000 रुपये पेंशन?"
Bot replies:
```
🎤 Voice Message Received

📝 You said: क्या PM दे रहे हैं 5000 रुपये पेंशन?

🔍 FACT-CHECK RESULT
━━━━━━━━━━━━━━━━━━

❌ FALSE

💡 ANALYSIS:
यह दावा गलत है। PM द्वारा ऐसी कोई योजना घोषित नहीं की गई है...
```

## Troubleshooting

### "Could not understand voice message"
- Speak clearly and reduce background noise
- Ensure good microphone quality
- Try sending shorter voice messages (< 30 seconds)

### "Could not download voice message"
- Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env
- Verify Twilio webhook is properly configured

### "Audio processing error"
- Ensure FFmpeg is installed and in PATH
- Try: `ffmpeg -version` to verify

## Testing

Send a WhatsApp voice message to your bot number with any query like:
- "Is this news true?"
- "Fact check this claim"
- Any government scheme query

The bot will respond with transcription + fact-check results!
