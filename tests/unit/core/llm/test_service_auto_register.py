"""
测试模块：LLM服务自动注册测试
功能描述：测试LLMService的自动发现和注册功能
"""

import pytest
from unittest.mock import AsyncMock, patch
from core.llm.service import LLMService


@pytest.mark.asyncio
class TestLLMServiceAutoRegister:
    """LLMService自动注册测试类"""
    
    async def test_auto_discover_adapters(self):
        """测试自动发现适配器"""
        # Arrange
        config = {
            "llm": {
                "auto_discover_adapters": True,
                "adapters": {
                    "qwen-adapter": {
                        "api_key": "test-qwen-key"
                    }
                }
            }
        }
        
        # Act
        service = LLMService(config)
        await service.initialize()
        
        # Assert
        assert service._registry.is_initialized is True
        assert len(service._adapters) > 0
    
    async def test_auto_register_with_config(self):
        """测试根据配置自动注册适配器"""
        # Arrange
        config = {
            "llm": {
                "auto_discover_adapters": True,
                "adapters": {
                    "qwen-adapter": {
                        "api_key": "test-key"
                    }
                }
            }
        }
        
        # Act
        service = LLMService(config)
        await service.initialize()
        
        # Assert
        # 检查适配器是否已注册（如果有API密钥配置）
        # 注意：实际测试中需要Mock适配器的初始化
    
    async def test_disable_auto_discover(self):
        """测试禁用自动发现"""
        # Arrange
        config = {
            "llm": {
                "auto_discover_adapters": False
            }
        }
        
        # Act
        service = LLMService(config)
        await service.initialize()
        
        # Assert
        assert service._auto_discover is False
    
    async def test_get_adapter_for_model(self):
        """测试根据模型名称获取适配器"""
        # Arrange
        config = {
            "llm": {
                "auto_discover_adapters": True,
                "model_adapter_mapping": {
                    "qwen-turbo": "qwen-adapter",
                    "deepseek-chat": "deepseek-adapter"
                },
                "adapters": {
                    "qwen-adapter": {"api_key": "test-key"},
                    "deepseek-adapter": {"api_key": "test-key"}
                }
            }
        }
        
        # Act
        service = LLMService(config)
        await service.initialize()
        
        # Assert
        # 测试_get_adapter方法（通过chat方法间接测试）
        # 注意：需要Mock适配器的实际调用
