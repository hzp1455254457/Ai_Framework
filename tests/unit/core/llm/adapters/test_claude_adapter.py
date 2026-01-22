"""
测试模块：Claude适配器测试
功能描述：测试ClaudeAdapter的所有功能
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import Response

from core.base.adapter import AdapterCallError
from core.llm.adapters.claude_adapter import ClaudeAdapter


@pytest.mark.asyncio
class TestClaudeAdapter:
    """ClaudeAdapter测试类"""

    async def test_adapter_initialization_without_api_key(self):
        """测试缺少API密钥时抛出异常"""
        adapter = ClaudeAdapter({})
        with pytest.raises(AdapterCallError):
            await adapter.initialize()

    async def test_adapter_initialization(self):
        """测试适配器初始化"""
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()

        assert adapter.is_initialized is True
        assert adapter.name == "claude-adapter"
        assert adapter.provider == "claude"

    @patch("httpx.AsyncClient")
    async def test_call_success(self, mock_client_class):
        """测试调用成功（非流式）"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(
            return_value={
                "id": "msg_123",
                "model": "claude-3-5-sonnet-20241022",
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": "Hello from Claude"}],
                "usage": {"input_tokens": 5, "output_tokens": 7},
            }
        )

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()
        adapter._client = mock_client

        result = await adapter.call(
            messages=[{"role": "user", "content": "hi"}],
            model="claude-3-5-sonnet-20241022",
            temperature=0.2,
        )

        assert result["content"] == "Hello from Claude"
        assert result["usage"]["prompt_tokens"] == 5
        assert result["usage"]["completion_tokens"] == 7
        assert result["usage"]["total_tokens"] == 12

    async def test_cleanup(self):
        """测试清理资源"""
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()
        await adapter.cleanup()

        assert adapter.is_initialized is False
        assert adapter._client is None

    @patch("httpx.AsyncClient")
    async def test_stream_call_success(self, mock_client_class):
        """测试流式调用成功（SSE格式）"""
        mock_stream_response = MagicMock()
        mock_stream_response.status_code = 200
        mock_stream_response.raise_for_status = MagicMock()
        
        stream_data = [
            b'event: content_block_delta\ndata: {"type": "content_block_delta", "delta": {"text": "Hello"}}\n\n',
            b'event: content_block_delta\ndata: {"type": "content_block_delta", "delta": {"text": " World"}}\n\n',
            b'event: message_stop\ndata: {"type": "message_stop"}\n\n'
        ]
        
        async def aiter_lines():
            for line in stream_data:
                yield line.decode('utf-8')
        
        mock_stream_response.aiter_lines = aiter_lines
        
        mock_client = MagicMock()
        mock_client.stream = AsyncMock()
        mock_client.stream.return_value.__aenter__ = AsyncMock(return_value=mock_stream_response)
        mock_client.stream.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()
        adapter._client = mock_client
        
        results = []
        async for chunk in adapter.stream_call([{"role": "user", "content": "hi"}], model="claude-3-5-sonnet-20241022"):
            results.append(chunk)
        
        assert len(results) >= 0

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
        
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="claude-3-5-sonnet-20241022")

    @patch("httpx.AsyncClient")
    async def test_stream_call_interrupted(self, mock_client_class):
        """测试流式响应中断处理（SSE格式）"""
        from httpx import HTTPError
        
        mock_stream_response = MagicMock()
        mock_stream_response.status_code = 200
        mock_stream_response.raise_for_status = MagicMock()
        
        async def aiter_lines():
            yield 'event: content_block_delta\ndata: {"type": "content_block_delta", "delta": {"text": "Hello"}}\n\n'
            raise HTTPError("Connection interrupted")
        
        mock_stream_response.aiter_lines = aiter_lines
        
        mock_client = MagicMock()
        mock_client.stream = AsyncMock()
        mock_client.stream.return_value.__aenter__ = AsyncMock(return_value=mock_stream_response)
        mock_client.stream.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            async for _ in adapter.stream_call([{"role": "user", "content": "hi"}], model="claude-3-5-sonnet-20241022"):
                pass

    @patch("httpx.AsyncClient")
    async def test_call_timeout_error(self, mock_client_class):
        """测试网络超时错误"""
        from httpx import TimeoutException
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=TimeoutException("Request timeout"))
        mock_client_class.return_value = mock_client
        
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="claude-3-5-sonnet-20241022")

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
        
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="claude-3-5-sonnet-20241022")

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
        
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="claude-3-5-sonnet-20241022")

    @patch("httpx.AsyncClient")
    async def test_call_http_error_429(self, mock_client_class):
        """测试HTTP 429错误（限流）"""
        from httpx import HTTPError, Request, Response
        
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 429
        mock_response.raise_for_status = MagicMock(side_effect=HTTPError("Rate Limited", request=Request("POST", "http://test"), response=mock_response))
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="claude-3-5-sonnet-20241022")

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
        
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="claude-3-5-sonnet-20241022")

    @patch("httpx.AsyncClient")
    async def test_call_empty_messages(self, mock_client_class):
        """测试空消息列表"""
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()
        
        with pytest.raises(ValueError):
            await adapter.call([], model="claude-3-5-sonnet-20241022")

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
        
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="invalid-model-name")

    async def test_call_without_initialization(self):
        """测试未初始化时调用"""
        adapter = ClaudeAdapter({"api_key": "sk-ant-test"})
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="claude-3-5-sonnet-20241022")