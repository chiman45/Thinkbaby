/**
 * CredibilityChecker Component
 * 
 * Example component demonstrating how to use the credibility check API
 */

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useCredibilityCheck } from '@/hooks/useCredibilityCheck';
import {
  getVerdictEmoji,
  getRiskEmoji,
  formatScore,
  getVerdictDescription,
  getRiskDescription,
} from '@/services/credibilityApi';

export function CredibilityChecker() {
  const [claim, setClaim] = useState('');
  const { result, loading, error, quickCheck, reset } = useCredibilityCheck();

  const handleCheck = async () => {
    if (claim.trim().length < 5) {
      return;
    }
    await quickCheck(claim);
  };

  const handleReset = () => {
    setClaim('');
    reset();
  };

  // Verdict color mapping
  const verdictColorMap = {
    TRUE: 'bg-green-100 text-green-800 border-green-300',
    FALSE: 'bg-red-100 text-red-800 border-red-300',
    UNCERTAIN: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    UNVERIFIED: 'bg-gray-100 text-gray-800 border-gray-300',
    BREAKING: 'bg-blue-100 text-blue-800 border-blue-300',
  };

  const riskColorMap = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span>🔍</span>
            <span>Claim Credibility Checker</span>
          </CardTitle>
          <CardDescription>
            Enter a claim to verify its credibility using AI-powered analysis
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Input Section */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Claim to Verify</label>
            <Textarea
              placeholder="Enter a claim to fact-check (e.g., 'PM Kisan Yojana provides ₹6000 annually to farmers')"
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              rows={4}
              className="resize-none"
            />
            <p className="text-xs text-muted-foreground">
              Minimum 5 characters required
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button
              onClick={handleCheck}
              disabled={loading || claim.trim().length < 5}
              className="flex-1"
            >
              {loading ? 'Analyzing...' : 'Check Credibility'}
            </Button>
            {result && (
              <Button onClick={handleReset} variant="outline">
                Reset
              </Button>
            )}
          </div>

          {/* Error State */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Results Section */}
          {result && (
            <div className="space-y-4 border-t pt-4">
              {/* Main Verdict */}
              <div className={`p-4 rounded-lg border-2 ${verdictColorMap[result.verdict]}`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{getVerdictEmoji(result.verdict)}</span>
                    <h3 className="text-lg font-bold">{result.verdict}</h3>
                  </div>
                  <Badge className={riskColorMap[result.risk_level]}>
                    {getRiskEmoji(result.risk_level)} {result.risk_level.toUpperCase()}
                  </Badge>
                </div>
                <p className="text-sm mb-2">{getVerdictDescription(result.verdict)}</p>
                <p className="text-xs opacity-75">{getRiskDescription(result.risk_level)}</p>
              </div>

              {/* Score Breakdown */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Credibility Analysis</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold">Overall Score</span>
                    <span className="text-2xl font-bold">{formatScore(result.final_score)}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span>Confidence</span>
                    <span className="font-medium">{formatScore(result.confidence)}</span>
                  </div>

                  <div className="border-t pt-3 space-y-2">
                    <h4 className="text-sm font-semibold mb-2">Score Breakdown</h4>
                    {[
                      { label: 'Source Trust', value: result.source_score },
                      { label: 'Language Quality', value: result.linguistic_score },
                      { label: 'Amount Plausibility', value: result.numerical_score },
                      { label: 'Database Match', value: result.rag_match_score },
                      { label: 'Temporal Analysis', value: result.temporal_score },
                      { label: 'Community Votes', value: result.community_score },
                    ].map((item) => (
                      <div key={item.label} className="flex justify-between items-center text-sm">
                        <span className="text-muted-foreground">{item.label}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                item.value >= 0.7
                                  ? 'bg-green-500'
                                  : item.value >= 0.4
                                  ? 'bg-yellow-500'
                                  : 'bg-red-500'
                              }`}
                              style={{ width: `${item.value * 100}%` }}
                            />
                          </div>
                          <span className="font-medium w-12 text-right">{formatScore(item.value)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Explanation */}
              <Alert>
                <AlertDescription>{result.explanation}</AlertDescription>
              </Alert>

              {/* Flags */}
              {result.flags.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Detection Signals</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {result.flags.map((flag, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {flag.replace(/_/g, ' ')}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Sources */}
              {result.sources_found.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Verified Sources</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {result.sources_found.map((source, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between text-sm p-2 bg-gray-50 rounded"
                        >
                          <span className="font-medium">{source.domain}</span>
                          <Badge variant="secondary">Tier {source.tier}</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Metadata */}
              <div className="text-xs text-muted-foreground flex gap-4">
                <span>Processed in {result.processing_ms}ms</span>
                <span>Hash: {result.claim_hash.slice(0, 10)}...</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default CredibilityChecker;
