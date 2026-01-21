"""
API数据模型模块

提供API请求和响应的数据模型。
"""

from .request import ChatRequest, StreamChatRequest
from .response import ChatResponse, ErrorResponse, HealthResponse

__all__ = [
    "ChatRequest",
    "StreamChatRequest",
    "ChatResponse",
    "ErrorResponse",
    "HealthResponse",
]
