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
from app.schemas import TopicAnalysisRequest
from app.conversation_service import analyze_conversation_thread
import app.twitter_client as twitter_client


class ThreadAnalysisRequest(BaseModel):
    url: str = Field(
        ...,
        description="Public Twitter/X post URL (e.g., https://x.com/username/status/1234567890)",
        examples=["https://x.com/techcorp/status/1827364591029384756"],
    )
    max_replies: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum replies to harvest and evaluate",
    )
    include_nested: bool = Field(
        default=True,
        description="Whether to harvest nested sub-replies where accessible",
    )
    provider: str | None = Field(
        default=None,
        description="Optional provider override ('apify' or 'synthetic')",
    )


router = APIRouter(prefix="/api/v1/social", tags=["Social Media v1"])


@router.post(
    "/thread",
    summary="Full Twitter/X conversation thread intelligence",
    description="Harvests original post and public replies, evaluates sentiment per comment, calculates aggregate opinion, and yields grounded recommendations.",
)
def analyze_thread_v1(data: ThreadAnalysisRequest):
    if not twitter_client.is_valid_tweet_url(data.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must be a valid Twitter/X post link (e.g., https://x.com/user/status/1234567890).",
        )

    result = analyze_conversation_thread(
        url=data.url,
        max_replies=data.max_replies,
        include_nested=data.include_nested,
        provider_name=data.provider,
    )

    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Failed to retrieve conversation thread."),
        )

    return result["data"]


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


@router.post(
    "/topic",
    summary="Analyze sentiment distribution for a topic or hashtag",
    description="Searches social posts for a topic or keyword query and aggregates polarity distribution and intelligence.",
)
def analyze_topic_v1(data: TopicAnalysisRequest):
    query = data.query.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic query must not be blank.",
        )

    fetcher = getattr(twitter_client, "fetch_tweets", lambda _query: [])
    tweets = fetcher(query)

    if not tweets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No tweets found matching query '{query}'.",
        )

    results = []
    limit = data.limit or 20
    for tweet in tweets[:limit]:
        text = (tweet.get("text", "") or "").strip()
        if not text:
            continue

        sentiment_result = _analyze_tweet_sentiment(text)
        if not sentiment_result:
            continue

        metrics = {
            "likes": _get_number(tweet, "likeCount"),
            "retweets": _get_number(tweet, "retweetCount"),
            "replies": _get_number(tweet, "replyCount"),
            "quotes": _get_number(tweet, "quoteCount"),
        }

        item_intel = build_item_intelligence(
            text,
            sentiment_result["sentiment"],
            sentiment_result["confidence"],
            metrics=metrics,
        )

        results.append({
            "text": text,
            "url": tweet.get("url", ""),
            "author": _get_author_username(tweet),
            "likes": metrics["likes"],
            "retweets": metrics["retweets"],
            "replies": metrics["replies"],
            "quotes": metrics["quotes"],
            "views": _get_number(tweet, "viewCount"),
            "bookmarks": _get_number(tweet, "bookmarkCount"),
            "created_at": tweet.get("createdAt", ""),
            "media_type": tweet.get("mediaType", None),
            "sentiment": sentiment_result["sentiment"],
            "confidence": sentiment_result["confidence"],
            "intelligence": item_intel,
        })

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No valid tweets could be analyzed for the specified topic.",
        )

    summary = aggregate_results(results)
    intelligence = build_topic_intelligence(
        query,
        results,
        summary,
    )

    return {
        "query": query,
        "summary": summary,
        "total_tweets": len(results),
        "results": results[:limit],
        "intelligence": intelligence,
    }
