"""
模块名称：对话上下文管理模块
功能描述：管理LLM对话的上下文和历史记录
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - ConversationContext: 对话上下文管理类

依赖模块：
    - typing: 类型注解
"""

from typing import List, Dict, Optional, Any


class ConversationContext:
    """
    对话上下文管理
    
    管理LLM对话的上下文和历史记录，支持添加消息、获取消息列表等功能。
    
    特性：
        - 管理对话历史
        - 支持上下文清理
        - 支持上下文限制（最大消息数）
        - 支持Function Calling的tool消息（包含tool_call_id）
    
    示例:
        >>> context = ConversationContext()
        >>> context.add_message("user", "你好")
        >>> context.add_message("assistant", "你好！有什么可以帮助你的吗？")
        >>> messages = context.get_messages()
    """
    
    def __init__(self, max_messages: Optional[int] = None) -> None:
        """
        初始化对话上下文
        
        参数:
            max_messages: 最大消息数量（可选，None表示无限制）
        """
        self._messages: List[Dict[str, Any]] = []
        self._max_messages: Optional[int] = max_messages
    
    def add_message(self, role: str, content: str, **kwargs: Any) -> None:
        """
        添加消息
        
        参数:
            role: 消息角色（user/assistant/system/tool）
            content: 消息内容
            **kwargs: 其他消息字段（如tool_call_id用于Function Calling）
        
        异常:
            ValueError: 角色无效时抛出
        
        示例:
            >>> context.add_message("user", "你好")
            >>> context.add_message("tool", "结果", tool_call_id="call_123")
        """
        if role not in ["user", "assistant", "system", "tool"]:
            raise ValueError(f"无效的角色: {role}")
        
        message: Dict[str, Any] = {"role": role, "content": content}
        # 添加其他字段（如tool_call_id）
        message.update(kwargs)
        self._messages.append(message)
        
        # 如果设置了最大消息数，移除最旧的消息
        if self._max_messages and len(self._messages) > self._max_messages:
            self._messages.pop(0)
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """
        获取消息列表
        
        返回:
            消息列表，每个消息是包含role和content的字典（可能包含其他字段如tool_call_id）
        
        示例:
            >>> messages = context.get_messages()
        """
        return self._messages.copy()
    
    def clear(self) -> None:
        """清空上下文"""
        self._messages.clear()
    
    @property
    def message_count(self) -> int:
        """获取消息数量"""
        return len(self._messages)
    
    @property
    def is_empty(self) -> bool:
        """检查上下文是否为空"""
        return len(self._messages) == 0
