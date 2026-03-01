"""
credibility_engine.py
=====================
Real-Time News Credibility Scoring Engine
Designed for WhatsApp Bot + Decentralized Web3 Platform

Usage in main bot (main.py):
    from credibility_engine import CredibilityEngine
    engine = CredibilityEngine()
    result = await engine.score(claim, source_url, rag_context, web_context, votes_data)
"""

import re
import json
import math
import hashlib
import asyncio
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
import httpx

# ─────────────────────────────────────────────
# SOURCE CREDIBILITY REGISTRY
# Loaded from Official_Indian_Government_Verification_Sources.pdf
# + Trusted_Media_Houses_India_International.pdf
# ─────────────────────────────────────────────

TIER_1_DOMAINS = {
    # Government
    "pib.gov.in", "pmindia.gov.in", "egazette.nic.in", "mha.gov.in",
    "mohfw.gov.in", "education.gov.in", "rbi.org.in", "sebi.gov.in",
    "eci.gov.in", "uidai.gov.in", "finmin.nic.in", "rural.nic.in",
    # Tier 1 India Media
    "thehindu.com", "indianexpress.com", "hindustantimes.com",
    "timesofindia.indiatimes.com", "economictimes.indiatimes.com",
    "business-standard.com", "livemint.com",
    # International Wire Services
    "reuters.com", "apnews.com", "afp.com", "bloomberg.com",
    "bbc.com", "pbs.org",
}

TIER_2_DOMAINS = {
    "ndtv.com", "indiatoday.in", "news18.com", "republicworld.com",
    "timesnownews.com", "ddnews.gov.in", "newsonair.gov.in",
    "cnn.com", "nytimes.com", "washingtonpost.com", "aljazeera.com",
    "dw.com", "abc.net.au",
}

GOV_PATTERNS = [r"\.gov\.in$", r"\.nic\.in$", r"\.gov\.in/", r"uidai\.gov\.in"]

# ─────────────────────────────────────────────
# LINGUISTIC MISINFORMATION SIGNALS
# ─────────────────────────────────────────────

CLICKBAIT_PATTERNS = [
    r"\bbreaking\b", r"\bshocking\b", r"\bviral\b", r"\bexclusive\b",
    r"\bsecret\b", r"\bhidden\b", r"\bthey don.t want you\b",
    r"\byou won.t believe\b", r"\bfree money\b", r"\binstant\b",
    r"\bguaranteed\b", r"100%\s*(free|cash|money)",
]

URGENCY_PATTERNS = [
    r"(act now|limited time|expires today|last chance|hurry)",
    r"(claim (your|now|immediately))",
    r"(don.t miss|share immediately|forward to all)",
]

NUMERICAL_ANOMALY_PATTERNS = [
    r"₹\s*[\d,]+\s*(lakh|crore|lakhs|crores)",  # Large amounts
    r"\b(every|each)\s+(citizen|indian|person)\b",
    r"\b(free|subsidy)\s+of\s+₹",
]

SCHEME_IMPERSONATION = [
    r"pm\s*(modi|cares|kisan|awas|ujjwala|jan dhan)",
    r"(pradhan mantri|sarkar|government)\s+(is giving|is offering|will give)",
    r"(aadhar|ration card|voter id)\s+(linked|required|mandatory)\s+(for|to get)",
]


# ─────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class CredibilityResult:
    claim: str
    claim_hash: str

    # Scores (0.0 – 1.0)
    source_score: float
    linguistic_score: float
    numerical_score: float
    rag_match_score: float
    temporal_score: float
    community_score: float

    # Final composite
    final_score: float          # 0.0 – 1.0
    confidence: float           # 0.0 – 1.0

    # Classification
    verdict: str                # TRUE | FALSE | UNCERTAIN | UNVERIFIED | BREAKING
    risk_level: str             # low | medium | high | critical

    # Explainability
    flags: list
    sources_found: list
    explanation: str

    # Metadata
    timestamp: str
    processing_ms: int

    def to_json(self) -> dict:
        return asdict(self)


# ─────────────────────────────────────────────
# MAIN ENGINE
# ─────────────────────────────────────────────

