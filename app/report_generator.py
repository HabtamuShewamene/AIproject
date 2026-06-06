"""Generate executive summaries from aggregated topic intelligence."""

from __future__ import annotations

from app.intelligence_cache import cached_intelligence


@cached_intelligence("executive_summary", ttl=180)
def generate_executive_summary(
    query: str,
    summary: dict,
    clusters: list | None = None,
    trends: list | None = None,
) -> dict:
    positive = float(summary.get("positive") or 0)
    negative = float(summary.get("negative") or 0)
    neutral = float(summary.get("neutral") or 0)
    total = int(summary.get("total") or 0)

    if positive >= negative and positive >= neutral:
        tone = "strongly positive" if positive >= 60 else "moderately positive"
    elif negative >= positive and negative >= neutral:
        tone = "negative" if negative >= 40 else "mixed with negative lean"
    else:
        tone = "neutral to mixed"

    cluster_names = [c.get("name") for c in (clusters or [])[:3] if c.get("name")]
    trend_names = [t.get("topic") for t in (trends or [])[:3] if t.get("topic")]

    focus = ", ".join(cluster_names) if cluster_names else "general discussion"
    rising = ", ".join(trend_names) if trend_names else "no dominant rising terms"

    paragraph = (
        f'Public sentiment toward "{query}" remains {tone} '
        f"({positive:.0f}% positive, {negative:.0f}% negative, {neutral:.0f}% neutral "
        f"across {total} posts). "
        f"Discussion is centered on {focus}. "
    )

    if negative >= 25:
        paragraph += (
            f"Negative mentions ({negative:.0f}%) often relate to pricing, reliability, or criticism themes. "
        )

    if rising != "no dominant rising terms":
        paragraph += f"Emerging topics include {rising}."

    bullets = [
        f"Sample size: {total} posts analyzed.",
        f"Dominant tone: {tone}.",
        f"Top themes: {focus}.",
    ]

    return {
        "query": query,
        "summary_text": paragraph.strip(),
        "bullets": bullets,
    }
