import json
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from src import bert_train
from src.download_tweet_eval import DATASET_REVISION, LABEL_NAMES, sha256_file


def _write_split(path, labels=(0, 1, 2)):
    pd.DataFrame(
        {"text": [f"sample {label}" for label in labels], "label": labels}
    ).to_csv(path, index=False)


def _write_manifest(path, split_paths):
    names = ("train.csv", "val.csv", "test.csv")
    path.write_text(
        json.dumps(
            {
                "revision": DATASET_REVISION,
                "label_map": {str(key): value for key, value in LABEL_NAMES.items()},
                "processed_files": {
                    name: {
                        "sha256": sha256_file(split_path),
                        "rows": len(pd.read_csv(split_path)),
                    }
                    for name, split_path in zip(names, split_paths)
                },
            }
        ),
        encoding="utf-8",
    )


def test_load_splits_reads_three_class_data_from_configured_paths(tmp_path, monkeypatch):
    paths = [tmp_path / name for name in ("train.csv", "val.csv", "test.csv")]
    for path in paths:
        _write_split(path)
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, paths)
    monkeypatch.setattr(bert_train, "MANIFEST_PATH", manifest)
    monkeypatch.setattr(bert_train, "TRAIN_PATH", paths[0])
    monkeypatch.setattr(bert_train, "VAL_PATH", paths[1])
    monkeypatch.setattr(bert_train, "TEST_PATH", paths[2])

    frames = bert_train.load_splits()

    assert [len(frame) for frame in frames] == [3, 3, 3]
    assert [set(frame["label"]) for frame in frames] == [{0, 1, 2}] * 3


def test_load_splits_fails_with_actionable_message_when_data_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(bert_train, "TRAIN_PATH", tmp_path / "missing.csv")

    with pytest.raises(FileNotFoundError, match="download_tweet_eval"):
        bert_train.load_splits()


def test_load_splits_rejects_a_split_without_all_three_labels(tmp_path, monkeypatch):
    train_path = tmp_path / "train.csv"
    val_path = tmp_path / "val.csv"
    test_path = tmp_path / "test.csv"
    _write_split(train_path, labels=(0, 1))
    _write_split(val_path)
    _write_split(test_path)
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, (train_path, val_path, test_path))
    monkeypatch.setattr(bert_train, "MANIFEST_PATH", manifest)
    monkeypatch.setattr(bert_train, "TRAIN_PATH", train_path)
    monkeypatch.setattr(bert_train, "VAL_PATH", val_path)
    monkeypatch.setattr(bert_train, "TEST_PATH", test_path)

    with pytest.raises(ValueError, match="must contain all labels"):
        bert_train.load_splits()


def test_load_splits_rejects_data_that_no_longer_matches_manifest(tmp_path, monkeypatch):
    paths = [tmp_path / name for name in ("train.csv", "val.csv", "test.csv")]
    for path in paths:
        _write_split(path)
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, paths)
    paths[0].write_text("text,label\nchanged,0\n", encoding="utf-8")
    monkeypatch.setattr(bert_train, "TRAIN_PATH", paths[0])
    monkeypatch.setattr(bert_train, "VAL_PATH", paths[1])
    monkeypatch.setattr(bert_train, "TEST_PATH", paths[2])
    monkeypatch.setattr(bert_train, "MANIFEST_PATH", manifest)

    with pytest.raises(ValueError, match="checksum"):
        bert_train.load_splits()


def test_compute_metrics_reports_macro_three_class_scores():
    prediction = SimpleNamespace(
        label_ids=np.array([0, 1, 2]),
        predictions=np.array(
            [
                [0.9, 0.05, 0.05],
                [0.1, 0.8, 0.1],
                [0.05, 0.05, 0.9],
            ]
        ),
    )

    metrics = bert_train.compute_metrics(prediction)

    assert metrics == {
        "accuracy": 1.0,
        "precision_macro": 1.0,
        "recall_macro": 1.0,
        "f1_macro": 1.0,
    }
