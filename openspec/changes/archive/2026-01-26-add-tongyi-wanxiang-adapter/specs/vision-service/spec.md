## ADDED Requirements

### Requirement: TongYi WanXiang Adapter Support
系统 SHALL 提供通义万相适配器，支持通过 DashScope API 进行图像生成。

**Rationale**: 通义万相是阿里云提供的国产图像生成服务，与通义千问使用相同的DashScope API，对中国用户友好且成本较低。需要适配器实现才能使用 Vision 服务的图像生成功能。

#### Scenario: Generate Image with TongYi WanXiang
- **WHEN** 用户调用 Vision 服务的 `generate_image()` 方法，指定使用通义万相适配器
- **THEN** 系统应通过通义万相适配器调用 DashScope API，返回生成的图像 URL 或图像数据，并记录 API 调用日志

#### Scenario: Reuse Qwen API Key
- **WHEN** Vision 配置中 `tongyi-wanxiang-adapter.api_key` 为空
- **THEN** 系统应自动从 LLM 配置中的 `qwen-adapter.api_key` 或环境变量 `QWEN_API_KEY` 获取 API 密钥，实现配置复用

#### Scenario: Handle TongYi WanXiang API Errors
- **WHEN** DashScope API 返回错误（如 API 密钥无效、限流等）
- **THEN** 系统应捕获并转换错误为 `VisionAdapterError`，记录错误日志，并向用户返回清晰的错误信息

#### Scenario: Support Different Image Sizes and Quality
- **WHEN** 用户指定不同的图像尺寸和质量选项
- **THEN** 系统应根据通义万相API支持的参数，正确传递参数并返回符合规范的响应

#### Scenario: Configure TongYi WanXiang Adapter
- **WHEN** 用户在配置文件中设置通义万相适配器参数
- **THEN** 系统应从配置文件读取 API 密钥和配置，正确初始化适配器，并支持环境变量覆盖配置和API密钥复用
