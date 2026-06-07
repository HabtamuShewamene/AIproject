"""Generate sentiment and trend alerts from current vs baseline metrics."""

from __future__ import annotations


def generate_alerts(
    summary: dict | None = None,
    results: list | None = None,
    trends: list | None = None,
    *,
    previous_negative_pct: float | None = None,
) -> list[dict]:
    alerts: list[dict] = []
    summary = summary or {}
    results = results or []
    trends = trends or []

    negative = float(summary.get("negative") or 0)
    positive = float(summary.get("positive") or 0)

    if negative >= 35:
        alerts.append({
            "severity": "warning",
            "title": "Negative sentiment elevated",
            "message": f"Negative sentiment is {negative:.0f}% of the sample.",
            "icon": "warning",
        })

    if previous_negative_pct is not None and negative - previous_negative_pct >= 15:
        delta = negative - previous_negative_pct
        alerts.append({
            "severity": "critical",
            "title": "Negative sentiment spike",
            "message": f"Negative sentiment increased {delta:.0f}%.",
            "icon": "trending-down",
        })

    confidences = [float(r.get("confidence") or 0) for r in results]
    if confidences:
        avg_conf = sum(
            c if c <= 1 else c / 100 for c in confidences
        ) / len(confidences)
        if avg_conf < 0.55:
            alerts.append({
                "severity": "info",
                "title": "Confidence drop",
                "message": f"Average model confidence fell to {avg_conf * 100:.0f}%.",
                "icon": "shield",
            })

    for trend in trends[:3]:
        growth = float(trend.get("growth_percent") or 0)
        if growth >= 40:
            alerts.append({
                "severity": "warning",
                "title": "Topic trend exploding",
                "message": (
                    f'"{trend.get("topic")}" grew ~{growth:.0f}% in discussion share.'
                ),
                "icon": "zap",
            })

    if positive >= 70 and not alerts:
        alerts.append({
            "severity": "success",
            "title": "Strong positive outlook",
            "message": f"Positive sentiment holds at {positive:.0f}%.",
            "icon": "trending-up",
        })

    return alerts[:6]
