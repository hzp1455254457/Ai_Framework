# Change: 增强Vision适配器支持Base64本地文件上传 (TongYi WanXiang)

## Why

当前通义万相 (TongYi WanXiang) 适配器仅支持 HTTP/HTTPS URL 作为图像编辑的输入。这导致以下问题：
1. **用户体验受限**：用户无法直接上传本地图片进行编辑，必须先自行将图片托管到公开网络。
2. **前端兼容性问题**：前端 `ImageEditor` 组件虽然支持文件选择（转换为Base64），但后端适配器因API限制而拒绝Base64输入。
3. **API限制**：DashScope API 对 Base64 字符串长度有限制（或不支持），要求使用 URL。

为了解决这个问题，我们需要在适配器层实现 "Base64 -> URL" 的自动转换机制，使用户可以直接使用本地图片进行编辑。

## What Changes

### 核心变更

1. **后端：引入文件上传机制**
   - 引入 `dashscope` SDK 或使用 DashScope File API。
   - 在 `TongYiWanXiangAdapter` 中增加 `_upload_image(base64_str)` 私有方法。
   - 当检测到输入为 Base64 时，自动将其解码并上传到 DashScope 临时存储（或配置的 OSS）。
   - 获取上传后的 URL，替换原始请求中的 Base64 数据。

2. **后端：增强适配器逻辑**
   - 修改 `edit_image` 方法，在调用 API 前预处理 `image` 和 `mask` 参数。
   - 支持 `data:image/...;base64,` 格式的自动解析。

3. **配置更新**
   - 可能需要增加 `dashscope_api_key` 的依赖（已存在，复用 qwen adapter key）。

### 架构变更

**当前流程**：
```
Client (Base64) -> Adapter -> (Validation Error: URL required) -> Fail
```

**新流程**：
```
Client (Base64) -> Adapter -> Check if Base64?
                      |
                      +-> Yes -> Upload to DashScope/OSS -> Get URL -> Call WanXiang API -> Success
                      |
                      +-> No (URL) -> Call WanXiang API -> Success
```

## Impact

### 受影响的能力规格

- **vision-service**: 增强 `edit_image` 能力，支持 Base64 输入。

### 受影响的代码模块

1. **core/vision/adapters/tongyi_wanxiang_adapter.py**:
   - 引入 `dashscope` (需要添加依赖)。
   - 实现上传逻辑。
   - 修改 `edit_image` 流程。

### 新增依赖

- **dashscope**: 阿里云官方 SDK（建议使用 SDK 简化上传和调用流程）。
  - `pip install dashscope`

### 兼容性保证

- **向后兼容**：原有的 URL 输入方式继续支持。
- **透明升级**：调用方（前端）无需感知上传过程，只需发送 Base64 即可。
