# Change: 改进Vision服务适配器智能选择和前端文件上传功能

## Why

当前Vision服务存在以下问题：

1. **适配器选择机制不完善**：当前VisionService的适配器选择逻辑基于简单的名称推断（如"dalle"、"qwen"等），无法准确识别适配器的实际能力。这导致用户在使用图像分析功能时，系统可能错误地选择了不支持该功能的适配器（如Qwen-Vision适配器不支持图像生成，但可能被错误选择）。

2. **前端输入方式不友好**：当前前端Vision页面要求用户手动输入图像URL或Base64字符串，这种方式对用户不友好，增加了使用门槛。用户更期望能够直接选择本地图片文件，系统自动转换为Base64字符串。

3. **用户体验问题**：从错误提示可以看出，系统无法正确识别适配器能力，导致用户看到"通义千问Vision适配器不支持图像生成功能"的错误，影响用户体验。

改进这些功能可以：
- **提升适配器选择准确性**：通过适配器能力查询机制，确保每个图像处理功能（生成/分析/编辑）都能选择到支持该功能的大模型适配器
- **改善用户体验**：前端支持文件选择，自动转换为Base64，无需手动输入URL或字符串
- **增强系统健壮性**：避免因适配器选择错误导致的用户操作失败

## What Changes

### 核心变更

1. **后端：适配器能力查询机制**
   - 在 `BaseVisionAdapter` 基类中添加 `get_supported_operations()` 方法，返回适配器支持的操作列表（如 `["generate", "analyze", "edit"]`）
   - 更新 `VisionService._get_adapter()` 方法，优先根据适配器能力选择适配器，而不是基于名称推断
   - 确保每个图像处理功能都能选择到支持该功能的大模型适配器

2. **后端：适配器能力注册**
   - 更新所有Vision适配器（DALLEAdapter、QwenVisionAdapter、TongYiWanXiangAdapter），实现 `get_supported_operations()` 方法
   - DALLEAdapter：支持 `["generate", "edit"]`
   - QwenVisionAdapter：支持 `["analyze"]`
   - TongYiWanXiangAdapter：支持 `["generate"]`（如果支持）

3. **前端：图片文件选择功能**
   - 在 `ImageAnalyzer.vue` 组件中添加文件选择器（`<input type="file">`），支持图片文件选择
   - 在 `ImageEditor.vue` 组件中添加文件选择器，支持图片文件选择
   - 创建工具函数 `utils/image.ts`，实现图片文件转Base64字符串的功能
   - 移除或隐藏原有的URL/Base64文本输入框，改为文件选择方式

4. **前端：用户体验优化**
   - 添加文件预览功能，用户选择文件后可以预览图片
   - 添加文件大小和格式验证（支持常见图片格式：jpg、png、gif、webp等）
   - 优化错误提示，当适配器选择失败时提供更友好的错误信息

### 架构变更

**当前架构**：
```
VisionService._get_adapter()
  ├─ 基于适配器名称推断（"dalle" → generate/edit）
  └─ 基于适配器名称推断（"qwen" → analyze）
```

**实现后架构**：
```
VisionService._get_adapter()
  ├─ 查询适配器能力（adapter.get_supported_operations()）
  ├─ 根据操作类型匹配适配器能力
  └─ 优先选择支持该操作的适配器
```

**前端变更**：
```
ImageAnalyzer/ImageEditor
  ├─ 移除：URL/Base64文本输入框
  ├─ 新增：文件选择器（<input type="file">）
  ├─ 新增：文件转Base64工具函数
  └─ 新增：文件预览和验证
```

### 兼容性保证

- **向后兼容**：现有API接口保持不变，只是内部适配器选择逻辑优化
- **配置兼容**：现有配置继续有效
- **接口兼容**：API请求/响应格式不变
- **渐进式改进**：如果适配器未实现 `get_supported_operations()`，回退到原有名称推断逻辑

## Impact

### 受影响的能力规格

- **vision-service**: 需要添加适配器能力查询机制
- **api-server**: 无需变更（API接口保持不变）

### 受影响的代码模块

1. **core/vision/adapters/base.py**: 添加 `get_supported_operations()` 抽象方法（~10行）
2. **core/vision/service.py**: 更新 `_get_adapter()` 方法，使用能力查询（~30行）
3. **core/vision/adapters/dalle_adapter.py**: 实现 `get_supported_operations()` 方法（~5行）
4. **core/vision/adapters/qwen_vision_adapter.py**: 实现 `get_supported_operations()` 方法（~5行）
5. **core/vision/adapters/tongyi_wanxiang_adapter.py**: 实现 `get_supported_operations()` 方法（~5行）
6. **Ai_Web/src/components/vision/ImageAnalyzer.vue**: 添加文件选择功能（~80行）
7. **Ai_Web/src/components/vision/ImageEditor.vue**: 添加文件选择功能（~80行）
8. **Ai_Web/src/utils/image.ts**: 新增图片文件转Base64工具函数（~50行）

### 新增依赖

- **无新增外部依赖**：前端使用浏览器原生File API，后端无需新增依赖

### 测试影响

- 更新VisionService单元测试，测试适配器能力查询逻辑
- 更新适配器单元测试，测试 `get_supported_operations()` 方法
- 新增前端文件上传和Base64转换的单元测试
- 新增前端组件集成测试

### 文档影响

- 更新 `core/vision/README.md`，说明适配器能力查询机制
- 更新前端开发文档，说明文件上传功能的使用方法

## 风险评估

### 低风险项

1. **适配器能力查询机制**：实现简单，风险低
   - **缓解**：如果适配器未实现该方法，回退到原有逻辑

2. **前端文件上传**：使用浏览器原生API，成熟稳定
   - **缓解**：添加文件大小和格式验证，避免上传过大或格式不支持的文件

### 中风险项

1. **适配器选择逻辑变更**：可能影响现有功能
   - **缓解**：保持向后兼容，如果适配器未实现能力查询，使用原有逻辑
   - **测试**：编写完整的单元测试和集成测试

2. **前端用户体验变更**：移除URL输入可能影响部分用户
   - **缓解**：可以考虑保留URL输入作为备选方案，或提供"从URL加载"的选项

## 成功标准

1. ✅ 适配器能力查询机制完整实现
2. ✅ VisionService能够根据操作类型准确选择适配器
3. ✅ 所有Vision适配器实现 `get_supported_operations()` 方法
4. ✅ 前端支持图片文件选择，自动转换为Base64
5. ✅ 前端移除或隐藏URL/Base64文本输入框
6. ✅ 文件上传功能包含预览和验证
7. ✅ 所有测试通过
8. ✅ 文档完整更新
