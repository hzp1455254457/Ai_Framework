"""
模块名称：Agent引擎抽象接口
功能描述：定义Agent引擎的抽象接口，支持多种实现（自研、LangChain、LangGraph）
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - IAgentEngine: Agent引擎抽象接口

依赖模块：
    - abc: 抽象基类
    - typing: 类型注解
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class IAgentEngine(ABC):
    """
    Agent引擎抽象接口
    
    定义统一的Agent引擎接口规范，支持多种实现（自研、LangChain、LangGraph）。
    所有Agent引擎实现都必须实现此接口。
    
    特性：
        - 任务执行
        - 工具注册和管理
        - 记忆管理
        - 生命周期管理
    
    示例：
        >>> engine = NativeAgentEngine(config, llm_provider, tool_manager, memory)
        >>> await engine.initialize()
        >>> result = await engine.run_task("查询天气")
    """
    
    @abstractmethod
    async def run_task(
        self,
        task: str,
        conversation_id: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        执行任务
        
        接收任务描述，执行Agent工作流，返回执行结果。
        
        参数:
            task: 任务描述（文本）
            conversation_id: 对话ID（可选，用于长期记忆）
            **kwargs: 其他参数（如temperature、model等）
        
        返回:
            执行结果字典，包含：
                - content: 最终输出内容
                - tool_calls: 工具调用记录（如果有）
                - iterations: 迭代次数
                - metadata: 其他元数据
        
        异常:
            RuntimeError: 引擎未初始化时抛出
            ValueError: 任务为空时抛出
        
        示例:
            >>> result = await engine.run_task("查询北京天气")
            >>> print(result["content"])
        """
        pass
    
    @abstractmethod
    def register_tool(self, tool: Any) -> None:
        """
        注册工具
        
        将工具注册到Agent引擎，使其可以在任务执行中被调用。
        
        参数:
            tool: 工具实例（可以是自研Tool或LangChain Tool等）
        
        异常:
            ValueError: 工具无效时抛出
        
        示例:
            >>> from core.agent.tools import Tool
            >>> tool = Tool(name="get_weather", ...)
            >>> engine.register_tool(tool)
        """
        pass
    
    @abstractmethod
    def get_tools(self) -> List[str]:
        """
        获取工具列表
        
        返回:
            已注册的工具名称列表
        
        示例:
            >>> tools = engine.get_tools()
            >>> print(tools)
            ['get_weather', 'web_search', 'fetch_webpage']
        """
        pass
    
    @abstractmethod
    def clear_memory(self) -> None:
        """
        清空记忆
        
        清空Agent引擎的短期记忆，保留长期记忆。
        
        示例:
            >>> engine.clear_memory()
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        初始化Agent引擎
        
        初始化引擎所需的所有资源。
        
        异常:
            RuntimeError: 初始化失败时抛出
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """
        清理Agent引擎资源
        
        清理引擎占用的所有资源。
        """
        pass
