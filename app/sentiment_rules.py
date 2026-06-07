"""Shared sentiment heuristics used by main and intelligence modules."""

import re

NEGATIVE_WORDS = [
    "hate",
    "terrible",
    "awful",
    "worst",
    "stupid",
    "annoying",
    "disgusting",
    "broken",
    "crash",
    "crashed",
    "useless",
    "garbage",
    "bad",
    "horrible",
    "mad",
    "angry",
    "slow",
    "frustrated",
    "disappointed",
]

POSITIVE_WORDS = [
    "love",
    "great",
    "awesome",
    "amazing",
    "excellent",
    "perfect",
    "beautiful",
    "good",
    "fantastic",
]

SARCASM_PATTERNS = [
    r"oh great",
    r"yeah right",
    r"oh fantastic",
    r"fantastic, now",
    r"love that for me",
    r"love waiting",
    r"amazing\.",
    r"great job",
    r"well done",
    r"excellent, now",
    r"another .* meeting",
    r"thanks for nothing",
    r"works now and i have no idea why",
    r"nothing says",
    r"i (absolutely )?love waiting",
    r"what a brilliant idea",
    r"perfect timing",
    r"couldn't have gone worse",
    r"this is going so well",
    r"i'm thrilled",
    r"how lovely",
    r"masterpiece again",
]

NEGATION_WORDS = [
    "not",
    "never",
    "no",
    "don't",
    "didn't",
    "isn't",
    "wasn't",
    "can't",
]


def contains_sarcasm(text: str) -> bool:
    text = text.lower()
    return any(re.search(pattern, text) for pattern in SARCASM_PATTERNS)


def sarcasm_score(text: str) -> int:
    """Return a light sarcasm score used for edge-case correction."""

    text = (text or "").lower()
    score = 0

    for pattern in SARCASM_PATTERNS:
        if re.search(pattern, text):
            score += 2

    positive_markers = sum(text.count(word) for word in POSITIVE_WORDS)
    negative_markers = sum(text.count(word) for word in NEGATIVE_WORDS)

    if positive_markers and negative_markers:
        score += 1

    if "..." in text or text.count("!") >= 2:
        score += 1

    if "yeah right" in text or "sure," in text or "as usual" in text:
        score += 1

    return score


def count_keywords(text: str, keywords: list) -> int:
    text = text.lower()
    return sum(text.count(word) for word in keywords)


def has_negation(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in NEGATION_WORDS)
