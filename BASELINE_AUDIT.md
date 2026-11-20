# Phase 0: Baseline Audit and Gap Register

**Audit date:** 2026-11-20
**Branch:** `phase/0-baseline-audit`
**Scope:** Read-only inspection of the repository and its tracked files. No runtime tests or deployments have been performed as part of this audit. Status describes evidence in this checkout, not assets that may exist outside it.

## Executive assessment

This is a prototype with meaningful backend and model-training code, but this checkout does not yet provide a reproducible, usable end-to-end product. The core serving path expects model artifacts that are absent; training expects source data that is absent; the frontend source is incomplete and excluded from Git; and production deployment, security, and operational controls are not present. The recorded model metrics conflict with the two-class training and inference implementation and cannot be verified from the available artifacts.

**Immediate security finding:** `.env` is tracked by Git (`git ls-files` reports it), even though `.gitignore` lists `.env`. Treat any credentials ever stored in it as exposed: revoke/rotate them and audit repository history and access. The audit intentionally does not reproduce its contents. Adding `.env` to `.gitignore` alone does not remove a tracked file or erase its history.

## Status definitions

- **Implemented:** Present and connected in source, but not necessarily production verified.
- **Partial:** Some code exists, but important behavior, assets, integration, or evidence are missing.
- **Not started:** No implementation/configuration was found in this checkout.
- **Blocked/unknown:** Cannot be established without an external decision, artifact, credential, or environment.

## Feature and capability register

| Capability | Status | Evidence in checkout | Gap / audit note |
|---|---|---|---|
| HTTP API | Partial | `app/main.py` has `/`, `/predict`, `/analyze-twitter`, `/analyze-topic` | No auth, versioning, request limits, structured error contract, or health/readiness distinction. External failures often return HTTP 200 with an error object. |
| BERT inference | Partial | `app/predictor.py` loads a Transformers sequence classifier | `models/bert_sentiment/` is absent; current launch cannot demonstrate real inference. Confidence calibration and runtime target are unverified. |
| Training | Partial | `src/bert_train.py` uses Transformers Trainer and binary labels | Depends on absent data; script uses relative paths, fixed sample sizes, `fp16=True`, and no evident final test-set evaluation or reproducible artifact manifest. |
| Preprocessing and split | Partial | `src/preprocessing.py`, `src/split_dataset.py` | Raw CSV absent. Duplicate/leakage handling and preprocessing parity with serving are not established. |
| Dataset and model artifacts | Not present in checkout | `.gitignore` excludes data CSVs and model artifacts; no `data/` or `models/` directory is present | Need locate approved assets or define a lawful reproducible acquisition path. |
| Sentiment labels | Partial / inconsistent | Training uses two labels; `app/predictor.py` maps only negative/positive | `results/metrics.txt` reports neutral metrics and three classes, inconsistent with current training/inference code. Product label semantics are undecided. |
| Model quality evidence | Partial / unverified | `results/metrics.txt`, `results/confusion_matrix.png`, evaluation scripts | Metrics lack reproducible run metadata and model/data artifacts; multilingual and production quality claims need independent evidence. |
| Heuristic corrections | Implemented, unvalidated | `app/sentiment_rules.py`, `app/predictor.py`, `app/main.py` | Keyword/sarcasm/negation rules can override model labels and raise confidence without measured calibration. Potential false positives and contradictory decisions. |
| Translation/language handling | Partial | `app/translator.py` uses `langdetect` and `deep-translator` | External service dependency; failures return original text with language `unknown`, after which English model inference can continue. Supported language policy and quality evidence absent. |
| X/Twitter collection | Partial / externally dependent | `app/twitter_client.py` uses Apify actor and credentials | Provider/actor terms, availability, quotas, parsing contract, pagination, retries/timeouts, and real credential-backed behavior unverified. Errors collapse into empty/no-result responses. |
| Emotion/entities/explanations | Implemented as heuristics | `app/emotion_detector.py`, `app/entity_extractor.py`, `app/explanation_engine.py` | No evaluation; explanations infer keyword cues and may not faithfully explain the model. Must not imply validated AI output. |
| Topics/trends/alerts/virality/reporting | Implemented as heuristics | `app/topic_clustering.py`, `app/trend_detector.py`, `app/alerts_engine.py`, `app/virality_engine.py`, `app/report_generator.py` | Trend growth is estimated without time windows/baselines; virality uses fixed engagement tiers; cluster themes use keyword rules. Not validated predictive capabilities. |
| Frontend | Partial / not buildable from checkout | `frontend/app/layout.js`, components, `frontend/hooks/useAnalysis.js` | `frontend/` is ignored and untracked; no package manifest, app entry page, or imported `services/api` implementation found. UI cannot be built from this checkout. |
| Tests | Partial | `tests/test_api.py`, preprocessing, translator, Twitter tests, and quality scripts | API tests stub model/provider; no test execution yet; no frontend tests, full end-to-end test, deployment smoke test, or CI config found. |
| Persistence and history | Not established | No database or storage config found | Determine whether analysis results/history should persist; define access, retention, export, and deletion before adding storage. |
| Authentication / authorization / tenancy | Not started | No implementation found in API source | Required before exposing service beyond trusted local use; exact identity and tenant model depends on audience. |
| Observability / operations | Not started | No production telemetry/deployment config found | Need structured logs, metrics, traces, actionable alerts, ownership, runbooks, and SLOs. |
| CI/CD and deployment | Not started | No Dockerfile, CI workflow, infrastructure config, or lockfile found | Target platform, environments, release process, secrets provisioning, scaling, rollback, and recovery are undecided. |
| Security / privacy governance | Partial / critical gap | `.env` is tracked; CORS is hard-coded in `app/main.py` | Rotate credentials; inspect history/access; define data classification, retention, provider/legal basis, access control, and incident response. |
| Dependency management | Partial | `requirements.txt` exists | Dependencies are unpinned; no lock or vulnerability update process found. |
| Documentation | Partial | `README.md`, `ROADMAP.md` | README run instructions overstate availability of model/data and omit frontend and production setup. Some documented response fields differ from API implementation. |

