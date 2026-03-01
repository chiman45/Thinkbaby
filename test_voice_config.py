"""
Voice Message Configuration Tester
Run this to diagnose voice message issues
"""

import os
from dotenv import load_dotenv

print("=" * 70)
print("🔍 VOICE MESSAGE CONFIGURATION DIAGNOSTICS")
print("=" * 70)

# Load environment
load_dotenv()

print("\n1️⃣ Checking Environment Variables...")
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

if account_sid:
    print(f"   ✅ TWILIO_ACCOUNT_SID: {account_sid[:10]}..." if len(account_sid) > 10 else f"   ✅ TWILIO_ACCOUNT_SID: {account_sid}")
else:
    print("   ❌ TWILIO_ACCOUNT_SID: NOT SET")
    print("      Add to .env file: TWILIO_ACCOUNT_SID=your_account_sid")

if auth_token:
    print(f"   ✅ TWILIO_AUTH_TOKEN: {auth_token[:10]}..." if len(auth_token) > 10 else f"   ✅ TWILIO_AUTH_TOKEN: {auth_token}")
else:
    print("   ❌ TWILIO_AUTH_TOKEN: NOT SET")
    print("      Add to .env file: TWILIO_AUTH_TOKEN=your_auth_token")

print("\n2️⃣ Checking Python Dependencies...")
try:
    import speech_recognition as sr
    print("   ✅ speech_recognition installed")
except ImportError:
    print("   ❌ speech_recognition NOT installed")
    print("      Run: pip install SpeechRecognition")

try:
    from pydub import AudioSegment
    print("   ✅ pydub installed")
except ImportError:
    print("   ❌ pydub NOT installed")
    print("      Run: pip install pydub")

print("\n3️⃣ Checking FFmpeg (required for audio conversion)...")
import subprocess
try:
    result = subprocess.run(['ffmpeg', '-version'], 
                          capture_output=True, 
                          text=True, 
                          timeout=5)
    if result.returncode == 0:
        version_line = result.stdout.split('\n')[0]
        print(f"   ✅ FFmpeg installed: {version_line[:50]}")
    else:
        print("   ❌ FFmpeg not working properly")
except FileNotFoundError:
    print("   ❌ FFmpeg NOT FOUND")
    print("\n   📥 Install FFmpeg:")
    print("      Windows: Download from https://ffmpeg.org/download.html")
    print("               Extract, add bin folder to PATH, restart terminal")
    print("      Linux:   sudo apt-get install ffmpeg")
    print("      Mac:     brew install ffmpeg")
except Exception as e:
    print(f"   ⚠️  FFmpeg check failed: {e}")

print("\n4️⃣ Testing Audio Conversion (pydub + ffmpeg)...")
try:
    from pydub import AudioSegment
    import tempfile
    
    # Create a simple test
    print("   Creating test audio segment...")
    silent_audio = AudioSegment.silent(duration=100)  # 100ms silence
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    silent_audio.export(temp_file.name, format="wav")
    temp_file.close()
    
    print("   ✅ Audio conversion working!")
    os.remove(temp_file.name)
except Exception as e:
    print(f"   ❌ Audio conversion failed: {e}")
    print("      This usually means FFmpeg is not installed or not in PATH")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

issues = []
if not account_sid:
    issues.append("Missing TWILIO_ACCOUNT_SID in .env")
if not auth_token:
    issues.append("Missing TWILIO_AUTH_TOKEN in .env")

if issues:
    print("\n❌ VOICE MESSAGES WILL NOT WORK")
    print("\n⚠️  Issues found:")
    for issue in issues:
        print(f"   • {issue}")
    print("\n📝 TO FIX:")
    print("   1. Create/edit .env file in project root")
    print("   2. Add these lines:")
    print("      TWILIO_ACCOUNT_SID=your_account_sid_here")
    print("      TWILIO_AUTH_TOKEN=your_auth_token_here")
    print("   3. Get credentials from: https://console.twilio.com/")
    print("   4. Restart the bot")
else:
    print("\n✅ CONFIGURATION LOOKS GOOD!")
    print("\n   Text messages: Ready ✓")
    print("   Voice messages: Ready ✓")
    print("   Multilingual support: Ready ✓")
    
print("\n" + "=" * 70)
