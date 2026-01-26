# LangChain迁移指南

本指南介绍如何从Native实现迁移到LangChain实现。

## 迁移概述

通过抽象接口架构，迁移到LangChain非常简单，只需修改配置文件即可，无需修改代码。

## 迁移步骤

### 步骤1：安装LangChain

```bash
pip install langchain
```

### 步骤2：更新配置文件

修改 `config/default.yaml`：

```yaml
# 从Native实现迁移到LangChain
llm:
  implementation: "langchain"  # 改为langchain

agent:
  implementation: "langchain"  # 改为langchain
  agent_type: "openai-functions"  # 选择Agent类型

tools:
  implementation: "langchain"  # 改为langchain

memory:
  implementation: "langchain"  # 改为langchain
```

### 步骤3：验证功能

运行现有代码，验证功能是否正常：

```python
from core.factories import AgentFactory

# 代码无需修改，只需配置改变
agent = AgentFactory.create_from_config(config)
await agent.initialize()
result = await agent.run_task("测试任务")
```

## 渐进式迁移

可以逐个模块迁移，不需要一次性全部迁移：

### 阶段1：只迁移Agent

```yaml
llm:
  implementation: "native"  # 保持Native
agent:
  implementation: "langchain"  # 迁移到LangChain
tools:
  implementation: "native"  # 保持Native（会自动转换）
memory:
  implementation: "native"  # 保持Native（会自动转换）
```

### 阶段2：迁移工具

```yaml
llm:
  implementation: "native"  # 保持Native
agent:
  implementation: "langchain"  # 已迁移
tools:
  implementation: "langchain"  # 迁移到LangChain
memory:
  implementation: "native"  # 保持Native
```

### 阶段3：完全迁移

```yaml
llm:
  implementation: "langchain"  # 迁移到LangChain
agent:
  implementation: "langchain"  # 已迁移
tools:
  implementation: "langchain"  # 已迁移
memory:
  implementation: "langchain"  # 迁移到LangChain
```

## 混合使用场景

### 场景1：LangChain Agent + 自研工具

**适用场景**：需要使用LangChain的Agent能力，但工具是自研的。

**配置**：
```yaml
agent:
  implementation: "langchain"
tools:
  implementation: "native"  # 自研工具会自动转换为LangChain工具
```

**优势**：
- 使用LangChain的Agent能力
- 保持自研工具的灵活性
- 工具自动转换，无需修改代码

### 场景2：Native LLM + LangChain Agent

**适用场景**：需要使用自研LLM，但Agent使用LangChain。

**配置**：
```yaml
llm:
  implementation: "native"
agent:
  implementation: "langchain"  # 会自动使用Native LLM（通过包装器）
```

**优势**：
- 保持自研LLM的优势
- 使用LangChain的Agent能力
- LLM自动包装，无需修改代码

### 场景3：LangChain记忆 + Native工具

**适用场景**：需要使用LangChain的记忆功能，但工具是自研的。

**配置**：
```yaml
memory:
  implementation: "langchain"
tools:
  implementation: "native"
```

**优势**：
- 使用LangChain的记忆功能
- 保持自研工具的灵活性

## 回滚方案

如果迁移后出现问题，可以轻松回滚：

### 方案1：配置回滚

只需修改配置文件：

```yaml
llm:
  implementation: "native"  # 改回native
agent:
  implementation: "native"  # 改回native
# ...
```

### 方案2：部分回滚

只回滚有问题的模块：

```yaml
agent:
  implementation: "native"  # 只回滚Agent
# 其他模块保持LangChain
```

## 迁移检查清单

- [ ] 安装LangChain：`pip install langchain`
- [ ] 更新配置文件：修改 `implementation` 配置项
- [ ] 验证LLM功能：测试聊天功能
- [ ] 验证Agent功能：测试任务执行
- [ ] 验证工具功能：测试工具调用
- [ ] 验证记忆功能：测试消息管理
- [ ] 性能测试：验证性能是否满足要求
- [ ] 功能测试：验证所有功能正常

## 常见问题

### Q: 迁移后工具不工作？

A: 检查工具是否正确注册，自研工具会自动转换为LangChain工具。

### Q: 迁移后性能下降？

A: LangChain包装可能带来少量开销，但通常可以忽略。如果性能问题严重，可以考虑只迁移部分模块。

### Q: 可以同时使用两种实现吗？

A: 可以！不同组件可以使用不同的实现，例如LangChain Agent + Native工具。

### Q: 迁移后需要修改代码吗？

A: 不需要！通过抽象接口架构，只需修改配置即可。

## 更多信息

- [LangChain使用指南](./langchain-usage.md)
- [配置文档](./configuration.md)
- [抽象接口架构设计](../design/abstract-interface-architecture.md)
