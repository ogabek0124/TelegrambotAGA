import os
import ast
from time import time

try:
    import redis  # type: ignore[import-not-found]
except ImportError:  # redis is optional
    redis = None


REDIS_URL = os.getenv("REDIS_URL")
CACHE_PREFIX = os.getenv("BOT_CACHE_PREFIX", "inglizchaoson")

_memory_cache = {}


def _redis_client():
    if not redis or not REDIS_URL:
        return None
    try:
        return redis.Redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        return None


def cache_get(key: str):
    client = _redis_client()
    full_key = f"{CACHE_PREFIX}:{key}"

    if client:
        try:
            data = client.get(full_key)
            if data is not None:
                return ast.literal_eval(data)
        except Exception:
            pass

    item = _memory_cache.get(full_key)
    if not item:
        return None

    expires_at, value = item
    if time() > expires_at:
        _memory_cache.pop(full_key, None)
        return None
    return value


def cache_set(key: str, value, ttl: int = 20):
    client = _redis_client()
    full_key = f"{CACHE_PREFIX}:{key}"

    if client:
        try:
            client.setex(full_key, ttl, repr(value))
            return
        except Exception:
            pass

    _memory_cache[full_key] = (time() + ttl, value)


def cache_invalidate_prefix(prefix: str):
    client = _redis_client()
    full_prefix = f"{CACHE_PREFIX}:{prefix}"

    if client:
        try:
            for key in client.scan_iter(match=f"{full_prefix}*"):
                client.delete(key)
        except Exception:
            pass

    for key in list(_memory_cache.keys()):
        if key.startswith(full_prefix):
            _memory_cache.pop(key, None)


def cache_clear_all():
    client = _redis_client()
    if client:
        try:
            for key in client.scan_iter(match=f"{CACHE_PREFIX}:*"):
                client.delete(key)
        except Exception:
            pass

    _memory_cache.clear()
