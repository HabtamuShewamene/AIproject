"""Enterprise middleware for request correlation ID tracing and structured logging."""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("sentiai.access")


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures every HTTP request carries an X-Request-ID header,
    measures end-to-end processing latency, and records structured access logs.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract existing client correlation ID or generate a new UUIDv4
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.perf_counter()

        response: Response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Inject tracing headers into response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(duration_ms)

        # Emit structured log entry
        log_payload = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": request.client.host if request.client else "unknown",
        }
        logger.info(json.dumps(log_payload))

        return response
