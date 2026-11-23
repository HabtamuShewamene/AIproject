"""Typed Pydantic schemas for API requests, responses, and errors (Phase 4)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# =========================================
# PREDICTION SCHEMAS
# =========================================

class SentimentProbabilities(BaseModel):
    negative: float = Field(..., ge=0.0, le=1.0, description="Probability of negative sentiment")
    neutral: float = Field(..., ge=0.0, le=1.0, description="Probability of neutral sentiment")
    positive: float = Field(..., ge=0.0, le=1.0, description="Probability of positive sentiment")


class SentimentPredictionResponse(BaseModel):
    text: str = Field(..., description="Processed input text")
    original_text: str = Field(..., description="Original input text")
    translated_text: str = Field(..., description="English text analyzed by the neural model")
    language: str = Field(..., description="Detected language code")
    language_status: str = Field(..., description="Status of language detection and translation")
    model_version: str = Field(..., description="Active neural model version identifier")
    sentiment: str = Field(..., description="Predicted sentiment polarity: positive, neutral, negative, uncertain")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    low_confidence: bool = Field(..., description="Flag indicating if confidence fell below the abstention threshold")
    probabilities: Dict[str, float] = Field(..., description="Raw probability distribution across classes")
    processing_status: str = Field(..., description="Execution status: ok, too_short, truncated, translation_failed")
    latency_ms: float = Field(..., ge=0.0, description="Inference latency in milliseconds")
    intelligence: Optional[Dict[str, Any]] = Field(default=None, description="Enriched intelligence signals and explanations")
    evidence: Optional[Dict[str, Any]] = Field(default=None, description="Phase 5 structured evidence: sarcasm signals, keyword polarity, confidence reasoning")
    aria: Optional[Dict[str, Any]] = Field(default=None, description="Phase 6 ARIA semantic metadata for frontend assistive technology")


# =========================================
# BATCH PREDICTION SCHEMAS
# =========================================

class BatchPredictionRequest(BaseModel):
    texts: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of text strings to analyze in a single batch (max 50)",
        examples=[["This is fantastic!", "Service was unacceptably slow.", "The flight departs at 9 AM."]],
    )


class BatchPredictionResponse(BaseModel):
    total: int = Field(..., description="Total number of items processed in the batch")
    predictions: List[SentimentPredictionResponse] = Field(..., description="List of individual prediction responses")
    summary: Dict[str, float] = Field(..., description="Aggregated percentage distribution across sentiments")
    batch_latency_ms: float = Field(..., description="Total batch processing latency in milliseconds")


# =========================================
# SOCIAL INTELLIGENCE SCHEMAS
# =========================================

class TopicAnalysisRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Search topic query or hashtag (e.g. 'artificial intelligence' or '#MachineLearning')",
        examples=["artificial intelligence"],
    )
    limit: Optional[int] = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of tweets to retrieve and evaluate",
    )


# =========================================
# ERROR RESPONSE SCHEMA
# =========================================

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error classification name")
    detail: str = Field(..., description="Human-readable explanation of the error")
    request_id: Optional[str] = Field(default=None, description="Unique correlation ID of the failed request")
    status_code: int = Field(..., description="HTTP status code")
