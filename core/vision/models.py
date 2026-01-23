"""
模块名称：Vision数据模型模块
功能描述：定义Vision服务相关的数据模型
创建日期：2026-01-22
最后更新：2026-01-22
维护者：AI框架团队

主要类：
    - ImageGenerateRequest: 图像生成请求模型
    - ImageGenerateResponse: 图像生成响应模型
    - ImageAnalyzeRequest: 图像分析请求模型
    - ImageAnalyzeResponse: 图像分析响应模型
    - ImageEditRequest: 图像编辑请求模型
    - ImageEditResponse: 图像编辑响应模型

依赖模块：
    - typing: 类型注解
    - datetime: 时间处理
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum


class ImageSize(str, Enum):
    """图像尺寸枚举"""
    SQUARE_256 = "256x256"
    SQUARE_512 = "512x512"
    SQUARE_1024 = "1024x1024"
    LANDSCAPE_1024 = "1024x1792"
    PORTRAIT_1024 = "1792x1024"


class AnalyzeType(str, Enum):
    """图像分析类型枚举"""
    OCR = "ocr"  # 光学字符识别
    OBJECT_DETECTION = "object_detection"  # 物体识别
    IMAGE_UNDERSTANDING = "image_understanding"  # 图像理解
    ALL = "all"  # 全部分析


class ImageGenerateRequest:
    """
    图像生成请求模型
    
    表示图像生成请求，包含提示词、尺寸、数量等参数。
    
    属性:
        prompt: 文本提示词
        size: 图像尺寸
        n: 生成图像数量
        quality: 图像质量（standard/hd）
        style: 图像风格（可选）
        metadata: 其他元数据
    """
    
    def __init__(
        self,
        prompt: str,
        size: Union[str, ImageSize] = ImageSize.SQUARE_1024,
        n: int = 1,
        quality: str = "standard",
        style: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化图像生成请求
        
        参数:
            prompt: 文本提示词（必填）
            size: 图像尺寸，默认 1024x1024
            n: 生成图像数量，默认 1
            quality: 图像质量（standard/hd），默认 standard
            style: 图像风格（可选）
            metadata: 其他元数据（可选）
        """
        if not prompt or not prompt.strip():
            raise ValueError("提示词不能为空")
        if n < 1 or n > 10:
            raise ValueError("生成图像数量必须在 1-10 之间")
        
        self.prompt = prompt.strip()
        self.size = ImageSize(size) if isinstance(size, str) else size
        self.n = n
        self.quality = quality
        self.style = style
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "prompt": self.prompt,
            "size": self.size.value,
            "n": self.n,
            "quality": self.quality,
            "style": self.style,
            "metadata": self.metadata,
        }


class ImageGenerateResponse:
    """
    图像生成响应模型
    
    表示图像生成的结果。
    
    属性:
        images: 生成的图像列表（URL或base64数据）
        model: 使用的模型名称
        created_at: 创建时间
        metadata: 其他元数据（如生成时间、成本等）
    """
    
    def __init__(
        self,
        images: List[str],
        model: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化图像生成响应
        
        参数:
            images: 生成的图像列表（URL或base64编码的字符串）
            model: 使用的模型名称
            metadata: 其他元数据（可选）
        """
        if not images:
            raise ValueError("图像列表不能为空")
        
        self.images = images
        self.model = model
        self.created_at = datetime.now()
        self.metadata = metadata or {}
    
    @property
    def count(self) -> int:
        """获取生成的图像数量"""
        return len(self.images)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "images": self.images,
            "model": self.model,
            "count": self.count,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


class ImageAnalyzeRequest:
    """
    图像分析请求模型
    
    表示图像分析请求，包含图像数据和分析类型。
    
    属性:
        image: 图像数据（URL、base64或文件路径）
        analyze_type: 分析类型（OCR、物体识别、图像理解等）
        options: 分析选项（可选）
        metadata: 其他元数据
    """
    
    def __init__(
        self,
        image: str,
        analyze_type: Union[str, AnalyzeType] = AnalyzeType.ALL,
        options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化图像分析请求
        
        参数:
            image: 图像数据（URL、base64编码字符串或文件路径）
            analyze_type: 分析类型，默认 ALL（全部分析）
            options: 分析选项（可选）
            metadata: 其他元数据（可选）
        """
        if not image or not image.strip():
            raise ValueError("图像数据不能为空")
        
        self.image = image.strip()
        self.analyze_type = AnalyzeType(analyze_type) if isinstance(analyze_type, str) else analyze_type
        self.options = options or {}
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "image": self.image,
            "analyze_type": self.analyze_type.value,
            "options": self.options,
            "metadata": self.metadata,
        }


