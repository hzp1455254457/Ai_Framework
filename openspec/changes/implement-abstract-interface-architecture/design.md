# 抽象接口架构设计

## 设计原则

1. **接口抽象**：所有核心功能都定义抽象接口
2. **实现解耦**：具体实现与接口完全分离
3. **策略模式**：通过策略选择不同实现
4. **工厂模式**：通过工厂创建具体实现
5. **依赖注入**：通过配置注入依赖

## 架构设计

### 整体架构

```
应用层（API/CLI）
  ↓
抽象接口层（ILLMProvider、IAgentEngine、IToolManager、IMemory、IWorkflow、IChain）
  ↓
工厂层（LLMFactory、AgentFactory、ToolFactory、MemoryFactory、WorkflowFactory）
  ↓
实现层（Native/LangChain/LangGraph）
  ↓
组合管理器（ComponentManager）
```

### 核心抽象接口

#### 1. ILLMProvider（LLM提供者接口）
- `chat()` - 发送聊天请求
- `stream_chat()` - 流式聊天
- `get_available_models()` - 获取可用模型列表
- `health_check()` - 健康检查

#### 2. IAgentEngine（Agent引擎接口）
- `run_task()` - 执行任务
- `register_tool()` - 注册工具
- `get_tools()` - 获取工具列表
- `clear_memory()` - 清空记忆
- `initialize()` - 初始化
- `cleanup()` - 清理资源

#### 3. IToolManager（工具管理器接口）
- `register()` - 注册工具
- `execute()` - 执行工具
- `list_tools()` - 列出所有工具
- `get_tool_schema()` - 获取工具schema
- `get_all_schemas()` - 获取所有工具schema

#### 4. IMemory（记忆管理接口）
- `add_message()` - 添加消息
- `get_messages()` - 获取消息列表
- `clear()` - 清空记忆
- `save()` - 保存记忆（长期）
- `load()` - 加载记忆（长期）

#### 5. IWorkflow（工作流接口）
- `execute()` - 执行工作流
- `add_node()` - 添加节点
- `add_edge()` - 添加边
- `get_state()` - 获取当前状态

#### 6. IChain（链式调用接口）
- `invoke()` - 执行链
- `add_link()` - 添加链节点
- `get_links()` - 获取链节点列表

### 工厂模式实现

#### LLMFactory
- `create(implementation, config)` - 创建LLM提供者
- `create_from_config(config)` - 从配置创建

#### AgentFactory
- `create(implementation, config, llm_provider, tool_manager, memory)` - 创建Agent引擎
- `create_from_config(config)` - 从配置创建

#### ToolFactory
- `create(implementation, config)` - 创建工具管理器
- `create_from_config(config)` - 从配置创建

#### MemoryFactory
- `create(implementation, config, storage_manager)` - 创建记忆管理器
- `create_from_config(config)` - 从配置创建

### 具体实现

#### Native实现（自研）
- `NativeLLMProvider` - 包装现有LLMService
- `NativeAgentEngine` - 包装现有AgentEngine
- `NativeToolManager` - 包装现有ToolRegistry
- `NativeMemory` - 包装现有ShortTermMemory和LongTermMemory

#### LangChain实现
- `LangChainLLMProvider` - LangChain LLM包装器
- `LangChainAgentEngine` - LangChain Agent包装器
- `LangChainToolManager` - LangChain Tools包装器
- `LangChainMemory` - LangChain Memory包装器

#### LangGraph实现
- `LangGraphWorkflow` - LangGraph工作流包装器
- `LangGraphAgentEngine` - LangGraph Agent包装器

### 组合管理器

#### ComponentManager
- 负责创建和管理所有组件
- 支持运行时切换实现
- 支持依赖注入和组件组装
- 提供统一的组件访问接口

### 配置设计

```yaml
# LLM配置
llm:
  implementation: "native"  # native/litellm/langchain

# Agent配置
agent:
  implementation: "native"  # native/langchain/langgraph

# 工具配置
tools:
  implementation: "native"  # native/langchain

# 记忆配置
memory:
  implementation: "native"  # native/langchain

# 运行时切换配置
runtime:
  allow_switching: true  # 允许运行时切换实现
  hot_reload: false      # 是否支持热重载
```

## 设计决策

### 1. 为什么使用抽象接口而不是直接继承？

**决策**：使用抽象接口（ABC）而不是直接继承，因为：
- 接口与实现完全分离，可以独立替换
- 支持多实现共存，可以同时使用多种实现
- 符合依赖倒置原则，高层模块不依赖低层模块

### 2. 为什么使用工厂模式？

**决策**：使用工厂模式，因为：
- 封装对象创建逻辑，统一创建入口
- 支持根据配置动态选择实现
- 便于扩展新的实现类型

### 3. 为什么需要组合管理器？

**决策**：需要组合管理器，因为：
- 统一管理所有组件，避免分散创建
- 支持运行时切换，提供统一切换接口
- 支持依赖注入，自动组装组件

### 4. 如何保证向后兼容？

**决策**：通过适配器模式保证向后兼容：
- 现有实现通过适配器包装为接口实现
- 默认使用native实现，保持现有行为
- 配置兼容，现有配置继续有效

## 目录结构

```
core/
├── interfaces/              # 抽象接口层
│   ├── __init__.py
│   ├── llm.py              # ILLMProvider
│   ├── agent.py            # IAgentEngine
│   ├── tools.py            # IToolManager
│   ├── memory.py           # IMemory
│   ├── workflow.py          # IWorkflow
│   └── chain.py            # IChain
│
├── factories/              # 工厂层
│   ├── __init__.py
│   ├── llm_factory.py      # LLMFactory
│   ├── agent_factory.py    # AgentFactory
│   ├── tool_factory.py     # ToolFactory
│   ├── memory_factory.py   # MemoryFactory
│   └── workflow_factory.py # WorkflowFactory
│
├── implementations/        # 具体实现层
│   ├── native/            # 自研实现
│   │   ├── __init__.py
│   │   ├── native_llm.py
│   │   ├── native_agent.py
│   │   ├── native_tools.py
│   │   └── native_memory.py
│   │
│   ├── langchain/         # LangChain实现
│   │   ├── __init__.py
│   │   ├── langchain_llm.py
│   │   ├── langchain_agent.py
│   │   ├── langchain_tools.py
│   │   └── langchain_memory.py
│   │
│   └── langgraph/         # LangGraph实现
│       ├── __init__.py
│       ├── langgraph_workflow.py
│       └── langgraph_agent.py
│
└── composition/           # 组合管理
    ├── __init__.py
    └── component_manager.py
```

## 使用示例

### 示例1：使用自研实现

```python
config = {
    "llm": {"implementation": "native"},
    "agent": {"implementation": "native"},
    "tools": {"implementation": "native"},
    "memory": {"implementation": "native"}
}

manager = ComponentManager(config)
await manager.initialize()
result = await manager.agent_engine.run_task("查询天气")
```

### 示例2：混合使用

```python
config = {
    "llm": {"implementation": "native"},      # 自研LLM
    "agent": {"implementation": "langchain"}, # LangChain Agent
    "tools": {"implementation": "native"},    # 自研工具
    "memory": {"implementation": "langchain"} # LangChain记忆
}

manager = ComponentManager(config)
await manager.initialize()
result = await manager.agent_engine.run_task("查询天气")
```

### 示例3：运行时切换

```python
manager = ComponentManager(config)
await manager.initialize()

# 使用自研实现
result1 = await manager.agent_engine.run_task("任务1")

# 切换到LangChain
manager.switch_agent_implementation("langchain")
result2 = await manager.agent_engine.run_task("任务2")
```
