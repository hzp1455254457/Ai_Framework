# Tasks: Add DALL-E Adapter

## 任务列表

### 1. 实现 DALL-E 适配器核心类
**角色**：`llm-service-developer`（适配器实现经验可复用）
**文件**：`core/vision/adapters/dalle_adapter.py`
**描述**：
- 创建 `DALLEAdapter` 类，继承 `BaseVisionAdapter`
- 实现 `provider` 属性（返回 "openai"）
- 实现 `name` 属性（返回 "dalle-adapter"）
- 实现 `initialize()` 方法，配置 API 密钥和 HTTP 客户端
- 实现 `generate_image()` 方法，调用 OpenAI Images API
- 实现错误处理和重试机制
- 支持 DALL-E 2 和 DALL-E 3 模型选择

**验收标准**：
- [x] 类定义完整，继承关系正确
- [x] 初始化方法正确配置 API 密钥和 HTTP 客户端
- [x] `generate_image()` 方法正确调用 OpenAI API
- [x] 错误处理覆盖常见场景（API 错误、网络错误、超时等）

### 2. 实现适配器注册
**角色**：`llm-service-developer`
**文件**：`core/vision/adapters/__init__.py`
**描述**：
- 导入 `DALLEAdapter` 类
- 在 `__init__.py` 中导出适配器类
- 确保适配器可以被自动发现机制识别

**验收标准**：
- [x] 适配器类正确导出
- [x] 可以被 Vision 服务自动发现和注册

### 3. 添加配置支持
**角色**：`infrastructure-developer`
**文件**：`config/default.yaml`
**描述**：
- 在 `vision.adapters` 下添加 `dalle-adapter` 配置项
- 配置 API 密钥字段
- 配置默认模型（dall-e-3）
- 配置 base_url（https://api.openai.com/v1）

**验收标准**：
- [x] 配置项格式正确
- [x] 配置项与适配器实现匹配

### 4. 编写单元测试
**角色**：`ai-framework-qa-engineer`
**文件**：`tests/unit/core/vision/test_dalle_adapter.py`
**描述**：
- 测试适配器初始化
- 测试 `generate_image()` 方法（Mock HTTP 请求）
- 测试错误处理（API 错误、网络错误、超时等）
- 测试不同模型选择（DALL-E 2/3）
- 测试不同图像尺寸和参数

**验收标准**：
- [x] 测试覆盖率 ≥ 80%
- [x] 所有测试用例通过（15个测试全部通过）
- [x] Mock 使用正确，不依赖真实 API

### 5. 更新文档
**角色**：`ai-framework-documenter`
**文件**：`core/vision/README.md`
**描述**：
- 添加 DALL-E 适配器说明
- 添加使用示例代码
- 添加配置说明
- 添加常见问题解答

**验收标准**：
- [x] 文档内容完整
- [x] 示例代码可运行
- [x] 配置说明清晰

## 任务依赖关系

```
任务1 (DALL-E适配器核心) 
  ↓
任务2 (适配器注册) 
  ↓
任务3 (配置支持) 
  ↓
任务4 (单元测试) ← 依赖任务1和2
  ↓
任务5 (文档更新) ← 依赖任务1-4
```

## 预计工作量

- **任务1**：4-6 小时（参考 OpenAI LLM 适配器实现）
- **任务2**：0.5 小时
- **任务3**：0.5 小时
- **任务4**：3-4 小时
- **任务5**：1-2 小时

**总计**：约 9-13 小时（1-2 个工作日）
