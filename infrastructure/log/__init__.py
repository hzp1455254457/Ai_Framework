"""
日志管理模块

提供统一的日志管理能力，支持结构化日志、多级别日志、日志轮转等功能。
"""

from .manager import LogManager

__all__ = [
    "LogManager",
]
