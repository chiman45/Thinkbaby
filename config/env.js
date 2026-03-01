/**
 * Environment Configuration Module
 * Validates and exports environment variables
 */

require('dotenv').config();

/**
 * Validate required environment variables
 */
function validateEnv() {
  const required = [
    'TWILIO_ACCOUNT_SID',
    'TWILIO_AUTH_TOKEN'
  ];

  const missing = required.filter(key => !process.env[key]);

  if (missing.length > 0) {
    console.warn(`⚠️  Warning: Missing environment variables: ${missing.join(', ')}`);
    console.warn('   Some features may not work properly.');
    console.warn('   Copy .env.example to .env and fill in your credentials.');
  }
}

// Run validation
validateEnv();

/**
 * Export configuration object
 */
const config = {
  // Node environment
  env: process.env.NODE_ENV || 'development',
  isDevelopment: process.env.NODE_ENV !== 'production',
  isProduction: process.env.NODE_ENV === 'production',

  // Backend API
  backend: {
    url: process.env.BACKEND_API_URL || 'http://localhost:3000/api'
  },

  // Twilio
  twilio: {
    accountSid: process.env.TWILIO_ACCOUNT_SID,
    authToken: process.env.TWILIO_AUTH_TOKEN,
    whatsappNumber: process.env.TWILIO_WHATSAPP_NUMBER || '+14155238886',
    phoneNumber: process.env.TWILIO_PHONE_NUMBER
  },

  // WhatsApp Bot
  whatsapp: {
    port: parseInt(process.env.WHATSAPP_BOT_PORT) || 3001
  },

  // IVR
  ivr: {
    port: parseInt(process.env.IVR_PORT) || 3002,
    baseUrl: process.env.IVR_BASE_URL || 'http://localhost:3002'
  },

  // Optional: AI API
  ai: {
    apiKey: process.env.AI_API_KEY,
    apiUrl: process.env.AI_API_URL,
    model: process.env.AI_MODEL || 'gpt-3.5-turbo'
  },

  // Optional: Database
  database: {
    url: process.env.DATABASE_URL,
    redisUrl: process.env.REDIS_URL
  },

  // Logging
  logging: {
    level: process.env.LOG_LEVEL || 'info'
  }
};

module.exports = config;
