"""Sentiment prediction powered primarily by the trained BERT model."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.config import MODEL_PATH
from app.sentiment_rules import (
    NEGATIVE_WORDS,
    POSITIVE_WORDS,
    contains_sarcasm,
    count_keywords,
    has_negation,
    sarcasm_score,
)
from app.translator import translate_to_english


LABEL_MAP = {
    0: "negative",
    1: "positive",
}

LOCAL_MODEL_FALLBACK = Path(__file__).resolve().parent.parent / "models" / "bert_sentiment"


@lru_cache(maxsize=1)
def _load_model_bundle():
    model_path = Path(MODEL_PATH)
    candidate_paths = [model_path]

    if not model_path.is_absolute():
        candidate_paths.append(LOCAL_MODEL_FALLBACK)

    last_error: Exception | None = None

    for candidate in candidate_paths:
        if not candidate.exists():
            continue

        try:
            tokenizer = AutoTokenizer.from_pretrained(candidate)
            model = AutoModelForSequenceClassification.from_pretrained(candidate)
            model.eval()
            return tokenizer, model
        except Exception as exc:  # pragma: no cover - runtime safety
            last_error = exc

    raise RuntimeError(
        "Unable to load the trained sentiment model from MODEL_PATH."
    ) from last_error


def _softmax_scores(logits: torch.Tensor) -> torch.Tensor:
    return torch.softmax(logits, dim=-1)


def _predict_with_model(text: str) -> tuple[str, float]:
    tokenizer, model = _load_model_bundle()

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128,
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probs = _softmax_scores(outputs.logits)[0]
    label_id = int(torch.argmax(probs).item())
    confidence = float(probs[label_id].item())

    sentiment = LABEL_MAP.get(label_id, "neutral")
    if sentiment not in {"positive", "negative"}:
        sentiment = "neutral"

    return sentiment, round(confidence, 4)


def _apply_rule_helpers(
    text: str,
    sentiment: str,
    confidence: float,
) -> tuple[str, float]:
    """Light correction layer for edge cases when the model is unsure."""

    lower_text = (text or "").lower()

    positive_hits = count_keywords(lower_text, POSITIVE_WORDS)
    negative_hits = count_keywords(lower_text, NEGATIVE_WORDS)

    sarcasm_strength = sarcasm_score(lower_text)

    if sarcasm_strength >= 2:
        if sentiment == "positive" and confidence < 0.95:
            sentiment = "negative"
            confidence = min(confidence + 0.08, 0.99)
        else:
            confidence = min(confidence + 0.04, 0.99)
    elif confidence < 0.60:
        if contains_sarcasm(lower_text) and positive_hits > 0:
            confidence = min(confidence + 0.05, 0.99)

        if has_negation(lower_text) and positive_hits > negative_hits:
            confidence = min(confidence + 0.03, 0.99)

    return sentiment, round(confidence, 4)


def predict_sentiment(text):
    clean_text = (text or "").strip()

    if not clean_text:
        raise ValueError("Text is required for sentiment prediction.")

    translated_text, language = translate_to_english(clean_text)
    model_input = translated_text or clean_text
    sentiment, confidence = _predict_with_model(model_input)
    sentiment, confidence = _apply_rule_helpers(model_input, sentiment, confidence)

    return {
        "original_text": clean_text,
        "translated_text": translated_text or clean_text,
        "language": language,
        "sentiment": sentiment,
        "confidence": confidence,
    }
