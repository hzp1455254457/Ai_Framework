"""
模块名称：LLM数据模型模块
功能描述：定义LLM服务相关的数据模型
创建日期：2026-01-21
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - LLMResponse: LLM响应模型
    - LLMMessage: LLM消息模型
    - ModelCapability: 模型能力标签
    - RoutingStrategy: 路由策略枚举

依赖模块：
    - typing: 类型注解
    - dataclasses: 数据类
    - enum: 枚举类型
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


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


@dataclass
class ModelCapability:
    """
    模型能力标签
    
    用于描述模型的能力特征，用于智能路由决策。
    
    属性:
        reasoning: 推理能力（逻辑推理、数学计算等）
        creativity: 创造力（创意写作、内容生成等）
        cost_effective: 成本效益（性价比高）
        fast: 快速响应（低延迟）
        multilingual: 多语言支持
        vision: 视觉理解能力
        function_calling: 函数调用能力
    """
    reasoning: bool = False
    creativity: bool = False
    cost_effective: bool = False
    fast: bool = False
    multilingual: bool = False
    vision: bool = False
    function_calling: bool = False
    
    def to_dict(self) -> Dict[str, bool]:
        """转换为字典格式"""
        return {
            "reasoning": self.reasoning,
            "creativity": self.creativity,
            "cost_effective": self.cost_effective,
            "fast": self.fast,
            "multilingual": self.multilingual,
            "vision": self.vision,
            "function_calling": self.function_calling,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, bool]) -> "ModelCapability":
        """从字典创建能力标签"""
        return cls(**data)


class RoutingStrategy(str, Enum):
    """
    路由策略枚举
    
    定义不同的路由策略，用于智能选择适配器。
    """
    COST_FIRST = "cost_first"  # 成本优先
    PERFORMANCE_FIRST = "performance_first"  # 性能优先
    AVAILABILITY_FIRST = "availability_first"  # 可用性优先
    BALANCED = "balanced"  # 平衡模式
    MANUAL = "manual"  # 手动指定
