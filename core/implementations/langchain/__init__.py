"""
模块名称：LangChain实现模块
功能描述：导出所有LangChain实现
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队
"""

# LangChain实现（可选依赖）
try:
    from core.implementations.langchain.langchain_llm import (
        LangChainLLMWrapper,
        LangChainLLMProvider
    )
    from core.implementations.langchain.langchain_agent import LangChainAgentEngine
    from core.implementations.langchain.langchain_tools import LangChainToolManager
    from core.implementations.langchain.langchain_memory import LangChainMemory
    LANGCHAIN_AVAILABLE = True
    __all__ = [
        "LangChainLLMWrapper",
        "LangChainLLMProvider",
        "LangChainAgentEngine",
        "LangChainToolManager",
        "LangChainMemory",
    ]
except ImportError:
    LANGCHAIN_AVAILABLE = False
    __all__ = []
