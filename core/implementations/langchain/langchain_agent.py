"""
模块名称：LangChain Agent引擎实现
功能描述：使用LangChain Agent实现IAgentEngine接口
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - LangChainAgentEngine: LangChain Agent引擎实现

依赖模块：
    - core.interfaces.agent: Agent引擎接口
    - core.interfaces.llm: LLM提供者接口
    - core.interfaces.tools: 工具管理器接口
    - core.interfaces.memory: 记忆管理接口
    - langchain: LangChain框架（可选）
"""

from typing import Dict, Any, Optional, List
import json

try:
    # LangChain 1.2+ 将旧API移到 langchain_classic
    try:
        from langchain_classic.agents import AgentExecutor, initialize_agent, AgentType
    except ImportError:
        # 兼容旧版本
        from langchain.agents import AgentExecutor, initialize_agent, AgentType
    
    try:
        from langchain.tools import BaseTool
    except ImportError:
        from langchain_core.tools import BaseTool
    
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    AgentExecutor = None
    initialize_agent = None
    AgentType = None
    BaseTool = None

from core.interfaces.agent import IAgentEngine
from core.interfaces.llm import ILLMProvider
from core.interfaces.tools import IToolManager
from core.interfaces.memory import IMemory
from core.implementations.langchain.langchain_llm import LangChainLLMWrapper
from core.implementations.langchain.langchain_tools import LangChainToolManager
from core.implementations.langchain.langchain_memory import LangChainMemory


