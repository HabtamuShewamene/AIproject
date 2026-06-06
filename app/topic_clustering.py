"""Group tweets into thematic keyword clusters."""

from __future__ import annotations

import re
from collections import Counter

from app.intelligence_cache import cached_intelligence

_STOP = {
    "the", "and", "for", "with", "that", "this", "from", "your", "you", "are",
    "was", "have", "has", "not", "but", "can", "will", "just", "about", "into",
    "https", "http", "com", "www", "rt", "via",
}

_THEME_SEEDS: dict[str, list[str]] = {
    "GPT": ["gpt", "chatgpt", "model", "llm"],
    "API": ["api", "endpoint", "integration", "sdk"],
    "Pricing": ["price", "pricing", "cost", "subscription", "billing"],
    "Coding": ["code", "coding", "developer", "python", "javascript", "bug"],
    "Competition": ["google", "anthropic", "claude", "gemini", "competitor", "vs"],
}


def _tokenize(text: str) -> list[str]:
    return [
        t.lower()
        for t in re.findall(r"[a-z0-9][a-z0-9'-]{2,}", (text or "").lower())
        if t.lower() not in _STOP
    ]


@cached_intelligence("topic_clusters", ttl=300)
def cluster_topics(tweets: list[dict], query: str = "") -> dict:
    texts = [t.get("text", "") for t in tweets if t.get("text")]
    if not texts:
        return {"query": query, "clusters": [], "total_posts": 0}

    counter: Counter = Counter()
    for text in texts:
        counter.update(_tokenize(text))

    clusters = []
    assigned_tokens: set[str] = set()

    for theme, seeds in _THEME_SEEDS.items():
        volume = 0
        keywords: list[str] = []
        for seed in seeds:
            count = sum(counter.get(tok, 0) for tok in counter if seed in tok)
            volume += count
            if count:
                keywords.extend([tok for tok in counter if seed in tok][:3])
        if volume > 0:
            assigned_tokens.update(keywords)
            clusters.append({
                "name": theme,
                "volume": volume,
                "keywords": list(dict.fromkeys(keywords))[:5],
            })

    # Residual top keywords as "General" themes
    for word, count in counter.most_common(8):
        if word in assigned_tokens:
            continue
        if any(c["name"] == word.title() for c in clusters):
            continue
        clusters.append({"name": word.title(), "volume": count, "keywords": [word]})
        if len(clusters) >= 8:
            break

    clusters.sort(key=lambda c: c["volume"], reverse=True)

    return {
        "query": query,
        "clusters": clusters[:6],
        "total_posts": len(texts),
    }
