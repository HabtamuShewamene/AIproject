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
