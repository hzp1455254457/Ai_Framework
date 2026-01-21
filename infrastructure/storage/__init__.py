"""
存储管理模块

提供统一的存储管理能力，支持多种存储后端（数据库、文件存储等）。
"""

from .manager import StorageManager
from .connection_pool import ConnectionPoolManager

__all__ = [
    "StorageManager",
    "ConnectionPoolManager",
]
