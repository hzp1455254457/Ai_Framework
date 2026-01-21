"""
模块名称：记忆管理模块
功能描述：提供Agent的短期和长期记忆管理能力
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - ShortTermMemory: 短期记忆（会话上下文）
    - LongTermMemory: 长期记忆（持久化存储）
    - MemoryError: 记忆错误异常

依赖模块：
    - core.llm.context: 对话上下文
    - infrastructure.storage: 存储管理器
    - typing: 类型注解
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from core.llm.context import ConversationContext


class MemoryError(Exception):
    """记忆模块异常基类"""
    pass


class ShortTermMemory:
    """
    短期记忆
    
    管理Agent的会话上下文，基于ConversationContext实现。
    
    特性：
        - 维护对话消息历史
        - 支持消息添加和获取
        - 支持上下文清理
    
    示例：
        >>> memory = ShortTermMemory()
        >>> memory.add_message("user", "查询北京天气")
        >>> memory.add_message("assistant", "正在查询...")
        >>> messages = memory.get_messages()
    """
    
    def __init__(self, max_messages: Optional[int] = None) -> None:
        """
        初始化短期记忆
        
        参数:
            max_messages: 最大消息数量（可选，None表示无限制）
        """
        self._context: ConversationContext = ConversationContext(max_messages=max_messages)
    
    def add_message(self, role: str, content: str) -> None:
        """
        添加消息
        
        参数:
            role: 消息角色（user/assistant/system/tool）
            content: 消息内容
        
        异常:
            ValueError: 角色无效时抛出
        """
        # 扩展支持tool角色（用于Function Calling）
        if role not in ["user", "assistant", "system", "tool"]:
            raise ValueError(f"无效的角色: {role}")
        
        self._context.add_message(role, content)
    
    def add_tool_message(self, tool_name: str, tool_result: Any) -> None:
        """
        添加工具调用结果消息
        
        参数:
            tool_name: 工具名称
            tool_result: 工具执行结果（会被转换为字符串）
        """
        # 将工具结果转换为字符串
        if isinstance(tool_result, str):
            content = tool_result
        else:
            import json
            content = json.dumps(tool_result, ensure_ascii=False)
        
        # 格式：tool_name: result
        message_content = f"{tool_name}: {content}"
        self.add_message("tool", message_content)
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        获取消息列表
        
        返回:
            消息列表，每个消息是包含role和content的字典
        """
        return self._context.get_messages()
    
    def clear(self) -> None:
        """清空短期记忆"""
        self._context.clear()
    
    @property
    def message_count(self) -> int:
        """获取消息数量"""
        return self._context.message_count
    
    @property
    def is_empty(self) -> bool:
        """检查记忆是否为空"""
        return self._context.is_empty


class LongTermMemory:
    """
    长期记忆
    
    通过StorageManager持久化Agent的对话历史。
    
    特性：
        - 持久化对话历史
        - 支持对话检索
        - 支持元数据存储
    
    示例：
        >>> from infrastructure.storage import StorageManager
        >>> storage = StorageManager(config)
        >>> await storage.initialize()
        >>> memory = LongTermMemory(storage)
        >>> await memory.save("conv1", messages, metadata={"task": "weather_query"})
        >>> messages = await memory.load("conv1")
    """
    
    def __init__(
        self,
        storage_manager: Any,  # StorageManager类型，避免循环导入
    ) -> None:
        """
        初始化长期记忆
        
        参数:
            storage_manager: StorageManager实例
        
        异常:
            MemoryError: 存储管理器无效时抛出
        """
        if storage_manager is None:
            raise MemoryError("存储管理器不能为空")
        
        self._storage = storage_manager
    
    async def save(
        self,
        conversation_id: str,
        messages: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        保存对话历史
        
        参数:
            conversation_id: 对话ID
            messages: 消息列表
            metadata: 元数据（可选）
        
        异常:
            MemoryError: 保存失败时抛出
        """
        try:
            await self._storage.save_conversation(
                conversation_id,
                messages,
                metadata,
            )
        except Exception as e:
            raise MemoryError(f"保存对话失败: {e}") from e
    
    async def load(
        self,
        conversation_id: str,
    ) -> Optional[List[Dict[str, str]]]:
        """
        加载对话历史
        
        参数:
            conversation_id: 对话ID
        
        返回:
            消息列表，如果不存在返回None
        
        异常:
            MemoryError: 加载失败时抛出
        """
        try:
            return await self._storage.get_conversation(conversation_id)
        except Exception as e:
            raise MemoryError(f"加载对话失败: {e}") from e
    
    async def delete(
        self,
        conversation_id: str,
    ) -> None:
        """
        删除对话历史
        
        参数:
            conversation_id: 对话ID
        
        异常:
            MemoryError: 删除失败时抛出
        """
        try:
            await self._storage.delete_conversation(conversation_id)
        except Exception as e:
            raise MemoryError(f"删除对话失败: {e}") from e
    
    async def list_conversations(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        列出对话列表
        
        参数:
            limit: 返回数量限制
            offset: 偏移量
        
        返回:
            对话列表，每个元素包含conversation_id和metadata
        
        异常:
            MemoryError: 查询失败时抛出
        """
        try:
            return await self._storage.list_conversations(limit=limit, offset=offset)
        except Exception as e:
            raise MemoryError(f"列出对话失败: {e}") from e
