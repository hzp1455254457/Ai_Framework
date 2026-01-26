"""
模块名称：Agent引擎工厂
功能描述：提供Agent引擎的工厂方法，支持创建不同实现（native/langchain/langgraph）
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - AgentFactory: Agent引擎工厂

依赖模块：
    - core.interfaces.agent: Agent引擎接口
    - core.interfaces.llm: LLM提供者接口
    - core.interfaces.tools: 工具管理器接口
    - core.interfaces.memory: 记忆管理接口
    - core.agent.engine: Agent引擎
"""

from typing import Dict, Any, Optional, List
from core.interfaces.agent import IAgentEngine
from core.interfaces.llm import ILLMProvider
from core.interfaces.tools import IToolManager
from core.interfaces.memory import IMemory

# Native实现
from core.implementations.native.native_agent import NativeAgentEngine

# LangChain实现（可选）
try:
    from core.implementations.langchain.langchain_agent import LangChainAgentEngine
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LangChainAgentEngine = None

# LangGraph实现（可选）
try:
    from core.implementations.langgraph.langgraph_agent import LangGraphAgentEngine
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    LangGraphAgentEngine = None

# 导入工厂（避免循环导入）
from core.factories.llm_factory import LLMFactory
from core.factories.tool_factory import ToolFactory
from core.factories.memory_factory import MemoryFactory


class AgentFactory:
    """
    Agent引擎工厂
    
    负责创建不同实现的Agent引擎实例。
    支持native（自研）、langchain、langgraph三种实现。
    支持依赖注入（LLM提供者、工具管理器、记忆管理器）。
    
    示例：
        >>> factory = AgentFactory()
        >>> engine = factory.create("native", config, llm_provider, tool_manager, memory)
        >>> await engine.initialize()
    """
    
    @staticmethod
    def create(
        implementation: str,
        config: Dict[str, Any],
        llm_provider: Optional[ILLMProvider] = None,
        tool_manager: Optional[IToolManager] = None,
        memory: Optional[IMemory] = None
    ) -> IAgentEngine:
        """
        创建Agent引擎
        
        参数:
            implementation: 实现类型（native/langchain/langgraph）
            config: 配置字典
            llm_provider: LLM提供者（可选，如果未提供则从配置创建）
            tool_manager: 工具管理器（可选，如果未提供则从配置创建）
            memory: 记忆管理器（可选，如果未提供则从配置创建）
        
        返回:
            Agent引擎实例（实现IAgentEngine接口）
        
        异常:
            ValueError: 实现类型不支持时抛出
            RuntimeError: 实现依赖不可用时抛出
        
        示例:
            >>> engine = AgentFactory.create("native", config, llm_provider, tool_manager, memory)
        """
        # 如果没有提供依赖，从配置创建
        if llm_provider is None:
            llm_provider = LLMFactory.create_from_config(config)
        
        if tool_manager is None:
            tool_manager = ToolFactory.create_from_config(config)
        
        if memory is None:
            # 获取存储管理器（如果配置了长期记忆）
            storage_manager = None
            if config.get("memory", {}).get("enable_long_term", False):
                from infrastructure.storage import StorageManager
                storage_config = config.get("storage", {})
                storage_manager = StorageManager(storage_config)
            
            memory = MemoryFactory.create_from_config(config, storage_manager)
        
        if implementation == "native":
            return NativeAgentEngine(config, llm_provider, tool_manager, memory)
        elif implementation == "langchain":
            if not LANGCHAIN_AVAILABLE:
                raise RuntimeError("LangChain未安装，请运行: pip install langchain")
            return LangChainAgentEngine(config, llm_provider, tool_manager, memory)
        elif implementation == "langgraph":
            if not LANGGRAPH_AVAILABLE:
                raise RuntimeError("LangGraph未安装，请运行: pip install langgraph")
            return LangGraphAgentEngine(config, llm_provider, tool_manager, memory)
        else:
            raise ValueError(f"不支持的实现类型: {implementation}，支持的类型：native, langchain, langgraph")
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> IAgentEngine:
        """
        从配置创建Agent引擎（自动选择实现）
        
        参数:
            config: 配置字典，应包含 `agent.implementation` 配置项
        
        返回:
            Agent引擎实例
        
        示例:
            >>> engine = AgentFactory.create_from_config(config)
        """
        agent_config = config.get("agent", {})
        implementation = agent_config.get("implementation", "native")
        return AgentFactory.create(implementation, config)


# NativeAgentEngine已移到core/implementations/native/native_agent.py
