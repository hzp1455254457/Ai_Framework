"""
模块名称：Vision适配器基类模块
功能描述：定义Vision适配器的基类和接口
创建日期：2026-01-22
最后更新：2026-01-22
维护者：AI框架团队

主要类：
    - BaseVisionAdapter: Vision适配器基类

依赖模块：
    - core.base.adapter: 适配器基类
    - core.vision.models: Vision数据模型
    - typing: 类型注解
"""

from abc import abstractmethod
from typing import Dict, Any, Optional, List
from core.base.adapter import BaseAdapter
from core.vision.models import (
    ImageGenerateRequest,
    ImageGenerateResponse,
    ImageAnalyzeRequest,
    ImageAnalyzeResponse,
    ImageEditRequest,
    ImageEditResponse,
)


class VisionAdapterError(Exception):
    """Vision适配器错误异常"""
    pass


class BaseVisionAdapter(BaseAdapter):
    """
    Vision适配器基类
    
    所有Vision适配器的抽象基类，定义了统一的Vision调用接口。
    
    特性：
        - 统一的调用接口
        - 图像生成、分析、编辑支持
        - 响应格式标准化
    
    示例:
        >>> class MyAdapter(BaseVisionAdapter):
        ...     @property
        ...     def provider(self) -> str:
        ...         return "my-provider"
        ...     
        ...     async def generate_image(self, request: ImageGenerateRequest) -> ImageGenerateResponse:
        ...         # 实现图像生成逻辑
        ...         return ImageGenerateResponse(...)
    """
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """
        服务提供商名称
        
        返回:
            服务提供商的名称（如 "dalle", "stable-diffusion", "midjourney"）
        """
        pass
    
    def get_supported_operations(self) -> List[str]:
        """
        获取适配器支持的操作类型列表
        
        返回适配器支持的操作类型，如 ["generate", "analyze", "edit"]。
        如果适配器未实现此方法，将回退到基于名称的推断逻辑。
        
        返回:
            支持的操作类型列表，可能的值：
            - "generate": 图像生成
            - "analyze": 图像分析
            - "edit": 图像编辑
        
        示例:
            >>> adapter.get_supported_operations()
            ["generate", "edit"]
        """
        # 默认实现：尝试通过检查方法是否存在来推断支持的操作
        # 子类应该重写此方法以明确声明支持的操作
        supported = []
        if hasattr(self, 'generate_image'):
            try:
                # 检查是否是抽象方法（未实现）
                if not getattr(self.generate_image, '__isabstractmethod__', False):
                    supported.append("generate")
            except AttributeError:
                pass
        
        if hasattr(self, 'analyze_image'):
            try:
                if not getattr(self.analyze_image, '__isabstractmethod__', False):
                    supported.append("analyze")
            except AttributeError:
                pass
        
        if hasattr(self, 'edit_image'):
            try:
                if not getattr(self.edit_image, '__isabstractmethod__', False):
                    supported.append("edit")
            except AttributeError:
                pass
        
        return supported
    
    @abstractmethod
    async def generate_image(
        self,
        request: ImageGenerateRequest,
        **kwargs: Any,
    ) -> ImageGenerateResponse:
        """
        生成图像
        
        根据文本提示词生成图像。
        
        参数:
            request: 图像生成请求
            **kwargs: 其他适配器特定参数
        
        返回:
            ImageGenerateResponse对象，包含生成的图像
        
        异常:
            VisionAdapterError: 生成失败时抛出
        """
        pass
    
    @abstractmethod
    async def analyze_image(
        self,
        request: ImageAnalyzeRequest,
        **kwargs: Any,
    ) -> ImageAnalyzeResponse:
        """
        分析图像
        
        分析图像内容（OCR、物体识别、图像理解等）。
        
        参数:
            request: 图像分析请求
            **kwargs: 其他适配器特定参数
        
        返回:
            ImageAnalyzeResponse对象，包含分析结果
        
        异常:
            VisionAdapterError: 分析失败时抛出
        """
        pass
    
    @abstractmethod
    async def edit_image(
        self,
        request: ImageEditRequest,
        **kwargs: Any,
    ) -> ImageEditResponse:
        """
        编辑图像
        
        根据编辑指令修改图像。
        
        参数:
            request: 图像编辑请求
            **kwargs: 其他适配器特定参数
        
        返回:
            ImageEditResponse对象，包含编辑后的图像
        
        异常:
            VisionAdapterError: 编辑失败时抛出
        """
        pass
    
    async def call(self, *args, **kwargs) -> Dict[str, Any]:
        """
        调用服务接口（实现BaseAdapter抽象方法）
        
        此方法用于兼容BaseAdapter接口，实际调用应使用具体方法。
        
        参数:
            *args: 位置参数
            **kwargs: 关键字参数
        
        返回:
            服务响应的标准格式字典
        
        异常:
            VisionAdapterError: 调用失败时抛出
        """
        # 默认实现：根据操作类型路由到对应方法
        operation = kwargs.pop("operation", "generate")
        
        if operation == "generate":
            request = kwargs.pop("request")
            if not isinstance(request, ImageGenerateRequest):
                raise VisionAdapterError("generate操作需要ImageGenerateRequest")
            response = await self.generate_image(request, **kwargs)
            return response.to_dict()
        elif operation == "analyze":
            request = kwargs.pop("request")
            if not isinstance(request, ImageAnalyzeRequest):
                raise VisionAdapterError("analyze操作需要ImageAnalyzeRequest")
            response = await self.analyze_image(request, **kwargs)
            return response.to_dict()
        elif operation == "edit":
            request = kwargs.pop("request")
            if not isinstance(request, ImageEditRequest):
                raise VisionAdapterError("edit操作需要ImageEditRequest")
            response = await self.edit_image(request, **kwargs)
            return response.to_dict()
        else:
            raise VisionAdapterError(f"不支持的操作类型: {operation}")
