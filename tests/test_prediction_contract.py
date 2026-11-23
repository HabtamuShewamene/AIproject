"""Test suite verifying the Phase 3 prediction contract schema and guaranteed keys."""

import pytest
from app.predictor import predict_sentiment


GUARANTEED_CONTRACT_KEYS = {
    "text",
    "original_text",
    "translated_text",
    "language",
    "language_status",
    "model_version",
    "sentiment",
    "confidence",
    "low_confidence",
    "probabilities",
    "processing_status",
}

EXPECTED_PROBABILITY_CLASSES = {"negative", "neutral", "positive"}


def test_predict_sentiment_returns_all_contract_keys():
    result = predict_sentiment("The quick brown fox jumps over the lazy dog.")

    missing_keys = GUARANTEED_CONTRACT_KEYS - set(result.keys())
    assert not missing_keys, f"Missing guaranteed contract keys: {missing_keys}"


def test_predict_sentiment_types():
    result = predict_sentiment("The service was exceptionally helpful and prompt.")

    assert isinstance(result["text"], str)
    assert isinstance(result["original_text"], str)
    assert isinstance(result["translated_text"], str)
    assert isinstance(result["language"], str)
    assert isinstance(result["language_status"], str)
    assert isinstance(result["model_version"], str)
    assert isinstance(result["sentiment"], str)
    assert isinstance(result["confidence"], float)
    assert isinstance(result["low_confidence"], bool)
    assert isinstance(result["probabilities"], dict)
    assert isinstance(result["processing_status"], str)


def test_probabilities_sum_to_one_and_have_correct_classes():
    result = predict_sentiment("We had a wonderful vacation at the beach.")

    probs = result["probabilities"]
    assert set(probs.keys()) == EXPECTED_PROBABILITY_CLASSES

    prob_sum = sum(probs.values())
    assert 0.99 <= prob_sum <= 1.01, f"Probabilities should sum to ~1.0, got {prob_sum}"


def test_model_version_is_non_empty_and_valid():
    result = predict_sentiment("Standard factual sentence for version checking.")

    assert len(result["model_version"]) > 0
    assert result["model_version"] != ""


# ---------------------------------------------------------------------------
# Boundary & Length Tests
# ---------------------------------------------------------------------------

def test_empty_input_returns_too_short():
    result = predict_sentiment("")

    assert result["processing_status"] == "too_short"
    assert result["sentiment"] == "uncertain"
    assert result["low_confidence"] is True
    assert result["confidence"] == 0.0


def test_whitespace_only_input_returns_too_short():
    result = predict_sentiment("     ")

    assert result["processing_status"] == "too_short"
    assert result["sentiment"] == "uncertain"
    assert result["low_confidence"] is True


def test_sub_minimum_length_returns_too_short():
    result = predict_sentiment("hi")

    assert result["processing_status"] == "too_short"
    assert result["sentiment"] == "uncertain"
    assert result["low_confidence"] is True
    assert "at least 3 characters" in result.get("detail", "")


def test_overlong_input_is_truncated_and_flagged():
    long_text = ("Good morning! " * 200).strip()  # 2799 characters, exceeds MAX_INPUT_CHARS (2000)

    result = predict_sentiment(long_text)

    assert result["processing_status"] == "truncated"
    assert len(result["text"]) == len(long_text)  # original stripped text preserved
    assert len(result["translated_text"]) <= 2000  # truncated for model
    assert result["sentiment"] in {"positive", "neutral", "negative", "uncertain"}


