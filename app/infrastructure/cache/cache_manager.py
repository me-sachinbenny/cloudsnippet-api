from typing import Any, Optional, Union, Dict, List, Callable
from datetime import timedelta
import asyncio
from .base import BaseCache
from ...core.logging import get_logger
from .memory_cache import MemoryCache
from .redis_cache import RedisCache

logger = get_logger(__name__)

class CacheManager:
    """
    Hierarchical cache manager implementing various caching patterns.
    Supports L1 (memory) and L2 (distributed) caching with refresh-ahead.
    """
    
    def __init__(
        self,
        l1_cache: Optional[BaseCache] = None,
        l2_cache: Optional[BaseCache] = None,
        refresh_ahead_factor: float = 0.8
    ):
        """
        Initialize cache manager with optional L1 and L2 caches.
        
        Args:
            l1_cache: First level cache (typically MemoryCache)
            l2_cache: Second level cache (typically RedisCache)
            refresh_ahead_factor: Trigger refresh when TTL * factor remains
        """
        self.l1_cache = l1_cache or MemoryCache()
        self.l2_cache = l2_cache
        self.refresh_ahead_factor = refresh_ahead_factor
        self._refresh_tasks: Dict[str, asyncio.Task] = {}
    
    async def get(
        self,
        key: str,
        refresh_func: Optional[Callable] = None,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> Optional[Any]:
        """
        Hierarchical get with optional refresh-ahead.
        
        Args:
            key: Cache key
            refresh_func: Function to refresh data if needed
            ttl: Time-to-live for cached data
        """
        # Try L1 cache first
        value = await self.l1_cache.get(key)
        if value is not None:
            return value
        
        # On L1 miss, try L2 if available
        if self.l2_cache:
            value = await self.l2_cache.get(key)
            if value is not None:
                # Populate L1 cache
                await self.l1_cache.set(key, value, ttl)
                
                # Schedule refresh-ahead if needed
                if refresh_func and ttl:
                    self._schedule_refresh(key, refresh_func, ttl)
                
                return value
        
        # Cache miss
        if refresh_func:
            value = await refresh_func()
            if value is not None:
                await self.set(key, value, ttl)
            return value
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in all cache layers."""
        success = await self.l1_cache.set(key, value, ttl)
        if self.l2_cache:
            success &= await self.l2_cache.set(key, value, ttl)
        return success
    
    async def delete(self, key: str) -> bool:
        """Delete from all cache layers."""
        success = await self.l1_cache.delete(key)
        if self.l2_cache:
            success &= await self.l2_cache.delete(key)
        return success
    
    async def clear(self) -> bool:
        """Clear all cache layers."""
        success = await self.l1_cache.clear()
        if self.l2_cache:
            success &= await self.l2_cache.clear()
        return success
    
    def _schedule_refresh(
        self,
        key: str,
        refresh_func: Callable,
        ttl: Union[int, timedelta]
    ):
        """Schedule refresh-ahead task."""
        if isinstance(ttl, timedelta):
            ttl = int(ttl.total_seconds())
        
        async def refresh_task():
            try:
                await asyncio.sleep(ttl * self.refresh_ahead_factor)
                value = await refresh_func()
                if value is not None:
                    await self.set(key, value, ttl)
            except Exception as e:
                logger.error(f"Error in refresh-ahead task for key {key}: {e}")
            finally:
                self._refresh_tasks.pop(key, None)
        
        # Cancel existing refresh task if any
        if key in self._refresh_tasks:
            self._refresh_tasks[key].cancel()
        
        # Schedule new refresh task
        self._refresh_tasks[key] = asyncio.create_task(refresh_task())
    
    async def close(self):
        """Clean up resources."""
        # Cancel all refresh tasks
        for task in self._refresh_tasks.values():
            task.cancel()
        
        # Close L2 cache if it's Redis
        if isinstance(self.l2_cache, RedisCache):
            await self.l2_cache.close()
