"""Production Apify Social Data Provider for live Twitter/X thread harvesting."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import List, Optional

from app.config import APIFY_TOKEN, TWITTER_COOKIE
from app.providers.base import (
    ConversationDataset,
    PostData,
    PostMetrics,
    ProvenanceData,
    ReplyData,
    SocialDataProvider,
)

try:
    from apify_client import ApifyClient
except ImportError:  # pragma: no cover
    ApifyClient = None


ACTOR_ID = "automation-lab/twitter-scraper"


class ApifySocialProvider(SocialDataProvider):
    """Fetches original post and replies from Twitter/X via Apify actors."""

    def __init__(self, token: Optional[str] = None):
        self._token = token or APIFY_TOKEN
        self._client = ApifyClient(self._token) if (ApifyClient and self._token) else None

    @property
    def provider_name(self) -> str:
        return "apify"

    def is_configured(self) -> bool:
        return bool(self._client and self._token)

    def fetch_post(self, url: str) -> Optional[PostData]:
        if not self.is_configured():
            return None

        post_id = self._extract_post_id(url)
        if not post_id:
            return None

        try:
            items = self._run_actor({
                "scrapeMode": "x-post-scraper",
                "scrapingMode": "Tweets by URL/ID",
                "mode": "tweets",
                "tweetURLs": [url],
                "tweet_url": url,
                "twitterCookie": TWITTER_COOKIE,
                "loginCookies": TWITTER_COOKIE,
            })
            if not items:
                return None

            raw = items[0]
            return self._normalize_post(raw, url, post_id)
        except Exception:
            return None

    def fetch_conversation(
        self,
        url: str,
        max_replies: int = 50,
        include_nested: bool = True,
    ) -> Optional[ConversationDataset]:
        if not self.is_configured():
            return None

        post_id = self._extract_post_id(url)
        if not post_id:
            return None

        try:
            # Apify Actor configuration for tweet + conversation replies
            items = self._run_actor({
                "scrapeMode": "x-post-scraper",
                "scrapingMode": "Tweets with Replies",
                "mode": "replies",
                "tweetURLs": [url],
                "tweet_url": url,
                "maxReplies": max_replies,
                "twitterCookie": TWITTER_COOKIE,
                "loginCookies": TWITTER_COOKIE,
            })
            if not items:
                return None

            original_raw = items[0]
            original_post = self._normalize_post(original_raw, url, post_id)

            replies: List[ReplyData] = []
            seen_texts = set()

            for item in items[1:]:
                text = (item.get("text") or "").strip()
                if not text or text in seen_texts:
                    continue
                seen_texts.add(text)

                parent_id = str(item.get("inReplyToStatusId") or post_id)
                is_nested = parent_id != post_id
                if not include_nested and is_nested:
                    continue

                reply_id = str(item.get("id") or item.get("id_str") or f"{post_id}_r{len(replies)+1}")
                author = item.get("author") or {}
                author_username = author.get("userName") or item.get("authorUsername") or "anonymous"
                author_name = author.get("name") or author_username

                metrics = PostMetrics(
                    likes=int(item.get("likeCount") or 0),
                    retweets=int(item.get("retweetCount") or 0),
                    replies=int(item.get("replyCount") or 0),
                    quotes=int(item.get("quoteCount") or 0),
                )

                replies.append(
                    ReplyData(
                        reply_id=reply_id,
                        parent_id=parent_id,
                        text=text,
                        author_username=author_username,
                        author_name=author_name,
                        created_at=item.get("createdAt") or datetime.now(timezone.utc).isoformat(),
                        language=item.get("lang") or "en",
                        depth=2 if is_nested else 1,
                        metrics=metrics,
                        is_nested=is_nested,
                    )
                )

            total_on_x = max(original_post.metrics.replies, len(replies))
            collected = len(replies)
            coverage = round((collected / max(total_on_x, 1)) * 100, 2)
            is_complete = collected >= total_on_x

            provenance = ProvenanceData(
                source_url=url,
                provider_name=self.provider_name,
                total_replies_on_x=total_on_x,
                replies_collected=collected,
                coverage_percentage=coverage,
                is_complete=is_complete,
                collection_method="apify_actor",
                access_limitations=(
                    None
                    if is_complete
                    else f"Apify harvested {collected} of estimated {total_on_x} replies (coverage: {coverage}%)."
                ),
            )

            return ConversationDataset(
                original_post=original_post,
                replies=replies,
                provenance=provenance,
            )
        except Exception:
            return None

    def _run_actor(self, run_input: dict):
        if not self._client:
            return []
        run = self._client.actor(ACTOR_ID).call(run_input=run_input)
        dataset_id = run.get("defaultDatasetId") if isinstance(run, dict) else None
        if not dataset_id:
            return []
        items = self._client.dataset(dataset_id).list_items().items
        return items or []

    def _normalize_post(self, raw: dict, url: str, post_id: str) -> PostData:
        author = raw.get("author") or {}
        author_username = author.get("userName") or raw.get("authorUsername") or "unknown"
        author_name = author.get("name") or author_username
        author_verified = bool(author.get("isBlueVerified") or author.get("verified"))

        metrics = PostMetrics(
            likes=int(raw.get("likeCount") or raw.get("likes") or 0),
            retweets=int(raw.get("retweetCount") or raw.get("retweets") or 0),
            replies=int(raw.get("replyCount") or raw.get("replies") or 0),
            quotes=int(raw.get("quoteCount") or raw.get("quotes") or 0),
            views=int(raw.get("viewCount") or 0),
            bookmarks=int(raw.get("bookmarkCount") or 0),
        )

        return PostData(
            post_id=post_id,
            url=url,
            text=raw.get("text") or "",
            author_username=author_username,
            author_name=author_name,
            author_verified=author_verified,
            created_at=raw.get("createdAt") or datetime.now(timezone.utc).isoformat(),
            language=raw.get("lang") or "en",
            metrics=metrics,
            raw_payload=raw,
        )

    def _extract_post_id(self, url: str) -> str:
        match = re.search(r"/status/(\d+)", url)
        return match.group(1) if match else ""
