"""
Cache Module - Simple in-memory caching with TTL
"""

from typing import Any, Optional
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib
import json


class CacheManager:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl_seconds: int = 1800):  # 30 minutes default
        self.cache = {}
        self.default_ttl = default_ttl_seconds
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Create cache key from arguments"""
        key_data = f"{prefix}:{json.dumps(args)}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            value, expiry = self.cache[key]
            if datetime.now() < expiry:
                return value
            else:
                # Expired, remove
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Set value in cache with TTL"""
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expiry)
    
    def invalidate(self, key: str):
        """Remove key from cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()


# Global cache instance
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
