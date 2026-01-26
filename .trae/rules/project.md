---
alwaysApply: true
---
# AI框架统一开发规则

## 📋 文档说明

本文档是AI框架项目的**唯一权威规则文件**，整合了所有开发规范、工作流程和最佳实践。

**核心原则**：
1. **OpenSpec 为主流程**：所有功能开发遵循 OpenSpec 三阶段流程（提案→实现→归档）
2. **PromptX 角色驱动**：每个阶段由合适的专业角色处理
3. **记忆驱动决策**：利用 PromptX 记忆系统积累经验，指导架构决策和实现
4. **规范统一**：代码、文档、测试、架构遵循统一规范
5. **文档同步**：代码与文档必须同步更新（硬性规则）

## 🎯 AI 工作流程（必须首先执行）

### 第一步：任务识别和路由

**⚠️ 重要：收到用户请求后，必须首先执行此决策流程**

```
用户请求
  ↓
【步骤1：判断是否需要 OpenSpec 提案】
  ├─ 包含关键词："实现"、"开发"、"添加功能"、"架构"、"设计"、"API"、"重构"
  │  → ✅ 需要 OpenSpec 提案
  │  → 跳转到【1.2 提案创建流程】
  │
  ├─ 包含关键词："修复"、"bug"、"错误"、"格式化"、"lint"、"注释"
  │  → ❌ 无需提案，直接修复
  │  → 跳转到【直接修复流程】（见下方）
  │
  ├─ 包含关键词："提案"、"proposal"、"change"、"spec"
  │  → ✅ 明确需要 OpenSpec 提案
  │  → 跳转到【1.2 提案创建流程】
  │
  └─ 包含关键词："apply"、"实现提案"、"执行提案"
     → ✅ 实现已批准的 OpenSpec 提案
     → 跳转到【1.3 提案实现流程】

【步骤2：识别任务类型和角色】
  根据任务关键词匹配角色（参考下方角色映射表）：
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

---

## 📚 目录导航

### 第一部分：开发工作流（OpenSpec + PromptX 集成）

- [1. OpenSpec 规范开发流程](#1-openspec-规范开发流程)
  - [1.1 任务类型识别](#11-任务类型识别)
  - [1.2 提案创建流程](#12-提案创建流程)
  - [1.3 提案实现流程](#13-提案实现流程)
  - [1.4 提案归档流程](#14-提案归档流程)
- [2. PromptX 角色系统](#2-promptx-角色系统)
  - [2.1 角色定义体系](#21-角色定义体系)
  - [2.2 角色激活策略](#22-角色激活策略)
  - [2.3 智能角色转换](#23-智能角色转换)
- [3. 记忆系统集成](#3-记忆系统集成)
  - [3.1 记忆域定义](#31-记忆域定义)
  - [3.2 记忆使用流程](#32-记忆使用流程)
  - [3.3 记忆保存时机](#33-记忆保存时机)

### 第二部分：代码规范

- [4. 命名规范](#4-命名规范)
- [5. 代码结构规则](#5-代码结构规则)
- [6. 类型注解规则](#6-类型注解规则)
- [7. 异步编程规则](#7-异步编程规则)
- [8. 错误处理规则](#8-错误处理规则)
- [9. 测试规范](#9-测试规范)

### 第三部分：文档规范

- [10. 文档类型定义](#10-文档类型定义)
- [11. 文档同步更新规则](#11-文档同步更新规则)
- [12. 文档一致性规则](#12-文档一致性规则)

### 第四部分：项目规则

- [13. 目录结构规范](#13-目录结构规范)
- [14. 项目计划规则](#14-项目计划规则)
- [15. 架构设计规则](#15-架构设计规则)

---

## 第一部分：开发工作流（OpenSpec + PromptX 集成）

### 1. OpenSpec 规范开发流程

#### 1.1 任务类型识别

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

#### 1.2 提案创建流程（必须严格遵循）

**⚠️ 重要：提案阶段只创建文档，不编写代码**

**标准流程（逐步执行）**：

**步骤1：识别任务类型和角色**
```python
# 分析用户请求，提取关键词
keywords = extract_keywords(user_request)
task_type = identify_task_type(keywords)  # 新功能/架构/API/重构

# 根据任务类型匹配角色（参考下方角色映射表）
primary_role = match_role(task_type)
secondary_roles = identify_secondary_roles(task_type)
```

**步骤2：激活 PromptX 角色（必须执行）**
```python
# 使用 PromptX action 工具激活主角色
mcp_promptx_action(role=primary_role)

# 示例：
# - 架构设计 → action("ai-framework-architect")
# - LLM功能 → action("llm-service-developer")
# - API设计 → action("api-developer")
```

**步骤3：检索 PromptX 记忆（必须执行）**
```python
# 3.1 DMN 全景扫描 - 查看角色的所有记忆域
memory_network = mcp_promptx_recall(
    role=primary_role,
    query=None,  # null 表示 DMN 模式
    mode="balanced"
)

# 3.2 深入检索相关记忆（根据任务关键词）
# 架构相关
architect_memory = mcp_promptx_recall(
    role=primary_role,
    query="架构决策 设计模式",
    mode="focused"
)

# 技术选型相关
tech_memory = mcp_promptx_recall(
    role=primary_role,
    query="技术选型",
    mode="focused"
)

# 继续多轮检索，直到信息充足
# 不要一次就停止，根据返回的网络图继续深入
```

**步骤4：创建 OpenSpec 提案文件**
```python
# 4.1 检查现有提案和规格
# 运行：openspec list
# 运行：openspec list --specs

# 4.2 生成唯一的 change-id（kebab-case, verb-led）
change_id = generate_change_id()  # 例如：add-llm-streaming

# 4.3 创建目录结构
mkdir(f"openspec/changes/{change_id}/")
mkdir(f"openspec/changes/{change_id}/specs/")

# 4.4 创建 proposal.md（引用记忆中的经验）
write_proposal_with_memory(
    path=f"openspec/changes/{change_id}/proposal.md",
    memory_context=memory_network,
    architect_insights=architect_memory,
    tech_insights=tech_memory
)

# 4.5 创建 tasks.md（标注每个任务需要的角色）
# ⚠️ 重要：每个任务组（## 标题）必须标注角色
write_tasks_with_roles(
    path=f"openspec/changes/{change_id}/tasks.md",
    primary_role=primary_role,
    secondary_roles=secondary_roles,
    role_annotation_format="**角色**：`角色ID`"  # 标准格式
)
# 格式要求：
# - 每个任务组（## 标题）后，在任务列表最后添加一行：**角色**：`角色ID`
# - 角色ID必须使用反引号包裹（如：`api-developer`）
# - 如果任务组需要多个角色协作，标注主要角色，并在任务描述中说明

# 4.6 创建 design.md（如果需要，参考 OpenSpec 规则判断）
# 条件：跨模块变更、新依赖、安全/性能复杂性、架构模式变更
if needs_design_doc(task_type):
    write_design_with_memory(
        path=f"openspec/changes/{change_id}/design.md",
        memory_context=architect_memory
    )

# 4.7 创建 spec deltas（每个受影响的 capability 一个文件）
for capability in affected_capabilities:
    write_spec_delta(
        path=f"openspec/changes/{change_id}/specs/{capability}/spec.md",
        operation="ADDED|MODIFIED|REMOVED",
        requirements=extract_requirements(user_request),
        scenarios=extract_scenarios(user_request)
    )
```

**步骤4.5：tasks.md 格式规范（必须严格遵循）**

**⚠️ 关键：每个任务组必须标注角色，格式必须规范**

**标准格式**：
```markdown
## 1. 任务组标题
- [ ] 1.1 任务项1
- [ ] 1.2 任务项2
- [ ] 1.3 任务项3

**角色**：`角色ID`
```

**格式要求**：
1. **任务组标识**：每个 `## 标题` 视为一个任务组
2. **角色标注位置**：在每个任务组的任务列表最后一行，单独一行
3. **角色标注格式**：
   - 标准格式：`**角色**：`角色ID``
   - 角色ID必须使用反引号包裹
   - 角色ID必须与 PromptX 角色ID完全匹配（参考角色映射表）
4. **角色识别规则**：
   - 代码实现任务 → 对应模块开发者（`llm-service-developer`, `api-developer` 等）
   - 测试任务 → `ai-framework-qa-engineer`
   - 文档任务 → `ai-framework-documenter`
   - 前端任务 → `ai-framework-frontend-developer`
   - 架构相关 → `ai-framework-architect`
