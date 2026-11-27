"""Tests for Twitter/X conversation thread harvesting & intelligence (Blueprint Module 2, 4, 5, 6)."""

from fastapi.testclient import TestClient
import pytest

from app.conversation_service import analyze_conversation_thread
from app.main import app
from app.providers.apify_provider import ApifySocialProvider
from app.providers.base import ConversationDataset, PostData, PostMetrics, ProvenanceData, ReplyData
from app.providers.factory import get_social_provider
from app.providers.synthetic_provider import SyntheticSocialProvider


client = TestClient(app)


def test_synthetic_provider_post_and_replies():
    provider = SyntheticSocialProvider()
    assert provider.provider_name == "synthetic"

    url = "https://x.com/techcorp/status/1827364591029384756"
    post = provider.fetch_post(url)
    assert post is not None
    assert post.post_id == "1827364591029384756"
    assert post.metrics.likes > 0

    dataset = provider.fetch_conversation(url, max_replies=5, include_nested=True)
    assert dataset is not None
    assert len(dataset.replies) <= 5
    assert dataset.provenance.provider_name == "synthetic"
    assert dataset.provenance.replies_collected == len(dataset.replies)
    assert dataset.provenance.coverage_percentage > 0.0


def test_factory_fallback():
    # Synthetic provider explicitly requested
    prov = get_social_provider("synthetic")
    assert isinstance(prov, SyntheticSocialProvider)

    # Provider fallback returns a valid SocialDataProvider instance
    default_prov = get_social_provider()
    assert default_prov is not None
    assert hasattr(default_prov, "fetch_conversation")


def test_analyze_conversation_thread_pipeline():
    url = "https://x.com/techcorp/status/1827364591029384756"
    report = analyze_conversation_thread(url=url, max_replies=10, provider_name="synthetic")

    assert report["status"] == "ok"
    data = report["data"]

    # Verify Root Post
    assert "root_post" in data
    assert data["root_post"]["post_id"] == "1827364591029384756"
    assert data["root_post"]["sentiment"] in ["positive", "neutral", "negative"]

    # Verify Public Opinion Distribution
    opinion = data["public_opinion"]
    assert "distribution" in opinion
    dist = opinion["distribution"]
    assert dist["positive_percentage"] + dist["negative_percentage"] + dist["neutral_percentage"] == pytest.approx(100.0, 0.1)
    assert "engagement_weighted_sentiment_score" in opinion

    # Verify Topic Intelligence & Complaints
    topic_intel = data["topic_intelligence"]
    assert "top_complaints" in topic_intel
    assert "top_praise" in topic_intel

    # Verify Grounded Recommendations
    recs = data["executive_recommendations"]
    assert isinstance(recs, list)
    assert len(recs) > 0
    for r in recs:
        assert "priority" in r
        assert "recommended_action" in r
        assert "evidence_quote" in r

    # Verify Provenance Disclosure
    prov = data["provenance"]
    assert prov["source_url"] == url
    assert prov["provider_name"] == "synthetic"
    assert prov["replies_collected"] > 0
    assert prov["coverage_percentage"] > 0.0


def test_api_v1_social_thread_endpoint_success():
    payload = {
        "url": "https://x.com/techcorp/status/1827364591029384756",
        "max_replies": 8,
        "include_nested": True,
        "provider": "synthetic",
    }
    response = client.post("/api/v1/social/thread", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "root_post" in data
    assert "public_opinion" in data
    assert "executive_recommendations" in data
    assert "provenance" in data
    assert len(data["replies"]) <= 8


def test_api_v1_social_thread_endpoint_invalid_url():
    payload = {
        "url": "https://google.com/not-a-tweet",
        "max_replies": 10,
    }
    response = client.post("/api/v1/social/thread", json=payload)
    assert response.status_code == 400
    assert "valid Twitter/X" in response.json()["detail"]


def test_apify_provider_normalization():
    prov = ApifySocialProvider(token="test_mock_token")
    assert prov.provider_name == "apify"

    # Test normalization helper directly
    raw_tweet = {
        "text": "Excited to introduce our new product feature!",
        "author": {
            "userName": "founder_jane",
            "name": "Jane Doe",
            "isBlueVerified": True,
        },
        "likeCount": 150,
        "retweetCount": 25,
        "replyCount": 12,
        "quoteCount": 4,
        "viewCount": 5000,
        "createdAt": "2026-11-27T12:00:00Z",
        "lang": "en",
    }
    post = prov._normalize_post(raw_tweet, "https://x.com/jane/status/999", "999")
    assert post.post_id == "999"
    assert post.author_username == "founder_jane"
    assert post.author_verified is True
    assert post.metrics.likes == 150
    assert post.metrics.views == 5000
