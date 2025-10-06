from __future__ import annotations

import json
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar

T = TypeVar('T')


class DatabaseCache:
    """Simple in-memory cache for database query results."""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default TTL
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def _make_key(self, query: str, params: tuple = ()) -> str:
        """Create a cache key from query and parameters."""
        return f"{query}:{hash(params)}"
    
    def get(self, query: str, params: tuple = ()) -> Optional[Any]:
        """Get a cached result."""
        key = self._make_key(query, params)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry['expires']:
                return entry['data']
            else:
                # Expired, remove it
                del self._cache[key]
        return None
    
    def set(self, query: str, params: tuple, data: Any, ttl: Optional[int] = None) -> None:
        """Cache a query result."""
        key = self._make_key(query, params)
        ttl = ttl or self.default_ttl
        self._cache[key] = {
            'data': data,
            'expires': time.time() + ttl
        }
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate cache entries matching a pattern."""
        keys_to_remove = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_remove:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
    
    def size(self) -> int:
        """Get the number of cached entries."""
        return len(self._cache)


# Global cache instance
_cache = DatabaseCache()


def cached_query(ttl: int = 300, invalidate_on: Optional[str] = None):
    """Decorator to cache database query results."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = _cache.get(cache_key, ())
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache.set(cache_key, (), result, ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str) -> None:
    """Invalidate cache entries matching a pattern."""
    _cache.invalidate_pattern(pattern)


def clear_cache() -> None:
    """Clear all cache entries."""
    _cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return {
        'size': _cache.size(),
        'default_ttl': _cache.default_ttl
    }
