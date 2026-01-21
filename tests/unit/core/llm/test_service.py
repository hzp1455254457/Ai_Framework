"""
测试模块：LLM服务测试
功能描述：测试LLMService的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from core.llm.service import LLMService, LLMError
from core.llm.adapters.base import BaseLLMAdapter


class MockAdapter(BaseLLMAdapter):
    """用于测试的Mock适配器"""
    
    @property
    def name(self) -> str:
        return "mock-adapter"
    
    @property
    def provider(self) -> str:
        return "mock"
    
    async def call(self, messages, model, **kwargs):
        return {
            "content": "Mock response",
            "usage": {"total_tokens": 10},
            "metadata": {},
        }


@pytest.mark.asyncio
class TestLLMService:
    """LLMService测试类"""
    
    async def test_service_initialization(self):
        """测试服务初始化"""
        # Arrange
        config = {
            "llm": {
                "default_model": "gpt-3.5-turbo"
            }
        }
        
        # Act
        service = LLMService(config)
        await service.initialize()
        
        # Assert
        assert service.is_initialized is True
    
    async def test_register_adapter(self):
        """测试注册适配器"""
        # Arrange
        config = {"llm": {}}
        service = LLMService(config)
        await service.initialize()
        adapter = MockAdapter()
        
        # Act
        service.register_adapter(adapter)
        
        # Assert
        assert "mock-adapter" in service._adapters
    
    async def test_chat_success(self):
        """测试聊天成功场景"""
        # Arrange
        config = {"llm": {"default_model": "gpt-3.5-turbo"}}
        service = LLMService(config)
        await service.initialize()
        
        adapter = MockAdapter()
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act
        response = await service.chat(messages)
        
        # Assert
        assert response.content == "Mock response"
        assert response.total_tokens == 10
    
    async def test_chat_with_empty_messages(self):
        """测试空消息列表时抛出异常"""
        # Arrange
        config = {"llm": {}}
        service = LLMService(config)
        await service.initialize()
        
        adapter = MockAdapter()
        service.register_adapter(adapter)
        
        # Act & Assert
        with pytest.raises(ValueError):
            await service.chat([])
    
    async def test_chat_without_adapter(self):
        """测试没有适配器时抛出异常"""
        # Arrange
        config = {"llm": {}}
        service = LLMService(config)
        await service.initialize()
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act & Assert
        with pytest.raises(LLMError):
            await service.chat(messages)
    
    async def test_stream_chat(self):
        """测试流式聊天"""
        # Arrange
        config = {"llm": {}}
        service = LLMService(config)
        await service.initialize()
        
        adapter = MockAdapter()
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act
        chunks = []
        async for chunk in service.stream_chat(messages):
            chunks.append(chunk)
        
        # Assert
        assert len(chunks) > 0
        assert chunks[0].content == "Mock response"
    
    async def test_calculate_tokens(self):
        """测试Token计算"""
        # Arrange
        config = {"llm": {}}
        service = LLMService(config)
        
        # Act
        tokens = service.calculate_tokens("Hello, world!", model="gpt-3.5-turbo")
        
        # Assert
        assert isinstance(tokens, int)
        assert tokens > 0
