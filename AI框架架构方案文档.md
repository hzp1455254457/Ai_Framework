# 个人AI框架架构方案文档

## 📋 项目概述

### 目标
构建一个轻量级、模块化、易扩展的个人AI应用框架，支持多种AI能力（LLM对话、图像处理、语音识别等），便于个人开发者快速集成和使用。

### 核心定位
- **轻量级**：适合个人开发者，不依赖重型基础设施
- **模块化**：各功能模块独立，按需使用
- **易扩展**：插件化架构，方便添加新的AI能力
- **易用性**：简洁的API设计，降低使用门槛

---

## 🏗️ 架构设计

### 1. 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                     应用层 (Application Layer)            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Web UI   │  │ CLI      │  │ API      │  │ Plugin   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                 抽象接口层 (Abstract Interface Layer)    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ ILLM     │  │ IAgent   │  │ ITool    │  │ IMemory  │ │
│  │ Provider │  │ Engine   │  │ Manager  │  │          │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│  ┌──────────┐  ┌──────────┐                              │
│  │ IWorkflow│  │ IChain   │                              │
│  └──────────┘  └──────────┘                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │ ComponentManager (组件管理器)                       │ │
│  │ - 运行时切换实现                                    │ │
│  │ - 依赖注入和组件组装                                │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   工厂层 (Factory Layer)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ LLM      │  │ Agent    │  │ Tool     │  │ Memory   │ │
│  │ Factory  │  │ Factory  │  │ Factory  │  │ Factory  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   实现层 (Implementation Layer)            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Native实现   │  │ LangChain    │  │ LangGraph    │   │
│  │ (自研)       │  │ 实现         │  │ 实现         │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    核心服务层 (Core Service Layer)        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ LLM      │  │ Vision   │  │ Audio    │  │ Agent    │ │
│  │ Service  │  │ Service  │  │ Service  │  │ Engine   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    适配器层 (Adapter Layer)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ OpenAI   │  │ Claude   │  │ Local    │  │ Custom   │ │
│  │ Adapter  │  │ Adapter  │  │ Model    │  │ Adapter  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    基础设施层 (Infrastructure Layer)      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Config   │  │ Cache    │  │ Log      │  │ Storage  │ │
│  │ Manager  │  │ Manager  │  │ Manager  │  │ Manager  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 2. 核心模块设计

#### 2.1 LLM服务模块 (LLM Service)
**功能**：
- 统一的多模型LLM接口
- 支持流式输出
- 上下文管理（对话历史）
- Token计算和成本估算
- 重试和错误处理

**支持的提供商**：
- OpenAI (GPT-3.5, GPT-4, etc.)
- Anthropic (Claude)
- 本地模型 (Ollama, LM Studio)
- 开源模型 (Llama, Mistral等)

#### 2.2 视觉服务模块 (Vision Service)
**功能**：
- 图像生成 (DALL-E, Stable Diffusion)
- 图像分析 (OCR, 物体识别)
- 图像编辑和处理

#### 2.3 音频服务模块 (Audio Service)
**功能**：
- 语音转文字 (STT)
- 文字转语音 (TTS)
- 音频处理和转换

#### 2.4 Agent引擎 (Agent Engine)
**功能**：
- 工具调用 (Function Calling)
- 工作流编排
- 记忆管理
- 任务规划

**架构特性**：
- **抽象接口架构**：通过 `IAgentEngine` 接口支持多种实现（Native、LangChain、LangGraph）
- **工厂模式**：使用 `AgentFactory` 根据配置创建不同实现
- **灵活组装**：支持混合使用不同实现（如LangChain Agent + 自研工具）
- **运行时切换**：支持运行时动态切换实现，无需重启
- **LangChain集成**：完整支持LangChain生态，包括工具转换、记忆转换、多种Agent类型

#### 2.5 配置管理 (Config Manager)
**功能**：
- 多环境配置支持 (dev/prod)
- 敏感信息加密存储
- 配置热重载

#### 2.6 缓存管理 (Cache Manager)
**功能**：
- 请求结果缓存
- 向量化结果缓存
- 支持多种后端 (内存/Redis/文件)

#### 2.7 日志管理 (Log Manager)
**功能**：
- 结构化日志
- 多级别日志
- 日志轮转和归档

#### 2.8 存储管理 (Storage Manager)
**功能**：
- 对话历史存储
- 文件存储管理
- 向量数据库集成

---

## 🔧 抽象接口架构（v2.0 核心特性）

### 设计理念

