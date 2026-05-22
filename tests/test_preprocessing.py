import pandas as pd

from src.preprocessing import clean_text, preprocess


def test_clean_text_removes_urls_mentions_and_hashtag_symbol():
    text = "Check THIS out! https://example.com @User #Amazing"

    cleaned = clean_text(text)

    assert cleaned == "check this out! amazing"


def test_clean_text_returns_empty_string_for_missing_values():
    assert clean_text(None) == ""


def test_preprocess_filters_invalid_rows_and_maps_labels():
    df = pd.DataFrame(
        [
            {"target": 0, "text": "Bad service @brand"},
            {"target": 4, "text": "Loved it! #Great"},
            {"target": 2, "text": "ignored label"},
            {"target": 0, "text": None},
            {"target": 4, "text": "https://example.com"},
        ]
    )

    processed = preprocess(df)

    assert list(processed.columns) == ["text", "label"]
    assert len(processed) == 2
    assert set(processed["label"]) == {0, 1}
    assert set(processed["text"]) == {"bad service", "loved it! great"}
