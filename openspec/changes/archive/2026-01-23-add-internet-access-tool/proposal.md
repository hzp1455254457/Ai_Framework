# Change: 新增大模型访问互联网能力查询的工具

## Why
当前 Agent 系统虽然支持工具调用，但缺少访问互联网内容的能力。大模型在执行任务时，经常需要查询实时信息、获取最新数据或访问网页内容。新增互联网访问工具可以显著扩展 Agent 的能力边界，使其能够：
- 查询实时信息（如天气、新闻、股价等）
- 获取网页内容进行分析
- 搜索互联网资源
- 访问 API 接口获取数据

## What Changes
- **ADDED**: 新增 `web_search` 工具，支持通过搜索引擎查询互联网内容
- **ADDED**: 新增 `fetch_webpage` 工具，支持获取并解析网页内容
- **ADDED**: 工具配置支持（超时、重试、内容过滤等）
- **MODIFIED**: Agent Engine 在初始化时自动注册互联网访问工具（可选）

## Impact
- **Affected specs**: `agent-engine` (新增工具相关需求)
- **Affected code**: 
  - `core/agent/tools.py` - 可能需要扩展工具基类
  - `core/agent/engine.py` - 工具注册逻辑
  - 新增 `core/agent/tools/web_tools.py` - 互联网访问工具实现
  - `api/routes/agent.py` - 可能需要暴露工具配置接口
- **Dependencies**: 
  - 需要 HTTP 客户端库（已有 `httpx`）
  - 可能需要 HTML 解析库（如 `beautifulsoup4` 或 `lxml`）
  - 可能需要搜索引擎 API（如 Google Search API、Bing Search API 或 DuckDuckGo）
