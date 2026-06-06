"""Detect emerging discussion themes from topic results."""

from __future__ import annotations

import re
from collections import Counter

from app.intelligence_cache import cached_intelligence


def _tokens(text: str) -> list[str]:
    stop = {"the", "and", "for", "with", "that", "this", "from", "your", "rt"}
    return [
        t
        for t in re.findall(r"[a-z][a-z0-9'-]{2,}", (text or "").lower())
        if t not in stop
    ]


@cached_intelligence("trends", ttl=300)
def detect_trends(tweets: list[dict], query: str = "") -> dict:
    if not tweets:
        return {"query": query, "trending": []}

    counter: Counter = Counter()
    sentiment_by_token: dict[str, list[str]] = {}

    for tweet in tweets:
        text = tweet.get("text", "")
        sentiment = (tweet.get("sentiment") or "neutral").lower()
        for token in _tokens(text):
            counter[token] += 1
            sentiment_by_token.setdefault(token, []).append(sentiment)

    total = max(len(tweets), 1)
    trending = []

    for token, volume in counter.most_common(10):
        share = round((volume / total) * 100, 1)
        sentiments = sentiment_by_token.get(token, [])
        neg_ratio = sentiments.count("negative") / max(len(sentiments), 1)
        growth = min(99.0, round(share * 1.2 + neg_ratio * 15, 1))

        trending.append({
            "topic": token.title(),
            "volume": volume,
            "share_percent": share,
            "growth_percent": growth,
        })

    return {"query": query, "trending": trending[:8]}
