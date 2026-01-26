# Change: 实现通义万相（TongYi WanXiang）适配器 - 支持国产图像生成

## Why

当前Vision服务仅支持DALL-E（OpenAI）进行图像生成，缺少国产图像生成模型支持。通义万相是阿里云提供的图像生成服务，与通义千问同源，使用相同的DashScope API，对中国用户友好且成本较低。

实现通义万相适配器可以：
- **提供国产图像生成选择**：支持中国用户使用国产模型进行图像生成，无需依赖OpenAI
- **复用现有配置**：与通义千问使用相同的DashScope API和API密钥，配置简单
- **成本优势**：通义万相价格相对较低，适合国内用户
- **统一框架**：与现有Vision适配器保持一致架构，无缝集成

## What Changes

### 核心变更

1. **创建通义万相适配器**
   - 实现 `TongYiWanXiangAdapter` 类，继承 `BaseVisionAdapter`
   - 支持通义万相图像生成API（DashScope API）
   - 实现 `generate_image` 方法，支持文生图功能
   - 支持多种图像尺寸和质量选项

2. **复用现有架构**
   - 复用 `BaseVisionAdapter` 接口
   - 复用 `VisionService` 服务层
   - 复用 `VisionRequest/Response` 数据模型
   - 复用 `api/routes/vision.py` API路由

3. **配置支持**
   - 在 `config/default.yaml` 中添加 `tongyi-wanxiang-adapter` 配置
   - 支持从环境变量或LLM配置中获取API密钥（复用Qwen配置）
   - 支持API端点自定义（默认DashScope API端点）

### 架构变更

**当前架构**：
```
VisionService
  ├── DALL-E Adapter (图像生成 - OpenAI)
  └── Qwen-Vision Adapter (图像分析)
```

**实现后架构**：
```
VisionService
  ├── DALL-E Adapter (图像生成 - OpenAI)
  ├── TongYi-WanXiang Adapter (图像生成 - 国产) ← 新增
  └── Qwen-Vision Adapter (图像分析)
```

### 兼容性保证

- **向后兼容**：现有DALL-E和Qwen-Vision适配器继续工作
- **配置兼容**：现有配置继续有效
- **接口兼容**：实现标准 `BaseVisionAdapter` 接口
- **渐进式启用**：通过配置选择是否启用

## Impact

### 受影响的能力规格

- **vision-service**: 需要添加通义万相适配器支持

### 受影响的代码模块

1. **core/vision/adapters/tongyi_wanxiang_adapter.py**: 新增通义万相适配器（~300行）
2. **core/vision/adapters/__init__.py**: 添加适配器导出
3. **config/default.yaml**: 添加通义万相配置（~10行）
4. **api/dependencies.py**: 添加适配器注册逻辑（~20行）
5. **tests/unit/core/vision/test_tongyi_wanxiang_adapter.py**: 新增单元测试（~150行）

### 新增依赖

- **无新增外部依赖**：复用现有 `httpx`、`pydantic` 等依赖
- **API端点**：使用DashScope API（与通义千问相同）

### 测试影响

- 新增通义万相适配器单元测试（覆盖率目标80%+）
- 测试场景：
  - 图像生成测试
  - 不同尺寸和质量选项测试
  - 错误处理测试
  - 配置加载测试
  - API密钥复用测试

### 文档影响

- 更新 `core/vision/README.md`，添加通义万相说明
- 更新配置文档，说明通义万相配置选项
- 说明API密钥复用机制

## 风险评估

### 低风险项

1. **API稳定性**：DashScope API相对稳定，与通义千问使用相同平台
   - **缓解**：参考现有Qwen适配器实现，使用标准HTTP调用

2. **实现复杂度**：适配器实现相对直接
   - **缓解**：参考现有DALL-E适配器实现模式，复用DashScope API调用经验

3. **配置复用**：可以复用Qwen的API密钥
   - **缓解**：实现自动从Qwen配置中获取API密钥的逻辑

### 中风险项

1. **API文档准确性**：需要确认通义万相API的具体参数格式
   - **缓解**：参考DashScope官方文档，实现时进行充分测试

2. **模型能力差异**：通义万相与DALL-E的能力可能有差异
   - **缓解**：在适配器中明确标注支持的参数和限制

## 成功标准

1. ✅ 通义万相适配器功能完整实现
2. ✅ 支持图像生成功能，支持多种尺寸和质量选项
3. ✅ 可以复用Qwen的API密钥配置
4. ✅ 现有DALL-E和Qwen-Vision适配器继续正常工作
5. ✅ 代码覆盖率保持在80%以上
6. ✅ 所有测试通过
7. ✅ 文档完整，包含使用说明和配置示例
