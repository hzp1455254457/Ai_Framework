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

