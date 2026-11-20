# Phase 1: Reproducible Engineering Foundation

**Status:** In progress; not complete.
**Branch:** `phase/1-reproducible-foundation`
**Baseline date:** 2026-11-20

## Changes in this checkpoint

- Added `pyproject.toml` as the authoritative project metadata and dependency declaration, with Python 3.11–3.13 support and development/research dependency groups.
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
| Resolve dependency graph and generate `uv.lock` | Not completed: the network-enabled resolver repeatedly hung on package-index requests; no lockfile was produced |
| Clean virtual-environment install and full test suite | Not run: no dependency lock/install could be verified |

## Remaining Phase 1 gate

The dependency ranges are declared but exact resolution is not checked in. Until `uv.lock` is generated and `uv sync --locked --extra dev` succeeds in a clean environment, this phase must not be called reproducible or complete. Then run the full test suite in that environment and correct any dependency or compatibility failures.

The current test failures and missing lock are captured as environment/setup blockers, not silently treated as passing checks. This checkpoint is pushed so the phase work is reviewable; continue on this same branch until its exit gate is met.
