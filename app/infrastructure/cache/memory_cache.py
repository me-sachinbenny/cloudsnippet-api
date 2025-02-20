from typing import Any, Optional, Union, Dict
from datetime import datetime, timedelta
import time
import asyncio
from collections import OrderedDict
from .base import BaseCache

class CacheEntry:
    """Represents a cache entry with value and expiration."""
    def __init__(
        self, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ):
        self.value = value
        if ttl:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            self.expires_at = time.time() + ttl
        else:
            self.expires_at = None
    
    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

class MemoryCache(BaseCache):
    """In-memory cache implementation with LRU eviction."""
    
    def __init__(self, max_size: int = 1000):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._lock = asyncio.Lock()
    
    async def _evict_if_needed(self):
        """LRU eviction if cache is full."""
        while len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)
    
    async def get(self, key: str) -> Optional[Any]:
        """Cache-aside (Lazy Loading) pattern implementation."""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            if entry.is_expired():
                del self._cache[key]
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return entry.value
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Write-through pattern implementation."""
        async with self._lock:
            await self._evict_if_needed()
            entry = CacheEntry(value, ttl)
            self._cache[key] = entry
            self._cache.move_to_end(key)
            return True
    
    async def delete(self, key: str) -> bool:
        """Remove a key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None or entry.is_expired():
                return False
            return True
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            return True
    
    async def get_many(self, keys: list[str]) -> Dict[str, Any]:
        """Batch get operation."""
        result = {}
        async with self._lock:
            for key in keys:
                value = await self.get(key)
                if value is not None:
                    result[key] = value
        return result
    
    async def set_many(
        self, 
        mapping: Dict[str, Any], 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Batch set operation."""
        async with self._lock:
            for key, value in mapping.items():
                await self.set(key, value, ttl)
            return True
    
    async def delete_many(self, keys: list[str]) -> bool:
        """Batch delete operation."""
        async with self._lock:
            for key in keys:
                await self.delete(key)
            return True
