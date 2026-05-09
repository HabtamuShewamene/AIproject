import pandas as pd
import re
import nltk
import spacy
from nltk.corpus import stopwords
from sklearn.utils import shuffle
from pathlib import Path

# -----------------------
# PATHS
# -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "sentiment140.csv"
OUT_PATH = BASE_DIR / "data" / "processed" / "cleaned_data.csv"

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# -----------------------
# NLP SETUP
# -----------------------
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

print("⏳ Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")

# -----------------------
# LOAD DATA
# -----------------------
df = pd.read_csv(
    DATA_PATH,
    encoding="latin-1",
    header=None,
    low_memory=False
)

print("📊 Raw shape:", df.shape)

# -----------------------
# DETECT FORMAT
# -----------------------
if df.shape[1] == 6:
    print("✅ Sentiment140 format")

    df.columns = ['sentiment', 'id', 'date', 'query', 'user', 'text']

    df = df[['sentiment', 'text']]

    df['sentiment'] = df['sentiment'].replace({
        0: 0,
        4: 1
    })

elif df.shape[1] == 2:
    print("✅ Simple format")

    df.columns = ['text', 'sentiment']

    df = df[['sentiment', 'text']]

    df['sentiment'] = df['sentiment'].replace({
        0: 0,
        1: 1
    })

else:
    raise ValueError("❌ Unknown dataset format")

# -----------------------
# CLEANING FUNCTION
# -----------------------
def clean_text(text):

    if pd.isna(text):
        return ""

    text = text.lower()

    # remove urls
    text = re.sub(r'http\S+|www\S+', '', text)

    # remove mentions
    text = re.sub(r'@\w+', '', text)

    # remove hashtags symbol only
    text = re.sub(r'#', '', text)

    # remove non letters
    text = re.sub(r'[^a-z\s]', '', text)

    # remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # spaCy processing
    doc = nlp(text)

    words = []

    for token in doc:

        lemma = token.lemma_.strip()

        if (
            lemma not in stop_words
            and len(lemma) > 2
            and lemma.isalpha()
        ):
            words.append(lemma)

    return " ".join(words)

# -----------------------
# APPLY CLEANING
# -----------------------
print("⏳ Cleaning text...")

df['clean_text'] = df['text'].apply(clean_text)

# -----------------------
# REMOVE EMPTY ROWS
# -----------------------
df = df[df['clean_text'].str.len() > 0]

# minimum 2 words
df = df[df['clean_text'].str.split().str.len() >= 2]

df = df.dropna()

# -----------------------
# SHUFFLE
# -----------------------
df = shuffle(df, random_state=42)

# -----------------------
# SAVE
# -----------------------
df.to_csv(OUT_PATH, index=False)

# -----------------------
# OUTPUT
# -----------------------
print("\n✅ PREPROCESSING COMPLETE")

print(df[['sentiment', 'clean_text']].head())

print("\nFinal shape:", df.shape)

print("\n💾 Saved to:", OUT_PATH)