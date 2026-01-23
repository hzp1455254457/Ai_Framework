# Web前端框架技术设计文档

## Context

### 背景

AI框架项目提供了完整的后端API服务（FastAPI），包括：
- LLM服务API（聊天、流式聊天、模型列表）
- Agent服务API（任务执行、工具管理、记忆搜索、多Agent协作）
- Vision服务API（图像生成、分析、编辑）
- 健康检查API

为了支持用户快速构建Web应用界面，需要设计一套基于Vue3+TypeScript+Vite的前端框架方案。

### 约束条件

- **技术栈要求**：必须使用Vue3 + TypeScript + Vite
- **独立性**：方案作为独立设计文档，不在当前工程中实现代码
- **可执行性**：方案必须足够详细，能够指导AI或开发者生成完整代码
- **API对接**：必须与现有后端API完全对接
- **轻量级**：符合项目轻量级定位，避免过度设计

### 目标用户

- 个人开发者
- 需要快速构建AI应用Web界面的开发者
- 希望基于现有API构建前端应用的开发者

## Goals / Non-Goals

### Goals

1. **完整的架构设计**：提供清晰的前端架构方案
2. **代码生成指导**：方案足够详细，能够指导代码生成
3. **API完全对接**：与后端API无缝集成
4. **现代化技术栈**：使用Vue3 Composition API、TypeScript、Vite
5. **最佳实践**：遵循Vue3和TypeScript最佳实践
6. **可扩展性**：支持功能扩展和模块化开发

### Non-Goals

1. **不在当前工程实现**：仅提供设计文档，不生成代码
2. **不包含后端代码**：仅关注前端架构
3. **不过度设计**：保持轻量级，避免企业级复杂架构
4. **不包含测试框架**：测试框架选择留给实现者决定

## Decisions

### 决策1：技术栈选型

**决策**：使用Vue3 + TypeScript + Vite + Pinia + Vue Router

**理由**：
- **Vue3**：现代化、性能优秀、Composition API提供更好的逻辑复用
- **TypeScript**：类型安全，提升代码质量和开发体验
- **Vite**：快速构建工具，开发体验优秀
- **Pinia**：Vue3官方推荐的状态管理库，比Vuex更简洁
- **Vue Router**：Vue官方路由库，成熟稳定

**替代方案考虑**：
- React + TypeScript：Vue3更适合快速开发，学习曲线更平缓
- Vuex：Pinia是Vue3官方推荐，API更简洁
- Webpack：Vite构建速度更快，开发体验更好

### 决策2：项目目录结构

**决策**：采用功能模块化的目录结构

**理由**：
- 按功能模块组织，便于维护和扩展
- 清晰的职责划分
- 符合Vue3最佳实践

### 决策3：API客户端设计

**决策**：使用axios + 类型定义 + 统一错误处理

**理由**：
- axios成熟稳定，支持拦截器
- TypeScript类型定义确保类型安全
- 统一错误处理提升用户体验

### 决策4：状态管理策略

**决策**：使用Pinia进行全局状态管理，组件内使用ref/reactive

**理由**：
- Pinia轻量级，API简洁
- 全局状态（用户信息、配置等）使用Pinia
- 组件内状态使用Composition API的ref/reactive

## 详细设计

## 1. 技术栈

