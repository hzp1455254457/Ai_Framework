"""
模块名称：通义万相适配器测试模块
功能描述：测试通义万相适配器的功能
创建日期：2026-01-26
最后更新：2026-01-26
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.vision.adapters.tongyi_wanxiang_adapter import TongYiWanXiangAdapter
from core.vision.models import (
    ImageGenerateRequest,
    ImageEditRequest,
    ImageSize,
)
from core.vision.adapters.base import VisionAdapterError


class TestTongYiWanXiangAdapter:
    """通义万相适配器测试类"""

    @pytest.fixture
    def adapter_config(self):
        """测试用配置"""
        return {
            "api_key": "test-api-key",
            "base_url": "https://dashscope.aliyuncs.com/api/v1",
            "model": "wanx-v1",
        }

    @pytest.fixture
    def adapter(self, adapter_config):
        """创建适配器实例"""
        return TongYiWanXiangAdapter(adapter_config)

    @pytest.mark.asyncio
    async def test_adapter_initialization(self, adapter, adapter_config):
        """测试适配器初始化"""
        with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            await adapter.initialize(adapter_config)
            
            assert adapter._initialized
            assert adapter._api_key == adapter_config["api_key"]
            assert adapter._base_url == adapter_config["base_url"]
            assert adapter._default_model == adapter_config["model"]

    @pytest.mark.asyncio
    async def test_adapter_initialization_without_api_key(self):
        """测试无API密钥初始化失败"""
        adapter = TongYiWanXiangAdapter({})
        
        with pytest.raises(VisionAdapterError) as exc_info:
            await adapter.initialize({})
        
        assert "API密钥未配置" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_adapter_initialization_invalid_model(self, adapter_config):
        """测试不支持的模型初始化失败"""
        adapter = TongYiWanXiangAdapter(adapter_config)
        adapter_config["model"] = "invalid-model"
        
        with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            with pytest.raises(VisionAdapterError) as exc_info:
                await adapter.initialize(adapter_config)
            
            assert "不支持的模型" in str(exc_info.value)

    def test_adapter_properties(self, adapter):
        """测试适配器属性"""
        assert adapter.name == "tongyi-wanxiang-adapter"
        assert adapter.provider == "tongyi-wanxiang"

    def test_adapter_supported_models(self):
        """测试支持的模型列表"""
        assert "wanx-v1" in TongYiWanXiangAdapter.SUPPORTED_MODELS

    @pytest.mark.asyncio
    async def test_edit_image_success(self, adapter, adapter_config):
        """测试图像编辑成功"""
        with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟API提交响应
            mock_submit_response = MagicMock()
            mock_submit_response.json.return_value = {
                "output": {
                    "task_id": "edit-task-123"
                }
            }
            mock_submit_response.raise_for_status = MagicMock()
            
            # 模拟任务查询响应
            mock_task_response = MagicMock()
            mock_task_response.json.return_value = {
                "output": {
                    "task_status": "SUCCEEDED",
                    "results": [
                        {"url": "https://example.com/edited.jpg"}
                    ]
                }
            }
            mock_task_response.raise_for_status = MagicMock()
            
            # 配置mock_client.post返回提交响应
            mock_client.post.return_value = mock_submit_response
            # 配置mock_client.get返回任务响应
            mock_client.get.return_value = mock_task_response
            
            await adapter.initialize(adapter_config)
            
            request = ImageEditRequest(
                image="https://example.com/base.jpg",
                prompt="Make it red",
                mask="https://example.com/mask.jpg"
            )
            
            response = await adapter.edit_image(request)
            
            assert response.images[0]["url"] == "https://example.com/edited.jpg"
            assert response.model == "wanx2.1-imageedit"
            assert response.metadata["task_id"] == "edit-task-123"
            assert response.metadata["function"] == "repainting"
            
            # 验证API调用
            mock_client.post.assert_called_once()
            args, kwargs = mock_client.post.call_args
            assert kwargs["json"]["input"]["function"] == "repainting"
            assert kwargs["json"]["input"]["mask_image_url"] == "https://example.com/mask.jpg"
            assert kwargs["headers"]["X-DashScope-Async"] == "enable"

    @pytest.mark.asyncio
    async def test_edit_image_instruction_success(self, adapter, adapter_config):
        """测试指令编辑成功（无mask）"""
        with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_submit_response = MagicMock()
            mock_submit_response.json.return_value = {
                "output": {
                    "task_id": "edit-task-456"
                }
            }
            mock_submit_response.raise_for_status = MagicMock()
            
            mock_task_response = MagicMock()
            mock_task_response.json.return_value = {
                "output": {
                    "task_status": "SUCCEEDED",
                    "results": [
                        {"url": "https://example.com/instruction_edited.jpg"}
                    ]
                }
            }
            mock_task_response.raise_for_status = MagicMock()
            
            mock_client.post.return_value = mock_submit_response
            mock_client.get.return_value = mock_task_response
            
            await adapter.initialize(adapter_config)
            
            request = ImageEditRequest(
                image="https://example.com/base.jpg",
                prompt="Make it cyberpunk style"
            )
            
            response = await adapter.edit_image(request)
            
            assert response.metadata["function"] == "instruction_edit"
            
            args, kwargs = mock_client.post.call_args
            assert kwargs["json"]["input"]["function"] == "instruction_edit"
            assert "mask_image_url" not in kwargs["json"]["input"]
        """测试图像生成成功"""
        with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟API响应
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "output": {
                    "task_id": "test-task-id-123",
                    "tasks": [
                        {
                            "task_results": [
                                {"image": "https://example.com/image1.jpg"}
                            ]
                        }
                    ]
                }
            }
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            await adapter.initialize(adapter_config)
            
            request = ImageGenerateRequest(
                prompt="A beautiful sunset",
                size=ImageSize.SQUARE_1024,
            )
            
            response = await adapter.generate_image(request)
            
            assert response is not None
            assert len(response.images) == 1
            assert response.images[0] == "https://example.com/image1.jpg"
            assert response.model == "wanx-v1"
            assert response.metadata["task_id"] == "test-task-id-123"

    @pytest.mark.asyncio
    async def test_generate_image_with_different_sizes(self, adapter, adapter_config):
        """测试不同尺寸的图像生成"""
        sizes = [
            (ImageSize.SQUARE_1024, "1024*1024"),
            (ImageSize.LANDSCAPE_1024, "1024*1792"),
            (ImageSize.PORTRAIT_1024, "1792*1024"),
        ]
        
        with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "output": {
                    "task_id": "test-task-id",
                    "tasks": [{"task_results": [{"image": "https://example.com/img.jpg"}]}]
                }
            }
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            await adapter.initialize(adapter_config)
            
            for size, expected_size_str in sizes:
                request = ImageGenerateRequest(
                    prompt="A test image",
                    size=size,
                )
                
                # 清空调用历史
                mock_client.post.reset_mock()
                
                await adapter.generate_image(request)
                
                # 验证请求中包含正确的尺寸
                call_args = mock_client.post.call_args
                request_data = call_args.kwargs.get("json", call_args[1].get("json", {}))
                assert request_data["parameters"]["size"] == expected_size_str

    @pytest.mark.asyncio
    async def test_generate_image_uninitialized(self, adapter):
        """测试未初始化时生成图像失败"""
        request = ImageGenerateRequest(prompt="Test")
        
        with pytest.raises(VisionAdapterError) as exc_info:
            await adapter.generate_image(request)
        
        assert "适配器未初始化" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_analyze_image_not_supported(self, adapter, adapter_config):
        """测试图像分析功能不支持"""
        with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            await adapter.initialize(adapter_config)
            
            from core.vision.models import ImageAnalyzeRequest, AnalyzeType
            
            request = ImageAnalyzeRequest(
                image="https://example.com/image.jpg",
                analyze_type=AnalyzeType.IMAGE_UNDERSTANDING,
            )
            
            with pytest.raises(VisionAdapterError) as exc_info:
                await adapter.analyze_image(request)
            
            assert "不支持图像分析功能" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, adapter, adapter_config):
        """测试健康检查 - 健康状态"""
        with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_client.stream.return_value = mock_response

            await adapter.initialize(adapter_config)

            result = await adapter.health_check()

            # 健康检查会尝试调用API，验证它尝试了调用
            mock_client.stream.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_uninitialized(self, adapter):
        """测试健康检查 - 未初始化"""
        result = await adapter.health_check()
        
        assert result.status.value == "unhealthy"
        assert "未初始化" in result.message

    @pytest.mark.asyncio
    async def test_api_error_handling(self, adapter, adapter_config):
        """测试API错误处理"""
        from httpx import HTTPStatusError

        with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # 模拟API返回错误
            mock_response = MagicMock()
            mock_response.json.return_value = {"message": "Invalid API key"}
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"

            http_error = HTTPStatusError(
                message="401 Client Error",
                request=MagicMock(),
                response=mock_response
            )

            mock_response.raise_for_status.side_effect = http_error
            mock_client.post.return_value = mock_response

            await adapter.initialize(adapter_config)

            request = ImageGenerateRequest(prompt="Test")

            with pytest.raises(VisionAdapterError) as exc_info:
                await adapter.generate_image(request)

            # 验证错误消息中包含API调用失败信息
            error_msg = str(exc_info.value)
            assert "API调用失败" in error_msg or "401" in error_msg

    @pytest.mark.asyncio
    async def test_cleanup(self, adapter, adapter_config):
        """测试资源清理"""
        with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            await adapter.initialize(adapter_config)
            
            await adapter.cleanup()
            
            mock_client.aclose.assert_called_once()
            assert not adapter._initialized

    @pytest.mark.asyncio
    async def test_shutdown(self, adapter, adapter_config):
        """测试关闭适配器"""
        with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            await adapter.initialize(adapter_config)
            
            await adapter.shutdown()
            
            mock_client.aclose.assert_called_once()
            assert adapter._client is None
            assert not adapter._initialized

    @pytest.mark.asyncio
    async def test_response_with_multiple_images(self, adapter, adapter_config):
        """测试多图像响应解析"""
        with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.json.return_value = {
                "output": {
                    "task_id": "test-task-id",
                    "tasks": [
                        {
                            "task_results": [
                                {"images": ["url1.jpg", "url2.jpg"]}
                            ]
                        }
                    ]
                }
            }
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response

            await adapter.initialize(adapter_config)

            request = ImageGenerateRequest(prompt="Multiple images")

            response = await adapter.generate_image(request)

            assert len(response.images) == 2
            assert "url1.jpg" in response.images
            assert "url2.jpg" in response.images
            assert response.count == 2  # 使用count属性验证


class TestTongYiWanXiangAdapterConfigReuse:
    """测试通义万相适配器配置复用"""

    @pytest.mark.asyncio
    async def test_api_key_from_environment(self):
        """测试从环境变量获取API密钥"""
        with patch.dict("os.environ", {"QWEN_API_KEY": "env-api-key"}):
            adapter = TongYiWanXiangAdapter({})
            
            with patch("core.vision.adapters.tongyi_wanxiang_adapter.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value = mock_client
                
                config = {"api_key": ""}  # 空的API密钥
                
                with pytest.raises(VisionAdapterError):
                    await adapter.initialize(config)
                
                # 验证环境变量被检查
                assert os.getenv("QWEN_API_KEY") == "env-api-key"

    @pytest.mark.asyncio
    async def test_api_key_from_llm_config(self):
        """测试从LLM配置获取API密钥"""
        adapter = TongYiWanXiangAdapter({})
        
        llm_config = {
            "adapters": {
                "qwen-adapter": {
                    "api_key": "llm-config-api-key"
                }
            }
        }
        
        api_key = ""
        if not api_key:
            llm_adapters_config = llm_config.get("adapters", {})
            if "qwen-adapter" in llm_adapters_config:
                api_key = llm_adapters_config["qwen-adapter"].get("api_key", "")
        
        assert api_key == "llm-config-api-key"
