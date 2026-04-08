import json
import logging
import inspect
import time
from functools import wraps
from hashlib import sha1
from typing import Any, Callable
from uuid import uuid4

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings


_redis_client: Redis | None = None
_cache_logger = logging.getLogger("app.cache")


def get_redis_client() -> Redis | None:
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    try:
        _redis_client = Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        _redis_client.ping()
    except RedisError as exc:
        logging.warning("Redis unavailable, cache disabled: %s", exc)
        _redis_client = None
    return _redis_client


def cache_get_json(key: str) -> Any | None:
    client = get_redis_client()
    if client is None:
        return None

    try:
        raw = client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except (RedisError, json.JSONDecodeError) as exc:
        logging.warning("Redis get failed for key %s: %s", key, exc)
        return None


def cache_set_json(key: str, payload: Any, ttl_seconds: int) -> None:
    client = get_redis_client()
    if client is None:
        return

    try:
        client.setex(key, ttl_seconds, json.dumps(payload, ensure_ascii=True, default=str))
    except (RedisError, TypeError, ValueError) as exc:
        logging.warning("Redis set failed for key %s: %s", key, exc)


def build_cache_key(namespace: str, payload: dict[str, Any] | None = None) -> str:
    normalized = payload or {}
    canonical = json.dumps(normalized, sort_keys=True, separators=(",", ":"), default=str)
    digest = sha1(canonical.encode("utf-8")).hexdigest()[:16]
    return f"analytics:v2:{namespace}:{digest}"


def cache_get_or_set_json(
    key: str,
    ttl_seconds: int,
    compute_fn,
    *,
    lock_ttl_seconds: int | None = None,
    wait_ms: int | None = None,
    poll_interval_ms: int | None = None,
) -> Any:
    cached = cache_get_json(key)
    if cached is not None:
        return cached

    client = get_redis_client()
    if client is None:
        return compute_fn()

    lock_ttl = int(lock_ttl_seconds or settings.CACHE_LOCK_TTL_SECONDS)
    lock_wait_ms = int(wait_ms or settings.CACHE_LOCK_WAIT_MS)
    poll_ms = int(poll_interval_ms or settings.CACHE_LOCK_POLL_INTERVAL_MS)

    lock_key = f"{key}:lock"
    lock_token = str(uuid4())
    acquired = False

    try:
        acquired = bool(client.set(lock_key, lock_token, nx=True, ex=lock_ttl))
    except RedisError as exc:
        logging.warning("Redis lock acquire failed for key %s: %s", key, exc)

    if acquired:
        try:
            second_check = cache_get_json(key)
            if second_check is not None:
                return second_check
            computed = compute_fn()
            cache_set_json(key, computed, ttl_seconds)
            return computed
        finally:
            try:
                # Release lock only if owned by this caller.
                if client.get(lock_key) == lock_token:
                    client.delete(lock_key)
            except RedisError:
                pass

    deadline = time.time() + (lock_wait_ms / 1000.0)
    while time.time() < deadline:
        time.sleep(max(poll_ms, 10) / 1000.0)
        refreshed = cache_get_json(key)
        if refreshed is not None:
            return refreshed

    computed = compute_fn()
    cache_set_json(key, computed, ttl_seconds)
    return computed


def cache_or_compute(
    key: str,
    ttl_seconds: int,
    compute_function,
    *,
    lock_ttl_seconds: int | None = None,
    wait_ms: int | None = None,
    poll_interval_ms: int | None = None,
) -> Any:
    cached = cache_get_json(key)
    if cached is not None:
        _cache_logger.warning("CACHE HIT key=%s", key)
        return cached

    _cache_logger.warning("CACHE MISS key=%s", key)
    return cache_get_or_set_json(
        key,
        ttl_seconds,
        compute_function,
        lock_ttl_seconds=lock_ttl_seconds,
        wait_ms=wait_ms,
        poll_interval_ms=poll_interval_ms,
    )


def cached_endpoint(
    namespace: str,
    ttl_seconds: int,
    *,
    key_builder: Callable[..., dict[str, Any]] | None = None,
):
    """Decorator for FastAPI handlers that caches payloads in Redis."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            payload = key_builder(**kwargs) if key_builder else {
                k: v for k, v in kwargs.items() if k != "db"
            }
            key = build_cache_key(namespace, payload)
            return cache_or_compute(key, ttl_seconds, lambda: func(*args, **kwargs))

        wrapper.__signature__ = inspect.signature(func)
        return wrapper

    return decorator


def cache_invalidate_prefix(prefix: str) -> int:
    client = get_redis_client()
    if client is None:
        return 0

    deleted = 0
    try:
        for key in client.scan_iter(match=f"{prefix}*"):
            deleted += int(client.delete(key) or 0)
    except RedisError as exc:
        logging.warning("Redis invalidate failed for prefix %s: %s", prefix, exc)
        return 0
    return deleted


def invalidate_analytics_cache(service_id: str | None = None) -> int:
    base = cache_invalidate_prefix("analytics:v2:")
    if not service_id:
        return base
    return base + cache_invalidate_prefix(f"analytics:v2:service:{service_id}:")
