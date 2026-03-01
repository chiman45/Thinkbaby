/**
 * Backend API Integration Layer
 * Handles all communication with the backend REST API
 * Backend API interacts with the smart contract on Ethereum Sepolia
 */

const axios = require('axios');

// Get backend URL from environment or use default
const BACKEND_URL = process.env.BACKEND_API_URL || 'http://localhost:3000/api';

// Axios instance with default config
const apiClient = axios.create({
  baseURL: BACKEND_URL,
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for logging
apiClient.interceptors.request.use(
  config => {
    console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  error => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for logging
apiClient.interceptors.response.use(
  response => {
    console.log(`[API Response] ${response.status} ${response.config.url}`);
    return response;
  },
  error => {
    console.error('[API Response Error]', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

/**
 * Submit a new claim to the backend (and blockchain)
 * @param {string} claimHash - The keccak256 hash of the claim
 * @param {string} claimText - The original claim text (optional, for backend storage)
 * @returns {Promise<Object>} Response from backend
 */
async function submitClaimToBackend(claimHash, claimText = '') {
  try {
    const response = await apiClient.post('/submitClaim', {
      claimHash,
      claimText
    });

    return {
      success: true,
      data: response.data,
      message: 'Claim submitted successfully'
    };

  } catch (error) {
    return handleAPIError('submitClaimToBackend', error);
  }
}

/**
 * Vote TRUE for a claim
 * @param {string} claimHash - The keccak256 hash of the claim
 * @param {string} voterAddress - Address of the voter (optional)
 * @returns {Promise<Object>} Response from backend
 */
async function voteTrue(claimHash, voterAddress = null) {
  try {
    const response = await apiClient.post('/voteTrue', {
      claimHash,
      voterAddress
    });

    return {
      success: true,
      data: response.data,
      message: 'Vote TRUE recorded'
    };

  } catch (error) {
    return handleAPIError('voteTrue', error);
  }
}

/**
 * Vote FALSE for a claim
 * @param {string} claimHash - The keccak256 hash of the claim
 * @param {string} voterAddress - Address of the voter (optional)
 * @returns {Promise<Object>} Response from backend
 */
async function voteFalse(claimHash, voterAddress = null) {
  try {
    const response = await apiClient.post('/voteFalse', {
      claimHash,
      voterAddress
    });

    return {
      success: true,
      data: response.data,
      message: 'Vote FALSE recorded'
    };

  } catch (error) {
    return handleAPIError('voteFalse', error);
  }
}

/**
 * Get the voting results for a claim
 * @param {string} claimHash - The keccak256 hash of the claim
 * @returns {Promise<Object>} Claim result with vote counts and status
 */
async function getClaimResult(claimHash) {
  try {
    const response = await apiClient.get('/getClaimResult', {
      params: { claimHash }
    });

    return {
      success: true,
      data: response.data,
      exists: response.data.exists || false,
      trueVotes: response.data.trueVotes || 0,
      falseVotes: response.data.falseVotes || 0,
      status: response.data.status || 'Under Review'
    };

  } catch (error) {
    return handleAPIError('getClaimResult', error);
  }
}

/**
 * Get reputation score for a validator
 * @param {string} validatorAddress - Ethereum address of the validator
 * @returns {Promise<Object>} Reputation data
 */
async function getReputation(validatorAddress) {
  try {
    const response = await apiClient.get('/getReputation', {
      params: { validatorAddress }
    });

    return {
      success: true,
      data: response.data,
      reputation: response.data.reputation || 0
    };

  } catch (error) {
    return handleAPIError('getReputation', error);
  }
}

/**
 * Check if a claim already exists in the system
 * @param {string} claimHash - The keccak256 hash of the claim
 * @returns {Promise<boolean>} True if claim exists
 */
async function claimExists(claimHash) {
  try {
    const result = await getClaimResult(claimHash);
    return result.success && result.exists;
  } catch (error) {
    console.error('Error checking claim existence:', error);
    return false;
  }
}

/**
 * Centralized error handler for API calls
 */
function handleAPIError(functionName, error) {
  console.error(`[${functionName}] Error:`, error.message);

  if (error.response) {
    // Server responded with error status
    return {
      success: false,
      error: error.response.data?.message || error.message,
      statusCode: error.response.status
    };
  } else if (error.request) {
    // Request made but no response received
    return {
      success: false,
      error: 'Backend server not responding. Please try again later.',
      statusCode: 503
    };
  } else {
    // Something else happened
    return {
      success: false,
      error: error.message,
      statusCode: 500
    };
  }
}

/**
 * Health check for backend API
 * @returns {Promise<boolean>} True if backend is reachable
 */
async function healthCheck() {
  try {
    const response = await apiClient.get('/health', { timeout: 3000 });
    return response.status === 200;
  } catch (error) {
    console.error('Backend health check failed:', error.message);
    return false;
  }
}

module.exports = {
  submitClaimToBackend,
  voteTrue,
  voteFalse,
  getClaimResult,
  getReputation,
  claimExists,
  healthCheck
};
