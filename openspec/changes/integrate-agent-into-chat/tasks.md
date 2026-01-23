## 1. 后端API扩展
- [x] 1.1 在 `ChatRequest` 和 `StreamChatRequest` 中添加 `use_agent` 和 `conversation_id` 参数
- [x] 1.2 修改 `/api/v1/llm/chat` 接口，支持Agent模式（当 `use_agent=true` 时调用Agent引擎）
- [x] 1.3 修改 `/api/v1/llm/chat/stream` 接口，支持Agent模式流式输出
- [x] 1.4 在 `ChatResponse` 的 `metadata` 中包含工具调用信息（tool_calls, iterations）
- [x] 1.5 添加Agent模式下的错误处理和降级机制

**角色**：`api-developer`

## 2. 前端API客户端
- [x] 2.1 更新 `ChatRequest` 类型定义，添加 `use_agent` 和 `conversation_id` 字段
- [x] 2.2 更新 `ChatResponse` 类型定义，在 `metadata` 中包含工具调用信息
- [x] 2.3 更新 `llmApi.chat()` 和 `llmApi.streamChat()` 支持Agent参数

**角色**：`ai-framework-frontend-developer`

## 3. 前端状态管理
- [x] 3.1 在 `llm.ts` store 中添加 `useAgent` 状态
- [x] 3.2 在 `llm.ts` store 中添加 `toolCalls` 状态（当前消息的工具调用）
- [x] 3.3 修改 `sendMessage` 和 `streamMessage` 方法，支持Agent模式
- [x] 3.4 添加工具调用信息的解析和存储逻辑

**角色**：`ai-framework-frontend-developer`

## 4. 前端UI重新设计
- [x] 4.1 重新设计 `Chat.vue` 页面布局（更现代的聊天界面）
- [x] 4.2 添加Agent模式开关（Toggle按钮或Switch组件）
- [x] 4.3 优化消息显示区域（支持工具调用状态显示）
- [x] 4.4 创建 `ToolCallCard.vue` 组件（显示工具调用信息）
- [x] 4.5 优化输入区域（添加Agent模式提示）
- [x] 4.6 添加工具调用加载状态（"正在使用工具..."）
- [ ] 4.7 优化移动端响应式布局（可选，基础响应式已实现）

**角色**：`ai-framework-frontend-developer`

## 5. 工具调用可视化
- [x] 5.1 创建 `ToolCallCard.vue` 组件（显示单个工具调用）
- [x] 5.2 显示工具名称、参数、执行状态、结果
- [x] 5.3 支持展开/折叠工具调用详情
- [x] 5.4 为不同工具类型添加图标和颜色标识
- [x] 5.5 优化工具调用结果的展示格式

**角色**：`ai-framework-frontend-developer`

## 6. 测试
- [ ] 6.1 编写后端API单元测试（Agent模式开关测试）
- [ ] 6.2 编写后端API集成测试（Agent工具调用流程）
- [ ] 6.3 编写前端组件单元测试（工具调用显示组件）
- [ ] 6.4 编写E2E测试（完整聊天+工具调用流程）

**角色**：`ai-framework-qa-engineer`

## 7. 文档
- [ ] 7.1 更新API文档（聊天接口的Agent模式说明）
- [ ] 7.2 更新前端设计文档（聊天界面重新设计说明）
- [ ] 7.3 添加使用示例（如何在聊天中使用工具）

**角色**：`ai-framework-documenter`
