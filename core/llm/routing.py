"""
模块名称：适配器路由模块
功能描述：提供适配器路由功能，支持智能路由和负载均衡
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - AdapterRouter: 适配器路由器
    - RoutingStrategy: 路由策略基类
    - CostFirstStrategy: 成本优先策略
    - PerformanceFirstStrategy: 性能优先策略
    - AvailabilityFirstStrategy: 可用性优先策略
    - BalancedStrategy: 平衡模式策略

依赖模块：
    - core.llm.adapters.base: 适配器基类
    - core.llm.models: 数据模型
    - core.base.health_check: 健康检查
    - typing: 类型注解
    - abc: 抽象基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from core.llm.adapters.base import BaseLLMAdapter
from core.llm.models import ModelCapability, RoutingStrategy
from core.base.health_check import HealthStatus, HealthCheckResult
from core.llm.load_balancer import LoadBalancer, LoadBalanceStrategy

if TYPE_CHECKING:
    from core.llm.adapters.factory import AdapterFactory


class RoutingStrategyBase(ABC):
    """
    路由策略基类
    
    定义路由策略的接口，所有具体策略必须实现此接口。
    """
    
    @abstractmethod
    async def select_adapter(
        self,
        request: Dict[str, Any],
        adapters: List[BaseLLMAdapter],
    ) -> Optional[BaseLLMAdapter]:
        """
        选择适配器
        
        参数:
            request: 请求信息（包含messages、model、strategy等）
            adapters: 候选适配器列表
        
        返回:
            选中的适配器，如果无法选择返回None
        """
        pass


class CostFirstStrategy(RoutingStrategyBase):
    """
    成本优先路由策略
    
    选择成本最低的适配器。
    """
    
    async def select_adapter(
        self,
        request: Dict[str, Any],
        adapters: List[BaseLLMAdapter],
    ) -> Optional[BaseLLMAdapter]:
        """选择成本最低的适配器"""
        if not adapters:
            return None
        
        # 估算每个适配器的成本
        best_adapter = None
        min_cost = float('inf')
        
        for adapter in adapters:
            # 检查健康状态
            try:
                health = await adapter.health_check()
                if health.status != HealthStatus.HEALTHY:
                    continue
            except Exception:
                continue
            
            # 获取成本信息
            model = request.get("model", "")
            cost_info = adapter.get_cost_per_1k_tokens(model)
            
            if cost_info:
                # 简单估算：假设输入和输出各占一半
                avg_cost = (cost_info.get("input", 0) + cost_info.get("output", 0)) / 2
                if avg_cost < min_cost:
                    min_cost = avg_cost
                    best_adapter = adapter
        
        # 如果没有找到有成本信息的适配器，返回第一个健康的适配器
        if best_adapter is None:
            for adapter in adapters:
                try:
                    health = await adapter.health_check()
                    if health.status == HealthStatus.HEALTHY:
                        return adapter
                except Exception:
                    continue
        
        return best_adapter or (adapters[0] if adapters else None)


class PerformanceFirstStrategy(RoutingStrategyBase):
    """
    性能优先路由策略
    
    选择性能最优的适配器（基于延迟、吞吐量等指标）。
    """
    
    async def select_adapter(
        self,
        request: Dict[str, Any],
        adapters: List[BaseLLMAdapter],
    ) -> Optional[BaseLLMAdapter]:
        """选择性能最优的适配器"""
        if not adapters:
            return None
        
        # 检查健康状态，选择健康的适配器
        healthy_adapters = []
        for adapter in adapters:
            try:
                health = await adapter.health_check()
                if health.status == HealthStatus.HEALTHY:
                    healthy_adapters.append(adapter)
            except Exception:
                continue
        
        if not healthy_adapters:
            return adapters[0] if adapters else None
        
        # 简单实现：选择第一个健康的适配器
        # TODO: 可以根据历史性能数据选择
        return healthy_adapters[0]


class AvailabilityFirstStrategy(RoutingStrategyBase):
    """
    可用性优先路由策略
    
    选择健康状态最好的适配器。
    """
    
    async def select_adapter(
        self,
        request: Dict[str, Any],
        adapters: List[BaseLLMAdapter],
    ) -> Optional[BaseLLMAdapter]:
        """选择健康状态最好的适配器"""
        if not adapters:
            return None
        
        # 检查所有适配器的健康状态
        best_adapter = None
        best_status = HealthStatus.UNKNOWN
        
        for adapter in adapters:
            try:
                health = await adapter.health_check()
                if health.status == HealthStatus.HEALTHY:
                    return adapter  # 找到健康的就返回
                elif health.status.value > best_status.value:
                    best_status = health.status
                    best_adapter = adapter
            except Exception:
                continue
        
        return best_adapter or (adapters[0] if adapters else None)


class BalancedStrategy(RoutingStrategyBase):
    """
    平衡模式路由策略
    
    综合考虑成本、性能、可用性等因素。
    """
    
    async def select_adapter(
        self,
        request: Dict[str, Any],
        adapters: List[BaseLLMAdapter],
    ) -> Optional[BaseLLMAdapter]:
        """综合考虑多个因素选择适配器"""
        if not adapters:
            return None
        
        # 首先过滤出健康的适配器
        healthy_adapters = []
        for adapter in adapters:
            try:
                health = await adapter.health_check()
                if health.status == HealthStatus.HEALTHY:
                    healthy_adapters.append(adapter)
            except Exception:
                continue
        
        if not healthy_adapters:
            return adapters[0] if adapters else None
        
        # 简单实现：优先选择有成本信息的适配器，然后选择第一个
        for adapter in healthy_adapters:
            model = request.get("model", "")
            if adapter.get_cost_per_1k_tokens(model):
                return adapter
        
        return healthy_adapters[0]


class AdapterRouter:
    """
    适配器路由器
    
    根据路由策略选择适配器，支持负载均衡和故障转移。
    
    特性：
        - 智能路由决策
        - 负载均衡
        - 故障转移
        - 健康状态管理
    
    示例:
        >>> router = AdapterRouter(factory)
        >>> adapter = await router.route(request, RoutingStrategy.COST_FIRST)
    """
    
    def __init__(self, factory: "AdapterFactory") -> None:
        """
        初始化适配器路由器
        
        参数:
            factory: 适配器工厂实例
        """
        self._factory = factory
        self._strategies: Dict[RoutingStrategy, RoutingStrategyBase] = {
            RoutingStrategy.COST_FIRST: CostFirstStrategy(),
            RoutingStrategy.PERFORMANCE_FIRST: PerformanceFirstStrategy(),
            RoutingStrategy.AVAILABILITY_FIRST: AvailabilityFirstStrategy(),
            RoutingStrategy.BALANCED: BalancedStrategy(),
        }
        self._load_balancer: LoadBalancer = LoadBalancer(LoadBalanceStrategy.ROUND_ROBIN)
        self._health_cache: Dict[str, HealthCheckResult] = {}  # adapter_name -> health_result
        self._health_cache_ttl: float = 60.0  # 健康检查缓存TTL（秒）
        self._health_cache_timestamps: Dict[str, float] = {}  # adapter_name -> timestamp
    
    async def route(
        self,
        request: Dict[str, Any],
        strategy: RoutingStrategy = RoutingStrategy.BALANCED,
        adapters: Optional[List[BaseLLMAdapter]] = None,
    ) -> Optional[BaseLLMAdapter]:
        """
        根据策略路由到合适的适配器
        
        参数:
            request: 请求信息
            strategy: 路由策略
            adapters: 候选适配器列表（如果为None，则从工厂获取）
        
        返回:
            选中的适配器，如果无法选择返回None
        """
        # 获取候选适配器
        if adapters is None:
            adapters = await self._get_available_adapters(request)
        
        if not adapters:
            return None
        
        # 如果是手动模式，直接返回指定的适配器
        if strategy == RoutingStrategy.MANUAL:
            model = request.get("model")
            if model:
                adapter_name = self._factory.registry.get_adapter_for_model(model)
                if adapter_name:
                    # TODO: 从工厂获取适配器实例
                    pass
            return adapters[0] if adapters else None
        
        # 使用策略选择适配器
        strategy_impl = self._strategies.get(strategy)
        if not strategy_impl:
            # 默认使用平衡模式
            strategy_impl = self._strategies[RoutingStrategy.BALANCED]
        
        # 过滤健康的适配器（故障转移机制）
        healthy_adapters = await self._filter_healthy_adapters(adapters, request.get("require_healthy", True))
        
        if not healthy_adapters:
            # 如果没有健康的适配器，尝试使用所有适配器（降级）
            healthy_adapters = adapters
        
        # 使用策略选择适配器
        selected = await strategy_impl.select_adapter(request, healthy_adapters)
        
        # 如果策略没有选择，使用负载均衡器选择
        if not selected and healthy_adapters:
            selected = self._load_balancer.select(healthy_adapters)
        
        # 更新负载均衡状态
        if selected:
            adapter_name = selected.name
            self._load_balancer.record_request(adapter_name)
        
        return selected
    
    async def _get_available_adapters(
        self,
        request: Dict[str, Any],
    ) -> List[BaseLLMAdapter]:
        """
        获取可用的适配器列表
        
        参数:
            request: 请求信息
        
        返回:
            可用适配器列表
        """
        # 从工厂的注册表获取所有适配器
        # 注意：这里需要传入已创建的适配器实例列表
        # 实际使用时，应该从LLMService传入适配器列表
        return []
    
    async def _filter_healthy_adapters(
        self,
        adapters: List[BaseLLMAdapter],
        require_healthy: bool = True,
    ) -> List[BaseLLMAdapter]:
        """
        过滤健康的适配器（故障转移机制）
        
        参数:
            adapters: 候选适配器列表
            require_healthy: 是否只返回健康的适配器
        
        返回:
            健康的适配器列表
        """
        if not require_healthy:
            return adapters
        
        import time
        healthy_adapters = []
        current_time = time.time()
        
        for adapter in adapters:
            adapter_name = adapter.name
            
            # 检查缓存
            cached_health = self._health_cache.get(adapter_name)
            cache_timestamp = self._health_cache_timestamps.get(adapter_name, 0)
            
            # 如果缓存有效，使用缓存
            if cached_health and (current_time - cache_timestamp) < self._health_cache_ttl:
                if cached_health.status == HealthStatus.HEALTHY:
                    healthy_adapters.append(adapter)
                continue
            
            # 执行健康检查
            try:
                health = await adapter.health_check()
                # 更新缓存
                self._health_cache[adapter_name] = health
                self._health_cache_timestamps[adapter_name] = current_time
                
                if health.status == HealthStatus.HEALTHY:
                    healthy_adapters.append(adapter)
            except Exception:
                # 健康检查失败，标记为不健康
                unhealthy_health = HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message="健康检查异常"
                )
                self._health_cache[adapter_name] = unhealthy_health
                self._health_cache_timestamps[adapter_name] = current_time
        
        return healthy_adapters
    
    async def get_healthy_adapters(
        self,
        adapters: Optional[List[BaseLLMAdapter]] = None,
        capability: Optional[ModelCapability] = None,
    ) -> List[BaseLLMAdapter]:
        """
        获取健康的适配器列表
        
        参数:
            adapters: 候选适配器列表（如果为None，则从工厂获取）
            capability: 所需的能力标签（可选，用于过滤）
        
        返回:
            健康的适配器列表
        """
        if adapters is None:
            adapters = await self._get_available_adapters({})
        
        healthy_adapters = await self._filter_healthy_adapters(adapters, require_healthy=True)
        
        # 如果指定了能力要求，进一步过滤
        if capability:
            filtered = []
            for adapter in healthy_adapters:
                adapter_capability = adapter.get_capability()
                if adapter_capability and self._match_capability(adapter_capability, capability):
                    filtered.append(adapter)
            return filtered
        
        return healthy_adapters
    
    def _match_capability(
        self,
        adapter_capability: ModelCapability,
        required_capability: ModelCapability,
    ) -> bool:
        """
        检查适配器能力是否满足要求
        
        参数:
            adapter_capability: 适配器能力
            required_capability: 所需能力
        
        返回:
            是否满足要求
        """
        # 检查所有必需的能力
        if required_capability.reasoning and not adapter_capability.reasoning:
            return False
        if required_capability.creativity and not adapter_capability.creativity:
            return False
        if required_capability.function_calling and not adapter_capability.function_calling:
            return False
        if required_capability.vision and not adapter_capability.vision:
            return False
        # cost_effective、fast、multilingual 是可选属性，不强制要求
        return True
    
    def register_strategy(
        self,
        strategy: RoutingStrategy,
        implementation: RoutingStrategyBase,
    ) -> None:
        """
        注册自定义路由策略
        
        参数:
            strategy: 路由策略枚举
            implementation: 策略实现
        """
        self._strategies[strategy] = implementation
    
    def set_load_balance_strategy(self, strategy: LoadBalanceStrategy) -> None:
        """
        设置负载均衡策略
        
        参数:
            strategy: 负载均衡策略
        """
        self._load_balancer = LoadBalancer(strategy)
    
    def set_load_balance_weights(self, weights: Dict[str, int]) -> None:
        """
        设置负载均衡权重（用于加权轮询）
        
        参数:
            weights: 权重字典 {adapter_name: weight}
        """
        self._load_balancer.set_weights(weights)
    
    def clear_health_cache(self) -> None:
        """清空健康检查缓存"""
        self._health_cache.clear()
        self._health_cache_timestamps.clear()
    
    def get_load_balance_statistics(self) -> Dict[str, Any]:
        """
        获取负载均衡统计信息
        
        返回:
            统计信息字典
        """
        return self._load_balancer.get_statistics()