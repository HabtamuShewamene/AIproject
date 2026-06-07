from app.predictor import predict_sentiment
from tests.multilingual_test_cases import TEST_CASES


def analyze():

    print("\n===== CONFIDENCE TEST =====\n")

    for item in TEST_CASES:

        result = predict_sentiment(item["text"])

        print(
            f"{item['text'][:50]}"
            f"\nPrediction: {result['sentiment']}"
            f"\nConfidence: {result['confidence']}"
            f"\n"
        )


if __name__ == "__main__":
    analyze()