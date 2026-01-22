"""
模块名称：任务规划器模块
功能描述：提供任务分解和步骤规划能力
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - Planner: 规划器基类
    - LLMPlanner: 基于LLM的规划器实现
    - Plan: 规划结果类
    - PlanStep: 规划步骤类

依赖模块：
    - core.llm.service: LLM服务
    - typing: 类型注解
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


class PlannerError(Exception):
    """规划器异常基类"""
    pass


@dataclass
class PlanStep:
    """
    规划步骤
    
    表示任务规划中的一个执行步骤。
    
    属性:
        step_id: 步骤ID（唯一标识）
        description: 步骤描述
        dependencies: 依赖的步骤ID列表
        required_tools: 所需工具列表（可选）
        expected_output: 预期输出描述（可选）
    """
    
    step_id: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    expected_output: Optional[str] = None


@dataclass
class Plan:
    """
    任务规划
    
    包含任务分解后的步骤列表和执行顺序。
    
    属性:
        task: 原始任务描述
        steps: 步骤列表
        execution_order: 优化后的执行顺序（步骤ID列表）
    """
    
    task: str
    steps: List[PlanStep] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    
    def get_step(self, step_id: str) -> Optional[PlanStep]:
        """根据步骤ID获取步骤"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_ready_steps(self, completed_steps: List[str]) -> List[PlanStep]:
        """
        获取可以执行的步骤（所有依赖已完成）
        
        参数:
            completed_steps: 已完成的步骤ID列表
        
        返回:
            可以执行的步骤列表
        """
        ready = []
        for step in self.steps:
            if step.step_id in completed_steps:
                continue
            # 检查所有依赖是否已完成
            if all(dep in completed_steps for dep in step.dependencies):
                ready.append(step)
        return ready


