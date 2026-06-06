"""Estimate engagement virality from metrics and sentiment."""

from __future__ import annotations

_LEVELS = ["Low", "Medium", "High", "Very High"]


def _engagement_raw(metrics: dict | None) -> float:
    if not metrics:
        return 0.0
    likes = float(metrics.get("likes") or 0)
    retweets = float(metrics.get("retweets") or 0)
    replies = float(metrics.get("replies") or 0)
    quotes = float(metrics.get("quotes") or metrics.get("views") or 0)
    return likes + retweets * 2 + quotes * 3 + replies


def predict_virality(
    metrics: dict | None = None,
    sentiment: str = "neutral",
    confidence: float = 0.0,
) -> dict:
    raw = _engagement_raw(metrics)
    sentiment = (sentiment or "neutral").lower()

    # Heuristic tiers when metrics exist
    if raw >= 5000:
        level = "Very High"
        score = 0.95
    elif raw >= 1000:
        level = "High"
        score = 0.8
    elif raw >= 200:
        level = "Medium"
        score = 0.55
    elif raw > 0:
        level = "Low"
        score = 0.3
    else:
        # No metrics: infer from sentiment intensity
        conf = confidence if confidence <= 1 else confidence / 100
        if sentiment in {"positive", "negative"} and conf >= 0.8:
            level = "Medium"
            score = 0.5
        else:
            level = "Low"
            score = 0.25

    if sentiment in {"positive", "negative"} and level in {"Low", "Medium"}:
        score = min(score + 0.1, 1.0)

    explanation = (
        f"Engagement score {int(raw)} maps to {level} virality potential."
        if raw > 0
        else f"No engagement data — estimated {level} from sentiment strength."
    )

    return {
        "level": level,
        "score": round(score, 3),
        "engagement_score": int(raw),
        "explanation": explanation,
        "tiers": _LEVELS,
    }
