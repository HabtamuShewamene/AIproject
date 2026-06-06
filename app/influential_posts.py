"""Rank tweets by engagement impact."""

from __future__ import annotations


def engagement_score(tweet: dict) -> int:
    likes = int(tweet.get("likes") or 0)
    retweets = int(tweet.get("retweets") or 0)
    quotes = int(tweet.get("quotes") or 0)
    replies = int(tweet.get("replies") or 0)
    return likes + retweets * 2 + quotes * 3 + replies


def rank_influential_posts(tweets: list[dict], limit: int = 10) -> list[dict]:
    ranked = []
    for tweet in tweets:
        score = engagement_score(tweet)
        ranked.append({
            **tweet,
            "engagement_score": score,
        })

    ranked.sort(key=lambda item: item["engagement_score"], reverse=True)
    return ranked[:limit]
