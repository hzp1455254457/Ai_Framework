"""
模块名称：负载均衡器模块
功能描述：提供负载均衡算法，支持轮询、加权轮询、最少连接等策略
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - LoadBalancer: 负载均衡器
    - LoadBalanceStrategy: 负载均衡策略枚举
    - RoundRobinStrategy: 轮询策略
    - WeightedRoundRobinStrategy: 加权轮询策略
    - LeastConnectionsStrategy: 最少连接策略

依赖模块：
    - core.llm.adapters.base: 适配器基类
    - typing: 类型注解
    - enum: 枚举类型
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional
from core.llm.adapters.base import BaseLLMAdapter


class LoadBalanceStrategy(str, Enum):
    """负载均衡策略枚举"""
    ROUND_ROBIN = "round_robin"  # 轮询
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"  # 加权轮询
    LEAST_CONNECTIONS = "least_connections"  # 最少连接
    RANDOM = "random"  # 随机


class LoadBalanceStrategyBase(ABC):
    """负载均衡策略基类"""
    
    @abstractmethod
    def select_adapter(
        self,
        adapters: List[BaseLLMAdapter],
        state: Dict[str, Any],
    ) -> Optional[BaseLLMAdapter]:
        """
        选择适配器
        
        参数:
            adapters: 候选适配器列表
            state: 负载均衡状态（用于跟踪请求计数、连接数等）
        
        返回:
            选中的适配器，如果无法选择返回None
        """
        pass


class RoundRobinStrategy(LoadBalanceStrategyBase):
    """轮询策略"""
    
    def select_adapter(
        self,
        adapters: List[BaseLLMAdapter],
        state: Dict[str, Any],
    ) -> Optional[BaseLLMAdapter]:
        """轮询选择适配器"""
        if not adapters:
            return None
        
        # 获取当前索引
        current_index = state.get("round_robin_index", 0)
        
        # 选择适配器
        selected = adapters[current_index % len(adapters)]
        
        # 更新索引
        state["round_robin_index"] = (current_index + 1) % len(adapters)
        
        return selected


class WeightedRoundRobinStrategy(LoadBalanceStrategyBase):
    """加权轮询策略"""
    
    def select_adapter(
        self,
        adapters: List[BaseLLMAdapter],
        state: Dict[str, Any],
    ) -> Optional[BaseLLMAdapter]:
        """加权轮询选择适配器"""
        if not adapters:
            return None
        
        # 获取权重信息（从适配器能力或配置中获取）
        weights = state.get("weights", {})
        if not weights:
            # 如果没有权重配置，使用轮询
            return RoundRobinStrategy().select_adapter(adapters, state)
        
        # 计算总权重
        total_weight = sum(weights.get(adapter.name, 1) for adapter in adapters)
        if total_weight == 0:
            return adapters[0] if adapters else None
        
        # 获取当前权重累计值
        current_weight = state.get("weighted_round_robin_weight", 0)
        
        # 选择适配器（基于权重）
        for adapter in adapters:
            weight = weights.get(adapter.name, 1)
            if current_weight < weight:
                # 更新权重累计值
                state["weighted_round_robin_weight"] = (current_weight + 1) % total_weight
                return adapter
            current_weight -= weight
        
        # 如果没找到，重置并返回第一个
        state["weighted_round_robin_weight"] = 0
        return adapters[0] if adapters else None


class LeastConnectionsStrategy(LoadBalanceStrategyBase):
    """最少连接策略"""
    
    def select_adapter(
        self,
        adapters: List[BaseLLMAdapter],
        state: Dict[str, Any],
    ) -> Optional[BaseLLMAdapter]:
        """选择连接数最少的适配器"""
        if not adapters:
            return None
        
        # 获取连接数统计
        connections = state.get("connections", {})
        
        # 找到连接数最少的适配器
        best_adapter = None
        min_connections = float('inf')
        
        for adapter in adapters:
            adapter_name = adapter.name
            connection_count = connections.get(adapter_name, 0)
            if connection_count < min_connections:
                min_connections = connection_count
                best_adapter = adapter
        
        return best_adapter or (adapters[0] if adapters else None)


class RandomStrategy(LoadBalanceStrategyBase):
    """随机策略"""
    
    def select_adapter(
        self,
        adapters: List[BaseLLMAdapter],
        state: Dict[str, Any],
    ) -> Optional[BaseLLMAdapter]:
        """随机选择适配器"""
        if not adapters:
            return None
        
        import random
        return random.choice(adapters)


class LoadBalancer:
    """
    负载均衡器
    
    提供多种负载均衡算法，用于在多个适配器之间分配请求。
    
    特性：
        - 轮询策略
        - 加权轮询策略
        - 最少连接策略
        - 随机策略
    
    示例:
        >>> balancer = LoadBalancer(LoadBalanceStrategy.ROUND_ROBIN)
        >>> adapter = balancer.select(adapters, state)
    """
    
    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN) -> None:
        """
        初始化负载均衡器
        
        参数:
            strategy: 负载均衡策略
        """
        self._strategy = strategy
        self._strategy_impl: LoadBalanceStrategyBase = self._create_strategy(strategy)
        self._state: Dict[str, Any] = {
            "round_robin_index": 0,
            "weighted_round_robin_weight": 0,
            "connections": {},
            "request_counts": {},
        }
    
    def _create_strategy(self, strategy: LoadBalanceStrategy) -> LoadBalanceStrategyBase:
        """创建策略实现"""
        strategies = {
            LoadBalanceStrategy.ROUND_ROBIN: RoundRobinStrategy(),
            LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN: WeightedRoundRobinStrategy(),
            LoadBalanceStrategy.LEAST_CONNECTIONS: LeastConnectionsStrategy(),
            LoadBalanceStrategy.RANDOM: RandomStrategy(),
        }
        return strategies.get(strategy, RoundRobinStrategy())
    
    def select(
        self,
        adapters: List[BaseLLMAdapter],
    ) -> Optional[BaseLLMAdapter]:
        """
        选择适配器
        
        参数:
            adapters: 候选适配器列表
        
        返回:
            选中的适配器
        """
        return self._strategy_impl.select_adapter(adapters, self._state)
    
    def record_request(self, adapter_name: str) -> None:
        """
        记录请求
        
        参数:
            adapter_name: 适配器名称
        """
        self._state["request_counts"][adapter_name] = \
            self._state["request_counts"].get(adapter_name, 0) + 1
    
    def record_connection(self, adapter_name: str, increment: int = 1) -> None:
        """
        记录连接数变化
        
        参数:
            adapter_name: 适配器名称
            increment: 连接数增量（正数表示增加，负数表示减少）
        """
        current = self._state["connections"].get(adapter_name, 0)
        self._state["connections"][adapter_name] = max(0, current + increment)
    
    def set_weights(self, weights: Dict[str, int]) -> None:
        """
        设置适配器权重（用于加权轮询）
        
        参数:
            weights: 权重字典 {adapter_name: weight}
        """
        self._state["weights"] = weights
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取负载均衡统计信息
        
        返回:
            统计信息字典
        """
        return {
            "strategy": self._strategy.value,
            "request_counts": self._state["request_counts"].copy(),
            "connections": self._state["connections"].copy(),
        }
    
    def reset_statistics(self) -> None:
        """重置统计信息"""
        self._state["request_counts"].clear()
        self._state["connections"].clear()
