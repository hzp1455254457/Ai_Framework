# LLM服务模块

## 模块概述

本模块提供统一的多模型LLM接口，支持多种AI服务提供商，实现对话、流式输出、上下文管理等功能。

**在整体架构中的位置**：
- 属于核心服务层
- 依赖基础设施层（配置管理、日志管理）
- 被应用层（API、CLI、Web）调用

**核心职责**：
- 统一的多模型LLM接口
- 适配器管理和切换
- 上下文管理
- Token计算和成本估算

---

## 模块结构

```
core/llm/
├── __init__.py          # 模块导出
├── service.py           # LLM服务主类
├── context.py           # 对话上下文管理
├── models.py            # 数据模型
├── adapters/            # 适配器实现
│   ├── __init__.py
│   ├── base.py          # 适配器基类
│   ├── openai_adapter.py
│   ├── claude_adapter.py
│   └── ollama_adapter.py
└── README.md            # 本文件
```

---

## 核心API

### LLMService（LLM服务主类）

**主要方法**：
- `chat(messages, model, temperature, max_tokens)` - 发送聊天请求
- `stream_chat(messages, model, temperature)` - 流式聊天
- `calculate_tokens(text, model)` - 计算Token数量
- `register_adapter(adapter)` - 注册适配器

**使用示例**：
```python
from core.llm import LLMService
from infrastructure.config import ConfigManager

# 加载配置
config = ConfigManager.load()

# 创建服务
service = LLMService(config)
await service.initialize()

# 发送聊天请求
messages = [{"role": "user", "content": "Hello"}]
response = await service.chat(messages, model="gpt-3.5-turbo")
print(response.content)
```

### ConversationContext（对话上下文）

**主要方法**：
- `add_message(role, content)` - 添加消息
- `get_messages()` - 获取消息列表
- `clear()` - 清空上下文

**使用示例**：
```python
from core.llm import ConversationContext

# 创建上下文
context = ConversationContext()

# 添加消息
context.add_message("user", "你好")
context.add_message("assistant", "你好！有什么可以帮助你的吗？")

# 获取消息列表
messages = context.get_messages()
```

---

## 支持的适配器

### 已实现的适配器

1. **DoubaoAdapter（豆包适配器）**
   - 提供商：字节跳动豆包AI
   - 模型：doubao-pro-4k, doubao-pro-32k等
   - API端点：https://ark.cn-beijing.volces.com/api/v3

2. **QwenAdapter（通义千问适配器）**
   - 提供商：阿里云通义千问
   - 模型：qwen-turbo, qwen-plus, qwen-max等
   - API端点：https://dashscope.aliyuncs.com/api/v1

3. **DeepSeekAdapter（DeepSeek适配器）**
   - 提供商：DeepSeek AI
   - 模型：deepseek-chat, deepseek-coder等
   - API端点：https://api.deepseek.com/v1

### 适配器的自动发现和注册

LLM服务支持适配器的自动发现和注册机制，无需手动注册适配器。

#### 自动发现机制

服务初始化时会自动：
1. 扫描`core/llm/adapters`目录下的所有适配器类
2. 识别`BaseLLMAdapter`的子类
3. 根据配置自动创建和注册适配器实例

#### 配置方式

**方式1：通过配置文件自动注册**

在配置文件中设置适配器配置：

```yaml
# config/default.yaml
llm:
  auto_discover_adapters: true  # 启用自动发现
  adapters:
    qwen-adapter:
      api_key: "your-qwen-key"
    deepseek-adapter:
      api_key: "your-deepseek-key"
    doubao-adapter:
      api_key: "your-doubao-key"
  
  # 模型到适配器的映射（可选）
  model_adapter_mapping:
    "qwen-turbo": "qwen-adapter"
    "deepseek-chat": "deepseek-adapter"
```

**方式2：手动注册适配器**

如果需要更多控制，可以手动注册：

```python
from core.llm import LLMService
from core.llm.adapters import DoubaoAdapter

# 创建服务（禁用自动发现）
config = {
    "llm": {
        "auto_discover_adapters": False
    }
}
service = LLMService(config)
await service.initialize()

# 手动注册适配器
adapter = DoubaoAdapter({"api_key": "your-key"})
await adapter.initialize()
service.register_adapter(adapter)
```

#### 使用示例

```python
from core.llm import LLMService
from infrastructure.config import ConfigManager

# 加载配置（包含适配器配置）
config = ConfigManager.load()

# 创建服务（自动发现和注册适配器）
service = LLMService(config)
await service.initialize()

# 使用服务（根据模型自动选择合适的适配器）
messages = [{"role": "user", "content": "Hello"}]
response = await service.chat(messages, model="qwen-turbo")  # 自动使用qwen-adapter
print(response.content)
```

### 适配器选择机制

服务会根据以下优先级选择适配器：

1. **模型映射**：如果配置了`model_adapter_mapping`，优先使用映射的适配器
2. **模糊匹配**：根据模型名称前缀匹配（如"qwen-*" → qwen-adapter）
3. **默认适配器**：使用配置的`default_adapter`
4. **第一个适配器**：如果没有匹配，使用第一个注册的适配器

## 依赖关系

### 依赖的其他模块
- `core/base/` - 基础服务类和适配器基类
- `infrastructure/config/` - 配置管理
- `infrastructure/log/` - 日志管理

### 外部依赖
- `httpx`：异步HTTP客户端（适配器使用）
- `tiktoken`：Token计算（可选）

### 被哪些模块依赖
- `api/routes/llm.py` - API路由
- `cli/commands/chat.py` - CLI命令
- `core/agent/` - Agent引擎

---

## 相关文档

- [LLM服务设计文档](../../docs/design/llm-service.md)
- [架构方案文档](../../AI框架架构方案文档.md)
- [基础服务框架设计文档](../../docs/design/base-service-framework.md)

---

## 更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-01-21 | 1.0 | 初始版本，实现LLM服务模块 | - |
