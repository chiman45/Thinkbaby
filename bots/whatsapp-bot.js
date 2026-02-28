/**
 * WhatsApp Bot Handler
 * Handles incoming WhatsApp messages via Twilio
 * Processes claims and returns verification results
 */

require('dotenv').config();
const express = require('express');
const twilio = require('twilio');

// Import modules
const { analyzeMessage } = require('../modules/claimExtractor');
const { generateClaimHash } = require('../modules/hashGenerator');
const { submitClaimToBackend, getClaimResult, claimExists } = require('../modules/backendClient');
const { 
  formatWhatsAppReport, 
  formatErrorMessage, 
  formatWelcomeMessage,
  formatHelpMessage 
} = require('../utils/formatter');

// Initialize Express app
const app = express();
app.use(express.urlencoded({ extended: false }));
app.use(express.json());

// Twilio configuration
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const twilioClient = twilio(accountSid, authToken);

// Validate Twilio webhook (optional but recommended for production)
const validateTwilioRequest = (req, res, next) => {
  if (process.env.NODE_ENV === 'production') {
    const twilioSignature = req.headers['x-twilio-signature'];
    const url = `${req.protocol}://${req.get('host')}${req.originalUrl}`;
    
    if (!twilio.validateRequest(authToken, twilioSignature, url, req.body)) {
      return res.status(403).send('Forbidden');
    }
  }
  next();
};

/**
 * Main message handler
 * Process incoming WhatsApp messages
 */
async function handleWhatsAppMessage(messageText, fromNumber) {
  try {
    console.log(`[WhatsApp] Message from ${fromNumber}: ${messageText}`);

    // Handle commands
    const lowerText = messageText.toLowerCase().trim();
    
    if (lowerText === 'start' || lowerText === 'hi' || lowerText === 'hello') {
      return formatWelcomeMessage();
    }
    
    if (lowerText === 'help') {
      return formatHelpMessage();
    }

    // Analyze the message
    console.log('[WhatsApp] Analyzing message...');
    const analysis = await analyzeMessage(messageText);
    
    if (!analysis.claims || analysis.claims.length === 0) {
      return formatErrorMessage('invalid_message');
    }

    // Generate claim hash from first claim
    const claimText = analysis.claims[0];
    const claimHash = generateClaimHash(claimText);
    console.log(`[WhatsApp] Generated hash: ${claimHash}`);

    // Check if claim exists in blockchain
    const exists = await claimExists(claimHash);
    
    if (!exists) {
      // Submit new claim to backend
      console.log('[WhatsApp] Submitting new claim to blockchain...');
      await submitClaimToBackend(claimHash, claimText);
    }

    // Get current result from blockchain
    console.log('[WhatsApp] Fetching blockchain result...');
    const blockchainResult = await getClaimResult(claimHash);

    if (!blockchainResult.success) {
      return formatErrorMessage('api_down');
    }

    // Format and return response
    const report = formatWhatsAppReport(analysis, blockchainResult.data || blockchainResult);
    console.log('[WhatsApp] Report generated successfully');
    
    return report;

  } catch (error) {
    console.error('[WhatsApp] Error handling message:', error);
    return formatErrorMessage('general');
  }
}

/**
 * Webhook endpoint for incoming WhatsApp messages
 * Twilio sends POST requests here
 */
app.post('/webhook/whatsapp', validateTwilioRequest, async (req, res) => {
  try {
    const incomingMessage = req.body.Body || '';
    const fromNumber = req.body.From || '';
    
    console.log(`[Webhook] Received message: "${incomingMessage}" from ${fromNumber}`);

    // Process message
    const responseMessage = await handleWhatsAppMessage(incomingMessage, fromNumber);

    // Send response via Twilio
    const twiml = new twilio.twiml.MessagingResponse();
    twiml.message(responseMessage);

    res.type('text/xml');
    res.send(twiml.toString());

  } catch (error) {
    console.error('[Webhook] Error:', error);
    
    const twiml = new twilio.twiml.MessagingResponse();
    twiml.message(formatErrorMessage('general'));
    
    res.type('text/xml');
    res.send(twiml.toString());
  }
});

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    service: 'WhatsApp Bot',
    timestamp: new Date().toISOString()
  });
});

/**
 * Send outbound WhatsApp message (for testing or notifications)
 */
async function sendWhatsAppMessage(toNumber, message) {
  try {
    const twilioWhatsAppNumber = process.env.TWILIO_WHATSAPP_NUMBER;
    
    const sentMessage = await twilioClient.messages.create({
      from: `whatsapp:${twilioWhatsAppNumber}`,
      to: `whatsapp:${toNumber}`,
      body: message
    });

    console.log(`[WhatsApp] Message sent: ${sentMessage.sid}`);
    return { success: true, sid: sentMessage.sid };

  } catch (error) {
    console.error('[WhatsApp] Error sending message:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Start the server
 */
const PORT = process.env.WHATSAPP_BOT_PORT || 3001;

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`✅ WhatsApp Bot server running on port ${PORT}`);
    console.log(`📱 Webhook URL: http://localhost:${PORT}/webhook/whatsapp`);
    console.log(`🔧 Environment: ${process.env.NODE_ENV || 'development'}`);
  });
}

module.exports = {
  app,
  handleWhatsAppMessage,
  sendWhatsAppMessage
};
