## 1. Proposal (OpenSpec)
- [x] 1.1 明确 capability 划分：`agent-engine` / `agent-api`（本次），`agent-planner`（后续可选）
- [x] 1.2 完成 `proposal.md`（why/what/impact/non-goals）
- [x] 1.3 完成 `design.md`（关键架构决策：工具协议、记忆分层、LLM工具调用适配）
- [x] 1.4 完成 spec deltas：
  - [x] 1.4.1 `specs/agent-engine/spec.md`
  - [x] 1.4.2 `specs/agent-api/spec.md`
- [x] 1.5 运行 `openspec validate add-agent-engine-core --strict` 并修复所有问题

## 2. Implementation (after approval)
- [x] 2.1 创建 `core/agent/` 模块骨架与 README（如需）
- [x] 2.2 实现 `AgentEngine`：任务接收与执行、LLMService 集成、基础循环
- [x] 2.3 实现 `tools.py`：工具定义/注册/调用协议（Function Calling 输入输出）
- [x] 2.4 实现 `memory.py`：
  - [x] 2.4.1 短期记忆（会话上下文）
  - [x] 2.4.2 长期记忆（StorageManager 集成）
- [x] 2.5 实现 `workflow.py`：基础工作流（线性步骤 + 错误处理）
- [x] 2.6 实现 `api/routes/agent.py`：任务接口 + 工具注册接口，并挂载到 FastAPI
- [x] 2.7 单元测试：
  - [x] 2.7.1 `tests/unit/core/agent/test_engine.py`
  - [x] 2.7.2 `tests/unit/core/agent/test_tools.py`
  - [x] 2.7.3 `tests/unit/core/agent/test_memory.py`
  - [x] 2.7.4 `tests/unit/api/test_agent_routes.py`
- [x] 2.8 文档同步（按项目规范）：
  - [x] 2.8.1 `docs/design/agent-engine.md`（功能设计文档）
  - [x] 2.8.2 更新 `docs/PROJECT_PLAN.md`：Phase 5 标记为进行中/已完成
- [x] 2.9 运行聚焦测试（agent + api），确保通过

