import time

from app.predictor import predict_sentiment
from tests.multilingual_test_cases import TEST_CASES


def benchmark():

    start = time.time()

    for item in TEST_CASES:

        predict_sentiment(item["text"])

    end = time.time()

    total = end - start

    avg = total / len(TEST_CASES)

    print("\n===== SPEED TEST =====")
    print(f"Total Time: {total:.4f}s")
    print(f"Average Per Prediction: {avg:.4f}s")


if __name__ == "__main__":
    benchmark()