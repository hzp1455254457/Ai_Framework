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

    @patch("httpx.AsyncClient")
    async def test_stream_call_success(self, mock_client_class):
        """测试流式调用成功"""
        mock_stream_response = MagicMock()
        mock_stream_response.status_code = 200
        mock_stream_response.raise_for_status = MagicMock()
        
        stream_data = [
            b'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n',
            b'data: {"choices": [{"delta": {"content": " World"}}]}\n\n',
            b'data: [DONE]\n\n'
        ]
        
        async def aiter_lines():
            for line in stream_data:
                yield line.decode('utf-8')
        
        mock_stream_response.aiter_lines = aiter_lines
        
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_stream_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_context_manager)
        mock_client_class.return_value = mock_client
        
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        
        results = []
        async for chunk in adapter.stream_call(messages, model="gpt-3.5-turbo"):
            results.append(chunk)
        
        assert len(results) == 2
        assert results[0]["content"] == "Hello"
        assert results[1]["content"] == " World"

    @patch("httpx.AsyncClient")
    async def test_call_http_error_401(self, mock_client_class):
        """测试HTTP 401错误"""
        from httpx import HTTPError, Request, Response
        
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 401
        mock_response.raise_for_status = MagicMock(side_effect=HTTPError("Unauthorized", request=Request("POST", "http://test"), response=mock_response))
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(AdapterCallError):
            await adapter.call(messages, model="gpt-3.5-turbo")

    @patch("httpx.AsyncClient")
    async def test_call_http_error_429(self, mock_client_class):
        """测试HTTP 429错误"""
        from httpx import HTTPError, Request, Response
        
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 429
        mock_response.raise_for_status = MagicMock(side_effect=HTTPError("Rate Limited", request=Request("POST", "http://test"), response=mock_response))
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(AdapterCallError):
            await adapter.call(messages, model="gpt-3.5-turbo")

    @patch("httpx.AsyncClient")
    async def test_stream_call_interrupted(self, mock_client_class):
        """测试流式响应中断处理"""
        from httpx import HTTPError
        
        mock_stream_response = MagicMock()
        mock_stream_response.status_code = 200
        mock_stream_response.raise_for_status = MagicMock()
        
        async def aiter_lines():
            yield 'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n'
            raise HTTPError("Connection interrupted")
        
        mock_stream_response.aiter_lines = aiter_lines
        
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_stream_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_context_manager)
        mock_client_class.return_value = mock_client
        
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(AdapterCallError):
            async for _ in adapter.stream_call(messages, model="gpt-3.5-turbo"):
                pass

    @patch("httpx.AsyncClient")
    async def test_call_timeout_error(self, mock_client_class):
        """测试网络超时错误"""
        from httpx import TimeoutException
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=TimeoutException("Request timeout"))
        mock_client_class.return_value = mock_client
        
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(AdapterCallError):
            await adapter.call(messages, model="gpt-3.5-turbo")

    @patch("httpx.AsyncClient")
    async def test_call_http_error_400(self, mock_client_class):
        """测试HTTP 400错误"""
        from httpx import HTTPError, Request, Response
        
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 400
        mock_response.raise_for_status = MagicMock(side_effect=HTTPError("Bad Request", request=Request("POST", "http://test"), response=mock_response))
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(AdapterCallError):
            await adapter.call(messages, model="gpt-3.5-turbo")

    @patch("httpx.AsyncClient")
    async def test_call_http_error_403(self, mock_client_class):
        """测试HTTP 403错误（禁止访问）"""
        from httpx import HTTPError, Request, Response
        
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 403
        mock_response.raise_for_status = MagicMock(side_effect=HTTPError("Forbidden", request=Request("POST", "http://test"), response=mock_response))
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(AdapterCallError):
            await adapter.call(messages, model="gpt-3.5-turbo")

    @patch("httpx.AsyncClient")
    async def test_call_http_error_500(self, mock_client_class):
        """测试HTTP 500错误（服务器错误）"""
        from httpx import HTTPError, Request, Response
        
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 500
        mock_response.raise_for_status = MagicMock(side_effect=HTTPError("Internal Server Error", request=Request("POST", "http://test"), response=mock_response))
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(AdapterCallError):
            await adapter.call(messages, model="gpt-3.5-turbo")

    @patch("httpx.AsyncClient")
    async def test_call_empty_messages(self, mock_client_class):
        """测试空消息列表"""
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        
        with pytest.raises(ValueError):
            await adapter.call([], model="gpt-3.5-turbo")

    @patch("httpx.AsyncClient")
    async def test_call_invalid_model_name(self, mock_client_class):
        """测试无效模型名称"""
        from httpx import HTTPError, Request, Response
        
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 400
        mock_response.json = MagicMock(return_value={
            "error": {
                "message": "Invalid model name",
                "type": "invalid_request_error"
            }
        })
        mock_response.raise_for_status = MagicMock(side_effect=HTTPError("Bad Request", request=Request("POST", "http://test"), response=mock_response))
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(AdapterCallError):
            await adapter.call(messages, model="invalid-model-name")

    @patch("httpx.AsyncClient")
    async def test_call_invalid_response_format(self, mock_client_class):
        """测试响应格式错误"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"invalid": "response"})
        mock_response.raise_for_status = MagicMock()
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(AdapterCallError):
            await adapter.call(messages, model="gpt-3.5-turbo")

    async def test_call_without_initialization(self):
        """测试未初始化时调用"""
        adapter = OpenAIAdapter({"api_key": "sk-test-key"})
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "Hello"}], model="gpt-3.5-turbo")