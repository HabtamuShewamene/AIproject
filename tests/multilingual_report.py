from app.predictor import predict_sentiment
from tests.multilingual_test_cases import TEST_CASES


def run_report():

    correct = 0

    total = len(TEST_CASES)

    print("\n===== MULTILINGUAL REPORT =====\n")

    for item in TEST_CASES:

        result = predict_sentiment(item["text"])

        predicted = result["sentiment"]

        expected = item["expected"]

        if predicted == expected:
            correct += 1

        print("-" * 60)

        print("TEXT:")
        print(item["text"])

        print("EXPECTED:")
        print(expected)

        print("PREDICTED:")
        print(predicted)

        print("CONFIDENCE:")
        print(result["confidence"])

    accuracy = correct / total * 100

    print("\n" + "=" * 60)

    print(f"TOTAL: {total}")
    print(f"CORRECT: {correct}")
    print(f"ACCURACY: {accuracy:.2f}%")

    print("=" * 60)


if __name__ == "__main__":
    run_report()