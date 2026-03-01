/**
 * Credibility Check API Service
 * 
 * Service to interact with the backend credibility engine
 * for fact-checking and claim verification.
 */

import axios from 'axios';

// Configure base URL - update this based on your environment
const API_BASE_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000/api';

// ============================================================================
// Types
// ============================================================================

export interface CredibilityCheckRequest {
  claim: string;
  source_url?: string;
  rag_context?: string;
  web_context?: string;
  votes_data?: {
    user_votes?: {
      true: number;
      false: number;
    };
    validator_votes?: {
      true: number;
      false: number;
    };
  };
}

export interface CredibilityResult {
  claim: string;
  claim_hash: string;
  
  // Individual layer scores (0.0 - 1.0)
  source_score: number;
  linguistic_score: number;
  numerical_score: number;
  rag_match_score: number;
  temporal_score: number;
  community_score: number;
  
  // Composite results
  final_score: number;
  confidence: number;
  
  // Classification
  verdict: 'TRUE' | 'FALSE' | 'UNCERTAIN' | 'UNVERIFIED' | 'BREAKING';
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  
  // Explainability
  flags: string[];
  sources_found: Array<{
    domain: string;
    tier: number | string;
  }>;
  explanation: string;
  
  // Metadata
  timestamp: string;
  processing_ms: number;
}

export type VerdictType = CredibilityResult['verdict'];
export type RiskLevel = CredibilityResult['risk_level'];

// ============================================================================
// API Functions
// ============================================================================

/**
 * Check the credibility of a claim using the AI engine
 * 
 * @param request - Credibility check request with claim and optional context
 * @returns Promise<CredibilityResult> - Detailed credibility analysis
 * @throws Error if the API call fails
 */
export const checkCredibility = async (
  request: CredibilityCheckRequest
): Promise<CredibilityResult> => {
  try {
    const response = await axios.post<CredibilityResult>(
      `${API_BASE_URL}/credibility/check`,
      request,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message;
      throw new Error(`Credibility check failed: ${message}`);
    }
    throw error;
  }
};

/**
 * Simplified credibility check - just provide the claim text
 * 
 * @param claim - The claim text to verify
 * @returns Promise<CredibilityResult>
 */
export const quickCheck = async (claim: string): Promise<CredibilityResult> => {
  return checkCredibility({ claim });
};

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get a color based on the verdict
 */
export const getVerdictColor = (verdict: VerdictType): string => {
  const colors: Record<VerdictType, string> = {
    TRUE: 'green',
    FALSE: 'red',
    UNCERTAIN: 'yellow',
    UNVERIFIED: 'gray',
    BREAKING: 'blue',
  };
  return colors[verdict] || 'gray';
};

/**
 * Get an emoji for the verdict
 */
export const getVerdictEmoji = (verdict: VerdictType): string => {
  const emojis: Record<VerdictType, string> = {
    TRUE: '✅',
    FALSE: '❌',
    UNCERTAIN: '⚠️',
    UNVERIFIED: '🔍',
    BREAKING: '⏳',
  };
  return emojis[verdict] || '❓';
};

/**
 * Get a color based on the risk level
 */
export const getRiskColor = (risk: RiskLevel): string => {
  const colors: Record<RiskLevel, string> = {
    low: 'green',
    medium: 'yellow',
    high: 'orange',
    critical: 'red',
  };
  return colors[risk] || 'gray';
};

/**
 * Get an emoji for the risk level
 */
export const getRiskEmoji = (risk: RiskLevel): string => {
  const emojis: Record<RiskLevel, string> = {
    low: '🟢',
    medium: '🟡',
    high: '🟠',
    critical: '🔴',
  };
  return emojis[risk] || '⚪';
};

/**
 * Format score as percentage
 */
export const formatScore = (score: number): string => {
  return `${Math.round(score * 100)}%`;
};

/**
 * Get a human-readable verdict description
 */
export const getVerdictDescription = (verdict: VerdictType): string => {
  const descriptions: Record<VerdictType, string> = {
    TRUE: 'This claim appears to be credible and verified',
    FALSE: 'This claim is likely false or misleading',
    UNCERTAIN: 'Insufficient evidence to verify this claim',
    UNVERIFIED: 'This claim could not be verified against known sources',
    BREAKING: 'Breaking news - verification is pending',
  };
  return descriptions[verdict] || 'Unknown verdict';
};

/**
 * Get risk level description
 */
export const getRiskDescription = (risk: RiskLevel): string => {
  const descriptions: Record<RiskLevel, string> = {
    low: 'Low risk - information appears reliable',
    medium: 'Medium risk - exercise caution',
    high: 'High risk - likely misinformation',
    critical: 'Critical risk - highly likely to be false',
  };
  return descriptions[risk] || 'Unknown risk level';
};

/**
 * Determine if a claim should be trusted based on score threshold
 */
export const shouldTrust = (result: CredibilityResult, threshold = 0.7): boolean => {
  return result.verdict === 'TRUE' && result.final_score >= threshold;
};

/**
 * Determine if a claim is suspicious
 */
export const isSuspicious = (result: CredibilityResult): boolean => {
  return result.verdict === 'FALSE' || result.risk_level === 'critical';
};

// ============================================================================
// Export all
// ============================================================================

export default {
  checkCredibility,
  quickCheck,
  getVerdictColor,
  getVerdictEmoji,
  getRiskColor,
  getRiskEmoji,
  formatScore,
  getVerdictDescription,
  getRiskDescription,
  shouldTrust,
  isSuspicious,
};
