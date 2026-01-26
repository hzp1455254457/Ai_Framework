# agent-engine Specification

## Purpose
Agent引擎核心（Agent Engine Core）是AI框架的核心价值体现，提供智能体（Agent）执行能力。包括任务接收和执行、LLM集成、工具调用、记忆管理（短期记忆和长期记忆）以及基础工作流编排。支持"LLM推理 → 工具调用（可选）→ 输出结果"的完整闭环。
## Requirements
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

### Requirement: LangChain Integration
系统 SHALL 支持集成LangChain作为可选AI应用开发框架，提供链式调用、工具集成、记忆管理等能力。

**Rationale**: LangChain提供了丰富的AI应用开发能力，可以降低开发复杂AI应用的难度，并可以使用LangChain生态的工具和组件。

#### Scenario: Use LangChain Chain
**Given** 系统已安装LangChain，配置启用了LangChain模式
**When** 用户创建LangChain链并执行
**Then** 系统应：
1. 检测到LangChain可用
2. 使用LangChainIntegration创建链
3. 执行链式调用
4. 返回标准格式的响应

#### Scenario: Integrate LangChain Tools
**Given** 系统已集成LangChain
**When** 用户在AgentEngine中使用LangChain工具
**Then** 系统应：
1. 将LangChain工具注册到AgentEngine
2. 在Agent执行时可以使用LangChain工具
3. 工具调用结果正确返回
4. 支持LangChain工具和自研工具混合使用

#### Scenario: Use LangChain Memory
**Given** 系统已集成LangChain
**When** 用户使用LangChain记忆管理
**Then** 系统应：
1. 使用LangChain的记忆组件（ConversationBufferMemory等）
2. 记忆数据正确存储和检索
3. 支持多种记忆类型（短期、长期等）
4. 记忆数据与AgentEngine集成

#### Scenario: Fallback to Custom Engine
**Given** 系统配置了LangChain，但LangChain不可用
**When** 用户发送Agent请求
**Then** 系统应：
1. 检测到LangChain不可用
2. 自动切换到自研Agent引擎
3. 使用自研引擎处理请求
4. 记录fallback事件

### Requirement: LangGraph Integration
系统 SHALL 支持集成LangGraph作为可选工作流编排引擎，支持复杂的状态机和工作流。

**Rationale**: LangGraph提供了强大的工作流编排能力，适合需要复杂工作流的场景（多步骤任务、条件分支、循环等）。

#### Scenario: Create LangGraph Workflow
**Given** 系统已安装LangGraph，配置启用了LangGraph模式
**When** 用户定义并创建工作流
**Then** 系统应：
1. 检测到LangGraph可用
2. 使用LangGraphIntegration创建工作流
3. 工作流定义正确解析
4. 工作流状态图正确构建

#### Scenario: Execute LangGraph Workflow
**Given** 系统已创建LangGraph工作流
**When** 用户执行工作流
**Then** 系统应：
1. 使用LangGraph执行引擎运行工作流
2. 工作流状态正确转换
3. 支持条件分支和循环
4. 返回工作流执行结果

#### Scenario: Workflow State Management
**Given** 系统已创建LangGraph工作流
**When** 工作流执行过程中需要状态管理
**Then** 系统应：
1. 正确保存和恢复工作流状态
2. 支持状态持久化（可选）
3. 支持工作流暂停和恢复
4. 状态数据正确传递

#### Scenario: Visualize Workflow
**Given** 系统已创建LangGraph工作流
**When** 用户请求可视化工作流
**Then** 系统应：
1. 生成工作流状态图（可选）
2. 可视化工作流节点和边
3. 显示工作流执行路径
4. 支持导出工作流图

#### Scenario: Fallback to Custom Engine
**Given** 系统配置了LangGraph，但LangGraph不可用
**When** 用户发送需要工作流的请求
**Then** 系统应：
1. 检测到LangGraph不可用
2. 自动切换到自研Agent引擎
3. 使用自研引擎处理请求（如果支持）
4. 记录fallback事件

### Requirement: Framework Selection Guidance
系统 SHALL 提供框架选择指导，帮助用户根据场景选择合适的框架组合。

**Rationale**: 不同场景适合不同的框架组合，需要提供清晰的指导避免用户过度使用复杂框架。

#### Scenario: Query Framework Recommendations
**Given** 用户需要选择框架
**When** 用户查询框架推荐
**Then** 系统应：
1. 根据使用场景推荐合适的框架
2. 提供框架选择指南
3. 说明各框架的适用场景
4. 提供性能和使用建议

#### Scenario: Configure Framework Mode
**Given** 用户需要配置框架模式
**When** 用户在配置文件中设置框架模式
**Then** 系统应：
1. 读取并应用框架配置
2. 支持启用/禁用各个框架
3. 支持混合使用多个框架
4. 配置验证和错误提示

### Requirement: Abstract Agent Engine Interface
系统 SHALL 提供 `IAgentEngine` 抽象接口，定义统一的Agent引擎接口规范。

**Rationale**: 通过抽象接口实现Agent引擎的解耦，支持多种实现（自研、LangChain、LangGraph）的灵活切换和组装。

