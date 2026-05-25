from fastapi import FastAPI
from pydantic import BaseModel

from app.predictor import predict_sentiment
from app.twitter_client import fetch_tweet


app = FastAPI(
    title="AI Sentiment Analysis API"
)


# -----------------------------
# REQUEST MODELS
# -----------------------------
class TextRequest(BaseModel):
    text: str


class TwitterRequest(BaseModel):
    url: str


# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "Sentiment API is running"
    }


# -----------------------------
# TEXT PREDICTION
# -----------------------------
@app.post("/predict")
def predict(data: TextRequest):

    result = predict_sentiment(data.text)

    return result


# -----------------------------
# TWITTER ANALYSIS
# -----------------------------
@app.post("/analyze-twitter")
def analyze_twitter(data: TwitterRequest):

    tweet = fetch_tweet(data.url)

    if not tweet:
        return {
            "error": "Could not fetch tweet"
        }

    sentiment_result = predict_sentiment(tweet["text"])

    return {
        "tweet_text": tweet["text"],
        "translated_text": sentiment_result["translated_text"],
        "language": tweet["language"],

        "metrics": {
            "likes": tweet["likes"],
            "retweets": tweet["retweets"],
            "replies": tweet["replies"],
            "quotes": tweet["quotes"]
        },

        "sentiment": sentiment_result["sentiment"],
        "confidence": sentiment_result["confidence"]
    }