"""
模块名称：自研工具管理器实现
功能描述：包装现有ToolRegistry为IToolManager接口
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - NativeToolManager: 自研工具管理器实现

依赖模块：
    - core.interfaces.tools: 工具管理器接口
    - core.agent.tools: 工具系统
"""

from typing import Dict, Any, List
from core.interfaces.tools import IToolManager
from core.agent.tools import ToolRegistry, Tool


class NativeToolManager(IToolManager):
    """
    自研工具管理器实现
    
    包装现有ToolRegistry为IToolManager接口。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化自研工具管理器
        
        参数:
            config: 配置字典
        """
        self._config = config
        self._registry = ToolRegistry()
    
    def register(self, tool: Any) -> None:
        """
        注册工具
        
        参数:
            tool: 工具实例（Tool对象）
        """
        # 如果传入的不是Tool对象，尝试转换
        if not isinstance(tool, Tool):
            raise ValueError(f"工具必须是Tool实例，当前类型: {type(tool)}")
        
        self._registry.register(tool)
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        执行工具
        
        参数:
            tool_name: 工具名称
            arguments: 工具参数
        
        返回:
            工具执行结果
        """
        return await self._registry.execute(tool_name, arguments)
    
    def list_tools(self) -> List[str]:
        """
        列出所有工具
        
        返回:
            工具名称列表
        """
        return self._registry.list_tools()
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """
        获取工具schema
        
        参数:
            tool_name: 工具名称
        
        返回:
            工具schema字典
        """
        tool = self._registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"工具不存在: {tool_name}")
        return tool.to_function_schema()
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        获取所有工具schema
        
        返回:
            所有工具的schema列表
        """
        return self._registry.get_function_schemas()
