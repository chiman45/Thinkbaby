# Credibility Engine Integration - Quick Start

## ✅ What Was Created

### Backend
1. **API Endpoint**: `POST /api/credibility/check`
   - Location: `backend/routes.py` (line ~650)
   - Imports credibility engine automatically
   - Validates input and returns comprehensive results

### Frontend
1. **API Service**: `frontend/src/services/credibilityApi.ts`
   - Type-safe API calls
   - Helper functions for formatting and display
   - Error handling

2. **React Hook**: `frontend/src/hooks/useCredibilityCheck.ts`
   - `useCredibilityCheck()` - Standard hook with loading/error states
   - `useDebouncedCredibilityCheck()` - Debounced version for real-time checking

3. **Example Component**: `frontend/src/components/CredibilityChecker.tsx`
   - Full-featured credibility checker UI
   - Score breakdown with progress bars
   - Flags, sources, and metadata display

### Documentation
1. **API Documentation**: `backend/CREDIBILITY_API.md`
   - Complete API reference
   - Request/response schemas
   - Usage examples

## 🚀 Quick Start

### 1. Start the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The credibility endpoint will be available at:
```
http://localhost:8000/api/credibility/check
```

### 2. Use in Frontend Component

```tsx
import { useCredibilityCheck } from '@/hooks/useCredibilityCheck';

function MyComponent() {
  const { result, loading, error, quickCheck } = useCredibilityCheck();

  const handleCheck = async () => {
    await quickCheck("PM Kisan Yojana provides ₹6000 to farmers");
  };

  return (
    <div>
      <button onClick={handleCheck} disabled={loading}>
        {loading ? 'Checking...' : 'Check Claim'}
      </button>
      
      {error && <p className="text-red-500">{error}</p>}
      
      {result && (
        <div>
          <h3>{result.verdict}</h3>
          <p>Score: {(result.final_score * 100).toFixed(0)}%</p>
          <p>Risk: {result.risk_level}</p>
          <p>{result.explanation}</p>
        </div>
      )}
    </div>
  );
}
```

### 3. Or Use the Pre-built Component

```tsx
import { CredibilityChecker } from '@/components/CredibilityChecker';

function App() {
  return (
    <div>
      <h1>Fact Checker</h1>
      <CredibilityChecker />
    </div>
  );
}
```

## 📡 API Usage Examples

### Simple Check

```typescript
import { quickCheck } from '@/services/credibilityApi';

const result = await quickCheck("Government announces new scheme");
console.log(result.verdict); // TRUE, FALSE, UNCERTAIN, etc.
console.log(result.final_score); // 0.0 - 1.0
```

### Advanced Check with Context

```typescript
import { checkCredibility } from '@/services/credibilityApi';

const result = await checkCredibility({
  claim: "Breaking: New ₹50000 scheme for all citizens",
  source_url: "https://example.com/news",
  votes_data: {
    user_votes: { true: 5, false: 20 },
    validator_votes: { true: 0, false: 3 }
  }
});
```

### With Loading State

```typescript
const { result, loading, error, checkClaim } = useCredibilityCheck();

// In your event handler
await checkClaim({
  claim: userInput,
  source_url: sourceUrl
});
```

## 📊 Response Format

```typescript
{
  claim: string;
  claim_hash: string;
  
  // Scores (0.0 - 1.0)
  source_score: number;
  linguistic_score: number;
  numerical_score: number;
  rag_match_score: number;
  temporal_score: number;
  community_score: number;
  final_score: number;
  confidence: number;
  
  // Classification
  verdict: "TRUE" | "FALSE" | "UNCERTAIN" | "UNVERIFIED" | "BREAKING";
  risk_level: "low" | "medium" | "high" | "critical";
  
  // Details
  flags: string[];           // e.g., ["clickbait_language", "unverified_source"]
  sources_found: Array<{
    domain: string;
    tier: number | string;
  }>;
  explanation: string;
  timestamp: string;
  processing_ms: number;
}
```

## 🎯 Use Cases

### 1. Real-time Fact Checking
```tsx
const { quickCheck } = useDebouncedCredibilityCheck(1000);

<textarea onChange={(e) => quickCheck(e.target.value)} />
```

### 2. Batch Verification
```typescript
const claims = ["Claim 1", "Claim 2", "Claim 3"];
const results = await Promise.all(
  claims.map(claim => quickCheck(claim))
);
```

### 3. Display with UI Components
```tsx
{result && (
  <>
    <Badge className={getVerdictColor(result.verdict)}>
      {getVerdictEmoji(result.verdict)} {result.verdict}
    </Badge>
    <Progress value={result.final_score * 100} />
  </>
)}
```

## 🔧 Configuration

### Update API Base URL

Edit `frontend/src/services/credibilityApi.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000/api';
```

Then in `.env`:
```
VITE_BACKEND_API_URL=https://your-production-api.com/api
```

### Adjust Score Thresholds

The endpoint uses these default thresholds:
- `≥ 0.72` → TRUE (low risk)
- `0.40 - 0.71` → UNCERTAIN (medium/high risk)
- `< 0.40` → FALSE (critical risk)

To customize in frontend:
```typescript
import { shouldTrust } from '@/services/credibilityApi';

// Custom threshold
const isTrusted = shouldTrust(result, 0.8); // 80% threshold
```

## 🧪 Testing

### Test with cURL

```bash
curl -X POST http://localhost:8000/api/credibility/check \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "PM Kisan Yojana provides financial support to farmers"
  }'
```

### Test in Browser Console

```javascript
fetch('http://localhost:8000/api/credibility/check', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    claim: 'Test claim to verify'
  })
})
.then(r => r.json())
.then(console.log);
```

## 📝 Notes

- **CORS**: Make sure backend CORS settings allow your frontend origin
- **Validation**: Minimum claim length is 5 characters
- **Performance**: Typical response time is 100-500ms
- **Caching**: Consider implementing client-side caching for repeated claims

## 🐛 Troubleshooting

### "Module not found" error
Make sure `credibility_engine.py` is in the parent directory of `backend/`

### CORS error
Add your frontend URL to `backend/config.py` CORS origins:
```python
cors_origins_list = ["http://localhost:5173", "http://localhost:3000"]
```

### Import error
The backend automatically adds parent directory to path:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

## 🎨 Styling Examples

### Tailwind Classes for Verdicts
```tsx
const verdictStyles = {
  TRUE: 'bg-green-100 text-green-800 border-green-300',
  FALSE: 'bg-red-100 text-red-800 border-red-300',
  UNCERTAIN: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  UNVERIFIED: 'bg-gray-100 text-gray-800 border-gray-300',
  BREAKING: 'bg-blue-100 text-blue-800 border-blue-300',
};
```

### Progress Bar for Score
```tsx
<div className="w-full bg-gray-200 rounded-full h-2">
  <div
    className={`h-2 rounded-full ${
      result.final_score >= 0.7 ? 'bg-green-500' :
      result.final_score >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
    }`}
    style={{ width: `${result.final_score * 100}%` }}
  />
</div>
```

## 🔗 Related Files

- Backend endpoint: `backend/routes.py`
- Frontend service: `frontend/src/services/credibilityApi.ts`
- React hook: `frontend/src/hooks/useCredibilityCheck.ts`
- Example component: `frontend/src/components/CredibilityChecker.tsx`
- Full documentation: `backend/CREDIBILITY_API.md`
