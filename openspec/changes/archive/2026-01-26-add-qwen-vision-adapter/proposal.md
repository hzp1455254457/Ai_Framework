# Change: 实现通义千问Qwen-Vision适配器 - 支持图像理解与分析

## Why

当前Vision服务缺少图像分析功能，无法支持用户对图像的理解、OCR、物体识别等需求。通义千问（Qwen-VL）系列模型提供了强大的视觉理解能力，是中国用户友好且成本较低的选择。

实现Qwen-Vision适配器可以：
- **补充Vision服务缺失的图像分析能力**：支持图像理解、OCR、物体识别
- **提供中国用户友好的选择**：通义千问对中国用户更友好，无需翻墙
- **成本优势**：通义千问视觉模型价格相对较低
- **统一框架**：与现有Qwen LLM适配器保持一致架构

## What Changes

### 核心变更

1. **创建Qwen-Vision适配器**
   - 实现 `QwenVisionAdapter` 类，继承 `BaseVisionAdapter`
   - 支持 `qwen-vl`、`qwen-vl-plus`、`qwen-vl-max` 三个模型
   - 实现 `analyze_image` 方法，支持多种分析类型：
     - `general`: 通用图像理解
     - `ocr`: 光学字符识别
     - `object_detection`: 物体识别
     - `face_detection`: 人脸检测（如果模型支持）

2. **复用现有架构**
   - 复用 `BaseVisionAdapter` 接口
   - 复用 `VisionService` 服务层
   - 复用 `VisionRequest/Response` 数据模型
   - 复用 `api/routes/vision.py` API路由

3. **配置支持**
   - 在 `config/default.yaml` 中添加 `qwen-vision-adapter` 配置
   - 支持模型选择：`model: "qwen-vl-plus"`（默认）
   - 支持API端点自定义

### 架构变更

**当前架构**：
```
VisionService → 无图像分析适配器（仅DALL-E图像生成）
```

**实现后架构**：
```
VisionService
  ├── DALL-E Adapter (图像生成)
  └── Qwen-Vision Adapter (图像分析) ← 新增
```

### 兼容性保证

- **向后兼容**：现有DALL-E适配器继续工作
- **配置兼容**：现有配置继续有效
- **接口兼容**：实现标准 `BaseVisionAdapter` 接口
- **渐进式启用**：通过配置选择是否启用

## Impact

### 受影响的能力规格

- **vision-service**: 需要添加Qwen-Vision适配器支持

### 受影响的代码模块

1. **core/vision/adapters/qwen_vision_adapter.py**: 新增Qwen-Vision适配器（~300行）
2. **core/vision/adapters/__init__.py**: 添加适配器导出
3. **config/default.yaml**: 添加Qwen-Vision配置（~15行）
4. **api/dependencies.py**: 添加适配器注册逻辑（~20行）
5. **tests/unit/core/vision/test_qwen_vision_adapter.py**: 新增单元测试（~150行）

### 新增依赖

- **无新增外部依赖**：复用现有 `httpx`、`pydantic` 等依赖

### 测试影响

- 新增Qwen-Vision适配器单元测试（覆盖率目标80%+）
- 测试场景：
  - 图像理解测试
  - OCR测试
  - 物体识别测试
  - 错误处理测试
  - 配置加载测试

### 文档影响

- 更新 `core/vision/README.md`，添加Qwen-Vision说明
- 更新配置文档，说明Qwen-Vision配置选项

## 风险评估

### 低风险项

1. **API稳定性**：通义千问API相对稳定
   - **缓解**：参考官方文档，使用标准HTTP调用

2. **实现复杂度**：适配器实现相对直接
   - **缓解**：参考现有DALL-E适配器实现模式

### 中风险项

1. **模型兼容性**：不同模型能力可能有差异
   - **缓解**：支持多个模型，用户可根据需求选择
   - 默认使用 `qwen-vl-plus`，能力最均衡

2. **网络依赖**：需要访问通义千问API
   - **缓解**：中国用户访问通义千问相对稳定

## 成功标准

1. ✅ Qwen-Vision适配器功能完整实现
2. ✅ 支持图像理解、OCR、物体识别三种分析类型
3. ✅ 可以通过配置选择不同模型
4. ✅ 现有DALL-E适配器继续正常工作
5. ✅ 代码覆盖率保持在80%以上
6. ✅ 所有测试通过
7. ✅ 文档完整，包含使用说明
