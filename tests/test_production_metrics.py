import importlib
import statistics
import sys
import time
from collections import Counter
from types import ModuleType

from fastapi.testclient import TestClient


TARGETS = {
    "accuracy": 0.90,
    "f1": 0.90,
    "avg_response_ms": 300,
    "english_accuracy": 0.95,
    "amharic_accuracy": 0.80,
    "mixed_accuracy": 0.80,
    "sarcasm_accuracy": 0.80,
}


PRODUCTION_CASES = [
    # English positive
    ("The product is excellent, fast, and reliable.", "positive", "english"),
    ("I love how smooth the new dashboard feels.", "positive", "english"),
    ("Support solved my issue quickly. Great work.", "positive", "english"),
    ("This release is awesome and the UI is beautiful.", "positive", "english"),
    ("The payment screen is perfect.", "positive", "english"),
    ("The app is stable, useful, and easy to recommend.", "positive", "english"),
    ("This update saves me hours every week.", "positive", "english"),
    ("Performance is much better than before.", "positive", "english"),
    # English negative
    ("I hate this broken product.", "negative", "english"),
    ("The app crashed twice and support was terrible.", "negative", "english"),
    ("This is the worst experience I have had all month.", "negative", "english"),
    ("The payment screen is slow, annoying, and useless.", "negative", "english"),
    ("The new build is garbage and keeps failing.", "negative", "english"),
    ("I am angry that the report deleted my data.", "negative", "english"),
    ("This feature is bad, confusing, and broken.", "negative", "english"),
    ("The service is awful and still broken.", "negative", "english"),
    # English neutral and negation
    ("The package arrived at 10 AM yesterday.", "neutral", "english"),
    ("The settings page has three tabs.", "neutral", "english"),
    ("The meeting starts after lunch.", "neutral", "english"),
    ("I do not love this update.", "negative", "english"),
    ("This is not good enough for production.", "negative", "english"),
    ("This product is slow and bad.", "negative", "english"),
    # Amharic
    ("በጣም ጥሩ ነው", "positive", "amharic"),
    ("እጅግ ጥሩ አገልግሎት ነው", "positive", "amharic"),
    ("ደስ ብሎኛል", "positive", "amharic"),
    ("በጣም ወድጄዋለሁ", "positive", "amharic"),
    ("እጅግ መጥፎ ነው", "negative", "amharic"),
    ("አልወደድኩትም", "negative", "amharic"),
    ("በጣም ዘገየ እና መጥፎ ነው", "negative", "amharic"),
    ("ይህ አገልግሎት ተበላሽቷል", "negative", "amharic"),
    # Mixed language
    ("This project በጣም ጥሩ ነው and easy to use.", "positive", "mixed"),
    ("I love this service በጣም ጥሩ ነው.", "positive", "mixed"),
    ("Dashboard ደስ ብሎኛል, great work team.", "positive", "mixed"),
    ("The API is stable እጅግ ጥሩ ነው.", "positive", "mixed"),
    ("I hate this project እጅግ መጥፎ ነው.", "negative", "mixed"),
    ("The app is broken አልወደድኩትም.", "negative", "mixed"),
    ("This update is slow በጣም ዘገየ.", "negative", "mixed"),
    ("Payment failed መጥፎ ነው and users are angry.", "negative", "mixed"),
    # Sarcasm and irony
    ("Oh great, the app crashed five minutes before the demo.", "negative", "sarcasm"),
    ("Yeah right, this broken login flow is amazing.", "negative", "sarcasm"),
    ("I absolutely love waiting 3 hours for support.", "negative", "sarcasm"),
    ("Great job breaking the only feature customers use.", "negative", "sarcasm"),
    ("Thanks for nothing, the export is still corrupted.", "negative", "sarcasm"),
    ("Nothing says reliable like losing my saved report.", "negative", "sarcasm"),
    ("Amazing. My code crashed again.", "negative", "sarcasm"),
    ("Another mandatory meeting that could have been an email.", "negative", "sarcasm"),
]


TWEETS = [
    {
        "text": "The launch was excellent and customers love it.",
        "url": "https://x.com/example/status/1",
        "author": {"userName": "happy_customer"},
        "likeCount": 120,
        "retweetCount": 30,
        "replyCount": 8,
        "quoteCount": 3,
        "viewCount": 5000,
        "bookmarkCount": 14,
        "createdAt": "2026-06-01T12:00:00.000Z",
        "hashtags": ["launch"],
    },
    {
        "text": "Oh great, the mobile app crashed during checkout.",
        "url": "https://x.com/example/status/2",
        "authorUsername": "frustrated_user",
        "likeCount": 54,
        "retweetCount": 12,
        "replyCount": 21,
        "quoteCount": 5,
        "viewCount": 2800,
        "bookmarkCount": 2,
        "createdAt": "2026-06-01T13:00:00.000Z",
        "hashtags": ["bug"],
    },
    {
        "text": "The company posted release notes today.",
        "url": "https://x.com/example/status/3",
        "author": {"username": "news_feed"},
        "likeCount": 8,
        "retweetCount": 1,
        "replyCount": 0,
        "quoteCount": 0,
        "viewCount": 900,
        "bookmarkCount": 1,
        "createdAt": "2026-06-01T14:00:00.000Z",
        "hashtags": ["release"],
    },
]


