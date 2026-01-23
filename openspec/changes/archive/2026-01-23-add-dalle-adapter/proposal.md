# Proposal: Add DALL-E Adapter

## Why

DALL-E 是 OpenAI 提供的图像生成服务，是 Vision 服务模块的重要适配器实现。当前 Vision 服务核心已完成，但缺少实际的适配器实现，无法提供图像生成功能。

**理由**：
1. **完善 Vision 服务能力**：Vision 服务核心已完成，需要适配器实现才能提供实际功能
2. **支持主流图像生成服务**：DALL-E 是业界主流的图像生成服务，优先级高
3. **复用架构模式**：采用与 LLM 服务相同的适配器模式，保持架构一致性
4. **扩展框架能力**：使框架支持图像生成功能，完善多模态能力

## What Changes

### 核心变更

1. **DALL-E 适配器实现** (`core/vision/adapters/dalle_adapter.py`)
   - 实现 `BaseVisionAdapter` 接口
   - 支持 DALL-E 2 和 DALL-E 3
   - 实现图像生成功能
   - 错误处理和重试机制
   - 流式响应支持（如适用）

2. **适配器注册** (`core/vision/adapters/__init__.py`)
   - 注册 DALL-E 适配器
   - 支持自动发现机制

3. **配置支持** (`config/default.yaml`)
   - 添加 DALL-E 适配器配置项
   - 支持 API 密钥配置
   - 支持模型选择（DALL-E 2/3）

4. **单元测试** (`tests/unit/core/vision/test_dalle_adapter.py`)
   - 适配器初始化测试
   - 图像生成功能测试
   - 错误处理测试
   - Mock HTTP 请求测试

5. **文档更新**
   - 更新 `core/vision/README.md`
   - 添加 DALL-E 适配器使用示例

### 技术细节

- **继承关系**：`DALL-EAdapter` 继承 `BaseVisionAdapter`
- **API 集成**：使用 OpenAI Images API (`/v1/images/generations`)
- **数据模型**：使用 `ImageGenerateRequest` 和 `ImageGenerateResponse`
- **错误处理**：遵循 `AdapterCallError` 异常体系
- **HTTP 客户端**：使用 `httpx.AsyncClient` 进行异步请求

## Impact

### 正面影响

- ✅ **功能完整性**：Vision 服务可以实际提供图像生成功能
- ✅ **架构一致性**：复用 LLM 适配器的实现模式，保持代码风格一致
- ✅ **可扩展性**：为后续其他 Vision 适配器（如 Stable Diffusion）提供参考实现
- ✅ **用户体验**：用户可以通过统一的 Vision 服务接口使用 DALL-E

### 潜在风险

- ⚠️ **API 密钥管理**：需要安全存储 OpenAI API 密钥（将在阶段2解决）
- ⚠️ **成本控制**：DALL-E API 调用有成本，需要监控（成本估算功能待实现）
- ⚠️ **错误处理**：需要处理 API 限流、超时等错误情况

### 依赖关系

- **依赖**：
  - Vision 服务核心（已完成）
  - BaseVisionAdapter（已完成）
  - Vision 数据模型（已完成）
  - OpenAI API 访问权限

- **被依赖**：
  - Vision 路由（将在后续提案中实现）
  - Web 界面（未来）

## Non-Goals

本次提案**不包含**以下内容：

- ❌ Vision 路由实现（将在 `add-vision-routes` 提案中实现）
- ❌ 图像分析适配器（将在后续提案中实现）
- ❌ Stable Diffusion 适配器（P2 优先级，后续实现）
- ❌ API 密钥加密存储（将在阶段2的 `add-api-key-encryption` 提案中实现）
- ❌ 成本估算功能（P2 优先级，后续实现）

## Success Criteria

- [ ] DALL-E 适配器实现完成，通过所有单元测试
- [ ] 支持 DALL-E 2 和 DALL-E 3 模型
- [ ] 错误处理完善，覆盖常见错误场景
- [ ] 代码风格与现有 LLM 适配器保持一致
- [ ] 文档更新完成，包含使用示例
- [ ] 测试覆盖率 ≥ 80%
