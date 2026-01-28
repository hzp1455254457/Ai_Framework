---
alwaysApply: true
---
# 📚 文档规范

## 📋 文档说明
本文档详细规定了文档结构、更新规则、Markdown 格式以及文档维护规范。

## 1. 文档体系结构

项目文档分为以下几类：

### 1.1 核心规则文档（.trae/rules/）
- **01_core_workflow.md**：核心决策和工作流程
- **02_openspec_protocol.md**：OpenSpec 提案协议规范
- **03_promptx_system.md**：PromptX 角色与记忆系统
- **04_coding_standards.md**：代码与工程规范
- **05_documentation.md**：文档规范（本文档）
- **06_project_rules.md**：项目结构与规划规则
- **project.md**：规则索引入口（Meta-Rule）

### 1.2 项目文档（docs/）
- **PROJECT_PLAN.md**：项目整体计划和进度（Single Source of Truth）
- **API/**：API 接口文档
- **architecture/**：架构设计文档
- **guides/**：开发指南和用户手册

### 1.3 OpenSpec 文档（openspec/）
- **changes/**：变更提案（proposal.md, tasks.md, design.md）
- **specs/**：功能规格说明（spec.md）

## 2. 文档同步规则（硬性规则）

**⚠️ 核心原则：代码与文档必须保持同步**

### 2.1 同步更新要求
- **代码变更**：如果修改了功能逻辑，必须同步更新对应的 `spec.md`
- **任务完成**：如果完成了 tasks.md 中的任务，必须同步更新 `PROJECT_PLAN.md`
- **架构调整**：如果调整了架构，必须同步更新 `docs/architecture/` 下的文档

### 2.2 项目计划更新（PROJECT_PLAN.md）
- **新增需求**：OpenSpec 提案批准后，必须添加到 PROJECT_PLAN.md
- **任务完成**：实现完成后，必须将对应条目标记为 `[x]` 并添加完成日期
- **进度追踪**：定期更新总体进度百分比

### 2.3 规格文档更新（openspec/specs/）
- **变更源**：以 `spec.md` 为功能的唯一事实来源
- **版本控制**：重大变更应记录在 `openspec/changes/` 中

## 3. Markdown 格式规范

### 3.1 标题层级
- **H1 (#)**：文档标题（每个文件仅一个）
- **H2 (##)**：主要章节
- **H3 (###)**：子章节
- **H4 (####)**：细分内容（避免使用 H5/H6）

### 3.2 代码块
- 必须指定语言标记（如 ```python, ```bash）
- 代码块前后必须有空行
- 示例代码应包含必要的导入和上下文

### 3.3 列表
- 使用 `-` 作为无序列表符号
- 使用 `1.` 作为有序列表符号
- 列表项之间不要空行（除非项内容很长）

### 3.4 强调
- **加粗**：用于关键概念、警告、注意点
- *斜体*：用于文件名、术语引用
- `代码`：用于行内代码、变量名、路径

### 3.5 链接
- 使用相对路径引用项目内文件
- 格式：`[显示文本](./path/to/file.md)`

## 4. PromptX 文档集成

### 4.1 角色归属
文档应明确维护责任人（PromptX 角色）。

**示例**：
```markdown
---
maintainer: ai-framework-documenter
---
```

### 4.2 记忆标记
在文档中引用 PromptX 记忆概念时，使用标准术语：
- **记忆域**（Memory Domain）
- **Engram**（记忆痕迹）
- **Schema**（记忆模式）

## 5. 自动维护规则

### 5.1 project.md 维护
- `project.md` 是规则的索引文件
- 当添加新规则文件时，必须更新 `project.md` 的索引
- 禁止将具体规则直接写入 `project.md`（除索引外）

### 5.2 目录结构文档
- 如果添加了新目录或重构了目录结构，必须更新 `06_project_rules.md` 中的目录树

## ⚠️ 常见文档错误

1. **文档过时**：
   - ❌ 代码改了，文档没改
   - ✅ 提交代码前检查相关文档是否更新

2. **格式混乱**：
   - ❌ 标题层级跳跃（H2 下直接 H4）
   - ✅ 保持层级清晰（H1 -> H2 -> H3）

3. **代码块无语言标记**：
   - ❌ ``` code ```
   - ✅ ```python code ```

4. **项目计划未更新**：
   - ❌ 功能做完了，PROJECT_PLAN.md 还是 [ ]
   - ✅ 每次完成功能必须更新项目计划

5. **重复文档**：
   - ❌ 在多个地方维护同一份信息
   - ✅ 遵循 Single Source of Truth 原则，使用引用
