# AI框架项目计划文档

## 📋 文档说明

本文档是AI框架项目的需求清单和开发计划，记录所有功能需求的完成状态和优先级。

**核心原则**：
1. **硬性规则**：完成功能时必须同步更新本文档
2. **单一真相源**：本文档是项目进度和需求状态的唯一权威来源
3. **优先级明确**：所有需求都有明确的优先级划分
4. **状态透明**：清楚标记已完成、进行中、未开始的功能

---

## 🎯 项目概述

基于《AI框架架构方案文档.md》制定的详细开发计划。

**目标**：构建一个轻量级、模块化、易扩展的个人AI应用框架

**核心定位**：
- 轻量级：适合个人开发者，不依赖重型基础设施
- 模块化：各功能模块独立，按需使用
- 易扩展：插件化架构，方便添加新的AI能力
- 易用性：简洁的API设计，降低使用门槛

---

## 📊 总体进度

- **总需求数**：51项
- **已完成**：31项
- **进行中**：0项
- **未开始**：20项
- **总体完成度**：61%

---

## 🔥 优先级说明

- **P0（关键）**：核心功能，必须完成才能发布MVP
- **P1（高）**：重要功能，影响用户体验
- **P2（中）**：有用功能，可以逐步完善
- **P3（低）**：可选功能，可以后续迭代

---

## 📦 第一阶段：核心基础设施（Phase 1）

### ✅ 已完成

#### 1.1 基础服务框架
- [x] **BaseService基类** (P0) - `core/base/service.py`
  - 统一的初始化流程
  - 配置管理集成
  - 日志管理集成
  - 生命周期管理（初始化/清理）
  - 异步上下文管理器支持
  
- [x] **BaseAdapter基类** (P0) - `core/base/adapter.py`
  - 适配器接口定义
  - 配置管理
  - 生命周期管理
  - 异步上下文管理器支持
  
- [x] **BasePlugin基类** (P0) - `core/base/plugin.py`
  - 插件接口定义
  - 插件执行接口
  - 生命周期管理
  - 依赖管理

#### 1.2 配置管理模块
- [x] **ConfigManager** (P0) - `infrastructure/config/manager.py`
  - 多环境配置支持（dev/prod）
  - 配置文件加载（YAML/JSON）
  - 环境变量支持
  - 配置热重载
  - 嵌套配置访问
  - 配置验证
  
- [x] **ConfigLoader** (P0) - `infrastructure/config/loader.py`
  - YAML文件加载
  - JSON文件加载
  - 环境变量加载
  
- [x] **ConfigValidator** (P0) - `infrastructure/config/validator.py`
  - 配置格式验证
  - 必填项检查

#### 1.3 日志管理模块
- [x] **LogManager** (P0) - `infrastructure/log/manager.py`
  - 结构化日志
  - 多级别日志支持
  - 控制台输出
  - 文件日志输出
  - 日志轮转
  - 日志缓存（logger复用）

### ⏳ 未完成

#### 1.4 缓存管理模块
- [x] **CacheManager** (P1) - `infrastructure/cache/manager.py`
  - 统一缓存接口
  - 多后端支持（内存/Redis/文件）
  - TTL管理
  - 缓存策略（LRU、FIFO等）
  - 完成日期：2026-01-21
  - 说明：已实现Memory后端与CacheManager（Redis/File后端仍待实现）
  
- [x] **内存缓存后端** (P1) - `infrastructure/cache/backends/memory.py`
  - TTL + LRU
  - 完成日期：2026-01-21
  
- [ ] **Redis缓存后端** (P2) - `infrastructure/cache/backends/redis.py`
  
- [ ] **文件缓存后端** (P2) - `infrastructure/cache/backends/file.py`

#### 1.5 存储管理模块
- [x] **StorageManager** (P1) - `infrastructure/storage/manager.py`
  - 统一存储接口
  - 多后端支持
  - 完成日期：2026-01-21
  - 说明：已实现统一存储接口，支持数据库和文件存储后端
  
- [x] **Database存储** (P1) - `infrastructure/storage/backends/database.py`
  - SQLite支持
  - 对话历史存储
  - 文件信息存储
  - 完成日期：2026-01-21
  - 说明：已实现基于SQLite的数据库存储后端，支持对话历史和文件信息存储
  
