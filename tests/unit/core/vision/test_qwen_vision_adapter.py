"""
测试模块：Qwen-Vision适配器单元测试
功能描述：测试QwenVisionAdapter的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.vision.adapters.qwen_vision_adapter import QwenVisionAdapter
from core.vision.models import (
    ImageAnalyzeRequest,
    ImageAnalyzeResponse,
    ImageGenerateRequest,
    ImageEditRequest,
    AnalyzeType,
)
from core.vision.adapters.base import VisionAdapterError


@pytest.fixture
def mock_config():
    """创建Mock配置"""
    return {
        "api_key": "test-api-key",
        "base_url": "https://dashscope.aliyuncs.com/api/v1",
        "model": "qwen-vl-plus",
    }


@pytest.fixture
def qwen_vision_adapter(mock_config):
    """创建Qwen-Vision适配器实例"""
    adapter = QwenVisionAdapter(mock_config)
    return adapter


@pytest.mark.asyncio
class TestQwenVisionAdapterInitialization:
    """Qwen-Vision适配器初始化测试类"""

    async def test_initialize_success(self, qwen_vision_adapter, mock_config):
        """测试初始化成功"""
        # Mock HTTP客户端
        with patch("core.vision.adapters.qwen_vision_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # 执行初始化
            await qwen_vision_adapter.initialize(mock_config)

            # 验证
            assert qwen_vision_adapter._api_key == "test-api-key"
            assert qwen_vision_adapter._default_model == "qwen-vl-plus"
            assert qwen_vision_adapter._initialized is True
            mock_client_class.assert_called_once()

    async def test_initialize_without_api_key(self):
        """测试缺少API密钥时初始化失败"""
        adapter = QwenVisionAdapter({})

        with pytest.raises(Exception) as exc_info:
            await adapter.initialize()

        assert "API密钥未配置" in str(exc_info.value)

    async def test_initialize_invalid_model(self, mock_config):
        """测试不支持的模型时初始化失败"""
        adapter = QwenVisionAdapter(mock_config)
        adapter._config["model"] = "invalid-model"

        with pytest.raises(Exception) as exc_info:
            await adapter.initialize()

        assert "不支持的模型" in str(exc_info.value)


@pytest.mark.asyncio
class TestQwenVisionAdapterProperties:
    """Qwen-Vision适配器属性测试类"""

    def test_adapter_name(self, qwen_vision_adapter):
        """测试适配器名称"""
        assert qwen_vision_adapter.name == "qwen-vision-adapter"

    def test_adapter_provider(self, qwen_vision_adapter):
        """测试服务提供商"""
        assert qwen_vision_adapter.provider == "qwen"

    def test_supported_models(self, qwen_vision_adapter):
        """测试支持的模型列表"""
        assert "qwen-vl" in qwen_vision_adapter.SUPPORTED_MODELS
        assert "qwen-vl-plus" in qwen_vision_adapter.SUPPORTED_MODELS
        assert "qwen-vl-max" in qwen_vision_adapter.SUPPORTED_MODELS

    def test_default_model(self, qwen_vision_adapter):
        """测试默认模型"""
        assert qwen_vision_adapter.DEFAULT_MODEL == "qwen-vl-plus"


@pytest.mark.asyncio
class TestQwenVisionAdapterImageAnalysis:
    """Qwen-Vision适配器图像分析测试类"""

    async def test_analyze_image_not_initialized(self, qwen_vision_adapter):
        """测试未初始化时调用分析功能"""
        request = ImageAnalyzeRequest(
            image="https://example.com/image.jpg",
            analyze_type=AnalyzeType.IMAGE_UNDERSTANDING
        )

        with pytest.raises(VisionAdapterError) as exc_info:
            await qwen_vision_adapter.analyze_image(request)

        assert "适配器未初始化" in str(exc_info.value)

    async def test_analyze_image_unsupported_model(self, qwen_vision_adapter, mock_config):
        """测试不支持的模型"""
        with patch("core.vision.adapters.qwen_vision_adapter.AsyncClient"):
            await qwen_vision_adapter.initialize(mock_config)

        request = ImageAnalyzeRequest(
            image="https://example.com/image.jpg",
            analyze_type=AnalyzeType.IMAGE_UNDERSTANDING
        )

        with pytest.raises(VisionAdapterError) as exc_info:
            await qwen_vision_adapter.analyze_image(request, model="invalid-model")

        assert "不支持的模型" in str(exc_info.value)

    async def test_analyze_image_general_success(self, qwen_vision_adapter, mock_config):
        """测试通用图像理解成功"""
        # 简化测试：只验证方法调用和响应创建，不测试完整的HTTP响应解析
        with patch("core.vision.adapters.qwen_vision_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()

            # 模拟 httpx.Response 的 json() 方法行为
            # 注意：response.json() 是同步方法，所以使用 MagicMock 而不是默认的 AsyncMock
            mock_response.json = MagicMock(return_value={
                "output": {
                    "choices": [
                        {
                            "message": {
                                "content": "这是一张包含天空和树木的图片。"
                            }
                        }
                    ]
                }
            })
            mock_response.raise_for_status = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            await qwen_vision_adapter.initialize(mock_config)

            request = ImageAnalyzeRequest(
                image="https://example.com/image.jpg",
                analyze_type=AnalyzeType.IMAGE_UNDERSTANDING
            )

            response = await qwen_vision_adapter.analyze_image(request)

            assert response is not None
            assert response.model == "qwen-vl-plus"
            assert response.description is not None

    async def test_analyze_image_ocr_success(self, qwen_vision_adapter, mock_config):
        """测试OCR识别成功"""
        with patch("core.vision.adapters.qwen_vision_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()

            # 注意：response.json() 是同步方法
            mock_response.json = MagicMock(return_value={
                "output": {
                    "choices": [
                        {
                            "message": {
                                "content": "识别到的文字内容：Hello World"
                            }
                        }
                    ]
                }
            })
            mock_response.raise_for_status = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            await qwen_vision_adapter.initialize(mock_config)

            request = ImageAnalyzeRequest(
                image="https://example.com/document.jpg",
                analyze_type=AnalyzeType.OCR
            )

            response = await qwen_vision_adapter.analyze_image(request)

            assert response is not None
            assert response.model == "qwen-vl-plus"
            assert response.text is not None


@pytest.mark.asyncio
class TestQwenVisionAdapterImageGeneration:
    """Qwen-Vision适配器图像生成测试类"""

    async def test_generate_image_not_supported(self, qwen_vision_adapter, mock_config):
        """测试图像生成功能不支持"""
        with patch("core.vision.adapters.qwen_vision_adapter.AsyncClient"):
            await qwen_vision_adapter.initialize(mock_config)

        request = ImageGenerateRequest(prompt="A beautiful sunset")

        with pytest.raises(VisionAdapterError) as exc_info:
            await qwen_vision_adapter.generate_image(request)

        assert "不支持图像生成" in str(exc_info.value)


@pytest.mark.asyncio
class TestQwenVisionAdapterImageEditing:
    """Qwen-Vision适配器图像编辑测试类"""

    async def test_edit_image_not_supported(self, qwen_vision_adapter, mock_config):
        """测试图像编辑功能不支持"""
        with patch("core.vision.adapters.qwen_vision_adapter.AsyncClient"):
            await qwen_vision_adapter.initialize(mock_config)

        request = ImageEditRequest(
            image="https://example.com/image.jpg",
            prompt="Add a rainbow"
        )

        with pytest.raises(VisionAdapterError) as exc_info:
            await qwen_vision_adapter.edit_image(request)

        assert "不支持图像编辑" in str(exc_info.value)


@pytest.mark.asyncio
class TestQwenVisionAdapterHealthCheck:
    """Qwen-Vision适配器健康检查测试类"""

    async def test_health_check_not_initialized(self, qwen_vision_adapter):
        """测试未初始化时健康检查"""
        result = await qwen_vision_adapter.health_check()

        assert result.status.value == "unhealthy"
        assert "未初始化" in result.message

    async def test_health_check_success(self, qwen_vision_adapter, mock_config):
        """测试健康检查成功"""
        with patch("core.vision.adapters.qwen_vision_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()

            # 模拟异步上下文管理器
            mock_response = MagicMock()
            mock_response.status_code = 200

            async def mock_context_manager(*args, **kwargs):
                return mock_response

            mock_client.stream = mock_context_manager
            mock_client_class.return_value = mock_client

            await qwen_vision_adapter.initialize(mock_config)

            result = await qwen_vision_adapter.health_check()

            assert result.status.value == "healthy"
            assert "可用" in result.message


@pytest.mark.asyncio
class TestQwenVisionAdapterCleanup:
    """Qwen-Vision适配器清理测试类"""

    async def test_cleanup(self, qwen_vision_adapter, mock_config):
        """测试清理资源"""
        with patch("core.vision.adapters.qwen_vision_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            await qwen_vision_adapter.initialize(mock_config)

            await qwen_vision_adapter.cleanup()

            mock_client.aclose.assert_called_once()
            assert qwen_vision_adapter._client is None


@pytest.mark.asyncio
class TestQwenVisionAdapterImageInputProcessing:
    """Qwen-Vision适配器图像输入处理测试类"""

    def test_is_base64_valid(self, qwen_vision_adapter):
        """测试有效base64检测"""
        # 有效的base64字符串（至少100字符，且不含特殊字符）
        import base64
        # 创建一个真实的base64编码字符串
        test_data = b"This is test data for base64 encoding with enough length." * 3
        valid_base64 = base64.b64encode(test_data).decode('ascii')
        assert len(valid_base64) >= 100
        assert qwen_vision_adapter._is_base64(valid_base64) is True

    def test_is_base64_invalid_short(self, qwen_vision_adapter):
        """测试太短的base64检测"""
        invalid_base64 = "aGVsbG8="
        assert qwen_vision_adapter._is_base64(invalid_base64) is False

    def test_is_base64_invalid_url(self, qwen_vision_adapter):
        """测试URL不是base64"""
        url = "https://example.com/image.jpg"
        assert qwen_vision_adapter._is_base64(url) is False


@pytest.mark.asyncio
class TestQwenVisionAdapterPromptBuilding:
    """Qwen-Vision适配器提示词构建测试类"""

    def test_build_ocr_prompt(self, qwen_vision_adapter):
        """测试OCR提示词构建"""
        prompt = qwen_vision_adapter._build_analysis_prompt(AnalyzeType.OCR)
        assert "文字" in prompt or "text" in prompt

    def test_build_object_detection_prompt(self, qwen_vision_adapter):
        """测试物体识别提示词构建"""
        prompt = qwen_vision_adapter._build_analysis_prompt(AnalyzeType.OBJECT_DETECTION)
        assert "物体" in prompt or "object" in prompt

    def test_build_image_understanding_prompt(self, qwen_vision_adapter):
        """测试图像理解提示词构建"""
        prompt = qwen_vision_adapter._build_analysis_prompt(AnalyzeType.IMAGE_UNDERSTANDING)
        assert "描述" in prompt or "describe" in prompt

    def test_build_all_prompt(self, qwen_vision_adapter):
        """测试全部分析提示词构建"""
        prompt = qwen_vision_adapter._build_analysis_prompt(AnalyzeType.ALL)
        assert "描述" in prompt or "describe" in prompt
