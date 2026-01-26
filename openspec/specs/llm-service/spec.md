# llm-service Specification

## Purpose
提供统一的多模型LLM接口，支持多种AI服务提供商，通过适配器模式实现不同提供商的统一调用接口。支持流式输出、上下文管理、Token计算、自动重试、成本估算和适配器健康检查功能。
## Requirements
### Requirement: Adapter Health Check
系统 SHALL 提供适配器健康检查功能，检测适配器可用性并支持自动故障转移。

**Rationale**: 在生产环境中，需要监控适配器状态，确保服务可用性，并在适配器故障时自动切换到可用适配器。

#### Scenario: Check Adapter Health Status
**Given** 系统已配置多个 LLM 适配器
**When** 系统执行适配器健康检查
**Then** 系统应：
1. 对每个适配器执行健康检查（轻量级 API 调用）
2. 返回适配器的健康状态（HEALTHY、UNHEALTHY、UNKNOWN）
3. 记录健康检查结果和时间戳
4. 在健康检查失败时记录错误信息

#### Scenario: Automatic Failover on Adapter Failure
**Given** 系统配置了多个 LLM 适配器，其中一个适配器不可用
**When** 用户发送 LLM 请求
**Then** 系统应：
1. 检测到主适配器不可用
2. 自动切换到可用的备用适配器
3. 使用备用适配器处理请求
4. 记录故障转移事件

#### Scenario: Query Adapter Health via API
**Given** 健康检查 API 已部署
**When** 用户发送 GET 请求到 `/api/health/adapters`
**Then** 系统应：
1. 执行所有适配器的健康检查
2. 返回所有适配器的健康状态
3. 返回健康检查结果和时间戳
4. 支持按服务类型过滤（LLM、Vision 等）

#### Scenario: Handle Health Check Timeout
**Given** 适配器健康检查已配置超时时间
**When** 健康检查请求超时
**Then** 系统应：
1. 检测到超时
2. 将适配器标记为 UNHEALTHY
3. 记录超时错误
4. 不阻塞其他适配器的健康检查

#### Scenario: Configure Health Check Interval
**Given** 用户需要配置健康检查间隔
**When** 用户在配置文件中设置健康检查间隔
**Then** 系统应：
1. 读取并应用健康检查间隔配置
2. 按配置的间隔执行健康检查
3. 支持不同环境的不同配置（开发/生产）

### Requirement: Adapter Router
系统 SHALL 提供适配器路由功能，根据路由策略智能选择适配器。

**Rationale**: 支持多个适配器时，需要根据成本、性能、可用性等因素智能选择最适合的适配器。

#### Scenario: Route by Cost Strategy
**Given** 系统配置了多个适配器，启用了成本优先路由策略
**When** 用户发送 LLM 请求，指定成本优先策略
**Then** 系统应：
1. 计算所有可用适配器的预估成本
2. 选择成本最低的适配器
3. 使用选定的适配器处理请求
4. 记录路由决策和成本信息

#### Scenario: Route by Performance Strategy
**Given** 系统配置了多个适配器，启用了性能优先路由策略
**When** 用户发送 LLM 请求，指定性能优先策略
**Then** 系统应：
1. 评估所有可用适配器的性能指标（延迟、吞吐量等）
2. 选择性能最优的适配器
3. 使用选定的适配器处理请求
4. 记录路由决策和性能指标

#### Scenario: Route by Availability Strategy
**Given** 系统配置了多个适配器，启用了可用性优先路由策略
**When** 用户发送 LLM 请求，指定可用性优先策略
**Then** 系统应：
1. 检查所有适配器的健康状态
2. 选择健康状态最好的适配器
3. 使用选定的适配器处理请求
4. 记录路由决策和健康状态

#### Scenario: Route by Balanced Strategy
**Given** 系统配置了多个适配器，启用了平衡模式路由策略
**When** 用户发送 LLM 请求，指定平衡模式策略
**Then** 系统应：
1. 综合考虑成本、性能、可用性等因素
2. 选择综合评分最高的适配器
3. 使用选定的适配器处理请求
4. 记录路由决策和评分信息

