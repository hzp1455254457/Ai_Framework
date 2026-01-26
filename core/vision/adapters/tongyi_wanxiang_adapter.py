"""
模块名称：通义万相适配器模块
功能描述：实现通义万相TongYi WanXiang图像生成服务的适配器
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - TongYiWanXiangAdapter: 通义万相图像生成适配器

依赖模块：
    - httpx: 异步HTTP客户端
    - core.vision.adapters.base: 适配器基类
    - core.vision.models: Vision数据模型
"""

import json
import logging
from typing import Dict, Any, Optional, List
from httpx import AsyncClient, HTTPError, TimeoutException
from core.vision.adapters.base import BaseVisionAdapter, VisionAdapterError
from core.base.health_check import HealthStatus, HealthCheckResult
from core.vision.models import (
    ImageGenerateRequest,
    ImageGenerateResponse,
    ImageAnalyzeRequest,
    ImageAnalyzeResponse,
    ImageEditRequest,
    ImageEditResponse,
    ImageSize,
)


class TongYiWanXiangAdapter(BaseVisionAdapter):
    """
    通义万相图像生成适配器

    实现阿里云通义万相图像生成服务（基于DashScope API）的适配器，支持文本到图像生成。

    特性：
        - 支持通义万相图像生成API
        - 支持多种图像尺寸和风格选项
        - 错误处理和重试
        - 支持API密钥复用（与通义千问共用）
        - 与现有Vision服务无缝集成

    配置示例:
        {
            "api_key": "your-api-key",  # 可留空，会从Qwen配置或环境变量获取
            "base_url": "https://dashscope.aliyuncs.com/api/v1",  # 可选
            "model": "wanx-v1"  # 可选，默认wanx-v1
        }

    示例:
        >>> adapter = TongYiWanXiangAdapter({"api_key": "your-key"})
        >>> await adapter.initialize()
        >>> request = ImageGenerateRequest(prompt="A beautiful sunset")
        >>> response = await adapter.generate_image(request)
    """

    # 支持的模型列表
    SUPPORTED_MODELS = ["wanx-v1"]

    # 默认模型
    DEFAULT_MODEL = "wanx-v1"

    # 默认API端点
    DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"

    # 支持的图像尺寸
    SUPPORTED_SIZES = [
        ImageSize.SQUARE_1024,  # 1024x1024
        ImageSize.LANDSCAPE_1024,  # 1024x1792
        ImageSize.PORTRAIT_1024,  # 1792x1024
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化通义万相适配器

        参数:
            config: 适配器配置，包含api_key、base_url、model等
        """
        super().__init__(config)
        self._api_key: str = ""
        self._base_url: str = self.DEFAULT_BASE_URL
        self._default_model: str = self.DEFAULT_MODEL
        self._client: Optional[AsyncClient] = None
        # 初始化logger
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def name(self) -> str:
        """适配器名称"""
        return "tongyi-wanxiang-adapter"

    @property
    def provider(self) -> str:
        """服务提供商名称"""
        return "tongyi-wanxiang"
    
    def get_supported_operations(self) -> List[str]:
        """
        获取适配器支持的操作类型列表
        
        通义万相适配器支持图像生成功能。
        
        返回:
            支持的操作类型列表：["generate"]
        """
        return ["generate"]

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
            raise VisionAdapterError("通义万相API密钥未配置")

        self._base_url = self._config.get("base_url", self.DEFAULT_BASE_URL)
        self._default_model = self._config.get("model", self.DEFAULT_MODEL)

        # 验证模型名称
        if self._default_model not in self.SUPPORTED_MODELS:
            raise VisionAdapterError(
                f"不支持的模型: {self._default_model}，"
                f"仅支持 {', '.join(self.SUPPORTED_MODELS)}"
            )

        # 创建HTTP客户端
        self._client = AsyncClient(
            base_url=self._base_url,
            timeout=120.0,  # 图像生成可能需要更长时间
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable",
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

        根据文本提示词生成图像，调用通义万相API。

        参数:
            request: 图像生成请求
            **kwargs: 其他适配器特定参数（如model指定模型）

        返回:
            ImageGenerateResponse对象，包含生成的图像

        异常:
            VisionAdapterError: 生成失败时抛出
        """
        if not self._client:
            raise VisionAdapterError("适配器未初始化")

        # 确定使用的模型（优先使用kwargs中的model，否则使用默认模型）
        model = kwargs.get("model", self._default_model)
        if model not in self.SUPPORTED_MODELS:
            raise VisionAdapterError(
                f"不支持的模型: {model}，仅支持 {', '.join(self.SUPPORTED_MODELS)}"
            )

        # 构建请求数据
        request_data = self._build_request_data(request, model)

        try:
            # 发送请求到通义万相API
            response = await self._client.post(
                "/services/aigc/text2image/image-synthesis",
                json=request_data,
            )
            response.raise_for_status()

            result = response.json()

            # 解析响应
            output = result.get("output", {})
            task_id = output.get("task_id", "")
            
            # 尝试直接解析图像（如果是同步返回）
            images = self._parse_images(output)

            # 如果没有图像但有任务ID，则轮询任务状态
            if not images and task_id:
                self.logger.info(f"通义万相任务已提交，任务ID: {task_id}，开始轮询状态...")
                task_output = await self._wait_for_task(task_id)
                images = self._parse_images(task_output)
                # 更新output以便后续使用
                output = task_output

            if not images:
                raise VisionAdapterError("API响应中没有图像数据")

            # 构建响应对象
            return ImageGenerateResponse(
                images=images,
                model=model,
                metadata={
                    "task_id": task_id,
                    "prompt": request.prompt,
                },
            )

        except HTTPError as e:
            error_message = f"通义万相API调用失败: {e}"
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_message = f"{error_message} - {error_detail.get('message', error_detail.get('error', str(e)))}"
                except Exception:
                    error_message = f"{error_message} - {e.response.text}"
            raise VisionAdapterError(error_message) from e
        except Exception as e:
            raise VisionAdapterError(f"通义万相适配器错误: {str(e)}") from e

    def _build_request_data(self, request: ImageGenerateRequest, model: str) -> Dict[str, Any]:
        """
        构建请求数据

        参数:
            request: 图像生成请求
            model: 使用的模型名称

        返回:
            API请求数据字典
        """
        # 基础请求数据
        request_data: Dict[str, Any] = {
            "model": model,
            "input": {
                "prompt": request.prompt,
            },
        }

        # 处理图像尺寸
        size_mapping = {
            ImageSize.SQUARE_1024: "1024*1024",
            ImageSize.LANDSCAPE_1024: "1024*1792",
            ImageSize.PORTRAIT_1024: "1792*1024",
        }

        if request.size in size_mapping:
            request_data["parameters"] = {
                "size": size_mapping[request.size],
            }
        else:
            # 默认使用1024x1024
            request_data["parameters"] = {
                "size": "1024*1024",
            }

        # 处理数量（通义万相通常只支持1张）
        if hasattr(request, "n") and request.n and request.n > 1:
            self.logger.warning("通义万相通常只支持生成1张图像，将忽略n参数")

        return request_data

    async def edit_image(
        self,
        request: ImageEditRequest,
        **kwargs: Any,
    ) -> ImageEditResponse:
        """
        编辑图像
        
        使用通义万相2.1 (wanx2.1-imageedit) 模型进行图像编辑。
        支持功能：
        1. 局部重绘 (Repainting): 当提供 mask 时
        2. 指令编辑 (Instruction Edit): 当未提供 mask 时
        3. 风格化 (Stylization): 通过 metadata 指定 function="stylization_all" 或 "stylization_local"
        
        参数:
            request: 图像编辑请求
            **kwargs: 其他参数
            
        返回:
            ImageEditResponse对象
        """
        if not self._initialized or not self._client:
            raise VisionAdapterError("适配器未初始化")
            
        try:
            # 确定功能类型
            function_type = request.metadata.get("function")
            if not function_type:
                if request.mask:
                    function_type = "description_edit_with_mask"  # 局部重绘 (原 repainting)
                else:
                    function_type = "description_edit"  # 指令编辑 (原 instruction_edit)
            
            # 确定模型
            model = request.metadata.get("model", "wanx2.1-imageedit")
            
            # 验证图像输入
            image_input = request.image
            if not image_input.startswith(("http://", "https://")):
                if len(image_input) > 1024: # 假设Base64肯定很长
                    raise VisionAdapterError(
                        "通义万相API仅支持公开可访问的图像URL (http/https)。"
                        "暂不支持Base64或本地文件直接上传，请提供有效的图像URL。"
                    )
                raise VisionAdapterError("无效的图像URL，必须以 http:// 或 https:// 开头")

            # 构建请求体
            # 注意：通义万相图像编辑使用 image2image 接口
            input_data = {
                "function": function_type,
                "prompt": request.prompt,
                "base_image_url": image_input,
            }
            
            # 如果有遮罩，添加遮罩参数
            if request.mask:
                mask_input = request.mask
                if not mask_input.startswith(("http://", "https://")):
                     raise VisionAdapterError(
                        "通义万相API仅支持公开可访问的遮罩图像URL (http/https)。"
                        "暂不支持Base64或本地文件直接上传。"
                    )
                input_data["mask_image_url"] = mask_input
                
            request_data = {
                "model": model,
                "input": input_data,
                "parameters": {
                    "n": request.n,
                }
            }
            
            # 发送请求 (必须使用异步模式)
            headers = {
                "X-DashScope-Async": "enable",
                "Content-Type": "application/json"
            }
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"
                
            response = await self._client.post(
                "/services/aigc/image2image/image-synthesis",
                json=request_data,
                headers=headers
            )
            response.raise_for_status()
            
            # 解析响应（异步任务）
            result = response.json()
            output = result.get("output", {})
            task_id = output.get("task_id", "")
            
            if not task_id:
                raise VisionAdapterError("API未返回任务ID")
                
            self.logger.info(f"通义万相图像编辑任务提交，任务ID: {task_id}，开始轮询状态...")
            
            # 轮询任务状态
            task_output = await self._wait_for_task(task_id)
            
            # 解析结果图像
            images = self._parse_images(task_output)
            
            if not images:
                raise VisionAdapterError("API响应中没有编辑后的图像数据")
                
            return ImageEditResponse(
                images=images,
                model=model,
                metadata={
                    "task_id": task_id,
                    "function": function_type,
                    "original_request": request.to_dict()
                }
            )
            
        except HTTPError as e:
            error_message = f"通义万相图像编辑API调用失败: {e}"
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_message = f"{error_message} - {error_detail.get('message', error_detail.get('error', str(e)))}"
                except Exception:
                    error_message = f"{error_message} - {e.response.text}"
            raise VisionAdapterError(error_message) from e
        except Exception as e:
            if isinstance(e, VisionAdapterError):
                raise
            raise VisionAdapterError(f"通义万相适配器错误: {str(e)}") from e

    def _parse_images(self, output: Dict[str, Any]) -> List[str]:
        """
        从API响应中解析图像URL列表

        参数:
            output: API响应中的output字段

        返回:
            图像URL列表
        """
        images: List[str] = []

        # 尝试多种响应格式
        # 格式1: tasks -> task_results -> images
        tasks = output.get("tasks", [])
        for task in tasks:
            task_results = task.get("task_results", [])
            for task_result in task_results:
                if "image" in task_result:
                    images.append(task_result["image"])
                elif "images" in task_result:
                    images.extend(task_result["images"])

        # 格式2: direct images array
        if not images and "images" in output:
            for item in output["images"]:
                if isinstance(item, str):
                    images.append(item)
                elif isinstance(item, dict) and "url" in item:
                    images.append(item["url"])

        # 格式4: results -> url (DashScope常见异步任务格式)
        results = output.get("results", [])
        if not images and results:
            for result in results:
                if isinstance(result, dict) and "url" in result:
                    images.append(result["url"])
                elif isinstance(result, dict) and "image_url" in result:
                    images.append(result["image_url"])

        # 格式5: task_result -> images (部分异步接口)
        if not images and "task_result" in output:
             task_result = output["task_result"]
             if isinstance(task_result, dict):
                 if "images" in task_result:
                     for img in task_result["images"]:
                         if isinstance(img, dict) and "url" in img:
                             images.append(img["url"])
                         elif isinstance(img, str):
                             images.append(img)

        return images

    async def _wait_for_task(self, task_id: str) -> Dict[str, Any]:
        """
        轮询等待任务完成
        
        参数:
            task_id: 任务ID
            
        返回:
            任务输出结果
            
        异常:
            VisionAdapterError: 任务失败或超时
        """
        import asyncio
        
        # 轮询配置
        max_retries = 60  # 最大重试次数（约30-60秒）
        interval = 1.0    # 初始间隔
        
        for i in range(max_retries):
            try:
                # 查询任务状态
                response = await self._client.get(f"/tasks/{task_id}")
                response.raise_for_status()
                
                result = response.json()
                output = result.get("output", {})
                task_status = output.get("task_status", "UNKNOWN")
                
                if task_status == "SUCCEEDED":
                    return output
                
                if task_status == "FAILED":
                    message = output.get("message", "未知错误")
                    code = output.get("code", "UNKNOWN_ERROR")
                    raise VisionAdapterError(f"通义万相任务失败: {code} - {message}")
                
                if task_status in ["PENDING", "RUNNING"]:
                    # 继续等待
                    await asyncio.sleep(interval)
                    continue
                    
                # 其他状态
                self.logger.warning(f"通义万相任务状态未知: {task_status}")
                await asyncio.sleep(interval)
                
            except HTTPError as e:
                # 网络错误，稍后重试
                self.logger.warning(f"查询任务状态失败: {e}，正在重试...")
                await asyncio.sleep(interval)
            except Exception as e:
                if isinstance(e, VisionAdapterError):
                    raise
                self.logger.error(f"轮询任务出错: {e}")
                await asyncio.sleep(interval)
                
        raise VisionAdapterError(f"通义万相任务超时，任务ID: {task_id}")

    async def analyze_image(
        self,
        request: ImageAnalyzeRequest,
        **kwargs: Any,
    ) -> ImageAnalyzeResponse:
        """
        分析图像

        通义万相适配器不支持图像分析功能，此方法会抛出异常。

        参数:
            request: 图像分析请求
            **kwargs: 其他适配器特定参数

        返回:
            ImageAnalyzeResponse对象

        异常:
            VisionAdapterError: 通义万相不支持图像分析
        """
        raise VisionAdapterError(
            "通义万相适配器不支持图像分析功能，"
            "请使用Qwen-Vision适配器进行图像分析"
        )

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

            # 发送一个简单的验证请求
            request_data = {
                "model": self._default_model,
                "input": {
                    "prompt": "test",  # 最小有效提示词
                },
                "parameters": {
                    "size": "1024*1024",
                },
            }

            async with self._client.stream(
                method="POST",
                url="/services/aigc/text2image/image-synthesis",
                json=request_data,
                timeout=timeout,
            ) as response:
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
