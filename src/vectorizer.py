import pandas as pd
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer

# -------------------------------
# 1. PATH SETUP (FIXED)
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_data.csv"
VECTORIZER_PATH = BASE_DIR / "models" / "tfidf_vectorizer.pkl"

# Create models folder if not exists
VECTORIZER_PATH.parent.mkdir(parents=True, exist_ok=True)

# -------------------------------
# 2. LOAD DATA
# -------------------------------
print("📂 Loading cleaned dataset...")
df = pd.read_csv(DATA_PATH)

print(f"📊 Loaded dataset shape: {df.shape}")

# Ensure correct column
if "clean_text" not in df.columns:
    raise ValueError("❌ 'clean_text' column not found in dataset")

texts = df["clean_text"].astype(str)

# -------------------------------
# 3. TF-IDF VECTORIZER (OPTIMIZED)
# -------------------------------
print("⚙️ Building TF-IDF vectorizer...")

vectorizer = TfidfVectorizer(
    max_features=10000,      # ↑ better accuracy than 5000
    ngram_range=(1, 2),      # unigrams + bigrams (VERY IMPORTANT)
    min_df=5,                # remove rare noise
    max_df=0.8,              # remove overly common words
    sublinear_tf=True        # improves performance
)

# -------------------------------
# 4. TRANSFORM TEXT
# -------------------------------
print("🔄 Transforming text to vectors...")

X = vectorizer.fit_transform(texts)

print(f"✅ TF-IDF shape: {X.shape}")

# -------------------------------
# 5. SAVE VECTORIZER
# -------------------------------
with open(VECTORIZER_PATH, "wb") as f:
    pickle.dump(vectorizer, f)

print(f"💾 Vectorizer saved at: {VECTORIZER_PATH}")

# -------------------------------
# 6. OPTIONAL: SAVE FEATURES (for debugging)
# -------------------------------
# WARNING: large file (~GB), only use if needed
# import scipy.sparse
# scipy.sparse.save_npz(BASE_DIR / "data" / "processed" / "X_tfidf.npz", X)

print("✅ VECTORIZATION COMPLETE")