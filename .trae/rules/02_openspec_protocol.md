---
alwaysApply: true
---
# 📜 OpenSpec 协议规范

## 📋 文档说明
本文档详细规定了 OpenSpec 提案的创建、实现和归档流程。所有涉及 OpenSpec 的开发任务必须严格遵循此规范。

## 1. 提案创建流程（必须严格遵循）

**⚠️ 重要：提案阶段只创建文档，不编写代码**

**标准流程（逐步执行）**：

**步骤1：识别任务类型和角色**
```python
# 分析用户请求，提取关键词
keywords = extract_keywords(user_request)
task_type = identify_task_type(keywords)  # 新功能/架构/API/重构

# 根据任务类型匹配角色（参考 03_promptx_system.md）
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

## 2. 提案实现流程（必须严格遵循）

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

## 3. 提案归档流程（必须严格遵循）

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

## 🎯 快速参考

### OpenSpec 命令

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

## ⚠️ 常见错误和注意事项

1. **提案阶段编写代码**：
   - ❌ 错误：在创建 OpenSpec 提案时就编写代码
   - ✅ 正确：提案阶段只创建文档，代码在实现阶段编写

2. **忘记更新项目计划**：
   - ❌ 错误：完成功能后忘记更新 PROJECT_PLAN.md
   - ✅ 正确：这是硬性规则，必须更新（标记为已完成）

3. **任务未完成就更新状态**：
   - ❌ 错误：在 tasks.md 中提前标记任务为完成
   - ✅ 正确：确认任务完全完成（代码+测试+文档）后再更新状态

4. **任务组执行前不切换角色**：
   - ❌ 错误：执行任务组时没有检查角色标注，直接使用当前角色
   - ✅ 正确：每个任务组执行前必须解析并切换角色

5. **tasks.md 中角色标注格式不规范**：
   - ❌ 错误：`角色：api-developer`
   - ✅ 正确：`**角色**：`api-developer``