class CredibilityEngine:
    """
    Modular real-time credibility scoring engine.
    Import and call from your WhatsApp bot (main.py).

    Pipeline:
        Input Claim
            │
            ▼
        [1] Feature Extraction
            ├── NER (person, amount, scheme, date)
            ├── Source Classifier (tier 1/2/unknown)
            ├── Linguistic Signal Detector
            └── Numerical Anomaly Detector
            │
            ▼
        [2] Multi-Layer Scoring
            ├── source_score      (0–1)
            ├── linguistic_score  (0–1, inverted – lower = more suspicious)
            ├── numerical_score   (0–1, inverted)
            ├── rag_match_score   (0–1, from ChromaDB similarity)
            ├── temporal_score    (0–1)
            └── community_score   (0–1, from blockchain votes)
            │
            ▼
        [3] Weighted Composite Score
            │   W = [0.25, 0.20, 0.15, 0.20, 0.10, 0.10]
            ▼
        [4] Threshold Classification
            │   ≥ 0.72 → TRUE
            │   0.48–0.71 → UNCERTAIN
            │   < 0.48 → FALSE / HIGH RISK
            ▼
        [5] Explainability Layer → JSON Output
    """

    def __init__(self):
        self.weights = {
            "source":     0.25,
            "linguistic": 0.20,
            "numerical":  0.15,
            "rag_match":  0.20,
            "temporal":   0.10,
            "community":  0.10,
        }
        # Confidence calibration: Platt Scaling approximation
        self._platt_a = -1.8
        self._platt_b = 0.5

    # ──────────────────────────────────────────
    # PUBLIC API
    # ──────────────────────────────────────────

    async def score(
        self,
        claim: str,
        source_url: Optional[str] = None,
        rag_context: Optional[str] = None,
        web_context: Optional[str] = None,
        votes_data: Optional[dict] = None,
    ) -> CredibilityResult:
        """
        Main entry point. Call from main.py:
            result = await engine.score(claim, source_url, rag_ctx, web_ctx, votes)
            print(result.to_json())
        """
        t_start = datetime.utcnow()

        claim = claim.strip()
        claim_hash = self._hash_claim(claim)
        flags = []

        # ── Layer 1: Source Score ─────────────────
        source_score, source_flags, sources_found = self._score_source(source_url, web_context)
        flags.extend(source_flags)

        # ── Layer 2: Linguistic Score ─────────────
        linguistic_score, ling_flags = self._score_linguistic(claim)
        flags.extend(ling_flags)

        # ── Layer 3: Numerical Anomaly Score ──────
        numerical_score, num_flags = self._score_numerical(claim)
        flags.extend(num_flags)

        # ── Layer 4: RAG Match Score ───────────────
        rag_score, rag_flags = self._score_rag_match(claim, rag_context)
        flags.extend(rag_flags)

        # ── Layer 5: Temporal Score ───────────────
        temporal_score, temp_flags = self._score_temporal(claim, web_context)
        flags.extend(temp_flags)

        # ── Layer 6: Community Score ──────────────
        community_score, comm_flags = self._score_community(votes_data)
        flags.extend(comm_flags)

        # ── Composite Weighted Score ──────────────
        final_score = self._composite_score(
            source_score, linguistic_score, numerical_score,
            rag_score, temporal_score, community_score
        )

        # ── Calibrated Confidence ─────────────────
        confidence = self._calibrate_confidence(final_score, len(sources_found))

        # ── Verdict & Risk ────────────────────────
        verdict, risk_level = self._classify(final_score, flags, rag_score, sources_found)

        # ── Explainability ────────────────────────
        explanation = self._explain(
            verdict, final_score, confidence, flags,
            source_score, linguistic_score, numerical_score, rag_score
        )

        t_end = datetime.utcnow()
        ms = int((t_end - t_start).total_seconds() * 1000)

        return CredibilityResult(
            claim=claim,
            claim_hash=claim_hash,
            source_score=round(source_score, 3),
            linguistic_score=round(linguistic_score, 3),
            numerical_score=round(numerical_score, 3),
            rag_match_score=round(rag_score, 3),
            temporal_score=round(temporal_score, 3),
            community_score=round(community_score, 3),
            final_score=round(final_score, 3),
            confidence=round(confidence, 3),
            verdict=verdict,
            risk_level=risk_level,
            flags=list(set(flags)),
            sources_found=sources_found,
            explanation=explanation,
            timestamp=t_start.isoformat(),
            processing_ms=ms,
        )

    # ──────────────────────────────────────────
    # LAYER 1: SOURCE CLASSIFIER
    # ──────────────────────────────────────────

    def _score_source(self, source_url, web_context):
        score = 0.5  # default: neutral for unknown source
        flags = []
        sources_found = []

        if source_url:
            domain = self._extract_domain(source_url)
            if domain in TIER_1_DOMAINS:
                score = 0.92
                sources_found.append({"domain": domain, "tier": 1})
            elif domain in TIER_2_DOMAINS:
                score = 0.72
                sources_found.append({"domain": domain, "tier": 2})
            elif any(re.search(p, domain) for p in GOV_PATTERNS):
                score = 0.88
                sources_found.append({"domain": domain, "tier": "gov"})
                flags.append("government_source_detected")
            else:
                score = 0.35
                flags.append("unverified_source")

        # Scan web context for trusted domain mentions
        if web_context:
            for domain in TIER_1_DOMAINS:
                if domain in web_context:
                    score = max(score, 0.78)
                    if domain not in [s.get("domain") for s in sources_found]:
                        sources_found.append({"domain": domain, "tier": "web_mention"})

        if not sources_found:
            flags.append("no_verified_source")

        return score, flags, sources_found

    # ──────────────────────────────────────────
    # LAYER 2: LINGUISTIC MISINFORMATION SIGNALS
    # ──────────────────────────────────────────

    def _score_linguistic(self, claim):
        """
        Returns 1.0 = clean text, 0.0 = maximum manipulation signals.
        Deductions applied per pattern category.
        """
        score = 1.0
        flags = []
        text = claim.lower()

        clickbait_hits = sum(1 for p in CLICKBAIT_PATTERNS if re.search(p, text))
        if clickbait_hits > 0:
            score -= min(0.35, clickbait_hits * 0.12)
            flags.append(f"clickbait_language:{clickbait_hits}_signals")

        urgency_hits = sum(1 for p in URGENCY_PATTERNS if re.search(p, text))
        if urgency_hits > 0:
            score -= min(0.25, urgency_hits * 0.10)
            flags.append("urgency_manipulation")

        scheme_hits = sum(1 for p in SCHEME_IMPERSONATION if re.search(p, text))
        if scheme_hits > 0:
            score -= min(0.30, scheme_hits * 0.12)
            flags.append("scheme_impersonation_suspected")

        # All-caps check (shouting = manipulation signal)
        words = claim.split()
        caps_ratio = sum(1 for w in words if w.isupper() and len(w) > 2) / max(len(words), 1)
        if caps_ratio > 0.3:
            score -= 0.15
            flags.append("excessive_caps")

        return max(0.0, score), flags

    # ──────────────────────────────────────────
    # LAYER 3: NUMERICAL ANOMALY DETECTOR
    # ──────────────────────────────────────────

    def _score_numerical(self, claim):
        """
        Detects implausible amounts, universal benefit claims, fake subsidies.
        Returns 1.0 = no anomaly, lower = more suspicious.
        """
        score = 1.0
        flags = []
        text = claim.lower()

        # Extract all monetary amounts
        amounts = re.findall(r'₹\s*([\d,]+)', text)
        for amt_str in amounts:
            amt = int(amt_str.replace(",", ""))
            # Implausibly large direct transfer
            if amt > 50000:
                score -= 0.35
                flags.append(f"implausible_amount:₹{amt:,}")
            elif amt > 10000:
                score -= 0.15
                flags.append(f"large_transfer_claim:₹{amt:,}")

        # "Every citizen" type universal claims
        for p in NUMERICAL_ANOMALY_PATTERNS:
            if re.search(p, text):
                score -= 0.20
                flags.append("universal_benefit_claim")
                break

        # Percentage anomalies
        pcts = re.findall(r'(\d+)\s*%', text)
        for pct in pcts:
            if int(pct) > 90:
                score -= 0.10
                flags.append(f"extreme_percentage:{pct}%")

        return max(0.0, score), flags

    # ──────────────────────────────────────────
    # LAYER 4: RAG MATCH SCORE
    # ──────────────────────────────────────────

    def _score_rag_match(self, claim, rag_context):
        """
        Converts ChromaDB retrieval result into a 0–1 match score.
        High similarity to known fraud = lower score.
        High similarity to known valid scheme = higher score.
        """
        score = 0.5  # neutral: unknown
        flags = []

        if not rag_context or rag_context == "No matching government schemes found.":
            flags.append("no_database_match")
            return 0.4, flags

        # Keyword overlap approximation (real implementation uses vector similarity)
        claim_words = set(claim.lower().split())
        context_words = set(rag_context.lower().split())
        overlap = len(claim_words & context_words) / max(len(claim_words), 1)

        score = min(0.95, 0.4 + overlap * 0.8)

        # Fraud indicators in RAG context
        if any(w in rag_context.lower() for w in ["fraud", "fake", "scam", "false", "hoax"]):
            score = max(0.0, score - 0.40)
            flags.append("database_fraud_indicator")

        if overlap > 0.4:
            flags.append(f"strong_database_match:{overlap:.0%}")

        return round(score, 3), flags

    # ──────────────────────────────────────────
    # LAYER 5: TEMPORAL SCORE
    # ──────────────────────────────────────────

    def _score_temporal(self, claim, web_context):
        """
        Breaking news = UNVERIFIED by default (not FALSE).
        Old recycled news = higher suspicion.
        """
        score = 0.75  # default
        flags = []
        text = claim.lower()

        breaking_patterns = [r"\bbreaking\b", r"\bjust in\b", r"\blive\b", r"\bunfolding\b"]
        if any(re.search(p, text) for p in breaking_patterns):
            score = 0.45
            flags.append("breaking_news_unverified")

        # Year extraction — recycled old news detection
        years = re.findall(r'\b(20[0-1][0-9])\b', text)
        current_year = datetime.utcnow().year
        for yr in years:
            if int(yr) < current_year - 2:
                score -= 0.15
                flags.append(f"potentially_recycled_news:{yr}")

        return max(0.0, score), flags

    # ──────────────────────────────────────────
    # LAYER 6: COMMUNITY SCORE (BLOCKCHAIN)
    # ──────────────────────────────────────────

    def _score_community(self, votes_data):
        """
        Converts blockchain vote data into 0–1 score.
        Validator votes weighted 3x over user votes.
        Only activates if enough votes exist (minimum 5).
        """
        score = 0.5
        flags = []

        if not votes_data:
            flags.append("no_community_data")
            return score, flags

        user_v = votes_data.get("user_votes", {"true": 0, "false": 0})
        val_v = votes_data.get("validator_votes", {"true": 0, "false": 0})

        total_users = user_v.get("true", 0) + user_v.get("false", 0)
        total_validators = val_v.get("true", 0) + val_v.get("false", 0)

        if total_users + total_validators < 5:
            flags.append("insufficient_community_votes")
            return 0.5, flags

        user_pct = user_v.get("true", 0) / max(total_users, 1)
        val_pct = val_v.get("true", 0) / max(total_validators, 1)

        # Validators weighted 3x
        if total_validators > 0:
            score = (user_pct * 1 + val_pct * 3) / 4
        else:
            score = user_pct

        if score > 0.75:
            flags.append("community_consensus_true")
        elif score < 0.35:
            flags.append("community_consensus_false")

        return round(score, 3), flags

    # ──────────────────────────────────────────
    # COMPOSITE + CALIBRATION
    # ──────────────────────────────────────────

    def _composite_score(self, src, ling, num, rag, temp, comm):
        """
        Weighted sum:
            source(25%) + linguistic(20%) + numerical(15%) +
            rag_match(20%) + temporal(10%) + community(10%)
        """
        w = self.weights
        return (
            src  * w["source"]     +
            ling * w["linguistic"] +
            num  * w["numerical"]  +
            rag  * w["rag_match"]  +
            temp * w["temporal"]   +
            comm * w["community"]
        )

    def _calibrate_confidence(self, score, num_sources):
        """
        Platt Scaling approximation for probability calibration.
        More sources = higher confidence in score.
        """
        # Sigmoid transformation
        raw = 1 / (1 + math.exp(self._platt_a * score + self._platt_b))
        # Scale confidence by evidence quantity
        source_boost = min(0.15, num_sources * 0.05)
        return min(1.0, raw + source_boost)

    # ──────────────────────────────────────────
    # CLASSIFICATION
    # ──────────────────────────────────────────

    def _classify(self, score, flags, rag_score, sources_found):
        """
        Maps composite score to verdict + risk level.

        Thresholds:
            ≥ 0.72  → TRUE    | low
            0.55–0.71 → UNCERTAIN | medium
            0.40–0.54 → UNCERTAIN | high
            < 0.40  → FALSE   | critical

        Special case: breaking_news_unverified flag → BREAKING (not FALSE)
        Special case: no_database_match + no_verified_source → UNVERIFIED
        """
        breaking = "breaking_news_unverified" in flags
        no_data = "no_database_match" in flags and "no_verified_source" in flags

        if breaking and score < 0.72:
            return "BREAKING", "medium"

        if no_data and score < 0.55:
            return "UNVERIFIED", "medium"

        if score >= 0.72:
            return "TRUE", "low"
        elif score >= 0.55:
            return "UNCERTAIN", "medium"
        elif score >= 0.40:
            return "UNCERTAIN", "high"
        else:
            return "FALSE", "critical"

    # ──────────────────────────────────────────
    # EXPLAINABILITY
    # ──────────────────────────────────────────

    def _explain(self, verdict, score, confidence, flags, src, ling, num, rag):
        """Produces human-readable explanation for WhatsApp output."""
        parts = []

        verdict_map = {
            "TRUE": "✅ Claim appears credible",
            "FALSE": "❌ Claim likely false or misleading",
            "UNCERTAIN": "⚠️ Insufficient evidence to verify",
            "UNVERIFIED": "🔍 Claim could not be verified against known sources",
            "BREAKING": "⏳ Breaking news — verification pending",
        }
        parts.append(verdict_map.get(verdict, "❓ Unknown"))
        parts.append(f"Credibility Score: {score:.0%} | Confidence: {confidence:.0%}")

        # Layer breakdown
        dominant_factor = max(
            [("Source Trust", src), ("Language Quality", ling),
             ("Amount Plausibility", num), ("Database Match", rag)],
            key=lambda x: x[1]
        )
        parts.append(f"Strongest factor: {dominant_factor[0]} ({dominant_factor[1]:.0%})")

        if flags:
            readable_flags = [f.replace("_", " ").title() for f in flags[:3]]
            parts.append("Signals: " + ", ".join(readable_flags))

        return " | ".join(parts)

    # ──────────────────────────────────────────
    # UTILITIES
    # ──────────────────────────────────────────

    def _hash_claim(self, claim):
        return "0x" + hashlib.sha256(claim.encode()).hexdigest()[:40]

    def _extract_domain(self, url):
        url = url.lower().strip()
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        return url.split('/')[0].split('?')[0]


# ─────────────────────────────────────────────
# OUTPUT JSON SCHEMA (Reference)
# ─────────────────────────────────────────────
"""
RESPONSE SCHEMA:
{
  "claim": "string",
  "claim_hash": "0x...",
  "source_score": float,         // 0.0–1.0
  "linguistic_score": float,
  "numerical_score": float,
  "rag_match_score": float,
  "temporal_score": float,
  "community_score": float,
  "final_score": float,          // Weighted composite
  "confidence": float,           // Platt-calibrated
  "verdict": "TRUE|FALSE|UNCERTAIN|UNVERIFIED|BREAKING",
  "risk_level": "low|medium|high|critical",
  "flags": ["string", ...],      // Explainability signals
  "sources_found": [
    {"domain": "thehindu.com", "tier": 1}
  ],
  "explanation": "string",       // Human-readable
  "timestamp": "ISO8601",
  "processing_ms": int
}
"""