框架采用**抽象接口架构**，实现了接口与实现的完全解耦，支持多种实现（Native、LangChain、LangGraph）的灵活切换和组装。

### 核心组件

#### 1. 抽象接口层

定义统一的组件接口，所有实现都必须遵循这些接口：

- **`ILLMProvider`**: LLM提供者接口，定义统一的LLM调用规范
- **`IAgentEngine`**: Agent引擎接口，定义任务执行规范
- **`IToolManager`**: 工具管理器接口，定义工具注册和执行规范
- **`IMemory`**: 记忆管理接口，定义消息管理规范
- **`IWorkflow`**: 工作流接口，定义工作流编排规范
- **`IChain`**: 链式调用接口，定义链式处理规范

#### 2. 工厂层

使用工厂模式封装对象创建逻辑：

- **`LLMFactory`**: 根据配置创建LLM提供者（Native/LangChain）
- **`AgentFactory`**: 根据配置创建Agent引擎（Native/LangChain/LangGraph）
- **`ToolFactory`**: 根据配置创建工具管理器（Native/LangChain）
- **`MemoryFactory`**: 根据配置创建记忆管理器（Native/LangChain）
- **`WorkflowFactory`**: 根据配置创建工作流（Native/LangGraph）

#### 3. 实现层

提供多种实现选择：

- **Native实现**：自研实现（默认），轻量级、高性能
- **LangChain实现**：完整集成LangChain生态，支持丰富的工具和Agent类型
- **LangGraph实现**：支持复杂工作流和状态管理

#### 4. 组合管理器

**`ComponentManager`** 统一管理所有组件：

- 支持运行时切换实现
- 支持依赖注入和组件组装
- 支持混合使用不同实现（如LangChain Agent + 自研工具）

### 使用方式

#### 配置驱动切换

通过配置文件选择实现类型：

```yaml
llm:
  implementation: "langchain"  # native/langchain

agent:
  implementation: "langchain"  # native/langchain/langgraph
  agent_type: "openai-functions"  # LangChain Agent类型

tools:
  implementation: "langchain"  # native/langchain

memory:
  implementation: "langchain"  # native/langchain
```

#### 代码示例

```python
from core.factories import AgentFactory
from infrastructure.config import ConfigManager

# 加载配置
config = ConfigManager.load().get_all()

# 通过工厂创建Agent引擎（自动根据配置选择实现）
agent = AgentFactory.create_from_config(config)

# 执行任务（无论使用哪种实现，接口都相同）
result = await agent.run_task("查询北京天气")
```

### LangChain集成特性

#### 完整的LangChain适配器实现

- **LLM适配器**：将框架的LLM服务包装为LangChain LLM
- **工具适配器**：自动将自研工具转换为LangChain工具
- **记忆适配器**：自动将自研记忆转换为LangChain记忆
- **Agent适配器**：支持多种LangChain Agent类型（OpenAI Functions、ReAct等）

#### 工具和记忆转换

- **工具转换**：自研Tool自动转换为LangChain Tool，支持参数验证和异步执行
- **记忆转换**：自研Memory自动转换为LangChain Memory，支持消息格式转换

#### 支持的LangChain Agent类型

- `openai-functions`: OpenAI Function Calling Agent
- `openai-multi-functions`: OpenAI Multi-Function Agent
- `react`: ReAct Agent
- `self-ask-with-search`: Self-Ask-With-Search Agent

### 优势

1. **完全解耦**：接口与实现完全分离，可以独立替换任何组件
2. **灵活组装**：可以随意组合不同实现，支持混合使用
3. **易于扩展**：新增实现只需实现接口，无需修改现有代码
4. **运行时切换**：支持运行时动态切换实现，无需重启
5. **向后兼容**：现有代码通过适配器模式兼容，无需修改

---

## 📁 目录结构

