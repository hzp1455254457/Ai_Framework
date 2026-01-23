# vision-service Specification Delta

## MODIFIED Requirements

### Requirement: DALL-E Adapter Support
系统 SHALL 提供 DALL-E 适配器，支持通过 OpenAI Images API 进行图像生成。

**Rationale**: DALL-E 是主流的图像生成服务，需要适配器实现才能使用 Vision 服务的图像生成功能。

#### Scenario: Generate Image with DALL-E 3
**Given** 用户配置了有效的 OpenAI API 密钥
**When** 用户调用 Vision 服务的 `generate_image()` 方法，指定使用 DALL-E 3 模型
**Then** 系统应：
1. 通过 DALL-E 适配器调用 OpenAI Images API
2. 返回生成的图像 URL 或图像数据
3. 记录 API 调用日志

#### Scenario: Handle DALL-E API Errors
**Given** DALL-E 适配器已初始化
**When** OpenAI API 返回错误（如 API 密钥无效、限流等）
**Then** 系统应：
1. 捕获并转换错误为 `AdapterCallError`
2. 记录错误日志
3. 向用户返回清晰的错误信息

#### Scenario: Support DALL-E 2 and DALL-E 3
**Given** DALL-E 适配器已初始化
**When** 用户指定不同的 DALL-E 模型（DALL-E 2 或 DALL-E 3）
**Then** 系统应：
1. 根据模型选择调用对应的 API 端点
2. 正确处理不同模型的参数差异
3. 返回符合模型规范的响应

#### Scenario: Configure DALL-E Adapter
**Given** 用户需要配置 DALL-E 适配器
**When** 用户在配置文件中设置 DALL-E 适配器参数
**Then** 系统应：
1. 从配置文件读取 API 密钥和配置
2. 正确初始化适配器
3. 支持环境变量覆盖配置
