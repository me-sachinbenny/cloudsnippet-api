"""
Core caching functionality and implementations.
This module provides various caching patterns and strategies.
"""

from .base import BaseCache
from .memory_cache import MemoryCache
from .redis_cache import RedisCache
from .cache_manager import CacheManager

__all__ = ['BaseCache', 'MemoryCache', 'RedisCache', 'CacheManager']