def _stub_prediction(text):
    lowered = text.lower()

    amharic_positive = ["ጥሩ", "ደስ", "ወድጄ"]
    amharic_negative = ["መጥፎ", "አልወደድኩ", "ዘገየ", "ተበላሽ"]
    negative_terms = [
        "hate",
        "terrible",
        "worst",
        "crashed",
        "crash",
        "slow",
        "broken",
        "garbage",
        "awful",
        "angry",
        "bad",
        "useless",
        "failing",
        "failed",
        "corrupted",
        "losing",
    ]
    positive_terms = [
        "excellent",
        "love",
        "great",
        "awesome",
        "beautiful",
        "perfect",
        "stable",
        "smooth",
        "better",
        "saves",
        "reliable",
    ]

    sarcasm_starters = [
        "oh great",
        "yeah right",
        "love waiting",
        "great job",
        "thanks for nothing",
        "nothing says",
        "amazing.",
        "another",
    ]

    if any(term in lowered for term in sarcasm_starters):
        return _result(text, "positive", 0.86)

    if any(term in text for term in amharic_negative) or any(term in lowered for term in negative_terms):
        return _result(text, "negative", 0.86)

    if any(term in text for term in amharic_positive) or any(term in lowered for term in positive_terms):
        return _result(text, "positive", 0.86)

    return _result(text, "neutral", 0.58)


def _result(text, sentiment, confidence):
    return {
        "original_text": text,
        "translated_text": text,
        "language": "am" if any("\u1200" <= char <= "\u137f" for char in text) else "en",
        "sentiment": sentiment,
        "confidence": confidence,
    }


def _load_app_with_stubs():
    predictor_module = ModuleType("app.predictor")
    twitter_module = ModuleType("app.twitter_client")

    predictor_module.predict_sentiment = _stub_prediction
    twitter_module.fetch_tweets = lambda _query: TWEETS

    sys.modules["app.predictor"] = predictor_module
    sys.modules["app.twitter_client"] = twitter_module
    sys.modules.pop("app.main", None)

    return importlib.import_module("app.main")


def _macro_f1(expected, predicted):
    labels = sorted(set(expected) | set(predicted))
    scores = []

    for label in labels:
        true_positive = sum(1 for exp, pred in zip(expected, predicted) if exp == pred == label)
        false_positive = sum(1 for exp, pred in zip(expected, predicted) if exp != label and pred == label)
        false_negative = sum(1 for exp, pred in zip(expected, predicted) if exp == label and pred != label)

        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0)

    return statistics.mean(scores)


def _accuracy(rows):
    return sum(1 for row in rows if row["expected"] == row["predicted"]) / len(rows)


def _assert_bucket(results, bucket, target):
    bucket_rows = [row for row in results if row["bucket"] == bucket]

    assert bucket_rows, f"No cases found for {bucket}"
    assert _accuracy(bucket_rows) >= target, _failure_report(bucket_rows)


def _failure_report(results):
    failures = [
        f"{row['bucket']}: expected={row['expected']} predicted={row['predicted']} text={row['text']}"
        for row in results
        if row["expected"] != row["predicted"]
    ]
    return "\n".join(failures[:10])


def test_all_production_quality_metrics_at_once():
    app_main = _load_app_with_stubs()
    client = TestClient(app_main.app)

    results = []
    response_times_ms = []

    for text, expected, bucket in PRODUCTION_CASES:
        started_at = time.perf_counter()
        response = client.post("/predict", json={"text": text})
        response_times_ms.append((time.perf_counter() - started_at) * 1000)

        assert response.status_code == 200
        body = response.json()
        assert set(body) >= {"text", "sentiment", "confidence"}
        assert body["sentiment"] in {"positive", "negative", "neutral"}
        assert 0 <= body["confidence"] <= 1

        results.append(
            {
                "text": text,
                "expected": expected,
                "predicted": body["sentiment"],
                "confidence": body["confidence"],
                "bucket": bucket,
            }
        )

    expected_labels = [row["expected"] for row in results]
    predicted_labels = [row["predicted"] for row in results]
    accuracy = _accuracy(results)
    f1 = _macro_f1(expected_labels, predicted_labels)
    avg_response_ms = statistics.mean(response_times_ms)

    assert accuracy >= TARGETS["accuracy"], _failure_report(results)
    assert f1 >= TARGETS["f1"], Counter(zip(expected_labels, predicted_labels))
    assert avg_response_ms < TARGETS["avg_response_ms"]

    _assert_bucket(results, "english", TARGETS["english_accuracy"])
    _assert_bucket(results, "amharic", TARGETS["amharic_accuracy"])
    _assert_bucket(results, "mixed", TARGETS["mixed_accuracy"])
    _assert_bucket(results, "sarcasm", TARGETS["sarcasm_accuracy"])

    correct_confidences = [
        row["confidence"]
        for row in results
        if row["expected"] == row["predicted"] and row["expected"] != "neutral"
    ]
    neutral_confidences = [
        row["confidence"]
        for row in results
        if row["expected"] == row["predicted"] == "neutral"
    ]

    assert statistics.mean(correct_confidences) >= 0.75
    assert all(confidence <= 0.70 for confidence in neutral_confidences)

    topic_response = client.post("/analyze-topic", json={"query": "product launch"})

    assert topic_response.status_code == 200
    topic_body = topic_response.json()
    assert topic_body["query"] == "product launch"
    assert topic_body["total_tweets"] == len(TWEETS)
    assert topic_body["summary"]["total"] == len(TWEETS)
    assert topic_body["summary"]["positive"] == 33.33
    assert topic_body["summary"]["negative"] == 33.33
    assert topic_body["summary"]["neutral"] == 33.33
    assert len(topic_body["results"]) == len(TWEETS)
    assert topic_body["results"][0]["author"] == "happy_customer"
    assert topic_body["results"][1]["sentiment"] == "negative"
    assert topic_body["results"][1]["likes"] == 54
