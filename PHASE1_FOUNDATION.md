# Phase 1: Reproducible Engineering Foundation

**Status:** Foundation checkpoint complete. Full inference/training installation and model loading are deferred to model validation, because the model artifact is not present and the large wheel download was too slow in this restricted environment.
**Branch:** `phase/1-reproducible-foundation`
**Baseline date:** 2026-11-20

## Changes in this checkpoint

- Added `pyproject.toml` as the authoritative project metadata and dependency declaration, with Python 3.11–3.13 support and development/research dependency groups.
- Generated and committed `uv.lock` with 193 resolved packages; configured an ignored project-local UV cache to work within this workspace’s filesystem permissions.
- Added `.python-version` targeting Python 3.13 for local tool selection.
- Added a redacted `.env.example` that documents the model path and optional Apify settings. `.gitignore` allows this template while ignoring local environment files.
- Updated the README setup instructions to use the project metadata and explain that model/data artifacts are not included.
- Kept `requirements.txt` as a compatibility shim pointing to the project’s development extra while migrating to `pyproject.toml`.

## Validation performed

| Check | Result |
|---|---|
| Parse `pyproject.toml` with Python `tomllib` and inspect required dependency declarations | Passed |
| Confirm `.env` is ignored and `.env.example` is allowlisted | Passed |
| `python -m pytest -q tests/test_api.py` | 4 passed |
| `python -m pytest -q` | Blocked at collection: active global Python lacks `scikit-learn` and `langdetect` |
| `uv lock --check` using the committed lock | Passed; 193 packages resolved and metadata is in sync |
| Locked development/test environment sync | Passed; 77 packages installed in the ignored project `.venv` |
| Full `python -m pytest -q` in the locked project environment | 15 passed after updating the Twitter test to mock the active Apify actor adapter |
| Full locked sync including Torch, Transformers, and Datasets | Lock resolution passed, but installation was stopped during slow large-wheel downloads. Direct installation and runtime import/load remain unverified |

## Remaining verification

`uv.lock` now makes the dependency graph exact, and the locked development/test environment passes the full automated suite. The installed test environment did not install Torch, Transformers, or Datasets directly. The lock includes them, but installing and importing the inference/training stack remains unverified and must be done with the model artifact during model validation.

The test suite now mocks the current Apify actor boundary instead of the obsolete Tweepy-style interface. The test does not establish that the real third-party actor works with live credentials; that remains an integration check for the social-ingestion phase.

The phase branch is pushed for review. Continue on a dedicated Phase 2 branch for the data/model audit; carry the runtime installation check as an explicit Phase 2/serving validation item rather than treating it as passed.
