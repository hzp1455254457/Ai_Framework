# Project Context

## Purpose
本项目是一个 **Python 异步优先的 AI 框架**，目标是提供统一、可扩展的基础能力，用于：
- **封装多家 LLM 提供商**（如 OpenAI、DeepSeek、通义千问等），通过适配器模式提供一致接口
- 提供 **LLM / 多模态核心能力层（core）**，上层通过 API、CLI、Web 等多种方式调用
- 提供通用的 **基础设施能力**（配置、缓存、日志、存储等），减少业务项目的样板代码
- 支撑后续的 **Agent 引擎、工具体系与工作流编排**

目标是形成一个 **高内聚、低耦合、文档驱动、易扩展** 的 AI 后端基础框架。

## Tech Stack
- **语言**: Python 3.10+（推荐 3.11）
- **Web 框架**: FastAPI（位于 `api/` 目录）
- **HTTP 客户端**: `httpx`（异步）
- **数据建模**: Pydantic（请求/响应模型、配置模型）
- **测试**: `pytest` + `pytest-asyncio`
- **依赖管理**: `requirements.txt` / `requirements-dev.txt`
- **代码结构**:
  - `core/`: 核心业务（LLM、Agent 等）
  - `infrastructure/`: 配置、缓存、日志、存储等基础设施
  - `api/`: FastAPI HTTP 接口
  - `cli/`: 命令行工具
  - `tests/`: 单测、集成测试、E2E 测试
- **规范与规则**: 通过 `.cursor/rules/*.mdc` 维护（代码规范、文档规范、项目计划规则等）
- **规格管理**: OpenSpec（`openspec/` 目录）

## Project Conventions

### Code Style
- **命名规范**（见 `.cursor/rules/CodeStandards.mdc`）：
  - 文件/目录：小写 + 下划线，例如 `llm_service.py`, `config_manager.py`
  - 类名：PascalCase，例如 `LLMService`, `ConfigManager`
  - 函数/方法/变量：snake_case，例如 `get_config`, `fetch_data`
  - 常量：全大写 + 下划线，例如 `DEFAULT_TIMEOUT`
- **类型注解**：
  - 所有对外公共函数、方法必须有完整类型注解
  - 常用 `List`, `Dict`, `Optional`, `Union`, `Callable`, `Awaitable` 等
- **异步优先**：
  - 所有 IO（HTTP、文件、DB 等）必须使用 async/await
  - 禁止在异步代码中使用阻塞调用（如 `time.sleep`, 同步 `requests`）
- **文件结构**：
  - 统一的导入顺序：标准库 → 第三方库 → 本地模块
  - 每个模块、类、公共函数必须有清晰的 docstring
- **单一职责 & DRY**：
  - 函数尽量 ≤50 行，类 ≤300 行，模块 ≤500 行
  - 公共逻辑抽取到工具函数或基类，避免复制粘贴

### Architecture Patterns
- **分层架构**：
  - **核心层 `core/`**：LLM 服务、Agent 引擎等核心能力
  - **基础设施层 `infrastructure/`**：配置、缓存、日志、存储等
  - **接口层 `api/`, `cli/`, `web/`**：向外暴露 HTTP、CLI、UI 等入口
  - 禁止上层被下层反向依赖，避免循环依赖
- **适配器模式**：
  - `core/llm/adapters/` 中通过 `BaseAdapter` 抽象不同 LLM 提供商（OpenAI、DeepSeek、Doubao、Qwen 等）
  - 新增模型时只需新增适配器类，而不修改核心服务接口
- **插件/扩展机制**：
  - `core/base/plugin.py` 定义插件接口，`PluginManager` 负责注册与执行
  - 通过插件扩展框架能力，保持核心代码简洁
- **配置驱动**：
  - 所有环境差异通过 `config/*.yaml` + `infrastructure/config` 管理
  - 禁止在代码中硬编码环境相关常量
- **依赖注入**：
  - 服务类通过构造函数注入依赖（适配器、配置管理器、日志等），便于测试和替换实现

### Testing Strategy
- 测试目录位于 `tests/`，结构尽量与源码目录镜像：
  - `tests/unit/`: 单元测试（core、infrastructure、api 等）
  - `tests/integration/`: 模块/接口集成测试
  - `tests/e2e/`: 端到端场景测试
- 使用 `pytest` + `pytest-asyncio` 对异步代码进行测试
- 对公共服务类（如 `LLMService`、Config/Cache/Log Manager）要求较高的测试覆盖率（目标 ≥80%）
- 使用 `unittest.mock.AsyncMock` 等方式对外部服务、网络请求进行 Mock
- 通过 `htmlcov/` 生成覆盖率报告，作为回归检查的参考

### Git Workflow
> 这里可以根据你团队习惯再细化；当前推荐的默认约定如下：

- 使用 **main** 或 **master** 作为稳定分支
- 功能开发在 `feature/<short-desc>` 分支上进行，完成后通过 Pull Request 合并
- 建议采用 **清晰的提交信息**，例如类似 Conventional Commits：
  - `feat: add llm streaming api`
  - `fix: handle openai timeout error`
  - `docs: update llm service design`
- 与 OpenSpec 集成：
  - 对需要规格变更的新功能/架构调整，先创建 `openspec/changes/<change-id>/`，再开始实现
  - Bugfix 和纯文档/格式变更可直接改代码，无需新 change proposal（遵循 OpenSpec 规则）

## Domain Context
- 本项目是一个 **LLM+多模态 AI 后端框架**，当前重点在：
  - **LLM 服务**：统一封装多种 LLM 模型提供商，实现聊天、补全等能力
  - **基础设施**：配置中心、缓存层、日志系统、存储抽象，为上层 AI 能力提供可靠支撑
  - **API/CLI 入口**：通过 FastAPI 路由和 CLI 命令对外暴露统一接口
- 后续规划包括：
  - **Agent 引擎**：任务规划、工具调用、记忆管理
  - 更多 **视觉/音频/多模态能力** 模块
- 文档规范、代码规范、项目计划均有专门规则文件（`.cursor/rules/*.mdc` + `docs/`），代码与文档必须同步更新。

## Important Constraints
- **异步 IO 强约束**：所有网络、文件等 IO 必须为异步实现，禁止在事件循环中引入阻塞操作
- **文档同步（硬性规则）**：
  - 任何功能开发、架构调整，必须同步更新相关设计文档（`docs/design/` 等）
  - **完成功能时必须更新 `docs/PROJECT_PLAN.md` 的状态与完成度**
- **模块职责清晰**：
  - `core/` 不得依赖 `api/`、`cli/` 等上层模块
  - `infrastructure/` 只提供通用能力，不依赖业务模块
- **可扩展性优先**：
  - 通过接口/基类/插件机制扩展，而不是修改核心逻辑
- **规范优先于个人风格**：
  - 命名、结构、注释、异常处理必须遵循规则文档

## External Dependencies
- **LLM 提供商 API**（通过适配器访问）：
  - OpenAI 系列模型
  - DeepSeek
  - 通义千问（Doubao/Qwen）
  - 后续可扩展其他本地或云端模型
- **配置来源**：
  - YAML 配置文件（`config/*.yaml`）
  - 环境变量（如 API Key、运行模式）
- **缓存与存储**：
  - 内存缓存（默认）
  - 可选 Redis / 文件 / 数据库（由 `infrastructure/storage` 及 `infrastructure/cache/backends` 负责）
- **Web 框架及生态**：
  - FastAPI + Uvicorn（部署时）
- 以上外部依赖都通过适配器或管理器层抽象，方便替换与 Mock。