5. **多角色协作**：如果一个任务组需要多个角色协作，标注主要角色，并在任务描述中说明协作关系

**示例**：
```markdown
## 1. 后端API扩展
- [ ] 1.1 在 `ChatRequest` 中添加 `use_agent` 参数
- [ ] 1.2 修改 `/api/v1/llm/chat` 接口，支持Agent模式
- [ ] 1.3 添加Agent模式下的错误处理

**角色**：`api-developer`

## 2. 前端组件开发
- [ ] 2.1 创建 `ToolCallCard.vue` 组件
- [ ] 2.2 在 `Chat.vue` 中集成工具调用显示
- [ ] 2.3 添加工具调用加载状态

**角色**：`ai-framework-frontend-developer`

## 3. 测试
- [ ] 3.1 编写后端API单元测试
- [ ] 3.2 编写前端组件单元测试
- [ ] 3.3 编写E2E测试

**角色**：`ai-framework-qa-engineer`
```

**步骤5：保存 PromptX 记忆（必须执行）**
```python
# 保存本次提案的关键决策和经验
mcp_promptx_remember(
    role=primary_role,
    engrams=[{
        content: "架构决策：选择X方案，理由：Y，替代方案：Z",
        schema: "架构决策 技术选型 提案",
        strength: 0.9,
        type: "PATTERN"
    }]
)
```

**步骤6：验证提案（必须执行）**
```bash
# 运行 OpenSpec 验证
openspec validate {change_id} --strict

# 修复所有验证错误
# 确保每个 requirement 至少有一个 scenario
# 确保 spec 文件格式正确
```

**角色激活策略**：

| 任务类型 | 主要角色 | 辅助角色 | 记忆域关键词 |
|---------|---------|---------|------------|
| 架构设计/技术选型 | `ai-framework-architect` | - | 架构决策、设计模式、技术选型 |
| 新功能模块开发 | 对应模块开发者 | `ai-framework-architect` | 模块实现、架构决策 |
| API接口设计 | `api-developer` | `ai-framework-architect` | API设计、接口规范 |
| Agent功能开发 | `agent-engine-developer` | `ai-framework-architect` | Agent架构、工具调用 |
| 前端功能开发 | `ai-framework-frontend-developer` | `api-developer` | Vue3、组件设计、状态管理 |
| 基础设施功能 | `infrastructure-developer` | - | 配置管理、缓存策略 |
| 文档编写 | `ai-framework-documenter` | `writer` | 文档规范、文档结构 |

**检查清单（必须逐项完成）**：

- [ ] **步骤1**：识别任务类型和主要角色（参考触发条件识别表）
- [ ] **步骤2**：使用 `mcp_promptx_action()` 激活主角色
- [ ] **步骤3.1**：执行 DMN 全景扫描 `recall(role, null, "balanced")`
- [ ] **步骤3.2**：深入检索相关记忆（至少2-3轮，不要一次就停止）
- [ ] **步骤4.1**：运行 `openspec list` 和 `openspec list --specs` 检查现有工作
- [ ] **步骤4.2**：生成唯一的 change-id（kebab-case, verb-led）
- [ ] **步骤4.3**：创建 `proposal.md`（引用记忆中的经验）
- [ ] **步骤4.4**：创建 `tasks.md`（标注每个任务需要的角色）
- [ ] **步骤4.5**：判断是否需要 `design.md`（跨模块/新依赖/安全性能复杂性）
- [ ] **步骤4.6**：创建 spec deltas（每个 capability 一个文件，包含至少一个 scenario）
- [ ] **步骤5**：使用 `mcp_promptx_remember()` 保存关键决策
- [ ] **步骤6**：运行 `openspec validate {change_id} --strict` 并修复所有问题

#### 1.3 提案实现流程（必须严格遵循）

**⚠️ 重要：实现阶段才开始编写代码，必须等待提案批准**

**标准流程（逐步执行）**：

**步骤1：读取提案文档（必须执行）**
```python
# 1.1 读取提案文档
proposal = read_file(f"openspec/changes/{change_id}/proposal.md")
design = read_file(f"openspec/changes/{change_id}/design.md")  # 如果存在
tasks = read_file(f"openspec/changes/{change_id}/tasks.md")

# 1.2 理解变更范围和验收标准
scope = extract_scope(proposal)
acceptance_criteria = extract_acceptance_criteria(proposal, design)
```

**步骤2：识别主要实现角色（必须执行）**
```python
# 2.1 分析 tasks.md，识别主要任务类型
task_types = analyze_tasks(tasks)

# 2.2 根据任务类型匹配主要角色
primary_role = identify_primary_role(task_types)

# 角色识别规则：
# - 代码实现任务 → 对应模块开发者（llm-service-developer, api-developer 等）
# - 测试任务 → ai-framework-qa-engineer
# - 文档任务 → ai-framework-documenter
# - 架构相关 → ai-framework-architect
```

**步骤3：激活 PromptX 角色并检索记忆（必须执行）**
```python
# 3.1 激活主要角色
mcp_promptx_action(role=primary_role)

# 3.2 DMN 全景扫描
memory_network = mcp_promptx_recall(
    role=primary_role,
    query=None,  # null 表示 DMN 模式
    mode="balanced"
)

# 3.3 深入检索实现相关记忆
impl_memory = mcp_promptx_recall(
    role=primary_role,
    query="实现 最佳实践",
    mode="focused"
)

# 3.4 继续检索任务特定记忆
task_specific_memory = mcp_promptx_recall(
    role=primary_role,
    query=extract_task_keywords(tasks),
    mode="focused"
)
```

**步骤4：按任务顺序实现（逐个完成，必须严格遵循角色切换流程）**

**⚠️ 关键：每个任务组执行前必须精准切换到对应角色**

```python
# 4.1 解析 tasks.md，按任务组（## 标题）组织任务
task_groups = parse_tasks_md(tasks_file)  # 解析为任务组列表
current_role = None  # 当前激活的角色

# 4.2 按任务组顺序处理（每个任务组代表一个角色职责范围）
for task_group in task_groups:
    # 4.2.1 从任务组中提取角色信息（从 "**角色**：`角色ID`" 行解析）
    # 格式：**角色**：`角色ID` 或 **角色**：角色ID
    required_role = extract_role_from_task_group(task_group)
    
    # 4.2.2 如果任务组没有标注角色，根据任务类型自动匹配
    if not required_role:
        task_type = analyze_task_group(task_group)
        required_role = match_role(task_type)  # 参考角色映射表
    
    # 4.2.3 检查当前角色是否匹配（必须检查）
    if current_role != required_role:
        # 4.2.4 必须切换角色（使用 MCP 工具，不要用自然语言）
        mcp_promptx_action(role=required_role)
        current_role = required_role
        
        # 4.2.5 激活新角色后立即执行 DMN 全景扫描（必须执行）
        memory_network = mcp_promptx_recall(
            role=required_role,
            query=None,  # null 表示 DMN 模式，查看所有记忆域
            mode="balanced"
        )
        
        # 4.2.6 深入检索任务相关记忆（从任务组描述中提取关键词）
        task_keywords = extract_keywords(task_group.title, task_group.description)
        task_memory = mcp_promptx_recall(
            role=required_role,
            query=task_keywords,
            mode="focused"
        )
        
        # 4.2.7 继续深入检索（多轮检索，至少2-3轮）
        # 从返回的网络图中选择关键词继续检索
        deep_memory = mcp_promptx_recall(
            role=required_role,
            query=select_keywords_from_network(memory_network),
            mode="balanced"
        )
    else:
        # 4.2.8 如果角色相同，只需检索任务特定记忆
        task_keywords = extract_keywords(task_group.title, task_group.description)
        task_memory = mcp_promptx_recall(
            role=required_role,
            query=task_keywords,
            mode="focused"
        )
    
    # 4.3 执行任务组中的所有任务项
    for task_item in task_group.items:
        # 4.3.1 使用记忆中的经验指导实现
        implement_task(task_item, task_memory)
    
    # 4.4 任务组完成后保存实现经验（必须执行）
    mcp_promptx_remember(
        role=required_role,
        engrams=[{
            content: f"完成任务组：{task_group.title}，关键点：...",
            schema: f"实现 {task_keywords}",
            strength: 0.7,
            type: "LINK"
        }]
    )
    
    # 4.5 更新任务状态（仅在任务组完全完成后）
    # ⚠️ 重要：确认任务组中所有任务项都完成后再更新状态
    if all_tasks_completed(task_group):
        update_task_status(task_group, completed=True)
```

