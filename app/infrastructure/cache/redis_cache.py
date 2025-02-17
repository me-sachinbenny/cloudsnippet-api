from typing import Any, Optional, Union, Dict
from datetime import timedelta
import json
import aioredis
from .base import BaseCache

class RedisCache(BaseCache):
    """Redis-based distributed cache implementation."""
    
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379",
        prefix: str = "cache:"
    ):
        self._redis = aioredis.from_url(redis_url)
        self._prefix = prefix
    
    def _key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self._prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Cache-aside (Lazy Loading) pattern implementation."""
        value = await self._redis.get(self._key(key))
        if value is None:
            return None
        return json.loads(value)
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Write-through pattern implementation."""
        serialized = json.dumps(value)
        if ttl is None:
            return await self._redis.set(self._key(key), serialized)
        
        if isinstance(ttl, timedelta):
            ttl = int(ttl.total_seconds())
        
        return await self._redis.setex(
            self._key(key), 
            ttl,
            serialized
        )
    
    async def delete(self, key: str) -> bool:
        """Remove a key from cache."""
        return bool(await self._redis.delete(self._key(key)))
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return bool(await self._redis.exists(self._key(key)))
    
    async def clear(self) -> bool:
        """Clear all cache entries with prefix."""
        cursor = 0
        while True:
            cursor, keys = await self._redis.scan(
                cursor,
                match=f"{self._prefix}*",
                count=100
            )
            if keys:
                await self._redis.delete(*keys)
            if cursor == 0:
                break
        return True
    
    async def get_many(self, keys: list[str]) -> Dict[str, Any]:
        """Batch get operation."""
        prefixed_keys = [self._key(key) for key in keys]
        values = await self._redis.mget(prefixed_keys)
        result = {}
        for key, value in zip(keys, values):
            if value is not None:
                result[key] = json.loads(value)
        return result
    
    async def set_many(
        self, 
        mapping: Dict[str, Any], 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Batch set operation."""
        pipe = self._redis.pipeline()
        for key, value in mapping.items():
            serialized = json.dumps(value)
            if ttl is None:
                pipe.set(self._key(key), serialized)
            else:
                if isinstance(ttl, timedelta):
                    ttl = int(ttl.total_seconds())
                pipe.setex(self._key(key), ttl, serialized)
        await pipe.execute()
        return True
    
    async def delete_many(self, keys: list[str]) -> bool:
        """Batch delete operation."""
        prefixed_keys = [self._key(key) for key in keys]
        await self._redis.delete(*prefixed_keys)
        return True
    
    async def close(self):
        """Close Redis connection."""
        await self._redis.close()
