"""
Vision适配器模块

提供Vision服务适配器的基类和接口定义。
"""

from core.vision.adapters.base import BaseVisionAdapter
from core.vision.adapters.dalle_adapter import DALLEAdapter

__all__ = [
    "BaseVisionAdapter",
    "DALLEAdapter",
]
