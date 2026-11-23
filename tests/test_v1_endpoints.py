"""Integration test suite for Phase 4 versioned API endpoints (/api/v1/*)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_v1_predict_endpoint_success():
    response = client.post(
        "/api/v1/predict",
        json={"text": "The platform performance is outstanding and blazingly fast."},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "positive"
    assert data["confidence"] > 0.80
    assert "model_version" in data
    assert "latency_ms" in data
    assert "X-Request-ID" in response.headers
    assert "X-Response-Time-Ms" in response.headers


def test_v1_predict_batch_endpoint_success():
    batch_texts = [
        "I absolutely adore this application!",
        "The server is having recurring outages and errors.",
        "The flight departure is scheduled for 10:15 AM tomorrow.",
    ]

    response = client.post(
        "/api/v1/predict/batch",
        json={"texts": batch_texts},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["predictions"]) == 3
    assert "summary" in data
    assert "batch_latency_ms" in data
    assert data["batch_latency_ms"] > 0

    # Verify individual item sentiments
    sentiments = [p["sentiment"] for p in data["predictions"]]
    assert "positive" in sentiments
    assert "negative" in sentiments
    assert "neutral" in sentiments


def test_v1_predict_batch_empty_list_returns_422():
    response = client.post(
        "/api/v1/predict/batch",
        json={"texts": []},
    )

    assert response.status_code == 422


def test_v1_predict_batch_over_limit_returns_422():
    over_limit = ["Sample text"] * 51

    response = client.post(
        "/api/v1/predict/batch",
        json={"texts": over_limit},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# /api/v1/social/tweet Integration Tests
# ---------------------------------------------------------------------------

def test_v1_social_tweet_invalid_url_returns_400():
    response = client.post(
        "/api/v1/social/tweet",
        json={"url": "https://invalid-site.com/not-a-tweet"},
    )

    assert response.status_code == 400
    assert "Twitter/X post link" in response.json()["detail"]


def test_v1_social_tweet_not_found_returns_404(monkeypatch):
    import app.twitter_client as twitter_client

    monkeypatch.setattr(twitter_client, "fetch_tweet", lambda _url: None)

    response = client.post(
        "/api/v1/social/tweet",
        json={"url": "https://x.com/user/status/1234567890"},
    )

    assert response.status_code == 404
    assert "could not be retrieved" in response.json()["detail"]


def test_v1_social_tweet_success(monkeypatch):
    import app.twitter_client as twitter_client

    mock_tweet = {
        "text": "This product launch exceeded all our expectations!",
        "likes": 42,
        "retweets": 15,
        "replies": 3,
        "quotes": 2,
    }
    monkeypatch.setattr(twitter_client, "fetch_tweet", lambda _url: mock_tweet)

    response = client.post(
        "/api/v1/social/tweet",
        json={"url": "https://x.com/tech_user/status/9876543210"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tweet_text"] == mock_tweet["text"]
    assert data["metrics"]["likes"] == 42
    assert data["sentiment"] == "positive"
    assert data["probabilities"] is not None
    assert "X-Request-ID" in response.headers


# ---------------------------------------------------------------------------
# Global Error Handling & Request Tracing Tests
# ---------------------------------------------------------------------------

def test_custom_request_id_header_is_propagated():
    custom_id = "req-custom-trace-uuid-12345"
    response = client.post(
        "/api/v1/predict",
        json={"text": "Everything is running smoothly."},
        headers={"X-Request-ID": custom_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id


def test_global_404_error_handler_payload():
    response = client.get("/api/v1/nonexistent-route-for-testing")

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "HTTPException"
    assert data["status_code"] == 404
    assert "detail" in data
    assert data["request_id"] == response.headers.get("X-Request-ID")


def test_global_422_validation_error_handler_payload():
    response = client.post(
        "/api/v1/predict",
        json={},
    )

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ValidationError"
    assert data["status_code"] == 422
    assert isinstance(data["detail"], list)
    assert data["request_id"] == response.headers.get("X-Request-ID")


# ---------------------------------------------------------------------------
# /api/v1/social/topic Integration Tests
# ---------------------------------------------------------------------------

def test_v1_social_topic_short_query_returns_422():
    response = client.post(
        "/api/v1/social/topic",
        json={"query": "a"},
    )

    assert response.status_code == 422


def test_v1_social_topic_not_found_returns_404(monkeypatch):
    import app.twitter_client as twitter_client

    monkeypatch.setattr(twitter_client, "fetch_tweets", lambda _q: [])

    response = client.post(
        "/api/v1/social/topic",
        json={"query": "nonexistenttopic12345"},
    )

    assert response.status_code == 404
    assert "No tweets found matching query" in response.json()["detail"]


def test_v1_social_topic_success(monkeypatch):
    import app.twitter_client as twitter_client

    mock_tweets = [
        {
            "text": "The new release is exceptionally fast and clean!",
            "likeCount": 100,
            "retweetCount": 20,
            "replyCount": 5,
            "quoteCount": 2,
            "viewCount": 5000,
            "bookmarkCount": 35,
            "createdAt": "2026-11-23T12:00:00Z",
            "url": "https://x.com/tech/status/1001",
            "author": {"username": "techlead"},
        },
        {
            "text": "Terrible customer experience and completely unresponsive support.",
            "likeCount": 12,
            "retweetCount": 3,
            "replyCount": 1,
            "quoteCount": 0,
            "viewCount": 600,
            "bookmarkCount": 1,
            "createdAt": "2026-11-23T12:05:00Z",
            "url": "https://x.com/user/status/1002",
            "author": {"username": "frustrated_user"},
        },
    ]

    monkeypatch.setattr(twitter_client, "fetch_tweets", lambda _q: mock_tweets)

    response = client.post(
        "/api/v1/social/topic",
        json={"query": "release performance", "limit": 10},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "release performance"
    assert data["total_tweets"] == 2
    assert len(data["results"]) == 2
    assert "summary" in data
    assert "intelligence" in data
    assert "X-Request-ID" in response.headers


# ---------------------------------------------------------------------------
# OpenAPI / Swagger Documentation Schema Tests
# ---------------------------------------------------------------------------

def test_openapi_schema_contains_versioned_routes_and_tags():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/predict" in schema["paths"]
    assert "/api/v1/predict/batch" in schema["paths"]
    assert "/api/v1/social/tweet" in schema["paths"]
    assert "/api/v1/social/topic" in schema["paths"]
    assert "/health/live" in schema["paths"]
    assert "/health/ready" in schema["paths"]
    assert "tags" in schema
    tag_names = [t["name"] for t in schema["tags"]]
    assert "Predictions v1" in tag_names
    assert "Social Media v1" in tag_names
    assert "Operational Health" in tag_names

