# 基础类和接口模块

## 模块概述

本模块提供AI框架中所有服务、适配器和插件的基础抽象类，定义统一的接口规范。

**在整体架构中的位置**：
- 属于核心服务层的基础组件
- 被所有核心服务模块（LLM、Vision、Audio、Agent）依赖
- 不依赖其他业务模块，只依赖基础设施层

**核心职责**：
- 定义统一的服务接口规范
- 定义统一的适配器接口规范
- 定义统一的插件接口规范
- 提供基础功能和通用实现

---

## 模块结构

```
core/base/
├── __init__.py          # 模块导出
├── service.py           # 服务基类
├── adapter.py           # 适配器基类
├── plugin.py            # 插件基类
└── README.md            # 本文件
```

---

## 核心API

### BaseService（服务基类）

所有服务的基础抽象类。

**主要方法**：
- `__init__(config)` - 初始化服务
- `initialize()` - 异步初始化资源
- `cleanup()` - 清理资源
- `config` - 获取配置（属性）
- `logger` - 获取日志记录器（属性）

**使用示例**：
```python
from core.base.service import BaseService

class MyService(BaseService):
    async def initialize(self) -> None:
        # 自定义初始化逻辑
        await super().initialize()
        # 初始化其他资源
    
    # 实现服务特定的方法
    async def process(self, data: str) -> str:
        self.logger.info(f"处理数据: {data}")
        return f"处理结果: {data}"

# 使用服务
service = MyService(config)
await service.initialize()
result = await service.process("test")
await service.cleanup()
```

### BaseAdapter（适配器基类）

所有适配器的基础抽象类。

**主要方法**：
- `name` - 适配器名称（抽象属性）
- `provider` - 服务提供商名称（抽象属性）
- `initialize(config)` - 初始化适配器
- `call(*args, **kwargs)` - 调用服务（抽象方法）
- `stream_call(*args, **kwargs)` - 流式调用
- `cleanup()` - 清理资源

**使用示例**：
```python
from core.base.adapter import BaseAdapter

class MyAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "my-adapter"
    
    @property
    def provider(self) -> str:
        return "my-provider"
    
    async def call(self, *args, **kwargs) -> dict:
        # 实现调用逻辑
        return {"content": "响应内容"}

# 使用适配器
adapter = MyAdapter()
await adapter.initialize({"api_key": "..."})
response = await adapter.call(messages=[...])
```

### BasePlugin（插件基类）

所有插件的基础抽象类。

**主要方法**：
- `name` - 插件名称（抽象属性）
- `version` - 插件版本（抽象属性）
- `description` - 插件描述（抽象属性）
- `initialize(config)` - 初始化插件
- `execute(context)` - 执行插件逻辑（抽象方法）
- `cleanup()` - 清理资源

**使用示例**：
```python
from core.base.plugin import BasePlugin

class MyPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "my-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "我的插件描述"
    
    async def execute(self, context: dict) -> dict:
        # 实现插件逻辑
        return {"result": "执行结果"}

# 使用插件
plugin = MyPlugin()
await plugin.initialize()
result = await plugin.execute({"input": "数据"})
```

---

## 依赖关系

### 依赖的其他模块
- 无（基础模块，不依赖其他业务模块）

### 被哪些模块依赖
- `core/llm/` - LLM服务模块
- `core/vision/` - 视觉服务模块
- `core/audio/` - 音频服务模块
- `core/agent/` - Agent引擎模块

### 外部依赖
- Python标准库：`abc`, `typing`, `asyncio`, `logging`
- 无第三方依赖

---

## 设计模式

### 模板方法模式
- BaseService定义了服务的初始化流程模板
- 子类可以重写特定方法自定义行为

### 策略模式
- BaseAdapter定义了适配器接口
- 不同的适配器实现不同的调用策略

### 插件模式
- BasePlugin定义了插件接口
- 支持动态加载和执行插件

---

## 扩展指南

### 如何创建新的服务

1. 继承 `BaseService`
2. 实现必要的初始化逻辑
3. 实现服务特定的业务方法

### 如何创建新的适配器

1. 继承 `BaseAdapter`
2. 实现 `name` 和 `provider` 属性
3. 实现 `call()` 方法
4. 可选：实现 `stream_call()` 方法

### 如何创建新的插件

1. 继承 `BasePlugin`
2. 实现 `name`、`version`、`description` 属性
3. 实现 `execute()` 方法

---

## 相关文档

- [基础服务框架设计文档](../../docs/design/base-service-framework.md)
- [架构方案文档](../../AI框架架构方案文档.md)
- [架构决策记录](../../docs/architecture/decisions/ADR-0001-适配器模式.md)

---

## 更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-01-21 | 1.0 | 初始版本，实现基础服务框架 | - |
