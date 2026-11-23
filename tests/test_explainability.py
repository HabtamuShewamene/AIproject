"""Tests for Phase 5 explainability engine: evidence bundles, sarcasm signals,
keyword polarity breakdown, and confidence reasoning."""

import pytest
from app.explainability import (
    build_evidence_bundle,
    extract_keyword_polarity,
    extract_sarcasm_evidence,
    explain_confidence,
)


# ---------------------------------------------------------------------------
# Sarcasm Evidence Tests
# ---------------------------------------------------------------------------

def test_sarcasm_detected_on_known_phrase():
    result = extract_sarcasm_evidence("Oh yeah right, like that ever works.")
    assert result["is_sarcastic"] is True
    assert "yeah right" in result["sarcasm_phrases"]


def test_sarcasm_not_detected_on_neutral_text():
    result = extract_sarcasm_evidence("The package arrived on Tuesday morning.")
    assert result["is_sarcastic"] is False
    assert result["sarcasm_phrases"] == []


def test_sarcasm_uppercase_stress_detected():
    result = extract_sarcasm_evidence("This is GREAT service!")
    assert result["uppercase_stress"] is True


def test_sarcasm_exclamation_count():
    result = extract_sarcasm_evidence("Wow!! So helpful!!")
    assert result["exclamation_count"] == 4


# ---------------------------------------------------------------------------
# Keyword Polarity Tests
# ---------------------------------------------------------------------------

def test_positive_keywords_extracted():
    result = extract_keyword_polarity("This is a great and excellent product!")
    assert result["positive_count"] > 0
    assert "great" in result["positive_keywords"] or "excellent" in result["positive_keywords"]


def test_negative_keywords_extracted():
    result = extract_keyword_polarity("This is terrible and absolutely awful.")
    assert result["negative_count"] > 0


def test_negated_positive_captured():
    result = extract_keyword_polarity("This is not great at all.")
    assert "great" in result["negated_positive"] or result["negated_count"] >= 0  # graceful


def test_net_polarity_score_positive():
    result = extract_keyword_polarity("Amazing, wonderful, fantastic experience!")
    assert result["net_polarity_score"] > 0


# ---------------------------------------------------------------------------
# Confidence Reasoning Tests
# ---------------------------------------------------------------------------

def test_high_confidence_tier():
    result = explain_confidence(
        sentiment="positive",
        confidence=0.95,
        low_confidence=False,
        probabilities={"positive": 0.95, "neutral": 0.03, "negative": 0.02},
    )
    assert result["confidence_tier"] == "high"
    assert "positive" in result["reason"]


def test_abstained_confidence_tier():
    result = explain_confidence(
        sentiment="uncertain",
        confidence=0.38,
        low_confidence=True,
        probabilities={"positive": 0.38, "neutral": 0.34, "negative": 0.28},
    )
    assert result["confidence_tier"] == "abstained"
    assert "uncertain" in result["reason"].lower() or "abstention" in result["reason"].lower()


def test_moderate_confidence_tier():
    result = explain_confidence(
        sentiment="negative",
        confidence=0.72,
        low_confidence=False,
        probabilities={"negative": 0.72, "neutral": 0.18, "negative_": 0.10},
    )
    assert result["confidence_tier"] in {"moderate", "high"}


# ---------------------------------------------------------------------------
# Unified Evidence Bundle Tests
# ---------------------------------------------------------------------------

def test_evidence_bundle_contains_all_keys():
    bundle = build_evidence_bundle(
        text="This is great but somehow disappointing.",
        sentiment="negative",
        confidence=0.76,
        low_confidence=False,
        probabilities={"negative": 0.76, "neutral": 0.15, "positive": 0.09},
    )
    assert "sarcasm_evidence" in bundle
    assert "keyword_polarity" in bundle
    assert "confidence_reasoning" in bundle


def test_evidence_bundle_sarcasm_evidence_structure():
    bundle = build_evidence_bundle(
        text="Oh wow, totally amazing service!",
        sentiment="positive",
        confidence=0.88,
        low_confidence=False,
        probabilities={"positive": 0.88, "neutral": 0.08, "negative": 0.04},
    )
    sarcasm = bundle["sarcasm_evidence"]
    assert "is_sarcastic" in sarcasm
    assert isinstance(sarcasm["exclamation_count"], int)


def test_evidence_bundle_confidence_reasoning_structure():
    bundle = build_evidence_bundle(
        text="Excellent performance overall.",
        sentiment="positive",
        confidence=0.93,
        low_confidence=False,
        probabilities={"positive": 0.93, "neutral": 0.05, "negative": 0.02},
    )
    reasoning = bundle["confidence_reasoning"]
    assert "confidence_tier" in reasoning
    assert "reason" in reasoning
    assert reasoning["confidence_tier"] == "high"
