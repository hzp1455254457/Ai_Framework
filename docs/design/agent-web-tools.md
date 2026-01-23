# Agent 互联网访问工具设计文档

## 概述

本文档描述 Agent 系统的互联网访问工具设计，包括搜索引擎查询和网页内容获取功能。

## 功能特性

### 1. Web Search（搜索引擎查询）

**功能描述：**
- 通过搜索引擎查询互联网内容
- 支持多种搜索引擎（DuckDuckGo、Google、Bing）
- 返回搜索结果摘要列表（标题、URL、摘要）

**使用场景：**
- 查询实时信息（新闻、股价、天气等）
- 搜索技术文档和教程
- 获取最新资讯

**配置示例：**
```yaml
agent:
  web_tools:
    web_search:
      enabled: true
      search_engine: "duckduckgo"  # duckduckgo/google/bing
      api_key: ""  # Google/Bing需要，DuckDuckGo不需要
      timeout: 10.0
      max_retries: 2
```

### 2. Fetch Webpage（网页内容获取）

**功能描述：**
- 获取指定URL的网页内容
- 解析HTML提取主要文本
- 过滤脚本、样式等无关内容

**使用场景：**
- 分析网页内容
- 获取文档信息
- 提取文章内容

**配置示例：**
```yaml
agent:
  web_tools:
    fetch_webpage:
      enabled: true
      timeout: 10.0
      max_retries: 2
      max_length: 10000  # 最大文本长度
```

## 技术实现

### 架构设计

```
AgentEngine
  └── ToolRegistry
      └── Web Tools
          ├── web_search
          └── fetch_webpage
```

### 依赖库

- **httpx**: 异步HTTP客户端（已有）
- **beautifulsoup4**: HTML解析库（新增）

### 错误处理

- 网络超时：自动重试（可配置重试次数）
- 无效URL：返回友好错误信息
- 不支持的内容类型：返回错误提示
- API密钥缺失：返回配置提示

### 安全考虑

- 仅访问公开可访问的内容
- 支持超时控制，避免长时间等待
- 内容长度限制，防止内存溢出
- 遵守网站使用条款（未来可扩展robots.txt支持）

## 使用示例

### 在Agent任务中使用

```python
# Agent会自动调用工具
task = "查询Python异步编程的最新教程"
result = await engine.run_task(task)
# Agent会调用web_search工具查询，然后返回结果
```

### 直接使用工具函数

```python
from core.agent.tools.web_tools import web_search, fetch_webpage

# 搜索
results = await web_search("Python async programming", max_results=5)

# 获取网页
content = await fetch_webpage("https://example.com/article")
```

### 工具Schema（Function Calling格式）

**web_search:**
```json
{
  "name": "web_search",
  "description": "通过搜索引擎查询互联网内容",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "搜索查询关键词"
      },
      "max_results": {
        "type": "integer",
        "description": "最大返回结果数（1-20，默认5）",
        "minimum": 1,
        "maximum": 20,
        "default": 5
      }
    },
    "required": ["query"]
  }
}
```

**fetch_webpage:**
```json
{
  "name": "fetch_webpage",
  "description": "获取指定URL的网页内容并提取主要文本",
  "parameters": {
    "type": "object",
    "properties": {
      "url": {
        "type": "string",
        "description": "要获取的网页URL（必须是http或https协议）"
      }
    },
    "required": ["url"]
  }
}
```

## 配置说明

### 完整配置示例

```yaml
agent:
  web_tools:
    enabled: true  # 是否启用互联网工具
    web_search:
      enabled: true
      search_engine: "duckduckgo"  # duckduckgo/google/bing
      api_key: ""  # Google/Bing API密钥（可选）
      timeout: 10.0
      max_retries: 2
    fetch_webpage:
      enabled: true
      timeout: 10.0
      max_retries: 2
      max_length: 10000
```

### 搜索引擎选择

1. **DuckDuckGo**（推荐，默认）
   - 无需API密钥
   - 免费使用
   - 隐私友好

2. **Google Custom Search**
   - 需要API密钥和Search Engine ID
   - 需要配置：`api_key` 和 `cx`（Search Engine ID）

3. **Bing Search API**
   - 需要API密钥
   - 需要配置：`api_key`

## 限制和注意事项

1. **内容长度限制**：fetch_webpage默认最大返回10000字符，可通过配置调整
2. **超时控制**：所有请求都有超时限制，默认10秒
3. **重试机制**：网络失败时自动重试，默认最多2次
4. **内容过滤**：自动过滤脚本、样式等无关内容
5. **协议限制**：仅支持http和https协议

## 未来扩展

- [ ] 支持更多搜索引擎
- [ ] 添加内容缓存机制
- [ ] 支持robots.txt检查
- [ ] 支持代理配置
- [ ] 支持请求频率限制
- [ ] 支持Cookie和Session
