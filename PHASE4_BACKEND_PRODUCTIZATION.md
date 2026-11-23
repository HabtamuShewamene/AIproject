# Phase 4: Backend Productization and External Integrations Specification

## Executive Overview
Phase 4 elevates the sentiment analysis backend from a prototype API to an enterprise-grade production service. Prior to this phase, the application lacked request tracing, structured logging, centralized error handling, lifespan lifecycle management, and API versioning. Social data extraction through Apify/Twitter also lacked boundary protections and resilience against missing tokens and network timeouts.

---

## Architectural Objectives

1. **Lifespan Application Lifecycle:**
   - Pre-load BERT model weights and tokenizer into memory during the FastAPI `lifespan` startup event, eliminating cold-start latency for incoming traffic.
   - Cleanly release GPU/RAM memory on shutdown.

2. **API Versioning & Routing (`/api/v1`):**
   - Establish dedicated, versioned routers under `/api/v1/predict`, `/api/v1/predict/batch`, `/api/v1/social/tweet`, and `/api/v1/social/topic`.
   - Maintain backwards-compatible legacy root aliases (`/predict`, `/analyze-twitter`, `/analyze-topic`) marked as deprecated.

3. **Request Tracing & Structured Logging:**
   - Implement `RequestIDMiddleware` that injects a unique UUID (`X-Request-ID`) into every request state and response header.
   - Output structured JSON logs containing timestamp, correlation ID, HTTP method, path, status code, and execution duration.

4. **High-Throughput Batch Processing:**
   - Introduce `POST /api/v1/predict/batch` accepting up to `MAX_BATCH_SIZE` items (default: 50).
   - Enforce batch-level and item-level boundary validation with partial failure safety.

5. **Hardened Social Media Adapters:**
   - Validate URL formats for Twitter/X status links prior to API calls.
   - Handle missing credentials (`APIFY_TOKEN`, `TWITTER_BEARER_TOKEN`), rate limits, empty response payloads, and network timeouts cleanly with typed error responses.

6. **Global Standardized Error Handling:**
   - Centralize exception handling for `HTTPException`, `RequestValidationError`, and unexpected 500 errors to guarantee consistent JSON error schemas across all routes.
