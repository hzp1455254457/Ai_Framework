# LangChain使用指南

本指南介绍如何在AI框架中使用LangChain实现。

## 概述

AI框架通过抽象接口架构支持LangChain实现，可以完全使用LangChain生态的LLM、Agent、工具和记忆功能。

## 配置LangChain实现

### 基本配置

在 `config/default.yaml` 中配置使用LangChain实现：

```yaml
# LLM配置
llm:
  implementation: "langchain"  # 使用LangChain LLM实现

# Agent配置
agent:
  implementation: "langchain"  # 使用LangChain Agent实现
  agent_type: "openai-functions"  # Agent类型
  verbose: false  # 是否输出详细日志
  return_intermediate_steps: true  # 是否返回中间步骤

# 工具配置
tools:
  implementation: "langchain"  # 使用LangChain工具实现

# 记忆配置
memory:
  implementation: "langchain"  # 使用LangChain记忆实现
  type: "buffer"  # 记忆类型：buffer/summary
```

### 支持的Agent类型

- `openai-functions`: OpenAI Functions Agent（推荐，支持Function Calling）
- `openai-multi-functions`: OpenAI Multi-Functions Agent
- `react`: ReAct Agent（推理和行动）
- `self-ask-with-search`: Self-Ask-With-Search Agent

## 使用示例

### 示例1：完全LangChain模式

所有组件都使用LangChain实现：

```python
from core.factories import LLMFactory, AgentFactory, ToolFactory, MemoryFactory

# 创建组件
llm_provider = LLMFactory.create("langchain", config)
tool_manager = ToolFactory.create("langchain", config)
memory = MemoryFactory.create("langchain", config)
agent = AgentFactory.create("langchain", config, llm_provider, tool_manager, memory)

# 初始化
await agent.initialize()

# 执行任务
result = await agent.run_task("查询北京天气")
print(result["content"])
```

### 示例2：混合模式

LangChain Agent + 自研工具：

```yaml
# config/default.yaml
agent:
  implementation: "langchain"
tools:
  implementation: "native"  # 使用自研工具（会自动转换为LangChain工具）
```

```python
from core.factories import AgentFactory, ToolFactory
from core.agent.tools import Tool

# 创建自研工具
async def get_weather(city: str) -> str:
    return f"{city}的天气是晴天"

tool = Tool(
    name="get_weather",
    description="获取城市天气",
    parameters={
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名称"}
        },
        "required": ["city"]
    },
    func=get_weather
)

# 注册工具（会自动转换为LangChain工具）
tool_manager = ToolFactory.create("langchain", config)
tool_manager.register(tool)

# 创建Agent（会使用转换后的工具）
agent = AgentFactory.create("langchain", config, llm_provider, tool_manager, memory)
```

## 工具转换

自研工具会自动转换为LangChain工具：

1. **JSON Schema → Pydantic模型**：自动将工具参数schema转换为Pydantic模型
2. **异步函数包装**：将自研工具的异步函数包装为LangChain Tool
3. **Schema获取**：支持获取Function Calling格式的schema

## 记忆转换

自研记忆会自动转换为LangChain记忆：

1. **消息格式转换**：自动转换消息格式（user/assistant/tool/system）
2. **工具消息处理**：支持tool_call_id等特殊字段
3. **长期记忆**：可选使用LangChain的持久化功能

## 最佳实践

1. **优先使用LangChain Agent**：LangChain提供了丰富的Agent类型和工具
2. **混合使用**：可以LangChain Agent + 自研工具，充分利用两者优势
3. **配置驱动**：通过配置文件切换实现，无需修改代码
4. **渐进式迁移**：可以逐个模块迁移到LangChain

## 常见问题

### Q: LangChain未安装怎么办？

A: 如果LangChain未安装，系统会自动fallback到Native实现。要使用LangChain，请安装：

```bash
pip install langchain
```

### Q: 如何选择Agent类型？

A: 
- 如果使用支持Function Calling的模型（如GPT-3.5/GPT-4），推荐使用 `openai-functions`
- 如果需要更强的推理能力，可以使用 `react`
- 如果需要搜索功能，可以使用 `self-ask-with-search`

### Q: 工具转换会影响性能吗？

A: 工具转换的开销很小，主要是函数包装和schema转换，对性能影响可以忽略。

### Q: 可以同时使用LangChain和Native实现吗？

A: 可以！不同组件可以使用不同的实现，例如：
- LangChain Agent + Native工具
- Native LLM + LangChain Agent
- LangChain记忆 + Native工具

## 更多信息

- [配置文档](./configuration.md)
- [迁移指南](./langchain-migration.md)
- [抽象接口架构设计](../design/abstract-interface-architecture.md)
