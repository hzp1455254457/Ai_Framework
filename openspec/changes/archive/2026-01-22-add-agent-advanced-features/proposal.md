# Change: Add Agent Advanced Features (任务规划器 + 向量检索 + 多Agent协作)

## Why
当前框架已具备 Agent 引擎核心能力（任务执行、工具调用、基础记忆管理），但缺少：
1. **任务规划能力**：Agent 无法自动分解复杂任务为可执行的步骤序列
2. **语义检索能力**：长期记忆仅支持基于 conversation_id 的精确检索，无法进行语义相似度搜索
3. **多 Agent 协作能力**：无法支持多个 Agent 协同完成复杂任务

这些能力是构建高级 AI Agent 系统的关键组件，能够显著提升 Agent 的智能水平和应用场景。

## What Changes
- 新增 `agent-planner` capability：任务规划器（任务分解、步骤规划、执行顺序优化）
- 新增 `agent-vector-memory` capability：向量检索集成（长期记忆的语义检索能力）
- 新增 `agent-collaboration` capability：多 Agent 协作（多 Agent 协同执行、任务分配、结果聚合）

## Impact
- **Affected specs**: `agent-planner`, `agent-vector-memory`, `agent-collaboration`（本次新增）
- **Affected code (planned)**:
  - `core/agent/planner.py`：任务规划器实现
  - `core/agent/memory.py`：扩展 LongTermMemory 支持向量检索
  - `infrastructure/storage/vector_db.py`：向量数据库集成（Chroma/SQLite-VSS）
  - `core/agent/collaboration.py`：多 Agent 协作管理器
  - `core/agent/orchestrator.py`：Agent 编排器（可选）
  - `api/routes/agent.py`：扩展 API 支持规划器和协作功能
  - `tests/unit/core/agent/test_planner.py`：规划器测试
  - `tests/unit/core/agent/test_vector_memory.py`：向量记忆测试
  - `tests/unit/core/agent/test_collaboration.py`：协作测试

## Non-Goals
- 不在本次 change 中实现复杂的可视化工作流编辑器
- 不在本次 change 中实现 Agent 之间的实时通信协议（WebSocket等）
- 不在本次 change 中实现分布式 Agent 部署（多机器/多进程）
- 不在本次 change 中实现 Agent 的自动学习和优化（强化学习等）
