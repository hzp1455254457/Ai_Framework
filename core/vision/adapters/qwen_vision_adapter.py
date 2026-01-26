"""
模块名称：通义千问Vision适配器模块
功能描述：实现通义千问Qwen-VL视觉模型的适配器
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - QwenVisionAdapter: 通义千问Vision适配器

依赖模块：
    - httpx: 异步HTTP客户端
    - core.vision.adapters.base: 适配器基类
    - core.vision.models: Vision数据模型
"""

import json
import logging
import base64
import asyncio
from typing import Dict, Any, Optional, List
from httpx import AsyncClient, HTTPError, TimeoutException
from core.vision.adapters.base import BaseVisionAdapter, VisionAdapterError
from core.base.health_check import HealthStatus, HealthCheckResult
from core.vision.models import (
    ImageAnalyzeRequest,
    ImageAnalyzeResponse,
    ImageGenerateRequest,
    ImageGenerateResponse,
    ImageEditRequest,
    ImageEditResponse,
    AnalyzeType,
)
from core.base.adapter import AdapterCallError


class QwenVisionAdapter(BaseVisionAdapter):
    """
    通义千问Vision适配器

    实现阿里云通义千问Qwen-VL视觉模型的服务适配器，支持图像理解、OCR、物体识别等。

    特性：
        - 支持Qwen-VL、Qwen-VL-Plus、Qwen-VL-Max模型
        - 支持图像理解（通用分析）
        - 支持OCR光学字符识别
        - 支持物体识别
        - 错误处理和重试
        - 与现有Vision服务无缝集成

    配置示例:
        {
            "api_key": "your-api-key",
            "base_url": "https://dashscope.aliyuncs.com/api/v1",  # 可选
            "model": "qwen-vl-plus"  # 可选，默认qwen-vl-plus
        }

    示例:
        >>> adapter = QwenVisionAdapter({"api_key": "your-key", "model": "qwen-vl-plus"})
        >>> await adapter.initialize()
        >>> request = ImageAnalyzeRequest(image="https://example.com/image.jpg", analyze_type="general")
        >>> response = await adapter.analyze_image(request)
    """

    # 支持的模型列表
    SUPPORTED_MODELS = ["qwen-vl", "qwen-vl-plus", "qwen-vl-max"]

    # 默认模型
    DEFAULT_MODEL = "qwen-vl-plus"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化通义千问Vision适配器

        参数:
            config: 适配器配置，包含api_key、base_url、model等
        """
        super().__init__(config)
        self._api_key: str = ""
        self._base_url: str = "https://dashscope.aliyuncs.com/api/v1"
        self._default_model: str = self.DEFAULT_MODEL
        self._client: Optional[AsyncClient] = None
        # 初始化logger
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def name(self) -> str:
        """适配器名称"""
        return "qwen-vision-adapter"

    @property
    def provider(self) -> str:
        """服务提供商名称"""
        return "qwen"
    
    def get_supported_operations(self) -> List[str]:
        """
        获取适配器支持的操作类型列表
        
        通义千问Vision适配器仅支持图像分析功能（图像理解、OCR、物体识别）。
        
        返回:
            支持的操作类型列表：["analyze"]
        """
        return ["analyze"]

    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化适配器

        参数:
            config: 适配器配置
        """
        if config:
            self._config.update(config)

        self._api_key = self._config.get("api_key", "")
        if not self._api_key:
            raise AdapterCallError("通义千问API密钥未配置")

        self._base_url = self._config.get("base_url", self._base_url)
        self._default_model = self._config.get("model", self.DEFAULT_MODEL)

        # 验证模型名称
        if self._default_model not in self.SUPPORTED_MODELS:
            raise AdapterCallError(
                f"不支持的模型: {self._default_model}，"
                f"仅支持 {', '.join(self.SUPPORTED_MODELS)}"
            )

        # 创建HTTP客户端
        self._client = AsyncClient(
            base_url=self._base_url,
            timeout=60.0,  # Vision API可能需要更长时间
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )

        await super().initialize()

    async def generate_image(
        self,
        request: ImageGenerateRequest,
        **kwargs: Any,
    ) -> ImageGenerateResponse:
        """
        生成图像

        通义千问Vision模型不支持图像生成功能，此方法会抛出异常。

        参数:
            request: 图像生成请求
            **kwargs: 其他适配器特定参数

        返回:
            ImageGenerateResponse对象

        异常:
            VisionAdapterError: 通义千问不支持图像生成
        """
        raise VisionAdapterError(
            "通义千问Vision适配器不支持图像生成功能，"
            "请使用DALL-E适配器进行图像生成"
        )

    async def analyze_image(
        self,
        request: ImageAnalyzeRequest,
        **kwargs: Any,
    ) -> ImageAnalyzeResponse:
        """
        分析图像

        根据请求的分析类型，调用通义千问Vision API分析图像内容。

        参数:
            request: 图像分析请求
            **kwargs: 其他适配器特定参数（如model指定模型）

        返回:
            ImageAnalyzeResponse对象，包含分析结果

        异常:
            VisionAdapterError: 分析失败时抛出
        """
        if not self._client:
            raise VisionAdapterError("适配器未初始化")

        # 确定使用的模型
        model = kwargs.get("model", self._default_model)
        if model not in self.SUPPORTED_MODELS:
            raise VisionAdapterError(
                f"不支持的模型: {model}，仅支持 {', '.join(self.SUPPORTED_MODELS)}"
            )

        input_data = await self._build_vision_input(request, model)
        prompt = self._build_analysis_prompt(request.analyze_type)

        messages_content: List[Dict[str, Any]] = []
        for item in input_data:
            messages_content.append({"image": item["image"]})
        messages_content.append({"text": prompt})

        request_data = {
            "model": model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": messages_content,
                    }
                ]
            },
            "parameters": {
                "max_tokens": 2048,
            },
        }

        try:
            # 发送请求到通义千问Vision API
            response = await self._client.post(
                "/services/aigc/multimodal-generation/generation",
                json=request_data,
            )
            response.raise_for_status()

            result = response.json()

            # 解析响应
            output = result.get("output", {})
            choices = output.get("choices", [])
            if not choices:
                raise VisionAdapterError("API响应中没有分析结果")

            # 提取分析结果
            message = choices[0].get("message", {})
            content = message.get("content", "")

            # 解析内容并构建响应对象
            return self._parse_analysis_response(
                content=content,
                model=model,
                analyze_type=request.analyze_type,
                original_request=request,
            )

        except HTTPError as e:
            error_message = f"通义千问Vision API调用失败: {e}"
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_message = f"{error_message} - {error_detail.get('message', error_detail.get('error', str(e)))}"
                except Exception:
                    error_message = f"{error_message} - {e.response.text}"
            raise VisionAdapterError(error_message) from e
        except Exception as e:
            raise VisionAdapterError(f"通义千问Vision适配器错误: {str(e)}") from e

    async def edit_image(
        self,
        request: ImageEditRequest,
        **kwargs: Any,
    ) -> ImageEditResponse:
        """
        编辑图像

        通义千问Vision模型不支持图像编辑功能，此方法会抛出异常。

        参数:
            request: 图像编辑请求
            **kwargs: 其他适配器特定参数

        返回:
            ImageEditResponse对象

        异常:
            VisionAdapterError: 通义千问不支持图像编辑
        """
        raise VisionAdapterError(
            "通义千问Vision适配器不支持图像编辑功能，"
            "请使用DALL-E适配器进行图像编辑"
        )

    async def _build_vision_input(
        self,
        request: ImageAnalyzeRequest,
        model: str,
    ) -> List[Dict[str, Any]]:
        """
        构建Vision API的输入数据

        参数:
            request: 图像分析请求
            model: 使用的模型名称

        返回:
            Vision API输入格式的列表
        """
        # 处理图像数据
        image = request.image

        # 如果是base64编码，直接使用
        if image.startswith("data:image"):
            # Data URL格式
            image_data = image
        elif image.startswith("base64,"):
            # Base64格式（不带data URL前缀）
            image_data = f"data:image/jpeg;base64,{image[7:]}"
        elif self._is_base64(image):
            # 纯base64编码
            image_data = f"data:image/jpeg;base64,{image}"
        else:
            # URL格式
            image_data = image

        # 构建输入数据
        input_data = [
            {
                "image": image_data,
            }
        ]

        return input_data

    def _build_analysis_prompt(self, analyze_type: AnalyzeType) -> str:
        """
        根据分析类型构建提示词

        参数:
            analyze_type: 分析类型

        返回:
            分析提示词
        """
        prompts = {
            AnalyzeType.OCR: "请识别并提取图片中的所有文字内容，包括印刷文字和手写文字，保持原有格式。",
            AnalyzeType.OBJECT_DETECTION: "请识别图片中的物体和场景，列出所有检测到的物体及其位置。",
            AnalyzeType.IMAGE_UNDERSTANDING: "请详细描述这张图片的内容，包括场景、物体、动作、氛围等。",
            AnalyzeType.ALL: "请对图片进行全面的分析，包括：1) 图片整体描述；2) 识别所有物体；3) 提取所有文字内容。",
        }

        return prompts.get(analyze_type, prompts[AnalyzeType.IMAGE_UNDERSTANDING])

    def _parse_analysis_response(
        self,
        content: Any,
        model: str,
        analyze_type: AnalyzeType,
        original_request: ImageAnalyzeRequest,
    ) -> ImageAnalyzeResponse:
        """
        解析API响应并构建分析响应对象

        参数:
            content: API返回的内容（可能是字符串或列表）
            model: 使用的模型名称
            analyze_type: 分析类型
            original_request: 原始请求

        返回:
            ImageAnalyzeResponse对象
        """
        # 确保内容是字符串
        if isinstance(content, list):
            # 如果内容是列表，尝试将其转换为字符串
            # 列表通常包含多个文本片段或其他结构化数据
            content_parts = []
            for item in content:
                if isinstance(item, dict):
                    if "text" in item:
                        content_parts.append(item["text"])
                    elif "content" in item:
                        content_parts.append(str(item["content"]))
                else:
                    content_parts.append(str(item))
            content = "\n".join(content_parts)
        elif not isinstance(content, str):
            content = str(content)

        # 初始化响应字段
        text = None
        description = None
        objects: List[Dict[str, Any]] = []

        # 根据分析类型提取结果
        if analyze_type in (AnalyzeType.OCR, AnalyzeType.ALL):
            # OCR模式，提取文字
            if "文字" in content or "text" in content.lower():
                # 简单处理：假设整个内容就是OCR结果
                text = content.strip()

        if analyze_type in (AnalyzeType.OBJECT_DETECTION, AnalyzeType.ALL):
            # 物体识别模式
            if "物体" in content or "object" in content.lower():
                # 简单处理：提取描述作为物体信息
                description = content.strip()
                # 尝试解析JSON格式的物体列表
                try:
                    # 尝试从内容中提取JSON
                    if "```json" in content:
                        json_content = content.split("```json")[1].split("```")[0]
                        objects = json.loads(json_content)
                    elif "```" in content:
                        json_content = content.split("```")[1].split("```")[0]
                        objects = json.loads(json_content)
                except (json.JSONDecodeError, IndexError):
                    # 非JSON格式，创建简单的描述
                    objects = [{"name": "detected_objects", "description": content.strip()}]
            else:
                description = content.strip()
        else:
            # 默认：图像理解
            description = content.strip()

        return ImageAnalyzeResponse(
            model=model,
            text=text,
            objects=objects if objects else [],
            description=description,
            metadata={
                "analyze_type": analyze_type.value,
                "original_request": original_request.to_dict(),
            },
        )

    def _is_base64(self, data: str) -> bool:
        """
        检查字符串是否为有效的base64编码

        参数:
            data: 要检查的字符串

        返回:
            是否为有效的base64编码
        """
        import re

        if len(data) < 100:
            return False

        # Base64字符集
        base64_pattern = r"^[A-Za-z0-9+/]+={0,2}$"
        return bool(re.match(base64_pattern, data.strip()))

    async def health_check(self) -> HealthCheckResult:
        """
        执行健康检查

        通过检查API端点可用性来检测适配器是否可用。

        返回:
            健康检查结果
        """
        if not self._initialized or not self._client:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message="适配器未初始化"
            )

        try:
            # 使用较短的超时时间进行健康检查
            timeout = 10.0

            request_data = {
                "model": self._default_model,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
                                },
                                {
                                    "text": "test",
                                },
                            ],
                        }
                    ]
                },
                "parameters": {
                    "max_tokens": 1,
                },
            }

            response = await self._client.stream(
                method="POST",
                url="/services/aigc/multimodal-generation/generation",
                json=request_data,
                timeout=timeout,
            )

            # 任何响应（非超时）都表示服务可用
            if response.status_code in (200, 400, 413, 429):
                # 400可能是参数问题，但API是可达的
                # 413是请求过大，API可达
                # 429是速率限制，API可达
                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    message="适配器可用",
                    details={
                        "provider": self.provider,
                        "model": self._default_model,
                        "status_code": response.status_code,
                    }
                )
            else:
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"API返回异常状态码: {response.status_code}"
                )

        except TimeoutException:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message="健康检查超时"
            )
        except HTTPError as e:
            # 401/403 表示API密钥问题，但适配器本身可能可用
            if e.response and e.response.status_code in (401, 403):
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message="API密钥无效或权限不足"
                )
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"健康检查失败: {e}"
            )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"健康检查出错: {e}"
            )

    async def cleanup(self) -> None:
        """清理适配器资源"""
        await self.shutdown()
        await super().cleanup()

    async def shutdown(self) -> None:
        """
        关闭适配器，释放资源
        """
        if self._client:
            await self._client.aclose()
            self._client = None
        self._initialized = False