## Current architecture observed

```text
Frontend source (incomplete/untracked)
  └─ intended API calls (API client file absent)
       └─ FastAPI app/main.py
            ├─ text → translator → local Transformers model → heuristic overrides
            ├─ X post/query → Apify scraper → same prediction path
            └─ topic post results → heuristic intelligence modules

Training scripts → expected Sentiment140 CSV → processed splits → BERT artifact
                   (source data and produced artifact absent in this checkout)
```

## Repository and delivery baseline

- Current base branch at audit start: `main`, at `41183a4` (`Merge pull request #6 ...`).
- Remote named `origin` points to the project GitHub repository.
- The only pre-existing worktree change at phase start was the untracked `ROADMAP.md` created for the roadmap request; it was retained on the phase branch.
- `.env` is tracked despite the ignore rule. Credential rotation/history review is a release-blocking security task.
- `frontend/` is ignored by `.gitignore`; listed frontend sources are therefore not part of the normal Git checkout.
- No deployment workflow, container definition, infrastructure-as-code, dependency lock, or CI workflow was found in the repository inventory.

## Baseline test execution

Commands were run from the repository root on the current Python 3.13 environment:

| Command | Result | Finding |
|---|---|---|
| `python -m pytest -q` | Collection failed | `tests/test_preprocessing.py` cannot import `sklearn`; `tests/test_translator.py` cannot import `langdetect`. The environment is missing declared runtime dependencies. |
| `python -m pytest -q tests/test_api.py tests/test_twitter_client.py` | 6 passed, 1 failed | `test_fetch_tweet_returns_metrics_with_safe_defaults` expects a mocked `client.get_tweet` response. Current `fetch_tweet` uses the Apify actor path, so the mock is bypassed and the result is `None`. This is an implementation/test contract mismatch, not a passing integration check. |

These are baseline results, not changes introduced by the audit. They must be rerun in the project’s reproducible environment after dependency and integration decisions are settled.

## Decisions required before Phase 1 implementation

These choices change architecture and acceptance criteria. Record the selected answer in a decision log before building on assumptions:

1. **Audience and exposure:** local/internal tool, single organization, or multi-tenant external product? Which identity provider/authentication approach?
2. **Sentiment semantics:** binary positive/negative, three-way positive/neutral/negative, or another scheme? Is aspect-based sentiment required?
3. **Language scope:** which languages must be supported at launch, and is translating to English acceptable or should multilingual inference be used?
4. **Input sources:** user-provided text only, supported social APIs, or scraping where contractually permitted? Which provider is approved?
5. **Data handling:** should request text/results persist? What retention, deletion, export, and audit requirements apply?
6. **Deployment target:** cloud/provider or on-premises? Which regions and environment boundaries?
7. **Service targets:** expected peak requests, batch size, latency, availability, recovery, and budget?
8. **Existing assets:** where are the approved dataset, trained model, and complete frontend/API client, if stored outside this repository?

## Phase 0 exit checklist

- [x] Repository structure, source paths, declared dependencies, API routes, tests, and deployment files inventoried.
- [x] Material implementation gaps and contradictions recorded with source evidence.
- [x] Phase branch created without overwriting pre-existing work.
- [ ] Exposed or historically committed credentials revoked/rotated and repository history/access reviewed.
- [ ] Product, language, data, hosting, and service targets decided.
- [ ] Data/model/frontend asset locations established or approved acquisition plans recorded.
- [ ] Baseline automated checks executed and results attached before merge.

Phase 0 should not be considered fully closed until the unchecked security and decision items are resolved. The next implementation phase must not silently assume these choices.

## Next step after Phase 0

Once the open decisions and asset locations are recorded, create the next phase branch from the accepted baseline. The first implementation milestone should establish reproducible setup/configuration and safe secret handling; then build and verify one vertical slice before adding further features.
