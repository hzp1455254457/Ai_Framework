# Vision服务模块

## 📋 模块概述

Vision服务模块提供统一的视觉服务接口，支持图像生成、分析和编辑功能。

## 🏗️ 模块结构

```
core/vision/
├── __init__.py           # 模块导出
├── service.py            # VisionService 核心类
├── models.py             # Vision 数据模型
├── adapters/             # 适配器目录
│   ├── __init__.py
│   ├── base.py          # BaseVisionAdapter 基类
│   └── dalle_adapter.py # DALL-E适配器
└── README.md            # 本文件
```

## 🔌 核心API

### VisionService

```python
from core.vision import VisionService, ImageGenerateRequest

# 创建服务
service = VisionService(config)
await service.initialize()

# 注册适配器
adapter = MyVisionAdapter(adapter_config)
await adapter.initialize()
service.register_adapter(adapter)

# 生成图像
request = ImageGenerateRequest(prompt="A beautiful sunset")
response = await service.generate_image(request)
print(f"生成了 {response.count} 张图像")
```

### BaseVisionAdapter

```python
from core.vision.adapters.base import BaseVisionAdapter
from core.vision.models import ImageGenerateRequest, ImageGenerateResponse

class MyAdapter(BaseVisionAdapter):
    @property
    def name(self) -> str:
        return "my-adapter"
    
    @property
    def provider(self) -> str:
        return "my-provider"
    
    async def generate_image(self, request, **kwargs):
        # 实现图像生成逻辑
        return ImageGenerateResponse(...)
```

### DALLEAdapter（DALL-E适配器）

DALL-E适配器实现了OpenAI DALL-E图像生成服务的集成，支持DALL-E 2和DALL-E 3模型。

**特性**：
- 支持DALL-E 2和DALL-E 3模型
- 支持图像生成功能
- 支持DALL-E 2的图像编辑功能（DALL-E 3不支持）
- 错误处理和重试机制

**使用示例**：

```python
from core.vision.adapters.dalle_adapter import DALLEAdapter
from core.vision.models import ImageGenerateRequest, ImageSize

# 创建适配器
adapter = DALLEAdapter({
    "api_key": "sk-your-openai-api-key",
    "default_model": "dall-e-3"
})
await adapter.initialize()

# 生成图像（DALL-E 3）
request = ImageGenerateRequest(
    prompt="A beautiful sunset over the ocean",
    size=ImageSize.SQUARE_1024,
    n=1,  # DALL-E 3只支持n=1
    quality="hd",
    style="vivid"
)
response = await adapter.generate_image(request)
print(f"生成的图像URL: {response.images[0]}")

# 生成图像（DALL-E 2，支持多张）
request2 = ImageGenerateRequest(
    prompt="A cute cat",
    size=ImageSize.SQUARE_512,
    n=2  # DALL-E 2支持多张
)
response2 = await adapter.generate_image(request2, model="dall-e-2")
print(f"生成了 {response2.count} 张图像")
```

**配置说明**：

在 `config/default.yaml` 中配置：

```yaml
vision:
  adapters:
    dalle-adapter:
      api_key: "sk-your-openai-api-key"  # OpenAI API密钥
      base_url: "https://api.openai.com/v1"  # 可选，默认OpenAI API端点
      default_model: "dall-e-3"  # 默认模型（dall-e-2 或 dall-e-3）
```

**模型差异**：

| 特性 | DALL-E 2 | DALL-E 3 |
|------|----------|----------|
| 支持的尺寸 | 256x256, 512x512, 1024x1024 | 1024x1024, 1024x1792, 1792x1024 |
| 生成数量 | 1-10 | 仅1 |
| 质量选项 | 不支持 | standard/hd |
| 风格选项 | 不支持 | vivid/natural |
| 图像编辑 | ✅ 支持 | ❌ 不支持 |
| 图像分析 | ❌ 不支持 | ❌ 不支持 |

**常见问题**：