### 1.1 核心依赖

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.3",
    "vite": "^5.0.8",
    "@types/node": "^20.10.5",
    "eslint": "^8.56.0",
    "@typescript-eslint/parser": "^6.15.0",
    "@typescript-eslint/eslint-plugin": "^6.15.0",
    "prettier": "^3.1.1"
  }
}
```

### 1.2 技术栈说明

| 技术 | 版本 | 用途 | 理由 |
|------|------|------|------|
| Vue3 | ^3.4.0 | 前端框架 | 现代化、性能优秀、Composition API |
| TypeScript | ^5.3.3 | 类型系统 | 类型安全、提升代码质量 |
| Vite | ^5.0.8 | 构建工具 | 快速构建、优秀开发体验 |
| Vue Router | ^4.2.5 | 路由管理 | Vue官方路由库 |
| Pinia | ^2.1.7 | 状态管理 | Vue3官方推荐，轻量级 |
| Axios | ^1.6.2 | HTTP客户端 | 成熟稳定、支持拦截器 |

## 2. 项目目录结构

```
web-frontend/
├── public/                      # 静态资源
│   ├── favicon.ico
│   └── index.html
├── src/
│   ├── api/                    # API客户端
│   │   ├── client.ts           # Axios实例配置
│   │   ├── types.ts            # API类型定义
│   │   ├── llm.ts              # LLM API
│   │   ├── agent.ts            # Agent API
│   │   ├── vision.ts           # Vision API
│   │   └── health.ts           # 健康检查API
│   ├── stores/                 # Pinia状态管理
│   │   ├── index.ts            # Store入口
│   │   ├── app.ts              # 应用全局状态
│   │   ├── llm.ts              # LLM状态
│   │   ├── agent.ts            # Agent状态
│   │   └── vision.ts           # Vision状态
│   ├── router/                 # 路由配置
│   │   ├── index.ts            # 路由定义
│   │   └── guards.ts           # 路由守卫
│   ├── views/                  # 页面组件
│   │   ├── Home.vue            # 首页
│   │   ├── Chat.vue            # 聊天页面
│   │   ├── Agent.vue           # Agent页面
│   │   └── Vision.vue          # Vision页面
│   ├── components/            # 公共组件
│   │   ├── common/             # 通用组件
│   │   │   ├── Button.vue
│   │   │   ├── Input.vue
│   │   │   ├── Loading.vue
│   │   │   └── ErrorMessage.vue
│   │   ├── chat/               # 聊天相关组件
│   │   │   ├── ChatMessage.vue
│   │   │   ├── ChatInput.vue
│   │   │   └── ChatHistory.vue
│   │   ├── agent/              # Agent相关组件
│   │   │   ├── TaskPanel.vue
│   │   │   ├── ToolList.vue
│   │   │   └── MemorySearch.vue
│   │   └── vision/             # Vision相关组件
│   │       ├── ImageGenerator.vue
│   │       ├── ImageAnalyzer.vue
│   │       └── ImageEditor.vue
│   ├── composables/            # 组合式函数
│   │   ├── useApi.ts           # API调用封装
│   │   ├── useStream.ts        # 流式响应处理
│   │   ├── useError.ts         # 错误处理
│   │   └── useConfig.ts        # 配置管理
│   ├── utils/                  # 工具函数
│   │   ├── request.ts          # 请求工具
│   │   ├── format.ts           # 格式化工具
│   │   └── constants.ts        # 常量定义
│   ├── types/                  # TypeScript类型定义
│   │   ├── api.ts              # API类型
│   │   ├── store.ts            # Store类型
│   │   └── common.ts           # 通用类型
│   ├── assets/                 # 资源文件
│   │   ├── styles/             # 样式文件
│   │   │   ├── main.css        # 主样式
│   │   │   └── variables.css   # CSS变量
│   │   └── images/             # 图片资源
│   ├── App.vue                 # 根组件
│   └── main.ts                 # 入口文件
├── .env                        # 环境变量
├── .env.development            # 开发环境变量
├── .env.production             # 生产环境变量
├── .eslintrc.js                # ESLint配置
├── .prettierrc                 # Prettier配置
├── tsconfig.json               # TypeScript配置
├── vite.config.ts              # Vite配置
├── package.json                # 项目配置
└── README.md                    # 项目说明
```

## 3. 核心模块设计

### 3.1 API客户端设计

#### 3.1.1 Axios实例配置

**文件**：`src/api/client.ts`

```typescript
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

