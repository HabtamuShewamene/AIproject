# Codex Work Audit Report

**Repository:** `HabtamuShewamene/AIproject`
**Audit date:** 2026-11-20
**Audited branch:** `phase/2-data-model-audit`
**Remote branch:** `origin/phase/2-data-model-audit`
**Repository state at audit start:** clean, with no tracked modifications

## Executive summary

Codex did substantial Phase 0, Phase 1, and Phase 2 preparation work. It audited the
existing application, added a reproducible Python environment, locked dependencies,
documented the project roadmap, corrected the TweetEval three-class pipeline, and
added a staged Sentiment140 plus TweetEval training path.

However, Codex did **not** produce or verify a trained sentiment model. It did not
commit model weights or a benchmark training run, did not validate a live API model,
and did not establish a production-quality result. The repository now contains a
validated Sentiment140 preparation manifest and processed binary splits, but it does
not contain the Stage A or Stage B model directories.

## 1. What Codex was doing

The recent commits show a deliberate sequence of engineering work:

1. Audit and documentation
2. Security and local-secret hardening
3. Reproducible runtime setup
4. Dependency locking and test-environment validation
5. Three-class TweetEval data/model audit
6. Staged Sentiment140 and TweetEval pipeline implementation

The work is assigned to the Git author `ICHTAG <habtamushewamene905@gmail.com>` in
the recent commits. This name may be the Codex or IDE/automation identity used in
this workspace; it is not sufficient evidence of a person's current location or
ongoing process.

## 2. What Codex completed

### Baseline and roadmap

- Added `BASELINE_AUDIT.md` and the Phase 0 baseline.
- Added `ROADMAP.md` with the implementation sequence.
- Added `PHASE1_FOUNDATION.md` and `PHASE2_DATA_MODEL_AUDIT.md`.
- Expanded the setup and training documentation in `README.md`.

### Security and repository safety

- Added local secret exclusions and a redacted `.env.example`.
- Removed or excluded the local `.env` file.
- Added exclusions for raw CSV, processed CSV, models, caches, credentials, and
  virtual environments.

### Reproducible environment

- Added `pyproject.toml` with Python 3.11–3.13 support.
- Added `.python-version`.
- Added or retained a compatibility `requirements.txt`.
- Generated `uv.lock`.
- Added test and research dependency groups.
- Configured the project package and pytest discovery.

### TweetEval three-class pipeline

- Added `src/download_tweet_eval.py`.
- Pinned the TweetEval dataset revision and label mapping.
- Added processed train, validation, and test splits.
- Added `results/tweet_eval_manifest.json`.
- Updated `src/bert_train.py` for three-class BERT training.
- Added manifest and split checksum validation.

### Sentiment140 staged pipeline

- Added `src/prepare_sentiment140.py`.
- Added binary label mapping:
  - raw `0` -> `0` negative
  - raw `4` -> `1` positive
- Added deterministic, tweet-ID-based train/validation splitting.
- Added duplicate-text normalization and cross-split duplicate checks.
- Added SHA-256 provenance for the source and processed files.
- Added `src/train_staged_sentiment.py`.
- Added a Colab runbook at `notebooks/COLAB_STAGED_TRAINING.md`.
- Added a modern human-review holdout template.

### Tests

Codex added tests for the Twitter/APify boundary, dataset preparation, model data,
Sentiment140 preparation, and staged training input handling.

The complete suite was rerun after correcting the temporary-directory environment:

- **29 tests passed**
- **0 tests failed**
- **2 FastAPI/httpx deprecation warnings**
- One pytest-cache warning occurred because `.pytest_cache` is inaccessible

The first test attempt encountered Windows temporary-directory permission errors;
rerunning pytest with a project-local temporary directory resolved those setup
errors. The test suite itself passed.

## 3. State verified during this audit

### Raw Sentiment140 data

The supplied file exists locally at:

`data/raw/training.1600000.processed.noemoticon.csv`

It was not committed because `data/raw/*.csv` is ignored.

- Size: 238,803,811 bytes
- SHA-256: `08cba6317a49528fcd074f9043aafcd5ad6c6be45ede159c4e36cec33af24afe`
- Raw rows: 1,600,000
- Labels: `0` and `4`
- Format: six original columns with no header

