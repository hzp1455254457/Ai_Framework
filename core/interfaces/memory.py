"""
模块名称：记忆管理抽象接口
功能描述：定义记忆管理的抽象接口，支持多种实现（自研、LangChain）
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - IMemory: 记忆管理抽象接口

依赖模块：
    - abc: 抽象基类
    - typing: 类型注解
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IMemory(ABC):
    """
    记忆管理抽象接口
    
    定义统一的记忆管理接口规范，支持多种实现（自研、LangChain）。
    所有记忆管理器实现都必须实现此接口。
    
    特性：
        - 消息管理（添加、获取、清空）
        - 长期记忆（保存、加载）
        - 消息计数
    
    示例：
        >>> memory = NativeMemory(config, storage_manager)
        >>> memory.add_message("user", "Hello")
        >>> messages = memory.get_messages()
    """
    
    @abstractmethod
    def add_message(self, role: str, content: str, **kwargs: Any) -> None:
        """
        添加消息
        
        将消息添加到记忆。
        
        参数:
            role: 消息角色（user/assistant/system/tool）
            content: 消息内容
            **kwargs: 其他消息字段（如tool_call_id用于Function Calling）
        
        异常:
            ValueError: 角色无效时抛出
        
        示例:
            >>> memory.add_message("user", "Hello")
            >>> memory.add_message("tool", "结果", tool_call_id="call_123")
        """
        pass
    
    @abstractmethod
    def get_messages(self) -> List[Dict[str, Any]]:
        """
        获取消息列表
        
        返回:
            消息列表，每个消息是包含role和content的字典（可能包含其他字段）
        
        示例:
            >>> messages = memory.get_messages()
            >>> print(messages)
            [{'role': 'user', 'content': 'Hello'}, ...]
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        清空记忆
        
        清空所有消息，保留长期记忆（如果已保存）。
        
        示例:
            >>> memory.clear()
        """
        pass
    
    @abstractmethod
    async def save(self, conversation_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        保存记忆（长期）
        
        将当前消息保存到长期存储。
        
        参数:
            conversation_id: 对话ID
            metadata: 元数据（可选）
        
        异常:
            RuntimeError: 保存失败时抛出
        
        示例:
            >>> await memory.save("conv_123", metadata={"task": "weather_query"})
        """
        pass
    
    @abstractmethod
    async def load(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        加载记忆（长期）
        
        从长期存储加载消息。
        
        参数:
            conversation_id: 对话ID
        
        返回:
            消息列表，如果不存在返回None
        
        异常:
            RuntimeError: 加载失败时抛出
        
        示例:
            >>> messages = await memory.load("conv_123")
            >>> if messages:
            ...     for msg in messages:
            ...         memory.add_message(msg["role"], msg["content"])
        """
        pass
    
    @property
    @abstractmethod
    def message_count(self) -> int:
        """
        消息数量
        
        返回:
            当前消息数量
        
        示例:
            >>> count = memory.message_count
            >>> print(count)
            5
        """
        pass
