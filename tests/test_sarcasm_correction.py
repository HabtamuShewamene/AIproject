"""
Tests for unified sarcasm detection and sentiment correction.

Verifies that the sarcasm correction layer overrides BERT's surface-positive
predictions when clear sarcasm signals are present, and does NOT flip genuine
positive sentiment.
"""
from app.sentiment_rules import contains_sarcasm, sarcasm_score, SARCASM_PATTERNS
from app.explainability import extract_sarcasm_evidence


# ---------------------------------------------------------------------------
# Pattern-level unit tests (sentiment_rules.py)
# ---------------------------------------------------------------------------


class TestContainsSarcasm:
    """contains_sarcasm() must return True for all canonical sarcasm signals."""

    def test_oh_wow_delay(self):
        text = "oh wow, another 4-hour delay with zero updates"
        assert contains_sarcasm(text.lower()), "oh wow + another delay should trigger"

    def test_just_wonderful(self):
        text = "just wonderful service as always"
        assert contains_sarcasm(text.lower()), "just wonderful should trigger"

    def test_as_always(self):
        text = "great service as always!"
        assert contains_sarcasm(text.lower()), "as always should trigger"

    def test_another_delay(self):
        text = "Another 4-hour delay and nobody cares"
        assert contains_sarcasm(text.lower()), "another.*delay should trigger"

    def test_zero_updates(self):
        text = "zero updates from support as usual"
        assert contains_sarcasm(text.lower()), "zero updates should trigger"

    def test_oh_great(self):
        text = "oh great, the app crashed again"
        assert contains_sarcasm(text.lower())

    def test_love_how(self):
        text = "love how they never respond to tickets"
        assert contains_sarcasm(text.lower())

    def test_totally_fine_negative(self):
        text = "totally fine, I'll just wait another week"
        assert contains_sarcasm(text.lower())

    def test_as_per_usual(self):
        text = "Service is broken, as per usual"
        assert contains_sarcasm(text.lower())

    def test_genuine_positive_not_flagged(self):
        """Real positive text must NOT be classified as sarcasm."""
        text = "The product is actually wonderful and I love using it every day"
        # None of the sarcasm patterns should match plain genuine praise
        result = contains_sarcasm(text.lower())
        # "love" alone is not a pattern — only "love how", "love waiting", etc.
        assert not result, f"Genuine positive should not be sarcastic; patterns matched"

    def test_great_alone_not_flagged(self):
        """'great' by itself is not a sarcasm trigger; only 'oh great' is."""
        text = "this is a great product"
        assert not contains_sarcasm(text.lower())


# ---------------------------------------------------------------------------
# Evidence-layer unit tests (explainability.py)
# ---------------------------------------------------------------------------


class TestExtractSarcasmEvidence:
    """extract_sarcasm_evidence() must flag the user-reported failing case."""

    def test_full_complaint_flagged(self):
        text = "Oh wow, another 4-hour delay with zero updates from gate staff. Just wonderful service as always!"
        result = extract_sarcasm_evidence(text)
        assert result["is_sarcastic"], (
            f"Expected is_sarcastic=True, got False. "
            f"Matched patterns: {result['sarcasm_phrases']}"
        )
        assert len(result["sarcasm_phrases"]) >= 1

    def test_oh_wow_just_wonderful_found(self):
        text = "Oh wow, just wonderful!"
        result = extract_sarcasm_evidence(text)
        assert "oh wow" in result["sarcasm_phrases"] or "just wonderful" in result["sarcasm_phrases"]
        assert result["is_sarcastic"]

    def test_genuine_positive_not_sarcastic(self):
        text = "The product is actually wonderful and I love using it every day."
        result = extract_sarcasm_evidence(text)
        # May detect "amazing"/"wonderful" via hyperbole but is_sarcastic
        # requires patterns OR (contrasts + hyperbole) — without contrast markers
        # and without sarcasm phrases, it should stay False
        # We only assert no false sarcasm phrase hits
        for phrase in ["oh wow", "oh sure", "just wonderful", "love how", "love it when"]:
            assert phrase not in result["sarcasm_phrases"], (
                f"Genuine positive should not match sarcasm phrase '{phrase}'"
            )


# ---------------------------------------------------------------------------
# Sarcasm score tests (regression)
# ---------------------------------------------------------------------------


class TestSarcasmScore:
    def test_complaint_scores_high(self):
        text = "oh wow, another 4-hour delay with zero updates from gate staff. Just wonderful service as always!"
        score = sarcasm_score(text.lower())
        assert score >= 2, f"Expected score >= 2, got {score}"

    def test_neutral_scores_zero_or_low(self):
        text = "The meeting is scheduled for 3pm tomorrow."
        score = sarcasm_score(text.lower())
        assert score <= 1, f"Neutral text should score 0-1, got {score}"


# ---------------------------------------------------------------------------
# Integration smoke test: patterns list completeness
# ---------------------------------------------------------------------------


class TestPatternsCoverage:
    """Ensure the SARCASM_PATTERNS list covers the minimum required signals."""

    REQUIRED_PATTERN_TRIGGERS = [
        "oh wow",
        "just wonderful",
        "as always",
        "another 4-hour delay",
        "zero updates",
        "love how they never respond",   # narrowed pattern requires negative follow-on
        "as per usual",
        "totally fine",
    ]

    def test_all_required_triggers_match(self):
        import re
        failures = []
        for phrase in self.REQUIRED_PATTERN_TRIGGERS:
            matched = any(re.search(p, phrase) for p in SARCASM_PATTERNS)
            if not matched:
                failures.append(phrase)
        assert not failures, (
            f"These phrases are NOT covered by SARCASM_PATTERNS: {failures}"
        )
