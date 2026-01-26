"""
模块名称：自研记忆管理器实现
功能描述：包装现有ShortTermMemory和LongTermMemory为IMemory接口
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - NativeMemory: 自研记忆管理器实现

依赖模块：
    - core.interfaces.memory: 记忆管理接口
    - core.agent.memory: 记忆管理
"""

from typing import Dict, Any, Optional, List
from core.interfaces.memory import IMemory
from core.agent.memory import ShortTermMemory, LongTermMemory


class NativeMemory(IMemory):
    """
    自研记忆管理器实现
    
    包装现有ShortTermMemory和LongTermMemory为IMemory接口。
    """
    
    def __init__(self, config: Dict[str, Any], storage_manager: Optional[Any] = None):
        """
        初始化自研记忆管理器
        
        参数:
            config: 配置字典
            storage_manager: 存储管理器（可选，用于长期记忆）
        """
        self._config = config
        memory_config = config.get("memory", {})
        max_messages = memory_config.get("max_messages")
        self._short_term = ShortTermMemory(max_messages=max_messages)
        self._long_term = LongTermMemory(storage_manager) if storage_manager else None
    
    def add_message(self, role: str, content: str, **kwargs: Any) -> None:
        """
        添加消息
        
        参数:
            role: 消息角色
            content: 消息内容
            **kwargs: 其他消息字段
        """
        # 如果有tool_call_id，使用add_tool_message
        if role == "tool" and "tool_call_id" in kwargs:
            tool_name = kwargs.pop("tool_name", "tool")
            self._short_term.add_tool_message(tool_name, content, tool_call_id=kwargs.get("tool_call_id"))
        else:
            self._short_term.add_message(role, content)
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """
        获取消息列表
        
        返回:
            消息列表
        """
        return self._short_term.get_messages()
    
    def clear(self) -> None:
        """清空记忆"""
        self._short_term.clear()
    
    async def save(self, conversation_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        保存记忆（长期）
        
        参数:
            conversation_id: 对话ID
            metadata: 元数据（可选）
        """
        if self._long_term:
            messages = self.get_messages()
            await self._long_term.save(conversation_id, messages, metadata)
    
    async def load(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        加载记忆（长期）
        
        参数:
            conversation_id: 对话ID
        
        返回:
            消息列表，如果不存在返回None
        """
        if self._long_term:
            return await self._long_term.load(conversation_id)
        return None
    
    @property
    def message_count(self) -> int:
        """
        消息数量
        
        返回:
            当前消息数量
        """
        return self._short_term.message_count
