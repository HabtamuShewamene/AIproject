import pandas as pd
import re
from pathlib import Path
from sklearn.utils import shuffle

from src.enterprise_cleaner import clean_tweet_text, is_valid_tweet

# -----------------------
# PATHS
# -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "training.1600000.processed.noemoticon.csv"
OUT_PATH = BASE_DIR / "data" / "processed" / "clean_data.csv"


# -----------------------
# CLEAN TEXT (ENTERPRISE REFINED)
# -----------------------
def clean_text(text, strip_mentions: bool = True):
    if pd.isna(text) or text is None:
        return ""

    text = str(text)
    cleaned = clean_tweet_text(text, preserve_casing=False)

    if strip_mentions:
        cleaned = re.sub(r"@\w+", "", cleaned)
        cleaned = re.sub(r"[^a-zA-Z0-9\s.,!?']", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


# -----------------------
# LOAD DATA
# -----------------------
def load_data():
    print("📂 Loading Sentiment140...")
    df = pd.read_csv(
        RAW_PATH,
        encoding="latin-1",
        header=None,
        low_memory=False,
    )
    df.columns = ["target", "id", "date", "flag", "user", "text"]
    print(f"📊 Raw shape: {df.shape}")
    return df


# -----------------------
# PREPROCESS
# -----------------------
def preprocess(df):
    print("🧹 Cleaning data with enterprise rules...")
    df = df[["target", "text"]].copy()
    df = df[df["target"].isin([0, 4])]
    df["label"] = df["target"].apply(lambda x: 0 if x == 0 else 1)
    df = df.dropna(subset=["text"])
    df["text"] = df["text"].astype(str)
    df["text"] = df["text"].apply(clean_text)
    df = df[df["text"].notna()]
    df = df[df["text"].str.strip() != ""]
    df = shuffle(df, random_state=42)
    return df[["text", "label"]]


if __name__ == "__main__":
    raw_df = load_data()
    clean_df = preprocess(raw_df)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(OUT_PATH, index=False)
    print(f"✅ Saved cleaned dataset to {OUT_PATH}")
