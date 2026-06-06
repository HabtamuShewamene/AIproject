"""Lightweight TTL cache for expensive intelligence operations."""

from __future__ import annotations

import hashlib
import time
from functools import wraps
from typing import Any, Callable

_DEFAULT_TTL_SECONDS = 300
_MAX_ENTRIES = 128

_store: dict[str, tuple[float, Any]] = {}


def _cache_key(prefix: str, payload: str) -> str:
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


def get_cached(prefix: str, payload: str) -> Any | None:
    key = _cache_key(prefix, payload)
    entry = _store.get(key)
    if not entry:
        return None
    expires_at, value = entry
    if time.time() > expires_at:
        _store.pop(key, None)
        return None
    return value


def set_cached(prefix: str, payload: str, value: Any, ttl: int = _DEFAULT_TTL_SECONDS) -> None:
    if len(_store) >= _MAX_ENTRIES:
        oldest_key = min(_store, key=lambda k: _store[k][0])
        _store.pop(oldest_key, None)
    key = _cache_key(prefix, payload)
    _store[key] = (time.time() + ttl, value)


def cached_intelligence(prefix: str, ttl: int = _DEFAULT_TTL_SECONDS) -> Callable:
    """Decorator: cache function result by first string arg or joined args."""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            raw = "|".join(str(a) for a in args) + "|" + "|".join(
                f"{k}={v}" for k, v in sorted(kwargs.items())
            )
            hit = get_cached(prefix, raw)
            if hit is not None:
                return hit
            result = fn(*args, **kwargs)
            set_cached(prefix, raw, result, ttl=ttl)
            return result

        return wrapper

    return decorator
