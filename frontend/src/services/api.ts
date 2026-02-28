/**
 * API Service Layer for Backend Communication
 * All backend endpoints are defined here with proper error handling
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ApiError {
  detail: string;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({ 
      detail: `HTTP ${response.status}: ${response.statusText}` 
    }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export interface FeedClaim {
  claimHash: string;
  contentCID: string;
  claimSubmitter: string;
  timestamp: number;
  blockNumber: number;
  userTrueVotes: number;
  userFalseVotes: number;
  validatorTrueVotes: number;
  validatorFalseVotes: number;
  score: number; // Reddit-style weighted score
}

export interface FeedResponse {
  claims: FeedClaim[];
  total: number;
}

export interface RoleInfo {
  role: number; // 0 = None, 1 = User, 2 = Validator
  roleName: string;
  tier: string;
  reputation: number;
}

export interface ClaimDetailResponse {
  claimHash: string;
  newsContent: string;
  contentCID: string;
  claimSubmitter: string;
  timestamp: number;
  blockNumber: number;
  userTrueVotes: number;
  userFalseVotes: number;
  validatorTrueVotes: number;
  validatorFalseVotes: number;
  callerRole?: RoleInfo;
  hasVoted: boolean;
}

export interface AnalyzeResponse {
  claimHash: string;
  newsContent: string;
  userTrueVotes: number;
  userFalseVotes: number;
  validatorTrueVotes: number;
  validatorFalseVotes: number;
  blockNumber: number;
  aiOutput: {
    ai_label: string;
    risk_score: number;
    summary: string;
  };
  snapshotHash: string;
  snapshotCID: string | null;
  callerRole?: RoleInfo;
  hasVoted: boolean;
  claimSubmitter: string;
  timestamp: number;
}

export interface RegisterContentResponse {
  claimHash: string;
  contentCID: string;
  blockNumber: number;
  claimSubmitter: string;
}

export const api = {
  /**
   * GET /feed
   * Fetch all registered claims with raw vote counts
   */
  async getFeed(): Promise<FeedResponse> {
    const response = await fetch(`${API_BASE_URL}/feed`);
    return handleResponse<FeedResponse>(response);
  },

  /**
   * GET /claims/{claimHash}/detail
   * Fetch claim detail with content from IPFS (no AI analysis)
   */
  async getClaimDetail(claimHash: string, callerAddress?: string): Promise<ClaimDetailResponse> {
    const url = new URL(`${API_BASE_URL}/claims/${claimHash}/detail`);
    if (callerAddress) {
      url.searchParams.append('caller_address', callerAddress);
    }
    const response = await fetch(url.toString());
    return handleResponse<ClaimDetailResponse>(response);
  },

  /**
   * POST /analyze-claim
   * Run AI analysis on claim (explicit user action only)
   */
  async analyzeClaim(claimHash: string, callerAddress?: string): Promise<AnalyzeResponse> {
    const response = await fetch(`${API_BASE_URL}/analyze-claim`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        claimHash,
        callerAddress,
      }),
    });
    return handleResponse<AnalyzeResponse>(response);
  },

  /**
   * POST /claims/register-content
   * Register claim content after on-chain registration
   */
  async registerContent(
    claimHash: string,
    newsContent: string,
    submitterAddress: string
  ): Promise<RegisterContentResponse> {
    const response = await fetch(`${API_BASE_URL}/claims/register-content`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        claimHash,
        newsContent,
        submitterAddress,
      }),
    });
    return handleResponse<RegisterContentResponse>(response);
  },

  /**
   * GET /health
   * Health check endpoint
   */
  async health(): Promise<{ status: string; service: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return handleResponse(response);
  },
};
