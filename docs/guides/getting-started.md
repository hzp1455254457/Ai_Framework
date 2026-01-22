# 快速开始指南

## 📋 文档说明

本文档帮助新用户快速上手AI框架，从安装到运行第一个示例，只需几分钟。

**预计时间**: 10-15分钟

---

## 📦 第一步：环境准备

### 1.1 检查Python版本

AI框架需要 **Python 3.10+**（推荐 3.11+）。

```bash
# 检查Python版本
python --version
# 或
python3 --version
```

如果版本低于3.10，请先升级Python。

### 1.2 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

---

## 🔧 第二步：安装框架

### 2.1 克隆项目（如果从Git仓库）

```bash
git clone <repository-url>
cd Ai_Framework
```

### 2.2 安装依赖

```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖（可选，用于开发和测试）
pip install -r requirements-dev.txt
```

### 2.3 验证安装

```bash
# 检查关键模块是否可以导入
python -c "from core.llm.service import LLMService; print('安装成功！')"
```

---

## ⚙️ 第三步：配置API密钥

### 3.1 获取API密钥

根据你要使用的LLM提供商，获取对应的API密钥：

- **通义千问**: 访问 [阿里云DashScope](https://dashscope.console.aliyun.com/) 获取API密钥
- **OpenAI**: 访问 [OpenAI Platform](https://platform.openai.com/) 获取API密钥
- **DeepSeek**: 访问 [DeepSeek Platform](https://platform.deepseek.com/) 获取API密钥
- **Claude**: 访问 [Anthropic Console](https://console.anthropic.com/) 获取API密钥

### 3.2 配置API密钥

**方式1：修改配置文件**（推荐开发环境）

编辑 `config/default.yaml` 或 `config/dev.yaml`：

```yaml
llm:
  adapters:
    qwen-adapter:
      api_key: "你的API密钥"
    openai-adapter:
      api_key: "你的OpenAI API密钥"
```

**方式2：使用环境变量**（推荐生产环境）

```bash
# Windows PowerShell
$env:QWEN_API_KEY="你的API密钥"
$env:OPENAI_API_KEY="你的OpenAI API密钥"

# Linux/Mac
export QWEN_API_KEY="你的API密钥"
export OPENAI_API_KEY="你的OpenAI API密钥"
```

---

## 🚀 第四步：运行第一个示例

### 4.1 基础聊天示例

创建文件 `my_first_chat.py`：

```python
import asyncio
from infrastructure.config import ConfigManager
from core.llm.service import LLMService

async def main():
    # 1. 加载配置
    config_manager = ConfigManager.load(env="dev")
    config = config_manager.get_all()
    
    # 2. 创建LLM服务
    service = LLMService(config)
    await service.initialize()
    
    # 3. 发送消息
    messages = [{"role": "user", "content": "你好，请介绍一下你自己"}]
    response = await service.chat(
        messages=messages,
        model="qwen-turbo"  # 或你配置的其他模型
    )
    
    # 4. 显示结果
    print(f"AI回复: {response.content}")
    print(f"Token使用: {response.total_tokens}")
    
    # 5. 清理资源
    await service.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

运行示例：

```bash
python my_first_chat.py
```

**预期输出**:
```
AI回复: 你好！我是AI助手...
Token使用: 30
```

### 4.2 使用项目示例

项目根目录提供了 `simple_chat_example.py` 示例：

```bash
python simple_chat_example.py
```

---

## 🌐 第五步：启动API服务（可选）

如果你想通过HTTP API使用框架：

### 5.1 启动FastAPI服务

```bash
# 方式1：使用uvicorn直接启动
uvicorn api.fastapi_app:app --reload --host 0.0.0.0 --port 8000

# 方式2：使用Python模块方式
python -m uvicorn api.fastapi_app:app --reload
```

### 5.2 访问API文档

启动服务后，访问以下地址：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 5.3 测试API

```bash
# 测试健康检查
curl http://localhost:8000/api/v1/health/

# 测试聊天接口
curl -X POST "http://localhost:8000/api/v1/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "model": "qwen-turbo"
  }'
```

---

## 💡 常见使用场景

### 场景1：简单问答

```python
import asyncio
from infrastructure.config import ConfigManager
from core.llm.service import LLMService

async def simple_qa():
    config = ConfigManager.load(env="dev").get_all()
    service = LLMService(config)
    await service.initialize()
    
    response = await service.chat(
        messages=[{"role": "user", "content": "Python中如何读取文件？"}],
        model="qwen-turbo"
    )
    
    print(response.content)
    await service.cleanup()

asyncio.run(simple_qa())
```

### 场景2：多轮对话

```python
import asyncio
from infrastructure.config import ConfigManager
from core.llm.service import LLMService
from core.llm.context import ConversationContext

async def multi_turn_chat():
    config = ConfigManager.load(env="dev").get_all()
    service = LLMService(config)
    await service.initialize()
    
    # 创建对话上下文
    context = ConversationContext()
    
    # 第一轮
    context.add_user_message("我想学习Python")
    response1 = await service.chat_with_context(context)
    print(f"AI: {response1.content}")
    
    # 第二轮
    context.add_user_message("推荐一些学习资源")
    response2 = await service.chat_with_context(context)
    print(f"AI: {response2.content}")
    
    await service.cleanup()

asyncio.run(multi_turn_chat())
```

### 场景3：Agent任务执行

```python
import asyncio
from infrastructure.config import ConfigManager
from core.agent.engine import AgentEngine

async def agent_task():
    config = ConfigManager.load(env="dev").get_all()
    engine = AgentEngine(config)
    await engine.initialize()
    
    # 执行Agent任务
    result = await engine.run_task(
        task="查询北京天气，然后告诉我适合穿什么衣服",
        model="gpt-3.5-turbo"
    )
    
    print(f"任务结果: {result['content']}")
    print(f"工具调用: {result.get('tool_calls', [])}")
    
    await engine.cleanup()

asyncio.run(agent_task())
```

### 场景4：流式输出

```python
import asyncio
from infrastructure.config import ConfigManager
from core.llm.service import LLMService

async def stream_chat():
    config = ConfigManager.load(env="dev").get_all()
    service = LLMService(config)
    await service.initialize()
    
    messages = [{"role": "user", "content": "写一首关于春天的诗"}]
    
    print("AI回复: ", end="", flush=True)
    async for chunk in service.stream_chat(
        messages=messages,
        model="qwen-turbo"
    ):
        print(chunk.content, end="", flush=True)
    print()  # 换行
    
    await service.cleanup()

asyncio.run(stream_chat())
```

---

## 🔍 故障排查

### 问题1：ModuleNotFoundError

**症状**: 导入模块时提示找不到模块

**解决方案**:
```bash
# 确保在项目根目录运行
cd Ai_Framework

# 确保虚拟环境已激活
# 重新安装依赖
pip install -r requirements.txt
```

### 问题2：API密钥错误

**症状**: 调用LLM时提示认证失败

**解决方案**:
1. 检查配置文件中的API密钥是否正确
2. 检查环境变量是否设置
3. 验证API密钥是否有效（访问对应提供商的平台）

### 问题3：模型不存在

**症状**: 提示模型不存在或未找到适配器

**解决方案**:
1. 检查模型名称是否正确（区分大小写）
2. 运行 `GET /api/v1/llm/models` 查看支持的模型列表
3. 检查适配器是否已正确注册

### 问题4：端口被占用

**症状**: 启动API服务时提示端口被占用

**解决方案**:
```bash
# 使用其他端口
uvicorn api.fastapi_app:app --reload --port 8001

# 或停止占用端口的进程
# Windows:
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

---

## 📚 下一步学习

完成快速开始后，建议按以下顺序深入学习：

### 1. 了解核心概念

- [架构方案文档](../../AI框架架构方案文档.md) - 理解整体架构
- [API参考文档](../api/api-reference.md) - 了解所有API接口

### 2. 学习高级功能

- **Agent引擎**: 学习如何使用Agent执行复杂任务
- **工具系统**: 学习如何定义和使用工具
- **记忆管理**: 学习如何使用短期和长期记忆
- **任务规划器**: 学习如何使用规划器分解复杂任务

### 3. 查看示例代码

- `simple_chat_example.py` - 基础聊天示例
- `examples/` 目录（如果存在）- 更多示例代码

### 4. 阅读设计文档

- `docs/design/` - 各模块的详细设计文档
- `docs/architecture/` - 架构决策和依赖关系

---

## 🎯 快速参考

### 常用命令

```bash
# 启动API服务
uvicorn api.fastapi_app:app --reload

# 运行测试
pytest

# 查看API文档
# 访问 http://localhost:8000/docs
```

### 配置文件位置

- `config/default.yaml` - 默认配置
- `config/dev.yaml` - 开发环境配置
- `config/prod.yaml` - 生产环境配置

### 重要文件

- `simple_chat_example.py` - 简单聊天示例
- `docs/api/api-reference.md` - API参考文档
- `docs/guides/quick-reference.md` - 快速参考指南

---

## 📚 相关文档

- [API参考文档](../api/api-reference.md) - 完整的API接口说明
- [快速参考指南](quick-reference.md) - 常用命令和代码片段
- [架构方案文档](../../AI框架架构方案文档.md) - 架构设计参考
- [项目计划文档](../../docs/PROJECT_PLAN.md) - 项目进度和功能清单

---

## 🔄 文档更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-01-22 | v1.0 | 初始版本，创建快速开始指南 | - |

---

**提示**: 如果在使用过程中遇到问题，请查看[故障排查](#故障排查)部分或查阅相关文档。
