# 快速参考指南

## 📋 文档说明

本文档提供AI框架项目的快速参考，包括常见任务的快速步骤、常用命令和常见问题解答。

**使用场景**：
- 快速查找常用操作
- 新手上手参考
- 日常开发速查

---

## 🚀 快速开始

### 安装和设置

```bash
# 1. 克隆项目（如果有）
git clone <repository-url>
cd Ai_Framework

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入API密钥等配置

# 5. 运行示例
python examples/basic/basic_chat.py
```

---

## 📝 常见任务快速参考

### 1. 开发新功能模块

**快速步骤**：
1. 创建功能设计文档：`docs/design/功能名.md`
2. 创建模块目录：`core/功能名/`
3. 实现核心代码：`core/功能名/service.py`
4. 编写测试：`tests/core/功能名/test_service.py`
5. 更新API路由（如需要）：`api/routes/功能名.py`
6. 更新文档

**详细流程**：参考 `.cursor/rules/ProjectRules.mdc` → "项目开发工作流"

---

### 2. 添加新的LLM适配器

**快速步骤**：
1. 创建适配器文件：`core/llm/adapters/提供商_adapter.py`
2. 继承 `BaseAdapter` 类
3. 实现 `call()` 和 `stream_call()` 方法
4. 在 `LLMService` 中注册新适配器
5. 编写测试

**示例代码位置**：`core/llm/adapters/openai_adapter.py`

---

### 3. 添加新的API端点

**快速步骤**：
1. 定义请求/响应模型：`api/models/request.py`
2. 实现路由处理函数：`api/routes/模块名.py`
3. 调用对应的服务模块
4. 注册路由到FastAPI应用
5. 更新API文档

**示例代码位置**：`api/routes/llm.py`

---

### 4. 编写测试

**快速步骤**：
1. 创建测试文件：`tests/unit/core/模块名/test_service.py`
2. 编写测试用例（使用pytest）
3. Mock外部依赖
4. 运行测试：`pytest tests/unit/`
5. 检查覆盖率：`pytest --cov=core tests/`

**测试规范**：参考 `.cursor/rules/CodeStandards.mdc` → "测试规范"

---

### 5. 更新文档

**快速步骤**：
1. 确定文档类型（设计文档/API文档/模块文档）
2. 找到对应的权威文档
3. 更新文档内容
4. 检查文档一致性
5. 更新CHANGELOG.md

**文档规范**：参考 `.cursor/rules/Documentation.mdc`

---

## 🔧 常用命令

### 开发环境

```bash
# 运行开发服务器
python scripts/dev_server.py

# 运行API服务
uvicorn api.fastapi_app:app --reload

# 运行CLI
python -m cli.main [command]

# 运行Web UI
streamlit run web/app.py
```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定模块的测试
pytest tests/unit/core/llm/

# 运行测试并查看覆盖率
pytest --cov=core --cov-report=html

# 运行异步测试
pytest --asyncio-mode=auto
```

### 代码质量

```bash
# 格式化代码
black .

# 类型检查
mypy core/

# 代码检查
ruff check .

# 运行所有检查
black . && mypy core/ && ruff check .
```

### 依赖管理

```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 更新依赖
pip install --upgrade -r requirements.txt

# 导出当前依赖
pip freeze > requirements.txt
```

---

## 📚 常用代码片段

### 创建LLM服务实例

```python
from core.llm.service import LLMService
from infrastructure.config.manager import ConfigManager

# 加载配置
config = ConfigManager.load()

# 创建服务实例
llm_service = LLMService(config)

# 使用服务
response = await llm_service.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-3.5-turbo"
)
```

### 创建适配器

```python
from core.base.adapter import BaseAdapter
from typing import List, Dict

class MyAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "my-adapter"
    
    async def call(self, messages: List[Dict]) -> Dict:
        # 实现调用逻辑
        pass
    
    async def stream_call(self, messages: List[Dict]):
        # 实现流式调用
        async for chunk in stream:
            yield chunk
```

### 定义API路由

```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/llm", tags=["LLM"])

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str = "gpt-3.5-turbo"

@router.post("/chat")
async def chat(request: ChatRequest):
    response = await llm_service.chat(
        messages=request.messages,
        model=request.model
    )
    return response
