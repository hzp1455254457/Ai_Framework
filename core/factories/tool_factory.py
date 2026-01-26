"""
模块名称：工具管理器工厂
功能描述：提供工具管理器的工厂方法，支持创建不同实现（native/langchain）
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - ToolFactory: 工具管理器工厂
    - NativeToolManager: 自研工具管理器实现

依赖模块：
    - core.interfaces.tools: 工具管理器接口
    - core.agent.tools: 工具系统
"""

from typing import Dict, Any, List
from core.interfaces.tools import IToolManager

# Native实现
from core.implementations.native.native_tools import NativeToolManager

# LangChain实现（可选）
try:
    from core.implementations.langchain.langchain_tools import LangChainToolManager
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LangChainToolManager = None


class ToolFactory:
    """
    工具管理器工厂
    
    负责创建不同实现的工具管理器实例。
    支持native（自研）、langchain两种实现。
    
    示例：
        >>> factory = ToolFactory()
        >>> manager = factory.create("native", config)
    """
    
    @staticmethod
    def create(implementation: str, config: Dict[str, Any]) -> IToolManager:
        """
        创建工具管理器
        
        参数:
            implementation: 实现类型（native/langchain）
            config: 配置字典
        
        返回:
            工具管理器实例（实现IToolManager接口）
        
        异常:
            ValueError: 实现类型不支持时抛出
            RuntimeError: 实现依赖不可用时抛出
        
        示例:
            >>> manager = ToolFactory.create("native", config)
        """
        if implementation == "native":
            return NativeToolManager(config)
        elif implementation == "langchain":
            if not LANGCHAIN_AVAILABLE:
                raise RuntimeError("LangChain未安装，请运行: pip install langchain")
            return LangChainToolManager(config)
        else:
            raise ValueError(f"不支持的实现类型: {implementation}，支持的类型：native, langchain")
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> IToolManager:
        """
        从配置创建工具管理器（自动选择实现）
        
        参数:
            config: 配置字典，应包含 `tools.implementation` 配置项
        
        返回:
            工具管理器实例
        
        示例:
            >>> manager = ToolFactory.create_from_config(config)
        """
        tool_config = config.get("tools", {})
        implementation = tool_config.get("implementation", "native")
        return ToolFactory.create(implementation, config)


# NativeToolManager已移到core/implementations/native/native_tools.py
