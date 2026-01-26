# agent-engine Specification Delta

## MODIFIED Requirements

### Requirement: Complete LangChain Agent Implementation
系统 SHALL 提供完整的LangChain Agent引擎实现，支持多种Agent类型和完整的工具/记忆转换。

**Rationale**: 通过完整的LangChain Agent适配器实现，可以使用LangChain生态的所有Agent功能和工具。

#### Scenario: Create LangChain Agent with Native Tools
**Given** 系统已配置使用LangChain Agent，但工具使用自研实现
**When** 用户创建Agent引擎
**Then** 系统应：
1. 自动将自研工具转换为LangChain工具
2. 创建LangChain AgentExecutor
3. 工具转换后的功能与原生工具一致
4. Agent可以正常调用转换后的工具

#### Scenario: Create LangChain Agent with Native Memory
**Given** 系统已配置使用LangChain Agent，但记忆使用自研实现
**When** 用户创建Agent引擎
**Then** 系统应：
1. 自动将自研记忆转换为LangChain记忆
2. 创建LangChain AgentExecutor
3. 记忆转换后的功能与原生记忆一致
4. Agent可以正常使用转换后的记忆

#### Scenario: Execute Task with LangChain Agent
**Given** 系统已创建LangChain Agent引擎
**When** 用户调用run_task执行任务
**Then** 系统应：
1. 使用LangChain AgentExecutor执行任务
2. 提取工具调用信息（从intermediate_steps）
3. 返回标准格式的结果
4. 包含完整的工具调用记录

#### Scenario: Support Multiple Agent Types
**Given** 系统已配置使用LangChain Agent
**When** 用户在配置中指定不同的agent_type
**Then** 系统应：
1. 支持openai-functions类型
2. 支持openai-multi-functions类型
3. 支持react类型
4. 支持self-ask-with-search类型
5. 根据配置创建对应的Agent类型

#### Scenario: Register Tool After Agent Initialization
**Given** 系统已初始化LangChain Agent引擎
**When** 用户注册新工具
**Then** 系统应：
1. 将工具转换为LangChain工具
2. 重新创建AgentExecutor以包含新工具
3. 新工具可以在后续任务中使用

### Requirement: Complete LangChain Tool Manager Implementation
系统 SHALL 提供完整的LangChain工具管理器实现，支持工具转换和执行。

**Rationale**: 通过完整的LangChain工具适配器实现，可以使用LangChain生态的所有工具功能。

#### Scenario: Convert Native Tool to LangChain Tool
**Given** 系统已配置使用LangChain工具管理器
**When** 用户注册自研工具
**Then** 系统应：
1. 将自研Tool转换为LangChain Tool
2. 创建Pydantic模型用于参数验证
3. 包装异步执行函数
4. 转换后的工具功能与原生工具一致

#### Scenario: Execute LangChain Tool
**Given** 系统已注册LangChain工具
**When** 用户调用execute方法执行工具
**Then** 系统应：
1. 调用LangChain Tool的ainvoke方法
2. 处理参数验证
3. 返回工具执行结果
4. 处理错误和异常

#### Scenario: Get Tool Schema from LangChain Tool
**Given** 系统已注册LangChain工具
**When** 用户调用get_tool_schema方法
**Then** 系统应：
1. 从LangChain Tool获取schema
2. 转换为标准Function Calling格式
3. 包含name、description、parameters字段

### Requirement: Complete LangChain Memory Implementation
系统 SHALL 提供完整的LangChain记忆管理器实现，支持消息管理和持久化。

**Rationale**: 通过完整的LangChain记忆适配器实现，可以使用LangChain生态的所有记忆功能。

#### Scenario: Add Messages to LangChain Memory
**Given** 系统已配置使用LangChain记忆管理器
**When** 用户调用add_message添加消息
**Then** 系统应：
1. 将user消息转换为HumanMessage
2. 将assistant消息转换为AIMessage
3. 将tool消息转换为ToolMessage（包含tool_call_id）
4. 正确添加到LangChain Memory

#### Scenario: Get Messages from LangChain Memory
**Given** 系统已添加消息到LangChain记忆
**When** 用户调用get_messages获取消息
**Then** 系统应：
1. 从LangChain Memory获取所有消息
2. 转换为标准格式（role和content）
3. 保留工具消息的特殊字段（tool_call_id）
4. 消息顺序正确

#### Scenario: Clear LangChain Memory
**Given** 系统已添加消息到LangChain记忆
**When** 用户调用clear清空记忆
**Then** 系统应：
1. 调用LangChain Memory的clear方法
2. 所有消息被清空
3. message_count返回0
