"""
模块名称：LangChain记忆管理器实现
功能描述：使用LangChain Memory实现IMemory接口
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - LangChainMemory: LangChain记忆管理器实现

依赖模块：
    - core.interfaces.memory: 记忆管理接口
    - langchain: LangChain框架（可选）
"""

from typing import Dict, Any, Optional, List

try:
    # LangChain 1.2+ 将memory移到langchain_classic
    try:
        from langchain_classic.memory import ConversationBufferMemory, ConversationSummaryMemory
        from langchain_classic.schema import HumanMessage, AIMessage, BaseMessage
    except ImportError:
        # 兼容旧版本
        from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
        from langchain.schema import HumanMessage, AIMessage, BaseMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ConversationBufferMemory = None
    ConversationSummaryMemory = None
    HumanMessage = None
    AIMessage = None
    BaseMessage = None

from core.interfaces.memory import IMemory


class LangChainMemory(IMemory):
    """
    LangChain记忆管理器实现
    
    使用LangChain Memory实现IMemory接口。
    支持LangChain的各种记忆类型。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化LangChain记忆管理器
        
        参数:
            config: 配置字典
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain未安装，请运行: pip install langchain")
        
        self._config = config
        memory_config = config.get("memory", {})
        memory_type = memory_config.get("type", "buffer")
        
        # 创建LangChain Memory实例
        if memory_type == "buffer":
            self._memory = ConversationBufferMemory()
        elif memory_type == "summary":
            # TODO: 需要LLM用于摘要
            self._memory = ConversationBufferMemory()
        else:
            self._memory = ConversationBufferMemory()
    
    def add_message(self, role: str, content: str, **kwargs: Any) -> None:
        """
        添加消息
        
        参数:
            role: 消息角色（user/assistant/system/tool）
            content: 消息内容
            **kwargs: 其他消息字段（如tool_call_id）
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain未安装")
        
        if role == "user":
            self._memory.chat_memory.add_user_message(content)
        elif role == "assistant":
            self._memory.chat_memory.add_ai_message(content)
        elif role == "tool":
            # LangChain的tool消息处理
            # 注意：LangChain的ToolMessage需要与AIMessage配合使用
            # 这里简化处理，直接添加为AI消息（包含工具调用结果）
            tool_call_id = kwargs.get("tool_call_id")
            if tool_call_id:
                # 如果有tool_call_id，创建包含工具调用的消息
                # 注意：这需要LangChain的特定版本支持
                # 简化实现：将工具结果作为AI消息的一部分
                tool_content = f"[Tool Call ID: {tool_call_id}] {content}"
                self._memory.chat_memory.add_ai_message(tool_content)
            else:
                # 没有tool_call_id，直接添加为AI消息
                self._memory.chat_memory.add_ai_message(content)
        elif role == "system":
            # LangChain的system消息处理
            # 注意：某些LangChain Memory类型可能不支持system消息
            # 这里将其作为user消息处理
            self._memory.chat_memory.add_user_message(f"[System] {content}")
        else:
            raise ValueError(f"不支持的消息角色: {role}")
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """
        获取消息列表
        
        返回:
            消息列表，每个消息包含role和content
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain未安装")
        
        messages = self._memory.chat_memory.messages
        result = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                # 检查是否是system消息（我们之前添加的标记）
                content = msg.content
                if content.startswith("[System] "):
                    result.append({
                        "role": "system",
                        "content": content[9:]  # 移除"[System] "前缀
                    })
                else:
                    result.append({
                        "role": "user",
                        "content": content
                    })
            elif isinstance(msg, AIMessage):
                # 检查是否是tool消息（我们之前添加的标记）
                content = msg.content
                if content.startswith("[Tool Call ID: "):
                    # 提取tool_call_id
                    end_idx = content.index("] ")
                    tool_call_id = content[15:end_idx]
                    tool_content = content[end_idx + 2:]
                    result.append({
                        "role": "tool",
                        "content": tool_content,
                        "tool_call_id": tool_call_id
                    })
                else:
                    result.append({
                        "role": "assistant",
                        "content": content
                    })
            else:
                # 其他类型的消息，尝试获取基本信息
                result.append({
                    "role": getattr(msg, "type", "unknown"),
                    "content": getattr(msg, "content", str(msg))
                })
        
        return result
    
    def clear(self) -> None:
        """清空记忆"""
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain未安装")
        
        # 清空LangChain Memory
        self._memory.clear()
    
    async def save(self, conversation_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        保存记忆（长期）
        
        参数:
            conversation_id: 对话ID
            metadata: 元数据（可选）
        """
        # TODO: 实现LangChain Memory长期保存
        # 需要使用LangChain的持久化功能
        pass
    
    async def load(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        加载记忆（长期）
        
        参数:
            conversation_id: 对话ID
        
        返回:
            消息列表，如果不存在返回None
        """
        # TODO: 实现LangChain Memory长期加载
        # 需要使用LangChain的持久化功能
        return None
    
    @property
    def message_count(self) -> int:
        """
        消息数量
        
        返回:
            当前消息数量
        """
        if not LANGCHAIN_AVAILABLE:
            return 0
        
        return len(self._memory.chat_memory.messages)