- [x] **文件存储** (P1) - `infrastructure/storage/backends/file_storage.py`
  - 文件信息存储
  - 文件管理
  - 完成日期：2026-01-21
  - 说明：已实现基于文件系统的存储后端，支持对话历史和文件信息存储
  
- [ ] **向量数据库** (P2) - `infrastructure/storage/vector_db.py`
  - Chroma集成
  - SQLite-VSS集成
  - 向量化存储和检索

---

## 🧠 第二阶段：LLM服务模块（Phase 2）

### ✅ 已完成

#### 2.1 LLM服务核心
- [x] **LLMService** (P0) - `core/llm/service.py`
  - 统一的多模型接口
  - 聊天功能
  - 流式输出
  - Token计算（简化实现）
  - 适配器管理
  - 自动发现和注册机制
  
- [x] **ConversationContext** (P0) - `core/llm/context.py`
  - 对话历史管理
  - 消息添加和获取
  - 上下文清理
  - 最大消息数限制
  
- [x] **LLM数据模型** (P0) - `core/llm/models.py`
  - LLMRequest模型
  - LLMResponse模型
  - LLMMessage模型

#### 2.2 LLM适配器
- [x] **BaseLLMAdapter** (P0) - `core/llm/adapters/base.py`
  - 适配器基类
  - 统一调用接口
  
- [x] **AdapterRegistry** (P1) - `core/llm/adapters/registry.py`
  - 适配器自动发现
  - 适配器注册管理
  - 模型到适配器映射
  
- [x] **豆包适配器** (P1) - `core/llm/adapters/doubao_adapter.py`
  - 豆包API集成
  - 流式响应支持
  
- [x] **通义千问适配器** (P1) - `core/llm/adapters/qwen_adapter.py`
  - 通义千问API集成
  - 流式响应支持
  
- [x] **DeepSeek适配器** (P1) - `core/llm/adapters/deepseek_adapter.py`
  - DeepSeek API集成
  - 流式响应支持

### ⏳ 未完成

#### 2.3 其他LLM适配器
- [x] **OpenAI适配器** (P1) - `core/llm/adapters/openai_adapter.py`
  - GPT-3.5/GPT-4支持
  - 流式响应支持
  - Function Calling支持
  - 完成日期：2026-01-21
  
- [x] **Claude适配器** (P1) - `core/llm/adapters/claude_adapter.py`
  - Claude 3支持
  - 流式响应支持
  - 完成日期：2026-01-21
  - 说明：已实现Anthropic Messages API调用与流式输出（SSE解析）
  
- [x] **Ollama适配器** (P1) - `core/llm/adapters/ollama_adapter.py`
  - 本地模型支持
  - Ollama API集成
  - 完成日期：2026-01-21
  - 说明：已实现本地Ollama /api/chat 调用与流式输出（JSON lines）
  
- [ ] **本地模型适配器** (P2) - `core/llm/adapters/local_adapter.py`
  - 本地模型加载
  - 推理接口封装

#### 2.4 LLM功能增强
- [x] **Token精确计算** (P1) - 使用tiktoken库
  - GPT系列Token计算
  - Claude系列Token计算
  - 其他模型Token计算
  - 完成日期：2026-01-21
  - 说明：新增 `core/llm/utils/token_counter.py`，并将 `LLMService.calculate_tokens()` 升级为tiktoken精确计数
  
- [ ] **成本估算** (P2)
  - 调用成本计算
  - 成本统计和报告
  
- [x] **重试机制** (P1)
  - 指数退避重试
  - 自定义重试策略
  - 错误分类和处理
  - 完成日期：2026-01-21
  - 说明：已实现 `core/llm/utils/retry.py`，集成到LLMService
  
- [ ] **适配器健康检查** (P2)
  - 适配器可用性检查
  - 自动故障转移
  
- [ ] **适配器负载均衡** (P2)
  - 多适配器负载均衡
  - 智能路由选择

---

## 👁️ 第三阶段：视觉服务模块（Phase 3）

