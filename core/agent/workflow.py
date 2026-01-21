"""
模块名称：工作流模块
功能描述：提供基础工作流编排能力
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - Workflow: 工作流类
    - WorkflowError: 工作流错误异常

依赖模块：
    - typing: 类型注解
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Awaitable


class WorkflowError(Exception):
    """工作流模块异常基类"""
    pass


class WorkflowStep:
    """
    工作流步骤
    
    表示工作流中的一个执行步骤。
    """
    
    def __init__(
        self,
        name: str,
        func: Callable[..., Awaitable[Any]],
        description: Optional[str] = None,
    ) -> None:
        """
        初始化工作流步骤
        
        参数:
            name: 步骤名称
            func: 异步执行函数
            description: 步骤描述（可选）
        """
        self.name: str = name
        self.func: Callable[..., Awaitable[Any]] = func
        self.description: Optional[str] = description
    
    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        执行步骤
        
        参数:
            context: 工作流上下文（字典格式，可在步骤间传递数据）
        
        返回:
            步骤执行结果（会被添加到context中）
        """
        try:
            result = await self.func(context)
            # 将结果添加到上下文
            context[self.name] = result
            return result
        except Exception as e:
            raise WorkflowError(f"步骤执行失败 [{self.name}]: {e}") from e


class Workflow:
    """
    工作流
    
    提供基础的工作流编排能力，支持线性步骤执行和错误处理。
    
    特性：
        - 线性步骤执行
        - 错误处理
        - 上下文传递
    
    示例：
        >>> async def step1(context):
        ...     return "step1_result"
        >>> async def step2(context):
        ...     return context["step1"] + "_step2"
        >>> workflow = Workflow()
        >>> workflow.add_step("step1", step1)
        >>> workflow.add_step("step2", step2)
        >>> result = await workflow.execute()
    """
    
    def __init__(self) -> None:
        """初始化工作流"""
        self._steps: List[WorkflowStep] = []
        self._context: Dict[str, Any] = {}
    
    def add_step(
        self,
        name: str,
        func: Callable[..., Awaitable[Any]],
        description: Optional[str] = None,
    ) -> None:
        """
        添加工作流步骤
        
        参数:
            name: 步骤名称
            func: 异步执行函数
            description: 步骤描述（可选）
        """
        step = WorkflowStep(name, func, description)
        self._steps.append(step)
    
    async def execute(
        self,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        执行工作流
        
        参数:
            initial_context: 初始上下文（可选）
        
        返回:
            最终上下文（包含所有步骤的执行结果）
        
        异常:
            WorkflowError: 工作流执行失败时抛出
        """
        # 初始化上下文
        self._context = initial_context.copy() if initial_context else {}
        
        try:
            # 按顺序执行所有步骤
            for step in self._steps:
                await step.execute(self._context)
            
            return self._context.copy()
        except Exception as e:
            raise WorkflowError(f"工作流执行失败: {e}") from e
    
    def clear(self) -> None:
        """清空工作流步骤"""
        self._steps.clear()
        self._context.clear()
    
    @property
    def step_count(self) -> int:
        """获取步骤数量"""
        return len(self._steps)
