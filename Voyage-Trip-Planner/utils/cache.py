# Caching mechanisms

"""
Caching utilities using diskcache for persistent caching across sessions.
Reduces API calls and speeds up repeated queries.
"""

import diskcache
import hashlib
import json
import functools
from pathlib import Path
from typing import Any, Callable, Optional
from utils.logger import logger


# Initialize disk cache
CACHE_DIR = Path(".cache/trip_planner")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

cache = diskcache.Cache(str(CACHE_DIR), size_limit=500 * 1024 * 1024)  # 500MB limit


def make_cache_key(*args, **kwargs) -> str:
    """Generate a unique cache key from arguments."""
    key_data = {"args": args, "kwargs": kwargs}
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl: int = 3600, prefix: str = ""):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time-to-live in seconds (default: 1 hour)
        prefix: Cache key prefix for namespacing
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{prefix}:{func.__name__}:{make_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache HIT for key: {cache_key[:50]}...")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache MISS for key: {cache_key[:50]}...")
            result = func(*args, **kwargs)
            
            if result is not None:
                cache.set(cache_key, result, expire=ttl)
            
            return result
        return wrapper
    return decorator


def clear_cache(prefix: Optional[str] = None):
    """Clear cache entries, optionally filtered by prefix."""
    if prefix:
        keys_to_delete = [k for k in cache.iterkeys() if str(k).startswith(prefix)]
        for key in keys_to_delete:
            del cache[key]
        logger.info(f"Cleared {len(keys_to_delete)} cache entries with prefix: {prefix}")
    else:
        cache.clear()
        logger.info("Cleared all cache entries")


def get_cache_stats() -> dict:
    """Return cache statistics."""
    return {
        "size": cache.volume(),
        "count": len(cache),
        "directory": str(CACHE_DIR)
    }