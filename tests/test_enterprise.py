"""Test suite for Phase 7 Enterprise Intelligence, Triage, and Copilot endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.triage_service import extract_aspects, evaluate_business_triage
from app.copilot_service import generate_copilot_assistance

client = TestClient(app)


def test_aspect_extraction_detects_support_and_billing():
    text = "The customer support agent was amazing, but billing charged me twice!"
    aspects = extract_aspects(text, base_sentiment="neutral", confidence=0.75)
    aspect_ids = [a["aspect_id"] for a in aspects]
    assert "customer_support" in aspect_ids
    assert "billing_pricing" in aspect_ids


def test_business_triage_detects_critical_churn():
    text = "This is a rip off and I am canceling my subscription immediately!"
    triage = evaluate_business_triage(text, sentiment="negative", confidence=0.92)
    assert triage["urgency"] == "Critical"
    assert triage["churn_risk"] == "High"
    assert "retention" in triage["recommended_action"].lower()


def test_business_triage_detects_bug_report():
    text = "The application crashed when I clicked export button."
    triage = evaluate_business_triage(text, sentiment="negative", confidence=0.88)
    assert triage["intent"] == "Product Defect / Bug Report"
    assert triage["urgency"] in {"Medium", "Attention"}


def test_copilot_service_generates_drafts_and_drivers():
    text = "Terrible delay with shipping and courier lost my package!"
    aspects = extract_aspects(text, "negative", 0.90)
    triage = evaluate_business_triage(text, "negative", 0.90)
    copilot = generate_copilot_assistance(text, "negative", 0.90, triage, aspects)

    assert "key_drivers" in copilot
    assert len(copilot["key_drivers"]) >= 2
    assert "drafts" in copilot
    assert "empathetic" in copilot["drafts"]
    assert "Dear customer" in copilot["drafts"]["empathetic"]


def test_copilot_chat_endpoint_returns_reply():
    response = client.post(
        "/api/v1/enterprise/copilot/chat",
        json={
            "message": "Draft a polite email to apologize to this customer",
            "analyzed_text": "I waited 2 hours on hold for support and nobody answered.",
            "sentiment": "negative",
            "confidence": 0.94,
            "triage": {"urgency": "High", "intent": "Customer Support Failure", "recommended_action": "Escalate"},
            "aspects": [{"label": "Customer Support", "polarity": "negative", "score": -0.9}],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "Dear Valued Customer" in data["reply"]


def test_benchmark_endpoint_evaluates_differential():
    response = client.post(
        "/api/v1/enterprise/benchmark",
        json={
            "text_a": "The new interface is extraordinarily smooth, fast, and delightful!",
            "text_b": "The software is sluggish, keeps freezing, and crashes repeatedly.",
            "label_a": "Platform v2.0",
            "label_b": "Legacy Platform",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["winner"] == "Platform v2.0"
    assert data["delta"] > 0
    assert "leads" in data["verdict"]
