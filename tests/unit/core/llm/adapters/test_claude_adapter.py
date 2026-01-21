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

