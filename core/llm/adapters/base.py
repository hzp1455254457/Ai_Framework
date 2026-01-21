"""
模块名称：LLM适配器基类模块
功能描述：定义LLM适配器的基类和接口
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - BaseLLMAdapter: LLM适配器基类

依赖模块：
    - core.base.adapter: 适配器基类
    - typing: 类型注解
"""

from abc import abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from core.base.adapter import BaseAdapter
from core.llm.models import LLMResponse


class BaseLLMAdapter(BaseAdapter):
    """
    LLM适配器基类
    
    所有LLM适配器的抽象基类，定义了统一的LLM调用接口。
    
    特性：
        - 统一的调用接口
        - 流式调用支持
        - 响应格式标准化
    
    示例:
        >>> class MyAdapter(BaseLLMAdapter):
        ...     @property
        ...     def provider(self) -> str:
        ...         return "my-provider"
        ...     
        ...     async def call(self, messages, model, **kwargs) -> dict:
        ...         # 实现调用逻辑
        ...         return {"content": "...", "usage": {...}}
    """
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """
        服务提供商名称
        
        返回:
            服务提供商的名称（如 "openai", "claude", "ollama"）
        """
        pass
    
    @abstractmethod
    async def call(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        调用LLM接口
        
        统一的LLM调用接口，将统一的接口转换为提供商特定的API调用。
        
        参数:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
        
        返回:
            标准格式的响应字典，包含：
                - content: 响应内容
                - usage: Token使用信息
                - metadata: 其他元数据
        
        异常:
            AdapterCallError: 调用失败时抛出
        """
        pass
    
    async def stream_call(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式调用接口
        
        支持流式响应的服务调用。
        
        参数:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            **kwargs: 其他参数
        
        生成器:
            逐个返回响应块，每个块为字典格式
        """
        # 默认实现：调用非流式接口并包装为流式响应
        response = await self.call(
            messages=messages,
            model=model,
            temperature=temperature,
            **kwargs,
        )
        yield response
