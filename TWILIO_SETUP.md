# 🚀 Twilio Setup Guide

Complete step-by-step guide to configure Twilio for WhatsApp and IVR.

---

## 📱 Part 1: Twilio Account Setup

### Step 1: Create Twilio Account

1. Go to [https://www.twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Sign up for a free trial account
3. Verify your email and phone number
4. You'll get **$15 free trial credit**

### Step 2: Get Credentials

1. Login to [Twilio Console](https://console.twilio.com/)
2. Find your **Account SID** and **Auth Token** on the dashboard
3. Copy these to your `.env` file:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
```

---

## 💬 Part 2: WhatsApp Setup

### Step 1: Enable WhatsApp Sandbox

1. Go to [Twilio WhatsApp Sandbox](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. You'll see a **Sandbox number** (e.g., `+1 415 523 8886`)
3. Follow instructions to join the sandbox:
   - Open WhatsApp
   - Send the join code (e.g., `join <your-code>`) to the sandbox number

### Step 2: Configure Webhook

1. In Twilio Console, go to: **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Scroll down to **Sandbox Configuration**
3. Set **"When a message comes in"** to:
   ```
   http://your-server-url/webhook/whatsapp
   ```
4. Method: `POST`
5. Click **Save**

### Step 3: Get Your Server URL

**For Local Development (using ngrok):**

```bash
# Install ngrok
npm install -g ngrok

# Start your WhatsApp bot
npm run whatsapp

# In another terminal, expose port 3001
ngrok http 3001

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**Your Webhook URL:** `https://abc123.ngrok.io/webhook/whatsapp`

**For Production (Heroku/Railway/Render):**

Your webhook URL will be: `https://your-app.herokuapp.com/webhook/whatsapp`

### Step 4: Test WhatsApp Bot

1. Send a message to your WhatsApp Sandbox number
2. Try: `hi` → Should get welcome message
3. Try: `Government giving free money` → Should get claim analysis

---

## 📞 Part 3: IVR (Voice) Setup

### Step 1: Get a Twilio Phone Number

1. Go to [Phone Numbers](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
2. Click **Buy a Number**
3. Select country and search
4. Choose a number with **Voice** capabilities
5. Purchase the number (uses trial credit)

### Step 2: Configure Voice Webhook

1. Click on your purchased phone number
2. Scroll to **Voice Configuration**
3. Set **"A Call Comes In"** to:
   ```
   http://your-server-url/ivr/incoming
   ```
4. Method: `POST`
5. Click **Save**

### Step 3: Update .env

```env
TWILIO_PHONE_NUMBER=+1234567890
```

### Step 4: Test IVR

1. Call your Twilio phone number
2. Wait for the prompt
3. Speak your claim clearly
4. Listen to the verification result

---

## 🌐 Part 4: Deployment Options

### Option A: Heroku (Recommended for Hackathon)

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create thinkbaby-bot

# Set environment variables
heroku config:set TWILIO_ACCOUNT_SID=ACxxxxx
heroku config:set TWILIO_AUTH_TOKEN=xxxxx
heroku config:set BACKEND_API_URL=https://your-backend.com/api
heroku config:set TWILIO_PHONE_NUMBER=+1234567890

# For WhatsApp + IVR, you need to run both servers
# Create a Procfile
echo "web: node bots/whatsapp-bot.js" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Your URL will be: https://thinkbaby-bot.herokuapp.com
```

Then update Twilio webhooks to use `https://thinkbaby-bot.herokuapp.com`

### Option B: Railway.app

1. Go to [Railway.app](https://railway.app/)
2. Connect GitHub repo
3. Add environment variables in dashboard
4. Deploy automatically
5. Copy your Railway URL and update Twilio webhooks

### Option C: Render.com

1. Go to [Render.com](https://render.com/)
2. Create new Web Service
3. Connect GitHub repo
4. Set environment variables
5. Deploy
6. Use the Render URL for webhooks

### Option D: Local Development (ngrok)

```bash
# Terminal 1: Start WhatsApp bot
npm run whatsapp

# Terminal 2: Start IVR
npm run ivr

# Terminal 3: Expose WhatsApp bot
ngrok http 3001

# Terminal 4: Expose IVR
ngrok http 3002

# Update Twilio webhooks with ngrok URLs
# WhatsApp: https://xxxxx.ngrok.io/webhook/whatsapp
# IVR: https://yyyyy.ngrok.io/ivr/incoming
```

---

## 🐛 Troubleshooting

### WhatsApp Not Responding

**Problem:** Bot doesn't reply to WhatsApp messages

**Solutions:**
1. Check webhook URL is correct in Twilio Console
2. Verify server is running: `curl https://your-url/health`
3. Check Twilio debugger: [https://console.twilio.com/us1/monitor/debugger](https://console.twilio.com/us1/monitor/debugger)
4. View server logs: `heroku logs --tail` or check your terminal

### IVR Not Processing Speech

**Problem:** IVR can't understand spoken claims

**Solutions:**
1. Speak clearly and slowly
2. Avoid background noise
3. Check Twilio debugger for errors
4. Test with simple claims first

### Webhook URL Not Working

**Problem:** Twilio can't reach your webhook

**Solutions:**
1. Ensure URL uses HTTPS (required by Twilio)
2. Check firewall isn't blocking requests
3. For ngrok: restart ngrok and update webhook URL
4. Test endpoint: `curl -X POST https://your-url/webhook/whatsapp`

### Backend API Connection Failed

**Problem:** Can't connect to backend

**Solutions:**
1. Verify `BACKEND_API_URL` in `.env`
2. Check backend is running: `curl http://backend-url/api/health`
3. Ensure backend accepts requests from your server IP
4. Check CORS settings on backend

---

## 📊 Testing Tools

### Test WhatsApp Without Phone

Use Twilio API Explorer or curl:

```bash
curl -X POST https://your-url/webhook/whatsapp \
  -d "Body=Government giving free money" \
  -d "From=whatsapp:+1234567890"
```

### Test IVR Without Calling

```bash
curl -X POST https://your-url/ivr/incoming
```

### Monitor Twilio Requests

1. Go to [Twilio Debugger](https://console.twilio.com/us1/monitor/debugger)
2. See all incoming/outgoing messages and calls
3. View error messages and response codes

---

## 💰 Twilio Pricing (for reference)

**Free Trial:**
- $15 credit
- WhatsApp Sandbox: Free
- Voice calls: ~$0.01/min
- SMS: ~$0.0075/message

**Production Upgrade:**
- WhatsApp: $0.005/message (sender pays model)
- Voice: $0.0085-$0.02/min depending on country
- Phone number: ~$1/month

**For Hackathon:** Free trial is more than enough!

---

## ✅ Pre-Launch Checklist

Before going live:

- [ ] Twilio account verified
- [ ] Account SID and Auth Token in `.env`
- [ ] WhatsApp Sandbox joined and configured
- [ ] Phone number purchased (for IVR)
- [ ] Server deployed (Heroku/Railway/Render)
- [ ] Webhook URLs updated in Twilio Console
- [ ] Backend API URL configured
- [ ] Test WhatsApp bot with sample messages
- [ ] Test IVR with sample calls
- [ ] Check logs for errors
- [ ] Prepare demo for judges!

---

## 🎯 Demo Tips for Hackathon

1. **WhatsApp Demo:**
   - Show welcome message
   - Verify a fake news claim
   - Show risk score and voting results

2. **IVR Demo:**
   - Call the number
   - Speak a claim
   - Get voice response

3. **Technical Explanation:**
   - Show code architecture
   - Explain AI risk scoring
   - Show keccak256 hash matching Solidity
   - Demonstrate backend integration

---

## 📧 Support

**Twilio Support:**
- [Help Center](https://support.twilio.com/)
- [Community Forum](https://www.twilio.com/community)
- [API Docs](https://www.twilio.com/docs)

**This Project:**
- Check README.md
- View logs
- Test individual modules

---

**Good luck with your hackathon! 🚀**
