from __future__ import annotations

import re
from types import SimpleNamespace

from app.config import APIFY_TOKEN, TWITTER_COOKIE

try:
    from apify_client import ApifyClient
except ImportError:  # pragma: no cover - optional runtime dependency
    ApifyClient = None


# Use the actor slug so the code is easier to verify against Apify Console.
ACTOR_ID = "automation-lab/twitter-scraper"


class _NoopClient:
    """Fallback client so the backend can start without Apify credentials."""

    def get_tweet(self, **_kwargs):
        return SimpleNamespace(data=None)

    def actor(self, *_args, **_kwargs):
        return self

    def dataset(self, *_args, **_kwargs):
        return self

    def call(self, **_kwargs):
        return {"defaultDatasetId": None}

    def list_items(self):
        return SimpleNamespace(items=[])


class _ClientAdapter:
    """Normalise the client interface expected by the app and tests."""

    def __init__(self, client_obj):
        self._client = client_obj

    def get_tweet(self, **_kwargs):
        return SimpleNamespace(data=None)

    def actor(self, *args, **kwargs):
        return self._client.actor(*args, **kwargs)

    def dataset(self, *args, **kwargs):
        return self._client.dataset(*args, **kwargs)


_raw_client = ApifyClient(APIFY_TOKEN) if ApifyClient and APIFY_TOKEN else _NoopClient()
client = _ClientAdapter(_raw_client)


def extract_tweet_id(url: str) -> str:
    match = re.search(r"/status/(\d+)", url or "")
    return match.group(1) if match else ""


def _safe_int(value) -> int:
    return int(value) if isinstance(value, (int, float)) else 0


def _normalize_public_metrics(item: dict) -> dict:
    return {
        "like_count": _safe_int(
            item.get("likeCount")
            or item.get("like_count")
            or item.get("likes")
        ),
        "retweet_count": _safe_int(
            item.get("retweetCount")
            or item.get("retweet_count")
            or item.get("retweets")
        ),
        "reply_count": _safe_int(
            item.get("replyCount")
            or item.get("reply_count")
            or item.get("replies")
        ),
        "quote_count": _safe_int(
            item.get("quoteCount")
            or item.get("quote_count")
            or item.get("quotes")
        ),
    }


def _normalize_tweet_item(item: dict) -> dict:
    metrics = _normalize_public_metrics(item)
    language = (
        item.get("lang")
        or item.get("language")
        or item.get("tweetLanguage")
        or "unknown"
    )

    return {
        "text": item.get("text", "") or "",
        "language": language,
        "likes": metrics["like_count"],
        "retweets": metrics["retweet_count"],
        "replies": metrics["reply_count"],
        "quotes": metrics["quote_count"],
    }


def _run_actor(run_input: dict):
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    dataset_id = run.get("defaultDatasetId") if isinstance(run, dict) else None
    if not dataset_id:
        return []
    items = client.dataset(dataset_id).list_items().items
    return items or []


def fetch_tweet(url: str):
    tweet_id = extract_tweet_id(url)
    if not tweet_id:
        return None

    try:
        items = _run_actor(
            {
                "scrapeMode": "x-post-scraper",
                "scrapingMode": "Tweets by URL/ID",
                "mode": "tweets",
                "tweetURLs": [url],
                "tweetUrls": [url],
                "tweet_url": url,
                "twitterCookie": TWITTER_COOKIE,
                "loginCookies": TWITTER_COOKIE,
            }
        )
    except Exception:
        return None

    if not items:
        return None

    first_item = items[0] if isinstance(items, list) else items
    return _normalize_tweet_item(first_item)


def fetch_tweets(query: str):
    if not TWITTER_COOKIE or not APIFY_TOKEN:
        return []

    try:
        items = _run_actor(
            {
                "scrapeMode": "x-search-scraper",
                "scrapingMode": "Search",
                "mode": "search",
                "searchQueries": [query],
                "searchTerms": [query],
                "query": query,
                "sort": "Latest",
                "maxResults": 20,
                "twitterCookie": TWITTER_COOKIE,
                "loginCookies": TWITTER_COOKIE,
            }
        )
        return items
    except Exception:
        return []
