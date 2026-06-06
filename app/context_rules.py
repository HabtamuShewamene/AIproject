import re


SARCASTIC_PATTERNS = [

    # fake positivity
    r"i (absolutely )?love waiting",
    r"oh great",
    r"yeah because",
    r"nothing says .* like",
    r"amazing\.? my .* broke",
    r"great job breaking",
    r"love that for me",

    # deadline frustration
    r"crashing .* before the deadline",
    r"another .* meeting",
    r"ignored for \d+",
    r"stuck for \d+ hours",

    # passive aggressive structures
    r"technically it works",
    r"well.*that happened",
    r"could.?ve been an email",

    # exaggerated irony
    r"best experience ever.*not",
    r"wow.*just wow",
    r"fantastic.*doesn't work",

    # disappointment patterns
    r"thanks for nothing",
    r"good luck with that",
    r"what could possibly go wrong",

]


NEGATIVE_CONTEXT_PATTERNS = [

    r"\bi hate\b",
    r"\bthis sucks\b",
    r"\bworst\b",
    r"\bterrible\b",
    r"\bawful\b",
    r"\bdisgusting\b",
    r"\bgarbage\b",
    r"\btrash\b",
    r"\bmad\b",
    r"\bangry\b",
    r"\bfrustrated\b",
]


POSITIVE_CONTEXT_PATTERNS = [

    r"\bi love\b",
    r"\bamazing\b",
    r"\bexcellent\b",
    r"\bawesome\b",
    r"\bgreat work\b",
    r"\bperfect\b",
]


def detect_context_sentiment(text):

    text_lower = text.lower()

    # -----------------------------
    # sarcasm detection
    # -----------------------------
    for pattern in SARCASTIC_PATTERNS:

        if re.search(pattern, text_lower):

            return {
                "sentiment": "negative",
                "confidence": 0.96,
                "source": "sarcasm_rule"
            }

    # -----------------------------
    # negative context
    # -----------------------------
    for pattern in NEGATIVE_CONTEXT_PATTERNS:

        if re.search(pattern, text_lower):

            return {
                "sentiment": "negative",
                "confidence": 0.90,
                "source": "negative_rule"
            }

    # -----------------------------
    # positive context
    # -----------------------------
    for pattern in POSITIVE_CONTEXT_PATTERNS:

        if re.search(pattern, text_lower):

            return {
                "sentiment": "positive",
                "confidence": 0.88,
                "source": "positive_rule"
            }

    return None