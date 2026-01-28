---
alwaysApply: true
---
# 🎯 AI 核心工作流程

## 📋 流程说明
收到用户请求后，必须首先执行此决策流程，确定任务类型和处理方式。

## 🚦 决策路由流程

### 第一步：任务识别和路由

**⚠️ 重要：收到用户请求后，必须首先执行此决策流程**

```
用户请求
  ↓
【步骤1：判断是否需要 OpenSpec 提案】
  ├─ 包含关键词："实现"、"开发"、"添加功能"、"架构"、"设计"、"API"、"重构"
  │  → ✅ 需要 OpenSpec 提案
  │  → 跳转到【OpenSpec 提案创建流程】（见 02_openspec_protocol.md）
  │
  ├─ 包含关键词："修复"、"bug"、"错误"、"格式化"、"lint"、"注释"
  │  → ❌ 无需提案，直接修复
  │  → 跳转到【直接修复流程】（见下方）
  │
  ├─ 包含关键词："提案"、"proposal"、"change"、"spec"
  │  → ✅ 明确需要 OpenSpec 提案
  │  → 跳转到【OpenSpec 提案创建流程】（见 02_openspec_protocol.md）
  │
  └─ 包含关键词："apply"、"实现提案"、"执行提案"
     → ✅ 实现已批准的 OpenSpec 提案
     → 跳转到【OpenSpec 提案实现流程】（见 02_openspec_protocol.md）

【步骤2：识别任务类型和角色】
  根据任务关键词匹配角色（参考 03_promptx_system.md）：
  ├─ LLM/适配器相关 → 角色：llm-service-developer
  ├─ 配置/缓存/日志/存储 → 角色：infrastructure-developer
  ├─ API/接口/路由 → 角色：api-developer
  ├─ Agent/工具调用/工作流 → 角色：agent-engine-developer
  ├─ 前端/Web/UI/组件 → 角色：ai-framework-frontend-developer
  ├─ 测试相关 → 角色：ai-framework-qa-engineer
  ├─ 文档相关 → 角色：ai-framework-documenter
  └─ 架构/设计/重构 → 角色：ai-framework-architect

【步骤3：激活 PromptX 角色】
  → 使用 mcp_promptx_action(role="角色ID") 激活角色
  → 不要使用自然语言描述

【步骤4：检索 PromptX 记忆】
  → 先执行 DMN 全景扫描：mcp_promptx_recall(role, null, "balanced")
  → 根据返回的网络图深入检索：mcp_promptx_recall(role, "关键词", "focused")
  → 多轮检索直到信息充足

【步骤5：执行任务】
  → 根据任务类型执行相应流程
```

### 直接修复流程（无需 OpenSpec 提案）

**适用场景**：Bug 修复、代码格式、注释更新、非破坏性依赖更新

```python
# 1. 识别任务类型和角色
task_type = "bug修复"
role = match_role(task_type)

# 2. 激活角色
mcp_promptx_action(role=role)

# 3. 检索相关记忆
memory = mcp_promptx_recall(role=role, query="错误处理 bug修复", mode="focused")

# 4. 直接修复代码
fix_code(memory)

# 5. 保存修复经验
mcp_promptx_remember(role=role, engrams=[...])
```

### 触发条件识别表

| 用户请求特征 | 需要 OpenSpec？ | 主要角色 | 下一步动作 |
|------------|---------------|---------|----------|
| "实现X功能"、"开发X"、"添加X" | ✅ 是 | 对应模块开发者 | 创建 OpenSpec 提案 |
| "架构设计"、"技术选型"、"重构" | ✅ 是 | `ai-framework-architect` | 创建 OpenSpec 提案 |
| "API设计"、"接口"、"路由" | ✅ 是 | `api-developer` | 创建 OpenSpec 提案 |
| "前端"、"Web"、"UI"、"组件"、"页面" | ✅ 是 | `ai-framework-frontend-developer` | 创建 OpenSpec 提案 |
| "修复bug"、"错误"、"问题" | ❌ 否 | 对应模块开发者 | 直接修复 |
| "格式化"、"lint"、"注释" | ❌ 否 | - | 直接处理 |
| "创建提案"、"proposal" | ✅ 是 | `ai-framework-architect` | 创建 OpenSpec 提案 |
| "实现提案"、"apply" | ✅ 是 | 根据 tasks.md | 实现 OpenSpec 提案 |

## 🔍 任务类型详细识别

**需要 OpenSpec 提案的任务**：

| 任务类型 | 触发关键词 | 主要角色 | 流程 |
|---------|-----------|---------|------|
| 新功能开发 | "实现", "开发", "添加功能" | 对应模块开发者 | 提案 → 实现 → 归档 |
| 架构设计 | "架构", "设计", "技术选型" | `ai-framework-architect` | 提案 → 实现 → 归档 |
| API设计 | "API", "接口", "路由" | `api-developer` | 提案 → 实现 → 归档 |
| 前端开发 | "前端", "Web", "UI", "组件", "页面" | `ai-framework-frontend-developer` | 提案 → 实现 → 归档 |
| 重大重构 | "重构", "优化架构" | `ai-framework-architect` | 提案 → 实现 → 归档 |

**无需 OpenSpec 的任务**：

| 任务类型 | 触发关键词 | 处理方式 |
|---------|-----------|---------|
| Bug修复 | "修复", "bug", "错误" | 直接修复，无需提案 |
| 代码格式 | "格式化", "lint" | 直接处理 |
| 注释更新 | "注释", "文档注释" | 直接更新 |
| 依赖更新 | "更新依赖"（非破坏性） | 直接更新 |
