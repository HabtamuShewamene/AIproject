"""Social data provider factory with environment-aware fallback."""

from __future__ import annotations

import os
from typing import Optional

from app.config import APIFY_TOKEN
from app.providers.apify_provider import ApifySocialProvider
from app.providers.base import SocialDataProvider
from app.providers.synthetic_provider import SyntheticSocialProvider


def get_social_provider(provider_name: Optional[str] = None) -> SocialDataProvider:
    """
    Resolve the requested social data provider.
    Defaults to Apify if APIFY_TOKEN is set, otherwise gracefully falls back to Synthetic.
    """
    selected = (provider_name or os.getenv("SOCIAL_DATA_PROVIDER", "")).lower()

    if selected == "apify":
        apify = ApifySocialProvider()
        if apify.is_configured():
            return apify
        # If explicitly requested but unconfigured, return Apify anyway so caller gets clear error
        return apify

    if selected == "synthetic":
        return SyntheticSocialProvider()

    # Automatic selection: Use Apify if credentials exist, else Synthetic
    if APIFY_TOKEN:
        apify = ApifySocialProvider()
        if apify.is_configured():
            return apify

    return SyntheticSocialProvider()
