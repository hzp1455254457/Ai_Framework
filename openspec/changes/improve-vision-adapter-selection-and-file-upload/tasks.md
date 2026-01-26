# Tasks: 改进Vision服务适配器智能选择和前端文件上传功能

## 1. 后端：适配器能力查询机制
- [x] 1.1 在 `BaseVisionAdapter` 基类中添加 `get_supported_operations()` 抽象方法
- [x] 1.2 更新 `VisionService._get_adapter()` 方法，优先根据适配器能力选择适配器
- [ ] 1.3 添加适配器能力查询的单元测试

**角色**：`api-developer`

## 2. 后端：适配器能力实现
- [x] 2.1 在 `DALLEAdapter` 中实现 `get_supported_operations()` 方法，返回 `["generate", "edit"]`
- [x] 2.2 在 `QwenVisionAdapter` 中实现 `get_supported_operations()` 方法，返回 `["analyze"]`
- [x] 2.3 在 `TongYiWanXiangAdapter` 中实现 `get_supported_operations()` 方法，返回 `["generate"]`
- [ ] 2.4 为每个适配器添加能力查询的单元测试

**角色**：`api-developer`

## 3. 前端：图片文件选择工具函数
- [x] 3.1 创建 `Ai_Web/src/utils/image.ts` 文件
- [x] 3.2 实现 `fileToBase64()` 函数，将图片文件转换为Base64字符串
- [x] 3.3 实现 `validateImageFile()` 函数，验证文件大小和格式
- [ ] 3.4 添加文件上传工具函数的单元测试

**角色**：`ai-framework-frontend-developer`

## 4. 前端：ImageAnalyzer组件改进
- [x] 4.1 添加文件选择器（`<input type="file" accept="image/*">`）
- [x] 4.2 移除或隐藏原有的URL/Base64文本输入框
- [x] 4.3 实现文件选择后的预览功能
- [x] 4.4 集成文件转Base64功能，自动转换后调用API
- [x] 4.5 添加文件大小和格式验证提示
- [x] 4.6 更新组件样式，优化用户体验

**角色**：`ai-framework-frontend-developer`

## 5. 前端：ImageEditor组件改进
- [x] 5.1 添加文件选择器（`<input type="file" accept="image/*">`）
- [x] 5.2 移除或隐藏原有的URL/Base64文本输入框
- [x] 5.3 实现文件选择后的预览功能
- [x] 5.4 集成文件转Base64功能，自动转换后调用API
- [x] 5.5 添加文件大小和格式验证提示
- [x] 5.6 更新组件样式，优化用户体验

**角色**：`ai-framework-frontend-developer`

## 6. 测试
- [ ] 6.1 更新VisionService单元测试，测试适配器能力查询逻辑
- [ ] 6.2 更新适配器单元测试，测试 `get_supported_operations()` 方法
- [ ] 6.3 新增前端文件上传和Base64转换的单元测试
- [ ] 6.4 新增前端组件集成测试（文件选择、预览、验证）
- [ ] 6.5 执行端到端测试，验证完整流程

**角色**：`ai-framework-qa-engineer`

## 7. 文档更新
- [ ] 7.1 更新 `core/vision/README.md`，说明适配器能力查询机制
- [ ] 7.2 更新前端开发文档，说明文件上传功能的使用方法
- [ ] 7.3 更新API文档（如有需要）

**角色**：`ai-framework-documenter`
