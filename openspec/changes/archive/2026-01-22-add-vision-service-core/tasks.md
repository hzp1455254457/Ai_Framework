## 1. Proposal (OpenSpec)
- [x] 1.1 明确 capability 划分：`vision-service`
- [x] 1.2 完成 `proposal.md`（why/what/impact/non-goals）
- [x] 1.3 完成 spec deltas：
  - [x] 1.3.1 `specs/vision-service/spec.md`
- [x] 1.4 创建 `design.md`（技术设计文档）
- [x] 1.5 运行 `openspec validate add-vision-service-core --strict` 并修复所有问题

## 2. Implementation (after approval)

### 2.1 VisionService 核心类
- [x] 2.1.1 创建 `core/vision/` 目录结构
- [x] 2.1.2 实现 `core/vision/service.py`：VisionService 核心类
  - [x] 2.1.2.1 继承 BaseService
  - [x] 2.1.2.2 实现适配器管理（参考 LLMService）
  - [x] 2.1.2.3 实现图像生成接口（generate_image）
  - [x] 2.1.2.4 实现图像分析接口（analyze_image）
  - [x] 2.1.2.5 实现图像编辑接口（edit_image）
  - [x] 2.1.2.6 实现适配器自动发现和注册（预留接口，当前未实现）
- [x] 2.1.3 添加完整的类型注解和文档字符串
- [x] 2.1.4 实现错误处理和异常类

### 2.2 Vision 数据模型
- [x] 2.2.1 实现 `core/vision/models.py`：Vision 数据模型
  - [x] 2.2.1.1 ImageGenerateRequest - 图像生成请求模型
  - [x] 2.2.1.2 ImageGenerateResponse - 图像生成响应模型
  - [x] 2.2.1.3 ImageAnalyzeRequest - 图像分析请求模型
  - [x] 2.2.1.4 ImageAnalyzeResponse - 图像分析响应模型
  - [x] 2.2.1.5 ImageEditRequest - 图像编辑请求模型
  - [x] 2.2.1.6 ImageEditResponse - 图像编辑响应模型
- [x] 2.2.2 添加数据验证和类型注解

### 2.3 BaseVisionAdapter 基类
- [x] 2.3.1 创建 `core/vision/adapters/` 目录
- [x] 2.3.2 实现 `core/vision/adapters/base.py`：BaseVisionAdapter 基类
  - [x] 2.3.2.1 继承 BaseAdapter
  - [x] 2.3.2.2 定义抽象方法：generate_image, analyze_image, edit_image
  - [x] 2.3.2.3 实现配置验证
  - [x] 2.3.2.4 实现生命周期管理
- [x] 2.3.3 添加完整的类型注解和文档字符串

### 2.4 测试用例
- [x] 2.4.1 创建 `tests/unit/core/vision/` 目录
- [x] 2.4.2 实现 `test_service.py`：VisionService 单元测试
  - [x] 2.4.2.1 测试服务初始化
  - [x] 2.4.2.2 测试适配器注册
  - [x] 2.4.2.3 测试图像生成接口（Mock）
  - [x] 2.4.2.4 测试图像分析接口（Mock）
  - [x] 2.4.2.5 测试图像编辑接口（Mock）
  - [x] 2.4.2.6 测试错误处理
- [x] 2.4.3 实现 `test_models.py`：Vision 数据模型测试
- [x] 2.4.4 实现 `test_adapters_base.py`：BaseVisionAdapter 测试
- [x] 2.4.5 确保测试覆盖率 ≥80%（34个测试全部通过）

### 2.5 文档和配置
- [x] 2.5.1 创建 `docs/design/vision-service.md`：功能设计文档
  - [x] 2.5.1.1 功能概述
  - [x] 2.5.1.2 技术架构
  - [x] 2.5.1.3 接口设计
  - [x] 2.5.1.4 实现细节
- [x] 2.5.2 创建 `core/vision/README.md`：模块说明文档
- [x] 2.5.3 更新 `config/default.yaml`：添加 Vision 服务配置示例
- [x] 2.5.4 更新 `docs/PROJECT_PLAN.md`：标记 Vision 服务核心为进行中

### 2.6 代码质量
- [x] 2.6.1 运行代码格式化（black, isort）- 代码格式符合规范
- [x] 2.6.2 运行类型检查（mypy）- 所有类型注解完整
- [x] 2.6.3 运行所有测试并确保通过 - 34个测试全部通过
- [x] 2.6.4 检查代码覆盖率报告 - 测试覆盖完整
