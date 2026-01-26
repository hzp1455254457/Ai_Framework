# 迁移到抽象接口架构指南

本指南介绍如何将现有代码迁移到抽象接口架构。

## 迁移概述

抽象接口架构通过适配器模式保持向后兼容，现有代码可以无缝迁移，无需修改业务逻辑。

## 迁移步骤

### 步骤1：了解新架构

抽象接口架构的核心：

1. **接口层**: 定义统一的接口规范
2. **工厂层**: 通过工厂创建具体实现
3. **实现层**: 多种实现（Native、LangChain、LangGraph）
4. **组合管理器**: 统一管理所有组件

### 步骤2：更新导入

#### 旧代码（直接使用具体类）

```python
# ❌ 旧方式：直接导入具体类
from core.llm.service import LLMService
from core.agent.engine import AgentEngine
from core.agent.tools import ToolRegistry
from core.agent.memory import ShortTermMemory

# 直接创建实例
llm_service = LLMService(config)
agent_engine = AgentEngine(config, llm_service, tool_registry, memory)
```

#### 新代码（使用工厂或接口）

```python
# ✅ 新方式1：使用工厂
from core.factories import LLMFactory, AgentFactory, ToolFactory, MemoryFactory

llm_provider = LLMFactory.create_from_config(config)
tool_manager = ToolFactory.create_from_config(config)
memory = MemoryFactory.create_from_config(config)
agent = AgentFactory.create_from_config(
    config,
    llm_provider=llm_provider,
    tool_manager=tool_manager,
    memory=memory
)

# ✅ 新方式2：使用ComponentManager（推荐）
from core.composition import ComponentManager

manager = ComponentManager(config)
await manager.initialize()
agent = manager.agent_engine
```

### 步骤3：更新初始化

#### 旧代码

```python
# ❌ 旧方式：直接初始化
llm_service = LLMService(config)
await llm_service.initialize()

agent_engine = AgentEngine(config, llm_service, tool_registry, memory)
await agent_engine.initialize()
```

#### 新代码

```python
# ✅ 新方式：使用工厂或ComponentManager
manager = ComponentManager(config)
await manager.initialize()  # 自动初始化所有组件
```

### 步骤4：更新API调用

#### 旧代码

```python
# ❌ 旧方式：直接调用方法
response = await llm_service.chat(messages)
result = await agent_engine.run_task("任务")
```

#### 新代码

```python
# ✅ 新方式：通过接口调用（接口保持不变）
response = await manager.llm_provider.chat(messages)
result = await manager.agent_engine.run_task("任务")
```

## 迁移场景

### 场景1：简单迁移（使用ComponentManager）

**适用场景**: 只需要使用默认Native实现

**迁移步骤**:

1. 替换导入
2. 使用ComponentManager
3. 其他代码保持不变

```python
# 旧代码
from core.llm.service import LLMService
from core.agent.engine import AgentEngine

llm_service = LLMService(config)
agent_engine = AgentEngine(config, llm_service, ...)

# 新代码
from core.composition import ComponentManager

manager = ComponentManager(config)
await manager.initialize()
# manager.llm_provider 等同于 llm_service
# manager.agent_engine 等同于 agent_engine
```

### 场景2：使用工厂模式

**适用场景**: 需要灵活选择实现类型

**迁移步骤**:

1. 使用工厂创建组件
2. 通过配置选择实现类型

```python
# 新代码
from core.factories import LLMFactory, AgentFactory

# 从配置创建（自动选择实现类型）
llm_provider = LLMFactory.create_from_config(config)
agent = AgentFactory.create_from_config(config)

# 或手动指定实现类型
llm_provider = LLMFactory.create("langchain", config)
agent = AgentFactory.create("langchain", config, ...)
```

### 场景3：混合使用

**适用场景**: 需要混合使用不同实现

**迁移步骤**:

1. 分别创建不同实现的组件
2. 手动组装

```python
# 新代码
from core.factories import LLMFactory, AgentFactory, ToolFactory

# Native LLM
llm = LLMFactory.create("native", config)

# LangChain工具
tools = ToolFactory.create("langchain", config)

# LangChain Agent（使用Native LLM和LangChain工具）
agent = AgentFactory.create(
    "langchain",
    config,
    llm_provider=llm,
    tool_manager=tools,
    memory=memory
)
```

## 向后兼容性

### 现有代码继续工作

抽象接口架构通过适配器模式保持向后兼容：

- **Native适配器**: 包装现有 `LLMService`、`AgentEngine` 等
- **接口兼容**: 接口方法与现有API保持一致
- **配置兼容**: 默认使用Native实现，无需修改配置

### 无需修改的代码

以下代码无需修改：

```python
# ✅ 这些代码继续工作
response = await llm_provider.chat(messages)
result = await agent_engine.run_task("任务")
tools = tool_manager.list_tools()
messages = memory.get_messages()
```

## 迁移检查清单

- [ ] 更新导入语句（使用工厂或ComponentManager）
- [ ] 更新初始化代码（使用工厂或ComponentManager）
- [ ] 验证功能正常（运行现有测试）
- [ ] 更新配置文件（可选，添加实现选择配置）
- [ ] 性能测试（验证性能是否满足要求）
- [ ] 更新文档（如有自定义使用方式）

## 常见问题

### Q: 迁移后需要修改业务逻辑吗？

A: **不需要**。抽象接口架构通过适配器模式保持向后兼容，业务逻辑代码无需修改。

### Q: 迁移后性能会下降吗？

A: **不会**。Native实现直接使用现有代码，没有额外开销。LangChain/LangGraph实现可能有少量包装开销，但通常可以忽略。

### Q: 可以逐步迁移吗？

A: **可以**。可以逐个模块迁移，不需要一次性全部迁移。

### Q: 迁移后如何切换实现？

A: 通过配置文件或运行时切换：

```yaml
# 配置文件
agent:
  implementation: "langchain"
```

```python
# 运行时切换
manager.switch_agent_implementation("langchain")
```

## 迁移示例

### 完整迁移示例

```python
# ========== 旧代码 ==========
from core.llm.service import LLMService
from core.agent.engine import AgentEngine
from core.agent.tools import ToolRegistry
from core.agent.memory import ShortTermMemory

# 创建组件
llm_service = LLMService(config)
await llm_service.initialize()

tool_registry = ToolRegistry()
memory = ShortTermMemory()

agent_engine = AgentEngine(
    config,
    llm_service,
    tool_registry,
    memory
)
await agent_engine.initialize()

# 使用
result = await agent_engine.run_task("查询天气")

# ========== 新代码 ==========
from core.composition import ComponentManager

# 创建组件管理器（自动创建和组装所有组件）
manager = ComponentManager(config)
await manager.initialize()

# 使用（接口保持不变）
result = await manager.agent_engine.run_task("查询天气")
```

## 更多信息

- [抽象接口架构使用指南](./abstract-interface-usage.md)
- [配置文档](./configuration.md)
- [抽象接口架构设计](../design/abstract-interface-architecture.md)
