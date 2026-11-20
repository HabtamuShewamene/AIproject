import pandas as pd
import pytest

from src.train_staged_sentiment import metric_function, read_csv


def test_read_csv_accepts_expected_label_subset(tmp_path):
    path = tmp_path / "split.csv"
    pd.DataFrame({"text": ["a", "b"], "label": [0, 1]}).to_csv(path, index=False)

    result = read_csv(path, {0, 1})

    assert result["label"].tolist() == [0, 1]


def test_read_csv_rejects_unknown_label(tmp_path):
    path = tmp_path / "split.csv"
    pd.DataFrame({"text": ["a"], "label": [2]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="outside"):
        read_csv(path, {0, 1})


def test_metric_function_returns_macro_scores():
    class Prediction:
        label_ids = [0, 1]
        predictions = [[0.9, 0.1], [0.1, 0.9]]

    metrics = metric_function([0, 1])(Prediction())

    assert metrics["f1_macro"] == 1.0
