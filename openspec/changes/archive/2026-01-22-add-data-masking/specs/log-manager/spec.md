# log-manager Specification Delta

## ADDED Requirements

### Requirement: Sensitive Data Masking
系统 SHALL 在日志输出和错误响应中自动脱敏敏感数据，防止敏感信息泄露。

**Rationale**: 日志可能包含敏感信息（如 API 密钥、用户输入等），必须脱敏以符合安全最佳实践和合规要求。

#### Scenario: Mask API Keys in Log Messages
**Given** 日志管理器已配置数据脱敏功能
**When** 日志消息包含 API 密钥（如 `sk-1234567890abcdef`）
**Then** 系统应：
1. 自动检测 API 密钥模式
2. 脱敏 API 密钥（如 `sk-****...****ef`）
3. 输出脱敏后的日志消息
4. 不记录原始 API 密钥

#### Scenario: Mask Sensitive Data in Error Responses
**Given** 错误处理中间件已配置数据脱敏功能
**When** API 返回错误响应，包含敏感信息
**Then** 系统应：
1. 自动检测错误响应中的敏感信息
2. 脱敏敏感信息
3. 返回脱敏后的错误响应
4. 保持错误信息可读性

#### Scenario: Configure Masking Rules
**Given** 用户需要自定义脱敏规则
**When** 用户在配置文件中设置脱敏规则
**Then** 系统应：
1. 读取并应用脱敏规则
2. 支持正则表达式模式
3. 支持多种脱敏模式（部分隐藏、完全隐藏等）
4. 在日志和错误响应中应用规则

#### Scenario: Disable Masking in Development
**Given** 系统支持按环境配置脱敏功能
**When** 开发环境配置禁用脱敏
**Then** 系统应：
1. 在开发环境中不进行脱敏
2. 输出原始日志消息（便于调试）
3. 在生产环境中强制启用脱敏

#### Scenario: Handle Custom Sensitive Patterns
**Given** 用户定义了自定义敏感数据模式
**When** 日志消息包含匹配自定义模式的数据
**Then** 系统应：
1. 检测自定义模式
2. 应用对应的脱敏规则
3. 输出脱敏后的日志消息
