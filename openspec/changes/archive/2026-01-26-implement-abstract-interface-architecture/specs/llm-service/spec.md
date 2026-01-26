# llm-service Specification Delta

## ADDED Requirements

### Requirement: Abstract LLM Provider Interface
系统 SHALL 提供 `ILLMProvider` 抽象接口，定义统一的LLM提供者接口规范。

**Rationale**: 通过抽象接口实现LLM提供者的解耦，支持多种实现（自研、LiteLLM、LangChain）的灵活切换。

#### Scenario: Create LLM Provider via Factory
**Given** 系统已实现 `ILLMFactory`
**When** 用户通过工厂创建LLM提供者，指定实现类型（native/litellm/langchain）
**Then** 系统应：
1. 根据实现类型创建对应的LLM提供者实例
2. 返回实现 `ILLMProvider` 接口的对象
3. 支持通过配置自动选择实现类型

#### Scenario: Use Native LLM Provider
**Given** 系统配置使用native实现
**When** 用户创建LLM提供者
**Then** 系统应：
1. 创建 `NativeLLMProvider` 实例
2. 包装现有 `LLMService` 为接口实现
3. 保持现有功能完全兼容

#### Scenario: Switch LLM Implementation at Runtime
**Given** 系统已初始化 `ComponentManager`
**When** 用户调用 `switch_llm_implementation()` 切换实现
**Then** 系统应：
1. 创建新的LLM提供者实例
2. 替换现有LLM提供者
3. 保持其他组件不变
4. 支持后续请求使用新实现

### Requirement: LLM Factory Pattern
系统 SHALL 提供 `LLMFactory` 工厂类，支持根据配置创建不同的LLM提供者实现。

**Rationale**: 使用工厂模式封装对象创建逻辑，统一创建入口，支持动态选择实现。

#### Scenario: Create from Configuration
**Given** 配置文件包含 `llm.implementation` 配置项
**When** 用户调用 `LLMFactory.create_from_config(config)`
**Then** 系统应：
1. 读取配置中的实现类型
2. 根据实现类型创建对应的LLM提供者
3. 如果实现类型不可用，返回错误或fallback到默认实现

#### Scenario: Create with Explicit Implementation
**Given** 系统已实现多种LLM提供者
**When** 用户调用 `LLMFactory.create(implementation, config)`
**Then** 系统应：
1. 根据指定的实现类型创建LLM提供者
2. 如果实现类型不支持，抛出 `ValueError`
3. 如果实现依赖不可用（如LangChain未安装），抛出适当的错误
