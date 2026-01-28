---
alwaysApply: true
---
# 💻 代码与工程规范

## 📋 文档说明
本文档详细规定了代码风格、异步编程、类型注解、错误处理、日志记录和测试规范。所有代码必须严格遵循此规范。

## 1. 通用代码风格

### 1.1 命名规范
- **类名**：使用 `PascalCase`（如 `LlmService`）
- **函数/变量名**：使用 `snake_case`（如 `process_request`）
- **常量名**：使用 `UPPER_CASE`（如 `MAX_RETRIES`）
- **私有成员**：使用 `_snake_case`（如 `_internal_helper`）
- **模块/文件名**：使用 `snake_case`（如 `llm_service.py`）

### 1.2 代码结构
- **导入顺序**：
  1. 标准库导入
  2. 第三方库导入
  3. 本地模块导入
  - 每组之间空一行
- **类结构**：
  1. `__init__`
  2. 公共方法
  3. 私有方法
  4. 静态方法/类方法

### 1.3 注释规范
- **Docstring**：所有公共类和函数必须有 Google 风格的 Docstring
- **行内注释**：仅在逻辑复杂处添加，解释"为什么"而不是"做什么"
- **TODO**：使用 `# TODO: 说明` 标记待办事项

## 2. 异步编程规范（硬性规则）

**⚠️ 核心原则：IO密集型操作必须全链路异步**

### 2.1 必须使用 `async/await` 的场景
- 所有网络请求（HTTP, DB, Redis, etc.）
- 所有文件 I/O 操作（使用 `aiofiles`）
- 所有耗时操作（如 LLM 推理等待）

### 2.2 禁止使用同步阻塞调用
- ❌ 禁止使用 `requests` 库（必须用 `httpx`）
- ❌ 禁止使用 `time.sleep()`（必须用 `await asyncio.sleep()`）
- ❌ 禁止在 async 函数中调用同步 IO 函数
- ✅ 必须使用 `await` 调用异步函数

**示例**：
```python
# ✅ 正确
import httpx
import asyncio

async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ❌ 错误
import requests
import time

async def fetch_data_wrong(url: str) -> dict:
    time.sleep(1)  # 阻塞整个事件循环！
    response = requests.get(url)  # 阻塞！
    return response.json()
```

### 2.3 并发控制
- 使用 `asyncio.gather()` 并发执行多个独立任务
- 使用 `asyncio.as_completed()` 处理流式并发结果
- 必须处理并发异常（`return_exceptions=True` 或 try-except）

**示例**：
```python
# ✅ 并发执行多个任务
results = await asyncio.gather(
    task1(),
    task2(),
    return_exceptions=True
)
```

## 3. 类型注解规范（硬性规则）

**⚠️ 核心原则：所有函数参数和返回值必须有类型注解**

### 3.1 基本要求
- 所有公共函数必须标注参数类型和返回值类型
- 使用 `typing` 模块的高级类型（`List`, `Dict`, `Optional`, `Union`, `Any` 等）
- 复杂数据结构优先使用 `Pydantic` 模型

### 3.2 Pydantic 模型使用
- 数据传输对象（DTO）必须使用 `Pydantic` 模型
- 配置类必须继承 `BaseSettings`
- 必须定义 `Config` 类以支持额外配置

**示例**：
```python
from typing import List, Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    roles: List[str] = []

# ✅ 正确：完整类型注解
async def get_user(user_id: int) -> Optional[User]:
    # ... implementation
    pass
```

## 4. 错误处理规范

### 4.1 异常捕获
- 禁止捕获裸 `Exception`（除非在顶层入口）
- 必须捕获特定异常类型
- 捕获异常后必须记录日志或重新抛出

### 4.2 自定义异常
- 模块必须定义自己的基础异常类
- 业务异常继承自基础异常类
- 异常类名以 `Error` 结尾

**示例**：
```python
class LlmServiceError(Exception):
    """LLM服务基础异常"""
    pass

class ModelNotFoundError(LlmServiceError):
    """模型未找到异常"""
    pass

async def call_model(name: str):
    try:
        # ...
    except KeyError as e:
        # ✅ 转换为业务异常
        raise ModelNotFoundError(f"Model {name} not found") from e
```

## 5. 日志规范

### 5.1 日志记录原则
- 使用项目统一的日志配置（`core.utils.logger`）
- 关键流程必须有日志（开始、结束、异常）
- 异常日志必须包含堆栈信息（`exc_info=True`）
- 禁止使用 `print()`

### 5.2 日志级别使用
- `DEBUG`: 调试信息（详细变量值）
- `INFO`: 关键流程节点（启动、连接成功、任务完成）
- `WARNING`: 预期内的异常情况（重试、降级）
- `ERROR`: 预期外的错误（服务不可用、数据损坏）
- `CRITICAL`: 系统级崩溃

**示例**：
```python
from core.utils.logger import logger

async def process_task(task_id: str):
    logger.info(f"Start processing task: {task_id}")
    try:
        # ...
        logger.debug(f"Task details: {details}")
    except Exception as e:
        logger.error(f"Failed to process task {task_id}", exc_info=True)
        raise
```

## 6. 测试规范

### 6.1 测试框架
- 使用 `pytest` 作为测试框架
- 使用 `pytest-asyncio` 处理异步测试
- 使用 `unittest.mock` 进行模拟

### 6.2 测试覆盖率目标
- **核心模块**（core/）：90% 以上
- **业务模块**：80% 以上
- **工具模块**：80% 以上

### 6.3 测试分类
- **单元测试**（tests/unit/）：测试单个函数/类，Mock所有外部依赖
- **集成测试**（tests/integration/）：测试模块间交互，使用真实依赖（或Docker容器）

### 6.4 Mock 规范
- 优先使用 `AsyncMock` 模拟异步函数
- 必须模拟所有网络请求（禁止在单元测试中发真实请求）
- 使用 `patch` 装饰器或上下文管理器

**示例**：
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_fetch_data():
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json.return_value = {"key": "value"}
        
        result = await fetch_data("http://test.com")
        assert result == {"key": "value"}
        mock_get.assert_called_once()
```

## ⚠️ 常见违规行为

1. **混用同步/异步**：
   - ❌ 在 async 函数中调用 `requests.get()`
   - ❌ 在 async 函数中使用 `time.sleep()`

2. **缺少类型注解**：
   - ❌ `def process(data):`
   - ✅ `def process(data: Dict[str, Any]) -> bool:`

3. **捕获所有异常**：
   - ❌ `except Exception:` 且不记录堆栈
   - ✅ `except SpecificError:` 或 `logger.error(..., exc_info=True)`

4. **使用 print**：
   - ❌ `print(f"Error: {e}")`
   - ✅ `logger.error(f"Error: {e}")`

5. **缺少 Docstring**：
   - ❌ 公共函数没有文档字符串
   - ✅ 添加 Google 风格的 Docstring

6. **测试中发真实请求**：
   - ❌ 单元测试依赖外部网络
   - ✅ 使用 Mock 模拟所有外部交互
