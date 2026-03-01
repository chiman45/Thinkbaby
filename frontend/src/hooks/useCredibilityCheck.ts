/**
 * useCredibilityCheck Hook
 * 
 * React hook for checking claim credibility with loading and error states
 */

import { useState, useCallback } from 'react';
import { 
  checkCredibility, 
  type CredibilityCheckRequest, 
  type CredibilityResult 
} from '@/services/credibilityApi';

interface UseCredibilityCheckReturn {
  result: CredibilityResult | null;
  loading: boolean;
  error: string | null;
  checkClaim: (request: CredibilityCheckRequest) => Promise<void>;
  quickCheck: (claim: string) => Promise<void>;
  reset: () => void;
}

/**
 * Hook for checking claim credibility
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { result, loading, error, checkClaim } = useCredibilityCheck();
 * 
 *   const handleCheck = async () => {
 *     await checkClaim({ claim: "Some claim to verify" });
 *   };
 * 
 *   return (
 *     <div>
 *       {loading && <p>Checking...</p>}
 *       {error && <p>Error: {error}</p>}
 *       {result && <p>Verdict: {result.verdict}</p>}
 *     </div>
 *   );
 * }
 * ```
 */
export const useCredibilityCheck = (): UseCredibilityCheckReturn => {
  const [result, setResult] = useState<CredibilityResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkClaim = useCallback(async (request: CredibilityCheckRequest) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const credibilityResult = await checkCredibility(request);
      setResult(credibilityResult);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to check credibility';
      setError(errorMessage);
      console.error('Credibility check error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const quickCheck = useCallback(async (claim: string) => {
    await checkClaim({ claim });
  }, [checkClaim]);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    result,
    loading,
    error,
    checkClaim,
    quickCheck,
    reset,
  };
};

/**
 * Hook for checking credibility with automatic debouncing
 * Useful for real-time checking as user types
 * 
 * @param delay - Debounce delay in milliseconds (default: 500ms)
 */
export const useDebouncedCredibilityCheck = (delay = 500): UseCredibilityCheckReturn => {
  const [result, setResult] = useState<CredibilityResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null);

  const checkClaim = useCallback((request: CredibilityCheckRequest) => {
    // Clear existing timeout
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    setLoading(true);
    setError(null);

    // Set new timeout
    const newTimeoutId = setTimeout(async () => {
      try {
        const credibilityResult = await checkCredibility(request);
        setResult(credibilityResult);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to check credibility';
        setError(errorMessage);
        console.error('Credibility check error:', err);
      } finally {
        setLoading(false);
      }
    }, delay);

    setTimeoutId(newTimeoutId);

    // Return a promise for async/await support
    return Promise.resolve();
  }, [delay, timeoutId]);

  const quickCheck = useCallback(async (claim: string) => {
    await checkClaim({ claim });
  }, [checkClaim]);

  const reset = useCallback(() => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    setResult(null);
    setError(null);
    setLoading(false);
    setTimeoutId(null);
  }, [timeoutId]);

  return {
    result,
    loading,
    error,
    checkClaim,
    quickCheck,
    reset,
  };
};

export default useCredibilityCheck;
