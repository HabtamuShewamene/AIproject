"""Generate human-readable sentiment explanations."""

from __future__ import annotations

import re

from app.sentiment_rules import (
    NEGATIVE_WORDS,
    NEGATION_WORDS,
    POSITIVE_WORDS,
    contains_sarcasm,
    count_keywords,
    has_negation,
)

_TOKEN_PATTERN = re.compile(r"[a-z0-9']+", re.I)


def _top_influencing_words(text: str, sentiment: str, limit: int = 5) -> list[str]:
    lower = text.lower()
    pool = POSITIVE_WORDS if sentiment == "positive" else NEGATIVE_WORDS
    if sentiment == "neutral":
        pool = POSITIVE_WORDS + NEGATIVE_WORDS

    hits = [word for word in pool if word in lower]
    tokens = _TOKEN_PATTERN.findall(lower)
    for token in tokens:
        if len(token) > 4 and token not in hits:
            if sentiment == "negative" and token in NEGATIVE_WORDS:
                hits.append(token)
            elif sentiment == "positive" and token in POSITIVE_WORDS:
                hits.append(token)
    return hits[:limit]


def _confidence_explanation(confidence: float, sentiment: str) -> str:
    pct = round(confidence * 100 if confidence <= 1 else confidence, 1)
    if pct >= 85:
        return (
            f"Model confidence is high ({pct}%). Strong signals support a {sentiment} label."
        )
    if pct >= 65:
        return (
            f"Model confidence is moderate ({pct}%). Signals lean {sentiment} with some ambiguity."
        )
    return (
        f"Model confidence is low ({pct}%). Mixed signals — interpret this {sentiment} label cautiously."
    )


def explain_sentiment(
    text: str,
    sentiment: str,
    confidence: float,
    *,
    sarcasm_detected: bool | None = None,
) -> dict:
    lower = (text or "").strip().lower()
    sentiment = (sentiment or "neutral").lower()
    confidence = float(confidence or 0)

    sarcasm = sarcasm_detected if sarcasm_detected is not None else contains_sarcasm(lower)
    negation = has_negation(lower)
    pos_hits = count_keywords(lower, POSITIVE_WORDS)
    neg_hits = count_keywords(lower, NEGATIVE_WORDS)
    key_words = _top_influencing_words(lower, sentiment)

    reasons: list[str] = []

    if sarcasm and sentiment == "negative":
        reasons.append(
            'Positive phrasing (e.g. "love") overridden by sarcasm or complaint context.'
        )
    elif pos_hits and sentiment == "positive":
        reasons.append(f"Positive language detected ({pos_hits} cue(s)).")
    elif neg_hits and sentiment == "negative":
        reasons.append(f"Negative language detected ({neg_hits} cue(s)).")
    elif sentiment == "neutral":
        reasons.append("Balanced or weak polarity across the text.")
    else:
        reasons.append(f"Overall tone classified as {sentiment}.")

    if negation and pos_hits:
        reasons.append("Negation shifted apparent positive wording toward negative.")

    summary = " ".join(reasons)
    if key_words:
        summary += f" Key terms: {', '.join(key_words)}."

    return {
        "sentiment": sentiment,
        "summary": summary.strip(),
        "key_words": key_words,
        "confidence_explanation": _confidence_explanation(confidence, sentiment),
        "signals": {
            "sarcasm_detected": sarcasm,
            "negation_detected": negation,
            "positive_cues": pos_hits,
            "negative_cues": neg_hits,
        },
    }