// API基础URL（从环境变量读取）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 创建Axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    // 统一错误处理
    if (error.response) {
      // 服务器返回错误
      const { status, data } = error.response
      console.error(`API Error [${status}]:`, data)
    } else if (error.request) {
      // 请求发送但无响应
      console.error('Network Error:', error.request)
    } else {
      // 其他错误
      console.error('Error:', error.message)
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

#### 3.1.2 API类型定义

**文件**：`src/api/types.ts`

```typescript
// 消息类型
export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
}

// 聊天请求
export interface ChatRequest {
  messages: Message[]
  model?: string
  temperature?: number
  max_tokens?: number
}

// Token使用信息
export interface UsageInfo {
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
}

// 聊天响应
export interface ChatResponse {
  content: string
  model: string
  usage: UsageInfo
  metadata: Record<string, any>
}

// 流式聊天响应（SSE格式）
export interface StreamChatChunk {
  content?: string
  model?: string
  usage?: UsageInfo
  metadata?: Record<string, any>
  error?: string
}

// Agent任务请求
export interface AgentTaskRequest {
  task: string
  conversation_id?: string
  model?: string
  temperature?: number
  max_tokens?: number
  use_planner?: boolean
  context?: Record<string, any>
}

// Agent任务响应
export interface AgentTaskResponse {
  content: string
  tool_calls: Array<{
    tool: string
    arguments: Record<string, any>
    result?: any
  }>
  iterations: number
  metadata: Record<string, any>
}

// 工具注册请求
export interface ToolRegistrationRequest {
  name: string
  description: string
  parameters: Record<string, any>
  allow_override?: boolean
}

// 向量搜索请求
export interface VectorSearchRequest {
  query: string
  top_k?: number
  conversation_id?: string
}

// Vision图像生成请求
export interface VisionGenerateRequest {
  prompt: string
  size?: string
  n?: number
  quality?: string
  style?: string
  adapter_name?: string
}

// Vision图像生成响应
export interface VisionGenerateResponse {
  images: string[]
  model: string
  count: number
  created_at: string
  metadata: Record<string, any>
}

// Vision图像分析请求
export interface VisionAnalyzeRequest {
  image: string
  analyze_type?: string
  options?: Record<string, any>
  adapter_name?: string
}

// Vision图像分析响应
export interface VisionAnalyzeResponse {
  model: string
  text?: string
  objects: Array<Record<string, any>>
  description?: string
  created_at: string
  metadata: Record<string, any>
}

// 健康检查响应
export interface HealthResponse {
  status: string
  version: string
  adapters: string[]
  models: string[]
}
```

#### 3.1.3 LLM API

**文件**：`src/api/llm.ts`

```typescript
import apiClient from './client'
import type { ChatRequest, ChatResponse, StreamChatChunk } from './types'

/**
 * LLM API客户端
 */
export const llmApi = {
  /**
   * 普通聊天
   */
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/llm/chat', request)
    return response.data
  },

  /**
   * 流式聊天（Server-Sent Events）
   */
  async streamChat(
    request: ChatRequest,
    onChunk: (chunk: StreamChatChunk) => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    try {
      const response = await fetch(
        `${apiClient.defaults.baseURL}/llm/chat/stream`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('Response body is null')
      }

      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              return
            }
            try {
              const chunk: StreamChatChunk = JSON.parse(data)
              onChunk(chunk)
            } catch (e) {
              console.error('Failed to parse SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error))
      if (onError) {
        onError(err)
      } else {
        throw err
      }
    }
  },

  /**
   * 获取支持的模型列表
   */
  async listModels(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/llm/models')
    return response.data
  },
}
```

#### 3.1.4 Agent API

**文件**：`src/api/agent.ts`

```typescript
import apiClient from './client'
import type {
  AgentTaskRequest,
  AgentTaskResponse,
  ToolRegistrationRequest,
  VectorSearchRequest,
} from './types'

/**
 * Agent API客户端
 */
export const agentApi = {
  /**
   * 执行Agent任务
   */
  async runTask(request: AgentTaskRequest): Promise<AgentTaskResponse> {
    const response = await apiClient.post<AgentTaskResponse>(
      '/agent/task',
      request
    )
    return response.data
  },

  /**
   * 注册工具
   */
  async registerTool(
    request: ToolRegistrationRequest
  ): Promise<{ success: boolean; message: string; tool_name: string }> {
    const response = await apiClient.post('/agent/tools/register', request)
    return response.data
  },

  /**
   * 获取工具列表
   */
  async listTools(): Promise<{
    tools: Record<string, any>
    schemas: Record<string, any>
    count: number
  }> {
    const response = await apiClient.get('/agent/tools')
    return response.data
  },

  /**
   * 向量语义搜索
   */
  async searchMemory(request: VectorSearchRequest): Promise<{
    results: Array<Record<string, any>>
    count: number
  }> {
    const response = await apiClient.post('/agent/memory/search', request)
    return response.data
  },

  /**
   * 多Agent协作任务
   */
  async executeMultiAgentTask(request: {
    task: string
    strategy?: string
    agent_ids?: string[]
    conversation_id?: string
    model?: string
    temperature?: number
  }): Promise<{
    content: string
    agent_results: Array<Record<string, any>>
    strategy: string
    metadata: Record<string, any>
  }> {
    const response = await apiClient.post('/agent/collaboration/task', request)
    return response.data
  },

  /**
   * 获取多Agent协作状态
   */
  async getCollaborationStatus(): Promise<{
    agents: Record<string, any>
    strategy: string
    total_agents: number
  }> {
    const response = await apiClient.get('/agent/collaboration/status')
    return response.data
  },
}
```

#### 3.1.5 Vision API

**文件**：`src/api/vision.ts`

```typescript
import apiClient from './client'
import type {
  VisionGenerateRequest,
  VisionGenerateResponse,
  VisionAnalyzeRequest,
  VisionAnalyzeResponse,
} from './types'

/**
 * Vision API客户端
 */
export const visionApi = {
  /**
   * 生成图像
   */
  async generate(
    request: VisionGenerateRequest
  ): Promise<VisionGenerateResponse> {
    const response = await apiClient.post<VisionGenerateResponse>(
      '/vision/generate',
      request
    )
    return response.data
  },

  /**
   * 分析图像
   */
  async analyze(
    request: VisionAnalyzeRequest
  ): Promise<VisionAnalyzeResponse> {
    const response = await apiClient.post<VisionAnalyzeResponse>(
      '/vision/analyze',
      request
    )
    return response.data
  },

  /**
   * 编辑图像
   */
  async edit(request: {
    image: string
    prompt: string
    mask?: string
    size?: string
    n?: number
    adapter_name?: string
  }): Promise<VisionGenerateResponse> {
    const response = await apiClient.post<VisionGenerateResponse>(
      '/vision/edit',
      request
    )
    return response.data
  },
}
```

#### 3.1.6 健康检查API

**文件**：`src/api/health.ts`

```typescript
import apiClient from './client'
import type { HealthResponse } from './types'

/**
 * 健康检查API客户端
 */
export const healthApi = {
  /**
   * 获取服务健康状态
   */
  async checkHealth(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/health')
    return response.data
  },

  /**
   * 获取适配器健康状态
   */
  async checkAdapterHealth(): Promise<{
    adapters: Record<string, any>
    healthy_count: number
    unhealthy_count: number
    unknown_count: number
  }> {
    const response = await apiClient.get('/health/adapters')
    return response.data
  },
}
```

### 3.2 状态管理设计（Pinia）

#### 3.2.1 应用全局状态

**文件**：`src/stores/app.ts`

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { healthApi } from '@/api/health'
import type { HealthResponse } from '@/api/types'

export const useAppStore = defineStore('app', () => {
  // 状态
  const health = ref<HealthResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 操作
  const checkHealth = async () => {
    try {
      loading.value = true
      error.value = null
      health.value = await healthApi.checkHealth()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return {
    health,
    loading,
    error,
    checkHealth,
  }
})
```

#### 3.2.2 LLM状态

**文件**：`src/stores/llm.ts`

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { llmApi } from '@/api/llm'
import type { ChatRequest, ChatResponse, Message } from '@/api/types'

export const useLLMStore = defineStore('llm', () => {
  // 状态
  const messages = ref<Message[]>([])
  const currentModel = ref<string | null>(null)
  const availableModels = ref<string[]>([])
  const loading = ref(false)
  const streaming = ref(false)
  const error = ref<string | null>(null)

  // 操作
  const loadModels = async () => {
    try {
      availableModels.value = await llmApi.listModels()
      if (availableModels.value.length > 0 && !currentModel.value) {
        currentModel.value = availableModels.value[0]
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load models'
    }
  }

  const sendMessage = async (content: string) => {
    try {
      loading.value = true
      error.value = null

      // 添加用户消息
      const userMessage: Message = { role: 'user', content }
      messages.value.push(userMessage)

      // 构建请求
      const request: ChatRequest = {
        messages: messages.value,
        model: currentModel.value || undefined,
      }

      // 发送请求
      const response: ChatResponse = await llmApi.chat(request)

      // 添加助手回复
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.content,
      }
      messages.value.push(assistantMessage)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to send message'
    } finally {
      loading.value = false
    }
  }

  const streamMessage = async (
    content: string,
    onChunk: (chunk: string) => void
  ) => {
    try {
      streaming.value = true
      error.value = null

      // 添加用户消息
      const userMessage: Message = { role: 'user', content }
      messages.value.push(userMessage)

      // 构建请求
      const request: ChatRequest = {
        messages: messages.value,
        model: currentModel.value || undefined,
      }

      let assistantContent = ''

      // 流式接收
      await llmApi.streamChat(
        request,
        (chunk) => {
          if (chunk.content) {
            assistantContent += chunk.content
            onChunk(chunk.content)
          }
          if (chunk.error) {
            throw new Error(chunk.error)
          }
        },
        (err) => {
          throw err
        }
      )

      // 添加完整的助手回复
      const assistantMessage: Message = {
        role: 'assistant',
        content: assistantContent,
      }
      messages.value.push(assistantMessage)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to stream message'
    } finally {
      streaming.value = false
    }
  }

  const clearMessages = () => {
    messages.value = []
  }

  return {
    messages,
    currentModel,
    availableModels,
    loading,
    streaming,
    error,
    loadModels,
    sendMessage,
    streamMessage,
    clearMessages,
  }
})
```

#### 3.2.3 Agent状态

**文件**：`src/stores/agent.ts`

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { agentApi } from '@/api/agent'
import type { AgentTaskResponse } from '@/api/types'

export const useAgentStore = defineStore('agent', () => {
  // 状态
  const currentTask = ref<string>('')
  const taskResult = ref<AgentTaskResponse | null>(null)
  const tools = ref<Record<string, any>>({})
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 操作
  const loadTools = async () => {
    try {
      const data = await agentApi.listTools()
      tools.value = data.tools
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load tools'
    }
  }

  const runTask = async (task: string, options?: {
    conversation_id?: string
    model?: string
    temperature?: number
  }) => {
    try {
      loading.value = true
      error.value = null
      currentTask.value = task

      const response = await agentApi.runTask({
        task,
        ...options,
      })

      taskResult.value = response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to run task'
    } finally {
      loading.value = false
    }
  }

  return {
    currentTask,
    taskResult,
    tools,
    loading,
    error,
    loadTools,
    runTask,
  }
})
```

### 3.3 路由设计

**文件**：`src/router/index.ts`

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat.vue'),
  },
  {
    path: '/agent',
    name: 'Agent',
    component: () => import('@/views/Agent.vue'),
  },
  {
    path: '/vision',
    name: 'Vision',
    component: () => import('@/views/Vision.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

### 3.4 组合式函数（Composables）

#### 3.4.1 流式响应处理

**文件**：`src/composables/useStream.ts`

```typescript
import { ref } from 'vue'

export function useStream() {
  const streamContent = ref('')
  const isStreaming = ref(false)

  const startStream = () => {
    streamContent.value = ''
    isStreaming.value = true
  }

  const appendChunk = (chunk: string) => {
    streamContent.value += chunk
  }

  const endStream = () => {
    isStreaming.value = false
  }

  const reset = () => {
    streamContent.value = ''
    isStreaming.value = false
  }

  return {
    streamContent,
    isStreaming,
    startStream,
    appendChunk,
    endStream,
    reset,
  }
}
```

#### 3.4.2 错误处理

**文件**：`src/composables/useError.ts`

```typescript
import { ref } from 'vue'

export function useError() {
  const error = ref<string | null>(null)

  const setError = (message: string) => {
    error.value = message
  }

  const clearError = () => {
    error.value = null
  }

  const handleError = (err: unknown) => {
    if (err instanceof Error) {
      setError(err.message)
    } else {
      setError('An unknown error occurred')
    }
  }

  return {
    error,
    setError,
    clearError,
    handleError,
  }
}
```

### 3.5 组件设计示例

#### 3.5.1 聊天消息组件

**文件**：`src/components/chat/ChatMessage.vue`

```vue
<template>
  <div :class="['chat-message', `chat-message--${message.role}`]">
    <div class="chat-message__avatar">
      <span v-if="message.role === 'user'">👤</span>
      <span v-else>🤖</span>
    </div>
    <div class="chat-message__content">
      <div class="chat-message__text">{{ message.content }}</div>
      <div v-if="message.role === 'assistant' && usage" class="chat-message__meta">
        <span>Tokens: {{ usage.total_tokens }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message, UsageInfo } from '@/api/types'

interface Props {
  message: Message
  usage?: UsageInfo
}

defineProps<Props>()
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 12px;
  padding: 12px;
  margin-bottom: 16px;
}

.chat-message--user {
  flex-direction: row-reverse;
}

.chat-message__avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
}

.chat-message__content {
  flex: 1;
}

.chat-message__text {
  padding: 8px 12px;
  border-radius: 8px;
  background: #f5f5f5;
}

.chat-message--user .chat-message__text {
  background: #007bff;
  color: white;
}

.chat-message__meta {
  margin-top: 4px;
  font-size: 12px;
  color: #666;
}
</style>
```

#### 3.5.2 聊天输入组件

**文件**：`src/components/chat/ChatInput.vue`

```vue
<template>
  <div class="chat-input">
    <textarea
      v-model="inputText"
      :disabled="loading"
      @keydown.enter.exact.prevent="handleSend"
      @keydown.enter.shift.exact="inputText += '\n'"
      placeholder="输入消息..."
      rows="3"
    />
    <div class="chat-input__actions">
      <button @click="handleSend" :disabled="loading || !inputText.trim()">
        {{ loading ? '发送中...' : '发送' }}
      </button>
      <label>
        <input type="checkbox" v-model="useStream" />
        流式输出
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useLLMStore } from '@/stores/llm'
import { useStream } from '@/composables/useStream'

