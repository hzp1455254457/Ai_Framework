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
from typing import List, Dict, Any, Optional, AsyncIterator, TYPE_CHECKING
from core.base.adapter import BaseAdapter
from core.llm.models import LLMResponse, ModelCapability

if TYPE_CHECKING:
    from core.llm.connection_pool import ConnectionPoolManager


class BaseLLMAdapter(BaseAdapter):
    """
    LLM适配器基类
    
    所有LLM适配器的抽象基类，定义了统一的LLM调用接口。
    
    特性：
        - 统一的调用接口
        - 流式调用支持
        - 响应格式标准化
        - 模型能力标签
        - 成本信息
    
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
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        connection_pool: Optional["ConnectionPoolManager"] = None,
    ) -> None:
        """
        初始化适配器
        
        参数:
            config: 适配器配置
            connection_pool: 连接池管理器（可选，用于性能优化）
        """
        super().__init__(config)
        self._capability: Optional[ModelCapability] = None
        self._cost_per_1k_tokens: Optional[Dict[str, float]] = None  # {input: cost, output: cost}
        self._connection_pool: Optional["ConnectionPoolManager"] = connection_pool
    
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
    
    def get_capability(self) -> Optional[ModelCapability]:
        """
        获取模型能力标签
        
        返回:
            模型能力标签，如果未设置返回None
        """
        return self._capability
    
    def set_capability(self, capability: ModelCapability) -> None:
        """
        设置模型能力标签
        
        参数:
            capability: 模型能力标签
        """
        self._capability = capability
    
    def get_cost_per_1k_tokens(self, model: str) -> Optional[Dict[str, float]]:
        """
        获取每1000个Token的成本（美元）
        
        参数:
            model: 模型名称
        
        返回:
            成本字典，包含input和output成本，如果未设置返回None
        """
        return self._cost_per_1k_tokens
    
    def set_cost_per_1k_tokens(
        self,
        input_cost: float,
        output_cost: float,
    ) -> None:
        """
        设置每1000个Token的成本
        
        参数:
            input_cost: 输入Token成本（每1000个Token）
            output_cost: 输出Token成本（每1000个Token）
        """
        self._cost_per_1k_tokens = {
            "input": input_cost,
            "output": output_cost,
        }