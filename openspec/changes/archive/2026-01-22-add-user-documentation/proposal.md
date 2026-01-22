# Change: Add User Documentation (API文档 + 快速开始指南)

## Why
当前框架已实现完整的API接口（LLM、Agent、健康检查等），但缺少：
1. **API文档**：用户无法快速了解所有可用的API接口、参数、响应格式和使用示例
2. **快速开始指南**：新用户无法快速上手，需要花费大量时间阅读代码和架构文档

这些文档是提升框架可用性和用户体验的关键，能够显著降低使用门槛，加速用户上手。

## What Changes
- 新增 `api-documentation` capability：提供完整的API参考文档
- 新增 `getting-started-guide` capability：提供快速开始指南

## Impact
- **Affected specs**: `api-documentation`, `getting-started-guide`（本次新增）
- **Affected code (planned)**:
  - `docs/api/api-reference.md`：API参考文档
  - `docs/guides/getting-started.md`：快速开始指南
  - `docs/api/openapi.yaml`：OpenAPI规范文件（可选，从FastAPI自动生成）
  - `README.md`：项目根目录README（可选更新）

## Non-Goals
- 不在本次 change 中实现自动生成API文档的工具（FastAPI已有自动生成）
- 不在本次 change 中实现交互式API文档（FastAPI Swagger UI已提供）
- 不在本次 change 中实现多语言文档（仅中文）
