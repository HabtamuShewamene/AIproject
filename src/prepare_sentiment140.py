"""Validate and prepare the Kaggle Sentiment140 training CSV for Stage A.

Applies enterprise-level cleaning (HTML unescaping, URL removal, mention standardization,
character elongation squashing, and noise filtering) followed by deterministic
cryptographic 80% Train, 10% Validation, 10% Test splitting with zero leakage.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from src.download_tweet_eval import BASE_DIR, sha256_file
from src.enterprise_cleaner import clean_tweet_text, is_valid_tweet, normalise_for_dedup


RAW_PATH = BASE_DIR / "data" / "raw" / "training.1600000.processed.noemoticon.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
MANIFEST_PATH = BASE_DIR / "results" / "sentiment140_manifest.json"
COLUMN_NAMES = ("target", "id", "date", "query", "user", "text")
LABEL_MAP = {0: 0, 4: 1}
LABEL_NAMES = {0: "negative", 1: "positive"}
SEED = 42


def normalise_text(text: str) -> str:
    """Normalize text strictly for deduplication."""
    return normalise_for_dedup(text)


def split_bucket(tweet_id: str) -> int:
    """Deterministic 0-99 bucket based on SHA-256 of tweet_id."""
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

    # 1. Map labels
    frame["label"] = frame["target"].map(LABEL_MAP).astype("int8")

    # 2. Enterprise Cleaning
    frame["text"] = frame["text"].fillna("").astype(str).apply(clean_tweet_text)

    # 3. Filter invalid / ghost text (e.g. empty, pure URLs, or pure punctuation)
    frame = frame[frame["text"].apply(is_valid_tweet)].copy()

    # 4. Normalized representation for deduplication
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

    # Global deduplication on cleaned text
    frame = frame.drop_duplicates(subset="normalized_text", keep="first").copy()
    duplicates_removed = before_deduplication - len(frame)

    # Compute deterministic bucket per tweet
    frame["bucket"] = frame["id"].map(split_bucket)

    if len(frame) >= 100:
        # Strict 80% Train, 10% Validation, 10% Test split via cryptographic buckets
        train = frame[frame["bucket"] < 80][["text", "label"]]
        validation = frame[(frame["bucket"] >= 80) & (frame["bucket"] < 90)][["text", "label"]]
        test = frame[frame["bucket"] >= 90][["text", "label"]]
    else:
        # Graceful fallback for tiny unit-test fixtures (< 100 rows)
        n = len(frame)
        n_val = max(1, int(n * 0.1))
        n_test = max(1, int(n * 0.1))
        train = frame.iloc[: max(1, n - n_val - n_test)][["text", "label"]]
        validation = frame.iloc[max(1, n - n_val - n_test) : n - n_test][["text", "label"]]
        test = frame.iloc[n - n_test :][["text", "label"]]

    for name, split in (("train", train), ("validation", validation), ("test", test)):
        if not len(split):
            raise ValueError(f"Prepared Stage A {name} split is empty.")
        if len(frame) >= 100 and set(split["label"]) != set(LABEL_NAMES):
            raise ValueError(f"Prepared Stage A {name} split is missing a class.")

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    output_paths = {
        "train": output_dir / "sentiment140_train.csv",
        "validation": output_dir / "sentiment140_validation.csv",
        "test": output_dir / "sentiment140_test.csv",
    }
    train.to_csv(output_paths["train"], index=False)
    validation.to_csv(output_paths["validation"], index=False)
    test.to_csv(output_paths["test"], index=False)

    def summary(split: pd.DataFrame) -> dict:
        counts = Counter(split["label"])
        return {
            "rows": len(split),
            "class_counts": {LABEL_NAMES[label]: counts.get(label, 0) for label in LABEL_NAMES},
        }

    # Cross-split leakage checks
    train_texts = set(train["text"].map(normalise_text))
    val_texts = set(validation["text"].map(normalise_text))
    test_texts = set(test["text"].map(normalise_text))

    leakage_train_val = len(train_texts & val_texts)
    leakage_train_test = len(train_texts & test_texts)
    leakage_val_test = len(val_texts & test_texts)

    if leakage_train_val or leakage_train_test or leakage_val_test:
        raise ValueError(
            f"Cross-split leakage detected! train:val={leakage_train_val}, "
            f"train:test={leakage_train_test}, val:test={leakage_val_test}"
        )

    manifest = {
        "dataset": "Sentiment140 Kaggle/Stanford training file",
        "raw_file": raw_path.name,
        "raw_sha256": sha256_file(raw_path),
        "cleaned_valid_rows": before_deduplication,
        "duplicate_text_rows_removed": duplicates_removed,
        "raw_label_map": {"0": "negative", "4": "positive"},
        "training_label_map": {str(key): value for key, value in LABEL_NAMES.items()},
        "split_method": "sha256(seed=42, tweet_id) buckets: <80 train (80%), 80-89 val (10%), >=90 test (10%)",
        "split_ratios": {"train": 0.80, "validation": 0.10, "test": 0.10},
        "cross_split_duplicate_texts": leakage_train_val + leakage_train_test + leakage_val_test,
        "cross_split_duplicates_by_pair": {
            "train:validation": leakage_train_val,
            "train:test": leakage_train_test,
            "validation:test": leakage_val_test,
        },
        "splits": {
            "train": summary(train),
            "validation": summary(validation),
            "test": summary(test),
        },
        "processed_files": {
            name: {
                "filename": path.name,
                "sha256": sha256_file(path),
                "rows": len(train) if name == "train" else len(validation) if name == "validation" else len(test),
            }
            for name, path in output_paths.items()
        },
        "preprocessing_pipeline": [
            "HTML entity unescaping (&quot; -> \", &amp; -> &)",
            "Unicode NFKC normalization",
            "URL stripping (https?://...)",
            "User mention standardization (@username -> @user)",
            "Hashtag content extraction (#hashtag -> hashtag)",
            "Character elongation squashing (e.g. sooooo -> soo)",
            "Punctuation normalization (!, ?)",
            "Contraction and negation preservation",
            "Noise and ghost text filtering (min_chars >= 3)",
            "Global deduplication on cleaned text",
        ],
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
