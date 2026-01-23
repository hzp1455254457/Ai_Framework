"""
测试模块：适配器工厂测试
功能描述：测试AdapterFactory的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.llm.adapters.factory import AdapterFactory
from core.llm.adapters.registry import AdapterRegistry
from core.llm.adapters.base import BaseLLMAdapter
from core.llm.connection_pool import ConnectionPoolManager


class MockAdapter(BaseLLMAdapter):
    """用于测试的Mock适配器"""
    
    def __init__(self, config=None, connection_pool=None):
        super().__init__(config, connection_pool)
        self._initialized = False
    
    @property
    def name(self) -> str:
        return "mock-adapter"
    
    @property
    def provider(self) -> str:
        return "mock"
    
    async def initialize(self, config=None):
        self._initialized = True
        await super().initialize(config)
    
    async def call(self, messages, model, **kwargs):
        return {
            "content": "Mock response",
            "usage": {"total_tokens": 10},
            "metadata": {},
        }


@pytest.mark.asyncio
class TestAdapterFactory:
    """AdapterFactory测试类"""
    
    async def test_factory_initialization(self):
        """测试工厂初始化"""
        # Arrange
        registry = AdapterRegistry()
        
        # Act
        factory = AdapterFactory(registry)
        
        # Assert
        assert factory._registry == registry
        assert factory._cache == {}
    
    async def test_create_adapter_without_cache(self):
        """测试创建适配器（无缓存）"""
        # Arrange
        registry = AdapterRegistry()
        registry.register_adapter("mock-adapter", MockAdapter)
        factory = AdapterFactory(registry)
        config = {"api_key": "test-key"}
        
        # Act
        adapter = await factory.create_adapter("mock-adapter", config)
        
        # Assert
        assert adapter is not None
        assert adapter.name == "mock-adapter"
        assert adapter._initialized is True
        assert "mock-adapter" in factory._cache
    
    async def test_create_adapter_with_cache(self):
        """测试创建适配器（使用缓存）"""
        # Arrange
        registry = AdapterRegistry()
        registry.register_adapter("mock-adapter", MockAdapter)
        factory = AdapterFactory(registry)
        config = {"api_key": "test-key"}
        
        # 第一次创建
        adapter1 = await factory.create_adapter("mock-adapter", config)
        
        # Act - 第二次创建（应该使用缓存）
        adapter2 = await factory.create_adapter("mock-adapter", config)
        
        # Assert
        assert adapter1 is adapter2  # 应该是同一个实例
        assert len(factory._cache) == 1
    
    async def test_create_adapter_with_connection_pool(self):
        """测试创建适配器（带连接池）"""
        # Arrange
        registry = AdapterRegistry()
        registry.register_adapter("mock-adapter", MockAdapter)
        factory = AdapterFactory(registry)
        config = {"api_key": "test-key"}
        connection_pool = MagicMock(spec=ConnectionPoolManager)
        
        # Act
        adapter = await factory.create_adapter("mock-adapter", config, connection_pool=connection_pool)
        
        # Assert
        assert adapter is not None
        assert adapter._connection_pool == connection_pool
    
    async def test_create_adapter_not_found(self):
        """测试创建不存在的适配器"""
        # Arrange
        registry = AdapterRegistry()
        factory = AdapterFactory(registry)
        config = {"api_key": "test-key"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="适配器类型 'unknown-adapter' 未注册"):
            await factory.create_adapter("unknown-adapter", config)
    
    async def test_clear_cache(self):
        """测试清理缓存"""
        # Arrange
        registry = AdapterRegistry()
        registry.register_adapter("mock-adapter", MockAdapter)
        factory = AdapterFactory(registry)
        config = {"api_key": "test-key"}
        
        # 创建适配器（会缓存）
        await factory.create_adapter("mock-adapter", config)
        assert len(factory._cache) == 1
        
        # Act
        factory.clear_cache()
        
        # Assert
        assert len(factory._cache) == 0
    
    async def test_get_cached_adapter(self):
        """测试获取缓存的适配器"""
        # Arrange
        registry = AdapterRegistry()
        registry.register_adapter("mock-adapter", MockAdapter)
        factory = AdapterFactory(registry)
        config = {"api_key": "test-key"}
        
        # 创建适配器
        adapter = await factory.create_adapter("mock-adapter", config)
        cache_key = factory._get_cache_key("mock-adapter", config)
        
        # Act
        cached_adapter = factory.get_cached_adapter("mock-adapter", config)
        
        # Assert
        assert cached_adapter is adapter
        assert cached_adapter == factory._cache.get(cache_key)