const llmStore = useLLMStore()
const { streamContent, startStream, appendChunk, endStream } = useStream()

const inputText = ref('')
const useStream = ref(false)

const handleSend = async () => {
  if (!inputText.value.trim()) return

  const message = inputText.value.trim()
  inputText.value = ''

  if (useStream.value) {
    startStream()
    await llmStore.streamMessage(message, appendChunk)
    endStream()
  } else {
    await llmStore.sendMessage(message)
  }
}
</script>

<style scoped>
.chat-input {
  padding: 16px;
  border-top: 1px solid #e0e0e0;
}

.chat-input textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
}

.chat-input__actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.chat-input__actions button {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.chat-input__actions button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
```

### 3.6 页面组件示例

#### 3.6.1 聊天页面

**文件**：`src/views/Chat.vue`

```vue
<template>
  <div class="chat-page">
    <div class="chat-page__header">
      <h1>AI聊天</h1>
      <select v-model="selectedModel" @change="handleModelChange">
        <option v-for="model in availableModels" :key="model" :value="model">
          {{ model }}
        </option>
      </select>
      <button @click="clearMessages">清空对话</button>
    </div>

    <div class="chat-page__messages">
      <ChatMessage
        v-for="(message, index) in messages"
        :key="index"
        :message="message"
      />
      <div v-if="loading" class="chat-page__loading">思考中...</div>
    </div>

    <ChatInput />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useLLMStore } from '@/stores/llm'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import ChatInput from '@/components/chat/ChatInput.vue'

