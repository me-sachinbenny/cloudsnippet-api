from abc import ABC, abstractmethod
from typing import Any, Optional, Union, Dict
from datetime import datetime, timedelta

class BaseCache(ABC):
    """Base interface for all cache implementations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Cache-aside (Lazy Loading) pattern: Get value from cache."""
        pass
    
    @abstractmethod
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Write-through pattern: Set value in cache with optional TTL."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Remove a key from cache."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    async def get_many(self, keys: list[str]) -> Dict[str, Any]:
        """Batch get operation."""
        pass
    
    @abstractmethod
    async def set_many(
        self, 
        mapping: Dict[str, Any], 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Batch set operation."""
        pass
    
    @abstractmethod
    async def delete_many(self, keys: list[str]) -> bool:
        """Batch delete operation."""
        pass
    
    async def get_or_set(
        self, 
        key: str, 
        default_func: callable,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> Any:
        """Read-through pattern: Get from cache or compute and store."""
        value = await self.get(key)
        if value is None:
            value = await default_func()
            await self.set(key, value, ttl)
        return value
    
    async def write_behind(
        self, 
        key: str, 
        value: Any,
        persist_func: callable,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Write-behind pattern: Update cache and async persist."""
        success = await self.set(key, value, ttl)
        if success:
            # Schedule async persistence
            await persist_func(key, value)
        return success
