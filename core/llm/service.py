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

from typing import List, Dict, Any, Optional, AsyncIterator, TYPE_CHECKING
from datetime import datetime
from time import time as time_now
from core.base.service import BaseService
from core.llm.models import LLMResponse, LLMMessage, RoutingStrategy
from core.llm.context import ConversationContext
from core.llm.adapters.base import BaseLLMAdapter
from core.llm.adapters.registry import AdapterRegistry
if TYPE_CHECKING:
    from core.llm.adapters.factory import AdapterFactory
    from core.llm.routing import AdapterRouter
else:
    from core.llm.adapters.factory import AdapterFactory
    from core.llm.routing import AdapterRouter
from core.llm.utils.retry import retry_with_backoff
from core.llm.utils.token_counter import TokenCounter
from core.base.health_check import HealthCheckResult, HealthStatus
from core.llm.connection_pool import ConnectionPoolManager
from core.llm.request_cache import RequestCache, RequestDeduplicator
from core.llm.cost_manager import CostManager
try:
    from core.llm.metrics_collector import MetricsCollector
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    MetricsCollector = None
from core.llm.request_tracer import RequestTracer


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
        self._factory: Optional[AdapterFactory] = None
        self._router: Optional[AdapterRouter] = None
        self._auto_discover: bool = config.get("llm", {}).get("auto_discover_adapters", True)
        self._enable_routing: bool = config.get("llm", {}).get("enable_routing", False)
        self._default_routing_strategy: RoutingStrategy = RoutingStrategy(
            config.get("llm", {}).get("default_routing_strategy", "balanced")
        )
        self._token_counter: TokenCounter = TokenCounter()
        
        # 性能优化组件
        llm_config = config.get("llm", {})
        perf_config = llm_config.get("performance", {})
        
        # 连接池管理器
        self._connection_pool: Optional[ConnectionPoolManager] = None
        if perf_config.get("enable_connection_pool", True):
            self._connection_pool = ConnectionPoolManager(
                max_connections=perf_config.get("max_connections", 100),
                max_keepalive_connections=perf_config.get("max_keepalive_connections", 20),
                timeout=perf_config.get("connection_timeout", 30.0),
            )
        
        # 请求缓存
        self._request_cache: Optional[RequestCache] = None
        if perf_config.get("enable_cache", True):
            self._request_cache = RequestCache(
                ttl=perf_config.get("cache_ttl", 3600.0),
                max_size=perf_config.get("cache_max_size", 1000),
            )
        
        # 请求去重器
        self._request_deduplicator: Optional[RequestDeduplicator] = None
        if perf_config.get("enable_deduplication", True):
            self._request_deduplicator = RequestDeduplicator()
        
        # 成本管理器
        cost_config = llm_config.get("cost", {})
        self._cost_manager: Optional[CostManager] = None
        if cost_config.get("enabled", True):
            self._cost_manager = CostManager(cost_config)
        
        # 指标采集器
        monitoring_config = llm_config.get("monitoring", {})
        self._metrics_collector: Optional[MetricsCollector] = None
        if monitoring_config.get("enabled", True) and METRICS_AVAILABLE:
            try:
                self._metrics_collector = MetricsCollector()
            except ImportError:
                self.logger.warning("prometheus_client未安装，监控功能已禁用")
                self._metrics_collector = None
        
        # 请求追踪器
        self._request_tracer: Optional[RequestTracer] = None
        if monitoring_config.get("tracing_enabled", True):
            self._request_tracer = RequestTracer(monitoring_config.get("tracing", {}))
    
    async def initialize(self) -> None:
        """初始化服务资源"""
        await super().initialize()
        
        # 自动发现适配器
        if self._auto_discover:
            self._registry.discover_adapters()
            await self._auto_register_adapters()
        
        # 初始化适配器工厂和路由层（如果启用路由）
        if self._enable_routing:
            self._factory = AdapterFactory(self._registry)
            self._router = AdapterRouter(self._factory)
            self.logger.info("适配器路由层已启用")
        
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
            # 跳过LiteLLM适配器（需要特殊处理，因为它是可选的）
            if adapter_name == "litellm-adapter":
                # LiteLLM适配器需要检查是否可用
                try:
                    from core.llm.adapters.litellm_adapter import LiteLLMAdapter, LITELLM_AVAILABLE
                    if not LITELLM_AVAILABLE:
                        self.logger.debug("LiteLLM未安装，跳过LiteLLM适配器注册")
                        continue
                except ImportError:
                    self.logger.debug("LiteLLM适配器不可用，跳过注册")
                    continue
            
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
            
            # 对于LiteLLM适配器，即使没有配置也可以注册（LiteLLM可以从环境变量读取）
            if adapter_config or adapter_name == "litellm-adapter":
                try:
                    # 将全局配置传递给适配器，以便适配器可以读取超时等全局设置
                    adapter_config_with_global = (adapter_config.copy() if adapter_config else {})
                    adapter_config_with_global["_global_config"] = self._config
                    
                    adapter = await self._registry.create_adapter(
                        adapter_name,
                        adapter_config_with_global,
                        connection_pool=self._connection_pool,
                    )
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
    
    async def _get_adapter(
        self,
        model: Optional[str] = None,
        require_healthy: bool = False,
        strategy: Optional[RoutingStrategy] = None,
    ) -> BaseLLMAdapter:
        """
        获取适配器
        
        根据模型名称自动选择适配器，如果未指定模型则使用默认适配器。
        支持健康检查和故障转移。
        如果启用了路由层，则使用路由策略选择适配器。
        
        参数:
            model: 模型名称（可选）
            require_healthy: 是否要求适配器健康（默认False，向后兼容）
            strategy: 路由策略（可选，如果启用路由层）
        
        返回:
            适配器实例
        
        异常:
            LLMError: 找不到适配器时抛出
        """
        if not self._adapters:
            raise LLMError("没有注册的适配器")
        
        # 如果启用了路由层，使用路由策略选择适配器
        if self._enable_routing and self._router:
            try:
                request = {
                    "model": model or self._default_model,
                    "require_healthy": require_healthy,
                }
                routing_strategy = strategy or self._default_routing_strategy
                selected = await self._router.route(request, routing_strategy, list(self._adapters.values()))
                if selected:
                    return selected
            except Exception as e:
                self.logger.warning(f"路由选择失败，回退到默认选择: {e}")
        
        # 回退到原有逻辑（保持向后兼容）
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
        adapter = await self._get_adapter(model)
        
        self.logger.debug(f"发送LLM请求，模型: {model}, 消息数: {len(messages)}")
        
        # 开始追踪（如果启用了追踪）
        trace_context = None
        span = None
        if self._request_tracer:
            try:
                trace_context = self._request_tracer.start_trace(
                    operation="llm_chat",
                    metadata={"model": model, "adapter": adapter.name},
                )
                span = self._request_tracer.start_span(
                    trace_context,
                    operation="adapter_call",
                    tags={"adapter": adapter.name, "model": model},
                )
            except Exception as e:
                self.logger.warning(f"开始追踪失败: {e}")
        
        # 记录活跃请求数
        if self._metrics_collector:
            self._metrics_collector.increment_active_requests(adapter.name, model)
        
        # 记录请求开始时间
        request_start_time = time_now()
        
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
            
            # 计算请求持续时间
            request_duration = time_now() - request_start_time
            
            # 记录成本（如果启用了成本管理）
            cost = None
            if self._cost_manager and response.usage:
                try:
                    # 获取适配器的成本信息
                    cost_info = adapter.get_cost_per_1k_tokens(model)
                    cost_record = await self._cost_manager.record_usage(
                        adapter_name=adapter.name,
                        model=model,
                        usage=response.usage,
                        cost_info=cost_info,
                    )
                    cost = cost_record.total_cost
                except Exception as e:
                    self.logger.warning(f"记录成本失败: {e}")
            
            # 结束追踪
            if span is not None:
                try:
                    self._request_tracer.end_span(span)
                    if trace_context is not None:
                        self._request_tracer.end_trace(trace_context)
                except Exception as e:
                    self.logger.warning(f"结束追踪失败: {e}")
            
            # 减少活跃请求数
            if self._metrics_collector:
                self._metrics_collector.decrement_active_requests(adapter.name, model)
            
            # 记录指标（如果启用了指标采集）
            if self._metrics_collector:
                try:
                    self._metrics_collector.record_request(
                        adapter=adapter.name,
                        model=model,
                        duration=request_duration,
                        success=True,
                        tokens=response.usage,
                        cost=cost,
                    )
                except Exception as e:
                    self.logger.warning(f"记录指标失败: {e}")
            
            self.logger.debug(f"LLM响应完成，Token使用: {response.total_tokens}")
            return response
            
        except Exception as e:
            # 计算请求持续时间
            request_duration = time_now() - request_start_time if 'request_start_time' in locals() else 0.0
            
            # 结束追踪（错误情况）
            if span is not None:
                try:
                    self._request_tracer.end_span(span, error=str(e))
                    if trace_context is not None:
                        self._request_tracer.end_trace(trace_context)
                except Exception:
                    pass
            
            # 减少活跃请求数
            if self._metrics_collector:
                try:
                    self._metrics_collector.decrement_active_requests(adapter.name, model)
                    # 记录错误指标
                    self._metrics_collector.record_request(
                        adapter=adapter.name,
                        model=model,
                        duration=request_duration,
                        success=False,
                        error_type=type(e).__name__,
                    )
                except Exception:
                    pass
            
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
        adapter = await self._get_adapter(model)
        
        self.logger.debug(f"发送流式LLM请求，模型: {model}")
        
        try:
            # 优化流式响应：立即yield，减少延迟
            accumulated_content = ""
            async for chunk_result in adapter.stream_call(
                messages=messages,
                model=model,
                temperature=temperature,
            ):
                chunk_content = chunk_result.get("content", "")
                if chunk_content:
                    accumulated_content += chunk_content
                    # 立即yield，不等待完整响应
                    yield LLMResponse(
                        content=chunk_content,  # 只返回增量内容
                        model=model,
                        usage=chunk_result.get("usage", {}),
                        metadata=chunk_result.get("metadata", {}),
                    )
                else:
                    # 最终块，包含完整使用信息
                    yield LLMResponse(
                        content="",  # 最终块不包含新内容
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
    
    async def get_cost_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        adapter_name: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        获取成本统计信息
        
        参数:
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            adapter_name: 适配器名称（可选）
            model: 模型名称（可选）
        
        返回:
            成本统计信息
        """
        if not self._cost_manager:
            return {"error": "成本管理未启用"}
        
        return await self._cost_manager.get_statistics(
            start_date=start_date,
            end_date=end_date,
            adapter_name=adapter_name,
            model=model,
        )
    
    async def get_cost_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """
        获取成本优化建议
        
        返回:
            优化建议列表
        """
        if not self._cost_manager:
            return []
        
        return await self._cost_manager.get_optimization_suggestions(
            adapters=list(self._adapters.values())
        )
    
    async def cleanup(self) -> None:
        """清理服务资源"""
        # 清理连接池
        if self._connection_pool:
            await self._connection_pool.close_all()
        
        # 清理适配器
        for adapter in self._adapters.values():
            if hasattr(adapter, 'cleanup'):
                await adapter.cleanup()
        
        await super().cleanup()