const llmStore = useLLMStore()

const messages = computed(() => llmStore.messages)
const availableModels = computed(() => llmStore.availableModels)
const selectedModel = computed({
  get: () => llmStore.currentModel || '',
  set: (value) => {
    llmStore.currentModel = value
  },
})
const loading = computed(() => llmStore.loading)

const handleModelChange = () => {
  // 模型切换逻辑
}

const clearMessages = () => {
  llmStore.clearMessages()
}

onMounted(() => {
  llmStore.loadModels()
})
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.chat-page__header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.chat-page__messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.chat-page__loading {
  padding: 16px;
  text-align: center;
  color: #666;
}
</style>
```

## 4. 配置文件

### 4.1 Vite配置

**文件**：`vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### 4.2 TypeScript配置

**文件**：`tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 4.3 环境变量配置

**文件**：`.env.development`

```env
VITE_API_BASE_URL=http://localhost:8000
```

**文件**：`.env.production`

```env
VITE_API_BASE_URL=https://api.example.com
```

### 4.4 ESLint配置

**文件**：`.eslintrc.js`

```javascript
module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es2021: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:vue/vue3-recommended',
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    ecmaVersion: 2021,
    parser: '@typescript-eslint/parser',
    sourceType: 'module',
  },
  plugins: ['@typescript-eslint'],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
  },
}
```

### 4.5 Prettier配置

**文件**：`.prettierrc`

```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

