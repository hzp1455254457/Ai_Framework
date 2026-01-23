# Vision服务功能设计文档

## 📋 功能概述

### 功能名称
Vision服务（视觉服务）

### 功能目的
为AI框架提供统一的视觉服务接口，支持图像生成、分析和编辑功能，使框架具备多模态AI能力。

### 解决的问题
1. **多模态能力缺失**：框架目前只有LLM能力，缺少视觉处理能力
2. **接口不统一**：不同Vision服务提供商的API差异较大，需要统一接口
3. **扩展性不足**：需要支持多种Vision服务提供商（DALL-E、Stable Diffusion等）

### 使用场景
- 图像生成：根据文本提示词生成图像
- 图像分析：OCR识别、物体识别、图像理解
- 图像编辑：修改、增强、风格转换
- Agent工具：为Agent提供视觉能力工具

---

## 🏗️ 技术架构

### 架构设计

```
core/vision/
├── __init__.py           # 模块导出
├── service.py            # VisionService 核心类
├── models.py             # Vision 数据模型
├── adapters/            # 适配器目录
│   ├── __init__.py
│   └── base.py          # BaseVisionAdapter 基类
└── README.md            # 模块说明文档
```

### 类继承关系

```
BaseService (抽象基类)
    └── VisionService

BaseAdapter (抽象基类)
    └── BaseVisionAdapter
        ├── DalleAdapter (未来实现)
        ├── StableDiffusionAdapter (未来实现)
        └── ImageAnalysisAdapter (未来实现)
```

### 核心组件

1. **VisionService**：Vision服务主类
   - 管理适配器注册和路由
   - 提供统一的图像生成、分析、编辑接口
   - 处理错误和日志

2. **BaseVisionAdapter**：Vision适配器基类
   - 定义统一的适配器接口
   - 提供配置验证和生命周期管理
   - 支持图像生成、分析、编辑三种能力

3. **Vision数据模型**：
   - ImageGenerateRequest/Response：图像生成
   - ImageAnalyzeRequest/Response：图像分析
   - ImageEditRequest/Response：图像编辑

---

## 🔌 接口设计

### VisionService（服务主类）

#### 核心职责
- 管理适配器注册和路由
- 提供统一的Vision服务接口
- 处理错误和日志记录

#### 公共接口

```python
class VisionService(BaseService):
    async def initialize(self) -> None:
        """初始化服务资源"""
    
    def register_adapter(self, adapter: BaseVisionAdapter) -> None:
        """手动注册适配器"""
    
    async def generate_image(
        self,
        request: ImageGenerateRequest,
        adapter_name: Optional[str] = None,
        **kwargs: Any,
    ) -> ImageGenerateResponse:
        """生成图像"""
    
    async def analyze_image(
        self,
        request: ImageAnalyzeRequest,
        adapter_name: Optional[str] = None,
        **kwargs: Any,
    ) -> ImageAnalyzeResponse:
        """分析图像"""
    
    async def edit_image(
        self,
        request: ImageEditRequest,
        adapter_name: Optional[str] = None,
        **kwargs: Any,
    ) -> ImageEditResponse:
        """编辑图像"""
```

### BaseVisionAdapter（适配器基类）

#### 核心职责
- 定义统一的适配器接口
- 提供配置验证
- 管理适配器生命周期

#### 抽象方法

```python
class BaseVisionAdapter(BaseAdapter):
    @property
    @abstractmethod
    def provider(self) -> str:
        """服务提供商名称"""
    
    @abstractmethod
    async def generate_image(
        self,
        request: ImageGenerateRequest,
        **kwargs: Any,
    ) -> ImageGenerateResponse:
        """生成图像"""
    
    @abstractmethod
    async def analyze_image(
        self,
        request: ImageAnalyzeRequest,
        **kwargs: Any,
    ) -> ImageAnalyzeResponse:
        """分析图像"""
    
    @abstractmethod
    async def edit_image(
        self,
        request: ImageEditRequest,
        **kwargs: Any,
    ) -> ImageEditResponse:
        """编辑图像"""
```

---

## 📊 数据模型

### ImageGenerateRequest
- `prompt` (str): 文本提示词（必填）
- `size` (ImageSize): 图像尺寸，默认 1024x1024
- `n` (int): 生成图像数量，默认 1，范围 1-10
- `quality` (str): 图像质量（standard/hd），默认 standard
- `style` (Optional[str]): 图像风格（可选）
- `metadata` (Optional[Dict]): 其他元数据

### ImageGenerateResponse
- `images` (List[str]): 生成的图像列表（URL或base64）
- `model` (str): 使用的模型名称
- `count` (int): 生成的图像数量
- `created_at` (datetime): 创建时间
- `metadata` (Dict): 其他元数据

### ImageAnalyzeRequest
- `image` (str): 图像数据（URL、base64或文件路径）
- `analyze_type` (AnalyzeType): 分析类型（OCR/物体识别/图像理解/ALL）
- `options` (Optional[Dict]): 分析选项
- `metadata` (Optional[Dict]): 其他元数据

### ImageAnalyzeResponse
- `model` (str): 使用的模型名称
- `text` (Optional[str]): OCR识别的文本
- `objects` (List[Dict]): 识别的物体列表
- `description` (Optional[str]): 图像描述
- `created_at` (datetime): 创建时间
- `metadata` (Dict): 其他元数据

### ImageEditRequest
- `image` (str): 原始图像数据（必填）
- `prompt` (str): 编辑提示词（必填）
- `mask` (Optional[str]): 遮罩图像（可选）
- `size` (Optional[ImageSize]): 输出图像尺寸（可选）
- `n` (int): 生成图像数量，默认 1
- `metadata` (Optional[Dict]): 其他元数据

### ImageEditResponse
- `images` (List[str]): 编辑后的图像列表
- `model` (str): 使用的模型名称
- `count` (int): 编辑后的图像数量
- `created_at` (datetime): 创建时间
- `metadata` (Dict): 其他元数据

---

## 🔄 实现细节

### 适配器管理
- Vision服务支持手动注册适配器
- 适配器通过 `register_adapter()` 方法注册
- 支持指定适配器名称或使用默认适配器

### 错误处理
- 使用 VisionError 异常类
- 所有适配器调用错误都会被捕获并转换为 VisionError
- 记录详细的错误日志

### 配置管理
- 通过 `config["vision"]` 配置Vision服务
- 支持 `default_adapter` 配置默认适配器
- 支持 `auto_discover_adapters` 配置自动发现（未来实现）

---

## 🧪 测试策略

### 单元测试
- VisionService 测试：服务初始化、适配器注册、接口调用
- BaseVisionAdapter 测试：适配器接口、生命周期管理
- 数据模型测试：请求/响应模型验证、类型转换

### 测试覆盖率
- 目标：≥80%
- 关键路径：100%

---

## 📚 依赖关系

### 依赖模块
- `core.base.service`: 服务基类
- `core.base.adapter`: 适配器基类
- `infrastructure.config`: 配置管理
- `infrastructure.log`: 日志管理

### 被依赖模块
- `api/routes/vision.py`: Vision API路由（未来实现）
- `core/agent/`: Agent引擎（可使用Vision工具）

---

## 🔄 变更历史

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-01-22 | v1.0 | 初始版本，实现Vision服务核心 | - |
