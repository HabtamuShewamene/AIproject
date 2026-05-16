import pandas as pd
import torch
from datasets import Dataset
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    TrainingArguments,
    Trainer
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# -----------------------
# DEVICE (GPU CHECK)
# -----------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("🚀 Using device:", device)

# -----------------------
# PATHS (COLAB FRIENDLY)
# -----------------------
TRAIN_PATH = "train.csv"
VAL_PATH   = "val.csv"
MODEL_DIR  = "./bert_sentiment"

# -----------------------
# LOAD DATA
# -----------------------
def load_data():
    print("📂 Loading datasets...")

    train_df = pd.read_csv(TRAIN_PATH)
    val_df   = pd.read_csv(VAL_PATH)

    print(f"Train size: {len(train_df)}")
    print(f"Val size: {len(val_df)}")

    # 🔥 IMPORTANT: Reduce for first run (avoid crash)
    train_df = train_df.sample(200000, random_state=42)
    val_df   = val_df.sample(50000, random_state=42)

    return train_df, val_df

# -----------------------
# CONVERT TO HF DATASET
# -----------------------
def to_dataset(df):
    return Dataset.from_pandas(df)

# -----------------------
# TOKENIZER
# -----------------------
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )

# -----------------------
# METRICS
# -----------------------
def compute_metrics(pred):
    labels = pred.label_ids
    preds  = pred.predictions.argmax(-1)

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="binary"
    )
    acc = accuracy_score(labels, preds)

    return {
        "accuracy": acc,
        "f1": f1,
        "precision": precision,
        "recall": recall
    }

# -----------------------
# MAIN TRAINING
# -----------------------
def main():
    train_df, val_df = load_data()

    # Convert to datasets
    train_ds = to_dataset(train_df)
    val_ds   = to_dataset(val_df)

    # Tokenize
    print("🔄 Tokenizing...")
    train_ds = train_ds.map(tokenize, batched=True)
    val_ds   = val_ds.map(tokenize, batched=True)

    # Remove unnecessary columns
    train_ds = train_ds.remove_columns(["text"])
    val_ds   = val_ds.remove_columns(["text"])

    # Set format for PyTorch
    train_ds.set_format(type="torch")
    val_ds.set_format(type="torch")

    # Load model
    print("🧠 Loading BERT model...")
    model = BertForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        num_labels=2
    ).to(device)

    # -----------------------
    # TRAINING CONFIG (OPTIMIZED)
    # -----------------------
    training_args = TrainingArguments(
        output_dir=MODEL_DIR,
        eval_strategy="epoch",        # ✅ new syntax
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=32,   # 🚀 larger for GPU
        per_device_eval_batch_size=32,
        num_train_epochs=2,
        weight_decay=0.01,
        logging_steps=100,
        fp16=True,                   # 🚀 GPU acceleration
        load_best_model_at_end=True,
        metric_for_best_model="f1"
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    # Train
    print("🚀 Training started...")
    trainer.train()

    # Save model
    trainer.save_model(MODEL_DIR)
    print(f"💾 Model saved at: {MODEL_DIR}")

    # Evaluate
    print("📊 Evaluating...")
    results = trainer.evaluate()
    print(results)

# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    main()