1. **Q: DALL-E 3为什么只支持生成1张图像？**
   - A: 这是OpenAI API的限制，DALL-E 3每次调用只能生成1张图像。

2. **Q: 如何选择DALL-E 2还是DALL-E 3？**
   - A: DALL-E 3质量更高，但功能限制更多（只支持1张、不支持编辑）。DALL-E 2更灵活，支持多张生成和编辑。

3. **Q: 图像编辑功能如何使用？**
   - A: 使用DALL-E 2模型，调用`edit_image()`方法，需要提供原始图像和编辑提示词。

## QwenVisionAdapter（通义千问Vision适配器）

Qwen-Vision适配器实现了阿里云通义千问Qwen-VL视觉模型的集成，支持图像理解、OCR文字识别和物体识别等功能。

**特性**：
- 支持Qwen-VL、Qwen-VL-Plus、Qwen-VL-Max模型
- 支持通用图像理解（图像内容描述）
- 支持OCR光学字符识别（提取图片中的文字）
- 支持物体识别（识别图片中的物体和场景）
- 错误处理和重试机制
- 与现有Vision服务无缝集成

**使用示例**：

```python
from core.vision.adapters.qwen_vision_adapter import QwenVisionAdapter
from core.vision.models import ImageAnalyzeRequest, AnalyzeType

# 创建适配器
adapter = QwenVisionAdapter({
    "api_key": "your-qwen-api-key",
    "model": "qwen-vl-plus"
})
await adapter.initialize()

# 通用图像理解
request = ImageAnalyzeRequest(
    image="https://example.com/image.jpg",
    analyze_type=AnalyzeType.IMAGE_UNDERSTANDING
)
response = await adapter.analyze_image(request)
print(f"图像描述: {response.description}")

# OCR文字识别
ocr_request = ImageAnalyzeRequest(
    image="https://example.com/document.jpg",
    analyze_type=AnalyzeType.OCR
)
ocr_response = await adapter.analyze_image(ocr_request)
print(f"识别文字: {ocr_response.text}")

# 物体识别
object_request = ImageAnalyzeRequest(
    image="https://example.com/scene.jpg",
    analyze_type=AnalyzeType.OBJECT_DETECTION
)
object_response = await adapter.analyze_image(object_request)
print(f"识别物体: {object_response.objects}")
```

**配置说明**：

在 `config/default.yaml` 中配置：

```yaml
vision:
  adapters:
    qwen-vision-adapter:
      enabled: true
      api_key: "your-qwen-api-key"  # 支持加密存储或从环境变量读取
      base_url: "https://dashscope.aliyuncs.com/api/v1"  # 可选，默认通义千问API端点
      model: "qwen-vl-plus"  # 默认模型（qwen-vl / qwen-vl-plus / qwen-vl-max）
      timeout: 60  # 请求超时时间（秒）
```

**模型对比**：

| 特性 | qwen-vl | qwen-vl-plus | qwen-vl-max |
|------|---------|--------------|-------------|
| 图像理解 | ✅ 支持 | ✅ 支持 | ✅ 支持 |
| OCR识别 | ✅ 支持 | ✅ 支持 | ✅ 支持 |
| 物体识别 | ✅ 支持 | ✅ 支持 | ✅ 支持 |
| 中文优化 | 基础 | 增强 | 增强 |
| 上下文长度 | 短 | 中等 | 长 |
| 价格 | 低 | 中 | 高 |

**注意事项**：

1. **Q: 通义千问Vision模型支持图像生成吗？**
   - A: 不支持。通义千问Vision模型专注于图像分析（理解、OCR、物体识别）。如需图像生成，请使用DALL-E适配器。

2. **Q: 如何选择模型？**
   - A: `qwen-vl-plus` 是最均衡的选择，支持大部分场景。如果需要更长上下文或更高质量，可以选择 `qwen-vl-max`。

3. **Q: 支持base64编码的图片吗？**
   - A: 支持。适配器会自动检测图片格式，支持URL、base64和data URL格式。