## 5. 入口文件

**文件**：`src/main.ts`

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
```

**文件**：`src/App.vue`

```vue
<template>
  <div id="app">
    <nav class="app-nav">
      <router-link to="/">首页</router-link>
      <router-link to="/chat">聊天</router-link>
      <router-link to="/agent">Agent</router-link>
      <router-link to="/vision">Vision</router-link>
    </nav>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
// App根组件
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.app-nav {
  display: flex;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.app-nav a {
  text-decoration: none;
  color: #333;
  padding: 8px 16px;
  border-radius: 4px;
}

.app-nav a.router-link-active {
  background: #007bff;
  color: white;
}

.app-main {
  flex: 1;
}
</style>
```

## 6. 代码规范和最佳实践

### 6.1 命名规范

- **组件名**：PascalCase（如 `ChatMessage.vue`）
- **文件名**：kebab-case（如 `chat-message.vue`）
- **变量/函数名**：camelCase（如 `sendMessage`）
- **常量**：UPPER_SNAKE_CASE（如 `API_BASE_URL`）
- **类型/接口**：PascalCase（如 `ChatRequest`）

### 6.2 组件设计原则

1. **单一职责**：每个组件只负责一个功能
2. **可复用性**：通用组件放在 `components/common/`
3. **组合式API**：优先使用 Composition API
4. **TypeScript**：所有组件和函数都要有类型定义
5. **Props验证**：使用 TypeScript 接口定义 Props

### 6.3 状态管理原则

1. **全局状态**：使用 Pinia Store
2. **组件状态**：使用 ref/reactive
3. **共享逻辑**：使用 Composables

### 6.4 API调用原则

1. **统一封装**：所有API调用通过 `api/` 目录
2. **类型安全**：使用 TypeScript 类型定义
3. **错误处理**：统一错误处理机制
4. **加载状态**：使用 loading 状态管理

## 7. 构建和部署

### 7.1 开发环境

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 7.2 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录，可以部署到任何静态文件服务器。

### 7.3 部署选项

1. **静态托管**：Netlify、Vercel、GitHub Pages
2. **CDN**：Cloudflare、AWS CloudFront
3. **服务器**：Nginx、Apache

## 8. 与后端API对接

### 8.1 API端点映射

| 前端功能 | 后端API端点 | 方法 |
|---------|------------|------|
| 聊天 | `/api/v1/llm/chat` | POST |
| 流式聊天 | `/api/v1/llm/chat/stream` | POST (SSE) |
| 模型列表 | `/api/v1/llm/models` | GET |
| Agent任务 | `/api/v1/agent/task` | POST |
| 工具列表 | `/api/v1/agent/tools` | GET |
| 图像生成 | `/api/v1/vision/generate` | POST |
| 图像分析 | `/api/v1/vision/analyze` | POST |
| 健康检查 | `/api/v1/health` | GET |

### 8.2 请求/响应格式

所有API请求和响应格式已在 `src/api/types.ts` 中定义，与后端完全对应。

## 9. 扩展指南

### 9.1 添加新页面

1. 在 `src/views/` 创建新组件
2. 在 `src/router/index.ts` 添加路由
3. 在导航中添加链接

### 9.2 添加新API

1. 在 `src/api/types.ts` 定义类型
2. 在对应的API文件中添加方法
3. 在Store中使用新API

### 9.3 添加新组件

1. 在 `src/components/` 创建组件
2. 使用 TypeScript 定义 Props
3. 遵循组件设计原则

## Risks / Trade-offs

### 风险

1. **API变更**：后端API变更需要同步更新前端类型定义
   - **缓解**：使用TypeScript类型定义，编译时检查

2. **跨域问题**：开发环境可能遇到CORS问题
   - **缓解**：Vite代理配置，生产环境配置CORS

3. **流式响应处理**：SSE处理可能复杂
   - **缓解**：封装为Composable，简化使用

### 权衡

1. **状态管理**：Pinia vs Vuex
   - **选择**：Pinia（更简洁，Vue3官方推荐）

2. **HTTP客户端**：Axios vs Fetch
   - **选择**：Axios（功能更丰富，拦截器支持）

3. **UI框架**：自建 vs 第三方
   - **选择**：自建（轻量级，符合项目定位）

## Migration Plan

本方案为全新设计，无需迁移。实现者可以：

1. 创建新项目
2. 按照本方案搭建项目结构
3. 逐步实现各个模块
4. 与后端API对接测试

## Open Questions

1. **认证方案**：是否需要用户认证？如果需要，使用JWT还是其他方案？
2. **UI框架**：是否需要引入UI组件库（如Element Plus、Ant Design Vue）？
3. **国际化**：是否需要多语言支持？
4. **主题**：是否需要暗色模式支持？

## 总结

本设计文档提供了完整的Vue3+TypeScript+Vite前端框架方案，包括：

- ✅ 完整的技术栈选型和理由
- ✅ 详细的项目目录结构
- ✅ 核心模块的完整代码示例
- ✅ API客户端与后端完全对接
- ✅ 状态管理、路由、组件设计
- ✅ 开发工具配置
- ✅ 代码规范和最佳实践
- ✅ 构建和部署方案

本方案足够详细，可以直接用于指导另一个工程生成完整的前端代码。