### Preparation performed

Running `src.prepare_sentiment140` completed successfully and created:

- `data/processed/sentiment140_train.csv`
- `data/processed/sentiment140_validation.csv`
- `results/sentiment140_manifest.json`

Preparation results:

| Split | Negative | Positive | Total |
|---|---:|---:|---:|
| Train | 779,474 | 781,311 | 1,560,785 |
| Validation | 7,863 | 7,799 | 15,662 |

- Duplicate text rows removed: 23,553
- Cross-split duplicate texts: 0
- Train SHA-256:
  `054903c53837f2ca159c399b403aa2d088e69ae0300aeaf9ffc74ff4aaf96f79`
- Validation SHA-256:
  `60864abbc2d7bb718a9b0f03bf2be71435e6349787af527411198c3c23a6e5a3`

The processed CSV files remain ignored by Git. Only the text-free manifest is
visible as an untracked generated report.

### TweetEval

The repository contains pinned TweetEval train, validation, and test CSV files plus
`results/tweet_eval_manifest.json`. Their presence indicates that dataset download
and preparation had already been completed. No staged training metrics or model
artifact were found.

### Models

No trained model directories or model weights were found, including:

- `models/stage_a_sentiment140`
- `models/bert_sentiment`
- `models/*.pkl`

No `staged_training_metrics.json` or `bert_tweeteval_metrics.json` file exists.

## 4. What Codex did not complete

Codex did not:

- Download or generate a model artifact.
- Run Stage A Sentiment140 adaptation.
- Run Stage B TweetEval fine-tuning.
- Evaluate an untouched TweetEval test split.
- Produce benchmark accuracy, precision, recall, or F1 metrics.
- Verify that the Transformers, PyTorch, Trainer, or model-download stack works
  end-to-end with an actual model.
- Add or verify a human-reviewed modern holdout dataset.
- Verify the live `/predict` endpoint with a real trained model.
- Establish production release thresholds.
- Commit or publish the raw Sentiment140 dataset.
- Commit the processed CSV files or model weights.

Training is not a Codex “failure”; it is explicitly deferred by the pipeline design.
The project requires a GPU/model-download run and separate modern evaluation before
production claims.

## 5. Evidence of the current state

The recent commit sequence is:

| Commit | Purpose |
|---|---|
| `06a8150` | Baseline audit and roadmap |
| `b6b9d0d` | Ignore secrets and untrack local environment |
| `958a823` | Runtime and local configuration |
| `389a051` | Lock dependencies and verify test environment |
| `fb52bde` | Pin and validate three-class TweetEval data pipeline |
| `0ab4322` | Add staged Sentiment140 and TweetEval training pipeline |

The active branch is `phase/2-data-model-audit`; it tracks
`origin/phase/2-data-model-audit`. The worktree is clean for tracked files after
dataset preparation, apart from the newly generated untracked manifest.

## 6. Where “Codex” is in the repository

The recent changes are not stored in a separate Codex workspace or process. They are
represented by commits on the active branch and by the files they changed.

Operationally:

- The recent Git identity is `ICHTAG <habtamushewamene905@gmail.com>`.
- The code is in the repository root:
  `C:\Sentimental Analysis  AI\AIproject`
- The dataset is at:
  `data/raw/training.1600000.processed.noemoticon.csv`
- Prepared Stage A data is at:
  `data/processed/sentiment140_*.csv`
- The generated audit manifest is at:
  `results/sentiment140_manifest.json`
- The next executable step is GPU training via the staged training script.

There is no retained Codex session transcript or running agent identity in the
repository evidence inspected here, so this report cannot prove a current Codex
process location, user account, or physical location.

## 7. Recommended next actions

1. Commit the generated `results/sentiment140_manifest.json` if it should be source-controlled.
2. Confirm that TweetEval and BERT package downloads work in the target environment.
3. Run Stage A with GPU support:
   `python -m src.train_staged_sentiment --stage a`
4. Run Stage B:
   `python -m src.train_staged_sentiment --stage b`
5. Preserve manifests, Git commit hash, GPU type, and metrics outside Git.
6. Build the human-reviewed modern holdout.
7. Compare modern-holdout and TweetEval results before updating `/predict`.
8. Integrate only an explicitly versioned model artifact into the API.
