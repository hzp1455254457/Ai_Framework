"""
测试模块：Vision API路由测试
功能描述：测试Vision路由的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from api.fastapi_app import app
from api.dependencies import get_vision_service
from core.vision.service import VisionService, VisionError
from core.vision.models import (
    ImageGenerateRequest,
    ImageGenerateResponse,
    ImageAnalyzeRequest,
    ImageAnalyzeResponse,
    ImageEditRequest,
    ImageEditResponse,
    ImageSize,
    AnalyzeType,
)
from datetime import datetime


@pytest.fixture
def mock_vision_service():
    """创建Mock Vision服务"""
    service = MagicMock(spec=VisionService)
    
    # Mock generate_image
    generate_response = ImageGenerateResponse(
        images=["https://example.com/generated-image.jpg"],
        model="dall-e-3",
        metadata={},
    )
    service.generate_image = AsyncMock(return_value=generate_response)
    
    # Mock analyze_image
    analyze_response = ImageAnalyzeResponse(
        model="gpt-4-vision",
        text="识别到的文本",
        objects=[],
        description="图像描述",
        metadata={},
    )
    service.analyze_image = AsyncMock(return_value=analyze_response)
    
    # Mock edit_image
    edit_response = ImageEditResponse(
        images=["https://example.com/edited-image.jpg"],
        model="dall-e-2",
        metadata={},
    )
    service.edit_image = AsyncMock(return_value=edit_response)
    
    return service


@pytest.fixture
def client(mock_vision_service):
    """创建测试客户端，并覆盖依赖"""
    # 覆盖依赖注入
    app.dependency_overrides[get_vision_service] = lambda: mock_vision_service
    
    yield TestClient(app)
    
    # 清理依赖覆盖
    app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestVisionRoutes:
    """Vision路由测试类"""
    
    async def test_generate_image_success(self, client, mock_vision_service):
        """测试图像生成成功"""
        # Arrange
        request_data = {
            "prompt": "A beautiful sunset",
            "size": "1024x1024",
            "n": 1,
            "quality": "standard",
        }
        
        # Act
        response = client.post("/api/v1/vision/generate", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "images" in data
        assert len(data["images"]) == 1
        assert data["model"] == "dall-e-3"
        assert data["count"] == 1
        mock_vision_service.generate_image.assert_called_once()
    
    async def test_generate_image_with_empty_prompt(self, client, mock_vision_service):
        """测试空提示词请求"""
        # Arrange
        request_data = {
            "prompt": "",
        }
        
        # Act
        response = client.post("/api/v1/vision/generate", json=request_data)
        
        # Assert
        # FastAPI 的 Pydantic 验证会在请求到达路由之前返回 422
        assert response.status_code in [400, 422]
    
    async def test_generate_image_with_invalid_n(self, client, mock_vision_service):
        """测试无效的图像数量"""
        # Arrange
        request_data = {
            "prompt": "A beautiful sunset",
            "n": 11,  # 超出范围
        }
        
        # Act
        response = client.post("/api/v1/vision/generate", json=request_data)
        
        # Assert
        # FastAPI 的 Pydantic 验证会在请求到达路由之前返回 422
        assert response.status_code in [400, 422]
    
    async def test_generate_image_service_error(self, client, mock_vision_service):
        """测试Vision服务错误"""
        # Arrange
        mock_vision_service.generate_image = AsyncMock(
            side_effect=VisionError("适配器不可用")
        )
        request_data = {
            "prompt": "A beautiful sunset",
        }
        
        # Act
        response = client.post("/api/v1/vision/generate", json=request_data)
        
        # Assert
        assert response.status_code == 500
        assert "图像生成失败" in response.json()["detail"]
    
    async def test_analyze_image_success(self, client, mock_vision_service):
        """测试图像分析成功"""
        # Arrange
        request_data = {
            "image": "https://example.com/image.jpg",
            "analyze_type": "all",
        }
        
        # Act
        response = client.post("/api/v1/vision/analyze", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "gpt-4-vision"
        assert data["text"] == "识别到的文本"
        assert data["description"] == "图像描述"
        mock_vision_service.analyze_image.assert_called_once()
    
    async def test_analyze_image_with_empty_image(self, client, mock_vision_service):
        """测试空图像数据请求"""
        # Arrange
        request_data = {
            "image": "",
        }
        
        # Act
        response = client.post("/api/v1/vision/analyze", json=request_data)
        
        # Assert
        # FastAPI 的 Pydantic 验证会在请求到达路由之前返回 422
        assert response.status_code in [400, 422]
    
    async def test_analyze_image_service_error(self, client, mock_vision_service):
        """测试图像分析服务错误"""
        # Arrange
        mock_vision_service.analyze_image = AsyncMock(
            side_effect=VisionError("分析失败")
        )
        request_data = {
            "image": "https://example.com/image.jpg",
        }
        
        # Act
        response = client.post("/api/v1/vision/analyze", json=request_data)
        
        # Assert
        assert response.status_code == 500
        assert "图像分析失败" in response.json()["detail"]
    
    async def test_edit_image_success(self, client, mock_vision_service):
        """测试图像编辑成功"""
        # Arrange
        request_data = {
            "image": "https://example.com/image.jpg",
            "prompt": "Add a rainbow in the sky",
            "n": 1,
        }
        
        # Act
        response = client.post("/api/v1/vision/edit", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "images" in data
        assert len(data["images"]) == 1
        assert data["model"] == "dall-e-2"
        assert data["count"] == 1
        mock_vision_service.edit_image.assert_called_once()
    
    async def test_edit_image_with_empty_prompt(self, client, mock_vision_service):
        """测试空编辑提示词请求"""
        # Arrange
        request_data = {
            "image": "https://example.com/image.jpg",
            "prompt": "",
        }
        
        # Act
        response = client.post("/api/v1/vision/edit", json=request_data)
        
        # Assert
        # FastAPI 的 Pydantic 验证会在请求到达路由之前返回 422
        assert response.status_code in [400, 422]
    
    async def test_edit_image_service_error(self, client, mock_vision_service):
        """测试图像编辑服务错误"""
        # Arrange
        mock_vision_service.edit_image = AsyncMock(
            side_effect=VisionError("编辑失败")
        )
        request_data = {
            "image": "https://example.com/image.jpg",
            "prompt": "Add a rainbow",
        }
        
        # Act
        response = client.post("/api/v1/vision/edit", json=request_data)
        
        # Assert
        assert response.status_code == 500
        assert "图像编辑失败" in response.json()["detail"]
    
    async def test_generate_image_with_adapter_name(self, client, mock_vision_service):
        """测试指定适配器名称"""
        # Arrange
        request_data = {
            "prompt": "A beautiful sunset",
            "adapter_name": "dalle-adapter",
        }
        
        # Act
        response = client.post("/api/v1/vision/generate", json=request_data)
        
        # Assert
        assert response.status_code == 200
        # 验证调用了 generate_image 并传递了 adapter_name
        call_args = mock_vision_service.generate_image.call_args
        assert call_args[1]["adapter_name"] == "dalle-adapter"
