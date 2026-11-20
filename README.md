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
uv sync --locked --extra dev
```

The project targets Python 3.11–3.13. `pyproject.toml` defines the supported dependency ranges, and the committed `uv.lock` pins the resolved dependency graph. Use `uv sync --locked` to install exactly that graph and fail if the metadata and lockfile drift.

For a pip-based editable install, use `pip install -r requirements.txt`; this compatibility path follows the dependency ranges and does not enforce the lockfile. Use `uv` when exact locked versions are required.

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

The current training path uses the pinned English TweetEval sentiment subset with negative, neutral, and positive labels:

1. Fetch and validate the pinned splits:

   ```bash
   uv run python -m src.download_tweet_eval
   ```

   This writes ignored CSVs under `data/processed/` and a text-free provenance/statistics manifest to `results/tweet_eval_manifest.json`. It preserves the official train, validation, and test partitions.

2. Fine-tune and evaluate the three-class model:

   ```bash
   uv run python -m src.bert_train
   ```

   The best validation checkpoint is saved under `models/bert_sentiment`; final validation and held-out test metrics are written to `results/bert_tweeteval_metrics.json`.

The older `src/preprocessing.py` and `src/split_dataset.py` scripts apply to the historical binary Sentiment140 path and are not part of this three-class workflow.

## Historical Model Metrics

`results/metrics.txt` and `results/confusion_matrix.png` are historical artifacts. Their reported three-class results do not match the former two-class training code and are not verified release metrics. Use the generated TweetEval manifest and evaluation report for new runs.

## Notes

- The current prediction path still expects a locally available model and maps only negative/positive; three-class serving integration is a later phase.
- The candidate evaluation baseline is pinned separately in the Phase 2 audit; it has not yet been downloaded or benchmarked locally.
- X/Twitter collection requires Apify credentials, network access, and compliance with the relevant platform terms.
