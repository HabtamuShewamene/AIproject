import importlib
import sys
from types import ModuleType

from fastapi.testclient import TestClient


def load_app_with_stubs():
    predictor_module = ModuleType("app.predictor")
    twitter_module = ModuleType("app.twitter_client")

    predictor_module.predict_sentiment = lambda text: {
        "original_text": text,
        "translated_text": text.upper(),
        "language": "en",
        "sentiment": "positive",
        "confidence": 0.99,
    }
    twitter_module.fetch_tweet = lambda url: {
        "text": "tweet body",
        "language": "en",
        "likes": 4,
        "retweets": 3,
        "replies": 2,
        "quotes": 1,
    }

    sys.modules["app.predictor"] = predictor_module
    sys.modules["app.twitter_client"] = twitter_module
    sys.modules.pop("app.main", None)

    return importlib.import_module("app.main")


def test_root_endpoint_returns_running_message():
    app_main = load_app_with_stubs()
    client = TestClient(app_main.app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Sentiment API is running"}


def test_predict_endpoint_returns_mocked_prediction():
    app_main = load_app_with_stubs()
    client = TestClient(app_main.app)

    response = client.post("/predict", json={"text": "great job"})

    assert response.status_code == 200
    assert response.json()["sentiment"] == "positive"
    assert response.json()["translated_text"] == "GREAT JOB"


def test_analyze_twitter_endpoint_returns_tweet_and_metrics():
    app_main = load_app_with_stubs()
    client = TestClient(app_main.app)

    response = client.post(
        "/analyze-twitter",
        json={"url": "https://twitter.com/example/status/123"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "tweet_text": "tweet body",
        "translated_text": "TWEET BODY",
        "language": "en",
        "metrics": {
            "likes": 4,
            "retweets": 3,
            "replies": 2,
            "quotes": 1,
        },
        "sentiment": "positive",
        "confidence": 0.99,
    }


def test_analyze_twitter_endpoint_returns_error_when_tweet_missing():
    predictor_module = ModuleType("app.predictor")
    twitter_module = ModuleType("app.twitter_client")

    predictor_module.predict_sentiment = lambda text: {
        "original_text": text,
        "translated_text": text,
        "language": "en",
        "sentiment": "positive",
        "confidence": 0.99,
    }
    twitter_module.fetch_tweet = lambda _url: None

    sys.modules["app.predictor"] = predictor_module
    sys.modules["app.twitter_client"] = twitter_module
    sys.modules.pop("app.main", None)

    app_main = importlib.import_module("app.main")
    client = TestClient(app_main.app)

    response = client.post(
        "/analyze-twitter",
        json={"url": "https://twitter.com/example/status/123"},
    )

    assert response.status_code == 200
    assert response.json() == {"error": "Could not fetch tweet"}
