"""
缓存管理模块

提供统一的缓存接口和多后端支持（memory/redis/file）。
"""

from .manager import CacheManager
from .backends.base import BaseCacheBackend
from .backends.memory import MemoryCacheBackend

__all__ = [
    "CacheManager",
    "BaseCacheBackend",
    "MemoryCacheBackend",
]

