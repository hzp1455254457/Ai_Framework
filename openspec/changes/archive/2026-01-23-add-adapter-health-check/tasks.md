# Tasks: Add Adapter Health Check

## 任务列表

### 1. 实现健康检查服务模块
**角色**：`infrastructure-developer`
**文件**：`core/base/health_check.py`
**描述**：
- 创建 `HealthStatus` 枚举（HEALTHY、UNHEALTHY、UNKNOWN）
- 创建 `HealthCheckResult` 数据类
- 创建 `BaseHealthCheck` 抽象基类
- 实现基础健康检查功能
- 提供健康检查工具函数

**验收标准**：
- [x] 健康检查接口定义清晰
- [x] 支持同步和异步健康检查
- [x] 代码包含完整的类型注解和文档字符串

### 2. 扩展适配器基类
**角色**：`llm-service-developer`（适配器相关）
**文件**：`core/base/adapter.py`
**描述**：
- 添加 `health_check()` 抽象方法
- 添加 `is_healthy()` 属性方法
- 实现基础健康检查逻辑（可选）
- 支持子类重写健康检查逻辑

**验收标准**：
- [x] 健康检查接口正确添加到基类
- [x] 支持子类自定义实现
- [x] 向后兼容现有适配器

### 3. 实现 LLM 适配器健康检查
**角色**：`llm-service-developer`
**文件**：`core/llm/adapters/base.py`、各 LLM 适配器文件
**描述**：
- 在 `BaseLLMAdapter` 中实现健康检查抽象方法
- 在各 LLM 适配器中实现具体健康检查逻辑
- 通过轻量级 API 调用检测适配器可用性
- 实现超时和错误处理

**验收标准**：
- [x] 所有 LLM 适配器实现健康检查（OpenAI适配器已实现）
- [x] 健康检查逻辑正确（轻量级、快速）
- [x] 错误处理完善

### 4. 实现 Vision 适配器健康检查
**角色**：`llm-service-developer`（适配器相关）
**文件**：`core/vision/adapters/base.py`、Vision 适配器文件
**描述**：
- 在 `BaseVisionAdapter` 中实现健康检查抽象方法
- 在 Vision 适配器中实现具体健康检查逻辑
- 检查 API 端点可用性

**验收标准**：
- [x] Vision 适配器支持健康检查（DALL-E适配器已实现）
- [x] 健康检查逻辑正确
- [x] 错误处理完善

### 5. 集成服务层健康检查
**角色**：`llm-service-developer`
**文件**：`core/llm/service.py`、`core/vision/service.py`
**描述**：
- 在服务层添加健康检查方法
- 实现自动故障转移（选择可用适配器）
- 支持健康状态查询
- 支持配置故障转移策略

**验收标准**：
- [x] 服务层支持健康检查
- [x] 自动故障转移逻辑正确
- [x] 配置支持完善

### 6. 实现健康检查 API
**角色**：`api-developer`
**文件**：`api/routes/health.py`
**描述**：
- 添加适配器健康状态接口（`GET /api/health/adapters`）
- 返回所有适配器的健康状态
- 支持按服务类型过滤（LLM、Vision 等）

**验收标准**：
- [x] 健康检查 API 接口实现
- [x] 返回格式清晰
- [x] 支持过滤和查询

### 7. 添加配置支持
**角色**：`infrastructure-developer`
**文件**：`config/default.yaml`
**描述**：
- 添加健康检查配置项
- 配置健康检查间隔
- 配置故障转移策略
- 配置超时时间

**验收标准**：
- [x] 配置文件格式正确
- [x] 配置项与实现匹配

### 8. 编写单元测试
**角色**：`ai-framework-qa-engineer`
**文件**：
- `tests/unit/core/base/test_health_check.py`
- `tests/unit/core/llm/test_adapter_health.py`
- `tests/unit/core/vision/test_adapter_health.py`
**描述**：
- 测试健康检查服务模块
- 测试适配器健康检查实现
- 测试服务层健康检查集成
- 测试自动故障转移
- 测试健康检查 API

**验收标准**：
- [ ] 测试覆盖率 ≥ 80%
- [ ] 所有测试用例通过
- [ ] 测试覆盖各种健康检查场景

### 9. 更新文档
**角色**：`ai-framework-documenter`
**文件**：适配器相关文档
**描述**：
- 添加健康检查使用说明
- 添加故障转移配置说明
- 添加监控集成说明

**验收标准**：
- [ ] 文档内容完整
- [ ] 示例代码可运行
- [ ] 配置说明清晰

## 任务依赖关系

```
任务1 (健康检查服务模块) 
  ↓
任务2 (适配器基类扩展) ← 依赖任务1
  ↓
任务3 (LLM适配器健康检查) ← 依赖任务2
任务4 (Vision适配器健康检查) ← 依赖任务2
  ↓
任务5 (服务层健康检查集成) ← 依赖任务3-4
  ↓
任务6 (健康检查API) ← 依赖任务5
  ↓
任务7 (配置支持) ← 依赖任务5
  ↓
任务8 (单元测试) ← 依赖任务1-7
  ↓
任务9 (文档更新) ← 依赖任务1-8
```

## 预计工作量

- **任务1**：2-3 小时
- **任务2**：1-2 小时
- **任务3**：3-4 小时（多个 LLM 适配器）
- **任务4**：1-2 小时（Vision 适配器）
- **任务5**：2-3 小时
- **任务6**：1-2 小时
- **任务7**：0.5 小时
- **任务8**：3-4 小时
- **任务9**：1-2 小时

**总计**：约 15-23 小时（2-3 个工作日）
