"""Rule-based emotion detection layered on sentiment."""

from __future__ import annotations

import re

EMOTIONS = ["Joy", "Anger", "Sadness", "Fear", "Surprise", "Disgust", "Neutral"]

_EMOTION_LEXICON: dict[str, list[str]] = {
    "Joy": ["love", "happy", "joy", "excited", "amazing", "wonderful", "great", "fantastic", "delighted"],
    "Anger": ["angry", "mad", "furious", "hate", "rage", "outraged", "annoyed", "frustrated", "irritated"],
    "Sadness": ["sad", "depressed", "disappointed", "heartbroken", "miserable", "unhappy", "crying", "grief"],
    "Fear": ["afraid", "scared", "worried", "anxious", "terrified", "nervous", "panic", "fear"],
    "Surprise": ["wow", "shocked", "surprised", "unexpected", "unbelievable", "omg", "whoa"],
    "Disgust": ["disgusting", "gross", "nasty", "revolting", "repulsive", "vile", "awful"],
}


def _score_emotions(text: str) -> dict[str, float]:
    lower = (text or "").lower()
    scores = {emotion: 0.0 for emotion in EMOTIONS}
    tokens = set(re.findall(r"[a-z']+", lower))

    for emotion, words in _EMOTION_LEXICON.items():
        for word in words:
            if word in lower or word in tokens:
                scores[emotion] += 1.0
            if re.search(rf"\b{re.escape(word)}\b", lower):
                scores[emotion] += 0.5

    return scores


def detect_emotion(text: str, sentiment: str = "neutral") -> dict:
    scores = _score_emotions(text)
    sentiment = (sentiment or "neutral").lower()

    if sentiment == "negative" and scores["Anger"] == 0 and scores["Sadness"] == 0:
        scores["Anger"] += 0.75
    if sentiment == "positive" and scores["Joy"] == 0:
        scores["Joy"] += 0.75

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    primary, top_score = ranked[0]

    if top_score == 0:
        primary = "Neutral"

    secondary = ranked[1][0] if len(ranked) > 1 and ranked[1][1] > 0 else None

    return {
        "primary": primary,
        "secondary": secondary,
        "scores": {k: round(v, 2) for k, v in scores.items()},
        "label": primary,
    }
