# Phase 2: Data and Model Audit

**Status:** In progress.
**Branch:** `phase/2-data-model-audit`
**Product scope:** English text, three labels: negative, neutral, positive.

## What was found in the repository

- No `data/` or `models/` assets were present in the checkout.
- The old preprocessing code expects Sentiment140 labels `0` and `4`, maps them to binary negative/positive, and drops any neutral class.
- The old trainer configured two labels, binary metrics, sampled 200,000 train and 50,000 validation rows (which fails on smaller datasets), forced FP16 on CPU, read files from the current directory, and wrote artifacts to `./bert_sentiment` rather than the API’s expected `models/bert_sentiment`.
- The old trainer never evaluated an untouched test set. `src/predict_bert.py` remains a placeholder.
- The API predictor still maps only labels 0/1 to negative/positive; it cannot yet serve a three-class model. That integration is a later phase.
- `results/metrics.txt` describes three classes despite the old binary trainer. Its figures remain historical and unverified.

## Pinned dataset candidate and actual local audit

The source selected for the English three-way baseline is the sentiment configuration of Cardiff NLP TweetEval, pinned to repository revision `b3a375baf0f409c77e6bc7aa35102b7b3534f8be`.

The pinned files provide these official splits:

| Split | Rows | Negative | Neutral | Positive | Empty text | Duplicate rows within split* |
|---|---:|---:|---:|---:|---:|---:|
| Train | 45,615 | 7,093 | 20,673 | 17,849 | 0 | 30 |
| Validation | 2,000 | 312 | 869 | 819 | 0 | 0 |
| Test | 12,284 | 3,972 | 5,937 | 2,375 | 0 | 4 |

There were no normalized text duplicates across train, validation, and test. The train split contains a small number of repeated rows; these are recorded and retained rather than silently removed. The test distribution differs notably from train, especially for negative and positive labels, so results must include per-class metrics and should not be interpreted as a universal production estimate.

The inspection reads only aggregate counts and hashes; tweet text is not in the audit report. `src/download_tweet_eval.py` downloads the pinned Parquet files without executing dataset-provided Python, validates split schema/labels/empty text/cross-split duplicates, writes ignored CSVs under `data/processed/`, and emits `results/tweet_eval_manifest.json` with source and processed-file SHA-256 values. The generated manifest is committed; tweet CSVs and the local Hugging Face cache are ignored.

### Dataset usage terms

The Hugging Face dataset page identifies the overall license as unknown, while its card describes licenses per task. The sentiment subset points to CC BY 3.0, and the Cardiff repository says restrictions from the original sources and Twitter terms can still apply. Treat this as a candidate for internal evaluation only until the original source terms and intended commercial deployment are reviewed. The project does not commit the tweet text. [TweetEval dataset card](https://huggingface.co/datasets/cardiffnlp/tweet_eval), [Cardiff NLP repository](https://github.com/cardiffnlp/tweeteval), [Sentiment140 card and its binary-training limitation](https://huggingface.co/datasets/stanfordnlp/sentiment140).

## Pinned model candidates

### Three-way social-text inference baseline

`cardiffnlp/twitter-roberta-base-sentiment-latest` at revision `3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7` is a suitable baseline candidate for English social text. Its card declares CC BY 4.0, labels 0/1/2 as negative/neutral/positive, and describes training on about 124 million tweets from 2018–2021 followed by TweetEval fine-tuning. It has **not** been downloaded or evaluated by this project; its name and model-card information do not establish current-domain quality. [Model card](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest).

### Fine-tuning path

The existing BERT fine-tuning direction is retained as a comparison model, but its base checkpoint is now pinned to `google-bert/bert-base-uncased` revision `86b5e0934494bd15c9632b12f734a8a67f723594`. `src/bert_train.py` now reads the pinned dataset splits, configures three labels, uses macro-averaged metrics, evaluates validation and untouched test data, uses a fixed seed, and writes artifacts to the API’s expected model directory. Training itself has not yet run in this environment because the full Torch/Transformers install was deferred after a slow wheel download.

## Phase 2 code and verification

- Added pinned dataset ingestion and a text-free provenance/quality manifest.
- Reworked training input paths and labels to use the agreed three-way split instead of hard-coded binary sample sizes.
- Added tests for split validation, empty and overlapping data rejection, training input validation, and macro metric calculation.
- `uv lock --check`: passed.
- Full locked development test suite: **22 passed**. Tests do not download or evaluate model weights.
- Dataset ingestion was run against the pinned source; split counts, class mappings, duplicate checks, and checksums are recorded in `results/tweet_eval_manifest.json`.

## Remaining Phase 2 gates

1. Review dataset/source terms for the intended deployment and record the decision; do not distribute raw tweets from this repository.
2. Install the locked inference/training dependencies in the supported environment and load the pinned model revision locally.
3. Compare the Cardiff baseline and the fine-tuned BERT model on the pinned held-out test set; report macro and per-class precision/recall/F1, confusion matrix, calibration, and error slices.
4. Reconcile the apparent split distribution shift and duplicate rows; preserve the benchmark test split and add an independently labeled, contemporary sample before any production-quality claim.
5. Produce a model card and quality thresholds, then update the serving label mapping in the dedicated inference integration phase.

The dataset preparation and training-input path are now concrete. The project still has no locally verified three-way model artifact, so `/predict` must not be represented as a working three-class endpoint yet.

## Staged training decision

The project will use the Kaggle/Stanford Sentiment140 archive as the Stage A volume source and retain TweetEval as Stage B three-class fine-tuning and benchmark data. The Sentiment140 schema defines target `2` as neutral, but the usual `training.1600000.processed.noemoticon.csv` file has 1.6M weakly labeled negative/positive tweets; the separate manually labeled test file is too small to be a neutral-training corpus. The preparation script validates the labels in the actual supplied CSV and will stop if it is not the expected Stage A binary source.

`src/train_staged_sentiment.py` now defines the execution sequence:

1. Prepare Sentiment140 into checksummed binary train/validation data.
2. Fine-tune the pinned BERT base checkpoint with binary negative/positive labels.
3. Replace the binary classifier head and fine-tune the encoder on the fixed TweetEval negative/neutral/positive training and validation splits.
4. Evaluate once on the untouched TweetEval test split.
5. Require a separate modern, human-reviewed holdout before a production decision.

The Google Colab runbook is at `notebooks/COLAB_STAGED_TRAINING.md`. Training cannot start until the original Sentiment140 training CSV is supplied. The preparation, training-input validation, and staging code can be tested locally without the raw corpus.
