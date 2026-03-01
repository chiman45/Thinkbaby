/**
 * Claim Hash Generator
 * Generates keccak256 hashes compatible with Solidity smart contracts
 */

const { keccak256, toUtf8Bytes } = require('ethers');

/**
 * Generates a keccak256 hash for a claim text
 * This hash MUST match the Solidity keccak256(abi.encodePacked(string)) exactly
 * 
 * @param {string} claimText - The claim text to hash
 * @returns {string} The keccak256 hash in hex format (0x...)
 */
function generateClaimHash(claimText) {
  try {
    // Input validation
    if (!claimText || typeof claimText !== 'string') {
      throw new Error('Claim text must be a non-empty string');
    }

    // Normalize the text (trim and normalize whitespace)
    const normalizedText = claimText.trim();
    
    if (normalizedText.length === 0) {
      throw new Error('Claim text cannot be empty after normalization');
    }

    // Convert string to UTF-8 bytes
    const bytes = toUtf8Bytes(normalizedText);
    
    // Generate keccak256 hash (compatible with Solidity)
    const hash = keccak256(bytes);
    
    console.log(`Generated hash for claim: "${normalizedText.substring(0, 50)}..." => ${hash}`);
    
    return hash;

  } catch (error) {
    console.error('Error generating claim hash:', error);
    throw new Error(`Hash generation failed: ${error.message}`);
  }
}

/**
 * Generates a hash from the first claim in an array
 * Useful for processing analyzed messages
 * 
 * @param {Array<string>} claims - Array of claim strings
 * @returns {string} The keccak256 hash of the first claim
 */
function hashFirstClaim(claims) {
  if (!Array.isArray(claims) || claims.length === 0) {
    throw new Error('Claims array must contain at least one claim');
  }
  
  return generateClaimHash(claims[0]);
}

/**
 * Batch hash multiple claims
 * 
 * @param {Array<string>} claims - Array of claim strings
 * @returns {Array<{claim: string, hash: string}>} Array of claim-hash pairs
 */
function hashMultipleClaims(claims) {
  if (!Array.isArray(claims) || claims.length === 0) {
    throw new Error('Claims array must contain at least one claim');
  }

  return claims.map(claim => ({
    claim: claim,
    hash: generateClaimHash(claim)
  }));
}

/**
 * Verify that two claims produce the same hash
 * Useful for debugging hash consistency
 * 
 * @param {string} claim1 - First claim text
 * @param {string} claim2 - Second claim text
 * @returns {boolean} True if hashes match
 */
function verifyHashMatch(claim1, claim2) {
  const hash1 = generateClaimHash(claim1);
  const hash2 = generateClaimHash(claim2);
  
  const match = hash1 === hash2;
  console.log(`Hash comparison: ${match ? 'MATCH' : 'DIFFERENT'}`);
  console.log(`  Claim 1: "${claim1}" => ${hash1}`);
  console.log(`  Claim 2: "${claim2}" => ${hash2}`);
  
  return match;
}

module.exports = {
  generateClaimHash,
  hashFirstClaim,
  hashMultipleClaims,
  verifyHashMatch
};
