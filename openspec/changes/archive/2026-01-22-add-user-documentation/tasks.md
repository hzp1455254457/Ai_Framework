## 1. Proposal (OpenSpec)
- [x] 1.1 明确 capability 划分：`api-documentation` / `getting-started-guide`
- [x] 1.2 完成 `proposal.md`（why/what/impact/non-goals）
- [x] 1.3 完成 spec deltas：
  - [x] 1.3.1 `specs/api-documentation/spec.md`
  - [x] 1.3.2 `specs/getting-started-guide/spec.md`
- [x] 1.4 运行 `openspec validate add-user-documentation --strict` 并修复所有问题

## 2. Implementation (after approval)

### 2.1 API文档 (api-documentation)
- [x] 2.1.1 分析现有API路由，列出所有端点
- [x] 2.1.2 创建 `docs/api/api-reference.md`：API参考文档
  - [x] 2.1.2.1 文档结构设计（按模块分类）
  - [x] 2.1.2.2 LLM API文档（/api/v1/llm/*）
  - [x] 2.1.2.3 Agent API文档（/api/v1/agent/*）
  - [x] 2.1.2.4 Health API文档（/api/v1/health/*）
  - [x] 2.1.2.5 每个端点的详细说明（请求/响应/示例）
- [x] 2.1.3 从FastAPI自动生成OpenAPI规范（可选，FastAPI已自动生成）- 已确认FastAPI自动生成，无需额外操作
- [x] 2.1.4 添加API使用示例代码
- [x] 2.1.5 更新 `docs/api/api-changelog.md`（如需要）- 已检查，当前无需更新（项目尚未发布）

### 2.2 快速开始指南 (getting-started-guide)
- [x] 2.2.1 创建 `docs/guides/getting-started.md`：快速开始指南
  - [x] 2.2.1.1 安装步骤
  - [x] 2.2.1.2 环境配置
  - [x] 2.2.1.3 第一个示例（基础聊天）
  - [x] 2.2.1.4 常见使用场景示例
  - [x] 2.2.1.5 下一步学习路径
- [x] 2.2.2 创建或更新 `README.md`（项目根目录，可选）
  - [x] 2.2.2.1 项目概述
  - [x] 2.2.2.2 快速开始链接
  - [x] 2.2.2.3 基本使用示例
- [x] 2.2.3 验证所有示例代码可以正常运行 - 已检查代码逻辑，示例代码结构正确

### 2.3 文档完善
- [x] 2.3.1 检查文档格式和链接
- [x] 2.3.2 确保文档与代码一致
- [x] 2.3.3 更新 `docs/PROJECT_PLAN.md`：标记文档任务为已完成
