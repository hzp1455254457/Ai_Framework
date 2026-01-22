"""
模块名称：多Agent协作模块
功能描述：提供多Agent协同执行任务的能力
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - AgentOrchestrator: Agent编排器
    - TaskDistributionStrategy: 任务分配策略基类
    - RoundRobinStrategy: 轮询分配策略
    - LoadBalancingStrategy: 负载均衡分配策略
    - SpecializationStrategy: 专业分工分配策略

依赖模块：
    - core.agent.engine: AgentEngine
    - typing: 类型注解
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


class CollaborationError(Exception):
    """协作模块异常基类"""
    pass


class DistributionStrategy(str, Enum):
    """任务分配策略枚举"""
    ROUND_ROBIN = "round_robin"
    LOAD_BALANCING = "load_balancing"
    SPECIALIZATION = "specialization"


@dataclass
class AgentInfo:
    """Agent信息"""
    agent_id: str
    agent: Any  # AgentEngine类型，避免循环导入
    specialization: Optional[str] = None  # 专业标签
    current_load: int = 0  # 当前负载（正在执行的任务数）


class TaskDistributionStrategy(ABC):
    """任务分配策略基类"""
    
    @abstractmethod
    async def select_agent(
        self,
        agents: List[AgentInfo],
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentInfo:
        """
        选择执行任务的Agent
        
        参数:
            agents: Agent列表
            task: 任务描述
            context: 上下文信息（可选）
        
        返回:
            选中的Agent信息
        """
        pass


class RoundRobinStrategy(TaskDistributionStrategy):
    """轮询分配策略"""
    
    def __init__(self) -> None:
        """初始化轮询策略"""
        self._current_index = 0
    
    async def select_agent(
        self,
        agents: List[AgentInfo],
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentInfo:
        """轮询选择Agent"""
        if not agents:
            raise CollaborationError("没有可用的Agent")
        
        agent = agents[self._current_index]
        self._current_index = (self._current_index + 1) % len(agents)
        return agent


class LoadBalancingStrategy(TaskDistributionStrategy):
    """负载均衡分配策略"""
    
    async def select_agent(
        self,
        agents: List[AgentInfo],
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentInfo:
        """选择负载最低的Agent"""
        if not agents:
            raise CollaborationError("没有可用的Agent")
        
        # 选择负载最低的Agent
        selected = min(agents, key=lambda a: a.current_load)
        return selected


class SpecializationStrategy(TaskDistributionStrategy):
    """专业分工分配策略"""
    
    async def select_agent(
        self,
        agents: List[AgentInfo],
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentInfo:
        """根据专业标签选择Agent"""
        if not agents:
            raise CollaborationError("没有可用的Agent")
        
        # 从任务描述中提取关键词，匹配专业标签
        # 这里使用简单的关键词匹配，实际可以使用更复杂的NLP方法
        task_lower = task.lower()
        
        # 优先选择有匹配专业标签的Agent
        for agent in agents:
            if agent.specialization and agent.specialization.lower() in task_lower:
                return agent
        
        # 如果没有匹配的，选择负载最低的
        return min(agents, key=lambda a: a.current_load)


class AgentOrchestrator:
    """
    Agent编排器
    
    管理多个Agent实例，协调任务分配和结果聚合。
    
    特性:
        - 多Agent管理
        - 任务分配策略（轮询、负载均衡、专业分工）
        - 结果聚合
        - 冲突解决
    
    示例:
        >>> orchestrator = AgentOrchestrator(config)
        >>> await orchestrator.initialize()
        >>> orchestrator.add_agent("agent1", engine1, specialization="weather")
        >>> result = await orchestrator.execute_task("查询北京天气")
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化编排器
        
        参数:
            config: 配置字典
        """
        self._config = config or {}
        self._agents: Dict[str, AgentInfo] = {}
        self._strategy: TaskDistributionStrategy = RoundRobinStrategy()
        self._strategy_type: DistributionStrategy = DistributionStrategy.ROUND_ROBIN
    
    async def initialize(self) -> None:
        """初始化编排器"""
        strategy_name = self._config.get("collaboration", {}).get("strategy", "round_robin")
        self.set_strategy(DistributionStrategy(strategy_name))
    
    def add_agent(
        self,
        agent_id: str,
        agent: Any,  # AgentEngine类型
        specialization: Optional[str] = None,
    ) -> None:
        """
        添加Agent
        
        参数:
            agent_id: Agent ID
            agent: AgentEngine实例
            specialization: 专业标签（可选）
        """
        self._agents[agent_id] = AgentInfo(
            agent_id=agent_id,
            agent=agent,
            specialization=specialization,
        )
    
    def remove_agent(self, agent_id: str) -> None:
        """移除Agent"""
        if agent_id in self._agents:
            del self._agents[agent_id]
    
    def set_strategy(self, strategy: DistributionStrategy) -> None:
        """
        设置任务分配策略
        
        参数:
            strategy: 分配策略
        """
        self._strategy_type = strategy
        if strategy == DistributionStrategy.ROUND_ROBIN:
            self._strategy = RoundRobinStrategy()
        elif strategy == DistributionStrategy.LOAD_BALANCING:
            self._strategy = LoadBalancingStrategy()
        elif strategy == DistributionStrategy.SPECIALIZATION:
            self._strategy = SpecializationStrategy()
    
    async def execute_task(
        self,
        task: str,
        conversation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        执行任务
        
        将任务分配给合适的Agent执行，并聚合结果。
        
        参数:
            task: 任务描述
            conversation_id: 对话ID（可选）
            **kwargs: 其他参数
        
        返回:
            执行结果字典
        """
        if not self._agents:
            raise CollaborationError("没有可用的Agent")
        
        # 选择Agent
        agents_list = list(self._agents.values())
        selected_agent = await self._strategy.select_agent(agents_list, task, kwargs.get("context"))
        
        # 更新负载
        selected_agent.current_load += 1
        
        try:
            # 执行任务
            result = await selected_agent.agent.run_task(
                task=task,
                conversation_id=conversation_id,
                **kwargs,
            )
            return result
        finally:
            # 减少负载
            selected_agent.current_load = max(0, selected_agent.current_load - 1)
    
    async def execute_tasks_parallel(
        self,
        tasks: List[str],
        conversation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        并行执行多个任务
        
        参数:
            tasks: 任务列表
            conversation_id: 对话ID（可选）
            **kwargs: 其他参数
        
        返回:
            执行结果列表
        """
        import asyncio
        
        # 为每个任务选择Agent并并行执行
        async def execute_single_task(task: str) -> Dict[str, Any]:
            agents_list = list(self._agents.values())
            selected_agent = await self._strategy.select_agent(agents_list, task, kwargs.get("context"))
            selected_agent.current_load += 1
            try:
                return await selected_agent.agent.run_task(
                    task=task,
                    conversation_id=conversation_id,
                    **kwargs,
                )
            finally:
                selected_agent.current_load = max(0, selected_agent.current_load - 1)
        
        # 并行执行所有任务
        results = await asyncio.gather(*[execute_single_task(task) for task in tasks])
        return list(results)
    
    def aggregate_results(
        self,
        results: List[Dict[str, Any]],
        method: str = "merge",
    ) -> Dict[str, Any]:
        """
        聚合多个执行结果
        
        参数:
            results: 结果列表
            method: 聚合方法（merge/vote/llm_arbitration）
        
        返回:
            聚合后的结果
        """
        if not results:
            return {}
        
        if method == "merge":
            # 简单合并：将所有内容合并
            aggregated_content = "\n\n".join([r.get("content", "") for r in results])
            return {
                "content": aggregated_content,
                "tool_calls": [tc for r in results for tc in r.get("tool_calls", [])],
                "iterations": sum(r.get("iterations", 0) for r in results),
                "metadata": {
                    "aggregated_from": len(results),
                    "method": method,
                },
            }
        elif method == "vote":
            # 投票：选择出现次数最多的结果（简化实现）
            # 实际可以使用更复杂的投票机制
            return results[0]  # 占位实现
        else:
            # 默认返回第一个结果
            return results[0]
    
    def get_agent_status(self) -> List[Dict[str, Any]]:
        """获取所有Agent的状态"""
        return [
            {
                "agent_id": agent.agent_id,
                "specialization": agent.specialization,
                "current_load": agent.current_load,
            }
            for agent in self._agents.values()
        ]
