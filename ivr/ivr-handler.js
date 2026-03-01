/**
 * IVR (Interactive Voice Response) Handler
 * Handles voice calls via Twilio
 * Converts speech to text, verifies claims, and responds with voice
 */

require('dotenv').config();
const express = require('express');
const twilio = require('twilio');

// Import modules
const { analyzeMessage } = require('../modules/claimExtractor');
const { generateClaimHash } = require('../modules/hashGenerator');
const { submitClaimToBackend, getClaimResult, claimExists } = require('../modules/backendClient');
const { formatIVRResponse, formatErrorMessage } = require('../utils/formatter');

// Initialize Express app
const app = express();
app.use(express.urlencoded({ extended: false }));
app.use(express.json());

// Twilio configuration
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;

/**
 * Main IVR handler - Entry point for incoming calls
 * Provides voice menu and initiates claim verification
 */
app.post('/ivr/incoming', async (req, res) => {
  try {
    console.log('[IVR] Incoming call received');
    
    const twiml = new twilio.twiml.VoiceResponse();
    
    // Welcome message
    twiml.say({
      voice: 'Polly.Joanna',
      language: 'en-US'
    }, 'Welcome to ThinkBaby, your AI-powered fact verification service.');

    // Gather speech input
    const gather = twiml.gather({
      input: 'speech',
      timeout: 5,
      speechTimeout: 'auto',
      action: '/ivr/process-claim',
      method: 'POST',
      language: 'en-US'
    });

    gather.say({
      voice: 'Polly.Joanna'
    }, 'Please speak the claim or news you want to verify. Speak clearly after the beep.');

    // If no input received
    twiml.say({
      voice: 'Polly.Joanna'
    }, 'We did not receive your input. Please call back and try again. Goodbye.');

    res.type('text/xml');
    res.send(twiml.toString());

  } catch (error) {
    console.error('[IVR] Error in incoming handler:', error);
    handleIVRError(res);
  }
});

/**
 * Process the spoken claim
 * Analyzes speech input and returns verification result
 */
app.post('/ivr/process-claim', async (req, res) => {
  try {
    const speechResult = req.body.SpeechResult || '';
    const callSid = req.body.CallSid || '';
    const fromNumber = req.body.From || '';

    console.log(`[IVR] Processing claim from ${fromNumber}: "${speechResult}"`);

    const twiml = new twilio.twiml.VoiceResponse();

    // Check if speech was captured
    if (!speechResult || speechResult.trim().length === 0) {
      twiml.say({
        voice: 'Polly.Joanna'
      }, 'Sorry, I could not understand your claim. Please try again. Goodbye.');
      
      res.type('text/xml');
      return res.send(twiml.toString());
    }

    // Acknowledge receipt
    twiml.say({
      voice: 'Polly.Joanna'
    }, 'Analyzing your claim. Please wait.');

    // Process the claim
    const responseMessage = await processVoiceClaim(speechResult);

    // Speak the result (keep under 12 seconds)
    twiml.say({
      voice: 'Polly.Joanna',
      language: 'en-US'
    }, responseMessage);

    // Offer to check another claim
    twiml.say({
      voice: 'Polly.Joanna'
    }, 'Thank you for using ThinkBaby. Goodbye.');

    res.type('text/xml');
    res.send(twiml.toString());

  } catch (error) {
    console.error('[IVR] Error processing claim:', error);
    handleIVRError(res);
  }
});

/**
 * Process voice claim - core logic
 * @param {string} claimText - The transcribed claim text
 * @returns {Promise<string>} Voice response text
 */
async function processVoiceClaim(claimText) {
  try {
    // Analyze the claim
    console.log('[IVR] Analyzing claim...');
    const analysis = await analyzeMessage(claimText);

    if (!analysis.claims || analysis.claims.length === 0) {
      return 'Sorry, I could not extract a verifiable claim from your input.';
    }

    // Generate hash
    const mainClaim = analysis.claims[0];
    const claimHash = generateClaimHash(mainClaim);
    console.log(`[IVR] Generated hash: ${claimHash}`);

    // Check if claim exists
    const exists = await claimExists(claimHash);

    if (!exists) {
      // Submit new claim
      console.log('[IVR] Submitting new claim...');
      await submitClaimToBackend(claimHash, mainClaim);
    }

    // Get blockchain result
    console.log('[IVR] Fetching verification result...');
    const blockchainResult = await getClaimResult(claimHash);

    if (!blockchainResult.success) {
      return 'Sorry, our verification system is temporarily unavailable. Please try again later.';
    }

    // Format voice response (short and clear)
    const voiceResponse = formatIVRResponse(analysis, blockchainResult.data || blockchainResult);
    
    console.log('[IVR] Response generated:', voiceResponse);
    return voiceResponse;

  } catch (error) {
    console.error('[IVR] Error in processVoiceClaim:', error);
    return 'An error occurred while processing your claim. Please try again.';
  }
}

/**
 * Handle IVR errors with user-friendly voice response
 */
function handleIVRError(res) {
  const twiml = new twilio.twiml.VoiceResponse();
  
  twiml.say({
    voice: 'Polly.Joanna'
  }, 'Sorry, we encountered a technical issue. Please try again later. Goodbye.');

  res.type('text/xml');
  res.send(twiml.toString());
}

/**
 * Status callback - Track call status (optional)
 */
app.post('/ivr/status', (req, res) => {
  const callStatus = req.body.CallStatus;
  const callSid = req.body.CallSid;
  
  console.log(`[IVR] Call ${callSid} status: ${callStatus}`);
  res.sendStatus(200);
});

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'IVR Handler',
    timestamp: new Date().toISOString()
  });
});

/**
 * Initiate outbound call (for testing or notifications)
 */
async function makeVerificationCall(toNumber, message) {
  try {
    const twilioClient = twilio(accountSid, authToken);
    const twilioPhoneNumber = process.env.TWILIO_PHONE_NUMBER;

    const call = await twilioClient.calls.create({
      url: `${process.env.IVR_BASE_URL}/ivr/outbound?message=${encodeURIComponent(message)}`,
      to: toNumber,
      from: twilioPhoneNumber
    });

    console.log(`[IVR] Outbound call initiated: ${call.sid}`);
    return { success: true, callSid: call.sid };

  } catch (error) {
    console.error('[IVR] Error making call:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Outbound call handler (for notifications)
 */
app.post('/ivr/outbound', (req, res) => {
  const message = req.query.message || 'This is a test call from ThinkBaby.';
  
  const twiml = new twilio.twiml.VoiceResponse();
  twiml.say({
    voice: 'Polly.Joanna'
  }, message);

  res.type('text/xml');
  res.send(twiml.toString());
});

/**
 * Alternative: SMS fallback if call fails
 */
app.post('/ivr/fallback', (req, res) => {
  const twiml = new twilio.twiml.VoiceResponse();
  
  twiml.say({
    voice: 'Polly.Joanna'
  }, 'Sorry, we are experiencing technical difficulties. Please try texting your claim to our WhatsApp number instead. Goodbye.');

  res.type('text/xml');
  res.send(twiml.toString());
});

/**
 * Start the server
 */
const PORT = process.env.IVR_PORT || 3002;

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`✅ IVR server running on port ${PORT}`);
    console.log(`📞 Incoming call webhook: http://localhost:${PORT}/ivr/incoming`);
    console.log(`🔧 Environment: ${process.env.NODE_ENV || 'development'}`);
  });
}

module.exports = {
  app,
  processVoiceClaim,
  makeVerificationCall
};
