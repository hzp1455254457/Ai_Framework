# Tasks: Add Vision Routes

## 任务列表

### 1. 实现 Vision 路由核心
**角色**：`api-developer`
**文件**：`api/routes/vision.py`
**描述**：
- 创建 `router = APIRouter()` 实例
- 实现 `POST /api/vision/generate` 接口（图像生成）
- 实现 `POST /api/vision/analyze` 接口（图像分析）
- 实现 `POST /api/vision/edit` 接口（图像编辑）
- 实现错误处理和 HTTP 异常转换
- 使用依赖注入获取 Vision 服务实例

**验收标准**：
- [x] 三个路由接口实现完整
- [x] 错误处理覆盖常见场景
- [x] HTTP 状态码使用正确
- [x] 代码风格与 LLM 路由保持一致

### 2. 添加请求/响应模型
**角色**：`api-developer`
**文件**：`api/models/request.py`, `api/models/response.py`
**描述**：
- 添加 `VisionGenerateRequest` 模型
- 添加 `VisionAnalyzeRequest` 模型
- 添加 `VisionEditRequest` 模型
- 添加对应的响应模型
- 使用 Pydantic 进行数据验证

**验收标准**：
- [x] 请求模型字段完整，验证规则正确
- [x] 响应模型格式统一
- [x] 与 Vision 服务的数据模型兼容

### 3. 实现依赖注入
**角色**：`api-developer`
**文件**：`api/dependencies.py`
**描述**：
- 添加 `get_vision_service()` 函数
- 实现 Vision 服务实例的获取和缓存
- 支持配置管理器依赖

**验收标准**：
- [x] 依赖函数实现正确
- [x] 服务实例缓存机制正确
- [x] 与现有依赖注入模式一致

### 4. 注册路由到 FastAPI 应用
**角色**：`api-developer`
**文件**：`api/fastapi_app.py`
**描述**：
- 导入 Vision 路由
- 使用 `app.include_router()` 注册路由
- 配置路由前缀 `/api/vision`
- 添加路由标签 `vision`

**验收标准**：
- [x] 路由正确注册
- [x] 路由前缀和标签配置正确
- [x] 路由在 OpenAPI 文档中可见

### 5. 编写单元测试
**角色**：`ai-framework-qa-engineer`
**文件**：`tests/unit/api/routes/test_vision.py`
**描述**：
- 测试图像生成接口（Mock Vision 服务）
- 测试图像分析接口
- 测试图像编辑接口
- 测试错误处理（400、500 等）
- 测试请求验证（无效参数等）

**验收标准**：
- [x] 测试覆盖率 ≥ 80%
- [x] 所有测试用例通过（11个测试全部通过）
- [x] Mock 使用正确，使用 FastAPI dependency_overrides，不依赖真实服务

### 6. 更新 API 文档
**角色**：`ai-framework-documenter`
**文件**：`docs/api/api-reference.md`
**描述**：
- 添加 Vision API 接口文档
- 添加请求/响应示例
- 添加错误码说明
- 添加使用示例

**验收标准**：
- [x] 文档内容完整
- [x] 示例代码可运行
- [x] 错误说明清晰

## 任务依赖关系

```
任务1 (Vision路由核心) 
  ↓
任务2 (请求/响应模型) 
  ↓
任务3 (依赖注入) 
  ↓
任务4 (注册路由) ← 依赖任务1-3
  ↓
任务5 (单元测试) ← 依赖任务1-4
  ↓
任务6 (API文档更新) ← 依赖任务1-5
```

## 预计工作量

- **任务1**：3-4 小时（参考 LLM 路由实现）
- **任务2**：1-2 小时
- **任务3**：1 小时
- **任务4**：0.5 小时
- **任务5**：2-3 小时
- **任务6**：1-2 小时

**总计**：约 8.5-12.5 小时（1-2 个工作日）
