"""Download and validate a pinned English three-way TweetEval sentiment set."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from datasets import DatasetDict, load_dataset
from huggingface_hub import hf_hub_download


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_ID = "cardiffnlp/tweet_eval"
DATASET_CONFIG = "sentiment"
DATASET_REVISION = "b3a375baf0f409c77e6bc7aa35102b7b3534f8be"
LABEL_NAMES = {0: "negative", 1: "neutral", 2: "positive"}
SPLITS = ("train", "validation", "test")


def _normalise_for_overlap(text: str) -> str:
    return " ".join(str(text).split()).casefold()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_splits(dataset: DatasetDict) -> dict:
    """Validate schema, all three labels, non-empty text, and split isolation."""
    if set(dataset.keys()) != set(SPLITS):
        raise ValueError(f"Expected splits {SPLITS}; received {tuple(dataset.keys())}.")

    texts_by_split: dict[str, list[str]] = {}
    summary: dict[str, dict] = {}

    for split_name in SPLITS:
        split = dataset[split_name]
        if not {"text", "label"}.issubset(split.column_names):
            raise ValueError(f"{split_name} must contain text and label columns.")

        labels = [int(label) for label in split["label"]]
        unknown_labels = sorted(set(labels) - set(LABEL_NAMES))
        if unknown_labels:
            raise ValueError(f"{split_name} contains unsupported labels: {unknown_labels}.")
        missing_labels = sorted(set(LABEL_NAMES) - set(labels))
        if missing_labels:
            raise ValueError(f"{split_name} is missing labels: {missing_labels}.")

        texts = [str(text) for text in split["text"]]
        if any(not text.strip() for text in texts):
            raise ValueError(f"{split_name} contains empty text.")

        normalized = [_normalise_for_overlap(text) for text in texts]
        texts_by_split[split_name] = normalized
        counts = Counter(labels)
        unique_count = len(set(normalized))
        summary[split_name] = {
            "rows": len(split),
            "class_counts": {
                LABEL_NAMES[label]: counts.get(label, 0)
                for label in LABEL_NAMES
            },
            "unique_texts": unique_count,
            "duplicate_rows_within_split": len(split) - unique_count,
            "empty_texts": 0,
        }

    overlaps = {}
    for left_idx, left in enumerate(SPLITS):
        for right in SPLITS[left_idx + 1 :]:
            overlap = len(set(texts_by_split[left]) & set(texts_by_split[right]))
            overlaps[f"{left}:{right}"] = overlap
    if any(overlaps.values()):
        raise ValueError(f"Text overlap found across data splits: {overlaps}.")

    return {"splits": summary, "cross_split_duplicate_texts": overlaps}


def load_pinned_dataset(cache_dir: str | Path | None = None) -> tuple[DatasetDict, dict[str, Path]]:
    """Fetch pinned Parquet files, avoiding execution of remote dataset scripts."""
    local_files: dict[str, str] = {}
    paths: dict[str, Path] = {}
    for split_name in SPLITS:
        filename = f"{DATASET_CONFIG}/{split_name}-00000-of-00001.parquet"
        path = hf_hub_download(
            repo_id=DATASET_ID,
            repo_type="dataset",
            filename=filename,
            revision=DATASET_REVISION,
            cache_dir=str(cache_dir) if cache_dir else None,
        )
        paths[split_name] = Path(path)
        local_files[split_name] = path

    dataset = load_dataset("parquet", data_files=local_files)
    return dataset, paths


def prepare_dataset(
    output_dir: str | Path | None = None,
    manifest_path: str | Path | None = None,
    cache_dir: str | Path | None = None,
) -> dict:
    output_dir = Path(output_dir or BASE_DIR / "data" / "processed")
    manifest_path = Path(
        manifest_path or BASE_DIR / "results" / "tweet_eval_manifest.json"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    dataset, source_files = load_pinned_dataset(cache_dir=cache_dir)
    audit = validate_splits(dataset)

    processed_files = {}
    for split_name in SPLITS:
        output_name = "val.csv" if split_name == "validation" else f"{split_name}.csv"
        output_path = output_dir / output_name
        frame = dataset[split_name].to_pandas()[["text", "label"]]
        frame["label"] = frame["label"].astype("int8")
        frame.to_csv(output_path, index=False)
        processed_files[output_name] = {
            "sha256": sha256_file(output_path),
            "rows": len(frame),
        }

    manifest = {
        "dataset_id": DATASET_ID,
        "config": DATASET_CONFIG,
        "revision": DATASET_REVISION,
        "label_map": LABEL_NAMES,
        "license_review": (
            "Review the original sentiment subset license and applicable X/Twitter "
            "terms before redistribution or commercial deployment."
        ),
        "source_files": {
            split: {"filename": path.name, "sha256": sha256_file(path)}
            for split, path in source_files.items()
        },
        "processed_files": processed_files,
        **audit,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    manifest = prepare_dataset()
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
