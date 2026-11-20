# Sentiment Analysis Platform: End-to-End Roadmap

## Purpose and working agreement

This roadmap turns the current prototype into a reproducible, secure, supportable sentiment analysis product. It covers discovery through deployment and ongoing maintenance. We will work in gated phases: inspect and record the baseline, agree product decisions, implement a small vertical slice, verify it, then move forward. Each phase produces reviewable artifacts and an audit record.

“No flaws” cannot be guaranteed for an ML system. The practical target is measurable quality, known limitations, safe failure behavior, monitoring, rollback, and a process that catches regressions quickly.

## Current baseline

The repository has a FastAPI API, Transformers/PyTorch inference and training code, Apify-based social collection, translation, heuristic intelligence modules, React-style frontend files, and pytest files. The current checkout does not include `data/` or `models/`; the frontend lacks its package/build manifest and the imported API service; and no deployment or CI configuration was found. Reported metrics are not reproducible from this checkout. These are the first audit items, not assumptions that the assets do not exist elsewhere.

The detailed Phase 0 inventory, evidence, risks, and decisions needed before implementation are recorded in [BASELINE_AUDIT.md](BASELINE_AUDIT.md).

## Delivery principles

- Keep a traceable link from each requirement to implementation, evidence, and owner.
- Do not call a feature complete because a module exists; verify it through its real API and user flow.
- Keep sentiment prediction, translation, collection, and heuristic insights distinguishable in the response and in evaluation.
- Preserve privacy and minimize retained source text. Set retention only after product and legal requirements are known.
- Treat model/data versions and platform-provider terms as production dependencies.
- Every release must have a deployment record, smoke check, monitoring plan, and rollback path.

## Phases and exit gates

### 0. Baseline audit and product decisions

**Work:** Inventory all tracked and ignored assets, inspect repository history and environment setup, map UI-to-API flows, inspect model/data provenance and credential handling, and identify actual deployment target and social data source constraints. Agree intended users, use cases, languages, supported sources, volume/latency targets, availability target, retention, and budget. Decide binary vs. neutral/mixed polarity and whether aspect sentiment is in scope.

**Deliverables:** Current-state architecture and data-flow diagrams; feature inventory with complete/partial/missing status; risk register; product requirements and nonfunctional targets; deployment/environment decision record; initial threat/privacy review.

**Exit gate:** Product scope, target environment, model labels, legal/provider constraints, and acceptance thresholds are written down. Unknown model/data artifacts are resolved or explicitly marked unavailable.

### 1. Reproducible engineering foundation

**Work:** Establish a clean setup from a fresh checkout, pin and lock dependencies, configure settings through validated environment variables, separate development/test/production config, remove accidental credentials and rotate exposed ones if necessary. Define package structure, logging conventions, API schemas, and supported Python/runtime versions. Restore frontend manifest/build and API client or explicitly retire the frontend.

**Deliverables:** Setup guide; dependency lock; configuration reference; secret handling procedure; CI checks for formatting/static checks/unit tests/build; repository artifact policy; frontend build instructions.

**Exit gate:** A new environment can install and start each supported component using documented commands, with no checked-in secrets and clear failure messages when required assets/configuration are absent.

### 2. Data and model audit

**Work:** Locate or reacquire the dataset and model; record source, license, consent/terms, labeling method, timestamps, language/domain coverage, class distribution, duplicates, and known bias. Check split leakage and deduplicate before splitting where appropriate. Define a versioned dataset manifest and immutable evaluation set. Reconcile the current two-class trainer, label mapping, README, and three-class metrics claims. Establish explicit preprocessing parity between training and inference.

**Model evaluation:** Evaluate untouched test data; confusion matrix and precision/recall/F1 per class; macro/weighted scores; calibration (Brier/reliability); confidence thresholds and abstention; slice metrics by language, source, text length, and relevant domain; error review; latency/memory on target hardware. Create a model card describing intended use and limitations. Do not ship the claimed metrics until they can be reproduced.

**Deliverables:** Dataset card/manifest; data quality report; versioned baseline model; reproducible evaluation report; model card; model acceptance thresholds.

**Exit gate:** Data/model provenance is acceptable, labels and metrics agree, the inference artifact can be loaded from a documented location, and agreed quality thresholds are met on a held-out representative evaluation set.

### 3. Prediction and language behavior

**Work:** Define supported languages and behavior for short/ambiguous/mixed-language content. Choose whether to use multilingual modeling or a translation pipeline; measure translation failures and their effect on sentiment. Add input normalization and validation without destroying sentiment cues. Remove or isolate heuristic overrides until separately validated. Calibrate confidence; support low-confidence/unknown/abstain outcomes where appropriate. Decide whether neutral and aspect-level sentiment are product requirements.

**Deliverables:** Stable prediction contract with model/version, label, score semantics, language and processing status; regression examples for negation, sarcasm, slang, emojis, code-switching, long inputs, and edge cases; quality report for supported languages.

**Exit gate:** Results are reproducible for a pinned model version; failed translation does not silently masquerade as successful English analysis; confidence has a documented interpretation; unsupported inputs return an explicit outcome.

### 4. Backend productization and external integrations

**Work:** Introduce typed request/response/error models, request limits, validation, consistent HTTP status codes, API versioning, authentication/authorization, tenant boundaries if multi-user, rate limits/quotas, request IDs, structured logs, timeouts, bounded retries, and health/readiness endpoints. Make model loading a controlled application lifecycle step. For social collection, confirm provider terms and supported operations; validate URLs/queries; handle pagination, quotas, empty results, partial results, provider outages, and source timestamps explicitly. Keep external collection behind an adapter. Add persistence only where required by product needs, with retention/deletion controls.

