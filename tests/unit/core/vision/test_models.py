"""
Vision数据模型单元测试
"""

import pytest
from datetime import datetime
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


class TestImageGenerateRequest:
    """测试ImageGenerateRequest"""
    
    def test_create_request_with_valid_params(self):
        """测试使用有效参数创建请求"""
        request = ImageGenerateRequest(
            prompt="A beautiful sunset",
            size=ImageSize.SQUARE_1024,
            n=2,
        )
        assert request.prompt == "A beautiful sunset"
        assert request.size == ImageSize.SQUARE_1024
        assert request.n == 2
    
    def test_create_request_with_string_size(self):
        """测试使用字符串尺寸创建请求"""
        request = ImageGenerateRequest(
            prompt="Test",
            size="512x512",
        )
        assert request.size == ImageSize.SQUARE_512
    
    def test_create_request_with_empty_prompt(self):
        """测试使用空提示词创建请求应该失败"""
        with pytest.raises(ValueError, match="提示词不能为空"):
            ImageGenerateRequest(prompt="")
    
    def test_create_request_with_invalid_n(self):
        """测试使用无效的n值创建请求应该失败"""
        with pytest.raises(ValueError, match="生成图像数量"):
            ImageGenerateRequest(prompt="Test", n=0)
        
        with pytest.raises(ValueError, match="生成图像数量"):
            ImageGenerateRequest(prompt="Test", n=11)
    
    def test_to_dict(self):
        """测试转换为字典"""
        request = ImageGenerateRequest(
            prompt="Test",
            size=ImageSize.SQUARE_1024,
            n=1,
            quality="hd",
        )
        data = request.to_dict()
        assert data["prompt"] == "Test"
        assert data["size"] == "1024x1024"
        assert data["n"] == 1
        assert data["quality"] == "hd"


class TestImageGenerateResponse:
    """测试ImageGenerateResponse"""
    
    def test_create_response_with_valid_params(self):
        """测试使用有效参数创建响应"""
        response = ImageGenerateResponse(
            images=["url1", "url2"],
            model="dalle-3",
        )
        assert len(response.images) == 2
        assert response.model == "dalle-3"
        assert response.count == 2
    
    def test_create_response_with_empty_images(self):
        """测试使用空图像列表创建响应应该失败"""
        with pytest.raises(ValueError, match="图像列表不能为空"):
            ImageGenerateResponse(images=[], model="dalle-3")
    
    def test_to_dict(self):
        """测试转换为字典"""
        response = ImageGenerateResponse(
            images=["url1"],
            model="dalle-3",
            metadata={"cost": 0.02},
        )
        data = response.to_dict()
        assert data["images"] == ["url1"]
        assert data["model"] == "dalle-3"
        assert data["count"] == 1
        assert "created_at" in data
        assert data["metadata"]["cost"] == 0.02


class TestImageAnalyzeRequest:
    """测试ImageAnalyzeRequest"""
    
    def test_create_request_with_valid_params(self):
        """测试使用有效参数创建请求"""
        request = ImageAnalyzeRequest(
            image="https://example.com/image.jpg",
            analyze_type=AnalyzeType.OCR,
        )
        assert request.image == "https://example.com/image.jpg"
        assert request.analyze_type == AnalyzeType.OCR
    
    def test_create_request_with_string_analyze_type(self):
        """测试使用字符串分析类型创建请求"""
        request = ImageAnalyzeRequest(
            image="test.jpg",
            analyze_type="ocr",
        )
        assert request.analyze_type == AnalyzeType.OCR
    
    def test_create_request_with_empty_image(self):
        """测试使用空图像创建请求应该失败"""
        with pytest.raises(ValueError, match="图像数据不能为空"):
            ImageAnalyzeRequest(image="")


class TestImageAnalyzeResponse:
    """测试ImageAnalyzeResponse"""
    
    def test_create_response_with_all_fields(self):
        """测试使用所有字段创建响应"""
        response = ImageAnalyzeResponse(
            model="gpt-4-vision",
            text="识别到的文本",
            objects=[{"name": "car", "confidence": 0.95}],
            description="图像描述",
        )
        assert response.text == "识别到的文本"
        assert len(response.objects) == 1
        assert response.description == "图像描述"


class TestImageEditRequest:
    """测试ImageEditRequest"""
    
    def test_create_request_with_valid_params(self):
        """测试使用有效参数创建请求"""
        request = ImageEditRequest(
            image="https://example.com/image.jpg",
            prompt="Add a rainbow",
        )
        assert request.image == "https://example.com/image.jpg"
        assert request.prompt == "Add a rainbow"
    
    def test_create_request_with_empty_prompt(self):
        """测试使用空提示词创建请求应该失败"""
        with pytest.raises(ValueError, match="编辑提示词不能为空"):
            ImageEditRequest(image="test.jpg", prompt="")


class TestImageEditResponse:
    """测试ImageEditResponse"""
    
    def test_create_response(self):
        """测试创建响应"""
        response = ImageEditResponse(
            images=["url1", "url2"],
            model="dalle-3",
        )
        assert response.count == 2
        assert response.model == "dalle-3"
