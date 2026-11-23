"""Integration & unit tests for Phase 6 accessibility layer."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.accessibility import (
    build_aria_metadata,
    get_a11y_report,
    WCAG_CHECKS,
)

client = TestClient(app)


# ---------------------------------------------------------------------------
# WCAG Compliance Report Tests
# ---------------------------------------------------------------------------

def test_a11y_report_all_criteria_pass():
    report = get_a11y_report()
    assert report["failed"] == 0
    assert report["overall_status"] == "compliant"
    assert report["compliance_rate"] == 100.0


def test_a11y_report_covers_required_criteria():
    report = get_a11y_report()
    criterion_ids = [c["criterion"] for c in report["criteria"]]
    # Must cover AA-level essentials
    for required in ["1.1.1", "1.4.3", "2.1.1", "2.4.1", "4.1.2", "4.1.3"]:
        assert required in criterion_ids, f"Missing WCAG criterion {required}"


def test_a11y_report_structure():
    report = get_a11y_report()
    assert "standard" in report
    assert report["standard"] == "WCAG 2.1 AA"
    assert "total_criteria" in report
    assert report["total_criteria"] == len(WCAG_CHECKS)


# ---------------------------------------------------------------------------
# ARIA Metadata Builder Tests
# ---------------------------------------------------------------------------

def test_aria_metadata_high_confidence():
    meta = build_aria_metadata("positive", 0.95, False, "en")
    assert "Positive" in meta["sentiment_label"]
    assert "high" in meta["confidence_label"].lower() or "High" in meta["confidence_label"]
    assert meta["content_language"] == "en"
    assert meta["focus_target"] == "#results-section"


def test_aria_metadata_abstained():
    meta = build_aria_metadata("uncertain", 0.35, True, "en")
    assert "Uncertain" in meta["sentiment_label"]
    assert "abstain" in meta["confidence_label"].lower()


def test_aria_metadata_negative_moderate():
    meta = build_aria_metadata("negative", 0.75, False, "fr")
    assert "Negative" in meta["sentiment_label"]
    assert meta["content_language"] == "fr"
    assert meta["live_region_policy"] == "polite"


def test_aria_metadata_low_confidence_tier():
    meta = build_aria_metadata("neutral", 0.52, False, "en")
    assert "low" in meta["confidence_label"].lower() or "moderate" in meta["confidence_label"].lower()


# ---------------------------------------------------------------------------
# /api/v1/accessibility/report Endpoint Tests
# ---------------------------------------------------------------------------

def test_accessibility_report_endpoint_returns_200():
    response = client.get("/api/v1/accessibility/report")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_status"] == "compliant"
    assert data["failed"] == 0
    assert isinstance(data["criteria"], list)
    assert len(data["criteria"]) > 0


def test_accessibility_report_has_request_id_header():
    response = client.get("/api/v1/accessibility/report")
    assert "X-Request-ID" in response.headers
    assert "X-Response-Time-Ms" in response.headers


def test_accessibility_aria_labels_endpoint_returns_200():
    response = client.get("/api/v1/accessibility/aria-labels")
    assert response.status_code == 200
    data = response.json()
    assert "aria_reference" in data
    assert isinstance(data["aria_reference"], list)
    assert len(data["aria_reference"]) > 0


def test_accessibility_aria_labels_all_sentiments_covered():
    response = client.get("/api/v1/accessibility/aria-labels")
    data = response.json()
    sentiments_in_response = {item["sentiment"] for item in data["aria_reference"]}
    for s in ["positive", "negative", "neutral", "uncertain"]:
        assert s in sentiments_in_response


# ---------------------------------------------------------------------------
# Prediction Response Includes ARIA Metadata (Phase 6 Integration)
# ---------------------------------------------------------------------------

def test_predict_response_includes_aria_field():
    response = client.post(
        "/api/v1/predict",
        json={"text": "This is an absolutely brilliant and outstanding result!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "aria" in data
    assert "sentiment_label" in data["aria"]
    assert "confidence_label" in data["aria"]
    assert "focus_target" in data["aria"]
    assert data["aria"]["focus_target"] == "#results-section"


def test_predict_response_aria_language_matches_detected_language():
    response = client.post(
        "/api/v1/predict",
        json={"text": "Great product, very happy with it."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["aria"]["content_language"] == data["language"]


def test_predict_explain_includes_evidence_and_aria():
    response = client.post(
        "/api/v1/predict/explain",
        json={"text": "The service was shockingly bad and completely unacceptable."},
    )
    assert response.status_code == 200
    data = response.json()
    assert "evidence" in data
    assert "intelligence" in data
