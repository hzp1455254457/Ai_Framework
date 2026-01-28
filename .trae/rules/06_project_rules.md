---
alwaysApply: true
---
# 🏗️ 项目结构与规划规则

## 📋 文档说明
本文档详细规定了项目的目录结构、文件放置规则以及项目计划的维护规范。

## 1. 目录结构规范

### 1.1 项目树状图（标准结构）

```
f:\Ai_Framework\
├── .trae/                      # Trae IDE 配置
│   └── rules/                  # 项目规则文档（Split Rules）
│       ├── 01_core_workflow.md
│       ├── 02_openspec_protocol.md
│       ├── 03_promptx_system.md
│       ├── 04_coding_standards.md
│       ├── 05_documentation.md
│       ├── 06_project_rules.md
│       └── project.md          # 规则索引
├── core/                       # 核心业务逻辑
│   ├── llm/                    # LLM 服务与适配器
│   ├── vision/                 # 视觉处理模块
│   ├── utils/                  # 通用工具
│   └── ...
├── infrastructure/             # 基础设施
│   ├── config/                 # 配置管理
│   ├── cache/                  # 缓存管理
│   ├── logging/                # 日志管理
│   └── storage/                # 存储管理
├── api/                        # API 接口层
│   ├── routers/                # FastAPI 路由
│   ├── models/                 # 请求/响应模型
│   └── main.py                 # 应用入口
├── tests/                      # 测试代码
│   ├── unit/                   # 单元测试
│   └── integration/            # 集成测试
├── docs/                       # 项目文档
│   ├── PROJECT_PLAN.md         # 项目总计划
│   ├── architecture/           # 架构文档
│   └── guides/                 # 开发指南
├── openspec/                   # OpenSpec 规范
│   ├── changes/                # 变更提案
│   └── specs/                  # 功能规格
├── scripts/                    # 脚本工具
└── requirements.txt            # 依赖列表
```

### 1.2 模块职责划分

| 目录 | 职责描述 | 允许的依赖 |
|------|---------|-----------|
| `core/` | 核心业务逻辑、领域模型 | `infrastructure`, 第三方库 |
| `infrastructure/` | 底层技术支撑（配置、日志、缓存） | 仅第三方库，**严禁依赖 core** |
| `api/` | HTTP 接口、路由、DTO | `core`, `infrastructure` |
| `tests/` | 测试代码 | 所有模块 |
| `openspec/` | 需求和规格管理 | - |

**⚠️ 依赖原则**：
- 下层模块（Infrastructure）严禁依赖上层模块（Core, API）
- Core 模块可以依赖 Infrastructure
- API 模块可以依赖 Core 和 Infrastructure
- 避免循环依赖

## 2. 文件放置规则

### 2.1 新文件创建位置
- **业务逻辑**：放入 `core/{module_name}/`
- **通用工具**：放入 `core/utils/` 或 `infrastructure/utils/`（视依赖而定）
- **配置文件**：放入 `config/` 或项目根目录（如 `.env`）
- **测试文件**：放入 `tests/unit/` 或 `tests/integration/`，保持与源码目录结构一致
- **文档文件**：放入 `docs/` 或 `openspec/`

### 2.2 临时文件
- 临时脚本放入 `scripts/` 或根目录（以 `debug_` 或 `tmp_` 开头）
- **注意**：任务完成后必须清理根目录下的临时文件

## 3. 项目计划管理（PROJECT_PLAN.md）

### 3.1 Single Source of Truth
`docs/PROJECT_PLAN.md` 是项目进度和计划的唯一事实来源。

### 3.2 维护规则（硬性规则）

1. **新增需求**：
   - OpenSpec 提案一旦批准，必须立即在 PROJECT_PLAN.md 中添加对应条目
   - 格式：`- [ ] 功能名称 (Change ID)`

2. **任务完成**：
   - OpenSpec 实现并归档后，必须立即将条目改为 `[x]`
   - 添加完成日期：`- [x] 功能名称 (Change ID) - 2024-xx-xx`

3. **进度统计**：
   - 每次更新状态后，重新计算总体进度百分比
   - 更新文档顶部的进度条

### 3.3 文档结构要求

```markdown
# 📅 项目计划 (Project Plan)

## 📊 总体进度
进度：[||||||----] 60%

## 🗓️ 阶段一：基础架构
- [x] 核心配置模块 - 2024-01-10
- [x] 日志系统 - 2024-01-12

## 🗓️ 阶段二：LLM 服务
- [ ] LLM 流式响应 (add-llm-streaming)
- [ ] 视觉模型适配 (add-vision-adapter)
```

## 4. 版本控制与变更管理

### 4.1 提交信息规范
使用 Conventional Commits 规范：
- `feat: ...` 新功能
- `fix: ...` 修复 Bug
- `docs: ...` 文档变更
- `style: ...` 格式调整
- `refactor: ...` 重构
- `test: ...` 测试相关
- `chore: ...` 构建/工具相关

### 4.2 分支策略
- `main`: 主分支，保持稳定
- `develop`: 开发分支
- `feature/{change-id}`: 功能分支（对应 OpenSpec Change ID）
- `fix/{issue-id}`: 修复分支

## 5. 资源文件管理

### 5.1 静态资源
- 图片、字体等静态资源放入 `assets/` 或 `frontend/src/assets/`
- 避免将大文件（>50MB）提交到 Git

### 5.2 敏感信息
- **严禁**将 API Key、密码、私钥提交到代码库
- 使用环境变量（`.env`）管理敏感信息
- 确保 `.gitignore` 包含 `.env` 和其他敏感文件
