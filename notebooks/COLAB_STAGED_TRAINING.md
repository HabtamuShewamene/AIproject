# Google Colab staged training runbook

Use a GPU runtime in Colab: **Runtime → Change runtime type → T4 GPU** (or the available GPU). This document assumes a private GitHub repository and that the Sentiment140 archive has been uploaded to Google Drive.

## 1. Start the environment

```python
!pip install -q uv
!git clone https://github.com/HabtamuShewamene/AIproject.git
%cd AIproject
!git checkout phase/2-data-model-audit
!uv sync --locked --extra dev
```

## 2. Mount Drive and supply the raw dataset

```python
from google.colab import drive
drive.mount('/content/drive')
!mkdir -p data/raw
!cp /content/drive/MyDrive/sentiment-data/training.1600000.processed.noemoticon.csv data/raw/
!uv run python -m src.prepare_sentiment140
```

Inspect `results/sentiment140_manifest.json`. Confirm its source hash, two labels, row count, duplicate count, and zero cross-split duplicate texts before training.

## 3. Obtain the pinned three-label benchmark

```python
!uv run python -m src.download_tweet_eval
```

## 4. Train in two stages

```python
!uv run python -m src.train_staged_sentiment --stage a
!uv run python -m src.train_staged_sentiment --stage b
```

Stage A saves its binary-adapted model under `models/stage_a_sentiment140`. Stage B reuses that encoder, replaces the binary classification head with a three-class head, fine-tunes on TweetEval, and saves the serving candidate at `models/bert_sentiment`.

## 5. Preserve outputs and record evidence

```python
!cp -r models /content/drive/MyDrive/sentiment-model-runs/run-YYYY-MM-DD/
!cp results/sentiment140_manifest.json results/tweet_eval_manifest.json results/staged_training_metrics.json /content/drive/MyDrive/sentiment-model-runs/run-YYYY-MM-DD/
```

Do not commit model weights, raw tweets, Drive paths, or credentials. Record the Git commit, Colab GPU type, package lockfile, both manifests, and test metrics for every run.

## Release rule

TweetEval test metrics are a benchmark only. Do not release a production claim until the model also passes the separate, human-reviewed modern holdout dataset. The template lives at `data/external/modern_holdout_template.csv`; replace the example rows with approved, reviewed data and keep the actual holdout outside Git.
