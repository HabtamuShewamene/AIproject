import pytest
from datasets import Dataset, DatasetDict

from src.download_tweet_eval import validate_splits


def _small_dataset(train_texts=None):
    train_texts = train_texts or ["train negative", "train neutral", "train positive"]
    return DatasetDict(
        {
            "train": Dataset.from_dict(
                {"text": train_texts, "label": [0, 1, 2][: len(train_texts)]}
            ),
            "validation": Dataset.from_dict(
                {"text": ["validation negative", "validation neutral", "validation positive"], "label": [0, 1, 2]}
            ),
            "test": Dataset.from_dict(
                {"text": ["test negative", "test neutral", "test positive"], "label": [0, 1, 2]}
            ),
        }
    )


def test_validate_splits_reports_three_way_counts_and_no_overlap():
    audit = validate_splits(_small_dataset())

    assert audit["splits"]["train"]["class_counts"] == {
        "negative": 1,
        "neutral": 1,
        "positive": 1,
    }
    assert not any(audit["cross_split_duplicate_texts"].values())


def test_validate_splits_rejects_cross_split_duplicates():
    dataset = _small_dataset()
    dataset["validation"] = Dataset.from_dict(
        {"text": ["train negative", "validation neutral", "validation positive"], "label": [0, 1, 2]}
    )

    with pytest.raises(ValueError, match="overlap found"):
        validate_splits(dataset)


def test_validate_splits_rejects_empty_text():
    dataset = _small_dataset()
    dataset["test"] = Dataset.from_dict(
        {"text": ["", "test neutral", "test positive"], "label": [0, 1, 2]}
    )

    with pytest.raises(ValueError, match="empty text"):
        validate_splits(dataset)
