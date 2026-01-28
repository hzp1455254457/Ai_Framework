---
alwaysApply: true
---
# 🧠 PromptX 角色与记忆系统

## 📋 文档说明
本文档详细规定了 PromptX 角色系统的定义、激活策略、智能切换规则以及记忆系统的集成规范。

## 1. PromptX 角色系统

### 1.1 角色定义体系

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

### 1.2 角色激活策略（必须严格遵循）

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
| LLM、GPT、Claude、Ollama、适配器 | `llm-service-developer` | 适配器实现、API调用 | 提案/实现 | `mcp_promptx_action(role="llm-service-developer")` |
| 配置、config、缓存、cache、日志 | `infrastructure-developer` | 配置管理、缓存策略 | 提案/实现 | `mcp_promptx_action(role="infrastructure-developer")` |
| API、FastAPI、路由、route、接口 | `api-developer` | API设计、FastAPI技巧 | 提案/实现 | `mcp_promptx_action(role="api-developer")` |
| Agent、工具调用、function calling | `agent-engine-developer` | Agent架构、工具调用 | 提案/实现 | `mcp_promptx_action(role="agent-engine-developer")` |
| 前端、frontend、Web、UI、Vue3 | `ai-framework-frontend-developer` | Vue3开发、组件设计 | 提案/实现 | `mcp_promptx_action(role="ai-framework-frontend-developer")` |
| 测试、test、pytest、覆盖率 | `ai-framework-qa-engineer` | 测试策略、Mock技巧 | 实现 | `mcp_promptx_action(role="ai-framework-qa-engineer")` |
| 文档、documentation、README | `ai-framework-documenter` | 文档规范、示例模式 | 提案/实现 | `mcp_promptx_action(role="ai-framework-documenter")` |
| 架构、architecture、设计、重构 | `ai-framework-architect` | 架构决策、设计模式 | 提案 | `mcp_promptx_action(role="ai-framework-architect")` |
| 工具、tool、插件、plugin | `luban` | 工具开发、插件系统 | 提案/实现 | `mcp_promptx_action(role="luban")` |
| 角色创建、role | `nuwa` | 角色定义、角色配置 | - | `mcp_promptx_action(role="nuwa")` |

**角色激活时机（必须遵守）**：

1. **任务开始时**：必须激活主角色
2. **任务类型变化时**：必须切换到新角色
3. **多角色协作时**：按需切换，但避免频繁切换
4. **任务完成后**：保存各角色经验后再切换

### 1.3 智能角色转换

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

## 2. 记忆系统集成

### 2.1 记忆域定义

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

### 2.2 记忆使用流程（必须严格遵循）

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

### 2.3 记忆保存时机

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

## ⚠️ 常见错误和注意事项

1. **使用自然语言激活角色**：
   - ❌ 错误：`"请以架构师角色处理这个任务"`
   - ✅ 正确：`mcp_promptx_action(role="ai-framework-architect")`

2. **跳过记忆检索直接实现**：
   - ❌ 错误：不检索记忆就直接开始编码
   - ✅ 正确：必须先激活角色 → DMN扫描 → 深入检索 → 再实现

3. **记忆检索只执行一次**：
   - ❌ 错误：执行一次 recall 就停止
   - ✅ 正确：多轮检索，根据返回的网络图继续深入，至少2-3轮

4. **使用错误的记忆检索模式**：
   - ❌ 错误：总是使用 focused 模式，或猜测不存在的关键词
   - ✅ 正确：先 DMN 扫描，从返回的网络图中选择关键词

5. **忘记保存记忆**：
   - ❌ 错误：完成任务后不保存经验
   - ✅ 正确：每个任务完成后都要 remember() 保存关键经验

6. **切换角色后不检索记忆**：
   - ❌ 错误：切换角色后直接开始编码
   - ✅ 正确：切换后必须执行 DMN 扫描和深入检索
