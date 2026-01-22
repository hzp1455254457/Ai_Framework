"""
测试模块：多Agent协作测试
功能描述：测试AgentOrchestrator和任务分配策略的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from core.agent.collaboration import (
    AgentOrchestrator,
    RoundRobinStrategy,
    LoadBalancingStrategy,
    SpecializationStrategy,
    DistributionStrategy,
    CollaborationError,
    AgentInfo,
)


@pytest.mark.asyncio
class TestTaskDistributionStrategy:
    """任务分配策略测试类"""
    
    async def test_round_robin_strategy(self):
        """测试轮询分配策略"""
        # Arrange
        strategy = RoundRobinStrategy()
        agents = [
            AgentInfo(agent_id="agent1", agent=MagicMock()),
            AgentInfo(agent_id="agent2", agent=MagicMock()),
        ]
        
        # Act
        selected1 = await strategy.select_agent(agents, "任务1")
        selected2 = await strategy.select_agent(agents, "任务2")
        selected3 = await strategy.select_agent(agents, "任务3")
        
        # Assert
        assert selected1.agent_id == "agent1"
        assert selected2.agent_id == "agent2"
        assert selected3.agent_id == "agent1"  # 轮询回到第一个
    
    async def test_load_balancing_strategy(self):
        """测试负载均衡分配策略"""
        # Arrange
        strategy = LoadBalancingStrategy()
        agents = [
            AgentInfo(agent_id="agent1", agent=MagicMock(), current_load=2),
            AgentInfo(agent_id="agent2", agent=MagicMock(), current_load=1),
        ]
        
        # Act
        selected = await strategy.select_agent(agents, "任务")
        
        # Assert
        assert selected.agent_id == "agent2"  # 负载最低
    
    async def test_specialization_strategy(self):
        """测试专业分工分配策略"""
        # Arrange
        strategy = SpecializationStrategy()
        agents = [
            AgentInfo(agent_id="agent1", agent=MagicMock(), specialization="weather"),
            AgentInfo(agent_id="agent2", agent=MagicMock(), specialization="code"),
        ]
        
        # Act
        selected = await strategy.select_agent(agents, "查询天气")
        
        # Assert
        assert selected.agent_id == "agent1"  # 匹配专业标签


@pytest.mark.asyncio
class TestAgentOrchestrator:
    """AgentOrchestrator测试类"""
    
    async def test_add_and_remove_agent(self):
        """测试添加和移除Agent"""
        # Arrange
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        mock_agent = MagicMock()
        
        # Act
        orchestrator.add_agent("agent1", mock_agent, specialization="test")
        orchestrator.remove_agent("agent1")
        
        # Assert
        assert "agent1" not in orchestrator._agents
    
    async def test_set_strategy(self):
        """测试设置分配策略"""
        # Arrange
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        # Act
        orchestrator.set_strategy(DistributionStrategy.LOAD_BALANCING)
        
        # Assert
        assert isinstance(orchestrator._strategy, LoadBalancingStrategy)
    
    async def test_execute_task(self):
        """测试执行任务"""
        # Arrange
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        mock_agent = MagicMock()
        mock_agent.run_task = AsyncMock(return_value={
            "content": "测试结果",
            "tool_calls": [],
            "iterations": 1,
            "metadata": {},
        })
        
        orchestrator.add_agent("agent1", mock_agent)
        
        # Act
        result = await orchestrator.execute_task("测试任务")
        
        # Assert
        assert result["content"] == "测试结果"
        mock_agent.run_task.assert_called_once()
    
    def test_aggregate_results(self):
        """测试结果聚合"""
        # Arrange
        orchestrator = AgentOrchestrator()
        results = [
            {"content": "结果1", "tool_calls": [], "iterations": 1},
            {"content": "结果2", "tool_calls": [], "iterations": 1},
        ]
        
        # Act
        aggregated = orchestrator.aggregate_results(results, method="merge")
        
        # Assert
        assert "结果1" in aggregated["content"]
        assert "结果2" in aggregated["content"]
        assert aggregated["metadata"]["aggregated_from"] == 2
    
    def test_get_agent_status(self):
        """测试获取Agent状态"""
        # Arrange
        orchestrator = AgentOrchestrator()
        mock_agent = MagicMock()
        orchestrator.add_agent("agent1", mock_agent, specialization="test")
        orchestrator._agents["agent1"].current_load = 2
        
        # Act
        status = orchestrator.get_agent_status()
        
        # Assert
        assert len(status) == 1
        assert status[0]["agent_id"] == "agent1"
        assert status[0]["current_load"] == 2