**角色解析函数示例**：
```python
def extract_role_from_task_group(task_group):
    """从任务组中提取角色ID"""
    # 查找 "**角色**：`角色ID`" 或 "**角色**：角色ID" 行
    role_pattern = r'\*\*角色\*\*：`?([a-z-]+)`?'
    match = re.search(role_pattern, task_group.content)
    if match:
        return match.group(1)
    return None
```

**任务组解析规则**：
- tasks.md 中的每个 `## 标题` 视为一个任务组
- 每个任务组必须包含 `**角色**：` 标注（在任务组最后一行）
- 如果任务组没有标注角色，根据任务类型自动匹配（参考角色映射表）

**步骤5：更新项目计划（硬性规则）**
```python
# 5.1 更新 PROJECT_PLAN.md
# 将对应需求标记为已完成 [x]
# 添加完成日期和说明
update_project_plan(change_id, status="completed")
```

**步骤6：保存项目级经验（必须执行）**
```python
# 保存整个功能完成的项目级经验
mcp_promptx_remember(
    role=primary_role,
    engrams=[{
        content: f"完成功能 {change_id}，关键决策：...，经验总结：...",
        schema: "项目经验 功能完成 {change_id}",
        strength: 0.8,
        type: "PATTERN"
    }]
)
```

**角色激活策略**：

| 实现任务 | 主要角色 | 辅助角色 | 记忆域关键词 |
|---------|---------|---------|------------|
| 代码实现 | 对应模块开发者 | - | 实现细节、最佳实践 |
| 前端实现 | `ai-framework-frontend-developer` | `api-developer` | Vue3开发、组件设计、API集成 |
| 测试编写 | `ai-framework-qa-engineer` | 对应模块开发者 | 测试策略、Mock技巧 |
| API实现 | `api-developer` | 对应模块开发者 | API设计、FastAPI技巧 |
| 文档编写 | `ai-framework-documenter` | `writer` | 文档规范、示例模式 |

**检查清单（必须逐项完成）**：

- [ ] **步骤1**：读取 `proposal.md`、`design.md`（如存在）、`tasks.md`
- [ ] **步骤2**：分析 tasks.md，识别主要实现角色
- [ ] **步骤3.1**：使用 `mcp_promptx_action()` 激活主要角色
- [ ] **步骤3.2**：执行 DMN 全景扫描 `recall(role, null, "balanced")`
- [ ] **步骤3.3**：深入检索实现相关记忆（至少2-3轮）
- [ ] **步骤4**：按 tasks.md 顺序实现（逐个任务组完成）
  - [ ] **4.1**：解析 tasks.md，提取任务组和角色信息
  - [ ] **4.2**：对每个任务组执行以下检查：
    - [ ] 从任务组中提取 `**角色**：` 标注
    - [ ] 检查当前角色是否与所需角色匹配
    - [ ] 如果不匹配，使用 `mcp_promptx_action(role=required_role)` 切换
    - [ ] 切换后立即执行 DMN 全景扫描 `recall(role, null, "balanced")`
    - [ ] 深入检索任务相关记忆（至少1-2轮，从任务描述提取关键词）
    - [ ] 使用记忆指导实现任务组中的所有任务项
    - [ ] 任务组完成后保存实现经验 `remember()`
    - [ ] 确认任务组中所有任务项都完成后再更新 tasks.md 状态
- [ ] **步骤5**：更新 `docs/PROJECT_PLAN.md`（硬性规则，标记为已完成）
- [ ] **步骤6**：保存项目级经验 `remember()`

#### 1.4 提案归档流程（必须严格遵循）

**⚠️ 重要：归档时必须同步更新项目计划文档**

**标准流程（逐步执行）**：

**步骤1：验证实现完整性（必须执行）**
```python
# 1.1 检查所有任务是否完成
validate_implementation(change_id)

# 1.2 验证归档前的状态
# 运行：openspec list
# 确认 change 状态为 Complete
```

**步骤2：执行 OpenSpec 归档（必须执行）**
```python
# 2.1 执行归档命令
# 运行：openspec archive {change_id} --yes

# 2.2 验证归档结果
# 检查归档目录：openspec/changes/archive/{date}-{change_id}/
# 检查规格更新：openspec/specs/{capability}/spec.md
```

**步骤3：读取归档内容并更新项目计划（必须执行）**
```python
# 3.1 读取归档的提案文档
proposal = read_file(f"openspec/changes/archive/{date}-{change_id}/proposal.md")
tasks = read_file(f"openspec/changes/archive/{date}-{change_id}/tasks.md")

# 3.2 从 proposal.md 提取功能信息
# - 识别实现的功能模块
# - 识别对应的项目计划条目
# - 提取完成日期和说明

# 3.3 更新 PROJECT_PLAN.md
# 查找对应的需求条目
# 确保标记为已完成 [x]
# 添加完成日期和说明（如果尚未添加）
# 更新完成度统计

# 3.4 验证更新
# 检查项目计划中的条目是否与归档内容一致
```

**步骤4：保存项目级经验（必须执行）**
```python
# 保存归档经验
mcp_promptx_remember(
    role="ai-framework-architect",
    engrams=[{
        content: f"归档 {change_id}，功能：...，经验总结：...",
        schema: "项目经验 功能完成 归档 项目计划同步",
        strength: 0.8,
        type: "PATTERN"
    }]
)
```

**检查清单（必须逐项完成）**：

- [ ] **步骤1**：验证实现完整性，确认所有任务完成
- [ ] **步骤2**：执行 `openspec archive {change_id} --yes`
- [ ] **步骤2.1**：验证归档目录和规格更新
- [ ] **步骤3.1**：读取归档的 proposal.md 和 tasks.md
- [ ] **步骤3.2**：从归档内容提取功能信息
- [ ] **步骤3.3**：更新 `docs/PROJECT_PLAN.md`（硬性规则）
  - [ ] 查找对应的需求条目
  - [ ] 确保标记为已完成 [x]
  - [ ] 添加完成日期和说明（如果尚未添加）
  - [ ] 更新完成度统计
- [ ] **步骤3.4**：验证项目计划更新是否与归档内容一致
- [ ] **步骤4**：保存项目级经验 `remember()`

**项目计划更新规则**：

1. **必须更新**：归档时如果项目计划中对应条目未标记为已完成，必须更新
2. **同步检查**：归档后必须检查项目计划，确保状态同步
3. **完成日期**：使用归档日期作为完成日期
4. **说明内容**：从 proposal.md 的 "What Changes" 部分提取功能说明

---

### 2. PromptX 角色系统

#### 2.1 角色定义体系

**系统角色（PromptX内置）**：
- **luban（鲁班）**：工具开发专家，处理框架工具和插件开发
- **nuwa（女娲）**：角色创建专家，创建新的AI角色
- **writer（写手）**：文档编写专家，处理所有文档相关任务

**项目角色**：

| 角色ID | 角色名称 | 职责范围 | 关键词触发 |
|--------|---------|---------|-----------|
| `ai-framework-architect` | AI框架架构师 | 整体架构设计决策、模块间接口设计、技术选型评估、架构重构和优化 | 架构、architecture、设计、design、重构、refactor、优化、optimize、技术选型 |
| `llm-service-developer` | LLM服务开发工程师 | LLM服务模块开发、适配器实现、上下文管理实现、Token计算和成本估算 | LLM、大语言模型、language model、GPT、Claude、Ollama、适配器、adapter、上下文、context、Token、成本 |
| `infrastructure-developer` | 基础设施开发工程师 | 配置管理模块、缓存管理模块、日志管理模块、存储管理模块 | 配置、config、配置管理、缓存、cache、缓存策略、日志、log、日志系统、存储、storage、数据库、SQLite、Redis、向量数据库 |
| `api-developer` | API开发工程师 | FastAPI应用开发、API路由设计、请求/响应模型定义、API文档维护 | API、接口、endpoint、FastAPI、路由、route、请求、request、响应、response、API文档、swagger、openapi |
| `agent-engine-developer` | Agent引擎开发工程师 | Agent引擎核心实现、工具调用（Function Calling）、工作流编排、记忆管理 | Agent、智能体、引擎、engine、工具调用、function calling、tool、工作流、workflow、编排、记忆、memory、记忆管理 |
| `ai-framework-frontend-developer` | AI框架前端开发工程师 | Vue3应用开发、组件开发、状态管理、路由设计、UI/UX实现、与后端API集成 | 前端、frontend、Web、UI、组件、component、页面、page、Vue、Vue3、TypeScript、Vite、状态管理、state、路由、router、响应式、reactive |
| `ai-framework-qa-engineer` | AI框架测试工程师 | 单元测试编写、集成测试设计、性能测试执行、测试覆盖率维护 | 测试、test、单元测试、unit test、集成测试、integration test、性能测试、performance test、覆盖率、coverage、pytest |
| `ai-framework-documenter` | AI框架文档工程师 | API文档编写、用户手册编写、开发文档维护、示例代码编写 | 文档、documentation、文档编写、README、用户手册、tutorial、示例、example、代码示例、API参考、api reference |

