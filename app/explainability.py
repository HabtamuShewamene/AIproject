"""
Phase 5 — Explainability & Evidence Engine.

Provides lightweight, model-agnostic token-level attribution, sarcasm
evidence extraction, keyword polarity breakdown, and confidence reasoning
so every prediction carries transparent, human-readable justification.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from app.sentiment_rules import (
    NEGATIVE_WORDS,
    POSITIVE_WORDS,
    contains_sarcasm,
    count_keywords,
    has_negation,
)

# ---------------------------------------------------------------------------
# Sarcasm Evidence Signals
# ---------------------------------------------------------------------------

_SARCASM_PATTERNS: List[str] = [
    "yeah right",
    "oh sure",
    "oh great",
    "totally",
    "obviously",
    "clearly",
    "as if",
    "whatever",
    "big surprise",
    "shocking",
    "oh wow",
    "wow amazing",
    "just great",
    "just wonderful",
    "love how",
    "love it when",
]

_CONTRAST_MARKERS: List[str] = [
    "but",
    "however",
    "although",
    "despite",
    "yet",
    "still",
    "even though",
    "even so",
    "except",
    "unfortunately",
]

_HYPERBOLE_MARKERS: List[str] = [
    "best ever",
    "worst ever",
    "absolutely",
    "literally",
    "literally the worst",
    "literally the best",
    "can't believe",
    "unbelievable",
    "incredible",
    "amazing",
    "unacceptable",
]


def extract_sarcasm_evidence(text: str) -> Dict[str, Any]:
    """Return structured evidence signals for sarcasm detection."""
    lower = text.lower()

    matched_patterns = [p for p in _SARCASM_PATTERNS if p in lower]
    matched_contrasts = [m for m in _CONTRAST_MARKERS if re.search(rf"\b{re.escape(m)}\b", lower)]
    matched_hyperbole = [h for h in _HYPERBOLE_MARKERS if h in lower]

    exclamation_count = text.count("!")
    question_exclamation = "?!" in text or "!?" in text

    has_uppercase_stress = bool(re.search(r"\b[A-Z]{3,}\b", text))

    is_sarcastic = bool(
        matched_patterns
        or (matched_contrasts and matched_hyperbole)
        or (exclamation_count >= 2 and matched_contrasts)
    )

    return {
        "is_sarcastic": is_sarcastic,
        "sarcasm_phrases": matched_patterns,
        "contrast_markers": matched_contrasts,
        "hyperbole_markers": matched_hyperbole,
        "exclamation_count": exclamation_count,
        "question_exclamation": question_exclamation,
        "uppercase_stress": has_uppercase_stress,
    }


# ---------------------------------------------------------------------------
# Keyword Polarity Breakdown
# ---------------------------------------------------------------------------

def extract_keyword_polarity(text: str) -> Dict[str, Any]:
    """Extract positive and negative keyword hits with context spans."""
    lower = text.lower()
    words = re.findall(r"\b\w+\b", lower)

    positive_hits = [w for w in words if w in POSITIVE_WORDS]
    negative_hits = [w for w in words if w in NEGATIVE_WORDS]

    negated_positive: List[str] = []
    negation_patterns = re.compile(
        r"\b(not|no|never|n't|cannot|can't|won't|don't|doesn't)\s+(\w+)", re.IGNORECASE
    )
    for match in negation_patterns.finditer(text):
        negated_word = match.group(2).lower()
        if negated_word in POSITIVE_WORDS:
            negated_positive.append(negated_word)

    net_score = len(positive_hits) - len(negative_hits) - len(negated_positive)

    return {
        "positive_keywords": positive_hits,
        "negative_keywords": negative_hits,
        "negated_positive": negated_positive,
        "positive_count": len(positive_hits),
        "negative_count": len(negative_hits),
        "negated_count": len(negated_positive),
        "net_polarity_score": net_score,
    }


# ---------------------------------------------------------------------------
# Confidence Reasoning Explanation
# ---------------------------------------------------------------------------

def explain_confidence(
    sentiment: str,
    confidence: float,
    low_confidence: bool,
    probabilities: Dict[str, float],
    abstention_threshold: float = 0.45,
) -> Dict[str, Any]:
    """Generate a human-readable reasoning explanation for the confidence score."""

    sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    top_class, top_prob = sorted_probs[0] if sorted_probs else ("unknown", 0.0)
    runner_up_class, runner_up_prob = sorted_probs[1] if len(sorted_probs) > 1 else ("unknown", 0.0)

    gap = round(top_prob - runner_up_prob, 4)

    if low_confidence:
        reason = (
            f"The model is uncertain: top class '{top_class}' scores {top_prob:.1%} "
            f"which is below the abstention threshold of {abstention_threshold:.0%}. "
            f"Runner-up '{runner_up_class}' is at {runner_up_prob:.1%} (gap: {gap:.1%}). "
            "The prediction is marked as 'uncertain' to prevent overconfident misclassification."
        )
        confidence_tier = "abstained"
    elif confidence >= 0.90:
        reason = (
            f"High-confidence decision: '{top_class}' wins with {top_prob:.1%} "
            f"vs '{runner_up_class}' at {runner_up_prob:.1%} (gap: {gap:.1%}). "
            "The model's probability mass is strongly concentrated on a single class."
        )
        confidence_tier = "high"
    elif confidence >= 0.70:
        reason = (
            f"Moderate confidence: '{top_class}' at {top_prob:.1%} leads "
            f"'{runner_up_class}' at {runner_up_prob:.1%} with a gap of {gap:.1%}. "
            "Some ambiguity exists but the leading class is clear."
        )
        confidence_tier = "moderate"
    else:
        reason = (
            f"Low confidence: '{top_class}' at {top_prob:.1%} is above the "
            f"abstention threshold but only marginally leads '{runner_up_class}' at {runner_up_prob:.1%} "
            f"(gap: {gap:.1%}). Treat this result with caution."
        )
        confidence_tier = "low"

    return {
        "confidence_tier": confidence_tier,
        "reason": reason,
        "top_class": top_class,
        "top_probability": round(top_prob, 4),
        "runner_up_class": runner_up_class,
        "runner_up_probability": round(runner_up_prob, 4),
        "probability_gap": gap,
    }


# ---------------------------------------------------------------------------
# Unified Evidence Bundle Builder
# ---------------------------------------------------------------------------

def build_evidence_bundle(
    text: str,
    sentiment: str,
    confidence: float,
    low_confidence: bool,
    probabilities: Optional[Dict[str, float]] = None,
    abstention_threshold: float = 0.45,
) -> Dict[str, Any]:
    """
    Build a complete evidence bundle for a prediction result.
    Returns structured JSON-serialisable insights covering:
    - sarcasm signals
    - keyword polarity breakdown
    - confidence reasoning
    """
    probs = probabilities or {}

    sarcasm = extract_sarcasm_evidence(text)
    keywords = extract_keyword_polarity(text)
    confidence_explanation = explain_confidence(
        sentiment=sentiment,
        confidence=confidence,
        low_confidence=low_confidence,
        probabilities=probs,
        abstention_threshold=abstention_threshold,
    )

    return {
        "sarcasm_evidence": sarcasm,
        "keyword_polarity": keywords,
        "confidence_reasoning": confidence_explanation,
    }
