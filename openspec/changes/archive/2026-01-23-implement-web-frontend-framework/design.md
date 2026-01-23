# Design: Web前端框架实现

## 架构概述

本设计基于 `Ai_Web/design.md` 技术设计文档，实现完整的Vue3+TypeScript+Vite前端应用，与后端FastAPI API完全对接。

## 技术架构

### 技术栈选型

- **Vue3 (^3.4.0)**：现代化前端框架，Composition API提供更好的逻辑复用
- **TypeScript (^5.3.3)**：类型安全，提升代码质量
- **Vite (^5.0.8)**：快速构建工具，优秀开发体验
- **Pinia (^2.1.7)**：Vue3官方推荐的状态管理库，轻量级
- **Vue Router (^4.2.5)**：Vue官方路由库
- **Axios (^1.6.2)**：成熟稳定的HTTP客户端

### 项目结构

```
Ai_Web/
├── src/
│   ├── api/                    # API客户端层
│   ├── stores/                 # Pinia状态管理
│   ├── router/                 # 路由配置
│   ├── views/                  # 页面组件
│   ├── components/             # 公共组件
│   ├── composables/           # 组合式函数
│   ├── utils/                  # 工具函数
│   ├── types/                  # TypeScript类型定义
│   └── assets/                 # 静态资源
├── public/                     # 公共静态资源
├── .env.development            # 开发环境变量
├── .env.production             # 生产环境变量
├── vite.config.ts             # Vite配置
├── tsconfig.json              # TypeScript配置
└── package.json               # 项目配置
```

## 核心模块设计

### 1. API客户端层

**设计原则**：
- 统一封装所有API调用
- 完整的TypeScript类型定义
- 统一错误处理机制
- 支持流式响应（SSE）

**实现要点**：
- Axios实例配置：baseURL、timeout、拦截器
- 请求拦截器：可添加认证token等
- 响应拦截器：统一错误处理
- 流式响应：使用fetch API处理SSE

### 2. 状态管理（Pinia）

**设计原则**：
- 全局状态使用Pinia Store
- 组件内状态使用ref/reactive
- Store按功能模块划分

**Store设计**：
- `app.ts`：应用全局状态（健康检查、配置）
- `llm.ts`：LLM相关状态（消息、模型、流式响应）
- `agent.ts`：Agent相关状态（任务、工具、结果）
- `vision.ts`：Vision相关状态（图像生成、分析结果）

### 3. 路由系统

**设计原则**：
- 使用Vue Router进行路由管理
- 路由懒加载提升性能
- 可扩展的路由守卫

**路由定义**：
- `/` - 首页
- `/chat` - 聊天页面
- `/agent` - Agent页面
- `/vision` - Vision页面

### 4. 组件设计

**设计原则**：
- 单一职责原则
- 可复用性优先
- Composition API优先
- TypeScript类型完整

**组件分类**：
- **通用组件**：Button、Input、Loading、ErrorMessage
- **聊天组件**：ChatMessage、ChatInput、ChatHistory
- **Agent组件**：TaskPanel、ToolList、MemorySearch
- **Vision组件**：ImageGenerator、ImageAnalyzer、ImageEditor

### 5. 组合式函数（Composables）

**设计原则**：
- 封装可复用的逻辑
- 提供清晰的API
- 类型安全

**Composables**：
- `useStream`：流式响应处理
- `useError`：错误处理
- `useApi`：API调用封装
- `useConfig`：配置管理

## 与后端API集成

### API端点映射

| 前端功能 | 后端API端点 | 方法 |
|---------|------------|------|
| 聊天 | `/api/v1/llm/chat` | POST |
| 流式聊天 | `/api/v1/llm/chat/stream` | POST (SSE) |
| 模型列表 | `/api/v1/llm/models` | GET |
| Agent任务 | `/api/v1/agent/task` | POST |
| 工具列表 | `/api/v1/agent/tools` | GET |
| 记忆搜索 | `/api/v1/agent/memory/search` | POST |
| 图像生成 | `/api/v1/vision/generate` | POST |
| 图像分析 | `/api/v1/vision/analyze` | POST |
| 健康检查 | `/api/v1/health` | GET |

### 类型定义对齐

所有API请求和响应类型定义必须与后端FastAPI模型完全对应，确保类型安全。

## 开发工具配置

### Vite配置

- 路径别名：`@` 指向 `src/`
- 开发服务器代理：`/api` 代理到后端
- 插件：Vue插件

### TypeScript配置

- 严格模式
- 路径解析：`@/*` 映射到 `src/*`
- 支持Vue SFC

### ESLint和Prettier

- ESLint：Vue3 + TypeScript规则
- Prettier：代码格式化

## 构建和部署

### 开发环境

```bash
npm install
npm run dev
```

### 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录，可部署到静态文件服务器。

## 代码规范

### 命名规范

- 组件名：PascalCase（如 `ChatMessage.vue`）
- 文件名：kebab-case（如 `chat-message.vue`）
- 变量/函数名：camelCase（如 `sendMessage`）
- 常量：UPPER_SNAKE_CASE（如 `API_BASE_URL`）
- 类型/接口：PascalCase（如 `ChatRequest`）

### 组件设计原则

1. 单一职责：每个组件只负责一个功能
2. 可复用性：通用组件放在 `components/common/`
3. Composition API：优先使用 Composition API
4. TypeScript：所有组件和函数都要有类型定义
5. Props验证：使用 TypeScript 接口定义 Props

## 风险与缓解

### 风险1：API变更

**风险**：后端API变更需要同步更新前端类型定义

**缓解**：
- 使用TypeScript类型定义，编译时检查
- 保持API类型定义与后端模型同步

### 风险2：跨域问题

**风险**：开发环境可能遇到CORS问题

**缓解**：
- Vite代理配置
- 生产环境配置CORS

### 风险3：流式响应处理

**风险**：SSE处理可能复杂

**缓解**：
- 封装为Composable，简化使用
- 提供清晰的错误处理

## 扩展性考虑

### 添加新页面

1. 在 `src/views/` 创建新组件
2. 在 `src/router/index.ts` 添加路由
3. 在导航中添加链接

### 添加新API

1. 在 `src/api/types.ts` 定义类型
2. 在对应的API文件中添加方法
3. 在Store中使用新API

### 添加新组件

1. 在 `src/components/` 创建组件
2. 使用 TypeScript 定义 Props
3. 遵循组件设计原则