## TongYiWanXiangAdapter（通义万相图像生成适配器）

TongYi-WanXiang适配器实现了阿里云通义万相图像生成服务的集成，支持文本到图像生成（文生图）。

**特性**：
- 支持通义万相图像生成API（wanx-v1模型）
- 支持多种图像尺寸（1024x1024、1024x1792、1792x1024）
- 支持API密钥复用（与通义千问共用DashScope API）
- 错误处理和重试机制
- 与现有Vision服务无缝集成

**使用示例**：

```python
from core.vision.adapters.tongyi_wanxiang_adapter import TongYiWanXiangAdapter
from core.vision.models import ImageGenerateRequest, ImageSize

# 创建适配器（API密钥可留空，会从Qwen配置或环境变量自动获取）
adapter = TongYiWanXiangAdapter({
    "api_key": "",  # 可留空，会自动复用Qwen的API密钥
    "model": "wanx-v1"
})
await adapter.initialize()

# 生成图像
request = ImageGenerateRequest(
    prompt="一只可爱的橘猫坐在窗台上，阳光洒在它身上",
    size=ImageSize.SQUARE_1024,
)
response = await adapter.generate_image(request)
print(f"生成的图像URL: {response.images[0]}")
print(f"任务ID: {response.metadata['task_id']}")
```

**配置说明**：

在 `config/default.yaml` 中配置：

```yaml
vision:
  adapters:
    tongyi-wanxiang-adapter:
      enabled: true
      api_key: ""  # 可留空，会从环境变量QWEN_API_KEY或qwen-adapter配置自动获取
      base_url: "https://dashscope.aliyuncs.com/api/v1"  # 可选，默认DashScope API端点
      model: "wanx-v1"  # 默认模型
      timeout: 120  # 请求超时时间（秒，图像生成需要更长时间）
```

**API密钥复用**：

通义万相与通义千问使用相同的DashScope API，因此可以复用API密钥：

1. **方式1**：环境变量
   ```bash
   export QWEN_API_KEY="your-api-key"
   ```

2. **方式2**：LLM配置（qwen-adapter）
   ```yaml
   llm:
     adapters:
       qwen-adapter:
         api_key: "your-api-key"  # 这个密钥会自动被通义万相复用
   ```

**支持的功能**：

|| 功能 | 支持情况 |
|------|------|---------|
| 图像生成 | 文生图 | ✅ 支持 |
| 图像分析 | 图像理解、OCR | ❌ 不支持 |
| 图像编辑 | 图像编辑 | ❌ 不支持 |

**支持的图像尺寸**：

|| 尺寸 | 比例 |
|------|------|------|
| 1024x1024 | 1:1 正方形 |
| 1024x1792 | 9:16 竖屏 |
| 1792x1024 | 16:9 横屏 |

**注意事项**：

1. **Q: 通义万相支持图像分析吗？**
   - A: 不支持。通义万相专注于图像生成。如需图像分析，请使用Qwen-Vision适配器。

2. **Q: 如何选择使用DALL-E还是通义万相？**
   - A: 
     - **通义万相**：中国用户友好，配置简单（可复用Qwen密钥），价格相对较低
     - **DALL-E**：国际通用，质量稳定，支持图像编辑功能

3. **Q: 通义万相支持图像编辑吗？**
   - A: 不支持。如需图像编辑，请使用DALL-E 2模型。

## 📦 依赖关系

### 依赖
- `core.base.service`: 服务基类
- `core.base.adapter`: 适配器基类
- `infrastructure.config`: 配置管理
- `infrastructure.log`: 日志管理

### 被依赖
- `api/routes/vision.py`: Vision API路由（未来实现）
- `core/agent/`: Agent引擎（可使用Vision工具）

## 📚 相关文档

- [功能设计文档](../../docs/design/vision-service.md)
- [架构方案文档](../../AI框架架构方案文档.md)