#### 2.2 角色激活策略（必须严格遵循）

**⚠️ 重要：角色激活是 PromptX 集成的核心，必须使用工具调用**

**激活方式（唯一正确方式）**：

```python
# ✅ 正确：使用 PromptX MCP 工具
mcp_promptx_action(role="ai-framework-architect")

# ❌ 错误：不要使用自然语言描述
# "请以架构师角色处理"  ← 这不会激活角色
# "切换到LLM开发者"     ← 这不会激活角色
```

**关键词路由表（自动匹配规则）**：

| 关键词（中文/英文） | 目标角色 | 记忆域关键词 | OpenSpec阶段 | 工具调用示例 |
|-------------------|---------|------------|------------|------------|
| LLM、GPT、Claude、Ollama、适配器、adapter | `llm-service-developer` | 适配器实现、API调用 | 提案/实现 | `mcp_promptx_action(role="llm-service-developer")` |
| 配置、config、缓存、cache、日志、log、存储、storage | `infrastructure-developer` | 配置管理、缓存策略 | 提案/实现 | `mcp_promptx_action(role="infrastructure-developer")` |
| API、FastAPI、路由、route、接口、endpoint | `api-developer` | API设计、FastAPI技巧 | 提案/实现 | `mcp_promptx_action(role="api-developer")` |
| Agent、工具调用、function calling、工作流、workflow | `agent-engine-developer` | Agent架构、工具调用 | 提案/实现 | `mcp_promptx_action(role="agent-engine-developer")` |
| 前端、frontend、Web、UI、组件、component、Vue、Vue3、TypeScript、Vite、页面、page | `ai-framework-frontend-developer` | Vue3开发、组件设计、状态管理、API集成 | 提案/实现 | `mcp_promptx_action(role="ai-framework-frontend-developer")` |
| 测试、test、pytest、覆盖率、coverage | `ai-framework-qa-engineer` | 测试策略、Mock技巧 | 实现 | `mcp_promptx_action(role="ai-framework-qa-engineer")` |
| 文档、documentation、README、示例、example | `ai-framework-documenter` | 文档规范、示例模式 | 提案/实现 | `mcp_promptx_action(role="ai-framework-documenter")` |
| 架构、architecture、设计、design、重构、refactor | `ai-framework-architect` | 架构决策、设计模式 | 提案 | `mcp_promptx_action(role="ai-framework-architect")` |
| 工具、tool、插件、plugin | `luban` | 工具开发、插件系统 | 提案/实现 | `mcp_promptx_action(role="luban")` |
| 角色创建、role | `nuwa` | 角色定义、角色配置 | - | `mcp_promptx_action(role="nuwa")` |
| **OpenSpec提案** | `ai-framework-architect` + 对应模块角色 | 架构决策、模块实现 | **提案** | 先激活架构师，再激活模块角色 |
| **OpenSpec实现** | 根据 tasks.md 识别 | 实现细节、最佳实践 | **实现** | 根据任务类型激活对应角色 |

**角色激活时机（必须遵守）**：

1. **任务开始时**：必须激活主角色
2. **任务类型变化时**：必须切换到新角色
3. **多角色协作时**：按需切换，但避免频繁切换
4. **任务完成后**：保存各角色经验后再切换

**角色激活检查清单**：

- [ ] 识别任务关键词
- [ ] 根据关键词路由表匹配角色
- [ ] 使用 `mcp_promptx_action()` 激活角色（不要用自然语言）
- [ ] 激活后立即执行 DMN 全景扫描
- [ ] 根据任务需求深入检索记忆

#### 2.3 智能角色转换

**角色切换原则**：

1. **任务开始时识别主角色**：明确主要责任
2. **任务组切换时精准切换**：每个任务组（## 标题）执行前必须检查并切换角色
3. **切换后立即检索记忆**：激活新角色后必须执行 DMN 扫描和深入检索
4. **任务完成后保存各角色经验**：积累多角色协作经验

**智能切换规则（OpenSpec 实现阶段）**：

```python
def smart_role_switch_for_openspec(task_group, current_role):
    """OpenSpec 实现阶段的智能角色切换"""
    # 1. 从任务组中提取角色（优先从标注中提取）
    required_role = extract_role_from_task_group(task_group)
    
    # 2. 如果任务组没有标注角色，根据任务类型自动匹配
    if not required_role:
        task_type = analyze_task_group(task_group)
        required_role = match_role(task_type)  # 参考角色映射表
    
    # 3. 如果角色不同，必须切换
    if required_role != current_role:
        # 3.1 使用 MCP 工具切换角色（不要用自然语言）
        mcp_promptx_action(role=required_role)
        
        # 3.2 切换后立即执行 DMN 全景扫描
        memory_network = mcp_promptx_recall(
            role=required_role,
            query=None,  # null 表示 DMN 模式
            mode="balanced"
        )
        
        # 3.3 深入检索任务相关记忆
        task_keywords = extract_keywords(task_group)
        task_memory = mcp_promptx_recall(
            role=required_role,
            query=task_keywords,
            mode="focused"
        )
        
        return required_role, task_memory
    
    # 4. 如果角色相同，只需检索任务特定记忆
    task_keywords = extract_keywords(task_group)
    task_memory = mcp_promptx_recall(
        role=current_role,
        query=task_keywords,
        mode="focused"
    )
    
    return current_role, task_memory
```

**角色切换检查清单（每个任务组执行前）**：

- [ ] **解析任务组**：从 tasks.md 中提取任务组（## 标题）和角色标注
- [ ] **提取角色**：查找 `**角色**：` 行，提取角色ID
- [ ] **检查当前角色**：比较当前激活角色与所需角色
- [ ] **切换角色**：如果不匹配，使用 `mcp_promptx_action(role=required_role)` 切换
- [ ] **DMN 扫描**：切换后立即执行 `recall(role, null, "balanced")`
- [ ] **深入检索**：从任务描述提取关键词，执行 `recall(role, keywords, "focused")`
- [ ] **多轮检索**：根据返回的网络图继续深入检索（至少2-3轮）
- [ ] **执行任务**：使用记忆指导实现任务组中的所有任务项
- [ ] **保存经验**：任务组完成后使用 `remember()` 保存实现经验

**常见错误和解决方案**：

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| 忘记切换角色 | 没有检查任务组的角色标注 | 每个任务组执行前必须检查并切换 |
| 切换后不检索记忆 | 切换角色后直接开始编码 | 切换后必须执行 DMN 扫描和深入检索 |
| 使用自然语言切换 | 用文字描述而非工具调用 | 必须使用 `mcp_promptx_action()` |
| 角色标注格式错误 | tasks.md 中角色标注格式不规范 | 使用标准格式：`**角色**：`角色ID`` |
| 任务组没有标注角色 | 创建提案时忘记标注角色 | 创建 tasks.md 时必须为每个任务组标注角色 |

---

### 3. 记忆系统集成

#### 3.1 记忆域定义

每个角色都应建立以下记忆域：

**架构设计记忆域**（`ai-framework-architect`）：
- `架构决策` - 重要架构决策和理由
- `设计模式` - 使用的设计模式及其应用场景
- `接口规范` - 模块间接口定义
- `技术选型` - 技术选型理由和对比

**LLM服务记忆域**（`llm-service-developer`）：
- `适配器实现` - 各种适配器的实现细节
- `API调用` - API调用的最佳实践和坑点
- `错误处理` - 错误处理和重试策略
- `性能优化` - LLM服务性能优化技巧

**基础设施记忆域**（`infrastructure-developer`）：
- `配置管理` - 配置管理的最佳实践
- `缓存策略` - 缓存策略选择和实现
- `日志规范` - 日志格式和级别规范
- `存储方案` - 存储方案对比和选择

**API开发记忆域**（`api-developer`）：
- `API设计` - API设计规范和最佳实践
- `FastAPI技巧` - FastAPI使用技巧
- `错误处理` - API错误处理模式
- `认证授权` - 认证授权实现方案

