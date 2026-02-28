/**
 * ThinkBaby - AI + Bot + IVR Layer
 * Main entry point for the application
 */

require('dotenv').config();
const config = require('./config/env');

// Import modules
const { analyzeMessage } = require('./modules/claimExtractor');
const { generateClaimHash, verifyHashMatch } = require('./modules/hashGenerator');
const { 
  submitClaimToBackend, 
  getClaimResult, 
  healthCheck 
} = require('./modules/backendClient');

console.log('');
console.log('╔════════════════════════════════════════════════════════════╗');
console.log('║                                                            ║');
console.log('║              🔥 THINKBABY - AI LAYER 🔥                   ║');
console.log('║                                                            ║');
console.log('║   Web3 Decentralized Fake News Verification Protocol      ║');
console.log('║                                                            ║');
console.log('╚════════════════════════════════════════════════════════════╝');
console.log('');

/**
 * Test function to verify all modules are working
 */
async function runSystemTest() {
  console.log('🧪 Running system tests...\n');

  try {
    // Test 1: Claim Extraction
    console.log('✅ Test 1: Claim Extraction Module');
    const testMessage = 'Government giving ₹5000 to all students. Forward this immediately!';
    const analysis = await analyzeMessage(testMessage);
    console.log('   Claims:', analysis.claims);
    console.log('   Risk Score:', analysis.riskScore);
    console.log('   Explanation:', analysis.explanation);
    console.log('');

    // Test 2: Hash Generation
    console.log('✅ Test 2: Hash Generator Module');
    const claimHash = generateClaimHash(analysis.claims[0]);
    console.log('   Hash:', claimHash);
    console.log('');

    // Test 3: Backend API Health
    console.log('✅ Test 3: Backend API Connection');
    const backendHealthy = await healthCheck();
    if (backendHealthy) {
      console.log('   ✅ Backend is reachable');
    } else {
      console.log('   ⚠️  Backend is not reachable (this is OK if backend is not running yet)');
    }
    console.log('');

    // Test 4: Configuration
    console.log('✅ Test 4: Configuration');
    console.log('   Environment:', config.env);
    console.log('   Backend URL:', config.backend.url);
    console.log('   WhatsApp Port:', config.whatsapp.port);
    console.log('   IVR Port:', config.ivr.port);
    console.log('');

    console.log('✅ All tests completed!\n');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error('');
  }
}

/**
 * Example: Process a claim end-to-end
 */
async function processClaim(messageText) {
  console.log('\n📝 Processing claim:', messageText);
  console.log('─'.repeat(60));

  try {
    // Step 1: Analyze
    const analysis = await analyzeMessage(messageText);
    console.log('✅ Analysis complete');
    console.log('   Risk Score:', analysis.riskScore);

    // Step 2: Generate hash
    const claimHash = generateClaimHash(analysis.claims[0]);
    console.log('✅ Hash generated:', claimHash);

    // Step 3: Submit to backend (if backend is available)
    const backendHealthy = await healthCheck();
    if (backendHealthy) {
      const submitResult = await submitClaimToBackend(claimHash, analysis.claims[0]);
      console.log('✅ Submitted to backend:', submitResult.success);

      // Step 4: Get result
      const result = await getClaimResult(claimHash);
      console.log('✅ Blockchain result:');
      console.log('   True Votes:', result.trueVotes || 0);
      console.log('   False Votes:', result.falseVotes || 0);
      console.log('   Status:', result.status || 'Under Review');
    } else {
      console.log('⚠️  Backend not available - skipping blockchain interaction');
    }

    console.log('─'.repeat(60));
    console.log('✅ Claim processed successfully\n');

  } catch (error) {
    console.error('❌ Error processing claim:', error.message);
  }
}

/**
 * Display usage instructions
 */
function displayInstructions() {
  console.log('📚 Usage Instructions:\n');
  console.log('1️⃣  Start WhatsApp Bot:');
  console.log('    npm run whatsapp');
  console.log('    Then configure Twilio webhook to: http://your-url/webhook/whatsapp\n');
  
  console.log('2️⃣  Start IVR Handler:');
  console.log('    npm run ivr');
  console.log('    Then configure Twilio voice webhook to: http://your-url/ivr/incoming\n');
  
  console.log('3️⃣  Run this test file:');
  console.log('    npm start\n');
  
  console.log('📖 For more information, see README.md\n');
}

/**
 * Main function
 */
async function main() {
  displayInstructions();
  
  // Run tests
  await runSystemTest();

  // Example: Process a test claim
  await processClaim('Breaking: New government scheme announced! Everyone gets free money!');

  console.log('🎯 Tip: To start the WhatsApp bot or IVR, use the npm scripts:');
  console.log('   npm run whatsapp  (for WhatsApp bot)');
  console.log('   npm run ivr       (for IVR handler)\n');
}

// Run if this is the main module
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

// Export for use in other modules
module.exports = {
  analyzeMessage,
  generateClaimHash,
  submitClaimToBackend,
  getClaimResult,
  processClaim
};
