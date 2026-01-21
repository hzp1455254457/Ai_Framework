"""
测试模块：OpenAI适配器测试
功能描述：测试OpenAIAdapter的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import Response
from core.llm.adapters.openai_adapter import OpenAIAdapter
from core.base.adapter import AdapterCallError


@pytest.mark.asyncio
class TestOpenAIAdapter:
    """OpenAIAdapter测试类"""
    
    async def test_adapter_initialization(self):
        """测试适配器初始化"""
        # Arrange
        config = {"api_key": "sk-test-key"}
        adapter = OpenAIAdapter(config)
        
        # Act
        await adapter.initialize()
        
        # Assert
        assert adapter.is_initialized is True
        assert adapter.name == "openai-adapter"
        assert adapter.provider == "openai"
    
    async def test_adapter_initialization_without_api_key(self):
        """测试缺少API密钥时抛出异常"""
        # Arrange
        adapter = OpenAIAdapter({})
        
        # Act & Assert
        with pytest.raises(AdapterCallError):
            await adapter.initialize()
    
    @patch("httpx.AsyncClient")
    async def test_call_success(self, mock_client_class):
        """测试调用成功"""
        # Arrange
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={
            "choices": [{
                "message": {"content": "Hello from OpenAI"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 5,
                "completion_tokens": 10,
                "total_tokens": 15
            },
            "model": "gpt-3.5-turbo"
        })
        mock_response.raise_for_status = MagicMock()
        
        # Mock AsyncClient实例
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        
        # 替换adapter的client为mock client
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act
        result = await adapter.call(messages, model="gpt-3.5-turbo")
        
        # Assert
        assert result["content"] == "Hello from OpenAI"
        assert result["usage"]["total_tokens"] == 15
        assert result["metadata"]["model"] == "gpt-3.5-turbo"
    
    @patch("httpx.AsyncClient")
    async def test_call_with_function_calling(self, mock_client_class):
        """测试Function Calling支持"""
        # Arrange
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={
            "choices": [{
                "message": {
                    "content": None,
                    "function_call": {
                        "name": "get_weather",
                        "arguments": '{"city": "Beijing"}'
                    }
                },
                "finish_reason": "function_call"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            },
            "model": "gpt-3.5-turbo"
        })
        mock_response.raise_for_status = MagicMock()
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "What's the weather in Beijing?"}]
        
        # Act
        result = await adapter.call(
            messages,
            model="gpt-3.5-turbo",
            functions=[{
                "name": "get_weather",
                "description": "Get weather information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    }
                }
            }]
        )
        
        # Assert
        assert result["content"] is None or result["content"] == ""
        assert result["metadata"]["function_call"] is not None
        assert result["metadata"]["function_call"]["name"] == "get_weather"
    
    async def test_cleanup(self):
        """测试清理资源"""
        # Arrange
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        
        # Act
        await adapter.cleanup()
        
        # Assert
        assert adapter.is_initialized is False
        assert adapter._client is None