class LangChainAgentEngine(IAgentEngine):
    """
    LangChain Agent引擎实现
    
    使用LangChain Agent实现IAgentEngine接口。
    支持LangChain的所有Agent类型和工具。
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        llm_provider: ILLMProvider,
        tool_manager: IToolManager,
        memory: IMemory
    ):
        """
        初始化LangChain Agent引擎
        
        参数:
            config: 配置字典
            llm_provider: LLM提供者
            tool_manager: 工具管理器
            memory: 记忆管理器
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain未安装，请运行: pip install langchain")
        
        self._config = config
        self._llm_provider = llm_provider
        self._tool_manager = tool_manager
        self._memory = memory
        self._agent_executor: Optional[Any] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化Agent引擎"""
        if self._initialized:
            return
        
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain未安装，请运行: pip install langchain")
        
        # 初始化LLM提供者
        if not hasattr(self._llm_provider, '_initialized') or not self._llm_provider._initialized:
            await self._llm_provider.initialize()
        
        # 1. 将LLMProvider转换为LangChain LLM
        langchain_llm = LangChainLLMWrapper(self._llm_provider)
        
        # 2. 将IToolManager转换为LangChain Tools
        langchain_tools = []
        tool_names = self._tool_manager.list_tools()
        
        for tool_name in tool_names:
            # 如果工具管理器是LangChainToolManager，直接获取工具
            if isinstance(self._tool_manager, LangChainToolManager):
                if tool_name in self._tool_manager._tools:
                    langchain_tools.append(self._tool_manager._tools[tool_name])
            else:
                # 否则，需要从工具管理器获取schema并创建LangChain Tool
                try:
                    tool_schema = self._tool_manager.get_tool_schema(tool_name)
                    try:
                        from langchain_core.tools import StructuredTool as Tool
                    except ImportError:
                        # 兼容旧版本
                        from langchain.tools import Tool
                    
                    # 创建工具函数（使用闭包捕获tool_name）
                    def create_tool_func(name: str):
                        async def tool_func(**kwargs):
                            result = await self._tool_manager.execute(name, kwargs)
                            return str(result)
                        return tool_func
                    
                    tool_func = create_tool_func(tool_name)
                    langchain_tool = Tool(
                        name=tool_name,
                        description=tool_schema.get("description", ""),
                        func=tool_func,
                    )
                    langchain_tools.append(langchain_tool)
                except Exception as e:
                    # 如果转换失败，跳过该工具
                    continue
        
        # 3. 将IMemory转换为LangChain Memory
        langchain_memory = None
        if isinstance(self._memory, LangChainMemory):
            langchain_memory = self._memory._memory
        else:
            # 如果是自研记忆，需要转换
            # 注意：这里简化处理，创建一个新的LangChain Memory并导入现有消息
            try:
                from langchain_classic.memory import ConversationBufferMemory
            except ImportError:
                # 兼容旧版本
                from langchain.memory import ConversationBufferMemory
            langchain_memory = ConversationBufferMemory()
            # 导入现有消息
            existing_messages = self._memory.get_messages()
            for msg in existing_messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    langchain_memory.chat_memory.add_user_message(content)
                elif role == "assistant":
                    langchain_memory.chat_memory.add_ai_message(content)
        
        # 4. 创建AgentExecutor
        agent_config = self._config.get("agent", {})
        agent_type_str = agent_config.get("agent_type", "openai-functions")
        
        # 映射Agent类型
        agent_type_map = {
            "openai-functions": AgentType.OPENAI_FUNCTIONS,
            "openai-multi-functions": AgentType.OPENAI_MULTI_FUNCTIONS,
            "react": AgentType.REACT_DOCSTORE,
            "self-ask-with-search": AgentType.SELF_ASK_WITH_SEARCH,
        }
        
        agent_type = agent_type_map.get(agent_type_str, AgentType.OPENAI_FUNCTIONS)
        
        self._agent_executor = initialize_agent(
            tools=langchain_tools,
            llm=langchain_llm,
            agent=agent_type,
            memory=langchain_memory,
            verbose=agent_config.get("verbose", False),
            max_iterations=agent_config.get("max_iterations", 10),
            return_intermediate_steps=agent_config.get("return_intermediate_steps", True),
        )
        
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
            conversation_id: 对话ID（可选，用于长期记忆）
            **kwargs: 其他参数
        
        返回:
            执行结果字典，包含：
                - content: 最终输出内容
                - tool_calls: 工具调用记录
                - iterations: 迭代次数
                - metadata: 其他元数据
        """
        if not self._initialized:
            raise RuntimeError("Agent引擎未初始化")
        
        if not self._agent_executor:
            raise RuntimeError("AgentExecutor未创建")
        
        # 加载长期记忆（如果启用且有conversation_id）
        if conversation_id and hasattr(self._memory, "load"):
            try:
                saved_messages = await self._memory.load(conversation_id)
                if saved_messages:
                    # 恢复消息到记忆
                    for msg in saved_messages:
                        self._memory.add_message(
                            msg.get("role", "user"),
                            msg.get("content", "")
                        )
            except Exception:
                # 如果加载失败，继续执行
                pass
        
        # 执行Agent
        try:
            result = await self._agent_executor.ainvoke({"input": task})
        except Exception as e:
            raise RuntimeError(f"Agent执行失败: {e}") from e
        
        # 提取工具调用信息
        tool_calls = []
        intermediate_steps = result.get("intermediate_steps", [])
        
        for step in intermediate_steps:
            # step格式: (AgentAction, observation)
            if len(step) >= 2:
                action = step[0]
                observation = step[1]
                
                tool_calls.append({
                    "tool": getattr(action, "tool", ""),
                    "input": getattr(action, "tool_input", {}),
                    "output": str(observation) if observation else ""
                })
        
        # 保存长期记忆（如果启用且有conversation_id）
        if conversation_id and hasattr(self._memory, "save"):
            try:
                await self._memory.save(conversation_id)
            except Exception:
                # 如果保存失败，继续执行
                pass
        
        # 转换为标准格式
        return {
            "content": result.get("output", ""),
            "tool_calls": tool_calls,
            "iterations": len(intermediate_steps),
            "metadata": {
                "agent_type": self._config.get("agent", {}).get("agent_type", "openai-functions"),
                "langchain_result": result
            }
        }
    
    def register_tool(self, tool: Any) -> None:
        """
        注册工具
        
        参数:
            tool: 工具实例
        """
        # 注册到工具管理器
        self._tool_manager.register(tool)
        
        # 如果Agent已初始化，需要重新创建AgentExecutor
        if self._initialized:
            # 重新初始化以包含新工具
            # 注意：这里简化处理，实际应该更优雅地处理工具更新
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果事件循环正在运行，创建任务
                    loop.create_task(self.initialize())
                else:
                    loop.run_until_complete(self.initialize())
            except RuntimeError:
                # 如果没有事件循环，创建新的
                asyncio.run(self.initialize())
    
    def get_tools(self) -> List[str]:
        """
        获取工具列表
        
        返回:
            工具名称列表
        """
        return self._tool_manager.list_tools()
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        获取所有工具的Function Calling schema列表
        
        返回:
            工具schema列表
        """
        return self._tool_manager.get_tool_schemas()
    
    def clear_memory(self) -> None:
        """清空记忆"""
        self._memory.clear()
    
    async def cleanup(self) -> None:
        """清理资源"""
        if self._llm_provider:
            await self._llm_provider.cleanup()
        self._initialized = False
