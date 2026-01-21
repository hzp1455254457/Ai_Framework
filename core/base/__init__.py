"""
基础类和接口定义模块

提供所有服务、适配器和插件的基础类和接口规范。
"""

from .service import BaseService
from .adapter import BaseAdapter
from .plugin import BasePlugin

__all__ = [
    "BaseService",
    "BaseAdapter",
    "BasePlugin",
]