### ⏳ 未完成

#### 3.1 Vision服务核心
- [ ] **VisionService** (P1) - `core/vision/service.py`
  - 统一视觉服务接口
  - 图像生成
  - 图像分析
  - 图像编辑
  
- [ ] **Vision数据模型** (P1) - `core/vision/models.py`
  - 图像生成请求/响应
  - 图像分析请求/响应

#### 3.2 Vision适配器
- [ ] **DALL-E适配器** (P1) - `core/vision/adapters/dalle_adapter.py`
  - DALL-E 2/3支持
  - 图像生成API
  
- [ ] **Stable Diffusion适配器** (P2) - `core/vision/adapters/stable_diffusion_adapter.py`
  - Stable Diffusion API
  - 本地模型支持
  
- [ ] **图像分析适配器** (P2) - `core/vision/adapters/image_analysis_adapter.py`
  - OCR功能
  - 物体识别
  - 图像理解

---

## 🔊 第四阶段：音频服务模块（Phase 4）

### ⏳ 未完成

#### 4.1 Audio服务核心
- [ ] **AudioService** (P2) - `core/audio/service.py`
  - 统一音频服务接口
  - 语音转文字（STT）
  - 文字转语音（TTS）
  - 音频处理
  
- [ ] **Audio数据模型** (P2) - `core/audio/models.py`
  - STT请求/响应
  - TTS请求/响应

#### 4.2 Audio适配器
- [ ] **TTS适配器** (P2) - `core/audio/adapters/tts_adapter.py`
  - 文字转语音功能
  - 多提供商支持
  
- [ ] **STT适配器** (P2) - `core/audio/adapters/stt_adapter.py`
  - 语音转文字功能
  - 多提供商支持

---

## 🤖 第五阶段：Agent引擎（Phase 5）

### ✅ 已完成

#### 5.1 Agent引擎核心
- [x] **AgentEngine** (P1) - `core/agent/engine.py`
  - Agent主引擎
  - 任务执行
  - 工具调用
  - 完成日期：2026-01-21
  - 说明：已实现AgentEngine核心类，支持任务接收、LLM集成、工具调用循环
  
- [x] **工具系统** (P1) - `core/agent/tools.py`
  - 工具定义和管理
  - Function Calling支持
  - 工具注册机制
  - 完成日期：2026-01-21
  - 说明：已实现Tool和ToolRegistry，支持工具注册、执行和Function Calling schema生成
  
- [x] **记忆管理** (P1) - `core/agent/memory.py`
  - 短期记忆
  - 长期记忆
  - 记忆检索和存储
  - 完成日期：2026-01-21
  - 说明：已实现ShortTermMemory（基于ConversationContext）和LongTermMemory（基于StorageManager）
  
- [x] **工作流编排** (P2) - `core/agent/workflow.py`
  - 工作流定义
  - 步骤执行
  - 错误处理
  - 完成日期：2026-01-21
  - 说明：已实现基础工作流（线性步骤执行）

### ⏳ 未完成

#### 5.2 Agent路由
- [x] **Agent路由** (P1) - `api/routes/agent.py`
  - Agent任务接口
  - 工具注册接口
  - 完成日期：2026-01-21
  - 说明：已实现Agent任务执行接口、工具注册接口、工具列表接口，并集成到FastAPI

- [ ] **任务规划器** (P2) - `core/agent/planner.py`
  - 任务分解
  - 步骤规划
  - 执行顺序优化

---

## 🌐 第六阶段：应用层接口（Phase 6）

### ⏳ 未完成

#### 6.1 API接口层
- [x] **FastAPI应用** (P1) - `api/fastapi_app.py`
  - FastAPI应用初始化
  - 中间件配置
  - CORS支持
  - 认证中间件（可选）
  - 完成日期：2026-01-21
  
- [x] **LLM路由** (P1) - `api/routes/llm.py`
  - 聊天接口
  - 流式聊天接口
  - 模型列表接口
  - 完成日期：2026-01-21
  
- [ ] **Vision路由** (P2) - `api/routes/vision.py`
  - 图像生成接口
  - 图像分析接口
  
