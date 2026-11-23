# Phase 3: Prediction and Language Behavior Specification

## Executive Overview
Phase 3 hardens the sentiment analysis platform's serving contract, language behavior, and edge-case handling. Prior to this phase, the application relied on silent fallbacks during translation failures, uncalibrated confidence scores, and heuristic keyword overrides that masked true neural model behavior. 

This phase guarantees an immutable, versioned prediction contract where every request returns explicit provenance, processing status, and confidence semantics.

---

## Prediction Contract Specification

### Guaranteed Response Schema (`/predict` & `predict_sentiment`)

```json
{
  "text": "Original or sanitized input string",
  "original_text": "Original input string before processing",
  "translated_text": "English text fed to the model",
  "language": "Detected BCP-47 code, 'unknown', or 'translation_failed'",
  "language_status": "english | translated | translation_failed | unknown | unsupported",
  "model_version": "Pinned model architecture and library version",
  "sentiment": "negative | neutral | positive | uncertain",
  "confidence": 0.9460,
  "low_confidence": false,
  "probabilities": {
    "negative": 0.9460,
    "neutral": 0.0468,
    "positive": 0.0072
  },
  "processing_status": "ok | too_short | truncated | translation_failed | model_error"
}
```

---

## Core Pillars & Implementation Scope

1. **Abstention & Confidence Calibration:**
   - Softmax winning probability threshold set to `ABSTENTION_THRESHOLD` (default: 0.45).
   - If `confidence < ABSTENTION_THRESHOLD`, the model abstains and assigns `sentiment = "uncertain"` with `low_confidence = true`.

2. **Boundary Validation & Sanitization:**
   - Inputs shorter than `MIN_INPUT_CHARS` (3 characters) return `processing_status = "too_short"`.
   - Inputs longer than `MAX_INPUT_CHARS` (2,000 characters) are safely truncated to protect inference latency and memory, returning `processing_status = "truncated"`.

3. **Transparent Language Pipeline:**
   - Detects Amharic (Ethiopic Unicode `[\u1200-\u137F]`), Arabic, Chinese, and Japanese.
   - Translation failures do not silently masquerade as English; they return `language_status = "translation_failed"` and `processing_status = "translation_failed"`.

4. **Decoupling Heuristics from Ground Truth:**
   - Raw neural predictions are preserved as ground truth.
   - Sarcasm, negation, and keyword counts are surfaced as `intelligence.signals` rather than hardcoded label mutations.

5. **Operational Probes & Health Checks:**
   - `/health/live`: Liveness probe verifying server process responsiveness.
   - `/health/ready`: Readiness probe verifying BERT model weights and tokenizer are loaded in memory.
