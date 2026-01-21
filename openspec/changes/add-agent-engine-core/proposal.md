# Change: Add Agent Engine Core (Agent 执行/工具/记忆 + API 路由)

## Why
当前框架已具备 LLM 与基础设施（配置/日志/存储/缓存）能力，但缺少 Agent 引擎核心（任务执行、工具调用、记忆管理、工作流编排），无法体现“智能体”这一核心价值。

## What Changes
- 新增 `agent-engine` capability：提供 AgentEngine 核心类、任务执行、LLM 集成、基础工作流、工具系统、记忆管理（短期/长期）
- 新增 `agent-api` capability：提供 Agent 路由（任务接口、工具注册接口），与 FastAPI 集成
- （可选，后续迭代）新增 `agent-planner` capability：任务规划器（任务分解/步骤规划/执行优化）

## Impact
- **Affected specs**: `agent-engine`, `agent-api`（本次新增；当前仓库尚无 openspec/specs）
- **Affected code (planned)**:
  - `core/agent/engine.py`, `core/agent/tools.py`, `core/agent/memory.py`, `core/agent/workflow.py`
  - `api/routes/agent.py`, `api/fastapi_app.py`, `api/dependencies.py`（依赖注入/路由挂载）
  - `infrastructure/storage/*`（长期记忆存储集成）
  - `tests/unit/core/agent/*`, `tests/unit/api/test_agent_routes.py`（新增测试）

## Non-Goals
- 不在本次 change 中实现复杂的可视化工作流编辑器
- 不在本次 change 中实现多 Agent 协作
- 不在本次 change 中实现完整的 RAG/向量检索（长期记忆以 StorageManager 的 KV/对话存储为 MVP）

