"""
测试模块：适配器基类测试
功能描述：测试BaseAdapter的所有功能
"""

import pytest
from typing import Dict, Any
from core.base.adapter import (
    BaseAdapter,
    AdapterError,
    AdapterConfigurationError,
    AdapterCallError,
)


class ConcreteAdapter(BaseAdapter):
    """用于测试的具体适配器实现"""
    
    @property
    def name(self) -> str:
        return "test-adapter"
    
    @property
    def provider(self) -> str:
        return "test-provider"
    
    async def call(self, *args, **kwargs) -> Dict[str, Any]:
        """实现调用逻辑"""
        return {
            "content": "test response",
            "metadata": {"tokens": 10}
        }


@pytest.mark.asyncio
class TestBaseAdapter:
    """BaseAdapter测试类"""
    
    async def test_adapter_initialization(self):
        """测试适配器初始化"""
        # Arrange
        config = {"api_key": "test-key"}
        adapter = ConcreteAdapter(config)
        
        # Act
        await adapter.initialize()
        
        # Assert
        assert adapter.is_initialized is True
        assert adapter.name == "test-adapter"
        assert adapter.provider == "test-provider"
    
    async def test_adapter_call(self):
        """测试适配器调用"""
        # Arrange
        adapter = ConcreteAdapter()
        await adapter.initialize()
        
        # Act
        response = await adapter.call(messages=[{"role": "user", "content": "test"}])
        
        # Assert
        assert response["content"] == "test response"
        assert "metadata" in response
    
    async def test_adapter_stream_call(self):
        """测试适配器流式调用"""
        # Arrange
        adapter = ConcreteAdapter()
        await adapter.initialize()
        
        # Act
        chunks = []
        async for chunk in adapter.stream_call(messages=[{"role": "user", "content": "test"}]):
            chunks.append(chunk)
        
        # Assert
        assert len(chunks) == 1
        assert chunks[0]["content"] == "test response"
    
    async def test_adapter_cleanup(self):
        """测试适配器清理"""
        # Arrange
        adapter = ConcreteAdapter()
        await adapter.initialize()
        
        # Act
        await adapter.cleanup()
        
        # Assert
        assert adapter.is_initialized is False
    
    async def test_adapter_context_manager(self):
        """测试异步上下文管理器"""
        # Arrange
        config = {"api_key": "test"}
        
        # Act
        async with ConcreteAdapter(config) as adapter:
            assert adapter.is_initialized is True
            response = await adapter.call()
            assert response is not None
        
        # Assert
        assert adapter.is_initialized is False
    
    async def test_adapter_config_access(self):
        """测试配置访问"""
        # Arrange
        config = {"key1": "value1"}
        adapter = ConcreteAdapter(config)
        
        # Act
        retrieved_config = adapter.config
        
        # Assert
        assert retrieved_config == config
        # 确保返回的是副本
        retrieved_config["new_key"] = "new_value"
        assert "new_key" not in adapter.config