```
Ai_Framework/
├── README.md                 # 项目说明
├── requirements.txt          # Python依赖
├── setup.py                  # 安装配置
├── config/
│   ├── __init__.py
│   ├── settings.py           # 配置管理
│   ├── default.yaml          # 默认配置
│   └── dev.yaml              # 开发环境配置
├── core/                     # 核心模块
│   ├── __init__.py
│   ├── base/                 # 基础类
│   │   ├── __init__.py
│   │   ├── service.py        # 服务基类
│   │   ├── adapter.py        # 适配器基类
│   │   └── plugin.py         # 插件基类
│   ├── interfaces/           # 抽象接口层（v2.0新增）
│   │   ├── __init__.py
│   │   ├── llm.py           # ILLMProvider接口
│   │   ├── agent.py         # IAgentEngine接口
│   │   ├── tools.py         # IToolManager接口
│   │   ├── memory.py        # IMemory接口
│   │   ├── workflow.py      # IWorkflow接口
│   │   └── chain.py         # IChain接口
│   ├── factories/            # 工厂层（v2.0新增）
│   │   ├── __init__.py
│   │   ├── llm_factory.py   # LLM工厂
│   │   ├── agent_factory.py # Agent工厂
│   │   ├── tool_factory.py  # 工具工厂
│   │   ├── memory_factory.py # 记忆工厂
│   │   └── workflow_factory.py # 工作流工厂
│   ├── implementations/      # 实现层（v2.0新增）
│   │   ├── native/          # Native实现（自研）
│   │   │   ├── __init__.py
│   │   │   ├── native_llm.py
│   │   │   ├── native_agent.py
│   │   │   ├── native_tools.py
│   │   │   └── native_memory.py
│   │   ├── langchain/       # LangChain实现
│   │   │   ├── __init__.py
│   │   │   ├── langchain_llm.py
│   │   │   ├── langchain_agent.py
│   │   │   ├── langchain_tools.py
│   │   │   └── langchain_memory.py
│   │   └── langgraph/       # LangGraph实现
│   │       ├── __init__.py
│   │       ├── langgraph_agent.py
│   │       └── langgraph_workflow.py
│   ├── composition/          # 组合管理器（v2.0新增）
│   │   ├── __init__.py
│   │   └── component_manager.py
│   ├── llm/                  # LLM服务
│   │   ├── __init__.py
│   │   ├── service.py        # LLM服务主类
│   │   ├── context.py        # 上下文管理
│   │   └── adapters/         # 各种适配器
│   │       ├── __init__.py
│   │       ├── openai_adapter.py
│   │       ├── claude_adapter.py
│   │       ├── ollama_adapter.py
│   │       └── local_adapter.py
│   ├── vision/               # 视觉服务
│   │   ├── __init__.py
│   │   ├── service.py
│   │   └── adapters/
│   ├── audio/                # 音频服务
│   │   ├── __init__.py
│   │   ├── service.py
│   │   └── adapters/
│   └── agent/                # Agent引擎
│       ├── __init__.py
│       ├── engine.py
│       ├── tools.py          # 工具定义
│       └── memory.py         # 记忆管理
├── infrastructure/           # 基础设施
│   ├── __init__.py
│   ├── config/               # 配置管理
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── cache/                # 缓存管理
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── log/                  # 日志管理
│   │   ├── __init__.py
│   │   └── manager.py
│   └── storage/              # 存储管理
│       ├── __init__.py
│       └── manager.py
├── api/                      # API接口
│   ├── __init__.py
│   ├── fastapi_app.py        # FastAPI应用
│   └── routes/
│       ├── __init__.py
│       ├── llm.py
│       ├── vision.py
│       └── audio.py
├── cli/                      # CLI工具
│   ├── __init__.py
│   └── main.py
├── web/                      # Web UI
│   ├── __init__.py
│   ├── app.py                # 前端应用
│   └── static/               # 静态资源
├── plugins/                  # 插件目录
│   └── README.md
├── tests/                    # 测试
│   ├── __init__.py
│   ├── test_llm.py
│   ├── test_vision.py
│   └── test_agent.py
├── examples/                 # 示例代码
│   ├── basic_chat.py
│   ├── agent_example.py
│   └── multi_modal.py
└── docs/                     # 文档
    ├── architecture.md
    ├── api_reference.md
    └── tutorials.md
```

---

## 🛠️ 技术栈选择

### 核心框架
- **Python 3.10+**：现代Python特性支持
- **asyncio**：异步IO支持，提升并发性能
- **pydantic**：数据验证和配置管理
- **typing**：类型提示，提升代码质量

### Web框架
- **FastAPI**：现代、快速的API框架
  - 自动API文档
  - 异步支持
  - 类型验证

### 前端（可选）
- **Streamlit**：快速构建Web UI（推荐新手）
- **Gradio**：简单易用的界面框架
- **React + Vite**：如果需要更复杂的UI（可选）

### 数据库
- **SQLite**：默认轻量级数据库
- **PostgreSQL**：生产环境可选
- **向量数据库**：Chroma/SQlite-VSS（用于记忆存储）

### 其他依赖
- **httpx**：异步HTTP客户端
- **aiofiles**：异步文件操作
- **python-dotenv**：环境变量管理
- **loguru**：日志管理
- **tenacity**：重试机制

---