**Deliverables:** API specification; threat model; provider adapter contract; error catalogue; operational dashboards/metrics; data retention policy and migration plan if storage is introduced.

**Exit gate:** API behavior is documented and tested against real service boundaries (with provider/model replaced only at test seams); unauthorized, invalid, overloaded, and dependency-failure paths are safe and observable.

### 5. Insight features: evidence before claims

**Work:** Audit each extra feature individually: emotion, entities, explanations, clustering, trends, alerts, virality, influential posts, executive summary. Label current heuristic outputs as estimates. For each feature, define intended decision use, baseline, offline evaluation, and safe wording. Replace frequency-as-growth with time-windowed baseline comparisons if true trends are required. Do not present virality as predictive unless trained and validated against future outcomes. Ensure explanations faithfully reflect model behavior and are not fabricated from keyword cues.

**Deliverables:** Feature-by-feature acceptance tests and limitations; validated algorithms or an explicit decision to defer/remove unsupported claims.

**Exit gate:** Every displayed insight has evidence, semantics, and a known limitation; unevaluated features are clearly marked experimental or omitted from production UX.

### 6. Frontend completion and accessibility

**Work:** Restore or define frontend toolchain and API client. Connect text, URL, and topic flows to actual response contracts; represent loading, partial, empty, error, unsupported-language, and low-confidence states. Add accessible navigation, keyboard support, responsive behavior, safe text rendering, and clear source/sample/time metadata. Prevent sensitive text from being persisted in browser history unless explicitly opted in.

**Deliverables:** Production build; component and API contract coverage; accessibility review; user-facing limitations/help copy; privacy behavior documentation.

**Exit gate:** A user can complete each supported flow in the built UI, inspect the result provenance, understand failures, and use it accessibly on supported browsers/devices.

### 7. Security, privacy, and compliance readiness

**Work:** Review data classification and flows, secrets, dependency vulnerabilities, authorization, injection/abuse limits, CORS, logs, backups, retention, deletion, and third-party data terms. Define incident response and access controls. Conduct a focused security review before external exposure. Confirm jurisdiction and applicable contractual/regulatory obligations with the organization’s responsible reviewer.

**Deliverables:** Security checklist with evidence; privacy/data-flow record; access and secret rotation procedures; incident and deletion runbooks; dependency scan findings and remediation record.

**Exit gate:** No known critical/high security findings remain without an explicit owner and approved mitigation; privacy and provider constraints are addressed for the deployment context.

### 8. Deployment and release

**Work:** Choose target runtime (cloud/on-prem), containerize API and frontend, provision model artifacts securely, separate environments, configure TLS, secrets, resource limits, autoscaling strategy, health checks, logs/metrics/traces, and backups. Add CI/CD with gated build, quality checks, image/artifact provenance, staged deployment, smoke checks, rollback, and migration strategy. Run load and failure testing against agreed targets.

**Deliverables:** Infrastructure/deployment definitions; release checklist; service-level objectives; on-call/ownership map; rollback and disaster recovery runbooks; cost estimate.

**Exit gate:** Staging deployment passes functional, quality, security, load, and recovery checks; production has monitoring, alert routing, rollback, and a named operator before launch.

### 9. Operations and continuous improvement

**Work:** Monitor availability, latency, errors, provider quotas, model load failures, cost, input distribution, language mix, confidence/abstention, and labeled quality samples where legally appropriate. Define alert thresholds and review cadence. Capture feedback with privacy controls. Investigate drift; refresh datasets/models only through versioned evaluation and staged rollout. Patch dependencies, rotate credentials, test restores, review access, and audit vendor/API changes.

**Deliverables:** Monthly/quarterly operating review; model/data change log; incident and postmortem records; retraining criteria; backup restore evidence; end-of-life plan for dependencies/providers.

**Exit gate:** Each production release and model change is traceable and reversible; service ownership, alert response, maintenance windows, and quality review cadence are active.

## Cross-cutting audit checklist

For every phase, maintain a table with: requirement, status (not started/partial/implemented/verified), evidence link, risk/severity, owner, target phase, and follow-up. Audit the whole path, not just code presence:

1. User input → validation → collection/translation → prediction → post-processing → insight generation → API response → UI rendering.
2. Data provenance → preprocessing → split integrity → training → evaluation → artifact/version → serving.
3. Authentication → authorization → secret access → logs → storage/retention → deletion.
4. Commit → CI → artifact build → staging → release approval → production verification → rollback.
5. Alert → triage → mitigation → recovery → postmortem → prevention.

## Proposed release acceptance bar

Before an external production launch, require all of the following to be agreed and met:

- Reproducible model evaluation on representative held-out data with per-class and per-language reporting.
- No unresolved critical security issue; documented privacy/provider basis and retention behavior.
- API and UI flows pass contract/integration checks, including failure paths.
- Deployment meets agreed latency, capacity, availability, and cost targets under load.
- Health, errors, model/provider dependency state, and quality indicators are monitored with actionable alerts.
- Tested rollback, backup/restore where data is persisted, and named operational ownership.
- Model card, API docs, user limitations, support path, and maintenance runbooks are available.

## First working sequence

1. Finish Phase 0 and resolve where the missing dataset/model/frontend assets live.
2. Create a traceable gap register from this roadmap and agree binary/neutral, language, source, privacy, and deployment decisions.
3. Make the baseline reproducible before changing model behavior.
4. Build one complete vertical slice: validated text input → versioned prediction → API response → UI result → logs/metrics.
5. Verify that slice, then add external collection and each insight as individually gated capabilities.
6. Deploy to staging, close security/operational gaps, and only then make a production release decision.

This order keeps foundational risks visible while letting us demonstrate working software early. Phase sequencing can be adjusted once the target deployment, available data/model artifacts, and product requirements are known.
