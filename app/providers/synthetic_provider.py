"""Synthetic Social Data Provider for deterministic testing, offline dev, and interactive demos."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import List, Optional

from app.providers.base import (
    ConversationDataset,
    PostData,
    PostMetrics,
    ProvenanceData,
    ReplyData,
    SocialDataProvider,
)

# Curated conversation response pools representing realistic public reactions
REPLY_POOLS = [
    {
        "text": "This is genuinely one of the best updates you have shipped this year. Massive speed improvement!",
        "author": "dev_alex",
        "likes": 42,
        "retweets": 5,
        "is_nested": False,
    },
    {
        "text": "Honestly disappointed. The new pricing structure makes this unaffordable for indie developers.",
        "author": "sarah_builds",
        "likes": 88,
        "retweets": 12,
        "is_nested": False,
    },
    {
        "text": "Does this also support legacy v1 configurations or do we have to migrate everything manually?",
        "author": "cloud_arch",
        "likes": 14,
        "retweets": 1,
        "is_nested": False,
    },
    {
        "text": "Tried testing it 10 minutes ago and it crashed immediately on export. Please investigate.",
        "author": "qa_tester_99",
        "likes": 31,
        "retweets": 4,
        "is_nested": False,
    },
    {
        "text": "Oh wow, another breaking change with zero migration notice. Just wonderful!",
        "author": "sarcastic_coder",
        "likes": 56,
        "retweets": 9,
        "is_nested": False,
    },
    {
        "text": "Completely agree with @sarah_builds, the cost doubled without any added value for small teams.",
        "author": "founder_mike",
        "likes": 27,
        "retweets": 2,
        "is_nested": True,
    },
    {
        "text": "The documentation is clear and the onboarding walkthrough was effortless. Kudos to the design team!",
        "author": "ux_elena",
        "likes": 19,
        "retweets": 0,
        "is_nested": False,
    },
    {
        "text": "Can we expect an official SDK for Python and Go sometime next quarter?",
        "author": "backend_dave",
        "likes": 8,
        "retweets": 0,
        "is_nested": False,
    },
    {
        "text": "Fix the mobile layout first before rolling out experimental features. Navigation is broken.",
        "author": "mobile_fanatic",
        "likes": 34,
        "retweets": 3,
        "is_nested": False,
    },
    {
        "text": "Loving the dark mode aesthetics! Clean typography and very responsive.",
        "author": "design_kai",
        "likes": 23,
        "retweets": 1,
        "is_nested": False,
    },
]


class SyntheticSocialProvider(SocialDataProvider):
    """Provides high-fidelity simulated conversation threads without external network calls."""

    @property
    def provider_name(self) -> str:
        return "synthetic"

    def fetch_post(self, url: str) -> Optional[PostData]:
        post_id = self._extract_post_id(url)
        return PostData(
            post_id=post_id,
            url=url,
            text="Today we are officially rolling out our new AI platform updates worldwide! What features are you most excited to try?",
            author_username="techcorp_official",
            author_name="TechCorp Official",
            author_verified=True,
            created_at=datetime.now(timezone.utc).isoformat(),
            language="en",
            metrics=PostMetrics(
                likes=1450,
                retweets=320,
                replies=len(REPLY_POOLS),
                quotes=85,
                views=45200,
                bookmarks=310,
            ),
        )

    def fetch_conversation(
        self,
        url: str,
        max_replies: int = 50,
        include_nested: bool = True,
    ) -> Optional[ConversationDataset]:
        original = self.fetch_post(url)
        if not original:
            return None

        # Seed selection deterministically by URL
        seed = int(hashlib.md5(url.encode()).hexdigest(), 16) % 1000
        total_on_x = max(len(REPLY_POOLS), 45)

        replies: List[ReplyData] = []
        target_count = min(max_replies, len(REPLY_POOLS))

        for idx, template in enumerate(REPLY_POOLS[:target_count]):
            if not include_nested and template["is_nested"]:
                continue

            parent_id = original.post_id if not template["is_nested"] else f"{original.post_id}_r1"
            reply_id = f"{original.post_id}_r{idx + 1}"

            replies.append(
                ReplyData(
                    reply_id=reply_id,
                    parent_id=parent_id,
                    text=template["text"],
                    author_username=template["author"],
                    author_name=template["author"].replace("_", " ").title(),
                    created_at=datetime.now(timezone.utc).isoformat(),
                    language="en",
                    depth=2 if template["is_nested"] else 1,
                    metrics=PostMetrics(
                        likes=template["likes"],
                        retweets=template["retweets"],
                        replies=2 if not template["is_nested"] else 0,
                    ),
                    is_nested=template["is_nested"],
                )
            )

        collected = len(replies)
        coverage = round((collected / total_on_x) * 100, 2)
        is_complete = collected >= total_on_x

        provenance = ProvenanceData(
            source_url=url,
            provider_name=self.provider_name,
            total_replies_on_x=total_on_x,
            replies_collected=collected,
            coverage_percentage=coverage,
            is_complete=is_complete,
            collection_method="synthetic_generator",
            access_limitations=None if is_complete else f"Capped by user max_replies limit ({max_replies})",
        )

        return ConversationDataset(
            original_post=original,
            replies=replies,
            provenance=provenance,
        )

    def _extract_post_id(self, url: str) -> str:
        match = re.search(r"/status/(\d+)", url)
        return match.group(1) if match else "1827364591029384756"
