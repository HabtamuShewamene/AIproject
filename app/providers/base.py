"""Social Data Provider abstract base interfaces and data structures (Blueprint Module 2)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class PostMetrics:
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    quotes: int = 0
    views: int = 0
    bookmarks: int = 0

    def engagement_score(self) -> int:
        """Weighted engagement score for engagement-weighted sentiment analytics."""
        return self.likes + (self.retweets * 2) + (self.replies * 3) + (self.quotes * 2)


@dataclass
class PostData:
    post_id: str
    url: str
    text: str
    author_username: str
    author_name: str = ""
    author_verified: bool = False
    created_at: str = ""
    language: str = "en"
    metrics: PostMetrics = field(default_factory=PostMetrics)
    raw_payload: Optional[Dict[str, Any]] = None


@dataclass
class ReplyData:
    reply_id: str
    parent_id: str
    text: str
    author_username: str
    author_name: str = ""
    created_at: str = ""
    language: str = "en"
    depth: int = 1
    metrics: PostMetrics = field(default_factory=PostMetrics)
    is_nested: bool = False


@dataclass
class ProvenanceData:
    source_url: str
    provider_name: str
    collected_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    total_replies_on_x: int = 0
    replies_collected: int = 0
    coverage_percentage: float = 100.0
    is_complete: bool = True
    collection_method: str = "api"
    access_limitations: Optional[str] = None


@dataclass
class ConversationDataset:
    original_post: PostData
    replies: List[ReplyData]
    provenance: ProvenanceData


class SocialDataProvider(ABC):
    """Abstract interface for social media data harvesting adapters."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider identifier (e.g. 'apify', 'synthetic', 'mock')."""
        pass

    @abstractmethod
    def fetch_post(self, url: str) -> Optional[PostData]:
        """Retrieve original post data."""
        pass

    @abstractmethod
    def fetch_conversation(
        self,
        url: str,
        max_replies: int = 50,
        include_nested: bool = True,
    ) -> Optional[ConversationDataset]:
        """Retrieve original post along with its public replies and conversation thread."""
        pass
