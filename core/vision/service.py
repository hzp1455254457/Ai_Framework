"""
模块名称：Vision服务主类模块
功能描述：提供统一的视觉服务接口，支持多种Vision服务提供商
创建日期：2026-01-22
最后更新：2026-01-22
维护者：AI框架团队

主要类：
    - VisionService: Vision服务主类

依赖模块：
    - core.base.service: 服务基类
    - core.vision.models: Vision数据模型
    - core.vision.adapters.base: 适配器基类
    - infrastructure.config: 配置管理
    - infrastructure.log: 日志管理
"""

from typing import Dict, Any, Optional, List
from core.base.service import BaseService
from core.vision.models import (
    ImageGenerateRequest,
    ImageGenerateResponse,
    ImageAnalyzeRequest,
    ImageAnalyzeResponse,
    ImageEditRequest,
    ImageEditResponse,
)
from core.vision.adapters.base import BaseVisionAdapter
from core.base.health_check import HealthCheckResult, HealthStatus


class VisionError(Exception):
    """Vision服务错误异常"""
    pass


class VisionService(BaseService):
    """
    Vision服务主类
    
    提供统一的视觉服务接口，支持多种Vision服务提供商。
    通过适配器模式实现不同提供商的统一调用接口。
    
    特性：
        - 图像生成
        - 图像分析
        - 图像编辑
        - 适配器自动发现和注册
    
    示例：
        >>> service = VisionService(config)
        >>> await service.initialize()
        >>> request = ImageGenerateRequest(prompt="A beautiful sunset")
        >>> response = await service.generate_image(request)
    
    属性:
        _adapters: 适配器字典
        _default_adapter: 默认适配器名称
        _auto_discover: 是否自动发现适配器
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        初始化Vision服务
        
        参数:
            config: 服务配置字典
        """
        super().__init__(config)
        self._adapters: Dict[str, BaseVisionAdapter] = {}
        self._default_adapter: Optional[str] = config.get("vision", {}).get("default_adapter")
        self._auto_discover: bool = config.get("vision", {}).get("auto_discover_adapters", True)
    
    async def initialize(self) -> None:
        """初始化服务资源"""
        await super().initialize()
        
        # 自动发现适配器（未来实现）
        # if self._auto_discover:
        #     await self._auto_register_adapters()
        
        self.logger.info("Vision服务初始化完成")
        self.logger.info(f"已注册适配器: {list(self._adapters.keys())}")
    
    def register_adapter(self, adapter: BaseVisionAdapter) -> None:
        """
        手动注册适配器
        
        参数:
            adapter: 适配器实例
        
        示例:
            >>> adapter = DalleAdapter(config)
            >>> await adapter.initialize()
            >>> service.register_adapter(adapter)
        """
        self._adapters[adapter.name] = adapter
        self.logger.info(f"手动注册适配器: {adapter.name} (provider: {adapter.provider})")
    
    def _get_adapter(self, adapter_name: Optional[str] = None) -> BaseVisionAdapter:
        """
        获取适配器
        
        根据适配器名称获取适配器实例，如果未指定则使用默认适配器。
        
        参数:
            adapter_name: 适配器名称（可选）
        
        返回:
            适配器实例
        
        异常:
            VisionError: 找不到适配器时抛出
        """
        if not self._adapters:
            raise VisionError("没有注册的适配器")
        
        # 如果指定了适配器名称，使用指定的适配器
        if adapter_name:
            if adapter_name not in self._adapters:
                raise VisionError(f"适配器不存在: {adapter_name}")
            return self._adapters[adapter_name]
        
        # 使用默认适配器
        if self._default_adapter and self._default_adapter in self._adapters:
            return self._adapters[self._default_adapter]
        
        # 使用第一个注册的适配器
        return next(iter(self._adapters.values()))
    
    async def generate_image(
        self,
        request: ImageGenerateRequest,
        adapter_name: Optional[str] = None,
        **kwargs: Any,
    ) -> ImageGenerateResponse:
        """
        生成图像
        
        根据文本提示词生成图像。
        
        参数:
            request: 图像生成请求
            adapter_name: 适配器名称（可选，默认使用配置的默认适配器）
            **kwargs: 其他适配器特定参数
        
        返回:
            ImageGenerateResponse对象，包含生成的图像
        
        异常:
            VisionError: 生成失败时抛出
            ValueError: 参数验证失败时抛出
        
        示例:
            >>> request = ImageGenerateRequest(prompt="A beautiful sunset", size="1024x1024")
            >>> response = await service.generate_image(request)
            >>> print(f"生成了 {response.count} 张图像")
        """
        adapter = self._get_adapter(adapter_name)
        
        self.logger.debug(f"发送图像生成请求，适配器: {adapter.name}, 提示词: {request.prompt[:50]}...")
        
        try:
            response = await adapter.generate_image(request, **kwargs)
            self.logger.debug(f"图像生成完成，生成了 {response.count} 张图像")
            return response
        except Exception as e:
            self.logger.error(f"图像生成失败: {e}", exc_info=True)
            raise VisionError(f"图像生成失败: {e}") from e
    
    async def analyze_image(
        self,
        request: ImageAnalyzeRequest,
        adapter_name: Optional[str] = None,
        **kwargs: Any,
    ) -> ImageAnalyzeResponse:
        """
        分析图像
        
        分析图像内容（OCR、物体识别、图像理解等）。
        
        参数:
            request: 图像分析请求
            adapter_name: 适配器名称（可选，默认使用配置的默认适配器）
            **kwargs: 其他适配器特定参数
        
        返回:
            ImageAnalyzeResponse对象，包含分析结果
        
        异常:
            VisionError: 分析失败时抛出
            ValueError: 参数验证失败时抛出
        
        示例:
            >>> request = ImageAnalyzeRequest(image="https://example.com/image.jpg", analyze_type="ocr")
            >>> response = await service.analyze_image(request)
            >>> print(f"识别文本: {response.text}")
        """
        adapter = self._get_adapter(adapter_name)
        
        self.logger.debug(f"发送图像分析请求，适配器: {adapter.name}, 分析类型: {request.analyze_type.value}")
        
        try:
            response = await adapter.analyze_image(request, **kwargs)
            self.logger.debug(f"图像分析完成，模型: {response.model}")
            return response
        except Exception as e:
            self.logger.error(f"图像分析失败: {e}", exc_info=True)
            raise VisionError(f"图像分析失败: {e}") from e
    
    async def edit_image(
        self,
        request: ImageEditRequest,
        adapter_name: Optional[str] = None,
        **kwargs: Any,
    ) -> ImageEditResponse:
        """
        编辑图像
        
        根据编辑指令修改图像。
        
        参数:
            request: 图像编辑请求
            adapter_name: 适配器名称（可选，默认使用配置的默认适配器）
            **kwargs: 其他适配器特定参数
        
        返回:
            ImageEditResponse对象，包含编辑后的图像
        
        异常:
            VisionError: 编辑失败时抛出
            ValueError: 参数验证失败时抛出
        
        示例:
            >>> request = ImageEditRequest(
            ...     image="https://example.com/image.jpg",
            ...     prompt="Add a rainbow in the sky"
            ... )
            >>> response = await service.edit_image(request)
            >>> print(f"生成了 {response.count} 张编辑后的图像")
        """
        adapter = self._get_adapter(adapter_name)
        
        self.logger.debug(f"发送图像编辑请求，适配器: {adapter.name}, 提示词: {request.prompt[:50]}...")
        
        try:
            response = await adapter.edit_image(request, **kwargs)
            self.logger.debug(f"图像编辑完成，生成了 {response.count} 张图像")
            return response
        except Exception as e:
            self.logger.error(f"图像编辑失败: {e}", exc_info=True)
            raise VisionError(f"图像编辑失败: {e}") from e
    
    async def check_adapter_health(self, adapter_name: Optional[str] = None) -> Dict[str, HealthCheckResult]:
        """
        检查适配器健康状态
        
        检查指定适配器或所有适配器的健康状态。
        
        参数:
            adapter_name: 适配器名称（可选，如果为None则检查所有适配器）
        
        返回:
            适配器健康状态字典，键为适配器名称，值为健康检查结果
        """
        results: Dict[str, HealthCheckResult] = {}
        
        if adapter_name:
            if adapter_name not in self._adapters:
                return {adapter_name: HealthCheckResult(
                    status=HealthStatus.UNKNOWN,
                    message="适配器未注册"
                )}
            adapters_to_check = {adapter_name: self._adapters[adapter_name]}
        else:
            adapters_to_check = self._adapters
        
        for name, adapter in adapters_to_check.items():
            try:
                result = await adapter.health_check()
                results[name] = result
            except Exception as e:
                results[name] = HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"健康检查异常: {e}"
                )
        
        return results
    
    async def get_healthy_adapters(self) -> List[str]:
        """
        获取健康的适配器列表
        
        返回:
            健康的适配器名称列表
        """
        health_results = await self.check_adapter_health()
        healthy_adapters = [
            name for name, result in health_results.items()
            if result.status == HealthStatus.HEALTHY
        ]
        return healthy_adapters