class Planner(ABC):
    """
    规划器基类
    
    定义任务规划器的接口，支持任务分解和步骤规划。
    """
    
    @abstractmethod
    async def plan(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Plan:
        """
        生成任务规划
        
        参数:
            task: 任务描述
            context: 上下文信息（可选）
        
        返回:
            任务规划对象
        
        异常:
            PlannerError: 规划失败时抛出
        """
        pass
    
    @abstractmethod
    async def adjust_plan(
        self,
        plan: Plan,
        completed_steps: List[str],
        step_results: Dict[str, Any],
        error: Optional[Exception] = None,
    ) -> Plan:
        """
        动态调整规划
        
        根据执行结果调整后续步骤。
        
        参数:
            plan: 原始规划
            completed_steps: 已完成的步骤ID列表
            step_results: 步骤执行结果字典
            error: 错误信息（如果有）
        
        返回:
            调整后的规划对象
        """
        pass


class LLMPlanner(Planner):
    """
    基于LLM的规划器
    
    使用LLM服务进行任务分解和步骤规划。
    
    特性:
        - LLM驱动的任务分解
        - 步骤依赖关系识别
        - 执行顺序优化
        - 动态规划调整
    
    示例:
        >>> planner = LLMPlanner(llm_service, config)
        >>> await planner.initialize()
        >>> plan = await planner.plan("开发一个Web应用")
    """
    
    def __init__(
        self,
        llm_service: Any,  # LLMService类型，避免循环导入
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化LLM规划器
        
        参数:
            llm_service: LLM服务实例
            config: 配置字典（可选）
        """
        self._llm_service = llm_service
        self._config = config or {}
        self._plan_cache: Dict[str, Plan] = {}
        self._enable_cache: bool = self._config.get("planner", {}).get("enable_cache", True)
    
    async def plan(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Plan:
        """
        生成任务规划
        
        使用LLM将任务分解为步骤列表。
        
        参数:
            task: 任务描述
            context: 上下文信息（可选）
        
        返回:
            任务规划对象
        """
        # 检查缓存
        if self._enable_cache and task in self._plan_cache:
            return self._plan_cache[task]
        
        try:
            # 构建规划提示词
            planning_prompt = self._build_planning_prompt(task, context)
            
            # 调用LLM生成规划
            messages = [
                {
                    "role": "system",
                    "content": "你是一个任务规划专家，擅长将复杂任务分解为可执行的步骤序列。"
                },
                {
                    "role": "user",
                    "content": planning_prompt
                }
            ]
            
            response = await self._llm_service.chat(
                messages=messages,
                model=self._config.get("planner", {}).get("model"),
                temperature=0.3,  # 较低温度以获得更稳定的规划
            )
            
            # 解析LLM响应为规划对象
            plan = self._parse_plan_response(task, response.content)
            
            # 优化执行顺序
            plan.execution_order = self._optimize_execution_order(plan)
            
            # 缓存规划结果
            if self._enable_cache:
                self._plan_cache[task] = plan
            
            return plan
        
        except Exception as e:
            raise PlannerError(f"任务规划失败: {e}") from e
    
    async def adjust_plan(
        self,
        plan: Plan,
        completed_steps: List[str],
        step_results: Dict[str, Any],
        error: Optional[Exception] = None,
    ) -> Plan:
        """
        动态调整规划
        
        根据执行结果调整后续步骤。
        
        参数:
            plan: 原始规划
            completed_steps: 已完成的步骤ID列表
            step_results: 步骤执行结果字典
            error: 错误信息（如果有）
        
        返回:
            调整后的规划对象
        """
        # 获取剩余未完成的步骤
        remaining_steps = [
            step for step in plan.steps
            if step.step_id not in completed_steps
        ]
        
        if not remaining_steps:
            return plan  # 所有步骤已完成，无需调整
        
        # 如果有错误，需要重新规划
        if error:
            try:
                # 构建调整提示词
                adjustment_prompt = self._build_adjustment_prompt(
                    plan, completed_steps, step_results, error
                )
                
                messages = [
                    {
                        "role": "system",
                        "content": "你是一个任务规划专家，擅长根据执行结果调整任务规划。"
                    },
                    {
                        "role": "user",
                        "content": adjustment_prompt
                    }
                ]
                
                response = await self._llm_service.chat(
                    messages=messages,
                    model=self._config.get("planner", {}).get("model"),
                    temperature=0.3,
                )
                
                # 解析调整后的规划
                adjusted_plan = self._parse_plan_response(plan.task, response.content)
                adjusted_plan.execution_order = self._optimize_execution_order(adjusted_plan)
                
                return adjusted_plan
            
            except Exception as e:
                # 如果调整失败，返回原始规划
                return plan
        
        # 没有错误，只需更新执行顺序
        plan.execution_order = self._optimize_execution_order(plan)
        return plan
    
    def _build_planning_prompt(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """构建规划提示词"""
        prompt = f"""请将以下任务分解为可执行的步骤序列。

任务：{task}

要求：
1. 将任务分解为3-10个清晰的步骤
2. 每个步骤应该有明确的描述
3. 识别步骤之间的依赖关系
4. 如果步骤需要特定工具，请列出所需工具
5. 描述每个步骤的预期输出

请以JSON格式返回规划结果，格式如下：
{{
    "steps": [
        {{
            "step_id": "step_1",
            "description": "步骤描述",
            "dependencies": [],
            "required_tools": [],
            "expected_output": "预期输出描述"
        }},
        ...
    ]
}}

只返回JSON，不要包含其他文本。"""
        
        if context:
            prompt += f"\n\n上下文信息：{json.dumps(context, ensure_ascii=False)}"
        
        return prompt
    
    def _build_adjustment_prompt(
        self,
        plan: Plan,
        completed_steps: List[str],
        step_results: Dict[str, Any],
        error: Exception,
    ) -> str:
        """构建调整提示词"""
        prompt = f"""原始任务：{plan.task}

已完成步骤：
{json.dumps([s.step_id for s in plan.steps if s.step_id in completed_steps], ensure_ascii=False)}

步骤执行结果：
{json.dumps(step_results, ensure_ascii=False)}

遇到的错误：
{str(error)}

请根据以上信息重新规划剩余任务，调整步骤列表和执行顺序。

请以JSON格式返回调整后的规划结果，格式与原始规划相同。"""
        
        return prompt
    
    def _parse_plan_response(self, task: str, response_content: str) -> Plan:
        """解析LLM响应为规划对象"""
        try:
            # 尝试提取JSON（可能包含markdown代码块）
            content = response_content.strip()
            if content.startswith("```"):
                # 提取代码块内容
                lines = content.split("\n")
                json_start = False
                json_lines = []
                for line in lines:
                    if line.strip().startswith("```"):
                        if json_start:
                            break
                        json_start = True
                        continue
                    if json_start:
                        json_lines.append(line)
                content = "\n".join(json_lines)
            elif content.startswith("```json"):
                content = content[7:].strip()
                if content.endswith("```"):
                    content = content[:-3].strip()
            
            # 解析JSON
            data = json.loads(content)
            steps = []
            
            for step_data in data.get("steps", []):
                step = PlanStep(
                    step_id=step_data.get("step_id", f"step_{len(steps) + 1}"),
                    description=step_data.get("description", ""),
                    dependencies=step_data.get("dependencies", []),
                    required_tools=step_data.get("required_tools", []),
                    expected_output=step_data.get("expected_output"),
                )
                steps.append(step)
            
            return Plan(task=task, steps=steps)
        
        except (json.JSONDecodeError, KeyError) as e:
            raise PlannerError(f"解析规划结果失败: {e}") from e
    
    def _optimize_execution_order(self, plan: Plan) -> List[str]:
        """
        优化执行顺序
        
        根据步骤依赖关系进行拓扑排序，确保依赖步骤先于被依赖步骤执行。
        
        参数:
            plan: 规划对象
        
        返回:
            优化后的执行顺序（步骤ID列表）
        """
        # 拓扑排序
        in_degree: Dict[str, int] = {step.step_id: 0 for step in plan.steps}
        graph: Dict[str, List[str]] = {step.step_id: [] for step in plan.steps}
        
        # 构建依赖图
        for step in plan.steps:
            for dep in step.dependencies:
                if dep in graph:
                    graph[dep].append(step.step_id)
                    in_degree[step.step_id] += 1
        
        # 拓扑排序
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # 如果还有未处理的步骤（存在循环依赖），按原始顺序添加
        remaining = [step.step_id for step in plan.steps if step.step_id not in execution_order]
        execution_order.extend(remaining)
        
        return execution_order
