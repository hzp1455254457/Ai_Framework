"""
模块名称：缓存管理器模块
功能描述：提供统一的缓存管理能力，支持多后端缓存
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - CacheManager: 缓存管理器
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .backends.base import BaseCacheBackend
from .backends.memory import MemoryCacheBackend


class CacheManager:
    """
    缓存管理器

    约定配置（来自 config/*.yaml）：
        cache:
          backend: "memory"
          ttl: 3600
          max_size: 1000
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config: Dict[str, Any] = config or {}
        self._backend: BaseCacheBackend = self._create_backend(self._config)

    def _create_backend(self, config: Dict[str, Any]) -> BaseCacheBackend:
        cache_cfg = config.get("cache", {}) if isinstance(config, dict) else {}
        backend = (cache_cfg.get("backend") or "memory").lower()

        if backend == "memory":
            ttl = int(cache_cfg.get("ttl", 3600))
            max_size = int(cache_cfg.get("max_size", 1000))
            return MemoryCacheBackend(default_ttl=ttl, max_size=max_size)

        # 未来扩展：redis/file 等
        raise ValueError(f"不支持的缓存后端: {backend}")

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        return await self._backend.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        await self._backend.set(key, value, ttl=ttl)

    async def delete(self, key: str) -> None:
        """删除缓存键"""
        await self._backend.delete(key)

    async def clear(self) -> None:
        """清空缓存"""
        await self._backend.clear()

    @property
    def backend(self) -> BaseCacheBackend:
        """获取当前缓存后端实例"""
        return self._backend

