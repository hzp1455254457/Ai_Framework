"""
模块名称：LLM数据模型模块
功能描述：定义LLM服务相关的数据模型
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - LLMResponse: LLM响应模型
    - LLMMessage: LLM消息模型

依赖模块：
    - pydantic: 数据验证（可选，当前使用简单字典）
    - typing: 类型注解
"""

from typing import Dict, Any, Optional
from datetime import datetime


class LLMMessage:
    """
    LLM消息模型
    
    表示单条对话消息，包含角色和内容。
    
    属性:
        role: 消息角色（user/assistant/system）
        content: 消息内容
    """
    
    def __init__(self, role: str, content: str) -> None:
        """
        初始化消息
        
        参数:
            role: 消息角色
            content: 消息内容
        """
        self.role = role
        self.content = content
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {
            "role": self.role,
            "content": self.content,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "LLMMessage":
        """从字典创建消息"""
        return cls(
            role=data["role"],
            content=data["content"],
        )


class LLMResponse:
    """
    LLM响应模型
    
    表示LLM服务的响应结果。
    
    属性:
        content: 响应内容
        model: 使用的模型名称
        usage: Token使用信息
        metadata: 其他元数据
        created_at: 响应创建时间
    """
    
    def __init__(
        self,
        content: str,
        model: str,
        usage: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化响应
        
        参数:
            content: 响应内容
            model: 模型名称
            usage: Token使用信息
            metadata: 其他元数据
        """
        self.content = content
        self.model = model
        self.usage = usage or {}
        self.metadata = metadata or {}
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    @property
    def prompt_tokens(self) -> int:
        """获取提示Token数量"""
        return self.usage.get("prompt_tokens", 0)
    
    @property
    def completion_tokens(self) -> int:
        """获取完成Token数量"""
        return self.usage.get("completion_tokens", 0)
    
    @property
    def total_tokens(self) -> int:
        """获取总Token数量"""
        return self.usage.get("total_tokens", 0)
