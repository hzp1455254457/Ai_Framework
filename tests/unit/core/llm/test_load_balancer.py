"""
测试模块：负载均衡器测试
功能描述：测试LoadBalancer的所有功能
"""

import pytest
from unittest.mock import MagicMock
from core.llm.load_balancer import LoadBalancer, LoadBalanceStrategy


class MockAdapter:
    """用于测试的Mock适配器"""
    
    def __init__(self, name):
        self.name = name
        self._active_connections = 0
    
    def get_active_connections(self):
        return self._active_connections


@pytest.mark.asyncio
class TestLoadBalancer:
    """LoadBalancer测试类"""
    
    @pytest.fixture
    def adapters(self):
        """创建适配器列表fixture"""
        return [
            MockAdapter("adapter1"),
            MockAdapter("adapter2"),
            MockAdapter("adapter3"),
        ]
    
    @pytest.fixture
    def load_balancer(self):
        """创建负载均衡器fixture"""
        return LoadBalancer()
    
    async def test_round_robin_strategy(self, load_balancer, adapters):
        """测试轮询策略"""
        # Arrange
        load_balancer.set_strategy(LoadBalanceStrategy.ROUND_ROBIN)
        
        # Act
        selected1 = load_balancer.select(adapters)
        selected2 = load_balancer.select(adapters)
        selected3 = load_balancer.select(adapters)
        selected4 = load_balancer.select(adapters)
        
        # Assert
        assert selected1.name == "adapter1"
        assert selected2.name == "adapter2"
        assert selected3.name == "adapter3"
        assert selected4.name == "adapter1"  # 循环回到第一个
    
    async def test_weighted_round_robin_strategy(self, load_balancer, adapters):
        """测试加权轮询策略"""
        # Arrange
        load_balancer.set_strategy(LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN)
        weights = {"adapter1": 0.5, "adapter2": 0.3, "adapter3": 0.2}
        load_balancer.set_weights(weights)
        
        # Act
        selected = load_balancer.select(adapters)
        
        # Assert
        assert selected in adapters
    
    async def test_least_connections_strategy(self, load_balancer, adapters):
        """测试最少连接策略"""
        # Arrange
        load_balancer.set_strategy(LoadBalanceStrategy.LEAST_CONNECTIONS)
        adapters[0]._active_connections = 5
        adapters[1]._active_connections = 2
        adapters[2]._active_connections = 3
        
        # Act
        selected = load_balancer.select(adapters)
        
        # Assert
        assert selected.name == "adapter2"  # 连接数最少
    
    async def test_random_strategy(self, load_balancer, adapters):
        """测试随机策略"""
        # Arrange
        load_balancer.set_strategy(LoadBalanceStrategy.RANDOM)
        
        # Act
        selected = load_balancer.select(adapters)
        
        # Assert
        assert selected in adapters
    
    async def test_empty_adapters_list(self, load_balancer):
        """测试空适配器列表"""
        # Act
        selected = load_balancer.select([])
        
        # Assert
        assert selected is None
    
    async def test_set_weights(self, load_balancer):
        """测试设置权重"""
        # Arrange
        weights = {"adapter1": 0.7, "adapter2": 0.3}
        
        # Act
        load_balancer.set_weights(weights)
        
        # Assert
        assert load_balancer._weights == weights
    
    async def test_get_statistics(self, load_balancer, adapters):
        """测试获取统计信息"""
        # Arrange
        load_balancer.set_strategy(LoadBalanceStrategy.ROUND_ROBIN)
        
        # 执行几次选择
        for _ in range(5):
            load_balancer.select(adapters)
        
        # Act
        stats = load_balancer.get_statistics()
        
        # Assert
        assert stats is not None
        assert isinstance(stats, dict)
        assert "total_requests" in stats
