# 任务规划器功能设计文档

## 功能概述

任务规划器是Agent引擎的高级功能，能够将复杂任务自动分解为可执行的步骤序列，并优化执行顺序。

**功能名称**：任务规划器（Task Planner）

**解决的问题**：
- 复杂任务无法直接执行，需要分解为多个步骤
- 步骤之间存在依赖关系，需要优化执行顺序
- 执行过程中可能需要动态调整计划

**使用场景**：
- 复杂多步骤任务（如"开发一个Web应用"）
- 需要按顺序执行的任务
- 需要根据中间结果调整后续步骤的任务

---

## 技术架构

### 核心类和接口

```
core/agent/planner.py
├── Planner: 规划器基类（抽象接口）
├── LLMPlanner: 基于LLM的规划器实现
├── Plan: 规划结果类
└── PlanStep: 规划步骤类
```

### 数据流设计

```
复杂任务
  ↓
LLMPlanner.plan()
  ↓
调用LLM生成步骤列表
  ↓
解析JSON响应为Plan对象
  ↓
拓扑排序优化执行顺序
  ↓
返回Plan（包含步骤列表和执行顺序）
  ↓
AgentEngine按Plan执行
```

---

## 接口设计

### LLMPlanner

#### plan()

**功能**：生成任务规划

**接口**：
```python
async def plan(
    self,
    task: str,
    context: Optional[Dict[str, Any]] = None,
) -> Plan
```

**参数**：
- `task`: 任务描述（文本）
- `context`: 上下文信息（可选）

**返回**：
- `Plan`对象，包含步骤列表和执行顺序

---

### Plan

**功能**：任务规划结果

**属性**：
- `task`: 原始任务描述
- `steps`: 步骤列表（`List[PlanStep]`）
- `execution_order`: 优化后的执行顺序（步骤ID列表）

**方法**：
- `get_step(step_id: str) -> Optional[PlanStep]`: 根据ID获取步骤
- `get_ready_steps(completed_steps: List[str]) -> List[PlanStep]`: 获取可执行步骤

---

### PlanStep

**功能**：规划步骤

**属性**：
- `step_id`: 步骤ID（唯一标识）
- `description`: 步骤描述
- `dependencies`: 依赖的步骤ID列表
- `required_tools`: 所需工具列表（可选）
- `expected_output`: 预期输出描述（可选）

---

## 实现细节

### 关键技术选型

1. **LLM驱动规划**：
   - 使用LLM的强大理解能力分解任务
   - 通过结构化提示词引导LLM生成JSON格式的规划
   - 支持规划结果缓存，减少LLM调用

2. **拓扑排序**：
   - 根据步骤依赖关系进行拓扑排序
   - 确保依赖步骤先于被依赖步骤执行
   - 处理循环依赖（如果存在）

3. **动态调整**：
   - 支持根据执行结果重新规划
   - 当步骤失败时，可以调整后续步骤

### 核心算法

**拓扑排序算法**：
```python
1. 构建依赖图（graph）和入度表（in_degree）
2. 将所有入度为0的步骤加入队列
3. 依次处理队列中的步骤：
   - 将步骤加入执行顺序
   - 减少其依赖步骤的入度
   - 如果依赖步骤入度为0，加入队列
4. 如果还有未处理的步骤（循环依赖），按原始顺序添加
```

---

## 依赖关系

### 依赖的其他模块

- `core.llm.service`: LLMService（用于调用LLM生成规划）

### 外部依赖库

- `json`: JSON解析（标准库）

---

## 测试策略

### 单元测试计划

- `test_planner.py`: 规划器测试
  - Plan和PlanStep的创建和操作
  - LLMPlanner的规划功能
  - 执行顺序优化
  - 动态调整规划

---

## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|---------|--------|
| v1.0 | 2026-01-21 | 初始版本，实现LLM驱动的任务规划器 | - |
