"""Validate and prepare the Kaggle Sentiment140 training CSV for Stage A."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from src.download_tweet_eval import BASE_DIR, sha256_file


RAW_PATH = BASE_DIR / "data" / "raw" / "training.1600000.processed.noemoticon.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
MANIFEST_PATH = BASE_DIR / "results" / "sentiment140_manifest.json"
COLUMN_NAMES = ("target", "id", "date", "query", "user", "text")
LABEL_MAP = {0: 0, 4: 1}
LABEL_NAMES = {0: "negative", 1: "positive"}
SEED = 42


def normalise_text(text: str) -> str:
    """Normalize only for duplicate detection; preserve training text unchanged."""
    return " ".join(str(text).split()).casefold()


def split_bucket(tweet_id: str) -> int:
    """Deterministic 0-99 bucket, independent of input-file order."""
    digest = hashlib.sha256(f"{SEED}:{tweet_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % 100


def load_raw(path: str | Path = RAW_PATH) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {path}. Download the Kaggle Sentiment140 archive and place "
            "training.1600000.processed.noemoticon.csv in data/raw/."
        )
    frame = pd.read_csv(
        path,
        encoding="latin-1",
        header=None,
        names=COLUMN_NAMES,
        dtype={"target": "int16", "id": "string", "text": "string", "user": "string"},
        low_memory=False,
    )
    if frame.shape[1] != len(COLUMN_NAMES):
        raise ValueError("Sentiment140 input must have exactly six columns.")
    labels = set(frame["target"].dropna().astype(int))
    if not labels.issubset(LABEL_MAP) or not labels:
        raise ValueError(
            f"Stage A accepts only raw Sentiment140 targets {sorted(LABEL_MAP)}; got {sorted(labels)}."
        )
    frame["text"] = frame["text"].fillna("").astype(str)
    frame = frame[frame["text"].str.strip().ne("")].copy()
    frame["label"] = frame["target"].map(LABEL_MAP).astype("int8")
    frame["normalized_text"] = frame["text"].map(normalise_text)
    return frame


def prepare_sentiment140(
    raw_path: str | Path = RAW_PATH,
    output_dir: str | Path = OUTPUT_DIR,
    manifest_path: str | Path = MANIFEST_PATH,
) -> dict:
    raw_path = Path(raw_path)
    output_dir = Path(output_dir)
    manifest_path = Path(manifest_path)
    frame = load_raw(raw_path)
    before_deduplication = len(frame)
    frame = frame.drop_duplicates(subset="normalized_text", keep="first").copy()
    frame["bucket"] = frame["id"].map(split_bucket)

    # One percent is an untouched binary validation sample for Stage A monitoring.
    train = frame[frame["bucket"] != 0][["text", "label"]]
    validation = frame[frame["bucket"] == 0][["text", "label"]]
    if (
        not len(validation)
        or set(train["label"]) != set(LABEL_NAMES)
        or set(validation["label"]) != set(LABEL_NAMES)
    ):
        raise ValueError("Prepared Stage A splits are empty or missing a class.")

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    output_paths = {
        "train": output_dir / "sentiment140_train.csv",
        "validation": output_dir / "sentiment140_validation.csv",
    }
    train.to_csv(output_paths["train"], index=False)
    validation.to_csv(output_paths["validation"], index=False)

    def summary(split: pd.DataFrame) -> dict:
        counts = Counter(split["label"])
        return {
            "rows": len(split),
            "class_counts": {LABEL_NAMES[label]: counts.get(label, 0) for label in LABEL_NAMES},
        }

    overlap = len(
        set(train["text"].map(normalise_text)) & set(validation["text"].map(normalise_text))
    )
    if overlap:
        raise ValueError(f"Prepared Stage A train/validation overlap: {overlap} rows.")
    manifest = {
        "dataset": "Sentiment140 Kaggle/Stanford training file",
        "raw_file": raw_path.name,
        "raw_sha256": sha256_file(raw_path),
        "raw_rows_after_empty_text_filter": before_deduplication,
        "duplicate_text_rows_removed": before_deduplication - len(frame),
        "raw_label_map": {"0": "negative", "4": "positive"},
        "training_label_map": {str(key): value for key, value in LABEL_NAMES.items()},
        "split_method": "sha256(seed=42, tweet_id) bucket 0 for validation",
        "cross_split_duplicate_texts": overlap,
        "splits": {"train": summary(train), "validation": summary(validation)},
        "processed_files": {
            name: {"filename": path.name, "sha256": sha256_file(path)}
            for name, path in output_paths.items()
        },
        "limitations": [
            "Labels are weak supervision derived from emoticons.",
            "Training data is binary and cannot train neutral sentiment.",
            "Tweets are historical and should not be the sole source for production quality claims.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    print(json.dumps(prepare_sentiment140(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