## 🔌 插件系统设计

### 插件接口规范
```python
# 插件基类接口（伪代码）
class Plugin:
    name: str
    version: str
    description: str
    
    async def initialize(self, config: dict) -> None:
        """插件初始化"""
        pass
    
    async def execute(self, context: dict) -> dict:
        """执行插件逻辑"""
        pass
    
    async def cleanup(self) -> None:
        """清理资源"""
        pass
```

### 插件类型
1. **工具插件**：扩展Agent的工具能力
2. **适配器插件**：添加新的模型提供商支持
3. **存储插件**：自定义存储后端
4. **中间件插件**：请求/响应拦截和处理

---

## 📝 使用示例（伪代码）

### 示例1：基础对话
```python
from ai_framework import LLMService, ConfigManager

# 初始化
config = ConfigManager.load()
llm = LLMService(config)

# 简单对话
response = await llm.chat(
    messages=[{"role": "user", "content": "你好"}],
    model="gpt-3.5-turbo"
)
print(response.content)
```

### 示例2：带上下文的对话
```python
from ai_framework import LLMService, ConversationContext

llm = LLMService(config)
ctx = ConversationContext()

# 添加消息
ctx.add_user_message("帮我写一个Python函数计算斐波那契数列")
response1 = await llm.chat_with_context(ctx)

ctx.add_assistant_message(response1.content)
ctx.add_user_message("优化一下性能")
response2 = await llm.chat_with_context(ctx)
```

### 示例3：Agent工作流
```python
from ai_framework import AgentEngine

agent = AgentEngine(config)

# 定义工具
@agent.tool("get_weather")
async def get_weather(city: str) -> str:
    # 获取天气的逻辑
    return f"{city}的天气是晴天"

# 执行任务
result = await agent.run(
    task="查询北京天气，然后告诉我适合穿什么衣服",
    tools=[get_weather]
)
```

### 示例4：多模态处理
```python
from ai_framework import LLMService, VisionService

llm = LLMService(config)
vision = VisionService(config)

# 图像分析
image_result = await vision.analyze("path/to/image.jpg")

# 结合LLM解释结果
explanation = await llm.chat(
    messages=[{
        "role": "user",
        "content": f"解释这张图片：{image_result.description}"
    }]
)
```

---

## 🔄 工作流程

### 开发阶段
1. **Phase 1：核心基础设施**
   - 配置管理
   - 日志系统
   - 基础服务框架

2. **Phase 2：LLM服务**
   - 适配器接口
   - OpenAI适配器实现
   - 本地模型适配器

3. **Phase 3：扩展服务**
   - Vision服务
   - Audio服务
   - Agent引擎

4. **Phase 4：接口层**
   - CLI工具
   - API服务
   - Web UI

5. **Phase 5：插件系统**
   - 插件框架
   - 示例插件
   - 插件管理

### 迭代原则
- **MVP优先**：先实现核心功能，再扩展
- **测试驱动**：每个模块都有对应测试
- **文档同步**：代码与文档同步更新

---

## 🔒 安全性考虑

### API密钥管理
- 使用环境变量存储密钥
- 支持密钥加密存储
- 密钥轮换机制

### 数据隐私
- 本地处理优先
- 敏感数据脱敏
- 日志中不记录敏感信息

### 访问控制
- API认证（可选）
- 请求限流
- IP白名单（可选）

---

## 📊 性能优化

### 缓存策略
- 常用请求结果缓存
- 向量化结果缓存
- 配置缓存

### 并发处理
- 异步IO充分利用
- 连接池管理
- 请求批处理

### 资源管理
- 内存使用监控
- 连接数限制
- 自动清理机制

---

## 🧪 测试策略

### 单元测试
- 每个模块独立测试
- Mock外部依赖
- 覆盖率目标：80%+

### 集成测试
- 模块间交互测试
- 端到端流程测试

### 性能测试
- 响应时间测试
- 并发压力测试
- 内存泄漏检测

---

## 📦 部署方案

### 开发环境
- 本地运行
- 使用SQLite
- 简单配置

### 生产环境（可选）
- Docker容器化
- 环境变量配置
- 日志收集
- 监控告警

---

## 🚀 后续扩展方向

1. **多Agent协作**：支持多个Agent协同工作
2. **知识库集成**：RAG能力增强
3. **工作流引擎**：可视化工作流编排
4. **模型微调**：支持模型微调流程
5. **边缘部署**：支持移动端/边缘设备
6. **成本优化**：智能路由和成本控制
7. **A/B测试**：模型效果对比测试
