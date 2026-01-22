"""
测试模块：任务规划器测试
功能描述：测试Planner和LLMPlanner的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.agent.planner import Planner, LLMPlanner, Plan, PlanStep, PlannerError


@pytest.mark.asyncio
class TestPlanStep:
    """PlanStep测试类"""
    
    def test_plan_step_creation(self):
        """测试规划步骤创建"""
        step = PlanStep(
            step_id="step_1",
            description="步骤描述",
            dependencies=["step_0"],
            required_tools=["tool1"],
            expected_output="预期输出",
        )
        
        assert step.step_id == "step_1"
        assert step.description == "步骤描述"
        assert "step_0" in step.dependencies
        assert "tool1" in step.required_tools


@pytest.mark.asyncio
class TestPlan:
    """Plan测试类"""
    
    def test_plan_creation(self):
        """测试规划创建"""
        steps = [
            PlanStep(step_id="step_1", description="步骤1"),
            PlanStep(step_id="step_2", description="步骤2", dependencies=["step_1"]),
        ]
        plan = Plan(task="测试任务", steps=steps)
        
        assert plan.task == "测试任务"
        assert len(plan.steps) == 2
    
    def test_get_step(self):
        """测试获取步骤"""
        step = PlanStep(step_id="step_1", description="步骤1")
        plan = Plan(task="测试", steps=[step])
        
        assert plan.get_step("step_1") == step
        assert plan.get_step("nonexistent") is None
    
    def test_get_ready_steps(self):
        """测试获取可执行步骤"""
        step1 = PlanStep(step_id="step_1", description="步骤1", dependencies=[])
        step2 = PlanStep(step_id="step_2", description="步骤2", dependencies=["step_1"])
        plan = Plan(task="测试", steps=[step1, step2])
        
        # 没有完成任何步骤时，只有step1可执行
        ready = plan.get_ready_steps([])
        assert len(ready) == 1
        assert ready[0].step_id == "step_1"
        
        # 完成step1后，step2可执行
        ready = plan.get_ready_steps(["step_1"])
        assert len(ready) == 1
        assert ready[0].step_id == "step_2"


@pytest.mark.asyncio
class TestLLMPlanner:
    """LLMPlanner测试类"""
    
    async def test_plan_simple_task(self):
        """测试规划简单任务"""
        # Arrange
        from core.llm.models import LLMResponse
        
        mock_llm_service = MagicMock()
        mock_llm_service.chat = AsyncMock(return_value=LLMResponse(
            content='{"steps": [{"step_id": "step_1", "description": "执行步骤1", "dependencies": [], "required_tools": [], "expected_output": "完成"}]}',
            model="test-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        ))
        
        planner = LLMPlanner(mock_llm_service, {})
        
        # Act
        plan = await planner.plan("测试任务")
        
        # Assert
        assert plan.task == "测试任务"
        assert len(plan.steps) == 1
        assert plan.steps[0].step_id == "step_1"
        assert len(plan.execution_order) == 1
    
    async def test_optimize_execution_order(self):
        """测试优化执行顺序"""
        # Arrange
        from core.llm.models import LLMResponse
        
        mock_llm_service = MagicMock()
        mock_llm_service.chat = AsyncMock(return_value=LLMResponse(
            content='{"steps": [{"step_id": "step_1", "description": "步骤1", "dependencies": []}, {"step_id": "step_2", "description": "步骤2", "dependencies": ["step_1"]}]}',
            model="test-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        ))
        
        planner = LLMPlanner(mock_llm_service, {})
        
        # Act
        plan = await planner.plan("测试任务")
        
        # Assert
        assert plan.execution_order == ["step_1", "step_2"]  # step_1应该在step_2之前
    
    async def test_adjust_plan(self):
        """测试动态调整规划"""
        # Arrange
        from core.llm.models import LLMResponse
        
        mock_llm_service = MagicMock()
        mock_llm_service.chat = AsyncMock(return_value=LLMResponse(
            content='{"steps": [{"step_id": "step_1", "description": "调整后的步骤", "dependencies": []}]}',
            model="test-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        ))
        
        planner = LLMPlanner(mock_llm_service, {})
        original_plan = Plan(
            task="测试任务",
            steps=[
                PlanStep(step_id="step_1", description="原始步骤1"),
                PlanStep(step_id="step_2", description="原始步骤2"),
            ],
        )
        
        # Act
        adjusted_plan = await planner.adjust_plan(
            original_plan,
            completed_steps=["step_1"],
            step_results={"step_1": "结果1"},
            error=Exception("测试错误"),
        )
        
        # Assert
        assert adjusted_plan.task == original_plan.task
        assert len(adjusted_plan.steps) == 1
