# Sentiment Analysis Pipeline

This project is a sentiment analysis system built around a fine-tuned BERT model and exposed through a FastAPI service. It supports direct text classification, multilingual input via translation to English, and tweet analysis from Twitter/X URLs.

## Features

- BERT-based sentiment classification
- Sentiment140 dataset preprocessing and train/validation/test splitting
- Fine-tuning pipeline for `bert-base-uncased`
- FastAPI inference API
- Multilingual input handling with automatic translation
- Twitter/X tweet lookup and sentiment analysis
- Saved model artifacts and evaluation results

## Tech Stack

- FastAPI
- Transformers
- PyTorch
- scikit-learn
- pandas
- Tweepy

## Project Structure

- `app/`: API application and inference helpers
- `src/`: preprocessing, dataset split, and training scripts
- `data/`: raw and processed datasets
- `models/`: saved model artifacts
- `results/`: evaluation outputs
- `notebooks/`: exploration notebook

## Installation

Create and activate a virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root if you want to use Twitter/X analysis:

```env
TWITTER_BEARER_TOKEN=your_token_here
MODEL_PATH=models/bert_sentiment
```

`MODEL_PATH` is optional because the app already defaults to `models/bert_sentiment`.

## Run the API

From the project root:

```bash
uvicorn app.main:app --reload
```

The API will start locally at:

```text
http://127.0.0.1:8000
```

Interactive docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

### `GET /`

Health-style root endpoint.

Response example:

```json
{
  "message": "Sentiment API is running"
}
```

### `POST /predict`

Predicts sentiment for input text.

Request body:

```json
{
  "text": "I really enjoyed this product."
}
```

Response example:

```json
{
  "original_text": "I really enjoyed this product.",
  "translated_text": "I really enjoyed this product.",
  "language": "en",
  "sentiment": "positive",
  "confidence": 0.9876
}
```

### `POST /analyze-twitter`

Fetches a tweet from a Twitter/X URL and runs sentiment analysis on the tweet text.

Request body:

```json
{
  "url": "https://twitter.com/user/status/1234567890"
}
```

Response example:

```json
{
  "tweet_text": "Sample tweet text",
  "translated_text": "Sample tweet text",
  "language": "en",
  "metrics": {
    "likes": 10,
    "retweets": 2,
    "replies": 1,
    "quotes": 0
  },
  "sentiment": "positive",
  "confidence": 0.9543
}
```

## Training Workflow

The training pipeline is split into separate scripts:

1. `src/preprocessing.py`
   Cleans the raw Sentiment140 dataset and saves `data/processed/clean_data.csv`.
2. `src/split_dataset.py`
   Splits the cleaned data into `train.csv`, `val.csv`, and `test.csv`.
3. `src/bert_train.py`
   Fine-tunes the BERT model and saves artifacts to `models/bert_sentiment`.

## Model Performance

The current recorded evaluation in `results/metrics.txt` reports:

- Accuracy: `0.8756`
- Precision: `0.8823`
- Recall: `0.8701`
- F1-score: `0.8761`

## Notes

- The inference app currently maps BERT labels to `negative` and `positive`.
- Some legacy files suggest an older TF-IDF direction, but the active app path is centered on the saved BERT model.
- Twitter/X analysis requires a valid bearer token and network access when the app is run outside this environment.
