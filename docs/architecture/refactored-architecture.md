# 重构后架构设计文档

本文档说明重构后的AI框架架构设计，包括新架构的组件、设计决策和集成方案。

## 版本信息

- **文档版本**: 2.0
- **更新日期**: 2026-01-23
- **架构版本**: v2.0

## 架构概述

重构后的AI框架在保持原有轻量级、模块化设计的基础上，引入了以下核心能力：

1. **智能路由和负载均衡**：支持多种路由策略和负载均衡算法，自动选择最优模型
2. **性能优化**：HTTP连接池、请求缓存、去重、批量处理，显著提升性能
3. **成本管理**：Token使用跟踪、成本计算、预算管理和优化建议
4. **监控和可观测性**：Prometheus指标采集、分布式请求追踪、结构化日志
5. **主流框架集成**：LiteLLM（统一多模型接口）、LangChain（AI应用开发）、LangGraph（工作流编排），全部可选

## 设计原则

1. **向后兼容**：现有API和配置完全兼容，无需修改代码即可使用
2. **可选集成**：所有新功能和框架集成都是可选的，可通过配置启用/禁用
3. **渐进式迁移**：支持逐步迁移到新架构，无需一次性重构
4. **性能优先**：在保持灵活性的同时，优化关键路径性能
5. **可观测性**：提供完整的监控和追踪能力，便于问题诊断和性能优化

## 架构层次

### 1. 应用层（Application Layer）

提供HTTP API、CLI工具和Web界面等外部接口。

- **FastAPI应用**：提供RESTful API
- **CLI工具**：命令行接口
- **Web前端**：Vue3前端应用

### 2. 抽象接口层（Abstract Interface Layer）

定义统一的组件接口，支持多种实现灵活切换。

**核心接口**：
- `ILLMProvider`: LLM提供者接口
- `IAgentEngine`: Agent引擎接口
- `IToolManager`: 工具管理器接口
- `IMemory`: 记忆管理接口
- `IWorkflow`: 工作流接口
- `IChain`: 链式调用接口

**工厂层**：
- `LLMFactory`: LLM提供者工厂
- `AgentFactory`: Agent引擎工厂
- `ToolFactory`: 工具管理器工厂
- `MemoryFactory`: 记忆管理器工厂
- `WorkflowFactory`: 工作流工厂

**组合管理器**：
- `ComponentManager`: 统一管理所有组件，支持运行时切换和组件组装

**实现层**：
- **Native实现**: 自研实现（默认）
- **LangChain实现**: LangChain框架实现
- **LangGraph实现**: LangGraph框架实现

### 3. 核心服务层（Core Service Layer）

核心业务逻辑，包括LLM服务、Agent引擎、视觉服务等。

#### 2.1 LLM服务（LLMService）

**核心组件**：

- **适配器工厂（AdapterFactory）**：动态创建适配器实例，支持实例缓存
- **适配器注册表（AdapterRegistry）**：管理适配器注册和模型映射
- **适配器路由层（AdapterRouter）**：智能路由和负载均衡
- **连接池管理器（ConnectionPoolManager）**：HTTP连接复用
- **请求缓存（RequestCache）**：缓存请求结果
- **请求去重器（RequestDeduplicator）**：合并重复请求
- **批量处理器（BatchProcessor）**：批量处理请求
- **成本管理器（CostManager）**：成本跟踪和预算管理
- **指标采集器（MetricsCollector）**：Prometheus指标采集
- **请求追踪器（RequestTracer）**：分布式请求追踪

**路由策略**：

- `COST_FIRST`：成本优先，选择成本最低的适配器
- `PERFORMANCE_FIRST`：性能优先，选择响应最快的适配器
- `AVAILABILITY_FIRST`：可用性优先，选择最健康的适配器
- `BALANCED`：平衡模式，综合考虑成本、性能和可用性
- `MANUAL`：手动指定适配器

**负载均衡策略**：

- `ROUND_ROBIN`：轮询
- `WEIGHTED_ROUND_ROBIN`：加权轮询
- `LEAST_CONNECTIONS`：最少连接
- `RANDOM`：随机

#### 2.2 Agent引擎（AgentEngine）

**抽象接口架构**：

- **接口抽象**：通过 `IAgentEngine` 接口统一Agent引擎
- **多种实现**：支持Native、LangChain、LangGraph三种实现
- **灵活切换**：通过配置或运行时切换实现
- **混合使用**：可以混合使用不同实现的组件

**可选集成**：

- **LangChain集成**：提供链式思维、工具集成、记忆管理
- **LangGraph集成**：提供工作流编排和状态机管理

### 3. 适配器层（Adapter Layer）

统一的多模型适配器接口，支持各种AI服务提供商。

**内置适配器**：

- OpenAI适配器
- 通义千问（Qwen）适配器
- 豆包（Doubao）适配器
- DeepSeek适配器
- Claude适配器
- Ollama适配器
- LiteLLM适配器（可选）

**适配器特性**：

- 统一接口：所有适配器实现 `BaseLLMAdapter` 接口
- 模型能力描述：通过 `ModelCapability` 描述模型特性
- 成本信息：提供Token成本信息
- 健康检查：支持健康状态检查
- 连接池集成：支持HTTP连接池复用

