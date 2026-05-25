from transformers import pipeline
from pathlib import Path

from app.translator import translate_to_english


# -----------------------------
# MODEL PATH
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "bert_sentiment"


# -----------------------------
# LOAD MODEL
# -----------------------------
classifier = pipeline(
    "sentiment-analysis",
    model=str(MODEL_PATH),
    tokenizer=str(MODEL_PATH)
)


# -----------------------------
# PREDICTION
# -----------------------------
def predict_sentiment(text):

    translated_text, language = translate_to_english(text)

    result = classifier(translated_text)[0]

    label_map = {
        "LABEL_0": "negative",
        "LABEL_1": "positive"
    }

    sentiment = label_map[result["label"]]

    confidence = round(result["score"], 4)

    return {
        "original_text": text,
        "translated_text": translated_text,
        "language": language,
        "sentiment": sentiment,
        "confidence": confidence
    }