#### Scenario: Route by Model Capability
**Given** 系统配置了多个适配器，每个适配器有不同的能力标签
**When** 用户发送 LLM 请求，指定所需的能力（如推理能力、创造力等）
**Then** 系统应：
1. 筛选出满足能力要求的适配器
2. 根据路由策略从候选适配器中选择
3. 使用选定的适配器处理请求
4. 记录路由决策和能力匹配信息

### Requirement: Load Balancing
系统 SHALL 提供负载均衡功能，在多个适配器间分配请求。

**Rationale**: 当多个适配器可用时，需要合理分配请求，避免单个适配器过载。

#### Scenario: Round Robin Load Balancing
**Given** 系统配置了多个适配器，启用了轮询负载均衡
**When** 用户发送多个 LLM 请求
**Then** 系统应：
1. 按顺序将请求分配到不同适配器
2. 确保请求均匀分布
3. 记录负载均衡决策

#### Scenario: Weighted Round Robin Load Balancing
**Given** 系统配置了多个适配器，每个适配器有不同的权重
**When** 用户发送多个 LLM 请求
**Then** 系统应：
1. 根据权重分配请求
2. 权重高的适配器接收更多请求
3. 记录负载均衡决策和权重信息

#### Scenario: Least Connections Load Balancing
**Given** 系统配置了多个适配器，启用了最少连接负载均衡
**When** 用户发送 LLM 请求
**Then** 系统应：
1. 统计每个适配器的当前连接数
2. 选择连接数最少的适配器
3. 使用选定的适配器处理请求
4. 记录负载均衡决策和连接数信息

### Requirement: LiteLLM Integration
系统 SHALL 支持集成LiteLLM作为可选统一接口层。

**Rationale**: LiteLLM提供了统一的多模型接口，支持100+模型提供商，可以降低维护成本并扩展模型支持。

#### Scenario: Use LiteLLM Adapter
**Given** 系统已安装LiteLLM，配置启用了LiteLLM模式
**When** 用户发送 LLM 请求
**Then** 系统应：
1. 检测到LiteLLM可用
2. 使用LiteLLMAdapter处理请求
3. 调用LiteLLM统一接口
4. 返回标准格式的响应

#### Scenario: Fallback to Custom Adapter
**Given** 系统配置了LiteLLM，但LiteLLM不可用
**When** 用户发送 LLM 请求
**Then** 系统应：
1. 检测到LiteLLM不可用
2. 自动切换到自研适配器
3. 使用自研适配器处理请求
4. 记录fallback事件

#### Scenario: Configure LiteLLM Mode
**Given** 用户需要配置LiteLLM模式
**When** 用户在配置文件中设置LiteLLM相关配置
**Then** 系统应：
1. 读取并应用LiteLLM配置
2. 初始化LiteLLMAdapter
3. 支持启用/禁用LiteLLM模式
4. 支持配置LiteLLM的模型映射

### Requirement: Performance Optimization
系统 SHALL 提供性能优化功能，包括连接池、缓存、批量处理等。

**Rationale**: 性能优化可以提升响应速度，降低资源消耗，改善用户体验。

#### Scenario: HTTP Connection Pooling
**Given** 系统启用了HTTP连接池
**When** 用户发送多个 LLM 请求
**Then** 系统应：
1. 复用HTTP连接，避免重复建立连接
2. 减少连接建立的开销
3. 提高请求处理速度
4. 记录连接池使用情况

#### Scenario: Request Caching
**Given** 系统启用了请求缓存
**When** 用户发送相同的 LLM 请求
**Then** 系统应：
1. 检查缓存中是否存在相同请求
2. 如果存在，直接返回缓存结果
3. 如果不存在，调用适配器并缓存结果
4. 记录缓存命中率

#### Scenario: Request Deduplication
**Given** 系统启用了请求去重
**When** 用户同时发送多个相同的 LLM 请求
**Then** 系统应：
1. 检测到重复请求
2. 合并重复请求，只调用一次适配器
3. 将结果返回给所有请求者
4. 记录去重统计信息

#### Scenario: Batch Request Processing
**Given** 系统启用了批量处理
**When** 用户发送多个 LLM 请求
**Then** 系统应：
1. 将请求批量收集
2. 使用批量API调用适配器
3. 批量返回结果
4. 提高处理效率

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

