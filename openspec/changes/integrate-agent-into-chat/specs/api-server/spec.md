## MODIFIED Requirements

### Requirement: Chat API supports Agent mode
聊天API SHALL 支持可选的Agent模式，当启用时自动使用Agent引擎处理请求并支持工具调用。

#### Scenario: Chat with Agent mode enabled
- **WHEN** 用户发送聊天请求，`use_agent=true`
- **THEN** API SHALL 使用Agent引擎处理请求，支持工具调用
- **AND** 响应中 SHALL 包含工具调用信息（tool_calls）在metadata中

#### Scenario: Chat with Agent mode disabled (backward compatible)
- **WHEN** 用户发送聊天请求，`use_agent=false` 或未提供
- **THEN** API SHALL 使用普通LLM服务处理请求（保持原有行为）
- **AND** 响应中 SHALL 不包含工具调用信息

#### Scenario: Stream chat with Agent mode
- **WHEN** 用户发送流式聊天请求，`use_agent=true`
- **THEN** API SHALL 支持流式输出Agent执行结果
- **AND** 流式响应中 SHALL 包含工具调用状态信息

#### Scenario: Agent mode error handling
- **WHEN** Agent模式执行失败（工具调用失败、超时等）
- **THEN** API SHALL 返回友好的错误信息
- **AND** API SHALL 支持降级到普通LLM模式（可选）

### Requirement: Chat request model includes Agent parameters
聊天请求模型 SHALL 包含Agent模式相关参数。

#### Scenario: ChatRequest includes use_agent parameter
- **WHEN** 创建ChatRequest实例
- **THEN** 模型 SHALL 包含 `use_agent: bool` 字段（默认False）
- **AND** 模型 SHALL 包含 `conversation_id: Optional[str]` 字段（用于Agent长期记忆）

#### Scenario: StreamChatRequest includes Agent parameters
- **WHEN** 创建StreamChatRequest实例
- **THEN** 模型 SHALL 包含与ChatRequest相同的Agent参数

### Requirement: Chat response includes tool call information
聊天响应 SHALL 在metadata中包含工具调用信息（当使用Agent模式时）。

#### Scenario: Response metadata contains tool calls
- **WHEN** Agent模式执行并调用了工具
- **THEN** 响应metadata SHALL 包含 `tool_calls` 列表
- **AND** 每个工具调用 SHALL 包含工具名称、参数、结果
- **AND** metadata SHALL 包含 `iterations` 字段（Agent迭代次数）
