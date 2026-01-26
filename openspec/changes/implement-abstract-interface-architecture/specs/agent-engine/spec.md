# agent-engine Specification Delta

## ADDED Requirements

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
