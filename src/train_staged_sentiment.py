"""Run binary Sentiment140 adaptation then three-way TweetEval fine-tuning."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from datasets import Dataset
from sklearn.metrics import accuracy_score, classification_report, precision_recall_fscore_support

from src.download_tweet_eval import BASE_DIR, LABEL_NAMES


DATA_DIR = BASE_DIR / "data" / "processed"
RESULTS_DIR = BASE_DIR / "results"
STAGE_A_DIR = BASE_DIR / "models" / "stage_a_sentiment140"
STAGE_B_DIR = BASE_DIR / "models" / "bert_sentiment"
BASE_MODEL = "google-bert/bert-base-uncased"
BASE_MODEL_REVISION = "86b5e0934494bd15c9632b12f734a8a67f723594"
MAX_LENGTH = 128
SEED = 42


def read_csv(path: Path, expected_labels: set[int]) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}. Run the required data preparation script first.")
    frame = pd.read_csv(path)
    if set(frame.columns) != {"text", "label"}:
        raise ValueError(f"{path} must contain exactly text and label columns.")
    if frame["text"].isna().any() or frame["text"].astype(str).str.strip().eq("").any():
        raise ValueError(f"{path} contains empty text.")
    frame["label"] = frame["label"].astype(int)
    if not set(frame["label"]).issubset(expected_labels):
        raise ValueError(f"{path} contains labels outside {sorted(expected_labels)}.")
    return frame


def tokenized_dataset(frame: pd.DataFrame, tokenizer) -> Dataset:
    dataset = Dataset.from_pandas(frame, preserve_index=False)
    dataset = dataset.map(
        lambda batch: tokenizer(batch["text"], truncation=True, max_length=MAX_LENGTH),
        batched=True,
    )
    dataset = dataset.remove_columns(["text"])
    dataset.set_format(type="torch")
    return dataset


def metric_function(label_ids: list[int]):
    def compute(prediction) -> dict[str, float]:
        labels = prediction.label_ids
        predicted = np.asarray(prediction.predictions).argmax(-1)
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predicted, labels=label_ids, average="macro", zero_division=0
        )
        return {
            "accuracy": float(accuracy_score(labels, predicted)),
            "precision_macro": float(precision),
            "recall_macro": float(recall),
            "f1_macro": float(f1),
        }
    return compute


def training_args(output_dir: Path, run_name: str):
    from transformers import TrainingArguments
    return TrainingArguments(
        output_dir=str(output_dir),
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        gradient_accumulation_steps=2,
        num_train_epochs=2,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        save_total_limit=2,
        fp16=True,
        seed=SEED,
        data_seed=SEED,
        report_to="none",
        run_name=run_name,
    )


def run_stage_a() -> Path:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, revision=BASE_MODEL_REVISION)
    train = read_csv(DATA_DIR / "sentiment140_train.csv", {0, 1})
    validation = read_csv(DATA_DIR / "sentiment140_validation.csv", {0, 1})
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
        num_labels=2,
        id2label={0: "negative", 1: "positive"},
        label2id={"negative": 0, "positive": 1},
    )
    trainer = Trainer(
        model=model,
        args=training_args(STAGE_A_DIR, "sentiment140-binary-adaptation"),
        train_dataset=tokenized_dataset(train, tokenizer),
        eval_dataset=tokenized_dataset(validation, tokenizer),
        processing_class=tokenizer,
        compute_metrics=metric_function([0, 1]),
    )
    trainer.train()
    trainer.save_model(str(STAGE_A_DIR))
    tokenizer.save_pretrained(str(STAGE_A_DIR))
    return STAGE_A_DIR


def run_stage_b(stage_a_dir: Path = STAGE_A_DIR) -> dict:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer
    if not stage_a_dir.is_dir():
        raise FileNotFoundError(f"Missing Stage A model at {stage_a_dir}. Run Stage A first.")
    tokenizer = AutoTokenizer.from_pretrained(stage_a_dir)
    train = read_csv(DATA_DIR / "train.csv", set(LABEL_NAMES))
    validation = read_csv(DATA_DIR / "val.csv", set(LABEL_NAMES))
    test = read_csv(DATA_DIR / "test.csv", set(LABEL_NAMES))
    model = AutoModelForSequenceClassification.from_pretrained(
        stage_a_dir,
        num_labels=3,
        id2label=LABEL_NAMES,
        label2id={label: index for index, label in LABEL_NAMES.items()},
        ignore_mismatched_sizes=True,
    )
    trainer = Trainer(
        model=model,
        args=training_args(STAGE_B_DIR, "tweet-eval-three-class-finetune"),
        train_dataset=tokenized_dataset(train, tokenizer),
        eval_dataset=tokenized_dataset(validation, tokenizer),
        processing_class=tokenizer,
        compute_metrics=metric_function(sorted(LABEL_NAMES)),
    )
    trainer.train()
    trainer.save_model(str(STAGE_B_DIR))
    tokenizer.save_pretrained(str(STAGE_B_DIR))
    output = trainer.predict(tokenized_dataset(test, tokenizer))
    predicted = output.predictions.argmax(-1)
    report = {
        "stage_a_model": str(stage_a_dir),
        "stage_b_model": str(STAGE_B_DIR),
        "tweet_eval_test": classification_report(
            output.label_ids, predicted, labels=sorted(LABEL_NAMES),
            target_names=[LABEL_NAMES[index] for index in sorted(LABEL_NAMES)],
            output_dict=True, zero_division=0,
        ),
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "staged_training_metrics.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("a", "b", "all"), default="all")
    args = parser.parse_args()
    if args.stage in {"a", "all"}:
        run_stage_a()
    if args.stage in {"b", "all"}:
        print(json.dumps(run_stage_b(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