**Agent引擎记忆域**（`agent-engine-developer`）：
- `Agent架构` - Agent引擎架构设计
- `工具调用` - 工具调用实现模式
- `工作流编排` - 工作流编排算法
- `记忆管理` - Agent记忆管理策略

**测试记忆域**（`ai-framework-qa-engineer`）：
- `测试策略` - 测试策略选择
- `Mock技巧` - Mock外部依赖的技巧
- `测试数据` - 测试数据管理方法
- `性能指标` - 性能测试指标和基准

**文档记忆域**（`ai-framework-documenter`）：
- `文档规范` - 文档编写规范
- `示例模式` - 示例代码编写模式
- `用户反馈` - 用户常见问题和解决方案
- `文档结构` - 文档结构设计

**前端开发记忆域**（`ai-framework-frontend-developer`）：
- `Vue3开发` - Vue3框架使用技巧和最佳实践
- `组件设计` - 组件设计模式和可复用组件开发
- `状态管理` - Pinia/Vuex状态管理方案
- `路由设计` - Vue Router路由配置和导航守卫
- `API集成` - 与后端API的集成模式和错误处理
- `UI/UX实现` - 用户界面和交互体验实现
- `TypeScript` - TypeScript在前端项目中的使用
- `性能优化` - 前端性能优化技巧和最佳实践

#### 3.2 记忆使用流程（必须严格遵循）

**⚠️ 重要：记忆检索和保存必须使用 PromptX MCP 工具**

**任务开始时的记忆检索（必须执行）**：

```python
# Step 1: DMN全景扫描 - 查看角色的所有记忆域
# ⚠️ 必须使用 null 作为 query 参数
memory_network = mcp_promptx_recall(
    role="llm-service-developer",
    query=None,  # null 表示 DMN 模式，查看所有记忆域
    mode="balanced"
)

# Step 2: 根据任务需求深入检索
# ⚠️ 从返回的网络图中选择关键词，不要猜测
task_memory = mcp_promptx_recall(
    role="llm-service-developer",
    query="OpenAI 适配器",  # 使用网络图中实际存在的词
    mode="focused"
)

# Step 3: 继续深入挖掘相关记忆（多轮检索）
# ⚠️ 不要一次就停止，根据返回的新网络图继续深入
deep_memory = mcp_promptx_recall(
    role="llm-service-developer",
    query="流式响应 错误处理",  # 从上次返回的网络图中选词
    mode="balanced"
)

# Step 4: 继续检索直到信息充足
# 重复步骤3，直到获得足够信息指导实现
```

**任务完成后的记忆保存（必须执行）**：

```python
# 保存本次任务的关键经验
# ⚠️ 必须使用 PromptX MCP 工具
mcp_promptx_remember(
    role="llm-service-developer",
    engrams=[{
        content: "遇到的具体问题或解决方案（完整描述）",
        schema: "关键词1 关键词2 关键词3",  # 从内容中提取关键词，空格分隔
        strength: 0.7,  # 根据重要性调整 0.1-1.0
        type: "ATOMIC"  # ATOMIC | LINK | PATTERN
    }]
)
```

**记忆检索最佳实践**：

1. **总是先 DMN 扫描**：`recall(role, null, "balanced")` 查看所有记忆域
2. **从网络图选词**：使用返回的网络图中实际存在的关键词
3. **多轮深入**：不要一次就停止，至少2-3轮检索
4. **模式选择**：
   - `focused`：精确查找，常用记忆优先
   - `balanced`：平衡精确和联想（默认）
   - `creative`：广泛联想，远距离连接

**记忆类型选择指南**：

- **ATOMIC（原子信息）**：具体事实、名词、实体
  - 示例：`"使用httpx作为异步HTTP客户端"`
  - schema: `"httpx 异步 HTTP客户端"`

- **LINK（关系连接）**：关系、动词、连接
  - 示例：`"OpenAI适配器通过httpx调用API"`
  - schema: `"OpenAI 适配器 httpx API调用"`

- **PATTERN（模式结构）**：流程、方法论、框架
  - 示例：`"错误处理流程：捕获异常 -> 记录日志 -> 重试3次 -> 返回默认值"`
  - schema: `"错误处理 异常 日志 重试 流程"`

#### 3.3 记忆保存时机

**提案阶段保存**：
- ✅ 架构决策和理由
- ✅ 技术选型对比和选择
- ✅ 设计模式应用
- ✅ 接口设计规范

**实现阶段保存**：
- ✅ 实现细节和最佳实践
- ✅ 遇到的坑点和解决方案
- ✅ 测试策略和技巧
- ✅ 性能优化经验

**归档阶段保存**：
- ✅ 项目级经验总结
- ✅ 功能完成的关键决策
- ✅ 后续优化建议

---

## 第二部分：代码规范

### 4. 命名规范

#### 4.1 文件命名

- **Python模块文件**：使用小写字母，单词间用下划线分隔
  - ✅ `llm_service.py`, `config_manager.py`
  - ❌ `LLMService.py`, `config-manager.py`

- **测试文件**：以 `test_` 开头，与源文件对应
  - ✅ `test_llm_service.py`
  - ❌ `testLLMService.py`

- **配置文件**：小写，连字符分隔
  - ✅ `default.yaml`, `dev-config.yaml`

#### 4.2 目录命名

- **规则**：使用小写字母，单词间用下划线分隔，单数形式
- **示例**：
  - ✅ `core/llm/adapters/`
  - ✅ `infrastructure/config/`
  - ❌ `core/LLM/Adapters/`

#### 4.3 类命名

- **规则**：使用驼峰命名法（PascalCase），名词
- **示例**：
  - ✅ `LLMService`, `ConfigManager`, `OpenAIAdapter`
  - ❌ `llm_service`, `Config_Manager`

- **特殊规则**：
  - 基类/抽象类：以 `Base` 或 `Abstract` 结尾
  - 接口类：以 `Interface` 结尾（可选）

#### 4.4 函数和方法命名

- **规则**：使用小写字母和下划线（snake_case），动词开头
- **示例**：
  - ✅ `async def get_config(self) -> dict:`
  - ✅ `async def calculate_tokens(self, text: str) -> int:`
  - ❌ `def GetConfig(self):`
  - ❌ `def config(self):`

- **特殊规则**：
  - 私有方法：以单下划线开头 `_validate_api_key()`
  - 异步方法：必须使用 `async def`

#### 4.5 变量命名

- **规则**：使用小写字母和下划线（snake_case）
- **示例**：
  - ✅ `api_key`, `max_retries`, `timeout_seconds`
  - ❌ `apiKey`, `maxRetries`

- **特殊规则**：
  - 常量：全大写，单词间用下划线分隔 `DEFAULT_TIMEOUT = 30`
  - 私有变量：以单下划线开头 `self._internal_cache`

---

### 5. 代码结构规则

#### 5.1 文件结构

每个Python文件应遵循以下结构：

```python
"""
模块文档字符串（必填）
包含模块说明、主要类/函数、使用示例
"""

# 标准库导入
import asyncio
import json
from typing import List, Dict, Optional

# 第三方库导入
from httpx import AsyncClient
from pydantic import BaseModel

# 本地应用导入
from core.base.service import BaseService
from infrastructure.config.manager import ConfigManager

# 常量定义
DEFAULT_TIMEOUT = 30

# 类型定义
ResponseType = Dict[str, Any]

# 类定义
class MyService(BaseService):
    """类文档字符串"""
    pass

# 函数定义
async def helper_function() -> None:
    """函数文档字符串"""
    pass
```

#### 5.2 导入顺序规则

1. **标准库导入**（按字母顺序）
2. **第三方库导入**（按字母顺序）
3. **本地应用导入**（按目录层级）
4. 每组导入之间空一行

#### 5.3 类结构顺序

```python
class MyClass:
    """类文档字符串"""
    
    # 1. 类常量
    DEFAULT_VALUE = 100
    
    # 2. 类变量
    shared_state = {}
    
    # 3. __init__方法
    def __init__(self):
        pass
    
    # 4. 特殊方法（__str__, __repr__等）
    def __str__(self) -> str:
        pass
    
    # 5. 公共方法（按功能分组）
    async def public_method(self):
        pass
    
    # 6. 私有方法
    def _private_method(self):
        pass
```

#### 5.4 长度限制

- **函数长度**：单个函数不超过50行（不含空行和注释）
- **类长度**：单个类不超过300行
- **模块复杂度**：单个模块不超过500行