class ImageAnalyzeResponse:
    """
    图像分析响应模型
    
    表示图像分析的结果。
    
    属性:
        text: OCR识别的文本（如果有）
        objects: 识别的物体列表（如果有）
        description: 图像描述（如果有）
        model: 使用的模型名称
        created_at: 创建时间
        metadata: 其他元数据
    """
    
    def __init__(
        self,
        model: str,
        text: Optional[str] = None,
        objects: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化图像分析响应
        
        参数:
            model: 使用的模型名称
            text: OCR识别的文本（可选）
            objects: 识别的物体列表（可选）
            description: 图像描述（可选）
            metadata: 其他元数据（可选）
        """
        self.model = model
        self.text = text
        self.objects = objects or []
        self.description = description
        self.created_at = datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "model": self.model,
            "text": self.text,
            "objects": self.objects,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


class ImageEditRequest:
    """
    图像编辑请求模型
    
    表示图像编辑请求，包含原始图像、编辑指令等。
    
    属性:
        image: 原始图像数据（URL、base64或文件路径）
        prompt: 编辑提示词
        mask: 遮罩图像（可选，指定编辑区域）
        size: 输出图像尺寸（可选）
        n: 生成图像数量
        metadata: 其他元数据
    """
    
    def __init__(
        self,
        image: str,
        prompt: str,
        mask: Optional[str] = None,
        size: Optional[Union[str, ImageSize]] = None,
        n: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化图像编辑请求
        
        参数:
            image: 原始图像数据（URL、base64编码字符串或文件路径）
            prompt: 编辑提示词（必填）
            mask: 遮罩图像（可选，指定需要编辑的区域）
            size: 输出图像尺寸（可选）
            n: 生成图像数量，默认 1
            metadata: 其他元数据（可选）
        """
        if not image or not image.strip():
            raise ValueError("图像数据不能为空")
        if not prompt or not prompt.strip():
            raise ValueError("编辑提示词不能为空")
        if n < 1 or n > 10:
            raise ValueError("生成图像数量必须在 1-10 之间")
        
        self.image = image.strip()
        self.prompt = prompt.strip()
        self.mask = mask
        self.size = ImageSize(size) if isinstance(size, str) and size else size
        self.n = n
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "image": self.image,
            "prompt": self.prompt,
            "mask": self.mask,
            "size": self.size.value if self.size else None,
            "n": self.n,
            "metadata": self.metadata,
        }


class ImageEditResponse:
    """
    图像编辑响应模型
    
    表示图像编辑的结果。
    
    属性:
        images: 编辑后的图像列表（URL或base64数据）
        model: 使用的模型名称
        created_at: 创建时间
        metadata: 其他元数据
    """
    
    def __init__(
        self,
        images: List[str],
        model: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化图像编辑响应
        
        参数:
            images: 编辑后的图像列表（URL或base64编码的字符串）
            model: 使用的模型名称
            metadata: 其他元数据（可选）
        """
        if not images:
            raise ValueError("图像列表不能为空")
        
        self.images = images
        self.model = model
        self.created_at = datetime.now()
        self.metadata = metadata or {}
    
    @property
    def count(self) -> int:
        """获取编辑后的图像数量"""
        return len(self.images)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "images": self.images,
            "model": self.model,
            "count": self.count,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }
