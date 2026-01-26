"""
LangChain LLM适配器单元测试

测试LangChainLLMWrapper和LangChainLLMProvider的功能。
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

# 检查LangChain是否可用
try:
    import langchain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not LANGCHAIN_AVAILABLE,
    reason="LangChain未安装，跳过测试"
)


@pytest.fixture
def mock_llm_provider():
    """创建模拟的ILLMProvider"""
    provider = Mock()
    provider._initialized = True
    provider.chat = AsyncMock(return_value=Mock(content="Test response"))
    provider.stream_chat = AsyncMock()
    provider.get_available_models = Mock(return_value=["gpt-3.5-turbo", "gpt-4"])
    provider.health_check = AsyncMock(return_value=True)
    provider.initialize = AsyncMock()
    provider.cleanup = AsyncMock()
    return provider


@pytest.fixture
def langchain_llm_config() -> Dict[str, Any]:
    """LangChain LLM配置"""
    return {
        "llm": {
            "default_model": "gpt-3.5-turbo",
            "timeout": 30,
        }
    }


@pytest.mark.asyncio
async def test_langchain_llm_wrapper_agenerate(mock_llm_provider):
    """测试LangChainLLMWrapper的_agenerate方法"""
    from core.implementations.langchain.langchain_llm import LangChainLLMWrapper
    
    wrapper = LangChainLLMWrapper(mock_llm_provider)
    result = await wrapper._agenerate(["Test prompt"])
    
    assert result is not None
    assert hasattr(result, "generations")
    mock_llm_provider.chat.assert_called_once()


@pytest.mark.asyncio
async def test_langchain_llm_provider_initialize(langchain_llm_config):
    """测试LangChainLLMProvider的initialize方法"""
    from core.implementations.langchain.langchain_llm import LangChainLLMProvider
    
    with patch("core.implementations.langchain.langchain_llm.LLMService") as mock_service:
        mock_service_instance = Mock()
        mock_service_instance.initialize = AsyncMock()
        mock_service.return_value = mock_service_instance
        
        provider = LangChainLLMProvider(langchain_llm_config)
        await provider.initialize()
        
        assert provider._initialized
        assert provider._langchain_llm is not None


@pytest.mark.asyncio
async def test_langchain_llm_provider_chat(langchain_llm_config):
    """测试LangChainLLMProvider的chat方法"""
    from core.implementations.langchain.langchain_llm import LangChainLLMProvider
    from core.llm.models import LLMResponse
    
    with patch("core.implementations.langchain.langchain_llm.LLMService") as mock_service:
        mock_service_instance = Mock()
        mock_service_instance.initialize = AsyncMock()
        mock_service_instance.chat = AsyncMock(return_value=LLMResponse(
            content="Test response",
            model="gpt-3.5-turbo"
        ))
        mock_service.return_value = mock_service_instance
        
        provider = LangChainLLMProvider(langchain_llm_config)
        response = await provider.chat([{"role": "user", "content": "Hello"}])
        
        assert response.content == "Test response"
        assert response.model == "gpt-3.5-turbo"
