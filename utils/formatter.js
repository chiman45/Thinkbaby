/**
 * Response Formatter Utility
 * Formats responses for WhatsApp, IVR, and other channels
 */

/**
 * Format credibility report for WhatsApp
 * @param {Object} analysis - Analysis result from claimExtractor
 * @param {Object} blockchainResult - Result from getClaimResult
 * @returns {string} Formatted WhatsApp message
 */
function formatWhatsAppReport(analysis, blockchainResult) {
  const { claims, riskScore, explanation } = analysis;
  const { trueVotes = 0, falseVotes = 0, status = 'Under Review' } = blockchainResult;

  const claimText = Array.isArray(claims) && claims.length > 0 
    ? claims[0] 
    : 'Unable to extract claim';

  // Determine emoji based on risk score
  let emoji = '🔍';
  if (riskScore >= 80) emoji = '🚨';
  else if (riskScore >= 60) emoji = '⚠️';
  else if (riskScore >= 40) emoji = '🔎';
  else emoji = '✅';

  // Determine final status
  let finalStatus = status;
  if (status === 'Under Review') {
    const totalVotes = trueVotes + falseVotes;
    if (totalVotes > 0) {
      finalStatus = trueVotes > falseVotes ? 'Likely True' : 'Likely False';
    }
  }

  const report = `${emoji} *Claim Analysis*

📝 *Claim:* ${claimText}

🤖 *AI Risk Score:* ${riskScore}%

📊 *Community Votes:*
✅ True: ${trueVotes}
❌ False: ${falseVotes}

📋 *Status:* ${finalStatus}

💡 *Explanation:*
${explanation}

---
⚡ Powered by ThinkBaby - Web3 Fact Verification`;

  return report;
}

/**
 * Format voice response for IVR (keep under 12 seconds)
 * @param {Object} analysis - Analysis result from claimExtractor
 * @param {Object} blockchainResult - Result from getClaimResult
 * @returns {string} Short voice script
 */
function formatIVRResponse(analysis, blockchainResult) {
  const { riskScore } = analysis;
  const { trueVotes = 0, falseVotes = 0, status = 'Under Review' } = blockchainResult;

  const totalVotes = trueVotes + falseVotes;

  // Short and clear responses for voice
  if (status === 'True' || (trueVotes > falseVotes && totalVotes >= 3)) {
    return 'This claim appears to be true based on community verification.';
  } else if (status === 'False' || (falseVotes > trueVotes && totalVotes >= 3)) {
    return 'This claim appears to be false. Please verify from official sources.';
  } else if (riskScore >= 70) {
    return 'High risk detected. This claim is currently under review. We recommend verifying from official sources.';
  } else {
    return 'This claim is currently under review by our community. Check back later for results.';
  }
}

/**
 * Format short SMS response
 * @param {Object} analysis - Analysis result
 * @param {Object} blockchainResult - Blockchain result
 * @returns {string} SMS text (under 160 chars)
 */
function formatSMSResponse(analysis, blockchainResult) {
  const { riskScore } = analysis;
  const { trueVotes = 0, falseVotes = 0 } = blockchainResult;

  if (trueVotes > falseVotes) {
    return `✅ Likely TRUE (Votes: ${trueVotes}/${falseVotes}) | Risk: ${riskScore}%`;
  } else if (falseVotes > trueVotes) {
    return `❌ Likely FALSE (Votes: ${trueVotes}/${falseVotes}) | Risk: ${riskScore}%`;
  } else {
    return `🔍 Under Review | Risk Score: ${riskScore}% | Votes: ${trueVotes}/${falseVotes}`;
  }
}

/**
 * Format error message for users
 * @param {string} errorType - Type of error
 * @returns {string} User-friendly error message
 */
function formatErrorMessage(errorType = 'general') {
  const errors = {
    'api_down': '⚠️ Our verification system is temporarily unavailable. Please try again in a few minutes.',
    'invalid_message': '❌ Unable to analyze this message. Please send a clear factual claim.',
    'rate_limit': '⏳ Too many requests. Please wait a moment before trying again.',
    'general': '❌ Something went wrong. Please try again later.'
  };

  return errors[errorType] || errors['general'];
}

/**
 * Format welcome message for new users
 * @returns {string} Welcome message
 */
function formatWelcomeMessage() {
  return `👋 Welcome to ThinkBaby!

I help verify claims using AI and blockchain-based community consensus.

📱 *How to use:*
1. Send me any claim or message
2. I'll analyze it for misinformation
3. Get instant credibility report

🚀 Try it now - send me any news or claim to verify!`;
}

/**
 * Format help message
 * @returns {string} Help instructions
 */
function formatHelpMessage() {
  return `❓ *ThinkBaby Help*

*What I do:*
🔍 Analyze claims for fake news
🤖 AI-powered risk assessment
⛓️ Blockchain-based verification
👥 Community voting system

*How to use:*
Just send me any claim or news message, and I'll verify it!

*Examples:*
"Government giving ₹5000 to students"
"New cryptocurrency launched by Tesla"

Need help? Visit: thinkbaby.io`;
}

module.exports = {
  formatWhatsAppReport,
  formatIVRResponse,
  formatSMSResponse,
  formatErrorMessage,
  formatWelcomeMessage,
  formatHelpMessage
};
