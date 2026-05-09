import pandas as pd
import pickle
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# -------------------------------
# 1. PATHS
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_data.csv"
VECTORIZER_PATH = BASE_DIR / "models" / "tfidf_vectorizer.pkl"
MODEL_PATH = BASE_DIR / "models" / "sentiment_model.pkl"

# -------------------------------
# 2. LOAD DATA
# -------------------------------
print("📂 Loading dataset...")
df = pd.read_csv(DATA_PATH)

print(f"📊 Dataset shape: {df.shape}")

X_text = df["clean_text"].astype(str)
y = df["sentiment"]

# -------------------------------
# 3. LOAD VECTORIZER
# -------------------------------
print("📦 Loading TF-IDF vectorizer...")
with open(VECTORIZER_PATH, "rb") as f:
    vectorizer = pickle.load(f)

# Transform text
X = vectorizer.transform(X_text)

print(f"✅ TF-IDF transformed: {X.shape}")

# -------------------------------
# 4. TRAIN / TEST SPLIT
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# -------------------------------
# 5. MODEL (OPTIMIZED)
# -------------------------------
print("🚀 Training Logistic Regression model...")

model = LogisticRegression(
    max_iter=200,
    C=2.0,              # stronger learning
    n_jobs=-1           # use all CPU cores
)

model.fit(X_train, y_train)

# -------------------------------
# 6. EVALUATION
# -------------------------------
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n🎯 Accuracy:", accuracy)
print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

# -------------------------------
# 7. SAVE MODEL
# -------------------------------
with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print(f"\n💾 Model saved at: {MODEL_PATH}")