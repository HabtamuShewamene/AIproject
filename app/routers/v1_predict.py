"""Versioned prediction router under /api/v1 (Phase 4 & 5)."""

from __future__ import annotations

import time
from collections import Counter
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.config import MAX_BATCH_SIZE
from app.explainability import build_evidence_bundle
from app.main import enhanced_sentiment_analysis, TextRequest
from app.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    SentimentPredictionResponse,
)

router = APIRouter(prefix="/api/v1", tags=["Predictions v1"])


@router.post(
    "/predict",
    response_model=SentimentPredictionResponse,
    summary="Predict single text sentiment",
    description="Analyzes single text input and returns calibrated polarity, probabilities, and intelligence context.",
)
def predict_v1(data: TextRequest):
    return enhanced_sentiment_analysis(data.text)


@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Batch sentiment prediction",
    description=f"Processes an array of texts (max {MAX_BATCH_SIZE}) and returns item predictions with aggregated distribution.",
)
def predict_batch_v1(data: BatchPredictionRequest):
    if len(data.texts) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch size {len(data.texts)} exceeds maximum allowed limit of {MAX_BATCH_SIZE}.",
        )

    start_time = time.perf_counter()
    predictions = [enhanced_sentiment_analysis(text) for text in data.texts]
    batch_latency = round((time.perf_counter() - start_time) * 1000, 2)

    total = len(predictions)
    counts = Counter(p["sentiment"] for p in predictions)
    summary = {
        sentiment: round((counts[sentiment] / total) * 100, 2)
        for sentiment in ["positive", "neutral", "negative", "uncertain"]
        if counts[sentiment] > 0
    }

    return {
        "total": total,
        "predictions": predictions,
        "summary": summary,
        "batch_latency_ms": batch_latency,
    }


class EvidenceRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=2000, description="Text to analyze and explain")


@router.post(
    "/predict/explain",
    summary="Predict sentiment with full evidence explanation",
    description=(
        "Phase 5 endpoint: runs sentiment inference and returns a rich evidence bundle — "
        "sarcasm signals, keyword polarity, and confidence reasoning — alongside the standard prediction."
    ),
)
def predict_with_explanation(data: EvidenceRequest):
    result = enhanced_sentiment_analysis(data.text)
    # evidence is already embedded by enhanced_sentiment_analysis (Phase 5 wiring)
    # but re-expose it at the top level for clarity
    return {
        "text": data.text,
        "sentiment": result.get("sentiment"),
        "confidence": result.get("confidence"),
        "low_confidence": result.get("low_confidence"),
        "probabilities": result.get("probabilities", {}),
        "model_version": result.get("model_version"),
        "evidence": result.get("evidence", {}),
        "intelligence": result.get("intelligence", {}),
    }
