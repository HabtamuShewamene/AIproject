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

- Python 3.11–3.13
- FastAPI and Uvicorn
- Hugging Face Transformers and PyTorch
- pandas, NumPy, scikit-learn, and Hugging Face Datasets
- Apify client for the current social collection adapter
- `uv` and `pyproject.toml` for environment and dependency management

## Project Structure

- `app/`: API application and inference helpers
- `src/`: preprocessing, dataset split, and training scripts
- `data/`: raw and processed datasets
- `models/`: saved model artifacts
- `results/`: evaluation outputs
- `notebooks/`: exploration notebook

## Installation

Install `uv` if it is not already available, then create the project environment and install the development dependencies from the project configuration:

```bash
python -m pip install uv
uv sync --extra dev
```

The project targets Python 3.11–3.13. `pyproject.toml` defines the supported dependency ranges; `uv.lock` is the intended exact resolution for repeatable installs. Until that lockfile is generated and committed, dependency resolution can vary and this setup is not yet fully reproducible.

For a non-editable pip installation, use `pip install -e ".[dev]"` from the project root. The legacy `requirements.txt` remains during this migration and is not the authoritative dependency definition.

## Environment Variables

Copy `.env.example` to `.env` for local development. Keep real credentials only in the ignored local file or a secret manager; never commit them.

```bash
cp .env.example .env
```

On PowerShell, use `Copy-Item .env.example .env`.

`MODEL_PATH` points to a locally available fine-tuned Transformers model. `APIFY_TOKEN` and `TWITTER_COOKIE` are only needed for the current Apify-based collection path. The model and dataset are not included in this checkout; `/predict` cannot return a real model prediction until a compatible model artifact is supplied.

## Run the API

From the project root:

```bash
uv run uvicorn app.main:app --reload
```

The API will start locally at:

```text
http://127.0.0.1:8000
```

Interactive docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Run the test suite with:

```bash
uv run pytest -q
```

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