- [ ] **Audio路由** (P2) - `api/routes/audio.py`
  - TTS接口
  - STT接口
  
- [ ] **Agent路由** (P1) - `api/routes/agent.py`
  - Agent任务接口
  - 工具注册接口
  
- [x] **健康检查路由** (P1) - `api/routes/health.py`
  - 健康检查接口
  - 服务状态接口
  - 完成日期：2026-01-21
  
- [x] **API依赖注入** (P1) - `api/dependencies.py`
  - 服务依赖注入
  - 配置管理器依赖
  - 完成日期：2026-01-21
  
- [x] **API中间件** (P1) - `api/middleware.py`
  - 请求日志中间件
  - 错误处理中间件
  - CORS中间件
  - 完成日期：2026-01-21

#### 6.2 CLI工具
- [x] **CLI入口** (P1) - `cli/main.py`
  - 命令定义
  - 参数解析
  - 完成日期：2026-01-21
  
- [x] **聊天命令** (P1) - `cli/commands/chat.py`
  - 交互式聊天
  - 单次对话
  - 完成日期：2026-01-21
  
- [ ] **配置命令** (P2) - `cli/commands/config.py`
  - 配置查看
  - 配置设置
  
- [ ] **插件管理命令** (P2) - `cli/commands/plugin.py`
  - 插件列表
  - 插件安装/卸载

#### 6.3 Web界面
- [ ] **Web应用** (P2) - `web/app.py`
  - 主应用入口
  - 页面路由
  
- [ ] **聊天页面** (P2) - `web/pages/chat.py`
  - 聊天界面
  - 消息显示
  - 输入框
  
- [ ] **配置页面** (P3) - `web/pages/config.py`
  - 配置管理界面
  
- [ ] **插件管理页面** (P3) - `web/pages/plugins.py`
  - 插件列表
  - 插件管理界面

---

## 🔌 第七阶段：插件系统（Phase 7）

### ⏳ 未完成

#### 7.1 插件框架
- [ ] **插件管理器** (P2) - `core/base/plugin_manager.py`
  - 插件加载
  - 插件注册
  - 插件执行
  
- [ ] **插件发现机制** (P2)
  - 自动发现插件
  - 插件元数据读取
  
- [ ] **插件生命周期管理** (P2)
  - 插件初始化
  - 插件清理
  - 插件依赖解析

#### 7.2 示例插件
- [ ] **工具插件示例** (P3) - `plugins/examples/tool_plugin.py`
  
- [ ] **适配器插件示例** (P3) - `plugins/examples/adapter_plugin.py`
  
- [ ] **存储插件示例** (P3) - `plugins/examples/storage_plugin.py`

---

## 🧪 第八阶段：测试和文档（Phase 8）

### ✅ 已完成

#### 8.1 单元测试
- [x] **基础模块测试** (P0)
  - BaseService测试
  - BaseAdapter测试
  - BasePlugin测试
  
- [x] **LLM服务测试** (P0)
  - LLMService测试
  - ConversationContext测试
  - 适配器测试
  - 自动注册机制测试
  
- [x] **基础设施测试** (P0)
  - ConfigManager测试
  - LogManager测试

#### 8.2 集成测试
- [x] **LLM服务集成测试** (P1)
  - 服务与配置管理器集成
  - 完整聊天流程
  
- [x] **配置服务集成测试** (P1)

#### 8.3 端到端测试
- [x] **完整聊天流程测试** (P1)

### ⏳ 未完成

#### 8.4 测试完善
- [ ] **提高测试覆盖率到80%+** (P1)
  - 适配器测试覆盖率提升
  - 配置加载器测试覆盖率提升
  
- [ ] **性能测试** (P2)
  - 响应时间测试
  - 并发压力测试
  - 内存泄漏检测
  
- [ ] **真实API集成测试** (P3) - 可选
  - 使用真实API密钥的集成测试
  - 需要保护API密钥安全

#### 8.5 文档完善
- [ ] **API文档** (P1) - `docs/api/api-reference.md`
  - 完整的API参考文档
  - 请求/响应示例
  
- [ ] **快速开始指南** (P1) - `docs/guides/getting-started.md`
  - 安装步骤
  - 快速示例
  
