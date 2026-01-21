"""
模块名称：工具系统模块
功能描述：提供工具定义、注册和管理功能，支持Function Calling
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - Tool: 工具定义类
    - ToolRegistry: 工具注册表
    - ToolError: 工具错误异常

依赖模块：
    - typing: 类型注解
    - json: JSON Schema验证
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, Awaitable
from dataclasses import dataclass


class ToolError(Exception):
    """工具模块异常基类"""
    pass


@dataclass
class Tool:
    """
    工具定义
    
    表示一个可被Agent调用的工具，包含名称、描述、参数schema和执行函数。
    
    特性：
        - 支持Function Calling格式的schema
        - 异步执行函数
        - 参数验证
    
    示例：
        >>> async def get_weather(city: str) -> str:
        ...     return f"{city}的天气是晴天"
        >>> tool = Tool(
        ...     name="get_weather",
        ...     description="获取城市天气",
        ...     parameters={
        ...         "type": "object",
        ...         "properties": {
        ...             "city": {"type": "string", "description": "城市名称"}
        ...         },
        ...         "required": ["city"]
        ...     },
        ...     func=get_weather
        ... )
    """
    
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema格式
    func: Callable[..., Awaitable[Any]]
    
    def __post_init__(self) -> None:
        """验证工具定义"""
        if not self.name:
            raise ToolError("工具名称不能为空")
        if not self.description:
            raise ToolError("工具描述不能为空")
        if not isinstance(self.parameters, dict):
            raise ToolError("工具参数必须是字典格式（JSON Schema）")
        if not callable(self.func):
            raise ToolError("工具执行函数必须是可调用对象")
    
    def to_function_schema(self) -> Dict[str, Any]:
        """
        转换为Function Calling格式的schema
        
        返回:
            符合OpenAI Function Calling格式的工具定义
        
        示例:
            >>> schema = tool.to_function_schema()
            >>> # 返回: {"name": "get_weather", "description": "...", "parameters": {...}}
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        """
        执行工具
        
        参数:
            arguments: 工具参数（字典格式）
        
        返回:
            工具执行结果
        
        异常:
            ToolError: 执行失败时抛出
        
        示例:
            >>> result = await tool.execute({"city": "北京"})
        """
        try:
            # 调用异步函数
            if arguments:
                result = await self.func(**arguments)
            else:
                result = await self.func()
            return result
        except Exception as e:
            raise ToolError(f"工具执行失败: {e}") from e


class ToolRegistry:
    """
    工具注册表
    
    管理所有可用工具的注册、查找和执行。
    
    特性：
        - 工具注册和管理
        - 工具查找
        - 工具执行
        - 防止重复注册（默认）
    
    示例：
        >>> registry = ToolRegistry()
        >>> registry.register(tool)
        >>> tool = registry.get("get_weather")
        >>> result = await registry.execute("get_weather", {"city": "北京"})
    """
    
    def __init__(self, allow_override: bool = False) -> None:
        """
        初始化工具注册表
        
        参数:
            allow_override: 是否允许覆盖已存在的工具（默认False）
        """
        self._tools: Dict[str, Tool] = {}
        self._allow_override: bool = allow_override
    
    def register(self, tool: Tool) -> None:
        """
        注册工具
        
        参数:
            tool: 工具实例
        
        异常:
            ToolError: 工具已存在且不允许覆盖时抛出
        
        示例:
            >>> registry.register(tool)
        """
        if tool.name in self._tools and not self._allow_override:
            raise ToolError(f"工具已存在: {tool.name}，如需覆盖请设置 allow_override=True")
        
        self._tools[tool.name] = tool
    
    def unregister(self, name: str) -> None:
        """
        注销工具
        
        参数:
            name: 工具名称
        
        异常:
            ToolError: 工具不存在时抛出
        """
        if name not in self._tools:
            raise ToolError(f"工具不存在: {name}")
        
        del self._tools[name]
    
    def get(self, name: str) -> Optional[Tool]:
        """
        获取工具
        
        参数:
            name: 工具名称
        
        返回:
            工具实例，如果不存在返回None
        """
        return self._tools.get(name)
    
    def has(self, name: str) -> bool:
        """
        检查工具是否存在
        
        参数:
            name: 工具名称
        
        返回:
            True表示存在，False表示不存在
        """
        return name in self._tools
    
    def list_tools(self) -> List[str]:
        """
        列出所有工具名称
        
        返回:
            工具名称列表
        """
        return list(self._tools.keys())
    
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """
        获取所有工具的Function Calling schema列表
        
        返回:
            工具schema列表，用于传递给LLM
        
        示例:
            >>> schemas = registry.get_function_schemas()
            >>> # 传递给LLM: functions=schemas
        """
        return [tool.to_function_schema() for tool in self._tools.values()]
    
    async def execute(
        self,
        name: str,
        arguments: Dict[str, Any],
    ) -> Any:
        """
        执行工具
        
        参数:
            name: 工具名称
            arguments: 工具参数（字典格式）
        
        返回:
            工具执行结果
        
        异常:
            ToolError: 工具不存在或执行失败时抛出
        """
        tool = self.get(name)
        if tool is None:
            raise ToolError(f"工具不存在: {name}")
        
        return await tool.execute(arguments)
    
    def clear(self) -> None:
        """清空所有工具"""
        self._tools.clear()