```

---

## ❓ 常见问题快速解答

### Q1: 如何切换LLM提供商？

**A**: 修改配置文件或环境变量中的默认提供商设置，或在调用时指定model参数。

```python
# 方式1：通过配置
config["llm"]["default_provider"] = "claude"

# 方式2：调用时指定
response = await llm_service.chat(messages, model="claude-3-sonnet")
```

---

### Q2: 如何添加自定义工具到Agent？

**A**: 实现工具函数，使用装饰器注册。

```python
from core.agent.engine import AgentEngine

agent = AgentEngine(config)

@agent.tool("my_tool")
async def my_tool(param: str) -> str:
    """工具描述"""
    return f"处理结果: {param}"

result = await agent.run(task="使用my_tool处理任务")
```

---

### Q3: 如何配置缓存？

**A**: 在配置文件中设置缓存后端和策略。

```yaml
# config/default.yaml
cache:
  backend: "memory"  # 或 "redis", "file"
  ttl: 3600  # 缓存过期时间（秒）
  max_size: 1000  # 最大缓存条目数
```

---

### Q4: 如何启用日志？

**A**: 配置日志级别和输出方式。

```python
from infrastructure.log.manager import LogManager

log_manager = LogManager(config)
logger = log_manager.get_logger("module_name")

logger.info("信息日志")
logger.error("错误日志", exc_info=True)
```

---

### Q5: 如何处理API错误？

**A**: 使用统一的异常处理机制。

```python
from core.exceptions import LLMError, ValidationError

try:
    response = await llm_service.chat(messages)
except ValidationError as e:
    # 处理验证错误
    logger.warning(f"参数错误: {e}")
except LLMError as e:
    # 处理LLM错误
    logger.error(f"LLM调用失败: {e}")
```

---

## 🔍 快速查找信息

### 查找项目信息

| 信息类型 | 查找位置 |
|---------|---------|
| 项目概述 | `README.md` 或 `AI框架架构方案文档.md` |
| 架构设计 | `AI框架架构方案文档.md` → "架构设计" |
| 技术栈版本 | `docs/architecture/tech-stack-versions.md` |
| 目录结构 | `.cursor/rules/ProjectRules.mdc` |
| 代码规范 | `.cursor/rules/CodeStandards.mdc` |
| 文档规范 | `.cursor/rules/Documentation.mdc` |
| 依赖关系 | `docs/architecture/dependencies.md` |
| 架构决策 | `docs/architecture/decisions/` |

### 查找API信息

| 信息类型 | 查找位置 |
|---------|---------|
| API参考 | `docs/api/api-reference.md` |
| OpenAPI规范 | `docs/api/openapi.yaml` |
| API变更日志 | `docs/api/api-changelog.md` |
| API路由代码 | `api/routes/` |

### 查找模块信息

| 信息类型 | 查找位置 |
|---------|---------|
| 模块设计 | `docs/design/模块名.md` |
| 模块代码 | `core/模块名/` |
| 模块测试 | `tests/unit/core/模块名/` |
| 模块文档 | `core/模块名/README.md` |

---

## 📖 学习路径

### 新手学习路径

1. **第1天：了解项目**
   - 阅读 `README.md`
   - 查看架构方案文档
   - 运行示例代码

2. **第2天：理解架构**
   - 学习分层架构设计
   - 理解模块职责
   - 查看依赖关系图

3. **第3天：开发实践**
   - 阅读代码规范
   - 编写简单功能
   - 编写测试

4. **第4天：深入理解**
   - 理解适配器模式
   - 学习异步编程
   - 查看架构决策记录

---

## 📚 相关文档

- [架构方案文档](../../AI框架架构方案文档.md)
- [快速开始指南](getting-started.md)
- [开发环境设置](development/setup.md)
- [故障排查指南](../troubleshooting/common-issues.md)

---

## 🔄 文档更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-01-21 | v1.0 | 初始版本，创建快速参考指南 | - |

---

## ⚠️ 重要提示

1. **及时更新**：常用命令和代码片段变更时及时更新本文档
2. **保持简洁**：快速参考应该简洁明了，详细说明查看相关文档
3. **验证准确性**：所有命令和代码片段应该经过验证
4. **分类清晰**：按任务类型组织，便于快速查找
