"""
测试模块：缓存管理模块测试
功能描述：测试CacheManager与MemoryCacheBackend
"""

import asyncio
import pytest

from infrastructure.cache.manager import CacheManager
from infrastructure.cache.backends.memory import MemoryCacheBackend


@pytest.mark.asyncio
class TestCacheManager:
    """CacheManager测试类"""

    async def test_create_memory_backend(self):
        """基于配置创建memory后端"""
        manager = CacheManager({"cache": {"backend": "memory", "ttl": 1, "max_size": 10}})
        assert isinstance(manager.backend, MemoryCacheBackend)

    async def test_get_set_delete(self):
        """get/set/delete基础流程"""
        manager = CacheManager({"cache": {"backend": "memory", "ttl": 60, "max_size": 10}})
        await manager.set("k1", {"v": 1})
        assert await manager.get("k1") == {"v": 1}
        await manager.delete("k1")
        assert await manager.get("k1") is None

    async def test_ttl_expire(self):
        """TTL过期"""
        manager = CacheManager({"cache": {"backend": "memory", "ttl": 1, "max_size": 10}})
        await manager.set("k1", "v1", ttl=1)
        assert await manager.get("k1") == "v1"
        await asyncio.sleep(1.1)
        assert await manager.get("k1") is None

    async def test_lru_eviction(self):
        """LRU淘汰：超过max_size时淘汰最久未访问项"""
        manager = CacheManager({"cache": {"backend": "memory", "ttl": 60, "max_size": 2}})

        await manager.set("k1", "v1")
        await manager.set("k2", "v2")
        # 访问k1，使k2成为最旧
        assert await manager.get("k1") == "v1"
        await manager.set("k3", "v3")  # 触发淘汰

        assert await manager.get("k2") is None
        assert await manager.get("k1") == "v1"
        assert await manager.get("k3") == "v3"

    async def test_clear(self):
        """清空缓存"""
        manager = CacheManager({"cache": {"backend": "memory", "ttl": 60, "max_size": 10}})
        await manager.set("k1", "v1")
        await manager.clear()
        assert await manager.get("k1") is None

