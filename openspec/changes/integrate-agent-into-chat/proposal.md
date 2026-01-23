# Change: 聊天对话集成Agent工具功能

## Why
当前聊天功能仅支持纯LLM对话，无法使用Agent工具（如互联网搜索、网页获取等）。用户需要在聊天中直接使用工具能力，而不需要切换到独立的Agent页面。集成Agent功能到聊天中可以：
- 提供统一的对话体验，用户无需切换页面
- 让聊天助手能够访问实时信息（通过web_search工具）
- 让聊天助手能够获取网页内容进行分析（通过fetch_webpage工具）
- 提升用户体验，实现"智能助手"的完整能力

## What Changes
- **MODIFIED**: 后端聊天API (`/api/v1/llm/chat`) 支持Agent模式，可选启用工具调用
- **MODIFIED**: 后端流式聊天API (`/api/v1/llm/chat/stream`) 支持Agent模式
- **ADDED**: 前端聊天界面新增Agent模式开关
- **ADDED**: 前端聊天界面显示工具调用状态和结果
- **ADDED**: 前端聊天界面重新设计，优化交互体验
- **MODIFIED**: 前端LLM Store支持Agent模式状态管理
- **ADDED**: 工具调用可视化组件（显示工具名称、参数、结果）

## Impact
- **Affected specs**: 
  - `api-server` (聊天API扩展)
  - `ai-framework-web` (前端聊天界面重构)
- **Affected code**: 
  - `api/routes/llm.py` - 聊天路由支持Agent模式
  - `api/models/request.py` - 添加Agent模式参数
  - `api/models/response.py` - 响应包含工具调用信息
  - `Ai_Web/src/views/Chat.vue` - 重新设计聊天页面
  - `Ai_Web/src/stores/llm.ts` - 支持Agent模式状态
  - `Ai_Web/src/components/chat/` - 新增工具调用显示组件
  - `Ai_Web/src/api/llm.ts` - API客户端支持Agent参数
- **Dependencies**: 
  - 依赖现有的Agent引擎和工具系统
  - 依赖互联网访问工具（web_search, fetch_webpage）