#### Scenario: Create Agent Engine via Factory
**Given** 系统已实现 `AgentFactory`
**When** 用户通过工厂创建Agent引擎，指定实现类型（native/langchain/langgraph）
**Then** 系统应：
1. 根据实现类型创建对应的Agent引擎实例
2. 支持依赖注入（LLM提供者、工具管理器、记忆管理器）
3. 返回实现 `IAgentEngine` 接口的对象
4. 支持通过配置自动选择实现类型

#### Scenario: Use Native Agent Engine
**Given** 系统配置使用native实现
**When** 用户创建Agent引擎
**Then** 系统应：
1. 创建 `NativeAgentEngine` 实例
2. 包装现有 `AgentEngine` 为接口实现
3. 保持现有功能完全兼容
4. 支持所有现有API调用

#### Scenario: Use LangChain Agent Engine
**Given** 系统已安装LangChain，配置使用langchain实现
**When** 用户创建Agent引擎
**Then** 系统应：
1. 创建 `LangChainAgentEngine` 实例
2. 使用LangChain Agent实现接口
3. 自动转换工具和记忆为LangChain格式
4. 支持LangChain的所有Agent类型

#### Scenario: Use LangGraph Agent Engine
**Given** 系统已安装LangGraph，配置使用langgraph实现
**When** 用户创建Agent引擎
**Then** 系统应：
1. 创建 `LangGraphAgentEngine` 实例
2. 使用LangGraph实现接口
3. 支持复杂工作流和状态管理
4. 支持工作流可视化（可选）

#### Scenario: Switch Agent Implementation at Runtime
**Given** 系统已初始化 `ComponentManager`
**When** 用户调用 `switch_agent_implementation()` 切换实现
**Then** 系统应：
1. 创建新的Agent引擎实例
2. 保持LLM提供者、工具管理器、记忆管理器不变
3. 替换现有Agent引擎
4. 支持后续请求使用新实现

#### Scenario: Mix Different Implementations
**Given** 系统已实现多种组件
**When** 用户配置混合使用不同实现（如LangChain Agent + 自研工具 + LangChain记忆）
**Then** 系统应：
1. 创建LangChain Agent引擎
2. 注入自研工具管理器
3. 注入LangChain记忆管理器
4. 所有组件正确协作
5. 任务执行成功

### Requirement: Agent Factory Pattern
系统 SHALL 提供 `AgentFactory` 工厂类，支持根据配置创建不同的Agent引擎实现，并支持依赖注入。

**Rationale**: 使用工厂模式封装对象创建逻辑，支持动态选择实现和依赖注入。

#### Scenario: Create with Dependency Injection
**Given** 系统已创建LLM提供者、工具管理器、记忆管理器
**When** 用户调用 `AgentFactory.create(implementation, config, llm_provider, tool_manager, memory)`
**Then** 系统应：
1. 使用提供的依赖创建Agent引擎
2. 如果依赖未提供，从配置自动创建
3. 根据实现类型创建对应的Agent引擎
4. 注入所有依赖到Agent引擎

#### Scenario: Create from Configuration
**Given** 配置文件包含 `agent.implementation` 配置项
**When** 用户调用 `AgentFactory.create_from_config(config)`
**Then** 系统应：
1. 读取配置中的实现类型
2. 自动创建所需的依赖（LLM提供者、工具管理器、记忆管理器）
3. 根据实现类型创建对应的Agent引擎
4. 注入所有依赖

### Requirement: Tool Manager Interface
系统 SHALL 提供 `IToolManager` 抽象接口，定义统一的工具管理器接口规范。

**Rationale**: 通过抽象接口实现工具管理器的解耦，支持多种实现（自研、LangChain）的灵活切换。

#### Scenario: Use Native Tool Manager
**Given** 系统配置使用native实现
**When** 用户创建工具管理器
**Then** 系统应：
1. 创建 `NativeToolManager` 实例
2. 包装现有 `ToolRegistry` 为接口实现
3. 保持现有功能完全兼容

#### Scenario: Use LangChain Tool Manager
**Given** 系统已安装LangChain，配置使用langchain实现
**When** 用户创建工具管理器
**Then** 系统应：
1. 创建 `LangChainToolManager` 实例
2. 使用LangChain Tools实现接口
3. 支持将自研工具转换为LangChain工具

### Requirement: Memory Interface
系统 SHALL 提供 `IMemory` 抽象接口，定义统一的记忆管理接口规范。

**Rationale**: 通过抽象接口实现记忆管理的解耦，支持多种实现（自研、LangChain）的灵活切换。

#### Scenario: Use Native Memory
**Given** 系统配置使用native实现
**When** 用户创建记忆管理器
**Then** 系统应：
1. 创建 `NativeMemory` 实例
2. 包装现有 `ShortTermMemory` 和 `LongTermMemory` 为接口实现
3. 保持现有功能完全兼容

#### Scenario: Use LangChain Memory
**Given** 系统已安装LangChain，配置使用langchain实现
**When** 用户创建记忆管理器
**Then** 系统应：
1. 创建 `LangChainMemory` 实例
2. 使用LangChain Memory实现接口
3. 支持将自研记忆转换为LangChain记忆

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

