"""
模块名称：记忆管理器工厂
功能描述：提供记忆管理器的工厂方法，支持创建不同实现（native/langchain）
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - MemoryFactory: 记忆管理器工厂
    - NativeMemory: 自研记忆管理器实现

依赖模块：
    - core.interfaces.memory: 记忆管理接口
    - core.agent.memory: 记忆管理
"""

from typing import Dict, Any, Optional, List
from core.interfaces.memory import IMemory

# Native实现
from core.implementations.native.native_memory import NativeMemory

# LangChain实现（可选）
try:
    from core.implementations.langchain.langchain_memory import LangChainMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LangChainMemory = None


class MemoryFactory:
    """
    记忆管理器工厂
    
    负责创建不同实现的记忆管理器实例。
    支持native（自研）、langchain两种实现。
    
    示例：
        >>> factory = MemoryFactory()
        >>> memory = factory.create("native", config, storage_manager)
    """
    
    @staticmethod
    def create(
        implementation: str,
        config: Dict[str, Any],
        storage_manager: Optional[Any] = None
    ) -> IMemory:
        """
        创建记忆管理器
        
        参数:
            implementation: 实现类型（native/langchain）
            config: 配置字典
            storage_manager: 存储管理器（可选，用于长期记忆）
        
        返回:
            记忆管理器实例（实现IMemory接口）
        
        异常:
            ValueError: 实现类型不支持时抛出
            RuntimeError: 实现依赖不可用时抛出
        
        示例:
            >>> memory = MemoryFactory.create("native", config, storage_manager)
        """
        if implementation == "native":
            return NativeMemory(config, storage_manager)
        elif implementation == "langchain":
            if not LANGCHAIN_AVAILABLE:
                raise RuntimeError("LangChain未安装，请运行: pip install langchain")
            return LangChainMemory(config)
        else:
            raise ValueError(f"不支持的实现类型: {implementation}，支持的类型：native, langchain")
    
    @staticmethod
    def create_from_config(config: Dict[str, Any], storage_manager: Optional[Any] = None) -> IMemory:
        """
        从配置创建记忆管理器（自动选择实现）
        
        参数:
            config: 配置字典，应包含 `memory.implementation` 配置项
            storage_manager: 存储管理器（可选）
        
        返回:
            记忆管理器实例
        
        示例:
            >>> memory = MemoryFactory.create_from_config(config, storage_manager)
        """
        memory_config = config.get("memory", {})
        implementation = memory_config.get("implementation", "native")
        return MemoryFactory.create(implementation, config, storage_manager)


# NativeMemory已移到core/implementations/native/native_memory.py
