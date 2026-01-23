"""
BaseVisionAdapter基类单元测试
"""

import pytest
from unittest.mock import AsyncMock
from core.vision.adapters.base import BaseVisionAdapter, VisionAdapterError
from core.vision.models import (
    ImageGenerateRequest,
    ImageGenerateResponse,
    ImageAnalyzeRequest,
    ImageAnalyzeResponse,
    ImageEditRequest,
    ImageEditResponse,
)


class MockVisionAdapter(BaseVisionAdapter):
    """Mock Vision适配器用于测试"""
    
    @property
    def name(self) -> str:
        return "mock-vision-adapter"
    
    @property
    def provider(self) -> str:
        return "mock-provider"
    
    async def generate_image(
        self,
        request: ImageGenerateRequest,
        **kwargs,
    ) -> ImageGenerateResponse:
        return ImageGenerateResponse(
            images=["mock-image-url"],
            model="mock-model",
        )
    
    async def analyze_image(
        self,
        request: ImageAnalyzeRequest,
        **kwargs,
    ) -> ImageAnalyzeResponse:
        return ImageAnalyzeResponse(
            model="mock-model",
            text="mock text",
        )
    
    async def edit_image(
        self,
        request: ImageEditRequest,
        **kwargs,
    ) -> ImageEditResponse:
        return ImageEditResponse(
            images=["mock-edited-image-url"],
            model="mock-model",
        )


class TestBaseVisionAdapter:
    """测试BaseVisionAdapter基类"""
    
    @pytest.mark.asyncio
    async def test_initialize(self):
        """测试适配器初始化"""
        adapter = MockVisionAdapter()
        assert not adapter.is_initialized
        
        await adapter.initialize()
        assert adapter.is_initialized
    
    @pytest.mark.asyncio
    async def test_generate_image(self):
        """测试图像生成"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        
        request = ImageGenerateRequest(prompt="Test")
        response = await adapter.generate_image(request)
        
        assert isinstance(response, ImageGenerateResponse)
        assert len(response.images) == 1
    
    @pytest.mark.asyncio
    async def test_analyze_image(self):
        """测试图像分析"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        
        request = ImageAnalyzeRequest(image="test.jpg")
        response = await adapter.analyze_image(request)
        
        assert isinstance(response, ImageAnalyzeResponse)
        assert response.text == "mock text"
    
    @pytest.mark.asyncio
    async def test_edit_image(self):
        """测试图像编辑"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        
        request = ImageEditRequest(image="test.jpg", prompt="Edit")
        response = await adapter.edit_image(request)
        
        assert isinstance(response, ImageEditResponse)
        assert len(response.images) == 1
    
    @pytest.mark.asyncio
    async def test_call_with_generate_operation(self):
        """测试call方法（generate操作）"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        
        request = ImageGenerateRequest(prompt="Test")
        result = await adapter.call(operation="generate", request=request)
        
        assert isinstance(result, dict)
        assert "images" in result
    
    @pytest.mark.asyncio
    async def test_call_with_invalid_operation(self):
        """测试call方法（无效操作）"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        
        with pytest.raises(VisionAdapterError, match="不支持的操作类型"):
            await adapter.call(operation="invalid")
    
    @pytest.mark.asyncio
    async def test_call_with_wrong_request_type(self):
        """测试call方法（错误的请求类型）"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        
        request = ImageAnalyzeRequest(image="test.jpg")
        with pytest.raises(VisionAdapterError, match="需要ImageGenerateRequest"):
            await adapter.call(operation="generate", request=request)
    
    @pytest.mark.asyncio
    async def test_cleanup(self):
        """测试资源清理"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        assert adapter.is_initialized
        
        await adapter.cleanup()
        assert not adapter.is_initialized
