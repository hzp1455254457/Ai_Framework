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
