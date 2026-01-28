---
alwaysApply: true
---
# 📜 AI Framework 项目规则索引

## 📋 概述
本项目采用模块化的规则管理体系。本文件作为规则索引，所有具体的开发规范、流程和标准请参考下方的分册文档。

## 📚 规则分册索引

### 1. 核心工作流
**📄 [01_core_workflow.md](./01_core_workflow.md)**
- **内容**：任务识别、决策路由、触发条件识别表
- **适用场景**：收到用户请求后的第一步，决定是否需要 OpenSpec 提案或直接修复。

### 2. OpenSpec 协议
**📄 [02_openspec_protocol.md](./02_openspec_protocol.md)**
- **内容**：OpenSpec 提案的创建、实现和归档流程
- **关键点**：提案阶段不写代码、tasks.md 角色标注、项目计划同步规则
- **适用场景**：执行 "新功能"、"架构变更"、"API设计" 等任务时。

### 3. PromptX 系统
**📄 [03_promptx_system.md](./03_promptx_system.md)**
- **内容**：角色定义、激活策略、智能切换、记忆系统集成
- **关键点**：必须使用 MCP 工具激活角色、DMN 全景扫描、多轮记忆检索
- **适用场景**：所有任务执行期间的角色管理和经验保存。

### 4. 代码与工程规范
**📄 [04_coding_standards.md](./04_coding_standards.md)**
- **内容**：代码风格、异步编程、类型注解、错误处理、日志、测试
- **关键点**：IO操作必须异步、全类型注解、禁止裸异常捕获
- **适用场景**：编写和审查代码时。

### 5. 文档规范
**📄 [05_documentation.md](./05_documentation.md)**
- **内容**：文档结构、同步规则、Markdown 格式
- **关键点**：Code <-> Doc 同步、PROJECT_PLAN.md 维护
- **适用场景**：编写文档、更新项目计划时。

### 6. 项目结构规则
**📄 [06_project_rules.md](./06_project_rules.md)**
- **内容**：目录结构、文件放置、模块职责、版本控制
- **关键点**：模块依赖原则、Single Source of Truth
- **适用场景**：创建新文件、规划项目结构时。

## 🚀 快速开始指南

1. **收到任务** → 查看 **[01_core_workflow.md](./01_core_workflow.md)** 决定路径
2. **需要提案** → 遵循 **[02_openspec_protocol.md](./02_openspec_protocol.md)** 流程
   - 激活角色 → 检索记忆 → 创建文档
3. **编写代码** → 遵守 **[04_coding_standards.md](./04_coding_standards.md)**
   - 始终使用 **[03_promptx_system.md](./03_promptx_system.md)** 管理角色和记忆
4. **提交成果** → 更新 **[05_documentation.md](./05_documentation.md)** 和项目计划

## ⚠️ 核心原则摘要

1. **角色驱动**：必须使用 `mcp_promptx_action` 激活角色，禁止自然语言扮演。
2. **记忆优先**：行动前先 `recall`，行动后必 `remember`。
3. **OpenSpec**：提案 → 实现 → 归档，三部曲不可跳过。
4. **文档同步**：代码变动必须同步更新文档和项目计划。
5. **全异步**：IO 操作必须使用 `async/await`，禁止阻塞。
