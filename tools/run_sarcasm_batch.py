from app.predictor import predict_sentiment


SAMPLES = [
    "Oh fantastic, the app crashed right before I submitted everything.",
    "Love that for me, spending my evening fixing the same bug again.",
    "Yeah, this is exactly what I needed today.",
    "Amazing performance as usual, nothing broken at all.",
    "Great job, the one thing that had to work definitely didn't.",
    "Perfect timing. Really couldn't have gone worse.",
    "What a brilliant idea, let's do the same thing that failed last time.",
    "I'm thrilled that it chose this exact moment to stop working.",
    "Sure, because waiting longer always makes things better.",
    "Excellent, now I get to debug this masterpiece again.",
    "Well done, the only button I needed is still useless.",
    "How lovely, another update that fixes nothing.",
    "This is going so well, I can barely contain my excitement.",
    "Incredible, it broke in a completely new and creative way.",
    "Fantastic, now I can enjoy the joy of redoing all my work.",
]


def main():
    for i, text in enumerate(SAMPLES, 1):
        result = predict_sentiment(text)
        print(f"{i}. {result['sentiment']} | {result['confidence']:.4f} | {result['translated_text']}")


if __name__ == "__main__":
    main()
