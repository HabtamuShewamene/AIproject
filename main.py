#!/usr/bin/env python3
"""
Main entry point for sentiment analysis pipeline
"""
import sys
from src.preprocessing import preprocess_text
from src.vectorizer import load_vectorizer
from src.predict_bert import predict_sentiment

def main():
    """Run sentiment analysis pipeline"""
    print("Sentiment Analysis Pipeline v1.0")
    
    # Load models
    vectorizer = load_vectorizer()
    
    # Example prediction
    text = "This product is amazing!"
    prediction = predict_sentiment(text, vectorizer)
    print(f"Text: {text}")
    print(f"Sentiment: {prediction}")

if __name__ == "__main__":
    main()
