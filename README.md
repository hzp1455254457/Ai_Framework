# AI框架

一个轻量级、模块化、易扩展的 Python 异步优先 AI 框架，提供统一的大语言模型（LLM）接口和 Agent 引擎能力。

## ✨ 特性

- 🚀 **异步优先**：全面采用 Python async/await，高性能 IO 处理
- 🔌 **适配器模式**：统一接口支持多种 LLM 提供商（OpenAI、DeepSeek、通义千问等）
- 🤖 **Agent 引擎**：内置任务规划、工具调用、记忆管理等能力
- 📦 **模块化设计**：核心层、基础设施层、接口层清晰分离
- ⚙️ **配置驱动**：多环境配置支持，灵活的环境变量管理
- 📚 **完整文档**：API 参考文档、快速开始指南、架构设计文档

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd Ai_Framework

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 配置

1. 复制配置文件：
```bash
cp config/default.yaml config/dev.yaml
```

2. 在 `config/dev.yaml` 中配置 API 密钥：
```yaml
llm:
  adapters:
    qwen-adapter:
      api_key: "你的API密钥"
```

或使用环境变量：
```bash
export QWEN_API_KEY="你的API密钥"
export OPENAI_API_KEY="你的OpenAI API密钥"
```

### 第一个示例

```python
import asyncio
from infrastructure.config import ConfigManager
from core.llm.service import LLMService

async def main():
    # 加载配置
    config_manager = ConfigManager.load(env="dev")
    config = config_manager.get_all()
    
    # 创建LLM服务
    service = LLMService(config)
    await service.initialize()
    
    # 发送消息
    messages = [{"role": "user", "content": "你好"}]
    response = await service.chat(messages, model="qwen-turbo")
    
    print(response.content)
    await service.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

运行项目提供的示例：
```bash
python simple_chat_example.py
```

## 📖 文档

- [快速开始指南](docs/guides/getting-started.md) - 详细的安装和使用教程
- [API 参考文档](docs/api/api-reference.md) - 完整的 API 接口说明
- [架构方案文档](AI框架架构方案文档.md) - 项目架构和技术选型
- [项目计划](docs/PROJECT_PLAN.md) - 开发计划和进度

## 🌐 API 服务

启动 FastAPI 服务：

```bash
uvicorn api.fastapi_app:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 项目结构

```
Ai_Framework/
├── core/              # 核心业务模块
│   ├── llm/          # LLM 服务
│   ├── agent/        # Agent 引擎
│   └── base/         # 基础类和接口
├── infrastructure/    # 基础设施模块
│   ├── config/       # 配置管理
│   ├── cache/        # 缓存管理
│   ├── log/          # 日志管理
│   └── storage/      # 存储管理
├── api/              # FastAPI 接口层
├── cli/              # 命令行工具
├── tests/             # 测试代码
└── docs/              # 项目文档
```

## 🛠️ 技术栈

- **Python**: 3.10+（推荐 3.11+）
- **Web 框架**: FastAPI
- **HTTP 客户端**: httpx（异步）
- **数据建模**: Pydantic
- **测试**: pytest + pytest-asyncio

## 📝 开发规范

项目遵循统一的开发规范，详见：
- [开发规则文档](.cursor/rules/AI_Framework_Rules.mdc) - 代码规范、文档规范、工作流程

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[待定]

---

**注意**：本项目仍在积极开发中，API 可能会发生变化。建议查看 [API 变更日志](docs/api/api-changelog.md) 了解最新变更。