---

### 6. 类型注解规则

#### 6.1 基本类型注解

**规则**：所有公共函数必须有完整的类型注解

```python
# ✅ 正确
async def process_data(
    data: Dict[str, Any],
    timeout: int = 30,
) -> Optional[List[str]]:
    pass

# ❌ 错误：缺少类型注解
async def process_data(data, timeout=30):
    pass
```

#### 6.2 常用类型注解模式

```python
from typing import List, Dict, Optional, Union, Any, Callable, Awaitable

# 列表和字典
def process_items(items: List[str]) -> None:
    pass

def create_mapping() -> Dict[str, int]:
    pass

# 可选类型
def find_user(user_id: Optional[int]) -> Optional[User]:
    pass

# 联合类型
def process_value(value: Union[str, int]) -> str:
    pass

# 回调函数
def register_callback(callback: Callable[[str], None]) -> None:
    pass

# 异步回调
def register_async_callback(
    callback: Callable[[str], Awaitable[None]]
) -> None:
    pass
```

---

### 7. 异步编程规则

#### 7.1 异步函数定义

**规则**：所有IO操作必须使用异步函数

```python
# ✅ 正确
async def fetch_data(url: str) -> dict:
    async with AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ❌ 错误：同步IO操作
def fetch_data(url: str) -> dict:
    response = requests.get(url)  # 同步操作，阻塞
    return response.json()
```

#### 7.2 异步上下文管理器

**规则**：使用 `async with` 管理异步资源

```python
# ✅ 正确
async def process_file(filepath: str) -> None:
    async with aiofiles.open(filepath, 'r') as f:
        content = await f.read()

# ❌ 错误：同步文件操作
def process_file(filepath: str) -> None:
    with open(filepath, 'r') as f:
        content = f.read()
```

#### 7.3 并发执行

**规则**：使用 `asyncio.gather` 或 `asyncio.create_task` 并发执行

```python
# ✅ 正确：并发执行多个任务
async def fetch_multiple(urls: List[str]) -> List[dict]:
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
```

---

### 8. 错误处理规则

#### 8.1 异常类型定义

**规则**：定义清晰的异常层次结构

```python
# 基础异常
class AIFrameworkError(Exception):
    """AI框架基础异常"""
    pass

# 模块级异常
class LLMError(AIFrameworkError):
    """LLM服务异常"""
    pass

class ConfigError(AIFrameworkError):
    """配置管理异常"""
    pass
```

#### 8.2 异常处理模式

```python
# ✅ 正确：捕获具体异常
try:
    response = await adapter.call(messages)
except LLMError as e:
    logger.error(f"LLM调用失败: {e}")
    raise
except ValueError as e:
    logger.warning(f"参数错误: {e}")
    raise

# ❌ 错误：捕获所有异常
try:
    response = await adapter.call(messages)
except Exception as e:  # 过于宽泛
    pass
```

---

### 9. 测试规范

#### 9.1 测试文件组织

- **测试文件命名**：`test_模块名.py`
- **测试函数命名**：`test_功能描述()`
- **测试目录结构**：与源代码目录保持一致

#### 9.2 测试编写规则

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_llm_service_chat():
    """测试LLM服务聊天功能"""
    # Arrange: 准备测试数据
    service = LLMService(config)
    messages = [{"role": "user", "content": "Hello"}]
    
    # Act: 执行测试
    response = await service.chat(messages)
    
    # Assert: 验证结果
    assert response.content is not None
    assert response.model == "gpt-3.5-turbo"
```

#### 9.3 测试覆盖率目标

- **目标**：80%以上
- **关键模块**：核心业务逻辑必须达到90%以上

---

## 第三部分：文档规范

### 10. 文档类型定义

#### 10.1 功能技术设计文档

**适用范围**：所有新功能模块、重大功能变更

**文档位置**：`docs/design/功能名称.md`

**必须包含内容**：
1. 功能概述
2. 技术架构
3. 接口设计
4. 实现细节
5. 依赖关系
6. 测试策略
7. 变更历史

**硬性规则**：
- ✅ 新功能开发前必须先创建技术设计文档
- ✅ 功能变更必须更新对应的技术设计文档
- ✅ 代码提交前必须检查文档是否同步更新

#### 10.2 API文档

**适用范围**：所有公共API接口

**文档位置**：
- FastAPI路由：使用OpenAPI自动生成，同时维护 `docs/api/api-reference.md`
- 公共类方法：使用Python docstring

**必须包含内容**：
1. 接口基本信息
2. 请求参数
3. 响应格式
4. 错误处理
5. 使用示例

#### 10.3 模块说明文档

**适用范围**：所有Python模块目录

**文档位置**：模块根目录下的 `README.md`

**必须包含内容**：
1. 模块概述
2. 模块结构
3. 核心API
4. 依赖关系

---

### 11. 文档同步更新规则（硬性规则）

#### 11.1 必须更新文档的情况

1. **新增功能模块**
   - ✅ 必须创建功能技术设计文档
   - ✅ 必须创建模块说明文档
   - ✅ 必须更新架构文档（如涉及架构变更）
   - ✅ 必须更新CHANGELOG.md

2. **功能变更**
   - ✅ 必须更新对应的功能技术设计文档
   - ✅ 必须更新模块说明文档（如涉及API变更）
   - ✅ 必须更新CHANGELOG.md

3. **API变更**
   - ✅ 必须更新接口文档
   - ✅ 必须更新模块说明文档
   - ✅ 必须更新CHANGELOG.md（破坏性变更）

4. **架构变更**
   - ✅ 必须更新架构文档
   - ✅ 必须更新受影响模块的文档
   - ✅ 必须更新CHANGELOG.md

#### 11.2 文档更新检查清单

在提交代码前，必须检查：

- [ ] 是否新增了功能模块？→ 是否创建了功能设计文档？
- [ ] 是否修改了功能逻辑？→ 是否更新了功能设计文档？
- [ ] 是否变更了API接口？→ 是否更新了接口文档？
- [ ] 是否修改了架构？→ 是否更新了架构文档？
- [ ] 是否更新了CHANGELOG.md？

---

### 12. 文档一致性规则

#### 12.1 单一真相源原则

1. **单一真相源（Single Source of Truth）**
   - 每个信息只在权威文档中定义一次
   - 其他文档引用权威文档，而非重复定义

2. **文档同步更新**
   - 代码变更必须同步更新相关文档（硬性规则）
   - 架构变更必须同步更新所有相关文档

3. **引用而非复制**
   - 使用引用链接而非复制内容
   - 避免文档间内容重复导致不一致

#### 12.2 权威文档索引

| 信息类型 | 权威文档 | 快速查找 |
|---------|---------|---------|
| 项目概述 | `AI框架架构方案文档.md` | 项目目标、核心定位 |
| 技术栈版本 | `docs/architecture/tech-stack-versions.md` | Python版本、框架版本 |
| 架构设计 | `AI框架架构方案文档.md` | 整体架构、模块职责 |
| 代码规范 | 本文档（第二部分） | 命名、结构、类型注解 |
| 文档规范 | 本文档（第三部分） | 文档类型、更新规则 |
| 角色系统 | 本文档（第一部分） | 角色定义、激活策略 |
| 项目计划 | `docs/PROJECT_PLAN.md` | 需求清单、完成状态 |

---

## 第四部分：项目规则

### 13. 目录结构规范

#### 13.1 核心代码目录

**`core/` - 核心业务模块**

职责：包含所有核心业务逻辑

结构：
```
core/
├── base/                    # 基础类和接口定义
│   ├── service.py          # 服务基类
│   ├── adapter.py          # 适配器基类
│   └── plugin.py           # 插件基类
├── llm/                     # LLM服务模块
│   ├── service.py          # LLM服务主类
│   ├── context.py          # 对话上下文管理
│   ├── models.py           # LLM相关的数据模型
│   └── adapters/           # LLM适配器实现
├── vision/                  # 视觉服务模块
├── audio/                   # 音频服务模块
└── agent/                   # Agent引擎模块
    ├── engine.py           # Agent引擎主类
    ├── tools.py            # 工具定义和管理
    ├── memory.py           # Agent记忆管理
    ├── planner.py          # 任务规划器
    └── workflow.py         # 工作流编排