- [ ] **使用教程** (P2) - `docs/tutorials/`
  - 基础使用教程
  - 高级功能教程
  
- [ ] **示例代码** (P2) - `examples/`
  - 基础示例
  - 高级示例
  - 集成示例

---

## 🔒 第九阶段：安全和性能优化（Phase 9）

### ⏳ 未完成

#### 9.1 安全功能
- [ ] **API密钥加密存储** (P1)
  - 密钥加密
  - 密钥轮换机制
  
- [ ] **敏感数据脱敏** (P1)
  - 日志脱敏
  - 错误信息脱敏
  
- [ ] **API认证** (P2) - 可选
  - API密钥认证
  - Token认证
  
- [ ] **请求限流** (P2)
  - 限流策略
  - 限流中间件

#### 9.2 性能优化
- [x] **连接池管理** (P1) - `infrastructure/storage/connection_pool.py`
  - HTTP连接池
  - 数据库连接池
  - 完成日期：2026-01-21
  - 说明：已实现ConnectionPoolManager，支持HTTP和数据库连接池管理
  
- [ ] **请求批处理** (P2)
  - 批量请求优化
  
- [ ] **资源监控** (P2)
  - 内存使用监控
  - 连接数监控

---

## 🚀 第十阶段：部署和运维（Phase 10）

### ⏳ 未完成

#### 10.1 部署配置
- [ ] **Docker配置** (P2) - `Dockerfile`
  - Docker镜像构建
  - docker-compose配置
  
- [ ] **部署文档** (P2) - `docs/deployment/`
  - 部署指南
  - 环境配置

#### 10.2 监控和日志
- [ ] **监控指标** (P3)
  - 性能指标
  - 错误率统计
  
- [ ] **日志收集** (P2)
  - 日志聚合
  - 日志查询

---

## 📋 需求清单汇总

### 按优先级汇总

#### P0（关键）- 必须完成
- [x] 基础服务框架（BaseService、BaseAdapter、BasePlugin）
- [x] 配置管理模块（ConfigManager、ConfigLoader、ConfigValidator）
- [x] 日志管理模块（LogManager）
- [x] LLM服务核心（LLMService、ConversationContext、Models）
- [x] 基础LLM适配器（BaseLLMAdapter、豆包、千问、DeepSeek）
- [x] 适配器自动发现和注册
- [x] 单元测试框架
- [x] 集成测试框架
- [x] 端到端测试框架

#### P1（高优先级）- 重要功能
- [x] 缓存管理模块（CacheManager）
- [x] 存储管理模块（StorageManager）
- [x] OpenAI适配器
- [x] Claude适配器
- [x] Ollama适配器
- [x] Token精确计算
- [x] 重试机制
- [ ] Vision服务核心
- [x] Agent引擎核心
- [x] FastAPI应用和路由
- [x] CLI工具
- [ ] API文档
- [ ] 快速开始指南
- [ ] API密钥加密存储
- [x] 连接池管理

#### P2（中优先级）- 逐步完善
- [ ] Redis缓存后端
- [ ] 向量数据库
- [ ] 成本估算
- [ ] 适配器健康检查
- [ ] 适配器负载均衡
- [ ] Vision适配器（DALL-E、Stable Diffusion）
- [ ] Audio服务核心
- [ ] 任务规划器
- [ ] 工作流编排
- [ ] Vision/Audio路由
- [ ] Web界面
- [ ] 插件框架
- [ ] 使用教程
- [ ] 示例代码
- [ ] 性能测试
- [ ] 请求限流
- [ ] 请求批处理
- [ ] 部署配置

#### P3（低优先级）- 可选功能
- [ ] 真实API集成测试
- [ ] 插件示例
- [ ] 监控指标
- [ ] 其他可选功能

---

## 📈 完成度统计

### 按模块统计

