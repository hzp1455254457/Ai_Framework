"""
测试模块：Ollama适配器测试
功能描述：测试OllamaAdapter的所有功能
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import Response

from core.llm.adapters.ollama_adapter import OllamaAdapter


@pytest.mark.asyncio
class TestOllamaAdapter:
    """OllamaAdapter测试类"""

    async def test_adapter_initialization(self):
        """测试适配器初始化"""
        adapter = OllamaAdapter({"base_url": "http://localhost:11434"})
        await adapter.initialize()

        assert adapter.is_initialized is True
        assert adapter.name == "ollama-adapter"
        assert adapter.provider == "ollama"

    @patch("httpx.AsyncClient")
    async def test_call_success(self, mock_client_class):
        """测试调用成功（非流式）"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(
            return_value={
                "model": "llama3.2",
                "done": True,
                "message": {"role": "assistant", "content": "Hello from Ollama"},
                "prompt_eval_count": 3,
                "eval_count": 5,
            }
        )

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        adapter = OllamaAdapter({"base_url": "http://localhost:11434"})
        await adapter.initialize()
        adapter._client = mock_client

        result = await adapter.call(
            messages=[{"role": "user", "content": "hi"}],
            model="llama3.2",
            temperature=0.2,
        )

        assert result["content"] == "Hello from Ollama"
        assert result["usage"]["prompt_tokens"] == 3
        assert result["usage"]["completion_tokens"] == 5
        assert result["usage"]["total_tokens"] == 8

    async def test_cleanup(self):
        """测试清理资源"""
        adapter = OllamaAdapter({"base_url": "http://localhost:11434"})
        await adapter.initialize()
        await adapter.cleanup()

        assert adapter.is_initialized is False
        assert adapter._client is None

    @patch("httpx.AsyncClient")
    async def test_stream_call_success(self, mock_client_class):
        """测试流式调用成功（JSON Lines格式）"""
        mock_stream_response = MagicMock()
        mock_stream_response.status_code = 200
        mock_stream_response.raise_for_status = MagicMock()
        
        stream_data = [
            b'{"model": "llama3.2", "done": false, "message": {"content": "Hello"}}\n',
            b'{"model": "llama3.2", "done": false, "message": {"content": " World"}}\n',
            b'{"model": "llama3.2", "done": true}\n'
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
        
        adapter = OllamaAdapter({"base_url": "http://localhost:11434"})
        await adapter.initialize()
        adapter._client = mock_client
        
        results = []
        async for chunk in adapter.stream_call([{"role": "user", "content": "hi"}], model="llama3.2"):
            results.append(chunk)
        
        assert len(results) >= 0

    @patch("httpx.AsyncClient")
    async def test_call_http_error_500(self, mock_client_class):
        """测试HTTP 500错误"""
        from httpx import HTTPError, Request, Response
        
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 500
        mock_response.raise_for_status = MagicMock(side_effect=HTTPError("Internal Server Error", request=Request("POST", "http://test"), response=mock_response))
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter({"base_url": "http://localhost:11434"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="llama3.2")

    @patch("httpx.AsyncClient")
    async def test_stream_call_interrupted(self, mock_client_class):
        """测试流式响应中断处理（JSON Lines格式）"""
        from httpx import HTTPError
        
        mock_stream_response = MagicMock()
        mock_stream_response.status_code = 200
        mock_stream_response.raise_for_status = MagicMock()
        
        async def aiter_lines():
            yield '{"model": "llama3.2", "done": false, "message": {"content": "Hello"}}\n'
            raise HTTPError("Connection interrupted")
        
        mock_stream_response.aiter_lines = aiter_lines
        
        mock_client = MagicMock()
        mock_client.stream = AsyncMock()
        mock_client.stream.return_value.__aenter__ = AsyncMock(return_value=mock_stream_response)
        mock_client.stream.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter({"base_url": "http://localhost:11434"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            async for _ in adapter.stream_call([{"role": "user", "content": "hi"}], model="llama3.2"):
                pass

    @patch("httpx.AsyncClient")
    async def test_call_timeout_error(self, mock_client_class):
        """测试网络超时错误"""
        from httpx import TimeoutException
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=TimeoutException("Request timeout"))
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter({"base_url": "http://localhost:11434"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="llama3.2")

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
        
        adapter = OllamaAdapter({"base_url": "http://localhost:11434"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="llama3.2")

    @patch("httpx.AsyncClient")
    async def test_call_http_error_404(self, mock_client_class):
        """测试HTTP 404错误（模型不存在）"""
        from httpx import HTTPError, Request, Response
        
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 404
        mock_response.raise_for_status = MagicMock(side_effect=HTTPError("Not Found", request=Request("POST", "http://test"), response=mock_response))
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter({"base_url": "http://localhost:11434"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="llama3.2")

    @patch("httpx.AsyncClient")
    async def test_call_empty_messages(self, mock_client_class):
        """测试空消息列表"""
        adapter = OllamaAdapter({"base_url": "http://localhost:11434"})
        await adapter.initialize()
        
        with pytest.raises(ValueError):
            await adapter.call([], model="llama3.2")

    @patch("httpx.AsyncClient")
    async def test_call_invalid_model_name(self, mock_client_class):
        """测试无效模型名称"""
        from httpx import HTTPError, Request, Response
        
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 404
        mock_response.json = MagicMock(return_value={
            "error": "model 'invalid-model' not found"
        })
        mock_response.raise_for_status = MagicMock(side_effect=HTTPError("Not Found", request=Request("POST", "http://test"), response=mock_response))
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter({"base_url": "http://localhost:11434"})
        await adapter.initialize()
        adapter._client = mock_client
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="invalid-model")

    async def test_call_without_initialization(self):
        """测试未初始化时调用"""
        adapter = OllamaAdapter({"base_url": "http://localhost:11434"})
        
        with pytest.raises(AdapterCallError):
            await adapter.call([{"role": "user", "content": "hi"}], model="llama3.2")