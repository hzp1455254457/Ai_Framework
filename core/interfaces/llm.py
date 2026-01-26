"""
模块名称：LLM提供者抽象接口
功能描述：定义LLM提供者的抽象接口，支持多种实现（自研、LiteLLM、LangChain）
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - ILLMProvider: LLM提供者抽象接口

依赖模块：
    - abc: 抽象基类
    - typing: 类型注解
    - core.llm.models: LLM数据模型
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncIterator, Optional
from core.llm.models import LLMResponse


class ILLMProvider(ABC):
    """
    LLM提供者抽象接口
    
    定义统一的LLM提供者接口规范，支持多种实现（自研、LiteLLM、LangChain）。
    所有LLM提供者实现都必须实现此接口。
    
    特性：
        - 统一的聊天接口
        - 流式输出支持
        - 模型列表查询
        - 健康检查
    
    示例：
        >>> provider = NativeLLMProvider(config)
        >>> await provider.initialize()
        >>> response = await provider.chat(messages=[{"role": "user", "content": "Hello"}])
    """
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """
        发送聊天请求
        
        参数:
            messages: 消息列表，每个消息包含role和content
            model: 模型名称（可选，如果未提供则使用默认模型）
            temperature: 温度参数（0.0-2.0）
            max_tokens: 最大token数（可选）
            **kwargs: 其他参数
        
        返回:
            LLMResponse对象，包含响应内容和元数据
        
        异常:
            RuntimeError: 提供者未初始化时抛出
            ValueError: 参数无效时抛出
        """
        pass
    
    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> AsyncIterator[LLMResponse]:
        """
        流式聊天
        
        支持流式输出，逐个返回响应块。
        
        参数:
            messages: 消息列表
            model: 模型名称（可选）
            temperature: 温度参数
            **kwargs: 其他参数
        
        生成器:
            逐个返回LLMResponse对象，每个对象包含部分响应内容
        
        异常:
            RuntimeError: 提供者未初始化时抛出
            ValueError: 参数无效时抛出
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        获取可用模型列表
        
        返回:
            可用模型名称列表
        
        示例:
            >>> models = provider.get_available_models()
            >>> print(models)
            ['gpt-3.5-turbo', 'gpt-4', 'claude-3-opus']
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        健康检查
        
        检查LLM提供者是否可用。
        
        返回:
            True表示健康可用，False表示不可用
        
        异常:
            RuntimeError: 检查过程中发生错误时抛出
        
        示例:
            >>> is_healthy = await provider.health_check()
            >>> if is_healthy:
            ...     print("LLM提供者可用")
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        初始化LLM提供者
        
        初始化提供者所需的所有资源。
        
        异常:
            RuntimeError: 初始化失败时抛出
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """
        清理LLM提供者资源
        
        清理提供者占用的所有资源。
        """
        pass
