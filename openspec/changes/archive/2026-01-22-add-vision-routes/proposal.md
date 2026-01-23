# Proposal: Add Vision Routes

## Why

Vision 服务核心和适配器已实现，但缺少 API 路由，无法通过 HTTP 接口访问 Vision 功能。需要添加 Vision 路由以支持 Web 应用和 API 调用。

**理由**：
1. **完善 API 接口层**：Vision 服务需要通过 API 路由暴露给外部调用
2. **支持前端开发**：Web 界面需要 Vision API 接口才能使用图像生成等功能
3. **保持架构一致性**：参考 LLM 路由的实现模式，保持代码风格一致
4. **提升用户体验**：用户可以通过 RESTful API 使用 Vision 功能

## What Changes

### 核心变更

1. **Vision 路由实现** (`api/routes/vision.py`)
   - 图像生成接口 (`POST /api/vision/generate`)
   - 图像分析接口 (`POST /api/vision/analyze`)
   - 图像编辑接口 (`POST /api/vision/edit`)
   - 错误处理和响应格式化

2. **请求/响应模型** (`api/models/request.py`, `api/models/response.py`)
   - 添加 Vision 相关的请求模型
   - 添加 Vision 相关的响应模型
   - 数据验证和类型转换

3. **依赖注入** (`api/dependencies.py`)
   - 添加 `get_vision_service()` 依赖函数
   - 支持 Vision 服务实例注入

4. **路由注册** (`api/fastapi_app.py`)
   - 注册 Vision 路由到 FastAPI 应用
   - 配置路由前缀和标签

5. **单元测试** (`tests/unit/api/routes/test_vision.py`)
   - 路由接口测试
   - 请求/响应模型测试
   - 错误处理测试
   - Mock Vision 服务测试

6. **API 文档更新**
   - 更新 `docs/api/api-reference.md`
   - 添加 Vision API 接口文档

### 技术细节

- **路由设计**：参考 `api/routes/llm.py` 的实现模式
- **请求模型**：使用 Pydantic 进行数据验证
- **响应格式**：统一的响应格式，包含错误信息
- **依赖注入**：使用 FastAPI 的 `Depends` 机制
- **错误处理**：统一的异常处理和 HTTP 状态码

## Impact

### 正面影响

- ✅ **功能完整性**：Vision 服务可以通过 API 访问
- ✅ **架构一致性**：复用 LLM 路由的实现模式，保持代码风格一致
- ✅ **前端支持**：为 Web 界面开发提供 API 接口
- ✅ **用户体验**：用户可以通过 RESTful API 使用 Vision 功能

### 潜在风险

- ⚠️ **文件上传处理**：图像分析/编辑需要处理文件上传，需要验证文件大小和格式
- ⚠️ **响应时间**：图像生成可能需要较长时间，需要考虑超时和异步处理
- ⚠️ **错误处理**：需要处理 Vision 服务的各种错误情况

### 依赖关系

- **依赖**：
  - Vision 服务核心（已完成）
  - Vision 适配器（DALL-E 适配器将在 `add-dalle-adapter` 中实现）
  - FastAPI 应用（已完成）
  - API 依赖注入系统（已完成）

- **被依赖**：
  - Web 界面（未来）
  - 第三方集成（未来）

## Non-Goals

本次提案**不包含**以下内容：

- ❌ Vision 适配器实现（在 `add-dalle-adapter` 提案中实现）
- ❌ 流式响应支持（图像生成通常不需要流式响应）
- ❌ 文件存储管理（图像文件存储将在后续提案中实现）
- ❌ 图像缓存（将在性能优化阶段实现）

## Success Criteria

- [ ] Vision 路由实现完成，通过所有单元测试
- [ ] 支持图像生成、分析、编辑三种接口
- [ ] 错误处理完善，覆盖常见错误场景
- [ ] 代码风格与现有 LLM 路由保持一致
- [ ] API 文档更新完成
- [ ] 测试覆盖率 ≥ 80%
