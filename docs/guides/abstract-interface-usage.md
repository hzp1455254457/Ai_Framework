# 抽象接口架构使用指南

本指南介绍如何使用抽象接口架构来切换和组装不同的实现。

## 概述

抽象接口架构通过定义统一的接口，支持多种实现（Native、LangChain、LangGraph），可以灵活切换和组装。

## 核心概念

### 接口层

所有组件都通过抽象接口访问：

- `ILLMProvider`: LLM提供者接口
- `IAgentEngine`: Agent引擎接口
- `IToolManager`: 工具管理器接口
- `IMemory`: 记忆管理接口
- `IWorkflow`: 工作流接口
- `IChain`: 链式调用接口

### 工厂层

通过工厂类创建具体实现：

- `LLMFactory`: 创建LLM提供者
- `AgentFactory`: 创建Agent引擎
- `ToolFactory`: 创建工具管理器
- `MemoryFactory`: 创建记忆管理器
- `WorkflowFactory`: 创建工作流

### 实现层

支持三种实现：

- **Native**: 自研实现（默认）
- **LangChain**: LangChain框架实现
- **LangGraph**: LangGraph框架实现

## 基本使用

### 方式1：使用工厂类

```python
from core.factories import LLMFactory, AgentFactory, ToolFactory, MemoryFactory

# 创建组件
llm_provider = LLMFactory.create("native", config)
tool_manager = ToolFactory.create("native", config)
memory = MemoryFactory.create("native", config)
agent = AgentFactory.create(
    "native",
    config,
    llm_provider=llm_provider,
    tool_manager=tool_manager,
    memory=memory
)

# 初始化
await llm_provider.initialize()
await agent.initialize()

# 使用
result = await agent.run_task("查询天气")
```

### 方式2：使用ComponentManager

```python
from core.composition import ComponentManager

# 创建组件管理器
manager = ComponentManager(config)
await manager.initialize()

# 使用组件
result = await manager.agent_engine.run_task("查询天气")
```

### 方式3：从配置创建

```python
from core.factories import LLMFactory, AgentFactory

# 从配置自动创建
llm_provider = LLMFactory.create_from_config(config)
agent = AgentFactory.create_from_config(config)
```

## 切换实现

### 通过配置切换

修改 `config/default.yaml`：

```yaml
# 切换到LangChain实现
llm:
  implementation: "langchain"
agent:
  implementation: "langchain"
tools:
  implementation: "langchain"
memory:
  implementation: "langchain"
```

### 运行时切换

```python
from core.composition import ComponentManager

manager = ComponentManager(config)
await manager.initialize()

# 运行时切换LLM实现
manager.switch_llm_implementation("langchain")

# 运行时切换Agent实现
manager.switch_agent_implementation("langchain")
```

## 混合使用

可以混合使用不同的实现：

### 示例1：LangChain Agent + Native工具

```yaml
# config/default.yaml
agent:
  implementation: "langchain"
tools:
  implementation: "native"  # 自研工具会自动转换为LangChain工具
```

### 示例2：Native LLM + LangChain Agent

```yaml
# config/default.yaml
llm:
  implementation: "native"
agent:
  implementation: "langchain"  # 会自动使用Native LLM（通过包装器）
```

### 示例3：LangChain记忆 + Native工具

```yaml
# config/default.yaml
memory:
  implementation: "langchain"
tools:
  implementation: "native"
```

## 组件组装

### 手动组装

```python
from core.factories import LLMFactory, AgentFactory, ToolFactory, MemoryFactory

# 创建各个组件
llm = LLMFactory.create("native", config)
tools = ToolFactory.create("langchain", config)
memory = MemoryFactory.create("native", config)

# 组装Agent（注入依赖）
agent = AgentFactory.create(
    "langchain",
    config,
    llm_provider=llm,
    tool_manager=tools,
    memory=memory
)
```

### 自动组装（使用ComponentManager）

```python
from core.composition import ComponentManager

# ComponentManager会自动根据配置组装组件
manager = ComponentManager(config)
await manager.initialize()

# 所有组件已自动组装完成
# manager.llm_provider
# manager.tool_manager
# manager.memory
# manager.agent_engine
```

## 最佳实践

### 1. 优先使用ComponentManager

ComponentManager提供了统一的组件管理接口，推荐使用：

```python
manager = ComponentManager(config)
await manager.initialize()
result = await manager.agent_engine.run_task("任务")
```

### 2. 配置驱动

通过配置文件选择实现，而不是硬编码：

```yaml
# ✅ 推荐：通过配置选择
agent:
  implementation: "langchain"
```

```python
# ❌ 不推荐：硬编码实现类型
agent = AgentFactory.create("langchain", config)  # 硬编码
```

### 3. 渐进式迁移

可以逐个模块迁移，不需要一次性全部迁移：

```yaml
# 阶段1：只迁移Agent
agent:
  implementation: "langchain"

# 阶段2：迁移工具
tools:
  implementation: "langchain"

# 阶段3：完全迁移
llm:
  implementation: "langchain"
memory:
  implementation: "langchain"
```

### 4. 利用混合使用

充分利用不同实现的优势：

- **LangChain Agent**: 丰富的Agent类型和工具生态
- **Native工具**: 自定义业务逻辑
- **LangGraph工作流**: 复杂的状态机和工作流

## 常见问题

### Q: 如何选择实现类型？

A: 
- **Native**: 默认选择，完全自研，性能最优
- **LangChain**: 需要丰富的工具生态和Agent类型
- **LangGraph**: 需要复杂的工作流编排

### Q: 切换实现会影响性能吗？

A: 
- Native实现性能最优
- LangChain/LangGraph实现可能有少量包装开销，但通常可以忽略
- 可以通过性能测试选择最适合的实现

### Q: 可以同时使用多种实现吗？

A: 可以！不同组件可以使用不同的实现，例如LangChain Agent + Native工具。

### Q: 如何添加新的实现？

A: 
1. 实现对应的接口（如 `ILLMProvider`）
2. 在工厂类中注册新实现
3. 更新配置文件支持新实现类型

## 更多信息

- [配置文档](./configuration.md)
- [迁移指南](./migration-to-abstract-interface.md)
- [LangChain使用指南](./langchain-usage.md)
- [抽象接口架构设计](../design/abstract-interface-architecture.md)
