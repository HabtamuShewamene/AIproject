import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

from app.predictor import predict_sentiment


print("Loading dataset...")

df = pd.read_csv("data/processed/test.csv")

# optional: test first 1000 rows initially
df = df.head(1000)

y_true = []
y_pred = []

for _, row in df.iterrows():

    text = str(row["text"])
    label = int(row["label"])

    try:
        result = predict_sentiment(text)

        sentiment = result["sentiment"]

        predicted_label = (
            1 if sentiment == "positive"
            else 0
        )

        y_true.append(label)
        y_pred.append(predicted_label)

    except Exception as e:
        print("ERROR:", e)

accuracy = accuracy_score(
    y_true,
    y_pred
)

precision, recall, f1, _ = (
    precision_recall_fscore_support(
        y_true,
        y_pred,
        average="binary"
    )
)

print("\n========== RESULTS ==========")

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")

print("\nConfusion Matrix")
print(confusion_matrix(y_true, y_pred))

print("\nClassification Report")
print(
    classification_report(
        y_true,
        y_pred
    )
)