```

**开发规则**：
- ✅ 所有核心业务逻辑都在此目录
- ✅ 模块间通过接口交互，避免直接依赖
- ✅ 每个模块都有独立的 `__init__.py` 和 `README.md`

#### 13.2 基础设施目录

**`infrastructure/` - 基础设施模块**

职责：提供通用基础设施能力

结构：
```
infrastructure/
├── config/                  # 配置管理
│   ├── manager.py          # 配置管理器
│   ├── loader.py           # 配置加载器
│   └── validator.py        # 配置验证器
├── cache/                   # 缓存管理
│   ├── manager.py          # 缓存管理器
│   └── backends/           # 缓存后端实现
├── log/                     # 日志管理
│   └── manager.py          # 日志管理器
└── storage/                 # 存储管理
    ├── manager.py          # 存储管理器
    ├── backends/           # 存储后端实现
    └── vector_db.py        # 向量数据库
```

#### 13.3 API接口目录

**`api/` - API接口层**

职责：提供HTTP API接口

结构：
```
api/
├── fastapi_app.py          # FastAPI应用
├── routes/                  # 路由定义
│   ├── llm.py              # LLM路由
│   ├── agent.py            # Agent路由
│   └── health.py           # 健康检查路由
├── models/                  # 请求/响应模型
│   ├── request.py          # 请求模型
│   └── response.py        # 响应模型
├── dependencies.py          # 依赖注入
└── middleware.py           # 中间件
```

#### 13.4 测试目录

**`tests/` - 测试代码**

职责：包含所有测试代码

结构：
```
tests/
├── unit/                    # 单元测试
│   ├── core/               # 核心模块测试
│   ├── infrastructure/     # 基础设施测试
│   └── api/                # API测试
├── integration/             # 集成测试
└── fixtures/                # 测试数据
```

#### 13.5 前端目录（Ai_Web 项目）

**`Ai_Web/` - Web前端项目**

职责：提供Web前端应用界面，与后端API集成

**项目结构**（基于Vue3 + TypeScript + Vite）：
```
Ai_Web/
├── src/                     # 源代码目录
│   ├── api/                 # API客户端
│   │   ├── client.ts       # API客户端封装
│   │   ├── endpoints/      # API端点定义
│   │   └── types/          # API类型定义
│   ├── components/          # Vue组件
│   │   ├── common/         # 通用组件
│   │   ├── layout/         # 布局组件
│   │   └── features/       # 功能组件
│   ├── views/               # 页面视图
│   │   ├── chat/           # 聊天页面
│   │   ├── agent/          # Agent页面
│   │   └── settings/       # 设置页面
│   ├── stores/              # 状态管理（Pinia）
│   │   ├── llm.ts          # LLM状态
│   │   ├── agent.ts        # Agent状态
│   │   └── user.ts         # 用户状态
│   ├── router/              # 路由配置
│   │   └── index.ts        # 路由定义
│   ├── composables/         # 组合式函数
│   ├── utils/               # 工具函数
│   ├── assets/              # 静态资源
│   ├── styles/              # 样式文件
│   ├── App.vue              # 根组件
│   └── main.ts              # 入口文件
├── public/                   # 公共静态资源
├── tests/                    # 测试文件
│   ├── unit/                # 单元测试
│   └── e2e/                 # 端到端测试
├── .env                      # 环境变量
├── .env.development          # 开发环境变量
├── .env.production           # 生产环境变量
├── vite.config.ts            # Vite配置
├── tsconfig.json             # TypeScript配置
├── package.json              # 项目依赖
└── README.md                 # 项目说明
```

**开发规则**：
- ✅ 使用Vue3 Composition API和TypeScript
- ✅ 组件采用单文件组件（SFC）格式
- ✅ 状态管理使用Pinia
- ✅ API调用统一通过API客户端封装
- ✅ 遵循Vue3和TypeScript最佳实践
- ✅ 与后端API完全对接，使用统一的请求/响应模型

**与后端集成**：
- API客户端基于后端FastAPI的OpenAPI规范生成类型定义
- 请求/响应模型与后端保持一致
- 错误处理统一使用后端定义的错误码和消息格式

---

### 14. 项目计划规则

#### 14.1 硬性规则

**规则1：完成功能时必须更新**

- 完成任何功能开发后，必须在项目计划文档中将对应需求标记为已完成
- 更新时间：功能开发完成后立即更新（代码提交前）
- 更新内容：将 `[ ]` 改为 `[x]`，添加完成日期和说明

**规则2：开始新功能时必须更新**

- 开始开发新功能时，必须在项目计划文档中将对应需求标记为进行中

**规则3：修改优先级时必须更新**

- 如果调整了需求的优先级，必须同步更新项目计划文档

**规则4：新增需求时必须更新**

- 如果新增了需求或功能点，必须添加到项目计划文档中

#### 14.2 更新流程

```
1. 开发功能
   ↓
2. 完成功能（代码+测试+文档）
   ↓
3. 更新本文档（标记为已完成）
   ↓
4. 更新CHANGELOG.md
   ↓
