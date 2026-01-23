"""
测试模块：适配器路由层测试
功能描述：测试AdapterRouter和路由策略的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.llm.routing import AdapterRouter, RoutingStrategy
from core.llm.adapters.factory import AdapterFactory
from core.llm.adapters.registry import AdapterRegistry
from core.llm.adapters.base import BaseLLMAdapter
from core.llm.models import ModelCapability
from core.base.health_check import HealthStatus, HealthCheckResult


class MockAdapter(BaseLLMAdapter):
    """用于测试的Mock适配器"""
    
    def __init__(self, name, config=None, connection_pool=None):
        super().__init__(config, connection_pool)
        self._name = name
        self._healthy = True
        self._cost = {"input": 0.001, "output": 0.002}
        self._capability = ModelCapability(
            reasoning=True,
            creativity=False,
            cost_effective=True,
            fast=True,
        )
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def provider(self) -> str:
        return "mock"
    
    def get_cost_per_1k_tokens(self, model: str = None):
        return self._cost
    
    def get_capability(self, model: str = None):
        return self._capability
    
    async def health_check(self):
        if self._healthy:
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="Healthy"
            )
        else:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message="Unhealthy"
            )
    
    async def call(self, messages, model, **kwargs):
        return {
            "content": f"Response from {self._name}",
            "usage": {"total_tokens": 10},
            "metadata": {},
        }


@pytest.mark.asyncio
class TestAdapterRouter:
    """AdapterRouter测试类"""
    
    @pytest.fixture
    def registry(self):
        """创建注册表fixture"""
        registry = AdapterRegistry()
        registry.register_adapter("adapter1", MockAdapter)
        registry.register_adapter("adapter2", MockAdapter)
        return registry
    
    @pytest.fixture
    def factory(self, registry):
        """创建工厂fixture"""
        return AdapterFactory(registry)
    
    @pytest.fixture
    def router(self, factory):
        """创建路由器fixture"""
        return AdapterRouter(factory)
    
    @pytest.fixture
    def adapters(self):
        """创建适配器列表fixture"""
        adapter1 = MockAdapter("adapter1")
        adapter2 = MockAdapter("adapter2")
        adapter2._cost = {"input": 0.0005, "output": 0.001}  # 更便宜
        return [adapter1, adapter2]
    
    async def test_router_initialization(self, router):
        """测试路由器初始化"""
        # Assert
        assert router._factory is not None
        assert router._health_cache == {}
    
    async def test_route_cost_first(self, router, adapters):
        """测试成本优先路由策略"""
        # Arrange
        request = {"model": "test-model"}
        
        # Act
        selected = await router.route(request, RoutingStrategy.COST_FIRST, adapters)
        
        # Assert
        assert selected is not None
        # adapter2 成本更低，应该被选中
        assert selected.name == "adapter2"
    
    async def test_route_performance_first(self, router, adapters):
        """测试性能优先路由策略"""
        # Arrange
        request = {"model": "test-model"}
        
        # Act
        selected = await router.route(request, RoutingStrategy.PERFORMANCE_FIRST, adapters)
        
        # Assert
        assert selected is not None
        assert selected in adapters
    
    async def test_route_availability_first(self, router, adapters):
        """测试可用性优先路由策略"""
        # Arrange
        request = {"model": "test-model"}
        adapters[0]._healthy = False  # adapter1不健康
        
        # Act
        selected = await router.route(request, RoutingStrategy.AVAILABILITY_FIRST, adapters)
        
        # Assert
        assert selected is not None
        # 应该选择健康的adapter2
        assert selected.name == "adapter2"
    
    async def test_route_balanced(self, router, adapters):
        """测试平衡路由策略"""
        # Arrange
        request = {"model": "test-model"}
        
        # Act
        selected = await router.route(request, RoutingStrategy.BALANCED, adapters)
        
        # Assert
        assert selected is not None
        assert selected in adapters
    
    async def test_route_with_capability_filter(self, router, adapters):
        """测试带能力过滤的路由"""
        # Arrange
        request = {
            "model": "test-model",
            "capability": ModelCapability(reasoning=True)
        }
        
        # Act
        selected = await router.route(request, RoutingStrategy.BALANCED, adapters)
        
        # Assert
        assert selected is not None
        # 两个适配器都支持reasoning，应该能选到
        assert selected.get_capability().reasoning is True
    
    async def test_route_no_healthy_adapters(self, router, adapters):
        """测试没有健康适配器的情况"""
        # Arrange
        request = {"model": "test-model", "require_healthy": True}
        adapters[0]._healthy = False
        adapters[1]._healthy = False
        
        # Act
        selected = await router.route(request, RoutingStrategy.AVAILABILITY_FIRST, adapters)
        
        # Assert
        assert selected is None
    
    async def test_set_load_balance_strategy(self, router):
        """测试设置负载均衡策略"""
        # Act
        router.set_load_balance_strategy("round_robin")
        
        # Assert
        assert router._load_balancer._strategy.name == "round_robin"
    
    async def test_set_load_balance_weights(self, router):
        """测试设置负载均衡权重"""
        # Arrange
        weights = {"adapter1": 0.7, "adapter2": 0.3}
        
        # Act
        router.set_load_balance_weights(weights)
        
        # Assert
        assert router._load_balancer._weights == weights
    
    async def test_clear_health_cache(self, router):
        """测试清理健康检查缓存"""
        # Arrange
        router._health_cache["adapter1"] = HealthCheckResult(
            status=HealthStatus.HEALTHY,
            message="Cached"
        )
        
        # Act
        router.clear_health_cache()
        
        # Assert
        assert len(router._health_cache) == 0
    
    async def test_get_load_balance_statistics(self, router, adapters):
        """测试获取负载均衡统计"""
        # Arrange
        request = {"model": "test-model"}
        
        # 执行几次路由
        for _ in range(5):
            await router.route(request, RoutingStrategy.BALANCED, adapters)
        
        # Act
        stats = router.get_load_balance_statistics()
        
        # Assert
        assert stats is not None
        assert isinstance(stats, dict)
