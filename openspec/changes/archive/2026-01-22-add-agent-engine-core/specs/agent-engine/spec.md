## ADDED Requirements

### Requirement: Agent Engine Core
系统 SHALL 提供一个 `AgentEngine` 用于接收任务并执行，能够在一次任务执行中完成“LLM 推理 → 工具调用（可选）→ 输出结果”的闭环。

#### Scenario: Execute a simple task without tools
- **WHEN** 用户提交一个无需工具的任务
- **THEN** AgentEngine SHALL 调用 LLM 并返回最终文本结果

#### Scenario: Execute a task that requires tool calls
- **WHEN** LLM 返回一个或多个工具调用请求（Function Calling / tool calls）
- **THEN** AgentEngine SHALL 按照工具调用协议执行对应工具并将结果回注，再继续调用 LLM 直到得到最终文本结果

### Requirement: Tool System
系统 SHALL 提供工具系统用于定义、注册和执行工具，并支持 Function Calling 的工具 schema 输出。

#### Scenario: Register a tool
- **WHEN** 开发者注册一个工具（包含 name/description/parameters schema 与 async 执行函数）
- **THEN** 工具系统 SHALL 使该工具可被 AgentEngine 在任务执行中调用

#### Scenario: Reject invalid tool definitions
- **WHEN** 注册的工具缺少 name 或 parameters schema 非法
- **THEN** 系统 SHALL 拒绝注册并返回可诊断的错误信息

### Requirement: Memory Management
系统 SHALL 提供记忆管理能力，包含短期记忆与长期记忆，并在任务执行中可读写。

#### Scenario: Short-term memory keeps conversation context
- **WHEN** AgentEngine 在同一会话中执行多轮 LLM 交互
- **THEN** 短期记忆 SHALL 维护会话消息历史以供后续轮次使用

#### Scenario: Long-term memory persists conversation via StorageManager
- **WHEN** 任务执行结束（成功或失败）且配置启用长期记忆
- **THEN** 长期记忆 SHALL 通过 StorageManager 持久化会话（至少包含 conversation_id、messages、metadata）

