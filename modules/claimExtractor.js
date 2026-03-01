/**
 * Claim Extraction Module
 * Analyzes messages to extract claims, calculate risk scores, and generate explanations
 */

const axios = require('axios');

/**
 * Analyzes a message to extract claims and calculate risk
 * @param {string} messageText - The text message to analyze
 * @returns {Promise<Object>} Analysis result with claims, risk score, and explanation
 */
async function analyzeMessage(messageText) {
  try {
    // Input validation
    if (!messageText || messageText.trim().length === 0) {
      throw new Error('Message text cannot be empty');
    }

    // For MVP: Simple rule-based analysis + optional AI API integration
    const analysis = await performAnalysis(messageText);

    return {
      claims: analysis.claims,
      riskScore: analysis.riskScore,
      explanation: analysis.explanation,
      timestamp: new Date().toISOString()
    };

  } catch (error) {
    console.error('Error in analyzeMessage:', error);
    throw new Error(`Claim extraction failed: ${error.message}`);
  }
}

/**
 * Performs the actual analysis logic
 * This can be extended to call external AI APIs (OpenAI, Google Gemini, etc.)
 */
async function performAnalysis(text) {
  // Normalize text
  const normalizedText = text.trim().toLowerCase();

  // Extract claims (simplified for MVP)
  const claims = extractClaims(text);

  // Calculate risk score
  const riskScore = calculateRiskScore(normalizedText, claims);

  // Generate explanation
  const explanation = generateExplanation(normalizedText, riskScore, claims);

  return {
    claims,
    riskScore,
    explanation
  };
}

/**
 * Extracts atomic claims from text
 * For MVP: Splits by sentences, can be enhanced with AI
 */
function extractClaims(text) {
  // Split into sentences
  const sentences = text
    .split(/[.!?]+/)
    .map(s => s.trim())
    .filter(s => s.length > 10); // Filter out very short fragments

  // For MVP, treat each sentence as a potential claim
  // In production, use NLP/LLM to extract actual factual claims
  return sentences.slice(0, 3); // Limit to top 3 claims
}

/**
 * Calculates risk score (0-100) based on content analysis
 */
function calculateRiskScore(text, claims) {
  let baseRisk = 50; // Start at neutral

  // High-risk keywords and patterns
  const urgentKeywords = ['immediately', 'urgent', 'breaking', 'alert', 'warning'];
  const financialKeywords = ['money', 'cash', 'prize', 'won', 'lottery', 'reward', '₹', '$'];
  const governmentKeywords = ['government', 'minister', 'official', 'scheme', 'policy'];
  const unverifiedPhrases = ['forward this', 'share immediately', 'before it\'s deleted', 'they don\'t want you to know'];

  // Check for urgent language
  if (urgentKeywords.some(keyword => text.includes(keyword))) {
    baseRisk += 15;
  }

  // Check for financial claims
  if (financialKeywords.some(keyword => text.includes(keyword))) {
    baseRisk += 20;
  }

  // Check for government-related claims
  if (governmentKeywords.some(keyword => text.includes(keyword))) {
    baseRisk += 10;
  }

  // Check for viral sharing patterns
  if (unverifiedPhrases.some(phrase => text.includes(phrase))) {
    baseRisk += 25;
  }

  // Check for all caps (shouting)
  const capsRatio = (text.match(/[A-Z]/g) || []).length / text.length;
  if (capsRatio > 0.5) {
    baseRisk += 10;
  }

  // Check for excessive punctuation
  const punctuationCount = (text.match(/[!?]{2,}/g) || []).length;
  if (punctuationCount > 2) {
    baseRisk += 10;
  }

  // Ensure score is within 0-100 range
  return Math.min(Math.max(Math.round(baseRisk), 0), 100);
}

/**
 * Generates explanation for the risk assessment
 */
function generateExplanation(text, riskScore, claims) {
  const explanations = [];

  if (riskScore >= 80) {
    explanations.push('High-risk content detected.');
  } else if (riskScore >= 60) {
    explanations.push('Moderate risk detected.');
  } else if (riskScore >= 40) {
    explanations.push('Some suspicious elements found.');
  } else {
    explanations.push('Content appears relatively neutral.');
  }

  // Add specific findings
  if (text.includes('government') || text.includes('minister')) {
    explanations.push('Contains government-related claims requiring verification.');
  }

  if (text.includes('₹') || text.includes('money') || text.includes('prize')) {
    explanations.push('Contains financial claims. Verify through official sources.');
  }

  if (text.includes('forward') || text.includes('share')) {
    explanations.push('Shows viral sharing patterns common in misinformation.');
  }

  if (explanations.length === 1) {
    explanations.push('Recommend verification through official sources and fact-checking websites.');
  }

  return explanations.join(' ');
}

/**
 * Optional: Call external AI API for advanced analysis
 * Uncomment and configure when AI API is available
 */
async function callAIAPI(text) {
  // Example for OpenAI, Google Gemini, or custom AI service
  // const apiKey = process.env.AI_API_KEY;
  // const apiUrl = process.env.AI_API_URL;
  
  // const response = await axios.post(apiUrl, {
  //   prompt: `Analyze this message for fake news risk and extract claims:\n\n${text}`,
  //   max_tokens: 200
  // }, {
  //   headers: {
  //     'Authorization': `Bearer ${apiKey}`,
  //     'Content-Type': 'application/json'
  //   }
  // });
  
  // return response.data;
}

module.exports = {
  analyzeMessage
};
