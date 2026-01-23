# Design: 互联网访问工具实现

## Context
Agent 系统需要访问互联网内容以扩展能力。当前工具系统已支持工具注册和调用，但缺少互联网访问能力。需要新增工具来支持：
1. 搜索引擎查询
2. 网页内容获取和解析

## Goals / Non-Goals

### Goals
- 提供 `web_search` 工具，支持通过搜索引擎查询互联网内容
- 提供 `fetch_webpage` 工具，支持获取并解析网页内容
- 工具可通过配置启用/禁用
- 支持超时和重试机制
- 工具结果格式化为 Agent 可理解的文本格式

### Non-Goals
- 不实现完整的浏览器渲染（仅获取 HTML 内容）
- 不实现复杂的网页交互（如登录、表单提交等）
- 不实现图片/视频下载（仅获取文本内容）
- 不实现爬虫功能（仅支持公开可访问的内容）

## Decisions

### Decision: 使用 httpx 作为 HTTP 客户端
- **Rationale**: 项目已使用 `httpx` 作为异步 HTTP 客户端，保持一致性
- **Alternatives considered**: 
  - `requests`: 同步库，不符合项目异步优先原则
  - `aiohttp`: 功能类似，但项目已统一使用 `httpx`

### Decision: 使用 beautifulsoup4 解析 HTML
- **Rationale**: 简单易用，支持多种解析器，适合提取文本内容
- **Alternatives considered**:
  - `lxml`: 性能更好但依赖更复杂
  - 正则表达式: 不够健壮，难以处理复杂 HTML

### Decision: 支持多种搜索引擎 API
- **Rationale**: 不同环境可能需要不同的搜索引擎（Google、Bing、DuckDuckGo 等）
- **Implementation**: 通过配置选择搜索引擎，支持 API 密钥配置
- **Default**: 优先使用 DuckDuckGo（无需 API 密钥），支持 Google/Bing（需要 API 密钥）

### Decision: 工具结果格式化为文本
- **Rationale**: Agent 需要文本格式的结果，便于 LLM 理解和处理
- **Format**: 
  - `web_search`: 返回搜索结果摘要列表（标题、URL、摘要）
  - `fetch_webpage`: 返回网页主要内容文本（去除 HTML 标签、脚本等）

## Risks / Trade-offs

### Risk: 网络请求可能失败或超时
- **Mitigation**: 实现超时和重试机制，提供友好的错误信息

### Risk: 网页内容可能包含大量无关信息
- **Mitigation**: 使用 HTML 解析器提取主要内容（如 `<main>`, `<article>` 标签），过滤脚本和样式

### Risk: 搜索引擎 API 可能需要密钥和费用
- **Mitigation**: 
  - 默认使用无需密钥的搜索引擎（如 DuckDuckGo）
  - 支持配置 API 密钥
  - 提供清晰的配置文档

### Risk: 可能违反网站的使用条款
- **Mitigation**: 
  - 仅访问公开可访问的内容
  - 遵守 robots.txt（可选，未来扩展）
  - 添加使用说明和免责声明

## Migration Plan

### Phase 1: 基础实现
1. 实现 `web_search` 和 `fetch_webpage` 工具函数
2. 添加基础配置项
3. 在 AgentEngine 中注册工具（可选）

### Phase 2: 测试和优化
1. 编写单元测试和集成测试
2. 优化错误处理和性能
3. 添加文档

### Phase 3: 扩展功能（可选）
1. 支持更多搜索引擎
2. 添加内容缓存（避免重复请求）
3. 支持内容过滤和摘要生成

## Open Questions
- [ ] 是否需要支持代理配置？
- [ ] 是否需要实现请求频率限制？
- [ ] 是否需要支持 Cookie 和 Session？
