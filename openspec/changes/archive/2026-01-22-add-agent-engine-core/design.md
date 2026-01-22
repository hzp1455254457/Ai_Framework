## Context
本项目是个人 AI 框架，已具备：
- `core/llm/`：统一 LLMService + 多适配器（含 Function Calling/stream）
- `infrastructure/storage/`：统一 StorageManager（数据库/文件）+ 连接池（HTTP/DB）
- `api/`：FastAPI 应用与 LLM 路由

本 change 需要补齐 Agent 核心能力，并保持：
- 异步优先（所有 IO 通过 async）
- 模块边界清晰（core 不依赖 api；infrastructure 不依赖 core）
- 可扩展（工具可注册、可替换；记忆可替换存储后端）

## Goals / Non-Goals
### Goals
- 提供最小可用 Agent 引擎：
  - 接收任务 → 选择/调用工具 → 汇总输出
  - 兼容 LLM Function Calling 工具协议（以 OpenAI 风格 schema 为主）
- 工具系统：
  - 工具注册（名称/描述/参数 schema）
  - 工具执行（async callable）
- 记忆系统：
  - 短期记忆：会话上下文（对话消息）
  - 长期记忆：通过 StorageManager 持久化（MVP：conversation_id + metadata）
- API 路由：
  - agent task 执行接口
  - 工具注册接口（用于动态扩展）

### Non-Goals
- 复杂 planner（P2，后续 `agent-planner`）
- 向量检索/RAG（P2，后续 `vector_db`）
- 多 Agent 协作

## Decisions
### Decision 1: 工具协议优先兼容 OpenAI Function Calling 形态
**Why**：框架已有 OpenAI 适配器，并且多家厂商（含兼容 OpenAI 的）可复用同一 schema。

**Shape**：
- Tool 定义包含：`name`, `description`, `parameters(JSON Schema)`
- LLM 输出包含：`tool_calls`（或 `function_call`）时，Agent 执行对应工具并将结果作为 tool message 回注，继续调用 LLM。

### Decision 2: 记忆分层（短期/长期）并通过接口隔离
**Why**：短期记忆与会话强绑定；长期记忆需要持久化且可替换后端。

**Approach**：
- `ShortTermMemory`：基于 `ConversationContext`/消息列表
- `LongTermMemory`：基于 `StorageManager` 的 `save_conversation/get_conversation`（MVP）

### Decision 3: 基础工作流采用线性循环（ReAct-like minimal loop）
**Why**：先交付最小可用；复杂 workflow / planner 留到后续。

**Loop**（概念）：
1) 将 task + memory 组装为 messages
2) 调用 LLM（支持工具 schema）
3) 若出现 tool call → 执行 tool → 写入 tool result → 回到 2
4) 否则输出最终 content

## Risks / Trade-offs
- **不同提供商工具协议差异**：先以 OpenAI 风格为主；后续可在适配器层做归一化。
- **长期记忆语义有限**：MVP 不做向量检索；后续接入 `vector_db`。
- **动态工具注册的安全性**：API 层需考虑鉴权/白名单（本 change 先提供接口，安全策略可在 Phase 9 引入）。

## Migration Plan
- 本次为新增能力，不影响现有接口（无 breaking changes）。
- 后续如果引入 planner 或向量检索，新增 capability/spec delta 即可。

## Open Questions
- Agent API 是否需要版本化路径（例如 `/api/v1/agent/*`）与现有路由保持一致？
- 工具注册接口是否允许覆盖同名工具？（默认：拒绝覆盖，需显式允许）

