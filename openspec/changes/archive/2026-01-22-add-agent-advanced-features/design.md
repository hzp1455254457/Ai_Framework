## Context
本项目已具备：
- `core/agent/engine.py`：AgentEngine 核心类，支持任务执行、工具调用、基础工作流循环
- `core/agent/memory.py`：ShortTermMemory（会话上下文）和 LongTermMemory（基于 StorageManager 的持久化）
- `core/agent/tools.py`：工具系统，支持 Function Calling
- `infrastructure/storage/`：StorageManager 统一存储接口，支持数据库和文件存储后端

本 change 需要扩展 Agent 能力，并保持：
- 异步优先（所有 IO 通过 async）
- 模块边界清晰（core 不依赖 api；infrastructure 不依赖 core）
- 可扩展（规划器可替换、向量后端可替换、协作模式可扩展）

## Goals / Non-Goals

### Goals
1. **任务规划器**：
   - 接收复杂任务描述，自动分解为可执行的步骤序列
   - 支持步骤依赖关系识别和执行顺序优化
   - 支持动态调整计划（根据执行结果调整后续步骤）

2. **向量检索集成**：
   - 长期记忆支持语义相似度搜索（基于向量嵌入）
   - 集成向量数据库（Chroma 或 SQLite-VSS）
   - 支持对话历史的向量化存储和检索

3. **多 Agent 协作**：
   - 支持多个 Agent 实例协同执行任务
   - 支持任务分配策略（轮询、负载均衡、专业分工等）
   - 支持结果聚合和冲突解决

### Non-Goals
- 复杂的可视化工作流编辑器
- Agent 之间的实时通信协议（WebSocket等）
- 分布式 Agent 部署（多机器/多进程）
- Agent 的自动学习和优化（强化学习等）

## Decisions

### Decision 1: 任务规划器采用 LLM 驱动的规划策略
**Why**：LLM 具备强大的任务理解和分解能力，可以处理复杂的自然语言任务描述。

**Approach**：
- Planner 使用 LLM 将任务分解为步骤列表
- 每个步骤包含：描述、依赖关系、所需工具、预期输出
- 支持执行过程中的动态调整（根据中间结果重新规划）

**Trade-offs**：
- 优点：灵活、能处理复杂任务
- 缺点：依赖 LLM 调用，可能产生成本；规划质量依赖 LLM 能力

### Decision 2: 向量检索使用 Chroma 作为主要后端，SQLite-VSS 作为可选后端
**Why**：
- Chroma：轻量级、易集成、支持本地和云端部署
- SQLite-VSS：基于 SQLite 扩展，适合小型项目，无需额外依赖

**Approach**：
- 定义 `BaseVectorBackend` 接口
- 实现 `ChromaVectorBackend` 和 `SQLiteVSSVectorBackend`
- 通过配置选择后端

**Trade-offs**：
- Chroma：功能完整但需要额外依赖
- SQLite-VSS：轻量但功能相对有限

### Decision 3: 多 Agent 协作采用中心化编排模式
**Why**：简化实现，便于任务分配和结果聚合。

**Approach**：
- `AgentOrchestrator` 作为中心协调器
- 支持多种任务分配策略（轮询、负载均衡、专业分工）
- Agent 之间通过 Orchestrator 通信，不直接通信

**Trade-offs**：
- 优点：实现简单、易于调试、支持集中式控制
- 缺点：Orchestrator 可能成为瓶颈；不支持完全去中心化的协作

## Risks / Trade-offs

1. **规划器依赖 LLM 调用**：
   - 风险：增加成本和延迟
   - 缓解：支持缓存规划结果；提供简单规则引擎作为备选

2. **向量检索的准确性**：
   - 风险：语义检索可能返回不相关结果
   - 缓解：支持混合检索（向量 + 关键词）；提供相似度阈值配置

3. **多 Agent 协作的复杂性**：
   - 风险：任务分配不当可能导致效率低下
   - 缓解：提供多种分配策略；支持手动指定 Agent

4. **向量数据库依赖**：
   - 风险：增加外部依赖和部署复杂度
   - 缓解：支持可选启用；提供轻量级 SQLite-VSS 选项

## Migration Plan
- 本次为新增能力，不影响现有接口（无 breaking changes）
- 向量检索作为 LongTermMemory 的可选扩展，默认不启用
- 规划器作为 AgentEngine 的可选组件，默认不启用
- 多 Agent 协作需要显式创建 Orchestrator，不影响单 Agent 使用

## Open Questions
1. 规划器是否应该支持预定义的规划模板（如 ReAct、Plan-and-Solve 等）？
2. 向量检索是否应该支持混合检索（向量 + 关键词）？
3. 多 Agent 协作是否应该支持 Agent 之间的直接通信（P2P模式）？
4. 向量嵌入模型是否应该内置（如 sentence-transformers）还是由用户提供？