| 模块 | 完成度 | 已完成 | 总数 |
|------|--------|--------|------|
| 基础框架 | 100% | 3 | 3 |
| 配置管理 | 100% | 3 | 3 |
| 日志管理 | 100% | 1 | 1 |
| 缓存管理 | 50% | 2 | 4 |
| 存储管理 | 75% | 3 | 4 |
| LLM服务 | 70% | 7 | 10 |
| Vision服务 | 0% | 0 | 5 |
| Audio服务 | 0% | 0 | 3 |
| Agent引擎 | 80% | 4 | 5 |
| API接口 | 0% | 0 | 8 |
| CLI工具 | 67% | 2 | 3 |
| Web界面 | 0% | 0 | 3 |
| 插件系统 | 0% | 0 | 3 |
| 测试和文档 | 50% | 6 | 12 |
| 安全和性能 | 14% | 1 | 7 |
| 部署和运维 | 0% | 0 | 4 |

### 总体统计

- **P0需求**：9/9 (100%) ✅
- **P1需求**：18/16 (112%) ✅
- **P2需求**：0/22 (0%)
- **P3需求**：0/4 (0%)
- **总计**：31/51 (61%)

---

## 🔄 更新规则（硬性规则）

### 必须更新本文档的情况

1. ✅ **完成新功能**：必须标记为已完成
2. ✅ **开始新功能**：必须标记为进行中
3. ✅ **取消功能**：必须标记为已取消并说明原因
4. ✅ **修改优先级**：必须更新优先级标记
5. ✅ **新增需求**：必须添加到对应阶段和优先级

### 更新流程

```
1. 开发功能
   ↓
2. 完成功能（代码+测试+文档）
   ↓
3. 更新本文档（标记为已完成）
   ↓
4. 更新CHANGELOG.md
   ↓
5. 提交代码和文档
```

### 更新格式

```markdown
- [x] **功能名称** (优先级) - `文件路径`
  - 完成日期：YYYY-MM-DD
  - 说明：功能描述
```

---

## 📝 最近更新记录

| 日期 | 更新内容 | 更新人 |
|------|---------|--------|
| 2026-01-21 | 创建项目计划文档，标记已完成功能 | - |
| 2026-01-21 | 完成LLM服务模块和适配器实现 | - |
| 2026-01-21 | 完成测试体系（单元测试、集成测试、端到端测试） | - |
| 2026-01-21 | 完成OpenAI适配器、重试机制、FastAPI应用和路由实现 | - |
| 2026-01-21 | 完成Token精确计算（tiktoken）、缓存管理模块（Memory后端）、CLI聊天工具 | - |
| 2026-01-21 | 完成存储管理模块（StorageManager、Database存储、文件存储）和连接池管理 | - |
| 2026-01-21 | 完成Agent引擎核心（AgentEngine、工具系统、记忆管理、工作流）和Agent路由 | - |

---

## 🎯 下一步计划

### 短期目标（1-2周）

1. **提高测试覆盖率到80%+** (P1)
2. **实现缓存管理模块** (P1)
3. **实现OpenAI适配器** (P1)
4. **完善API文档** (P1)

### 中期目标（1个月）

1. **实现存储管理模块** (P1)
2. **实现Agent引擎核心功能** (P1)
3. **实现FastAPI应用和路由** (P1)
4. **实现CLI工具** (P1)

### 长期目标（3个月）

1. **完成Vision服务模块** (P1)
2. **完成Audio服务模块** (P2)
3. **完成插件系统** (P2)
4. **完善安全和性能优化** (P1-P2)

---

## 📚 相关文档

- [架构方案文档](../AI框架架构方案文档.md) - 架构设计参考
- [开发规则文档](../AI框架开发规则文档.md) - 开发规范参考
- [代码规范](.cursor/rules/CodeStandards.mdc) - 代码规范
- [项目规则](.cursor/rules/ProjectRules.mdc) - 项目规则
- [文档规范](.cursor/rules/Documentation.mdc) - 文档规范
- [CHANGELOG](../CHANGELOG.md) - 变更日志

---

## ⚠️ 重要提醒

1. **硬性规则**：完成功能时必须同步更新本文档
2. **优先级**：优先完成P0和P1需求
3. **文档同步**：功能变更必须更新本文档和CHANGELOG.md
4. **状态透明**：清楚标记每个功能的状态

---

**说明**：本文档是项目进度和需求状态的唯一权威来源，所有开发者和AI助手都应该遵循本文档的规则。
