"""
VisionService单元测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from core.vision.service import VisionService, VisionError
from core.vision.models import (
    ImageGenerateRequest,
    ImageAnalyzeRequest,
    ImageEditRequest,
    ImageSize,
    AnalyzeType,
)
from core.vision.adapters.base import BaseVisionAdapter


class MockVisionAdapter(BaseVisionAdapter):
    """Mock Vision适配器用于测试"""
    
    @property
    def name(self) -> str:
        return "mock-adapter"
    
    @property
    def provider(self) -> str:
        return "mock-provider"
    
    async def generate_image(self, request, **kwargs):
        from core.vision.models import ImageGenerateResponse
        return ImageGenerateResponse(
            images=["mock-url"],
            model="mock-model",
        )
    
    async def analyze_image(self, request, **kwargs):
        from core.vision.models import ImageAnalyzeResponse
        return ImageAnalyzeResponse(
            model="mock-model",
            text="mock text",
        )
    
    async def edit_image(self, request, **kwargs):
        from core.vision.models import ImageEditResponse
        return ImageEditResponse(
            images=["mock-edited-url"],
            model="mock-model",
        )


@pytest.fixture
def config():
    """测试配置"""
    return {
        "vision": {
            "default_adapter": "mock-adapter",
            "auto_discover_adapters": False,
        },
        "log": {
            "level": "INFO",
        },
    }


@pytest.fixture
async def service(config):
    """测试服务实例"""
    service = VisionService(config)
    await service.initialize()
    return service


class TestVisionService:
    """测试VisionService"""
    
    @pytest.mark.asyncio
    async def test_initialize(self, config):
        """测试服务初始化"""
        service = VisionService(config)
        await service.initialize()
        
        assert service._initialized
        assert service._adapters == {}
    
    @pytest.mark.asyncio
    async def test_register_adapter(self, service):
        """测试注册适配器"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        
        service.register_adapter(adapter)
        
        assert "mock-adapter" in service._adapters
        assert service._adapters["mock-adapter"] == adapter
    
    @pytest.mark.asyncio
    async def test_generate_image_success(self, service):
        """测试图像生成成功"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        service.register_adapter(adapter)
        
        request = ImageGenerateRequest(prompt="A beautiful sunset")
        response = await service.generate_image(request)
        
        assert response.count == 1
        assert response.model == "mock-model"
    
    @pytest.mark.asyncio
    async def test_generate_image_with_adapter_name(self, service):
        """测试使用指定适配器生成图像"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        service.register_adapter(adapter)
        
        request = ImageGenerateRequest(prompt="Test")
        response = await service.generate_image(request, adapter_name="mock-adapter")
        
        assert response.count == 1
    
    @pytest.mark.asyncio
    async def test_generate_image_no_adapters(self, service):
        """测试没有适配器时生成图像应该失败"""
        request = ImageGenerateRequest(prompt="Test")
        
        with pytest.raises(VisionError, match="没有注册的适配器"):
            await service.generate_image(request)
    
    @pytest.mark.asyncio
    async def test_generate_image_invalid_adapter(self, service):
        """测试使用无效适配器名称应该失败"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        service.register_adapter(adapter)
        
        request = ImageGenerateRequest(prompt="Test")
        
        with pytest.raises(VisionError, match="适配器不存在"):
            await service.generate_image(request, adapter_name="invalid-adapter")
    
    @pytest.mark.asyncio
    async def test_analyze_image_success(self, service):
        """测试图像分析成功"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        service.register_adapter(adapter)
        
        request = ImageAnalyzeRequest(image="test.jpg", analyze_type=AnalyzeType.OCR)
        response = await service.analyze_image(request)
        
        assert response.text == "mock text"
        assert response.model == "mock-model"
    
    @pytest.mark.asyncio
    async def test_edit_image_success(self, service):
        """测试图像编辑成功"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        service.register_adapter(adapter)
        
        request = ImageEditRequest(image="test.jpg", prompt="Add rainbow")
        response = await service.edit_image(request)
        
        assert response.count == 1
        assert response.model == "mock-model"
    
    @pytest.mark.asyncio
    async def test_get_adapter_with_default(self, service):
        """测试获取默认适配器"""
        adapter1 = MockVisionAdapter()
        await adapter1.initialize()
        service.register_adapter(adapter1)
        
        adapter = service._get_adapter()
        assert adapter == adapter1
    
    @pytest.mark.asyncio
    async def test_get_adapter_with_name(self, service):
        """测试使用名称获取适配器"""
        adapter1 = MockVisionAdapter()
        await adapter1.initialize()
        service.register_adapter(adapter1)
        
        adapter = service._get_adapter("mock-adapter")
        assert adapter == adapter1
    
    @pytest.mark.asyncio
    async def test_generate_image_adapter_error(self, service):
        """测试适配器错误处理"""
        adapter = MockVisionAdapter()
        await adapter.initialize()
        
        # 模拟适配器抛出异常
        async def mock_generate(*args, **kwargs):
            raise Exception("Adapter error")
        
        adapter.generate_image = mock_generate
        service.register_adapter(adapter)
        
        request = ImageGenerateRequest(prompt="Test")
        
        with pytest.raises(VisionError, match="图像生成失败"):
            await service.generate_image(request)
