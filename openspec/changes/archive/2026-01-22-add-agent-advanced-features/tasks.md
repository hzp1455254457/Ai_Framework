## 1. Proposal (OpenSpec)
- [x] 1.1 明确 capability 划分：`agent-planner` / `agent-vector-memory` / `agent-collaboration`
- [x] 1.2 完成 `proposal.md`（why/what/impact/non-goals）
- [x] 1.3 完成 `design.md`（关键架构决策：规划策略、向量后端选择、协作模式）
- [x] 1.4 完成 spec deltas：
  - [x] 1.4.1 `specs/agent-planner/spec.md`
  - [x] 1.4.2 `specs/agent-vector-memory/spec.md`
  - [x] 1.4.3 `specs/agent-collaboration/spec.md`
- [x] 1.5 运行 `openspec validate add-agent-advanced-features --strict` 并修复所有问题

## 2. Implementation (after approval)

### 2.1 任务规划器 (agent-planner)
- [x] 2.1.1 创建 `core/agent/planner.py`：Planner 基类和接口
- [x] 2.1.2 实现 `LLMPlanner`：基于 LLM 的任务分解和步骤规划
- [x] 2.1.3 实现步骤依赖关系解析和执行顺序优化
- [x] 2.1.4 集成 Planner 到 AgentEngine（可选启用）
- [x] 2.1.5 单元测试：`tests/unit/core/agent/test_planner.py`

### 2.2 向量检索集成 (agent-vector-memory)
- [x] 2.2.1 创建 `infrastructure/storage/vector_db.py`：向量数据库接口和实现
- [x] 2.2.2 实现 `BaseVectorBackend`：向量后端基类
- [x] 2.2.3 实现 `ChromaVectorBackend`：Chroma 集成
- [x] 2.2.4 实现 `SQLiteVSSVectorBackend`：SQLite-VSS 集成（占位实现）
- [x] 2.2.5 扩展 `LongTermMemory`：支持向量检索方法
- [x] 2.2.6 实现对话历史的向量化存储和检索（基础结构，需要嵌入模型集成）
- [ ] 2.2.7 单元测试：`tests/unit/core/agent/test_vector_memory.py`（需要mock向量后端）
- [ ] 2.2.8 单元测试：`tests/unit/infrastructure/storage/test_vector_db.py`（需要mock向量后端）

### 2.3 多 Agent 协作 (agent-collaboration)
- [x] 2.3.1 创建 `core/agent/collaboration.py`：协作管理器
- [x] 2.3.2 实现 `AgentOrchestrator`：Agent 编排器
- [x] 2.3.3 实现任务分配策略（轮询、负载均衡、专业分工）
- [x] 2.3.4 实现结果聚合和冲突解决
- [x] 2.3.5 集成 Orchestrator 到 API 路由
- [x] 2.3.6 单元测试：`tests/unit/core/agent/test_collaboration.py`

### 2.4 API 扩展
- [x] 2.4.1 扩展 `api/routes/agent.py`：支持规划器参数
- [x] 2.4.2 扩展 `api/routes/agent.py`：支持向量检索接口
- [x] 2.4.3 扩展 `api/routes/agent.py`：支持多 Agent 协作接口
- [x] 2.4.4 更新 API 模型：`api/models/request.py` 和 `api/models/response.py`

### 2.5 文档和配置
- [x] 2.5.1 更新 `docs/design/agent-engine.md`：添加规划器、向量检索、协作说明
- [x] 2.5.2 创建 `docs/design/agent-planner.md`：规划器设计文档
- [x] 2.5.3 创建 `docs/design/vector-memory.md`：向量检索设计文档
- [x] 2.5.4 创建 `docs/design/agent-collaboration.md`：多 Agent 协作设计文档
- [x] 2.5.5 更新 `config/default.yaml`：添加规划器、向量检索、协作配置
- [x] 2.5.6 更新 `docs/PROJECT_PLAN.md`：标记 Phase 5 相关任务为已完成

### 2.6 测试和验证
- [x] 2.6.1 运行所有单元测试，确保通过（规划器和协作测试通过）
- [ ] 2.6.2 集成测试：规划器与 AgentEngine 集成（需要真实LLM调用）
- [ ] 2.6.3 集成测试：向量检索与 LongTermMemory 集成（需要嵌入模型）
- [ ] 2.6.4 集成测试：多 Agent 协作端到端测试（需要多个Agent实例）
