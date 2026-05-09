import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

import torch
from torch.utils.data import Dataset

from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    Trainer,
    TrainingArguments
)

# -------------------------------
# 1. PATHS
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_data.csv"

# -------------------------------
# 2. LOAD DATA
# -------------------------------
print("📂 Loading dataset...")
df = pd.read_csv(DATA_PATH)

df = df.dropna()

# Ensure binary labels (0/1)
df["sentiment"] = df["sentiment"].astype(int)

print("📊 Shape:", df.shape)

# -------------------------------
# 3. TRAIN / TEST SPLIT
# -------------------------------
train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["clean_text"].tolist(),
    df["sentiment"].tolist(),
    test_size=0.2,
    random_state=42
)

# -------------------------------
# 4. TOKENIZER (BERT)
# -------------------------------
print("⚙️ Loading BERT tokenizer...")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# -------------------------------
# 5. DATASET CLASS
# -------------------------------
class SentimentDataset(Dataset):
    def __init__(self, texts, labels):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=128
        )
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

train_dataset = SentimentDataset(train_texts, train_labels)
val_dataset = SentimentDataset(val_texts, val_labels)

# -------------------------------
# 6. MODEL
# -------------------------------
print("🚀 Loading BERT model...")
model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=2
)

# -------------------------------
# 7. TRAINING SETTINGS
# -------------------------------
training_args = TrainingArguments(
    output_dir=str(BASE_DIR / "models" / "bert"),
    num_train_epochs=2,              # start small
    per_device_train_batch_size=8,   # adjust if slow
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir=str(BASE_DIR / "logs"),
    logging_steps=200,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    report_to="none"
)

# -------------------------------
# 8. TRAINER
# -------------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# -------------------------------
# 9. TRAIN
# -------------------------------
print("🔥 Training BERT model...")
trainer.train()

# -------------------------------
# 10. EVALUATION
# -------------------------------
print("📊 Evaluating...")

predictions = trainer.predict(val_dataset)
y_pred = np.argmax(predictions.predictions, axis=1)

print("\n🎯 Accuracy:", accuracy_score(val_labels, y_pred))
print("\n📊 Classification Report:\n")
print(classification_report(val_labels, y_pred))

# -------------------------------
# 11. SAVE MODEL
# -------------------------------
model.save_pretrained(BASE_DIR / "models" / "bert_model")
tokenizer.save_pretrained(BASE_DIR / "models" / "bert_model")

print("💾 BERT model saved!")