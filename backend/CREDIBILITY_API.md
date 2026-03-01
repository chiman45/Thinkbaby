# Credibility Engine API Documentation

## Endpoint

**POST** `/credibility/check`

Analyzes a claim using the multi-layer credibility scoring engine.

## Base URL

```
http://localhost:8000/api/credibility/check
```

## Request Body

```typescript
{
  claim: string;              // Required: The claim to verify (5-10000 chars)
  source_url?: string;        // Optional: Source URL of the claim
  rag_context?: string;       // Optional: Context from RAG database
  web_context?: string;       // Optional: Additional web context
  votes_data?: {              // Optional: Blockchain voting data
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
```

## Response

```typescript
{
  claim: string;
  claim_hash: string;         // SHA-256 hash of claim
  
  // Individual layer scores (0.0 - 1.0)
  source_score: number;
  linguistic_score: number;
  numerical_score: number;
  rag_match_score: number;
  temporal_score: number;
  community_score: number;
  
  // Composite results
  final_score: number;        // 0.0 - 1.0
  confidence: number;         // 0.0 - 1.0
  
  // Classification
  verdict: "TRUE" | "FALSE" | "UNCERTAIN" | "UNVERIFIED" | "BREAKING";
  risk_level: "low" | "medium" | "high" | "critical";
  
  // Explainability
  flags: string[];            // Detection flags
  sources_found: Array<{
    domain: string;
    tier: number | string;
  }>;
  explanation: string;        // Human-readable summary
  
  // Metadata
  timestamp: string;          // ISO 8601
  processing_ms: number;      // Processing time in milliseconds
}
```

## Verdict Thresholds

- **TRUE** (≥ 0.72): Claim appears credible
- **UNCERTAIN** (0.40 - 0.71): Insufficient evidence
- **FALSE** (< 0.40): Claim likely false or misleading
- **BREAKING**: Breaking news, verification pending
- **UNVERIFIED**: No matching sources found

## Risk Levels

- **low**: High credibility, verified sources
- **medium**: Moderate credibility, some concerns
- **high**: Low credibility, multiple red flags
- **critical**: Very low credibility, likely misinformation

## Example Usage

### Frontend (React/TypeScript)

```typescript
// services/credibilityApi.ts
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

interface CredibilityCheckRequest {
  claim: string;
  source_url?: string;
  rag_context?: string;
  web_context?: string;
  votes_data?: {
    user_votes?: { true: number; false: number };
    validator_votes?: { true: number; false: number };
  };
}

interface CredibilityResult {
  claim: string;
  claim_hash: string;
  source_score: number;
  linguistic_score: number;
  numerical_score: number;
  rag_match_score: number;
  temporal_score: number;
  community_score: number;
  final_score: number;
  confidence: number;
  verdict: 'TRUE' | 'FALSE' | 'UNCERTAIN' | 'UNVERIFIED' | 'BREAKING';
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  flags: string[];
  sources_found: Array<{ domain: string; tier: number | string }>;
  explanation: string;
  timestamp: string;
  processing_ms: number;
}

export const checkCredibility = async (
  request: CredibilityCheckRequest
): Promise<CredibilityResult> => {
  const response = await axios.post(
    `${API_BASE}/credibility/check`,
    request
  );
  return response.data;
};
```

### Usage in Component

```typescript
import { checkCredibility } from '@/services/credibilityApi';
import { useState } from 'react';

function ClaimChecker() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCheck = async (claim: string) => {
    setLoading(true);
    try {
      const result = await checkCredibility({ claim });
      setResult(result);
      console.log('Verdict:', result.verdict);
      console.log('Score:', result.final_score);
      console.log('Risk:', result.risk_level);
    } catch (error) {
      console.error('Credibility check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Enter claim to verify..."
        onBlur={(e) => handleCheck(e.target.value)}
      />
      
      {loading && <p>Analyzing claim...</p>}
      
      {result && (
        <div className={`result ${result.risk_level}`}>
          <h3>{result.verdict}</h3>
          <p>Credibility Score: {(result.final_score * 100).toFixed(0)}%</p>
          <p>Risk Level: {result.risk_level.toUpperCase()}</p>
          <p>{result.explanation}</p>
          
          {result.flags.length > 0 && (
            <div>
              <strong>Flags:</strong>
              <ul>
                {result.flags.map((flag, i) => (
                  <li key={i}>{flag}</li>
                ))}
              </ul>
            </div>
          )}
          
          {result.sources_found.length > 0 && (
            <div>
              <strong>Sources:</strong>
              <ul>
                {result.sources_found.map((source, i) => (
                  <li key={i}>
                    {source.domain} (Tier {source.tier})
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### Simple Example

```typescript
// Basic usage
const result = await checkCredibility({
  claim: "PM Kisan Yojana provides ₹6000 annually to farmers"
});

console.log(result);
// {
//   verdict: "TRUE",
//   final_score: 0.85,
//   risk_level: "low",
//   explanation: "✅ Claim appears credible | Credibility Score: 85% | ...",
//   ...
// }
```

### With Additional Context

```typescript
// Advanced usage with all parameters
const result = await checkCredibility({
  claim: "Breaking: New government scheme offering ₹50000 to all citizens",
  source_url: "https://example.com/news",
  rag_context: "No matching government schemes found.",
  web_context: "Multiple unofficial sources mention this claim",
  votes_data: {
    user_votes: { true: 2, false: 15 },
    validator_votes: { true: 0, false: 3 }
  }
});

console.log(result);
// {
//   verdict: "FALSE",
//   final_score: 0.25,
//   risk_level: "critical",
//   flags: ["implausible_amount:₹50,000", "unverified_source", ...],
//   ...
// }
```

## Testing with cURL

```bash
# Simple test
curl -X POST http://localhost:8000/api/credibility/check \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "PM Kisan Yojana provides financial support to farmers"
  }'

# With source URL
curl -X POST http://localhost:8000/api/credibility/check \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Pradhan Mantri Awas Yojana offers housing subsidy",
    "source_url": "https://pib.gov.in/PressReleaseIframePage.aspx?PRID=1234567"
  }'
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Claim must be at least 5 characters"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "claim"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to check credibility: [error message]"
}
```

## Scoring Methodology

### Layer Weights
- **Source Score** (25%): Tier-1/2 domains, government sources
- **Linguistic Score** (20%): Clickbait, urgency, manipulation
- **Numerical Score** (15%): Anomalous amounts, percentages
- **RAG Match** (20%): Database similarity
- **Temporal Score** (10%): Breaking news, recycled content
- **Community Score** (10%): Blockchain votes

### Detection Signals

**Red Flags:**
- `clickbait_language` - Sensational wording
- `urgency_manipulation` - "Act now", "Limited time"
- `scheme_impersonation_suspected` - Fake government schemes
- `implausible_amount` - Unrealistic monetary claims
- `unverified_source` - Unknown or suspicious domains
- `no_database_match` - Not found in verified records

**Positive Signals:**
- `government_source_detected` - Official .gov.in domain
- `strong_database_match` - High similarity to known facts
- `community_consensus_true` - Majority votes true

## Integration Notes

1. **CORS**: Ensure backend CORS settings allow your frontend origin
2. **Error Handling**: Always implement try-catch for API calls
3. **Loading States**: Show user feedback during analysis
4. **Caching**: Consider caching results for identical claims
5. **Rate Limiting**: Implement client-side throttling if needed

## Backend Setup

Ensure the backend server is running:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The credibility endpoint will be available at:
```
http://localhost:8000/api/credibility/check
```
