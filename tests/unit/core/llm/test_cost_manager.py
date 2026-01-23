"""
测试模块：成本管理器测试
功能描述：测试CostManager的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from core.llm.cost_manager import CostManager, CostRecord, TokenUsage, CostBudget


@pytest.mark.asyncio
class TestCostManager:
    """CostManager测试类"""
    
    @pytest.fixture
    def cost_manager(self):
        """创建成本管理器fixture"""
        config = {
            "daily_budget": 10.0,
            "monthly_budget": 300.0,
            "alert_threshold": 0.8,
            "budget_enabled": True,
        }
        return CostManager(config)
    
    async def test_cost_manager_initialization(self):
        """测试成本管理器初始化"""
        # Arrange
        config = {"daily_budget": 10.0}
        
        # Act
        manager = CostManager(config)
        
        # Assert
        assert manager._budget.daily_budget == 10.0
        assert manager._budget.enabled is False  # 默认禁用
    
    async def test_record_usage(self, cost_manager):
        """测试记录Token使用和成本"""
        # Arrange
        usage = {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }
        cost_info = {"input": 0.001, "output": 0.002}
        
        # Act
        record = await cost_manager.record_usage(
            adapter_name="openai-adapter",
            model="gpt-3.5-turbo",
            usage=usage,
            cost_info=cost_info,
        )
        
        # Assert
        assert record is not None
        assert record.adapter_name == "openai-adapter"
        assert record.model == "gpt-3.5-turbo"
        assert record.token_usage.prompt_tokens == 100
        assert record.token_usage.completion_tokens == 50
        assert record.input_cost > 0
        assert record.output_cost > 0
        assert record.total_cost == record.input_cost + record.output_cost
    
    async def test_get_statistics(self, cost_manager):
        """测试获取成本统计信息"""
        # Arrange
        usage1 = {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        usage2 = {"prompt_tokens": 200, "completion_tokens": 100, "total_tokens": 300}
        cost_info = {"input": 0.001, "output": 0.002}
        
        # 记录两次使用
        await cost_manager.record_usage("adapter1", "model1", usage1, cost_info)
        await cost_manager.record_usage("adapter2", "model2", usage2, cost_info)
        
        # Act
        stats = await cost_manager.get_statistics()
        
        # Assert
        assert stats["total_cost"] > 0
        assert stats["total_tokens"] == 450
        assert stats["request_count"] == 2
        assert "adapter1" in stats["adapter_stats"]
        assert "adapter2" in stats["adapter_stats"]
        assert "model1" in stats["model_stats"]
        assert "model2" in stats["model_stats"]
    
    async def test_get_statistics_with_filters(self, cost_manager):
        """测试带过滤条件的统计"""
        # Arrange
        usage = {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        cost_info = {"input": 0.001, "output": 0.002}
        
        await cost_manager.record_usage("adapter1", "model1", usage, cost_info)
        await cost_manager.record_usage("adapter2", "model2", usage, cost_info)
        
        # Act - 按适配器过滤
        stats = await cost_manager.get_statistics(adapter_name="adapter1")
        
        # Assert
        assert stats["request_count"] == 1
        assert "adapter1" in stats["adapter_stats"]
        assert "adapter2" not in stats["adapter_stats"]
    
    async def test_get_optimization_suggestions(self, cost_manager):
        """测试获取成本优化建议"""
        # Arrange
        usage = {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        cost_info = {"input": 0.001, "output": 0.002}
        
        await cost_manager.record_usage("adapter1", "model1", usage, cost_info)
        
        # Act
        suggestions = await cost_manager.get_optimization_suggestions([])
        
        # Assert
        assert isinstance(suggestions, list)
    
    async def test_set_budget(self, cost_manager):
        """测试设置成本预算"""
        # Act
        cost_manager.set_budget(
            daily_budget=20.0,
            monthly_budget=600.0,
            alert_threshold=0.9,
            enabled=True,
        )
        
        # Assert
        assert cost_manager._budget.daily_budget == 20.0
        assert cost_manager._budget.monthly_budget == 600.0
        assert cost_manager._budget.alert_threshold == 0.9
        assert cost_manager._budget.enabled is True
    
    async def test_clear_records(self, cost_manager):
        """测试清理历史记录"""
        # Arrange
        usage = {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        cost_info = {"input": 0.001, "output": 0.002}
        
        await cost_manager.record_usage("adapter1", "model1", usage, cost_info)
        assert len(cost_manager._records) == 1
        
        # Act
        count = await cost_manager.clear_records()
        
        # Assert
        assert count == 1
        assert len(cost_manager._records) == 0
    
    async def test_clear_records_before_date(self, cost_manager):
        """测试清理指定日期之前的记录"""
        # Arrange
        usage = {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        cost_info = {"input": 0.001, "output": 0.002}
        
        await cost_manager.record_usage("adapter1", "model1", usage, cost_info)
        
        # 设置一个未来的日期
        future_date = datetime.now() + timedelta(days=1)
        
        # Act
        count = await cost_manager.clear_records(before_date=future_date)
        
        # Assert
        assert count == 1
        assert len(cost_manager._records) == 0
