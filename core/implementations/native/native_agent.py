"""
模块名称：自研Agent引擎实现
功能描述：包装现有AgentEngine为IAgentEngine接口
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - NativeAgentEngine: 自研Agent引擎实现

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
from core.agent.engine import AgentEngine


class NativeAgentEngine(IAgentEngine):
    """
    自研Agent引擎实现
    
    包装现有AgentEngine为IAgentEngine接口。
    需要适配接口到现有实现的差异。
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        llm_provider: ILLMProvider,
        tool_manager: IToolManager,
        memory: IMemory
    ):
        """
        初始化自研Agent引擎
        
        参数:
            config: 配置字典
            llm_provider: LLM提供者
            tool_manager: 工具管理器
            memory: 记忆管理器
        """
        self._config = config
        self._llm_provider = llm_provider
        self._tool_manager = tool_manager
        self._memory = memory
        self._engine: Optional[AgentEngine] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化Agent引擎"""
        if self._initialized:
            return
        
        # 初始化LLM提供者
        if not hasattr(self._llm_provider, '_initialized') or not self._llm_provider._initialized:
            await self._llm_provider.initialize()
        
        # 创建AgentEngine实例（使用现有实现）
        # 注意：这里需要将接口适配到现有AgentEngine
        # 由于AgentEngine需要LLMService，我们需要从LLMProvider中获取
        # 暂时使用配置创建AgentEngine，后续可以通过适配器模式优化
        self._engine = AgentEngine(self._config)
        await self._engine.initialize()
        
        # 将工具管理器中的工具注册到AgentEngine
        # 注意：这里需要访问ToolRegistry的内部实现
        if hasattr(self._tool_manager, '_registry'):
            registry = self._tool_manager._registry
            for tool_name in self._tool_manager.list_tools():
                tool = registry.get_tool(tool_name)
                if tool:
                    self._engine.register_tool(tool)
        
        self._initialized = True
    
    async def run_task(
        self,
        task: str,
        conversation_id: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        执行任务
        
        参数:
            task: 任务描述
            conversation_id: 对话ID（可选）
            **kwargs: 其他参数
        
        返回:
            执行结果字典
        """
        if not self._initialized or not self._engine:
            raise RuntimeError("Agent引擎未初始化")
        
        return await self._engine.run_task(task, conversation_id, **kwargs)
    
    def register_tool(self, tool: Any) -> None:
        """
        注册工具
        
        参数:
            tool: 工具实例
        """
        if self._engine:
            self._engine.register_tool(tool)
        # 同时注册到工具管理器
        self._tool_manager.register(tool)
    
    def get_tools(self) -> List[str]:
        """
        获取工具列表
        
        返回:
            工具名称列表
        """
        if self._engine:
            return self._engine.get_tools()
        return self._tool_manager.list_tools()
    
    def clear_memory(self) -> None:
        """清空记忆"""
        if self._engine:
            self._engine.clear_memory()
        self._memory.clear()
    
    async def cleanup(self) -> None:
        """清理资源"""
        if self._engine:
            await self._engine.cleanup()
        if self._llm_provider:
            await self._llm_provider.cleanup()
        self._initialized = False
