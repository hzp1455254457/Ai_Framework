## MODIFIED Requirements

### Requirement: Vision Service Architecture
系统 SHALL 采用适配器模式实现 Vision 服务，支持多种 Vision 服务提供商。

系统 SHALL 通过适配器能力查询机制智能选择适配器，确保每个图像处理功能（生成/分析/编辑）都能选择到支持该功能的大模型适配器。

#### Scenario: Developer adds new Vision adapter
- **WHEN** 开发者实现 BaseVisionAdapter 接口
- **THEN** 系统 SHALL 自动发现并注册适配器，无需修改核心服务代码

#### Scenario: User calls Vision service with specific provider
- **WHEN** 用户指定使用特定的 Vision 提供商（如 DALL-E）
- **THEN** 系统 SHALL 路由请求到对应的适配器，返回统一格式的响应

#### Scenario: System selects adapter based on operation capability
- **WHEN** 用户调用图像生成功能，未指定适配器
- **THEN** 系统 SHALL 查询所有适配器的支持能力，优先选择支持"generate"操作的适配器（如DALL-E适配器）

#### Scenario: System selects adapter based on operation capability for analysis
- **WHEN** 用户调用图像分析功能，未指定适配器
- **THEN** 系统 SHALL 查询所有适配器的支持能力，优先选择支持"analyze"操作的适配器（如Qwen-Vision适配器）

#### Scenario: System selects adapter based on operation capability for editing
- **WHEN** 用户调用图像编辑功能，未指定适配器
- **THEN** 系统 SHALL 查询所有适配器的支持能力，优先选择支持"edit"操作的适配器（如DALL-E适配器）

## ADDED Requirements

### Requirement: Vision Adapter Capability Query
系统 SHALL 提供适配器能力查询机制，允许适配器声明其支持的操作类型。

#### Scenario: Adapter declares supported operations
- **WHEN** 适配器实现 `get_supported_operations()` 方法
- **THEN** 适配器 SHALL 返回支持的操作列表（如 `["generate", "edit"]` 或 `["analyze"]`）

#### Scenario: Service queries adapter capability
- **WHEN** VisionService需要选择适配器时
- **THEN** 系统 SHALL 调用适配器的 `get_supported_operations()` 方法，获取适配器支持的操作列表

#### Scenario: Service falls back to name-based selection
- **WHEN** 适配器未实现 `get_supported_operations()` 方法
- **THEN** 系统 SHALL 回退到基于适配器名称的推断逻辑，保持向后兼容
