# Tasks: 增强Vision适配器支持Base64本地文件上传

## 1. 依赖与配置
- [x] 1.1 添加 `dashscope` 依赖到 `requirements.txt` (如果尚未存在)
- [x] 1.2 确认 `TongYiWanXiangAdapter` 能正确获取 API Key 并配置 DashScope SDK

**角色**：`llm-service-developer`

## 2. 适配器功能增强
- [x] 2.1 在 `TongYiWanXiangAdapter` 中实现 `_upload_image_to_dashscope(base64_data)` 方法
  - 解析 Base64 头部
  - 保存为临时文件
  - 使用 `dashscope.File.upload` (或其他适用API) 上传
  - 返回 URL
- [x] 2.2 修改 `edit_image` 方法
  - 检测 `image` 参数是否为 Base64
  - 检测 `mask` 参数是否为 Base64
  - 调用上传方法获取 URL
  - 使用 URL 调用 API
- [x] 2.3 增加错误处理（上传失败、API Key 无效等）

**角色**：`llm-service-developer`

## 3. 测试与验证
- [x] 3.1 编写单元测试 `test_tongyi_wanxiang_adapter_upload.py` 模拟 Base64 输入
- [x] 3.2 运行集成测试验证端到端流程 (Local File -> Frontend -> Backend -> DashScope -> Result)

**角色**：`ai-framework-qa-engineer`
