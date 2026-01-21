"""
模块名称：内存缓存后端模块
功能描述：提供基于内存的缓存实现（支持TTL与LRU）
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队
"""

from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional

from .base import BaseCacheBackend


@dataclass
class _CacheEntry:
    value: Any
    expires_at: Optional[float]

    def is_expired(self, now: float) -> bool:
        if self.expires_at is None:
            return False
        return now >= self.expires_at


class MemoryCacheBackend(BaseCacheBackend):
    """
    内存缓存后端（LRU + TTL）

    设计：
        - 使用OrderedDict维护LRU顺序（最近访问放到末尾）
        - 每次get/set会清理过期项
    """

    def __init__(self, default_ttl: int = 3600, max_size: int = 1000) -> None:
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._store: "OrderedDict[str, _CacheEntry]" = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            now = time.time()
            entry = self._store.get(key)
            if entry is None:
                return None

            if entry.is_expired(now):
                self._store.pop(key, None)
                return None

            # LRU: move to end
            self._store.move_to_end(key, last=True)
            return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        async with self._lock:
            now = time.time()
            self._purge_expired_locked(now)

            effective_ttl = ttl if ttl is not None else self._default_ttl
            expires_at = None if effective_ttl <= 0 else now + float(effective_ttl)

            self._store[key] = _CacheEntry(value=value, expires_at=expires_at)
            self._store.move_to_end(key, last=True)

            self._evict_if_needed_locked()

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()

    def _purge_expired_locked(self, now: float) -> None:
        # OrderedDict: we must iterate keys snapshot
        expired_keys = [k for k, v in self._store.items() if v.is_expired(now)]
        for k in expired_keys:
            self._store.pop(k, None)

    def _evict_if_needed_locked(self) -> None:
        while len(self._store) > self._max_size:
            # pop least-recently-used
            self._store.popitem(last=False)

