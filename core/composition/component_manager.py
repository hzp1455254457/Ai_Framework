"""
模块名称：组件管理器
功能描述：统一管理所有组件，支持运行时切换和组件组装
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - ComponentManager: 组件管理器

依赖模块：
    - core.interfaces.llm: LLM提供者接口
    - core.interfaces.agent: Agent引擎接口
    - core.interfaces.tools: 工具管理器接口
    - core.interfaces.memory: 记忆管理接口
    - core.factories: 所有工厂类
"""

from typing import Dict, Any, Optional
from core.interfaces.llm import ILLMProvider
from core.interfaces.agent import IAgentEngine
from core.interfaces.tools import IToolManager
from core.interfaces.memory import IMemory
from core.factories.llm_factory import LLMFactory
from core.factories.agent_factory import AgentFactory
from core.factories.tool_factory import ToolFactory
from core.factories.memory_factory import MemoryFactory


class ComponentManager:
    """
    组件管理器
    
    负责创建和管理所有组件，支持运行时切换实现和组件组装。
    提供统一的组件访问接口。
    
    示例：
        >>> manager = ComponentManager(config)
        >>> await manager.initialize()
        >>> result = await manager.agent_engine.run_task("查询天气")
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化组件管理器
        
        参数:
            config: 配置字典
        """
        self._config = config
        self._llm_provider: Optional[ILLMProvider] = None
        self._tool_manager: Optional[IToolManager] = None
        self._memory: Optional[IMemory] = None
        self._agent_engine: Optional[IAgentEngine] = None
        self._initialized = False
        self._allow_switching = config.get("runtime", {}).get("allow_switching", True)
    
    async def initialize(self) -> None:
        """
        初始化所有组件
        
        根据配置创建所有组件，并自动注入依赖。
        """
        if self._initialized:
            return
        
        # 创建LLM提供者
        self._llm_provider = LLMFactory.create_from_config(self._config)
        await self._llm_provider.initialize()
        
        # 创建工具管理器
        self._tool_manager = ToolFactory.create_from_config(self._config)
        
        # 创建记忆管理器
        storage_manager = None
        if self._config.get("memory", {}).get("enable_long_term", False):
            from infrastructure.storage import StorageManager
            storage_config = self._config.get("storage", {})
            storage_manager = StorageManager(storage_config)
        
        self._memory = MemoryFactory.create_from_config(self._config, storage_manager)
        
        # 创建Agent引擎（注入依赖）
        agent_config = self._config.get("agent", {})
        implementation = agent_config.get("implementation", "native")
        self._agent_engine = AgentFactory.create(
            implementation=implementation,
            config=self._config,
            llm_provider=self._llm_provider,
            tool_manager=self._tool_manager,
            memory=self._memory
        )
        await self._agent_engine.initialize()
        
        self._initialized = True
    
    def switch_llm_implementation(self, implementation: str) -> None:
        """
        切换LLM实现
        
        参数:
            implementation: 实现类型（native/litellm/langchain）
        
        异常:
            RuntimeError: 如果配置不允许切换时抛出
        """
        if not self._allow_switching:
            raise RuntimeError("运行时切换已禁用，请在配置中启用 runtime.allow_switching")
        
        # 清理旧实例
        if self._llm_provider:
            # 注意：这里不等待cleanup，因为可能正在使用
            pass
        
        # 创建新实例
        self._llm_provider = LLMFactory.create(implementation, self._config)
        # 注意：需要重新初始化Agent引擎以使用新的LLM提供者
        # 这里暂时不自动重新初始化，由用户手动调用
    
    def switch_agent_implementation(self, implementation: str) -> None:
        """
        切换Agent实现
        
        参数:
            implementation: 实现类型（native/langchain/langgraph）
        
        异常:
            RuntimeError: 如果配置不允许切换时抛出
        """
        if not self._allow_switching:
            raise RuntimeError("运行时切换已禁用，请在配置中启用 runtime.allow_switching")
        
        # 清理旧实例
        if self._agent_engine:
            # 注意：这里不等待cleanup，因为可能正在使用
            pass
        
        # 创建新实例（使用现有的LLM提供者、工具管理器、记忆管理器）
        self._agent_engine = AgentFactory.create(
            implementation=implementation,
            config=self._config,
            llm_provider=self._llm_provider,
            tool_manager=self._tool_manager,
            memory=self._memory
        )
        # 注意：需要手动调用initialize()
    
    def switch_tool_implementation(self, implementation: str) -> None:
        """
        切换工具实现
        
        参数:
            implementation: 实现类型（native/langchain）
        
        异常:
            RuntimeError: 如果配置不允许切换时抛出
        """
        if not self._allow_switching:
            raise RuntimeError("运行时切换已禁用，请在配置中启用 runtime.allow_switching")
        
        # 创建新实例
        self._tool_manager = ToolFactory.create(implementation, self._config)
        
        # 需要重新创建Agent引擎以使用新的工具管理器
        agent_config = self._config.get("agent", {})
        implementation = agent_config.get("implementation", "native")
        self._agent_engine = AgentFactory.create(
            implementation=implementation,
            config=self._config,
            llm_provider=self._llm_provider,
            tool_manager=self._tool_manager,
            memory=self._memory
        )
        # 注意：需要手动调用initialize()
    
    def switch_memory_implementation(self, implementation: str) -> None:
        """
        切换记忆实现
        
        参数:
            implementation: 实现类型（native/langchain）
        
        异常:
            RuntimeError: 如果配置不允许切换时抛出
        """
        if not self._allow_switching:
            raise RuntimeError("运行时切换已禁用，请在配置中启用 runtime.allow_switching")
        
        # 获取存储管理器（如果配置了长期记忆）
        storage_manager = None
        if self._config.get("memory", {}).get("enable_long_term", False):
            from infrastructure.storage import StorageManager
            storage_config = self._config.get("storage", {})
            storage_manager = StorageManager(storage_config)
        
        # 创建新实例
        self._memory = MemoryFactory.create(implementation, self._config, storage_manager)
        
        # 需要重新创建Agent引擎以使用新的记忆管理器
        agent_config = self._config.get("agent", {})
        implementation = agent_config.get("implementation", "native")
        self._agent_engine = AgentFactory.create(
            implementation=implementation,
            config=self._config,
            llm_provider=self._llm_provider,
            tool_manager=self._tool_manager,
            memory=self._memory
        )
        # 注意：需要手动调用initialize()
    
    @property
    def llm_provider(self) -> ILLMProvider:
        """
        获取LLM提供者
        
        返回:
            LLM提供者实例
        """
        if not self._llm_provider:
            raise RuntimeError("LLM提供者未初始化，请先调用initialize()")
        return self._llm_provider
    
    @property
    def agent_engine(self) -> IAgentEngine:
        """
        获取Agent引擎
        
        返回:
            Agent引擎实例
        """
        if not self._agent_engine:
            raise RuntimeError("Agent引擎未初始化，请先调用initialize()")
        return self._agent_engine
    
    @property
    def tool_manager(self) -> IToolManager:
        """
        获取工具管理器
        
        返回:
            工具管理器实例
        """
        if not self._tool_manager:
            raise RuntimeError("工具管理器未初始化，请先调用initialize()")
        return self._tool_manager
    
    @property
    def memory(self) -> IMemory:
        """
        获取记忆管理器
        
        返回:
            记忆管理器实例
        """
        if not self._memory:
            raise RuntimeError("记忆管理器未初始化，请先调用initialize()")
        return self._memory
