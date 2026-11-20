from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys

from app.intelligence_service import build_item_intelligence, build_topic_intelligence
from app.predictor import predict_sentiment
from app.sentiment_rules import (
    NEGATIVE_WORDS,
    POSITIVE_WORDS,
    contains_sarcasm,
    count_keywords,
    has_negation,
)
import app.twitter_client as twitter_client


def _twitter_module():
    return sys.modules.get("app.twitter_client", twitter_client)


# =========================================
# FASTAPI SETUP
# =========================================

app = FastAPI(
    title="AI Sentiment Analysis API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================
# REQUEST MODELS
# =========================================

class TextRequest(BaseModel):
    text: str


class TopicRequest(BaseModel):
    query: str


class TweetRequest(BaseModel):
    url: str


# =========================================
# ROOT ROUTE
# =========================================

@app.get("/")
def root():

    return {
        "message": "Sentiment API is running"
    }


# =========================================
# TEXT SENTIMENT ANALYSIS
# =========================================

@app.post("/predict")
def predict(data: TextRequest):

    result = enhanced_sentiment_analysis(data.text)

    return result


# =========================================
# SINGLE TWEET ANALYSIS
# =========================================

@app.post("/analyze-twitter")
def analyze_twitter(data: TweetRequest):

    tweet = getattr(_twitter_module(), "fetch_tweet", lambda _url: None)(data.url)

    if not tweet:

        return {
            "error": "Could not fetch tweet"
        }

    result = enhanced_sentiment_analysis(tweet.get("text", ""))

    metrics = {
        "likes": tweet.get("likes", 0),
        "retweets": tweet.get("retweets", 0),
        "replies": tweet.get("replies", 0),
        "quotes": tweet.get("quotes", 0),
    }

    return {
        "tweet_text": tweet.get("text", ""),
        "translated_text": result["translated_text"],
        "language": result["language"],
        "metrics": metrics,
        "sentiment": result["sentiment"],
        "confidence": result["confidence"],
    }


# =========================================
# ADVANCED AI SENTIMENT ENGINE
# =========================================

def enhanced_sentiment_analysis(text: str):

    prediction = predict_sentiment(text)

    sentiment = prediction.get(
        "sentiment",
        "neutral"
    )

    confidence = float(
        prediction.get(
            "confidence",
            0
        )
    )

    lower_text = text.lower()

    if contains_sarcasm(lower_text) and confidence < 0.90:

        if sentiment == "positive":

            sentiment = "negative"

            confidence = min(
                confidence + 0.15,
                1.0
            )

    if has_negation(lower_text):

        positive_hits = count_keywords(
            lower_text,
            POSITIVE_WORDS
        )

        negative_hits = count_keywords(
            lower_text,
            NEGATIVE_WORDS
        )

        if positive_hits > negative_hits:

            sentiment = "negative"

            confidence = min(
                confidence + 0.10,
                1.0
            )

    negative_score = count_keywords(
        lower_text,
        NEGATIVE_WORDS
    )

    if negative_score >= 2:

        sentiment = "negative"

        confidence = min(
            confidence + 0.12,
            1.0
        )

    positive_score = count_keywords(
        lower_text,
        POSITIVE_WORDS
    )

    if positive_score >= 2 and sentiment != "negative":

        sentiment = "positive"

        confidence = min(
            confidence + 0.10,
            1.0
        )

    confidence = round(confidence, 4)

    intelligence = build_item_intelligence(
        text,
        sentiment,
        confidence,
        metrics=None,
    )

    return {
        "text": text,
        "original_text": prediction.get("original_text", text),
        "translated_text": prediction.get("translated_text", text),
        "language": prediction.get("language", "en"),
        "sentiment": sentiment,
        "confidence": confidence,
        "probabilities": prediction.get("probabilities", {}),
        "intelligence": intelligence,
    }


# =========================================
# INTERNAL ANALYSIS WRAPPER
# =========================================

def _analyze_tweet_sentiment(text: str):

    try:

        return enhanced_sentiment_analysis(text)

    except Exception:

        return None


# =========================================
# HELPERS
# =========================================

def _get_author_username(tweet: dict) -> str:

    author = tweet.get("author", {})

    if isinstance(author, dict):

        username = author.get(
            "userName",
            ""
        ) or author.get(
            "username",
            ""
        )

        if username:
            return username

    return tweet.get(
        "authorUsername",
        ""
    )


def _get_number(tweet: dict, key: str) -> int:

    value = tweet.get(key, 0)

    return (
        value
        if isinstance(value, (int, float))
        and value is not None
        else 0
    )


# =========================================
# AGGREGATION
# =========================================

def aggregate_results(results):

    total = len(results)

    if total == 0:

        return {
            "total": 0,
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }

    positive = sum(
        1 for r in results
        if r["sentiment"] == "positive"
    )

    negative = sum(
        1 for r in results
        if r["sentiment"] == "negative"
    )

    neutral = sum(
        1 for r in results
        if r["sentiment"] == "neutral"
    )

    return {

        "total": total,

        "positive": round(
            (positive / total) * 100,
            2
        ),

        "negative": round(
            (negative / total) * 100,
            2
        ),

        "neutral": round(
            (neutral / total) * 100,
            2
        )
    }


# =========================================
# TOPIC ANALYSIS
# =========================================

@app.post("/analyze-topic")
def analyze_topic(data: TopicRequest):

    tweets = getattr(_twitter_module(), "fetch_tweets", lambda _query: [])(data.query)

    if not tweets:

        return {
            "error": "No tweets found"
        }

    results = []

    for tweet in tweets:

        text = (
            tweet.get("text", "")
            or ""
        ).strip()

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

            "url": tweet.get(
                "url",
                ""
            ),

            "author": _get_author_username(tweet),

            "likes": metrics["likes"],

            "retweets": metrics["retweets"],

            "replies": metrics["replies"],

            "quotes": metrics["quotes"],

            "views": _get_number(
                tweet,
                "viewCount"
            ),

            "bookmarks": _get_number(
                tweet,
                "bookmarkCount"
            ),

            "created_at": tweet.get(
                "createdAt",
                ""
            ),

            "media_type": tweet.get(
                "mediaType",
                None
            ),

            "hashtags": tweet.get(
                "hashtags",
                []
            ),

            "sentiment": sentiment_result[
                "sentiment"
            ],

            "confidence": sentiment_result[
                "confidence"
            ],

            "intelligence": item_intel,
        })

    summary = aggregate_results(results)
    intelligence = build_topic_intelligence(
        data.query,
        results,
        summary,
    )

    return {

        "query": data.query,

        "summary": summary,

        "total_tweets": len(results),

        "results": results[:10],

        "intelligence": intelligence,
    }
