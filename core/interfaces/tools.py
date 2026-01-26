"""
模块名称：工具管理器抽象接口
功能描述：定义工具管理器的抽象接口，支持多种实现（自研、LangChain）
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - IToolManager: 工具管理器抽象接口

依赖模块：
    - abc: 抽象基类
    - typing: 类型注解
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class IToolManager(ABC):
    """
    工具管理器抽象接口
    
    定义统一的工具管理器接口规范，支持多种实现（自研、LangChain）。
    所有工具管理器实现都必须实现此接口。
    
    特性：
        - 工具注册
        - 工具执行
        - 工具查询
        - Schema生成
    
    示例：
        >>> manager = NativeToolManager(config)
        >>> manager.register(tool)
        >>> result = await manager.execute("get_weather", {"city": "北京"})
    """
    
    @abstractmethod
    def register(self, tool: Any) -> None:
        """
        注册工具
        
        将工具注册到管理器，使其可以被调用。
        
        参数:
            tool: 工具实例（可以是自研Tool或LangChain Tool等）
        
        异常:
            ValueError: 工具无效或已存在时抛出
        
        示例:
            >>> from core.agent.tools import Tool
            >>> tool = Tool(name="get_weather", ...)
            >>> manager.register(tool)
        """
        pass
    
    @abstractmethod
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        执行工具
        
        根据工具名称和参数执行工具。
        
        参数:
            tool_name: 工具名称
            arguments: 工具参数（字典格式）
        
        返回:
            工具执行结果
        
        异常:
            ValueError: 工具不存在时抛出
            RuntimeError: 工具执行失败时抛出
        
        示例:
            >>> result = await manager.execute("get_weather", {"city": "北京"})
            >>> print(result)
        """
        pass
    
    @abstractmethod
    def list_tools(self) -> List[str]:
        """
        列出所有工具
        
        返回:
            已注册的工具名称列表
        
        示例:
            >>> tools = manager.list_tools()
            >>> print(tools)
            ['get_weather', 'web_search', 'fetch_webpage']
        """
        pass
    
    @abstractmethod
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """
        获取工具schema
        
        获取指定工具的Function Calling格式的schema。
        
        参数:
            tool_name: 工具名称
        
        返回:
            工具schema字典，包含name、description、parameters等
        
        异常:
            ValueError: 工具不存在时抛出
        
        示例:
            >>> schema = manager.get_tool_schema("get_weather")
            >>> print(schema)
            {'name': 'get_weather', 'description': '...', 'parameters': {...}}
        """
        pass
    
    @abstractmethod
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        获取所有工具schema
        
        返回:
            所有工具的schema列表
        
        示例:
            >>> schemas = manager.get_all_schemas()
            >>> print(len(schemas))
            3
        """
        pass