### 4. 基础设施层（Infrastructure Layer）

提供配置管理、缓存、日志、存储等基础设施能力。

#### 4.1 配置管理（ConfigManager）

**新功能**：

- 配置版本管理：支持配置版本（v1.0 → v2.0）
- 自动迁移：配置自动迁移工具
- 配置验证：完整的配置验证机制
- 敏感数据加密：API密钥加密存储
- 环境变量覆盖：支持环境变量覆盖配置

#### 4.2 缓存管理（CacheManager）

支持多种缓存后端（内存、Redis等）。

#### 4.3 日志管理（LogManager）

结构化日志、数据脱敏。

#### 4.4 存储管理（StorageManager）

支持多种存储后端（SQLite、向量数据库等）。

## 设计决策

### 1. 可选依赖策略

**决策**：LiteLLM、LangChain、LangGraph作为可选依赖

**理由**：
- 保持框架的轻量级特性
- 用户可以根据需求选择安装
- 不影响核心功能的可用性

**实现**：
- 使用 `try/except ImportError` 处理可选依赖
- 提供占位符类，支持优雅降级
- 配置中明确标注可选功能

### 2. 路由层设计

**决策**：独立的适配器路由层

**理由**：
- 解耦适配器选择逻辑
- 支持多种路由策略
- 便于扩展和测试

**实现**：
- `AdapterRouter` 类管理路由决策
- 策略模式实现不同路由策略
- 集成负载均衡器

### 3. 性能优化策略

**决策**：多层性能优化

**理由**：
- 连接池：减少连接建立开销
- 请求缓存：避免重复请求
- 请求去重：合并并发重复请求
- 批量处理：提高吞吐量

**实现**：
- 所有优化功能可配置启用/禁用
- 默认启用，但可关闭以降低内存使用

### 4. 监控和可观测性

**决策**：集成Prometheus和分布式追踪

**理由**：
- 标准化指标格式
- 支持与现有监控系统集成
- 提供完整的请求追踪能力

**实现**：
- `MetricsCollector` 采集Prometheus指标
- `RequestTracer` 提供分布式追踪
- 所有监控功能可配置启用/禁用

## 集成方案

### LiteLLM集成

**位置**：`core/llm/adapters/litellm_adapter.py`

**功能**：
- 统一多模型接口
- 自动路由和负载均衡
- 成本计算

**使用**：
```python
from core.llm.adapters.litellm_adapter import LiteLLMAdapter

adapter = LiteLLMAdapter(config)
await adapter.initialize()
```

### LangChain集成

**位置**：`core/agent/langchain_integration.py`

**功能**：
- 链式思维处理
- 工具集成
- 记忆管理

**使用**：
```python
from core.agent.langchain_integration import LangChainIntegration

integration = LangChainIntegration(config)
```

### LangGraph集成

**位置**：`core/agent/langgraph_integration.py`

**功能**：
- 工作流定义
- 状态机管理
- 复杂任务编排

**使用**：
```python
from core.agent.langgraph_integration import LangGraphIntegration

integration = LangGraphIntegration(config)
```

## 向后兼容性

### 配置兼容性

- ✅ 旧配置格式（v1.0）仍然有效
- ✅ 配置自动迁移（v1.0 → v2.0）
- ✅ 可选功能可禁用

### API兼容性

- ✅ 旧API调用方式仍然有效
- ✅ 响应格式与旧版本一致
- ✅ 错误处理与旧版本一致

### 适配器兼容性

- ✅ 旧适配器接口仍然有效
- ✅ 适配器注册方式向后兼容

## 性能指标

### 延迟指标

- 平均延迟：< 50ms（启用优化）
- 最大延迟：< 100ms（启用优化）
- 首块延迟：< 50ms（流式响应）

### 并发性能

- 20个并发请求总时间：< 150ms

### 内存使用

- 100次请求后内存增长：< 50MB

## 扩展性

### 添加新适配器

1. 创建适配器类，继承 `BaseLLMAdapter`
2. 实现必需的方法
3. 设置 `ModelCapability` 和成本信息
4. 适配器会自动被发现和注册

### 添加新路由策略

1. 创建策略类，继承 `RoutingStrategyBase`
2. 实现 `select_adapter` 方法
3. 在 `AdapterRouter` 中注册策略

### 添加新负载均衡算法

1. 在 `LoadBalancer` 中添加新策略
2. 实现对应的选择逻辑

## 最佳实践

1. **启用性能优化**：生产环境建议启用所有性能优化功能
2. **配置监控**：启用监控功能，便于问题排查和性能分析
3. **成本管理**：设置成本预算，避免意外超支
4. **路由策略选择**：根据业务需求选择合适的路由策略
5. **连接池配置**：根据并发量调整连接池大小

## 相关文档

- [配置管理指南](../guides/configuration.md)
- [性能优化指南](../guides/performance-optimization.md)
- [成本管理指南](../guides/cost-management.md)
- [迁移指南](../guides/migration.md)
- [API参考文档](../api/api-reference.md)
