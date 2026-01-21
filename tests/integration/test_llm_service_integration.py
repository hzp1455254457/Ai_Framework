"""
集成测试：LLM服务集成测试
功能描述：测试LLMService与其他模块的集成
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.llm.service import LLMService
from core.llm.adapters.base import BaseLLMAdapter
from infrastructure.config import ConfigManager


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
    
    async def stream_call(self, messages, model, **kwargs):
        yield {
            "content": "Mock",
            "usage": {"total_tokens": 5},
            "metadata": {},
        }
        yield {
            "content": " response",
            "usage": {"total_tokens": 5},
            "metadata": {},
        }


@pytest.mark.asyncio
class TestLLMServiceIntegration:
    """LLM服务集成测试类"""
    
    async def test_service_with_config_manager(self):
        """测试服务与配置管理器的集成"""
        # Arrange
        import tempfile as tf
        import yaml
        from pathlib import Path
        
        with tf.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()
            
            # 创建配置文件
            config_data = {
                "llm": {
                    "default_model": "mock-model",
                    "auto_discover_adapters": False,
                }
            }
            with open(config_dir / "default.yaml", "w", encoding="utf-8") as f:
                yaml.dump(config_data, f)
            
            # 加载配置
            config_manager = ConfigManager.load(env="default", config_dir=str(config_dir))
            
            # 将ConfigManager转换为字典（因为LLMService期望字典）
            # 或者直接使用config_manager.config
            config_dict = config_manager.config if hasattr(config_manager, 'config') else {}
            
            # Act
            service = LLMService(config_dict)
            await service.initialize()
            
            # 注册适配器
            adapter = MockAdapter({})
            await adapter.initialize()
            service.register_adapter(adapter)
            
            # Assert
            assert service.is_initialized is True
            assert service._default_model == "mock-model"
    
    async def test_service_chat_full_flow(self):
        """测试完整的聊天流程"""
        # Arrange
        config = {
            "llm": {
                "default_model": "mock-model",
                "auto_discover_adapters": False,
            }
        }
        service = LLMService(config)
        await service.initialize()
        
        adapter = MockAdapter({})
        await adapter.initialize()
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act
        response = await service.chat(messages)
        
        # Assert
        assert response.content == "Mock response"
        assert response.total_tokens == 10
    
    async def test_service_stream_chat_full_flow(self):
        """测试完整的流式聊天流程"""
        # Arrange
        config = {
            "llm": {
                "default_model": "mock-model",
                "auto_discover_adapters": False,
            }
        }
        service = LLMService(config)
        await service.initialize()
        
        adapter = MockAdapter({})
        await adapter.initialize()
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act
        chunks = []
        async for chunk in service.stream_chat(messages):
            chunks.append(chunk)
        
        # Assert
        assert len(chunks) == 2
        assert chunks[0].content == "Mock"
        assert chunks[1].content == " response"
    
    async def test_service_cleanup(self):
        """测试服务清理"""
        # Arrange
        config = {
            "llm": {
                "auto_discover_adapters": False,
            }
        }
        service = LLMService(config)
        await service.initialize()
        
        adapter = MockAdapter({})
        await adapter.initialize()
        service.register_adapter(adapter)
        
        # Act
        await service.cleanup()
        
        # Assert
        assert service.is_initialized is False
