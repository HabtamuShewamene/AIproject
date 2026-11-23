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
    "latency_ms",
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
    assert isinstance(result["latency_ms"], float)



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


# ---------------------------------------------------------------------------
# Confidence & Abstention Tests
# ---------------------------------------------------------------------------

def test_abstention_triggers_uncertain_when_confidence_below_threshold(monkeypatch):
    import app.predictor as predictor

    # Mock _run_inference to simulate an ambiguous prediction (max prob 0.40 < threshold 0.45)
    mock_probs = {"negative": 0.35, "neutral": 0.40, "positive": 0.25}
    monkeypatch.setattr(
        predictor,
        "_run_inference",
        lambda _text: ("uncertain", 0.40, mock_probs),
    )

    result = predictor.predict_sentiment("This experience was somewhat unremarkable and ambiguous.")

    assert result["sentiment"] == "uncertain"
    assert result["low_confidence"] is True
    assert result["confidence"] == 0.40
    assert result["probabilities"] == mock_probs


def test_high_confidence_clears_abstention(monkeypatch):
    import app.predictor as predictor

    mock_probs = {"negative": 0.05, "neutral": 0.10, "positive": 0.85}
    monkeypatch.setattr(
        predictor,
        "_run_inference",
        lambda _text: ("positive", 0.85, mock_probs),
    )

    result = predictor.predict_sentiment("Exceptional service, thoroughly impressed!")

    assert result["sentiment"] == "positive"
    assert result["low_confidence"] is False
    assert result["confidence"] == 0.85


# ---------------------------------------------------------------------------
# Language & Translation Status Tests
# ---------------------------------------------------------------------------

def test_english_language_status():
    result = predict_sentiment("The customer service representative resolved our dispute quickly.")

    assert result["language"] == "en"
    assert result["language_status"] == "english"
    assert result["processing_status"] == "ok"


def test_translated_language_status(monkeypatch):
    import app.predictor as predictor

    # Mock translate_to_english to simulate successful translation from Spanish
    monkeypatch.setattr(
        predictor,
        "translate_to_english",
        lambda _text: ("The food was delicious and fresh.", "es"),
    )

    result = predictor.predict_sentiment("La comida estaba deliciosa y fresca.")

    assert result["language"] == "es"
    assert result["language_status"] == "translated"
    assert result["translated_text"] == "The food was delicious and fresh."
    assert result["processing_status"] == "ok"


def test_translation_failure_is_explicitly_flagged(monkeypatch):
    import app.predictor as predictor

    # Mock translate_to_english to simulate an API/network outage
    monkeypatch.setattr(
        predictor,
        "translate_to_english",
        lambda text: (text, "translation_failed"),
    )

    result = predictor.predict_sentiment("C'était une catastrophe totale.")

    assert result["language"] == "translation_failed"
    assert result["language_status"] == "translation_failed"
    assert result["processing_status"] == "translation_failed"


# ---------------------------------------------------------------------------
# Edge Cases: Negation, Sarcasm & Emojis
# ---------------------------------------------------------------------------

def test_negation_inversion_to_negative():
    result = predict_sentiment("The hotel room was not clean and definitely not quiet.")

    assert result["sentiment"] == "negative"
    assert result["confidence"] > 0.50


def test_negation_inversion_to_positive():
    result = predict_sentiment("I cannot say anything bad about this restaurant, it was flawless.")

    assert result["sentiment"] == "positive"
    assert result["confidence"] > 0.50


def test_sarcasm_social_media_sample():
    # Sarcastic text with conflicting positive words ("wonderful", "dreamed") and negative context
    # correctly triggers either negative or uncertain abstention (never an erroneous high-confidence positive).
    result = predict_sentiment("Oh wonderful, another three hour delay on the tarmac. Exactly what I dreamed of.")

    assert result["sentiment"] in {"negative", "uncertain"}
    assert result["sentiment"] != "positive"



def test_positive_emoji_sentiment():
    result = predict_sentiment("This brand new feature is so amazingly cool! 😍🎉🔥")

    assert result["sentiment"] == "positive"
    assert result["confidence"] > 0.80


def test_negative_emoji_sentiment():
    result = predict_sentiment("Completely broken app, crashed five times in ten minutes 😡💔")

    assert result["sentiment"] == "negative"
    assert result["confidence"] > 0.80


# ---------------------------------------------------------------------------
# Multilingual & Non-English Tests
# ---------------------------------------------------------------------------

def test_amharic_positive_sentence(monkeypatch):
    import app.predictor as predictor

    # Mock translation to avoid live network flakiness in automated testing
    monkeypatch.setattr(
        predictor,
        "translate_to_english",
        lambda _text: ("This service is very excellent and wonderful.", "am"),
    )

    result = predictor.predict_sentiment("ይህ አገልግሎት በጣም ምርጥ እና አስደናቂ ነው")

    assert result["language"] == "am"
    assert result["language_status"] == "translated"
    assert result["sentiment"] == "positive"
    assert result["confidence"] > 0.80


def test_arabic_positive_sentence(monkeypatch):
    import app.predictor as predictor

    monkeypatch.setattr(
        predictor,
        "translate_to_english",
        lambda _text: ("This application is wonderful and very excellent.", "ar"),
    )

    result = predictor.predict_sentiment("هذا التطبيق رائع وممتاز جدا")

    assert result["language"] == "ar"
    assert result["language_status"] == "translated"
    assert result["sentiment"] == "positive"


def test_code_switching_mixed_language(monkeypatch):
    import app.predictor as predictor

    monkeypatch.setattr(
        predictor,
        "translate_to_english",
        lambda _text: ("Very beautiful, I really love this app!", "en"),
    )

    result = predictor.predict_sentiment("Betam konjo new, I really love this app!")

    assert result["sentiment"] == "positive"
    assert result["processing_status"] == "ok"






