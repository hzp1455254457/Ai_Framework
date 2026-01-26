"""
模块名称：LLM提供者工厂
功能描述：提供LLM提供者的工厂方法，支持创建不同实现（native/litellm/langchain）
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - LLMFactory: LLM提供者工厂
    - NativeLLMProvider: 自研LLM提供者实现

依赖模块：
    - core.interfaces.llm: LLM提供者接口
    - core.llm.service: LLM服务
"""

from typing import Dict, Any, Optional
from core.interfaces.llm import ILLMProvider

# Native实现
from core.implementations.native.native_llm import NativeLLMProvider

# LangChain实现（可选）
try:
    from core.implementations.langchain.langchain_llm import LangChainLLMProvider
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LangChainLLMProvider = None

# LiteLLM实现（可选）
try:
    from core.implementations.litellm.litellm_llm import LiteLLMLLMProvider
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    LiteLLMLLMProvider = None


class LLMFactory:
    """
    LLM提供者工厂
    
    负责创建不同实现的LLM提供者实例。
    支持native（自研）、litellm、langchain三种实现。
    
    示例：
        >>> factory = LLMFactory()
        >>> provider = factory.create("native", config)
        >>> await provider.initialize()
    """
    
    @staticmethod
    def create(
        implementation: str,
        config: Dict[str, Any]
    ) -> ILLMProvider:
        """
        创建LLM提供者
        
        参数:
            implementation: 实现类型（native/litellm/langchain）
            config: 配置字典
        
        返回:
            LLM提供者实例（实现ILLMProvider接口）
        
        异常:
            ValueError: 实现类型不支持时抛出
            RuntimeError: 实现依赖不可用时抛出
        
        示例:
            >>> provider = LLMFactory.create("native", config)
        """
        if implementation == "native":
            return NativeLLMProvider(config)
        elif implementation == "litellm":
            if not LITELLM_AVAILABLE:
                raise RuntimeError("LiteLLM未安装，请运行: pip install litellm")
            return LiteLLMLLMProvider(config)
        elif implementation == "langchain":
            if not LANGCHAIN_AVAILABLE:
                raise RuntimeError("LangChain未安装，请运行: pip install langchain")
            return LangChainLLMProvider(config)
        else:
            raise ValueError(f"不支持的实现类型: {implementation}，支持的类型：native, litellm, langchain")
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> ILLMProvider:
        """
        从配置创建LLM提供者（自动选择实现）
        
        参数:
            config: 配置字典，应包含 `llm.implementation` 配置项
        
        返回:
            LLM提供者实例
        
        示例:
            >>> provider = LLMFactory.create_from_config(config)
        """
        llm_config = config.get("llm", {})
        implementation = llm_config.get("implementation", "native")
        return LLMFactory.create(implementation, config)


# NativeLLMProvider已移到core/implementations/native/native_llm.py
