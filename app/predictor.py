
"""Sentiment prediction powered by the trained BERT model.

Prediction contract (Phase 3)
==============================
Every call to ``predict_sentiment`` returns a dict with the following
guaranteed keys so that callers never need to do ad-hoc .get() with
default magic:

    text            str   – original input (stripped, possibly truncated)
    original_text   str   – same as ``text``
    translated_text str   – English text fed to BERT (= text when already EN)
    language        str   – BCP-47 code, "unknown", or "translation_failed"
    language_status str   – one of: "english" | "translated" | "translation_failed"
                            | "unknown" | "unsupported"
    model_version   str   – value read from config.json ("transformers_version")
    sentiment       str   – "negative" | "neutral" | "positive" | "uncertain"
    confidence      float – softmax probability of the winning class (0–1)
    low_confidence  bool  – True when confidence < ABSTENTION_THRESHOLD
    probabilities   dict  – {"negative": float, "neutral": float, "positive": float}
    processing_status str – "ok" | "too_short" | "truncated" | "translation_failed"
                            | "model_error"
"""

from __future__ import annotations

import json
import time
from functools import lru_cache
from pathlib import Path


import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.config import (
    ABSTENTION_THRESHOLD,
    MAX_INPUT_CHARS,
    MIN_INPUT_CHARS,
    MODEL_PATH,
)
from app.translator import translate_to_english


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LABEL_MAP: dict[int, str] = {0: "negative", 1: "neutral", 2: "positive"}

LOCAL_MODEL_FALLBACK = (
    Path(__file__).resolve().parent.parent / "models" / "bert_sentiment"
)


# ---------------------------------------------------------------------------
# Model loading (singleton via lru_cache)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_model_bundle() -> tuple:
    """Load tokenizer + model once and cache for the process lifetime."""
    model_path = Path(MODEL_PATH)
    candidates = [model_path]
    if not model_path.is_absolute():
        candidates.append(LOCAL_MODEL_FALLBACK)

    last_error: Exception | None = None
    for candidate in candidates:
        if not candidate.exists():
            continue
        try:
            tokenizer = AutoTokenizer.from_pretrained(candidate)
            model = AutoModelForSequenceClassification.from_pretrained(candidate)
            model.eval()
            return tokenizer, model
        except Exception as exc:  # pragma: no cover
            last_error = exc

    raise RuntimeError(
        "Unable to load the trained sentiment model from MODEL_PATH."
    ) from last_error


def _get_model_version() -> str:
    """Read transformers_version from config.json; fall back to 'unknown'."""
    model_path = Path(MODEL_PATH)
    if not model_path.is_absolute():
        model_path = LOCAL_MODEL_FALLBACK
    cfg_file = model_path / "config.json"
    try:
        with open(cfg_file, encoding="utf-8") as fh:
            cfg = json.load(fh)
        # Use transformers_version from config; fall back to architectures[0]
        arch = cfg.get("architectures", ["unknown"])[0]
        tv = cfg.get("transformers_version", "")
        return f"{arch}@transformers-{tv}" if tv else arch
    except Exception:
        return "unknown"


# Cache so we don't re-read config.json on every request
_MODEL_VERSION: str = ""


def _model_version() -> str:
    global _MODEL_VERSION
    if not _MODEL_VERSION:
        _MODEL_VERSION = _get_model_version()
    return _MODEL_VERSION


def is_model_ready() -> tuple[bool, str]:
    """Check if model and tokenizer load successfully; returns (ready, version_or_error)."""
    try:
        _load_model_bundle()
        return True, _model_version()
    except Exception as exc:
        return False, str(exc)



# ---------------------------------------------------------------------------
# Core inference
# ---------------------------------------------------------------------------

def _run_inference(text: str) -> tuple[str, float, dict[str, float]]:
    """Run BERT forward pass; return (label, confidence, prob_dict)."""
    tokenizer, model = _load_model_bundle()

    # Resolve label map from model config (overrides hard-coded LABEL_MAP)
    if hasattr(model, "config") and getattr(model.config, "id2label", None):
        label_map: dict[int, str] = {
            int(k): str(v).lower() for k, v in model.config.id2label.items()
        }
    else:
        label_map = LABEL_MAP

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128,
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.softmax(outputs.logits, dim=-1)[0]
    label_id = int(torch.argmax(probs).item())
    confidence = float(probs[label_id].item())

    prob_dict: dict[str, float] = {
        label_map.get(i, f"class_{i}"): round(float(probs[i].item()), 4)
        for i in range(len(probs))
    }

    # Abstention: if no class clears the threshold, return "uncertain"
    if confidence < ABSTENTION_THRESHOLD:
        return "uncertain", round(confidence, 4), prob_dict

    return label_map.get(label_id, "uncertain"), round(confidence, 4), prob_dict


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict_sentiment(text: str) -> dict:
    """
    Analyze the sentiment of ``text`` and return the full prediction contract.

    See module docstring for the guaranteed response schema.
    """
    start_time = time.perf_counter()
    original_text = str(text).strip()
    processing_status = "ok"


    # --- input length validation ---
    if len(original_text) < MIN_INPUT_CHARS:
        return _error_response(
            original_text,
            processing_status="too_short",
            detail=f"Input must be at least {MIN_INPUT_CHARS} characters.",
        )

    working_text = original_text
    if len(working_text) > MAX_INPUT_CHARS:
        working_text = working_text[:MAX_INPUT_CHARS]
        processing_status = "truncated"

    # --- translation ---
    translated_text, language = translate_to_english(working_text)

    if language == "translation_failed":
        language_status = "translation_failed"
        # Feed original (possibly non-English) text to BERT rather than
        # silently pretending the translation succeeded.
        text_for_model = working_text
        processing_status = "translation_failed"
    elif language == "en":
        language_status = "english"
        text_for_model = working_text
    elif language == "unknown":
        language_status = "unknown"
        text_for_model = working_text
    else:
        language_status = "translated"
        text_for_model = translated_text

    # --- BERT inference ---
    try:
        sentiment, confidence, probabilities = _run_inference(text_for_model)
    except Exception as exc:  # pragma: no cover
        return _error_response(
            original_text,
            processing_status="model_error",
            detail=str(exc),
        )

    low_confidence = confidence < ABSTENTION_THRESHOLD

    return {
        "text": original_text,
        "original_text": original_text,
        "translated_text": translated_text if language_status == "translated" else working_text,
        "language": language,
        "language_status": language_status,
        "model_version": _model_version(),
        "sentiment": sentiment,
        "confidence": confidence,
        "low_confidence": low_confidence,
        "probabilities": probabilities,
        "processing_status": processing_status,
        "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
    }


# ---------------------------------------------------------------------------
# Error response helper
# ---------------------------------------------------------------------------

def _error_response(
    text: str,
    *,
    processing_status: str,
    detail: str = "",
) -> dict:
    return {
        "text": text,
        "original_text": text,
        "translated_text": text,
        "language": "unknown",
        "language_status": "unknown",
        "model_version": _model_version(),
        "sentiment": "uncertain",
        "confidence": 0.0,
        "low_confidence": True,
        "probabilities": {"negative": 0.0, "neutral": 0.0, "positive": 0.0},
        "processing_status": processing_status,
        "detail": detail,
        "latency_ms": 0.0,
    }

