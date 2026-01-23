# api-server Specification Delta

## ADDED Requirements

### Requirement: Vision API Routes
系统 SHALL 提供 Vision 服务的 RESTful API 接口，支持图像生成、分析和编辑功能。

**Rationale**: Vision 服务需要通过 API 路由暴露给外部调用，以支持 Web 应用和第三方集成。

#### Scenario: Generate Image via API
**Given** Vision 服务已配置并运行
**When** 用户发送 POST 请求到 `/api/vision/generate`，包含有效的图像生成参数
**Then** 系统应：
1. 验证请求参数
2. 调用 Vision 服务的 `generate_image()` 方法
3. 返回生成的图像 URL 或图像数据
4. 返回 HTTP 200 状态码

#### Scenario: Analyze Image via API
**Given** Vision 服务已配置并运行
**When** 用户发送 POST 请求到 `/api/vision/analyze`，包含图像文件或图像 URL
**Then** 系统应：
1. 验证请求参数和图像文件
2. 调用 Vision 服务的 `analyze_image()` 方法
3. 返回图像分析结果
4. 返回 HTTP 200 状态码

#### Scenario: Edit Image via API
**Given** Vision 服务已配置并运行
**When** 用户发送 POST 请求到 `/api/vision/edit`，包含图像文件、编辑提示词等参数
**Then** 系统应：
1. 验证请求参数和图像文件
2. 调用 Vision 服务的 `edit_image()` 方法
3. 返回编辑后的图像 URL 或图像数据
4. 返回 HTTP 200 状态码

#### Scenario: Handle Vision API Errors
**Given** Vision API 接口已部署
**When** API 调用失败（如参数无效、服务错误等）
**Then** 系统应：
1. 捕获错误并转换为适当的 HTTP 状态码
2. 返回包含错误信息的 JSON 响应
3. 记录错误日志

#### Scenario: Validate Vision API Requests
**Given** Vision API 接口已部署
**When** 用户发送包含无效参数的请求
**Then** 系统应：
1. 使用 Pydantic 验证请求参数
2. 返回 HTTP 400 状态码和验证错误信息
3. 不调用 Vision 服务
