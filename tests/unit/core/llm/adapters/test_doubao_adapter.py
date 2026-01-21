"""
测试模块：豆包适配器测试
功能描述：测试DoubaoAdapter的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import Response
from core.llm.adapters.doubao_adapter import DoubaoAdapter
from core.base.adapter import AdapterCallError


@pytest.mark.asyncio
class TestDoubaoAdapter:
    """DoubaoAdapter测试类"""
    
    async def test_adapter_initialization(self):
        """测试适配器初始化"""
        # Arrange
        config = {"api_key": "test-key"}
        adapter = DoubaoAdapter(config)
        
        # Act
        await adapter.initialize()
        
        # Assert
        assert adapter.is_initialized is True
        assert adapter.name == "doubao-adapter"
        assert adapter.provider == "doubao"
    
    async def test_adapter_initialization_without_api_key(self):
        """测试缺少API密钥时抛出异常"""
        # Arrange
        adapter = DoubaoAdapter({})
        
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
                "message": {"content": "Hello from Doubao"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 5,
                "completion_tokens": 10,
                "total_tokens": 15
            },
            "model": "doubao-pro-4k"
        })
        mock_response.raise_for_status = MagicMock()
        
        # Mock AsyncClient实例
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = DoubaoAdapter({"api_key": "test-key"})
        await adapter.initialize()
        
        # 替换adapter的client为mock client
        adapter._client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act
        result = await adapter.call(messages, model="doubao-pro-4k")
        
        # Assert
        assert result["content"] == "Hello from Doubao"
        assert result["usage"]["total_tokens"] == 15
    
    async def test_call_without_initialization(self):
        """测试未初始化时调用抛出异常"""
        # Arrange
        adapter = DoubaoAdapter({"api_key": "test-key"})
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act & Assert
        with pytest.raises(AdapterCallError):
            await adapter.call(messages, model="doubao-pro-4k")
    
    async def test_cleanup(self):
        """测试清理资源"""
        # Arrange
        adapter = DoubaoAdapter({"api_key": "test-key"})
        await adapter.initialize()
        
        # Act
        await adapter.cleanup()
        
        # Assert
        assert adapter.is_initialized is False
        assert adapter._client is None
