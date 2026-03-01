# Voice Message Troubleshooting Guide

## Error: "Could not download voice message"

### Common Causes & Solutions

#### 1. **Twilio Media URL Expiration**
- Twilio media URLs expire after a few hours
- If testing with old messages, they won't download
- **Solution:** Send a fresh voice message

#### 2. **Webhook Configuration Issue**
- Bot must receive `MediaUrl0` parameter from Twilio
- Check Twilio webhook settings
- **Solution:** 
  - Go to Twilio Console → WhatsApp Sandbox Settings
  - Ensure webhook URL is correct: `https://your-ngrok-url.ngrok.io/webhook/whatsapp`
  - Must use HTTPS (ngrok provides this)

#### 3. **Authentication Mismatch**
- TWILIO_AUTH_TOKEN must match the account
- **Solution:** Copy fresh token from Twilio Console → Account → API keys & tokens

#### 4. **Network/Firewall Issues**
- Bot can't reach Twilio's media servers
- **Solution:** Check firewall/antivirus, try different network

#### 5. **Media URL Format Issue**
- Twilio changed media URL format
- **Solution:** Check logs for actual URL format, update download logic if needed

### Debug Steps

1. **Check Environment Variables:**
```bash
python test_voice_config.py
```

2. **Monitor Real-Time Logs:**
When voice message arrives, you'll see:
```
🎤 Processing voice message...
📱 User: whatsapp:+1234567890
🔗 Media URL: https://api.twilio.com/2010-04-01/Accounts/AC.../Media/ME...
🔑 Using Account SID: AC3a5a509d...
📡 Response status: 200
✅ Downloaded audio: C:\Users\...\tmpxxxx.ogg (12345 bytes)
```

If it fails, you'll see:
```
❌ Failed to download audio: 401
Response: Unauthorized - Invalid credentials
```

3. **Test with Text Message First:**
Send "TEST" to verify bot is working

4. **Check Twilio Console:**
- Go to Monitor → Logs  Debugger
- Look for errors related to media access

### Quick Fix Checklist

- [ ] Fresh voice message sent (not old)
- [ ] Ngrok tunnel is running
- [ ] Webhook URL updated in Twilio with ngrok URL
- [ ] TWILIO_AUTH_TOKEN in .env matches Twilio Console
- [ ] FFmpeg installed (run `ffmpeg -version`)
- [ ] Bot restarted after .env changes

### Still Not Working?

Check the terminal logs when sending voice message. Look for:
- HTTP status code (401 = auth issue, 404 = URL expired, 403 = permissions)
- Exact error message
- Media URL format

Share the logs for specific debugging.
