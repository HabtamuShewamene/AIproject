import json

import pandas as pd
import pytest

from src.prepare_sentiment140 import load_raw, prepare_sentiment140, split_bucket


def _write_raw_csv(path, rows):
    pd.DataFrame(rows).to_csv(path, index=False, header=False, encoding="latin-1")


def test_prepare_sentiment140_maps_labels_and_writes_manifest(tmp_path):
    raw_path = tmp_path / "training.1600000.processed.noemoticon.csv"
    _write_raw_csv(
        raw_path,
        [
            [0, "34", "date", "NO_QUERY", "one", "bad service"],
            [4, "151", "date", "NO_QUERY", "two", "great service"],
            [0, "1", "date", "NO_QUERY", "three", "bad service"],
            [4, "2", "date", "NO_QUERY", "four", "nice support"],
            [0, "3", "date", "NO_QUERY", "five", "poor quality"],
        ],
    )
    output_dir = tmp_path / "processed"
    manifest_path = tmp_path / "manifest.json"

    manifest = prepare_sentiment140(raw_path, output_dir, manifest_path)

    assert manifest["raw_label_map"] == {"0": "negative", "4": "positive"}
    assert manifest["duplicate_text_rows_removed"] == 1
    assert manifest_path.is_file()
    saved = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert saved["cross_split_duplicate_texts"] == 0
    assert (output_dir / "sentiment140_train.csv").is_file()


def test_load_raw_rejects_neutral_label_in_stage_a_source(tmp_path):
    raw_path = tmp_path / "training.1600000.processed.noemoticon.csv"
    _write_raw_csv(raw_path, [[2, "1", "date", "NO_QUERY", "one", "neutral"]])

    with pytest.raises(ValueError, match="only raw Sentiment140 targets"):
        load_raw(raw_path)


def test_split_bucket_is_stable_and_within_range():
    assert split_bucket("12345") == split_bucket("12345")
    assert 0 <= split_bucket("12345") < 100
