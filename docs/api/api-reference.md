# API参考文档

## 📋 文档说明

本文档提供AI框架所有HTTP API接口的详细参考，包括请求参数、响应格式、使用示例和错误处理。

**API基础信息**：
- **Base URL**: `http://localhost:8000/api/v1`
- **API版本**: v1
- **文档格式**: OpenAPI 3.0
- **交互式文档**: 访问 `http://localhost:8000/docs` 查看Swagger UI

---

## 📚 目录

- [LLM API](#llm-api)
  - [聊天接口](#1-聊天接口)
  - [流式聊天接口](#2-流式聊天接口)
  - [获取模型列表](#3-获取模型列表)
- [Agent API](#agent-api)
  - [任务执行接口](#1-任务执行接口)
  - [工具注册接口](#2-工具注册接口)
  - [工具列表接口](#3-工具列表接口)
  - [向量语义搜索接口](#4-向量语义搜索接口)
  - [多Agent协作任务接口](#5-多agent协作任务接口)
  - [多Agent协作状态接口](#6-多agent协作状态接口)
- [Health API](#health-api)
  - [健康检查接口](#1-健康检查接口)
- [错误处理](#错误处理)
- [使用示例](#使用示例)

---

## LLM API

LLM API提供大语言模型的聊天和对话功能。

**Base Path**: `/api/v1/llm`

### 1. 聊天接口

发送消息列表，获取LLM响应。

**端点**: `POST /api/v1/llm/chat`

**请求体**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "你好"
    }
  ],
  "model": "qwen-turbo",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**请求参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| messages | Array[Message] | 是 | - | 消息列表，至少包含一条消息 |
| model | String | 否 | 服务默认模型 | 模型名称（如 "qwen-turbo", "gpt-3.5-turbo"） |
| temperature | Float | 否 | 0.7 | 温度参数，控制输出随机性（0.0-2.0） |
| max_tokens | Integer | 否 | - | 最大token数 |

**Message对象**:
```json
{
  "role": "user",  // 角色：user/assistant/system
  "content": "消息内容"
}
```

**响应**:
```json
{
  "content": "你好！我是AI助手。",
  "model": "qwen-turbo",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  },
  "metadata": {}
}
```

**响应字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| content | String | LLM响应内容 |
| model | String | 使用的模型名称 |
| usage | UsageInfo | Token使用信息 |
| metadata | Object | 其他元数据 |

**UsageInfo对象**:
```json
{
  "prompt_tokens": 10,      // 提示Token数量
  "completion_tokens": 20,  // 完成Token数量
  "total_tokens": 30        // 总Token数量
}
```

**状态码**:
- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `500 Internal Server Error`: 服务器内部错误

**示例**:

```bash
# 使用curl
curl -X POST "http://localhost:8000/api/v1/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "model": "qwen-turbo",
    "temperature": 0.7
  }'
```

```python
# 使用Python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/llm/chat",
        json={
            "messages": [
                {"role": "user", "content": "你好"}
            ],
            "model": "qwen-turbo",
            "temperature": 0.7
        }
    )
    result = response.json()
    print(result["content"])
```

---

### 2. 流式聊天接口

发送消息列表，以流式方式返回LLM响应（Server-Sent Events格式）。

**端点**: `POST /api/v1/llm/chat/stream`

**请求体**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "写一首关于春天的诗"
    }
  ],
  "model": "qwen-turbo",
  "temperature": 0.7
}
```

**请求参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| messages | Array[Message] | 是 | - | 消息列表 |
| model | String | 否 | 服务默认模型 | 模型名称 |
| temperature | Float | 否 | 0.7 | 温度参数（0.0-2.0） |

**响应格式**: Server-Sent Events (SSE)

**响应示例**:
```
data: {"content": "春", "model": "qwen-turbo", "usage": {...}, "metadata": {}}

data: {"content": "天", "model": "qwen-turbo", "usage": {...}, "metadata": {}}

data: [DONE]
```

**状态码**:
- `200 OK`: 流式响应开始
- `400 Bad Request`: 请求参数错误
- `500 Internal Server Error`: 服务器内部错误

**示例**:

```python
# 使用Python处理流式响应
import httpx
import json

async with httpx.AsyncClient() as client:
    async with client.stream(
        "POST",
        "http://localhost:8000/api/v1/llm/chat/stream",
        json={
            "messages": [{"role": "user", "content": "写一首诗"}],
            "model": "qwen-turbo"
        }
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = line[6:]  # 移除 "data: " 前缀
                if data == "[DONE]":
                    break
                chunk = json.loads(data)
                print(chunk["content"], end="", flush=True)
```

---

### 3. 获取模型列表

获取所有支持的模型列表。

**端点**: `GET /api/v1/llm/models`

**请求参数**: 无

**响应**:
```json
[
  "qwen-turbo",
  "qwen-plus",
  "qwen-max",
  "gpt-3.5-turbo",
  "gpt-4",
  "deepseek-chat"
]
```

**状态码**:
- `200 OK`: 请求成功
- `500 Internal Server Error`: 服务器内部错误

**示例**:

```bash
# 使用curl
curl "http://localhost:8000/api/v1/llm/models"
```

```python
# 使用Python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/api/v1/llm/models")
    models = response.json()
    print(f"支持的模型: {models}")
```

---

## Agent API

Agent API提供智能体（Agent）的任务执行、工具管理和协作功能。

**Base Path**: `/api/v1/agent`

### 1. 任务执行接口

接收任务描述，执行Agent工作流，返回执行结果。

**端点**: `POST /api/v1/agent/task`

**请求体**:
```json
{
  "task": "查询北京天气",
  "conversation_id": "conv-123",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 1000,
  "use_planner": false,
  "context": {}
}
```

**请求参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| task | String | 是 | - | 任务描述 |
| conversation_id | String | 否 | - | 对话ID，用于长期记忆 |
| model | String | 否 | 服务默认模型 | 模型名称 |
| temperature | Float | 否 | 0.7 | 温度参数（0.0-2.0） |
| max_tokens | Integer | 否 | - | 最大token数 |
| use_planner | Boolean | 否 | false | 是否使用任务规划器 |
| context | Object | 否 | {} | 上下文信息（用于规划器） |

**响应**:
```json
{
  "content": "北京今天晴天，温度25°C",
  "tool_calls": [
    {
      "tool": "get_weather",
      "arguments": {"city": "北京"},
      "result": "晴天，25°C"
    }
  ],
  "iterations": 2,
  "metadata": {
    "model": "gpt-3.5-turbo",
    "usage": {
      "prompt_tokens": 50,
      "completion_tokens": 30,
      "total_tokens": 80
    }
  }
}
```

**响应字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| content | String | 任务执行结果 |
| tool_calls | Array[Object] | 工具调用记录 |
| iterations | Integer | 迭代次数 |
| metadata | Object | 其他元数据 |

**状态码**:
- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误或Agent错误
- `500 Internal Server Error`: 服务器内部错误

**示例**:

```bash
# 使用curl
curl -X POST "http://localhost:8000/api/v1/agent/task" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "查询北京天气",
    "model": "gpt-3.5-turbo"
  }'
```

```python
# 使用Python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/agent/task",
        json={
            "task": "查询北京天气",
            "model": "gpt-3.5-turbo",
            "use_planner": False
        }
    )
    result = response.json()
    print(f"执行结果: {result['content']}")
    print(f"工具调用: {result['tool_calls']}")
```

---

### 2. 工具注册接口

在运行时注册新工具，扩展Agent能力。

**端点**: `POST /api/v1/agent/tools/register`

**请求体**:
```json
{
  "name": "get_weather",
  "description": "获取城市天气",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "城市名称"
      }
    },
    "required": ["city"]
  },
  "allow_override": false
}
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | String | 是 | 工具名称 |
| description | String | 是 | 工具描述 |
| parameters | Object | 是 | 工具参数schema（JSON Schema格式） |
| allow_override | Boolean | 否 | 是否允许覆盖已存在的工具（默认false） |

**响应**:
```json
{
  "success": true,
  "message": "工具定义已接收: get_weather（注意：执行函数需要在服务端预先定义）",
  "tool_name": "get_weather"
}
```

**响应字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| success | Boolean | 是否注册成功 |
| message | String | 响应消息 |
| tool_name | String | 工具名称 |

**状态码**:
- `200 OK`: 注册成功
- `400 Bad Request`: 请求参数错误
- `409 Conflict`: 工具已存在（且未设置allow_override）
- `500 Internal Server Error`: 服务器内部错误

**注意**: 当前版本中，工具的执行函数需要在服务端预先定义。此接口仅用于注册工具定义，实际执行需要预先注册工具函数。

**示例**:

```python
# 使用Python注册工具
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/agent/tools/register",
        json={
            "name": "get_weather",
            "description": "获取城市天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    }
                },
                "required": ["city"]
            }
        }
    )
    result = response.json()
    print(f"注册结果: {result['message']}")
```

---

### 3. 工具列表接口

获取已注册的工具列表。

**端点**: `GET /api/v1/agent/tools`

**请求参数**: 无

**响应**:
```json
{
  "tools": ["get_weather", "search_web"],
  "schemas": [
    {
      "name": "get_weather",
      "description": "获取城市天气",
      "parameters": {
        "type": "object",
        "properties": {
          "city": {
            "type": "string",
            "description": "城市名称"
          }
        },
        "required": ["city"]
      }
    }
  ],
  "count": 2
}
```

**响应字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| tools | Array[String] | 工具名称列表 |
| schemas | Array[Object] | 工具schema列表 |
| count | Integer | 工具数量 |

**状态码**:
- `200 OK`: 请求成功
- `500 Internal Server Error`: 服务器内部错误

**示例**:

```bash
# 使用curl
curl "http://localhost:8000/api/v1/agent/tools"
```

---

### 4. 向量语义搜索接口

在长期记忆中根据语义相似度搜索相关对话历史。

**端点**: `POST /api/v1/agent/memory/search`

**请求体**:
```json
{
  "query": "关于天气的对话",
  "top_k": 5,
  "conversation_id": "conv-123"
}
```

**请求参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| query | String | 是 | - | 查询文本 |
| top_k | Integer | 否 | 5 | 返回结果数量（1-100） |
| conversation_id | String | 否 | - | 限制搜索的对话ID（可选） |

**响应**:
```json
{
  "results": [
    {
      "conversation_id": "conv-123",
      "similarity": 0.95,
      "metadata": {}
    }
  ],
  "count": 1
}
```

**响应字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| results | Array[Object] | 搜索结果列表 |
| count | Integer | 结果数量 |

**状态码**:
- `200 OK`: 请求成功
- `400 Bad Request`: 长期记忆未启用或请求参数错误
- `500 Internal Server Error`: 服务器内部错误

**注意**: 需要先配置向量后端才能使用此功能。

**示例**:

```python
# 使用Python进行语义搜索
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/agent/memory/search",
        json={
            "query": "关于天气的对话",
            "top_k": 5
        }
    )
    result = response.json()
    print(f"找到 {result['count']} 条相关对话")
```

---

### 5. 多Agent协作任务接口

使用多个Agent协同执行任务。

**端点**: `POST /api/v1/agent/collaboration/task`

**请求体**:
```json
{
  "task": "查询北京天气",
  "strategy": "round_robin",
  "agent_ids": ["agent1", "agent2"],
  "conversation_id": "conv-123",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7
}
```

**请求参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| task | String | 是 | - | 任务描述 |
| strategy | String | 否 | "round_robin" | 任务分配策略：round_robin/load_balancing/specialization |
| agent_ids | Array[String] | 否 | - | 指定使用的Agent ID列表（可选） |
| conversation_id | String | 否 | - | 对话ID |
| model | String | 否 | - | 模型名称 |
| temperature | Float | 否 | 0.7 | 温度参数（0.0-2.0） |

**响应**:
```json
{
  "content": "聚合后的结果",
  "agent_results": [
    {
      "content": "北京今天晴天",
      "tool_calls": [],
      "iterations": 1,
      "metadata": {}
    }
  ],
  "strategy": "round_robin",
  "metadata": {}
}
```

**响应字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| content | String | 聚合后的执行结果 |
| agent_results | Array[Object] | 各Agent的执行结果 |
| strategy | String | 使用的分配策略 |
| metadata | Object | 其他元数据 |

**状态码**:
- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误或协作错误
- `500 Internal Server Error`: 服务器内部错误

**示例**:

```python
# 使用Python执行多Agent协作任务
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/agent/collaboration/task",
        json={
            "task": "查询北京天气",
            "strategy": "round_robin"
        }
    )
    result = response.json()
    print(f"协作结果: {result['content']}")
```

---

### 6. 多Agent协作状态接口

获取多Agent协作状态信息。

**端点**: `GET /api/v1/agent/collaboration/status`

**请求参数**: 无

**响应**:
```json
{
  "agents": [
    {
      "agent_id": "agent1",
      "specialization": "weather",
      "current_load": 2
    }
  ],
  "strategy": "round_robin",
  "total_agents": 1
}
```

**响应字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| agents | Array[Object] | Agent状态列表 |
| strategy | String | 当前使用的分配策略 |
| total_agents | Integer | Agent总数 |

**状态码**:
- `200 OK`: 请求成功
- `500 Internal Server Error`: 服务器内部错误

**示例**:

```bash
# 使用curl
curl "http://localhost:8000/api/v1/agent/collaboration/status"
```

---

## Health API

Health API提供健康检查和系统状态查询功能。

**Base Path**: `/api/v1/health`

### 1. 健康检查接口

检查服务健康状态，返回服务版本、可用适配器和模型列表。

**端点**: `GET /api/v1/health/`

**请求参数**: 无

**响应**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "adapters": ["qwen-adapter", "deepseek-adapter"],
  "models": ["qwen-turbo", "qwen-plus", "deepseek-chat"]
}
```

**响应字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| status | String | 服务状态：healthy/unhealthy |
| version | String | 服务版本 |
| adapters | Array[String] | 可用适配器列表 |
| models | Array[String] | 支持的模型列表 |

**状态码**:
- `200 OK`: 请求成功（无论健康状态如何）

**示例**:

```bash
# 使用curl
curl "http://localhost:8000/api/v1/health/"
```

```python
# 使用Python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/api/v1/health/")
    health = response.json()
    print(f"服务状态: {health['status']}")
    print(f"可用模型: {health['models']}")
```

---

## 错误处理

### 错误响应格式

所有错误响应都遵循统一格式：

```json
{
  "detail": "错误描述信息"
}
```

### 常见错误码

| 状态码 | 说明 | 可能原因 |
|--------|------|---------|
| 400 Bad Request | 请求参数错误 | 缺少必填参数、参数格式错误、参数值无效 |
| 401 Unauthorized | 未授权 | API密钥无效或缺失 |
| 404 Not Found | 资源不存在 | 端点路径错误 |
| 409 Conflict | 资源冲突 | 工具名称已存在 |
| 500 Internal Server Error | 服务器内部错误 | 服务异常、LLM调用失败、数据库错误 |

### 错误处理示例

```python
import httpx

async with httpx.AsyncClient() as client:
    try:
        response = await client.post(
            "http://localhost:8000/api/v1/llm/chat",
            json={"messages": [{"role": "user", "content": "你好"}]}
        )
        response.raise_for_status()  # 抛出HTTP错误
        result = response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            print(f"请求参数错误: {e.response.json()['detail']}")
        elif e.response.status_code == 500:
            print(f"服务器错误: {e.response.json()['detail']}")
        else:
            print(f"HTTP错误 {e.response.status_code}: {e.response.json()['detail']}")
```

---

## 使用示例

### 完整示例：多轮对话

```python
import httpx
import asyncio

async def multi_turn_chat():
    """多轮对话示例"""
    async with httpx.AsyncClient() as client:
        base_url = "http://localhost:8000/api/v1"
        conversation = []
        
        # 第一轮对话
        conversation.append({"role": "user", "content": "你好"})
        response = await client.post(
            f"{base_url}/llm/chat",
            json={
                "messages": conversation,
                "model": "qwen-turbo"
            }
        )
        result = response.json()
        print(f"AI: {result['content']}")
        conversation.append({"role": "assistant", "content": result['content']})
        
        # 第二轮对话
        conversation.append({"role": "user", "content": "你叫什么名字？"})
        response = await client.post(
            f"{base_url}/llm/chat",
            json={
                "messages": conversation,
                "model": "qwen-turbo"
            }
        )
        result = response.json()
        print(f"AI: {result['content']}")

asyncio.run(multi_turn_chat())
```

### 完整示例：Agent任务执行

```python
import httpx
import asyncio

async def agent_task_example():
    """Agent任务执行示例"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/agent/task",
            json={
                "task": "查询北京天气，然后告诉我适合穿什么衣服",
                "model": "gpt-3.5-turbo",
                "use_planner": True
            }
        )
        result = response.json()
        print(f"任务结果: {result['content']}")
        print(f"工具调用: {result['tool_calls']}")
        print(f"迭代次数: {result['iterations']}")

asyncio.run(agent_task_example())
```

---

## 📚 相关文档

- [快速开始指南](../guides/getting-started.md) - 新手上手指南
- [架构方案文档](../../AI框架架构方案文档.md) - 架构设计参考
- [API变更日志](api-changelog.md) - API变更历史

---

## 🔄 文档更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-01-22 | v1.0 | 初始版本，创建完整的API参考文档 | - |

---

**说明**: 本文档与代码实现同步更新。如有疑问或发现文档与代码不一致，请及时反馈。
