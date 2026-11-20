"""Enterprise-grade social text cleaning and normalization for sentiment analysis.

Designed to prevent underfitting (retaining negations, emoticons, intensity)
and overfitting (stripping random URLs, anonymizing user handles, squashing noise).
"""

from __future__ import annotations

import html
import re
import unicodedata


# Pre-compiled regex patterns for high-throughput performance
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
MENTION_PATTERN = re.compile(r"@\w+", re.UNICODE)
HASHTAG_PATTERN = re.compile(r"#(\w+)", re.UNICODE)
ELONGATED_PATTERN = re.compile(r"(.)\1{2,}", re.DOTALL)
EXCLAMATION_PATTERN = re.compile(r"!{2,}")
QUESTION_PATTERN = re.compile(r"\?{2,}")
WHITESPACE_PATTERN = re.compile(r"\s+")
CONTROL_CHAR_PATTERN = re.compile(r"[\r\n\t\x00-\x1f\x7f-\x9f]")


def clean_tweet_text(text: str, preserve_casing: bool = True) -> str:
    """Apply enterprise cleaning to raw social media / tweet text.

    Args:
        text: Raw text string.
        preserve_casing: If True, preserves original casing (for cased models like RoBERTa).

    Returns:
        Cleaned, normalized text ready for transformer tokenization.
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # 1. Unescape HTML entities (&quot;, &amp;, &lt;, &gt;, &#39;, etc.)
    cleaned = html.unescape(text)

    # 2. Normalize Unicode (NFKC handles composite characters and symbols cleanly)
    cleaned = unicodedata.normalize("NFKC", cleaned)

    # 3. Strip URLs (they eat sequence length and add domain noise)
    cleaned = URL_PATTERN.sub("", cleaned)

    # 4. Standardize user mentions to @user (CardiffNLP standard; preserves conversational syntax)
    cleaned = MENTION_PATTERN.sub("@user", cleaned)

    # 5. Extract hashtag content (e.g. #terrible -> terrible, #love -> love)
    cleaned = HASHTAG_PATTERN.sub(r"\1", cleaned)

    # 6. Squash elongated repeated characters (e.g. 'sooooo' -> 'soo', 'goooood' -> 'good')
    # Preserving 2 characters maintains emotional emphasis while matching vocabulary
    cleaned = ELONGATED_PATTERN.sub(r"\1\1", cleaned)

    # 7. Normalize repeated punctuation
    cleaned = EXCLAMATION_PATTERN.sub("!", cleaned)
    cleaned = QUESTION_PATTERN.sub("?", cleaned)

    # 8. Strip non-printable and control characters
    cleaned = CONTROL_CHAR_PATTERN.sub(" ", cleaned)

    # 9. Collapse multiple whitespaces and strip boundaries
    cleaned = WHITESPACE_PATTERN.sub(" ", cleaned).strip()

    if not preserve_casing:
        cleaned = cleaned.lower()

    return cleaned


def is_valid_tweet(cleaned_text: str, min_chars: int = 3) -> bool:
    """Check if cleaned tweet contains meaningful content for sentiment modeling.

    Rejects empty text, text consisting only of '@user', or pure punctuation.
    """
    if not cleaned_text or len(cleaned_text) < min_chars:
        return False

    # Check if text is just '@user' or multiple '@user' without content
    content_without_mentions = WHITESPACE_PATTERN.sub("", cleaned_text.replace("@user", "")).strip()
    if not content_without_mentions:
        return False

    # Must contain at least one alphanumeric character
    return any(c.isalnum() for c in content_without_mentions)


def normalise_for_dedup(text: str) -> str:
    """Normalize text strictly for cross-split duplicate detection."""
    return " ".join(str(text).split()).casefold()
