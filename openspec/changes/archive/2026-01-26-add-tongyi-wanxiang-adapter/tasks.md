# Tasks: 实现通义万相适配器

## 1. 创建通义万相适配器实现
- [x] 1.1 创建 `core/vision/adapters/tongyi_wanxiang_adapter.py` 文件
- [x] 1.2 实现 `TongYiWanXiangAdapter` 类，继承 `BaseVisionAdapter`
- [x] 1.3 实现 `initialize()` 方法，支持DashScope API初始化
- [x] 1.4 实现 `generate_image()` 方法，调用通义万相API
- [x] 1.5 实现 `analyze_image()` 方法（抛出不支持异常）
- [x] 1.6 实现 `edit_image()` 方法（抛出不支持异常）
- [x] 1.7 实现 `health_check()` 方法
- [x] 1.8 实现错误处理和重试机制
- [x] 1.9 添加完整的类型注解和文档字符串

**角色**：`llm-service-developer`

## 2. 配置和注册
- [x] 2.1 在 `config/default.yaml` 中添加 `tongyi-wanxiang-adapter` 配置项
- [x] 2.2 在 `api/dependencies.py` 中添加适配器注册逻辑
- [x] 2.3 实现API密钥自动获取（从Qwen配置或环境变量）
- [x] 2.4 在 `core/vision/adapters/__init__.py` 中添加适配器导出

**角色**：`infrastructure-developer`

## 3. 测试
- [x] 3.1 创建 `tests/unit/core/vision/test_tongyi_wanxiang_adapter.py` 测试文件
- [x] 3.2 编写适配器初始化测试
- [x] 3.3 编写图像生成功能测试
- [x] 3.4 编写不同尺寸和质量选项测试
- [x] 3.5 编写错误处理测试
- [x] 3.6 编写配置加载测试
- [x] 3.7 编写API密钥复用测试
- [x] 3.8 确保测试覆盖率 ≥80%

**角色**：`ai-framework-qa-engineer`

## 4. 文档
- [x] 4.1 更新 `core/vision/README.md`，添加通义万相适配器说明
- [x] 4.2 添加配置示例和使用说明
- [x] 4.3 说明API密钥复用机制
- [x] 4.4 添加API参数说明和限制

**角色**：`ai-framework-documenter`
