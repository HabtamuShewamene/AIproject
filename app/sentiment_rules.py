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
    # --- Core irony openers ---
    r"oh great",
    r"oh wow",
    r"oh sure",
    r"oh fantastic",
    r"oh really",
    r"yeah right",
    r"right\.",
    r"sure\.",
    # --- Positive-word + unambiguous negative-context combos ---
    r"just wonderful",
    r"just great",
    r"just perfect",
    r"wow amazing",
    r"fantastic, now",
    r"fantastic\. now",
    r"excellent, now",
    r"excellent\. now",
    # "great job" and "well done" removed — too ambiguous without sarcasm opener
    # --- Sarcastic love/appreciation (must require negative follow-on context) ---
    r"love that for me",
    r"love waiting",
    r"love how .{0,30}(never|always|still|keeps|keeps|broken|fail|slow|late|delay|bad|terrible|awful|annoying|useless|long|again|more|every time)",
    r"love it when .{0,30}(never|fail|broken|crash|slow|late|delay|always|bad|terrible|awful)",
    r"i (absolutely )?love waiting",
    r"absolutely love .{0,30}(never|fail|broken|slow|delay|bad)",
    # --- Delay / failure patterns ---
    r"another .* delay",
    r"another .* outage",
    r"another .* meeting",
    r"another .* issue",
    r"zero updates",
    r"no updates",
    # --- Context qualifiers that signal sarcasm ---
    r"as always",
    r"as per usual",
    r"as usual",
    r"totally fine",
    r"perfectly fine",
    r"works perfectly",
    r"works now and i have no idea why",
    r"what a surprise",
    r"big surprise",
    r"shocking",
    # --- Hyperbolic irony ---
    r"amazing\.",
    r"amazing!",
    r"what a brilliant idea",
    r"perfect timing",
    r"nothing says",
    r"couldn't have gone worse",
    r"this is going so well",
    r"i'm thrilled",
    r"how lovely",
    r"masterpiece again",
    r"thanks for nothing",
    r"not at all",
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
