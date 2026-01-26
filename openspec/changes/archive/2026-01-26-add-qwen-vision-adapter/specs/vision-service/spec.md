## ADDED Requirements

### Requirement: Qwen-Vision Image Analysis Adapter
系统 SHALL 实现Qwen-Vision适配器，支持通义千问视觉模型进行图像分析。

**Rationale**: 提供图像分析能力，支持图像理解、OCR和物体识别，与现有DALL-E图像生成功能互补。

#### Scenario: User performs image understanding analysis
- **WHEN** 用户上传图片，请求进行图像理解分析
- **THEN** 系统应调用Qwen-Vision适配器，返回图像的详细描述和分析结果

#### Scenario: User performs OCR text recognition
- **WHEN** 用户上传文档图片，请求进行OCR文字识别
- **THEN** 系统应调用Qwen-Vision适配器，返回识别出的文本内容

#### Scenario: User performs object detection
- **WHEN** 用户上传场景图片，请求识别其中的物体
- **THEN** 系统应调用Qwen-Vision适配器，返回识别的物体列表

#### Scenario: Qwen-Vision adapter health check
- **WHEN** 系统执行定期健康检查或用户请求检查适配器状态
- **THEN** Qwen-Vision适配器应返回健康状态（健康/不健康）及详细信息

---

### Requirement: Qwen-Vision Model Support
系统 SHALL 支持通义千问视觉模型（qwen-vl、qwen-vl-plus、qwen-vl-max）。

#### Scenario: Adapter selects specified model
- **WHEN** 用户在配置中指定使用某个Qwen-Vision模型
- **THEN** 适配器应使用指定的模型调用API

#### Scenario: Adapter uses default model
- **WHEN** 用户未指定模型
- **THEN** 适配器应默认使用 qwen-vl-plus 模型
