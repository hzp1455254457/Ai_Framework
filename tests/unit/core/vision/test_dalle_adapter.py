"""
测试模块：DALL-E适配器测试
功能描述：测试DALLEAdapter的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import Response, HTTPError
from core.vision.adapters.dalle_adapter import DALLEAdapter
from core.vision.models import (
    ImageGenerateRequest,
    ImageAnalyzeRequest,
    ImageEditRequest,
    ImageSize,
)
from core.vision.adapters.base import VisionAdapterError
from core.base.adapter import AdapterCallError


@pytest.mark.asyncio
class TestDALLEAdapter:
    """DALLEAdapter测试类"""
    
    async def test_adapter_initialization(self):
        """测试适配器初始化"""
        # Arrange
        config = {"api_key": "sk-test-key"}
        adapter = DALLEAdapter(config)
        
        # Act
        await adapter.initialize()
        
        # Assert
        assert adapter.is_initialized is True
        assert adapter.name == "dalle-adapter"
        assert adapter.provider == "openai"
    
    async def test_adapter_initialization_without_api_key(self):
        """测试缺少API密钥时抛出异常"""
        # Arrange
        adapter = DALLEAdapter({})
        
        # Act & Assert
        with pytest.raises(AdapterCallError, match="API密钥未配置"):
            await adapter.initialize()
    
    @patch("httpx.AsyncClient")
    async def test_generate_image_dalle3_success(self, mock_client_class):
        """测试DALL-E 3图像生成成功"""
        # Arrange
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={
            "created": 1234567890,
            "data": [
                {
                    "url": "https://example.com/image1.jpg",
                    "revised_prompt": "A beautiful sunset over the ocean with vibrant colors"
                }
            ]
        })
        mock_response.raise_for_status = MagicMock()
        
        # Mock AsyncClient实例
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = DALLEAdapter({"api_key": "sk-test-key", "default_model": "dall-e-3"})
        await adapter.initialize()
        adapter._client = mock_client
        
        request = ImageGenerateRequest(
            prompt="A beautiful sunset",
            size=ImageSize.SQUARE_1024,
            n=1,
            quality="standard"
        )
        
        # Act
        response = await adapter.generate_image(request)
        
        # Assert
        assert len(response.images) == 1
        assert response.images[0] == "https://example.com/image1.jpg"
        assert response.model == "dall-e-3"
        assert response.count == 1
        assert "revised_prompt" in response.metadata
    
    @patch("httpx.AsyncClient")
    async def test_generate_image_dalle2_success(self, mock_client_class):
        """测试DALL-E 2图像生成成功"""
        # Arrange
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={
            "created": 1234567890,
            "data": [
                {"url": "https://example.com/image1.jpg"},
                {"url": "https://example.com/image2.jpg"}
            ]
        })
        mock_response.raise_for_status = MagicMock()
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = DALLEAdapter({"api_key": "sk-test-key", "default_model": "dall-e-2"})
        await adapter.initialize()
        adapter._client = mock_client
        
        request = ImageGenerateRequest(
            prompt="A beautiful sunset",
            size=ImageSize.SQUARE_512,
            n=2
        )
        
        # Act
        response = await adapter.generate_image(request, model="dall-e-2")
        
        # Assert
        assert len(response.images) == 2
        assert response.model == "dall-e-2"
        assert response.count == 2
    
    @patch("httpx.AsyncClient")
    async def test_generate_image_dalle3_invalid_size(self, mock_client_class):
        """测试DALL-E 3不支持256x256尺寸"""
        # Arrange
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        adapter = DALLEAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        request = ImageGenerateRequest(
            prompt="A beautiful sunset",
            size=ImageSize.SQUARE_256,  # DALL-E 3不支持
            n=1
        )
        
        # Act & Assert
        with pytest.raises(VisionAdapterError, match="不支持的尺寸"):
            await adapter.generate_image(request, model="dall-e-3")
    
    @patch("httpx.AsyncClient")
    async def test_generate_image_dalle3_invalid_n(self, mock_client_class):
        """测试DALL-E 3不支持生成多张图像"""
        # Arrange
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        adapter = DALLEAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        request = ImageGenerateRequest(
            prompt="A beautiful sunset",
            size=ImageSize.SQUARE_1024,
            n=2  # DALL-E 3只支持n=1
        )
        
        # Act & Assert
        with pytest.raises(VisionAdapterError, match="只支持生成1张图像"):
            await adapter.generate_image(request, model="dall-e-3")
    
    @patch("httpx.AsyncClient")
    async def test_generate_image_dalle2_invalid_size(self, mock_client_class):
        """测试DALL-E 2不支持1792x1024尺寸"""
        # Arrange
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        adapter = DALLEAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        request = ImageGenerateRequest(
            prompt="A beautiful sunset",
            size=ImageSize.PORTRAIT_1024,  # DALL-E 2不支持
            n=1
        )
        
        # Act & Assert
        with pytest.raises(VisionAdapterError, match="不支持的尺寸"):
            await adapter.generate_image(request, model="dall-e-2")
    
    @patch("httpx.AsyncClient")
    async def test_generate_image_api_error(self, mock_client_class):
        """测试API错误处理"""
        # Arrange
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 401
        mock_response.json = MagicMock(return_value={
            "error": {
                "message": "Invalid API key",
                "type": "invalid_request_error"
            }
        })
        # 创建HTTPError异常
        http_error = HTTPError("401 Unauthorized")
        http_error.response = mock_response
        mock_response.raise_for_status = MagicMock(side_effect=http_error)
        mock_response.text = "Unauthorized"
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = DALLEAdapter({"api_key": "sk-invalid-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        request = ImageGenerateRequest(prompt="A beautiful sunset")
        
        # Act & Assert
        with pytest.raises(VisionAdapterError, match="API调用失败"):
            await adapter.generate_image(request)
    
    @patch("httpx.AsyncClient")
    async def test_generate_image_network_error(self, mock_client_class):
        """测试网络错误处理"""
        # Arrange
        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=Exception("Network error"))
        mock_client_class.return_value = mock_client
        
        adapter = DALLEAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        request = ImageGenerateRequest(prompt="A beautiful sunset")
        
        # Act & Assert
        with pytest.raises(VisionAdapterError, match="适配器错误"):
            await adapter.generate_image(request)
    
    @patch("httpx.AsyncClient")
    async def test_generate_image_empty_response(self, mock_client_class):
        """测试空响应处理"""
        # Arrange
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"data": []})
        mock_response.raise_for_status = MagicMock()
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = DALLEAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        request = ImageGenerateRequest(prompt="A beautiful sunset")
        
        # Act & Assert
        with pytest.raises(VisionAdapterError, match="没有图像数据"):
            await adapter.generate_image(request)
    
    async def test_analyze_image_not_supported(self):
        """测试图像分析不支持"""
        # Arrange
        adapter = DALLEAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        
        request = ImageAnalyzeRequest(image="https://example.com/image.jpg")
        
        # Act & Assert
        with pytest.raises(VisionAdapterError, match="不支持图像分析"):
            await adapter.analyze_image(request)
    
    @patch("httpx.AsyncClient")
    async def test_edit_image_dalle2_success(self, mock_client_class):
        """测试DALL-E 2图像编辑成功"""
        # Arrange
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={
            "created": 1234567890,
            "data": [
                {"url": "https://example.com/edited-image.jpg"}
            ]
        })
        mock_response.raise_for_status = MagicMock()
        
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        adapter = DALLEAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        adapter._client = mock_client
        
        request = ImageEditRequest(
            image="https://example.com/original.jpg",
            prompt="Add a rainbow",
            size=ImageSize.SQUARE_1024
        )
        
        # Act
        response = await adapter.edit_image(request, model="dall-e-2")
        
        # Assert
        assert len(response.images) == 1
        assert response.model == "dall-e-2"
    
    async def test_edit_image_dalle3_not_supported(self):
        """测试DALL-E 3不支持图像编辑"""
        # Arrange
        adapter = DALLEAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        
        request = ImageEditRequest(
            image="https://example.com/original.jpg",
            prompt="Add a rainbow"
        )
        
        # Act & Assert
        with pytest.raises(VisionAdapterError, match="不支持图像编辑"):
            await adapter.edit_image(request, model="dall-e-3")
    
    async def test_generate_image_not_initialized(self):
        """测试未初始化时调用生成图像"""
        # Arrange
        adapter = DALLEAdapter({"api_key": "sk-test-key"})
        request = ImageGenerateRequest(prompt="A beautiful sunset")
        
        # Act & Assert
        with pytest.raises(VisionAdapterError, match="适配器未初始化"):
            await adapter.generate_image(request)
    
    async def test_shutdown(self):
        """测试适配器关闭"""
        # Arrange
        adapter = DALLEAdapter({"api_key": "sk-test-key"})
        await adapter.initialize()
        assert adapter.is_initialized is True
        
        # Act
        await adapter.shutdown()
        
        # Assert
        assert adapter._client is None
        assert adapter.is_initialized is False
