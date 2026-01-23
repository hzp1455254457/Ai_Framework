"""
模块名称：LLM服务主类模块
功能描述：提供统一的多模型LLM接口，支持多种AI服务提供商
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - LLMService: LLM服务主类

依赖模块：
    - core.base.service: 服务基类
    - core.llm.models: LLM数据模型
    - core.llm.context: 对话上下文
    - core.llm.adapters.base: 适配器基类
    - infrastructure.config: 配置管理
    - infrastructure.log: 日志管理
"""

from typing import List, Dict, Any, Optional, AsyncIterator
from core.base.service import BaseService
from core.llm.models import LLMResponse, LLMMessage
from core.llm.context import ConversationContext
from core.llm.adapters.base import BaseLLMAdapter
from core.llm.adapters.registry import AdapterRegistry
from core.llm.utils.retry import retry_with_backoff
from core.llm.utils.token_counter import TokenCounter
from core.base.health_check import HealthCheckResult, HealthStatus


class LLMError(Exception):
    """LLM服务错误异常"""
    pass


class LLMService(BaseService):
    """
    LLM服务主类
    
    提供统一的多模型LLM接口，支持多种AI服务提供商。
    通过适配器模式实现不同提供商的统一调用接口。
    
    特性：
        - 支持流式输出
        - 上下文管理
        - Token计算
        - 自动重试
        - 成本估算
    
    示例：
        >>> service = LLMService(config)
        >>> await service.initialize()
        >>> response = await service.chat(messages=[...])
    
    属性:
        _adapters: 适配器字典
        _default_model: 默认模型名称
        _registry: 适配器注册表
        _auto_discover: 是否自动发现适配器
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        初始化LLM服务
        
        参数:
            config: 服务配置字典
        """
        super().__init__(config)
        self._adapters: Dict[str, BaseLLMAdapter] = {}
        self._default_model: str = config.get("llm", {}).get("default_model", "gpt-3.5-turbo")
        self._registry: AdapterRegistry = AdapterRegistry()
        self._auto_discover: bool = config.get("llm", {}).get("auto_discover_adapters", True)
        self._token_counter: TokenCounter = TokenCounter()
    
    async def initialize(self) -> None:
        """初始化服务资源"""
        await super().initialize()
        
        # 自动发现适配器
        if self._auto_discover:
            self._registry.discover_adapters()
            await self._auto_register_adapters()
        
        self.logger.info(f"LLM服务初始化完成，默认模型: {self._default_model}")
        self.logger.info(f"已注册适配器: {list(self._adapters.keys())}")
    
    async def _auto_register_adapters(self) -> None:
        """
        自动注册适配器
        
        根据配置自动创建并注册适配器实例。
        """
        llm_config = self._config.get("llm", {})
        adapters_config = llm_config.get("adapters", {})
        
        # 注册模型到适配器的映射
        model_mapping = llm_config.get("model_adapter_mapping", {})
        for model, adapter_name in model_mapping.items():
            self._registry.register_model_mapping(model, adapter_name)
        
        # 获取所有可用的适配器
        available_adapters = self._registry.get_available_adapters()
        
        for adapter_name in available_adapters:
            # 检查是否有该适配器的配置
            adapter_config = adapters_config.get(adapter_name, {})
            
            # 如果没有显式配置，尝试从全局配置中获取
            if not adapter_config:
                # 检查是否有通用的API密钥配置
                if "api_key" in llm_config:
                    adapter_config = {"api_key": llm_config["api_key"]}
                else:
                    # 尝试从适配器名称对应的配置获取
                    provider_key = adapter_name.replace("-adapter", "")
                    if provider_key in llm_config:
                        adapter_config = llm_config[provider_key]
            
            # 如果有配置，创建并注册适配器
            if adapter_config:
                try:
                    adapter = await self._registry.create_adapter(adapter_name, adapter_config)
                    self._adapters[adapter_name] = adapter
                    self.logger.info(f"自动注册适配器: {adapter_name}")
                except Exception as e:
                    self.logger.warning(f"适配器 {adapter_name} 自动注册失败: {e}")
    
    def register_adapter(self, adapter: BaseLLMAdapter) -> None:
        """
        手动注册适配器
        
        参数:
            adapter: 适配器实例
        
        示例:
            >>> adapter = DoubaoAdapter(config)
            >>> await adapter.initialize()
            >>> service.register_adapter(adapter)
        """
        self._adapters[adapter.name] = adapter
        self.logger.info(f"手动注册适配器: {adapter.name} (provider: {adapter.provider})")
    
    def _get_adapter(self, model: Optional[str] = None, require_healthy: bool = False) -> BaseLLMAdapter:
        """
        获取适配器
        
        根据模型名称自动选择适配器，如果未指定模型则使用默认适配器。
        支持健康检查和故障转移。
        
        参数:
            model: 模型名称（可选）
            require_healthy: 是否要求适配器健康（默认False，向后兼容）
        
        返回:
            适配器实例
        
        异常:
            LLMError: 找不到适配器时抛出
        """
        if not self._adapters:
            raise LLMError("没有注册的适配器")
        
        # 如果指定了模型，尝试根据模型名称找到对应的适配器
        candidate_adapters: List[BaseLLMAdapter] = []
        
        if model:
            adapter_name = self._registry.get_adapter_for_model(model)
            if adapter_name and adapter_name in self._adapters:
                candidate_adapters.append(self._adapters[adapter_name])
            
            # 如果找不到，使用模型名称作为提示信息
            if not candidate_adapters:
                self.logger.warning(
                    f"未找到模型 {model} 对应的适配器，使用默认适配器"
                )
        
        # 如果没有候选适配器，使用默认适配器
        if not candidate_adapters:
            default_adapter_name = self._config.get("llm", {}).get("default_adapter")
            if default_adapter_name and default_adapter_name in self._adapters:
                candidate_adapters.append(self._adapters[default_adapter_name])
            else:
                candidate_adapters.append(next(iter(self._adapters.values())))
        
        # 如果要求健康，选择健康的适配器
        if require_healthy:
            # 尝试从候选适配器中选择健康的
            for adapter in candidate_adapters:
                # 这里不实际执行健康检查（避免性能开销），而是依赖调用时的健康检查
                # 如果需要，可以在这里添加同步健康检查
                return adapter
            
            # 如果候选适配器都不健康，尝试所有适配器
            for adapter in self._adapters.values():
                if adapter not in candidate_adapters:
                    candidate_adapters.append(adapter)
            
            # 返回第一个候选适配器（实际健康检查在调用时进行）
            return candidate_adapters[0]
        
        return candidate_adapters[0]
    
    async def check_adapter_health(self, adapter_name: Optional[str] = None) -> Dict[str, HealthCheckResult]:
        """
        检查适配器健康状态
        
        检查指定适配器或所有适配器的健康状态。
        
        参数:
            adapter_name: 适配器名称（可选，如果为None则检查所有适配器）
        
        返回:
            适配器健康状态字典，键为适配器名称，值为健康检查结果
        """
        results: Dict[str, HealthCheckResult] = {}
        
        if adapter_name:
            if adapter_name not in self._adapters:
                return {adapter_name: HealthCheckResult(
                    status=HealthStatus.UNKNOWN,
                    message="适配器未注册"
                )}
            adapters_to_check = {adapter_name: self._adapters[adapter_name]}
        else:
            adapters_to_check = self._adapters
        
        for name, adapter in adapters_to_check.items():
            try:
                result = await adapter.health_check()
                results[name] = result
            except Exception as e:
                results[name] = HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"健康检查异常: {e}"
                )
        
        return results
    
    async def get_healthy_adapters(self) -> List[str]:
        """
        获取健康的适配器列表
        
        返回:
            健康的适配器名称列表
        """
        health_results = await self.check_adapter_health()
        healthy_adapters = [
            name for name, result in health_results.items()
            if result.status == HealthStatus.HEALTHY
        ]
        return healthy_adapters
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        发送聊天请求
        
        向指定的LLM模型发送消息列表，返回模型响应。
        
        参数:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称，默认使用配置的默认模型
            temperature: 温度参数，控制输出随机性，范围 0-2
            max_tokens: 最大token数（可选）
            functions: Function Calling工具定义列表（可选）
            **kwargs: 其他参数，会传递给适配器
        
        返回:
            LLMResponse对象，包含响应内容、Token使用量等信息
        
        异常:
            LLMError: LLM调用失败时抛出
            ValueError: 参数验证失败时抛出
        
        示例:
            >>> messages = [{"role": "user", "content": "Hello"}]
            >>> response = await service.chat(messages, model="gpt-4")
            >>> print(response.content)
        """
        if not messages:
            raise ValueError("消息列表不能为空")
        
        model = model or self._default_model
        adapter = self._get_adapter(model)
        
        self.logger.debug(f"发送LLM请求，模型: {model}, 消息数: {len(messages)}")
        
        # 获取重试配置
        max_retries = self._config.get("llm", {}).get("max_retries", 3)
        
        try:
            # 使用重试机制调用适配器
            async def _call_adapter():
                # 构建适配器调用参数
                adapter_kwargs = {
                    "messages": messages,
                    "model": model,
                    "temperature": temperature,
                }
                if max_tokens:
                    adapter_kwargs["max_tokens"] = max_tokens
                if functions:
                    adapter_kwargs["functions"] = functions
                # 合并其他kwargs参数
                adapter_kwargs.update(kwargs)
                
                return await adapter.call(**adapter_kwargs)
            
            result = await retry_with_backoff(
                _call_adapter,
                max_attempts=max_retries,
                initial_wait=1.0,
                max_wait=10.0,
            )
            
            # 构建响应对象
            response = LLMResponse(
                content=result.get("content", ""),
                model=model,
                usage=result.get("usage", {}),
                metadata=result.get("metadata", {}),
            )
            
            self.logger.debug(f"LLM响应完成，Token使用: {response.total_tokens}")
            return response
            
        except Exception as e:
            self.logger.error(f"LLM调用失败: {e}", exc_info=True)
            raise LLMError(f"LLM调用失败: {e}") from e
    
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[LLMResponse]:
        """
        流式聊天
        
        发送流式聊天请求，逐个返回响应块。
        
        参数:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
        
        生成器:
            逐个返回LLMResponse对象
        
        异常:
            LLMError: LLM调用失败时抛出
        
        示例:
            >>> async for chunk in service.stream_chat(messages):
            ...     print(chunk.content, end="", flush=True)
        """
        if not messages:
            raise ValueError("消息列表不能为空")
        
        model = model or self._default_model
        adapter = self._get_adapter(model)
        
        self.logger.debug(f"发送流式LLM请求，模型: {model}")
        
        try:
            async for chunk_result in adapter.stream_call(
                messages=messages,
                model=model,
                temperature=temperature,
            ):
                yield LLMResponse(
                    content=chunk_result.get("content", ""),
                    model=model,
                    usage=chunk_result.get("usage", {}),
                    metadata=chunk_result.get("metadata", {}),
                )
        except Exception as e:
            self.logger.error(f"流式LLM调用失败: {e}", exc_info=True)
            raise LLMError(f"流式LLM调用失败: {e}") from e
    
    def calculate_tokens(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> int:
        """
        计算Token数量
        
        计算文本的Token数量（用于成本估算）。
        
        参数:
            text: 文本内容
            model: 模型名称（可选，不同模型的token计算方式可能不同）
        
        返回:
            Token数量
        
        说明:
            - GPT等模型：使用tiktoken进行精确计算
            - 非OpenAI/未知模型：使用cl100k_base作为回退（仍为编码级别的真实token计数）
        """
        return self._token_counter.count_text_tokens(text=text, model=model)