5. 提交代码和文档
```

---

### 15. 架构设计规则

#### 15.1 分层架构原则

1. **核心层 `core/`**：LLM服务、Agent引擎等核心能力
2. **基础设施层 `infrastructure/`**：配置、缓存、日志、存储等
3. **接口层 `api/`, `cli/`, `web/`**：向外暴露HTTP、CLI、UI等入口
4. **禁止上层被下层反向依赖**：避免循环依赖

#### 15.2 适配器模式

- `core/llm/adapters/` 中通过 `BaseAdapter` 抽象不同LLM提供商
- 新增模型时只需新增适配器类，而不修改核心服务接口

#### 15.3 配置驱动

- 所有环境差异通过 `config/*.yaml` + `infrastructure/config` 管理
- 禁止在代码中硬编码环境相关常量

#### 15.4 依赖注入

- 服务类通过构造函数注入依赖（适配器、配置管理器、日志等）
- 便于测试和替换实现

---

## 🔗 OpenSpec + PromptX 集成示例

### 示例1：创建新功能提案

**用户请求**："实现 LLM 流式响应功能"

**AI 执行流程**：

```python
# 1. 识别任务类型
# 关键词："实现"、"LLM" → 需要 OpenSpec 提案 + llm-service-developer 角色

# 2. 激活角色
mcp_promptx_action(role="llm-service-developer")

# 3. 检索记忆
memory_network = mcp_promptx_recall(role="llm-service-developer", query=None, mode="balanced")
streaming_memory = mcp_promptx_recall(role="llm-service-developer", query="流式响应 streaming", mode="focused")

# 4. 创建 OpenSpec 提案
change_id = "add-llm-streaming"
create_proposal(change_id, memory_context=streaming_memory)
create_tasks(change_id, role="llm-service-developer")
create_spec_delta(change_id, capability="llm-service", operation="ADDED")

# 5. 保存记忆
mcp_promptx_remember(
    role="llm-service-developer",
    engrams=[{
        content: "提案：LLM流式响应功能，技术方案：...",
        schema: "流式响应 提案 架构决策",
        strength: 0.9,
        type: "PATTERN"
    }]
)

# 6. 验证
run_command("openspec validate add-llm-streaming --strict")
```

### 示例2：实现已批准的提案

**用户请求**："/openspec-apply add-llm-streaming"

**AI 执行流程**：

```python
# 1. 读取提案
proposal = read_file("openspec/changes/add-llm-streaming/proposal.md")
tasks = read_file("openspec/changes/add-llm-streaming/tasks.md")

# 2. 识别主要角色（从 tasks.md 分析）
primary_role = "llm-service-developer"

# 3. 激活角色并检索记忆
mcp_promptx_action(role=primary_role)
memory_network = mcp_promptx_recall(role=primary_role, query=None, mode="balanced")
impl_memory = mcp_promptx_recall(role=primary_role, query="流式响应 实现", mode="focused")

# 4. 按任务顺序实现
for task in tasks:
    # 任务1：实现流式适配器接口
    if task.type == "代码实现":
        # 使用记忆中的经验指导实现
        implement_streaming_adapter(task, impl_memory)
        
        # 保存实现经验
        mcp_promptx_remember(
            role=primary_role,
            engrams=[{
                content: "实现流式适配器，关键点：使用 async generator...",
                schema: "流式响应 适配器 实现",
                strength: 0.8,
                type: "LINK"
            }]
        )
        update_task_status(task, completed=True)
    
    # 任务2：编写测试
    elif task.type == "测试":
        # 切换到测试角色
        mcp_promptx_action(role="ai-framework-qa-engineer")
        test_memory = mcp_promptx_recall(role="ai-framework-qa-engineer", query="流式响应 测试", mode="focused")
        implement_tests(task, test_memory)
        update_task_status(task, completed=True)

# 5. 更新项目计划
update_project_plan("add-llm-streaming", status="completed")

# 6. 保存项目级经验
mcp_promptx_remember(
    role=primary_role,
    engrams=[{
        content: "完成LLM流式响应功能，经验总结：...",
        schema: "项目经验 功能完成 流式响应",
        strength: 0.8,
        type: "PATTERN"
    }]
)
```

### 示例3：直接修复 Bug（无需提案）

**用户请求**："修复 OpenAI 适配器的超时错误"

**AI 执行流程**：

```python
# 1. 识别任务类型
# 关键词："修复"、"错误" → 无需 OpenSpec 提案，直接修复

# 2. 激活角色
mcp_promptx_action(role="llm-service-developer")

# 3. 检索相关记忆
error_memory = mcp_promptx_recall(role="llm-service-developer", query="OpenAI 超时 错误处理", mode="focused")

# 4. 直接修复代码
fix_timeout_error(error_memory)

# 5. 保存修复经验
mcp_promptx_remember(
    role="llm-service-developer",
    engrams=[{
        content: "修复OpenAI适配器超时错误，解决方案：增加重试机制...",
        schema: "OpenAI 超时 错误处理 修复",
        strength: 0.7,
        type: "LINK"
    }]
)
```

## 🎯 快速参考

### OpenSpec 命令（Cursor 命令）

- **提案创建**：`/openspec-proposal` → 激活角色 → recall → 创建提案（标注角色） → remember
- **提案实现**：`/openspec-apply <id>` → 解析 tasks.md → 每个任务组切换角色 → recall → 实现 → remember
- **提案归档**：`/openspec-archive <id>` → 验证 → 归档 → remember

### 角色切换快速参考表

| 场景 | 操作步骤 | 工具调用 |
|------|---------|---------|
| **提案创建阶段** | 识别任务类型 → 激活主角色 → 检索记忆 → 创建 tasks.md（标注角色） | `mcp_promptx_action(role="主角色")` |
| **提案实现阶段 - 开始** | 读取 tasks.md → 识别主要角色 → 激活主角色 → DMN扫描 | `mcp_promptx_action(role="主角色")` → `recall(role, null, "balanced")` |
| **提案实现阶段 - 任务组切换** | 解析任务组 → 提取角色 → 检查当前角色 → 切换角色 → DMN扫描 → 深入检索 | `mcp_promptx_action(role="任务组角色")` → `recall(role, null, "balanced")` → `recall(role, keywords, "focused")` |
| **任务组完成** | 保存实现经验 | `mcp_promptx_remember(role="任务组角色", engrams=[...])` |
| **功能完成** | 保存项目级经验 | `mcp_promptx_remember(role="主角色", engrams=[...])` |

### tasks.md 角色标注格式

```markdown
## 任务组标题
- [ ] 任务1
- [ ] 任务2

**角色**：`角色ID`  ← 必须格式，每个任务组必须有
```

### PromptX 工具调用（必须使用 MCP 工具）

**⚠️ 重要：必须使用 MCP 工具调用，不要使用自然语言描述**

- **激活角色**：
  ```python
  mcp_promptx_action(role="ai-framework-architect")
  ```

- **检索记忆（DMN 模式）**：
  ```python
  mcp_promptx_recall(role="llm-service-developer", query=None, mode="balanced")
  ```

- **检索记忆（关键词模式）**：
  ```python
  mcp_promptx_recall(role="llm-service-developer", query="OpenAI 适配器", mode="focused")
  ```

- **保存记忆**：
  ```python
  mcp_promptx_remember(
      role="llm-service-developer",
      engrams=[{
          content: "具体经验内容",
          schema: "关键词1 关键词2 关键词3",
          strength: 0.7,
          type: "ATOMIC"  # 或 "LINK" 或 "PATTERN"
      }]
  )
  ```

### 角色快速查找

| 任务类型 | 角色ID | 激活指令 |
|---------|--------|---------|
| 架构设计 | `ai-framework-architect` | `action("ai-framework-architect")` |
| LLM开发 | `llm-service-developer` | `action("llm-service-developer")` |
| 基础设施 | `infrastructure-developer` | `action("infrastructure-developer")` |
| API开发 | `api-developer` | `action("api-developer")` |
| Agent开发 | `agent-engine-developer` | `action("agent-engine-developer")` |
| 前端开发 | `ai-framework-frontend-developer` | `action("ai-framework-frontend-developer")` |
| 测试 | `ai-framework-qa-engineer` | `action("ai-framework-qa-engineer")` |
| 文档 | `ai-framework-documenter` | `action("ai-framework-documenter")` |

---

## ⚠️ 常见错误和注意事项

### 错误1：使用自然语言激活角色

**❌ 错误示例**：
```
"请以架构师角色处理这个任务"
"切换到LLM开发者"
```

**✅ 正确方式**：
```python
mcp_promptx_action(role="ai-framework-architect")
mcp_promptx_action(role="llm-service-developer")
```

### 错误2：跳过记忆检索直接实现

**❌ 错误**：不检索记忆就直接开始编码

**✅ 正确**：必须先激活角色 → DMN扫描 → 深入检索 → 再实现

### 错误3：提案阶段编写代码

**❌ 错误**：在创建 OpenSpec 提案时就编写代码

**✅ 正确**：提案阶段只创建文档（proposal.md, tasks.md, design.md, spec deltas），代码在实现阶段编写

### 错误4：记忆检索只执行一次

**❌ 错误**：执行一次 recall 就停止

**✅ 正确**：多轮检索，根据返回的网络图继续深入，至少2-3轮

### 错误5：忘记更新项目计划

**❌ 错误**：完成功能后忘记更新 PROJECT_PLAN.md

**✅ 正确**：这是硬性规则，必须更新（标记为已完成）

### 错误6：任务未完成就更新状态

**❌ 错误**：在 tasks.md 中提前标记任务为完成

**✅ 正确**：确认任务完全完成（代码+测试+文档）后再更新状态

### 错误7：使用错误的记忆检索模式

**❌ 错误**：总是使用 focused 模式，或猜测不存在的关键词

**✅ 正确**：
- 先 DMN 扫描（query=null）查看所有记忆域
- 从返回的网络图中选择实际存在的关键词
- 根据需求选择模式（focused/balanced/creative）

### 错误8：忘记保存记忆

**❌ 错误**：完成任务后不保存经验

**✅ 正确**：每个任务完成后都要 remember() 保存关键经验

### 错误9：任务组执行前不切换角色

**❌ 错误**：执行任务组时没有检查角色标注，直接使用当前角色

**✅ 正确**：
```python
# 每个任务组执行前必须：
# 1. 解析任务组，提取角色标注
required_role = extract_role_from_task_group(task_group)

# 2. 检查并切换角色
if current_role != required_role:
    mcp_promptx_action(role=required_role)
    # 切换后立即检索记忆
    memory_network = mcp_promptx_recall(role=required_role, query=None, mode="balanced")
```

### 错误10：切换角色后不检索记忆

**❌ 错误**：切换角色后直接开始编码，不检索新角色的记忆

**✅ 正确**：
```python
# 切换角色后必须：
# 1. 执行 DMN 全景扫描
memory_network = mcp_promptx_recall(role=required_role, query=None, mode="balanced")

# 2. 深入检索任务相关记忆
task_memory = mcp_promptx_recall(role=required_role, query=task_keywords, mode="focused")

# 3. 多轮检索直到信息充足
```

### 错误11：tasks.md 中角色标注格式不规范

**❌ 错误**：
```markdown
## 1. 后端API扩展
- [ ] 任务1
- [ ] 任务2
角色：api-developer  # 格式不规范
```

**✅ 正确**：
```markdown
## 1. 后端API扩展
- [ ] 任务1
- [ ] 任务2

**角色**：`api-developer`  # 标准格式：**角色**：`角色ID`
```

## 🔄 文档更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-01-22 | v1.0 | 初始版本，整合所有规则到统一文件，集成 OpenSpec 和 PromptX | - |
| 2026-01-22 | v1.1 | 优化 OpenSpec 和 PromptX 集成流程，添加决策树、示例和常见错误说明 | - |
| 2026-01-22 | v1.2 | 新增前端部分：添加ai-framework-frontend-developer角色、前端记忆域、前端目录结构说明 | - |

---

**说明**：本文档是AI框架项目的唯一权威规则文件，所有开发工作都应遵循此规则。
Always respond in 中文.