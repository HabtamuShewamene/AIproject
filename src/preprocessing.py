import pandas as pd
import re
from sklearn.utils import shuffle
from pathlib import Path

# -----------------------
# PATHS
# -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "training.1600000.processed.noemoticon.csv"
OUT_PATH = BASE_DIR / "data" / "processed" / "clean_data.csv"

# -----------------------
# CLEAN TEXT (BERT-OPTIMIZED)
# -----------------------
def clean_text(text):
    if pd.isna(text):
        return ""

    text = str(text)

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)

    # Remove mentions
    text = re.sub(r"@\w+", "", text)

    # Remove hashtag symbol ONLY (keep word)
    text = re.sub(r"#", "", text)

    # Keep letters, numbers, punctuation (important for sentiment)
    text = re.sub(r"[^a-zA-Z0-9\s.,!?']", "", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

# -----------------------
# LOAD DATA
# -----------------------
def load_data():
    print("📂 Loading Sentiment140...")

    # Original dataset has NO header
    df = pd.read_csv(
        RAW_PATH,
        encoding="latin-1",
        header=None,
        low_memory=False
    )

    # Assign correct column names
    df.columns = ["target", "id", "date", "flag", "user", "text"]

    print(f"📊 Raw shape: {df.shape}")
    print(df.head(3))

    return df

# -----------------------
# PREPROCESS
# -----------------------
def preprocess(df):
    print("🧹 Cleaning data...")

    # Keep only required columns
    df = df[["target", "text"]].copy()

    # Keep valid labels only
    df = df[df["target"].isin([0, 4])]

    # Convert labels → 0 / 1
    df["label"] = df["target"].apply(lambda x: 0 if x == 0 else 1)

    # Drop missing text
    df = df.dropna(subset=["text"])

    # Ensure string
    df["text"] = df["text"].astype(str)

    # Apply cleaning
    df["text"] = df["text"].apply(clean_text)

    # Remove empty rows (SAFE)
    df = df[df["text"].notna()]
    df = df[df["text"].str.strip() != ""]

    # ⚠️ Keep duplicates for model strength (important for deep learning)
    # df = df.drop_duplicates(subset=["text"])

    # Shuffle dataset
    df = shuffle(df, random_state=42)

    # Final format
    df = df[["text", "label"]]

    print(f"✅ Final dataset shape: {df.shape}")
    print(df.head(5))
    print("\n📊 Label distribution:")
    print(df["label"].value_counts())

    return df

# -----------------------
# SAVE
# -----------------------
def save_data(df):
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"💾 Saved to: {OUT_PATH}")

# -----------------------
# MAIN
# -----------------------
def main():
    df = load_data()
    df_clean = preprocess(df)
    save_data(df_clean)
    print("🚀 Preprocessing completed successfully!")

if __name__ == "__main__":
    main()

# Commit marker: non-empty edit 2 - harmless comment added for commit tracking