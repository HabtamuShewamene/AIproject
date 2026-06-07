"""Orchestrate Phase 3 intelligence for single-item and topic analyses."""

from __future__ import annotations

from app.alerts_engine import generate_alerts
from app.emotion_detector import detect_emotion
from app.entity_extractor import extract_entities
from app.explanation_engine import explain_sentiment
from app.influential_posts import rank_influential_posts
from app.report_generator import generate_executive_summary
from app.sentiment_rules import contains_sarcasm
from app.topic_clustering import cluster_topics
from app.trend_detector import detect_trends
from app.virality_engine import predict_virality


def build_item_intelligence(
    text: str,
    sentiment: str,
    confidence: float,
    metrics: dict | None = None,
) -> dict:
    sarcasm = contains_sarcasm((text or "").lower())
    return {
        "explanation": explain_sentiment(
            text, sentiment, confidence, sarcasm_detected=sarcasm
        ),
        "emotion": detect_emotion(text, sentiment),
        "virality": predict_virality(metrics, sentiment, confidence),
        "entities": extract_entities(text),
    }


def build_topic_intelligence(
    query: str,
    results: list[dict],
    summary: dict,
) -> dict:
    clusters_payload = cluster_topics(results, query)
    trends_payload = detect_trends(results, query)
    influential = rank_influential_posts(results, limit=10)
    alerts = generate_alerts(
        summary=summary,
        results=results,
        trends=trends_payload.get("trending", []),
    )
    executive = generate_executive_summary(
        query,
        summary,
        clusters=clusters_payload.get("clusters"),
        trends=trends_payload.get("trending"),
    )

    return {
        "clusters": clusters_payload,
        "trends": trends_payload,
        "influential_posts": influential,
        "alerts": alerts,
        "executive_summary": executive,
    }
