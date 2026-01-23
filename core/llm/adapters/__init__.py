"""
LLM适配器模块

提供各种LLM服务提供商的适配器实现。
"""

from .base import BaseLLMAdapter
from .registry import AdapterRegistry
from .factory import AdapterFactory
from .doubao_adapter import DoubaoAdapter
from .qwen_adapter import QwenAdapter
from .deepseek_adapter import DeepSeekAdapter
from .openai_adapter import OpenAIAdapter
from .claude_adapter import ClaudeAdapter
from .ollama_adapter import OllamaAdapter

# LiteLLM适配器（可选）
try:
    from .litellm_adapter import LiteLLMAdapter
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    LiteLLMAdapter = None

__all__ = [
    "BaseLLMAdapter",
    "AdapterRegistry",
    "AdapterFactory",
    "DoubaoAdapter",
    "QwenAdapter",
    "DeepSeekAdapter",
    "OpenAIAdapter",
    "ClaudeAdapter",
    "OllamaAdapter",
]

if LITELLM_AVAILABLE:
    __all__.append("LiteLLMAdapter")
