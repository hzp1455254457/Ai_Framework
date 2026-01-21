"""
模块名称：缓存后端基类模块
功能描述：定义缓存后端的统一接口
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - BaseCacheBackend: 缓存后端基类
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class CacheError(Exception):
    """缓存模块异常基类"""


class BaseCacheBackend(ABC):
    """
    缓存后端基类

    说明：
        - 所有缓存后端均应实现异步接口（便于统一IO模型）
        - TTL 单位为秒；若 ttl 为 None，则由后端决定默认行为
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值（不存在返回None）"""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """删除缓存键"""

    @abstractmethod
    async def clear(self) -> None:
        """清空缓存"""

