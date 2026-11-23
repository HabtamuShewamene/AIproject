"""Versioned social media collection router under /api/v1 (Phase 4)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.main import (
    _analyze_tweet_sentiment,
    _get_author_username,
    _get_number,
    aggregate_results,
    enhanced_sentiment_analysis,
    TopicRequest,
    TweetRequest,
)
from app.intelligence_service import build_item_intelligence, build_topic_intelligence
import app.twitter_client as twitter_client

router = APIRouter(prefix="/api/v1/social", tags=["Social Media v1"])


@router.post(
    "/tweet",
    summary="Analyze single Twitter/X post",
    description="Validates tweet URL, safely extracts metrics through Twitter client adapter, and evaluates sentiment.",
)
def analyze_tweet_v1(data: TweetRequest):
    if not twitter_client.is_valid_tweet_url(data.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must be a valid Twitter/X post link (e.g., https://x.com/user/status/1234567890).",
        )

    tweet = twitter_client.fetch_tweet(data.url)
    if not tweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet could not be retrieved from provider. It may be deleted, private, or credentials may be missing.",
        )

    result = enhanced_sentiment_analysis(tweet.get("text", ""))

    metrics = {
        "likes": tweet.get("likes", 0),
        "retweets": tweet.get("retweets", 0),
        "replies": tweet.get("replies", 0),
        "quotes": tweet.get("quotes", 0),
    }

    return {
        "tweet_text": tweet.get("text", ""),
        "translated_text": result.get("translated_text", ""),
        "language": result.get("language", "en"),
        "metrics": metrics,
        "sentiment": result.get("sentiment", "neutral"),
        "confidence": result.get("confidence", 0.0),
        "probabilities": result.get("probabilities", {}),
        "intelligence": result.get("intelligence", {}),
    }
