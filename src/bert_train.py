"""Fine-tune a three-class BERT classifier on the pinned TweetEval splits."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from src.download_tweet_eval import (
    BASE_DIR,
    DATASET_REVISION,
    LABEL_NAMES,
    sha256_file,
)


DATA_DIR = BASE_DIR / "data" / "processed"
TRAIN_PATH = DATA_DIR / "train.csv"
VAL_PATH = DATA_DIR / "val.csv"
TEST_PATH = DATA_DIR / "test.csv"
MANIFEST_PATH = BASE_DIR / "results" / "tweet_eval_manifest.json"
MODEL_DIR = BASE_DIR / "models" / "bert_sentiment"
METRICS_PATH = BASE_DIR / "results" / "bert_tweeteval_metrics.json"
BASE_MODEL = "bert-base-uncased"
BASE_MODEL_REVISION = "86b5e0934494bd15c9632b12f734a8a67f723594"
MAX_LENGTH = 128
SEED = 42


def load_splits() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(
            f"Missing {MANIFEST_PATH}. Run `python -m src.download_tweet_eval` first."
        )
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("revision") != DATASET_REVISION:
        raise ValueError("Dataset manifest revision does not match the pinned source.")
    manifest_labels = {
        int(label_id): label_name
        for label_id, label_name in manifest.get("label_map", {}).items()
    }
    if manifest_labels != LABEL_NAMES:
        raise ValueError("Dataset manifest label mapping does not match this trainer.")

    frames = []
    for path in (TRAIN_PATH, VAL_PATH, TEST_PATH):
        if not path.is_file():
            raise FileNotFoundError(
                f"Missing {path}. Run `python -m src.download_tweet_eval` first."
            )
        expected = manifest.get("processed_files", {}).get(path.name)
        if not expected or sha256_file(path) != expected.get("sha256"):
            raise ValueError(f"{path} does not match its pinned dataset manifest checksum.")
        frame = pd.read_csv(path)
        if len(frame) != expected.get("rows"):
            raise ValueError(f"{path} row count does not match its dataset manifest.")
        if not {"text", "label"}.issubset(frame.columns):
            raise ValueError(f"{path} must contain text and label columns.")
        if frame["text"].isna().any() or frame["text"].astype(str).str.strip().eq("").any():
            raise ValueError(f"{path} contains empty text.")
        labels = set(frame["label"].astype(int).unique())
        if labels != set(LABEL_NAMES):
            raise ValueError(f"{path} must contain all labels {sorted(LABEL_NAMES)}.")
        frames.append(
            frame[["text", "label"]].assign(
                label=lambda data: data["label"].astype(int)
            )
        )
    return tuple(frames)


def to_tokenized_dataset(frame: pd.DataFrame, tokenizer) -> Dataset:
    dataset = Dataset.from_pandas(frame, preserve_index=False)

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=MAX_LENGTH,
        )

    dataset = dataset.map(tokenize, batched=True)
    dataset = dataset.remove_columns(["text"])
    dataset.set_format(type="torch")
    return dataset


def compute_metrics(prediction) -> dict[str, float]:
    labels = prediction.label_ids
    predictions = prediction.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels,
        predictions,
        labels=sorted(LABEL_NAMES),
        average="macro",
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "precision_macro": float(precision),
        "recall_macro": float(recall),
        "f1_macro": float(f1),
    }


def main() -> None:
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        Trainer,
        TrainingArguments,
    )

    train_frame, val_frame, test_frame = load_splits()
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
    )

    train_dataset = to_tokenized_dataset(train_frame, tokenizer)
    val_dataset = to_tokenized_dataset(val_frame, tokenizer)
    test_dataset = to_tokenized_dataset(test_frame, tokenizer)

    id2label = {label_id: label_name for label_id, label_name in LABEL_NAMES.items()}
    label2id = {label_name: label_id for label_id, label_name in id2label.items()}
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
        num_labels=len(LABEL_NAMES),
        id2label=id2label,
        label2id=label2id,
    )

    training_args = TrainingArguments(
        output_dir=str(MODEL_DIR),
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        num_train_epochs=3,
        weight_decay=0.01,
        logging_steps=100,
        fp16=False,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        save_total_limit=2,
        seed=SEED,
        data_seed=SEED,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.save_model(str(MODEL_DIR))
    tokenizer.save_pretrained(str(MODEL_DIR))

    validation_metrics = trainer.evaluate(val_dataset, metric_key_prefix="validation")
    test_metrics = trainer.evaluate(test_dataset, metric_key_prefix="test")
    report = {
        "dataset_manifest": "results/tweet_eval_manifest.json",
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "seed": SEED,
        "validation": validation_metrics,
        "test": test_metrics,
    }
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
