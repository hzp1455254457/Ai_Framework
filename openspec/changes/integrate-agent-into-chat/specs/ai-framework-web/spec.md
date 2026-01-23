## ADDED Requirements

### Requirement: Chat interface supports Agent mode toggle
聊天界面 SHALL 提供Agent模式开关，允许用户启用/禁用工具调用功能。

#### Scenario: User enables Agent mode
- **WHEN** 用户在聊天界面启用Agent模式开关
- **THEN** 后续发送的消息 SHALL 使用Agent模式（包含工具调用）
- **AND** 界面 SHALL 显示Agent模式已启用的视觉提示

#### Scenario: User disables Agent mode
- **WHEN** 用户在聊天界面禁用Agent模式开关
- **THEN** 后续发送的消息 SHALL 使用普通LLM模式（不调用工具）
- **AND** 界面 SHALL 显示Agent模式已禁用的状态

### Requirement: Chat interface displays tool call information
聊天界面 SHALL 清晰展示工具调用过程和结果。

#### Scenario: Display tool call during execution
- **WHEN** Agent正在执行工具调用
- **THEN** 界面 SHALL 显示"正在使用工具 [工具名称]..."的加载状态
- **AND** 界面 SHALL 显示工具调用的参数信息

#### Scenario: Display tool call result
- **WHEN** 工具调用完成
- **THEN** 界面 SHALL 在消息下方显示工具调用卡片
- **AND** 工具调用卡片 SHALL 显示工具名称、参数、执行结果
- **AND** 工具调用卡片 SHALL 支持展开/折叠查看详情

#### Scenario: Display multiple tool calls
- **WHEN** Agent在一次对话中调用了多个工具
- **THEN** 界面 SHALL 按顺序显示所有工具调用
- **AND** 每个工具调用 SHALL 有独立的卡片显示

### Requirement: Chat interface redesign for better UX
聊天界面 SHALL 重新设计以提供更好的用户体验。

#### Scenario: Modern chat layout
- **WHEN** 用户打开聊天页面
- **THEN** 界面 SHALL 采用现代化的卡片式消息布局
- **AND** 界面 SHALL 有清晰的信息层次和视觉反馈
- **AND** 界面 SHALL 支持响应式布局（移动端适配）

#### Scenario: Enhanced input area
- **WHEN** 用户查看输入区域
- **THEN** 输入区域 SHALL 显示当前Agent模式状态
- **AND** 输入区域 SHALL 提供Agent模式切换控件
- **AND** 输入区域 SHALL 有清晰的提示信息

## MODIFIED Requirements

### Requirement: LLM Store supports Agent mode state
LLM Store SHALL 支持Agent模式状态管理。

#### Scenario: Store manages Agent mode state
- **WHEN** 用户切换Agent模式
- **THEN** Store SHALL 更新 `useAgent` 状态
- **AND** Store SHALL 在发送消息时包含Agent模式参数

#### Scenario: Store manages tool call information
- **WHEN** 收到包含工具调用的响应
- **THEN** Store SHALL 解析并存储工具调用信息
- **AND** Store SHALL 将工具调用信息关联到对应的消息

### Requirement: API client supports Agent parameters
API客户端 SHALL 支持Agent模式相关参数。

#### Scenario: Chat API includes Agent parameters
- **WHEN** 调用聊天API
- **THEN** 请求 SHALL 包含 `use_agent` 和 `conversation_id` 参数（如果启用）
- **AND** 响应解析 SHALL 提取工具调用信息
