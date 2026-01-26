# 配置管理指南

本文档介绍AI框架的配置管理功能，包括配置结构、环境配置、配置迁移和验证。

## 配置版本

当前配置版本：**2.0**

### 版本历史

- **v1.0**: 基础配置，包含LLM、缓存、日志、存储等基础功能
- **v2.0**: 新增路由、性能优化、成本管理、监控等新架构功能

## 配置文件结构

### 主配置文件

配置文件位于 `config/` 目录：

- `default.yaml` - 默认配置（所有环境的基础配置）
- `dev.yaml` - 开发环境配置（覆盖默认配置）
- `prod.yaml` - 生产环境配置（覆盖默认配置）

### 配置加载顺序

1. 加载 `default.yaml`（基础配置）
2. 加载环境配置文件（`{env}.yaml`，覆盖默认配置）
3. 应用环境变量（覆盖文件配置）

## 配置项说明

### LLM服务配置

```yaml
llm:
  # 基础配置
  api_key: ""  # API密钥（支持加密存储）
  timeout: 30  # 请求超时时间（秒）
  max_retries: 3  # 最大重试次数
  default_model: "qwen-turbo"  # 默认模型
  auto_discover_adapters: true  # 是否自动发现适配器
  
  # 路由配置（v2.0新增）
  enable_routing: false  # 是否启用适配器路由层
  default_routing_strategy: "balanced"  # 默认路由策略
  
  # 性能优化配置（v2.0新增）
  performance:
    enable_connection_pool: true  # 是否启用HTTP连接池
    max_connections: 100  # 最大连接数
    enable_cache: true  # 是否启用请求缓存
    cache_ttl: 3600.0  # 缓存生存时间（秒）
    enable_deduplication: true  # 是否启用请求去重
  
  # 成本管理配置（v2.0新增）
  cost:
    enabled: true  # 是否启用成本管理
    daily_budget: 0.0  # 每日预算（美元）
    monthly_budget: 0.0  # 每月预算（美元）
    alert_threshold: 0.8  # 告警阈值
    budget_enabled: false  # 是否启用预算管理
  
  # 监控配置（v2.0新增）
  monitoring:
    enabled: true  # 是否启用监控
    tracing_enabled: true  # 是否启用请求追踪
    tracing:
      max_traces: 1000  # 最大追踪数
      trace_ttl: 3600  # 追踪TTL（秒）
  
  # 适配器配置
  adapters:
    openai-adapter:
      api_key: ""
      base_url: "https://api.openai.com/v1"
    # ... 其他适配器配置
  
  # 实现选择（v2.0新增）
  implementation: "native"  # 实现类型：native/litellm/langchain
```

### Agent配置

```yaml
agent:
  # 基础配置
  implementation: "native"  # 实现类型：native/langchain/langgraph
  max_iterations: 10  # 最大迭代次数
  timeout: 300  # Agent任务超时时间（秒）
  enable_long_term_memory: false  # 是否启用长期记忆
  enable_planner: false  # 是否启用任务规划器
  max_messages: null  # 最大消息数（null表示无限制）
  
  # LangChain配置（当implementation为langchain时生效）
  agent_type: "openai-functions"  # Agent类型：openai-functions/openai-multi-functions/react/self-ask-with-search
  verbose: false  # 是否输出详细日志
  return_intermediate_steps: true  # 是否返回中间步骤（工具调用信息）
```

### 工具配置

```yaml
tools:
  implementation: "native"  # 实现类型：native/langchain
```

### 记忆配置

```yaml
memory:
  implementation: "native"  # 实现类型：native/langchain
  type: "buffer"  # 记忆类型：buffer/summary（LangChain实现时生效）
```

### 路由策略

支持以下路由策略：

- `cost_first` - 成本优先：选择成本最低的适配器
- `performance_first` - 性能优先：选择延迟最低的适配器
- `availability_first` - 可用性优先：选择最健康的适配器
- `balanced` - 平衡模式：综合考虑成本、性能和可用性（默认）
- `manual` - 手动模式：使用指定的适配器

### 性能优化配置

性能优化功能包括：

- **HTTP连接池**：复用HTTP连接，提高性能
- **请求缓存**：缓存相同请求的响应，减少API调用
- **请求去重**：合并相同的并发请求
- **批量处理**：批量处理请求，提高吞吐量

### 成本管理配置

成本管理功能包括：

- **Token使用统计**：记录每次请求的Token使用量
- **成本计算**：自动计算每次请求的成本
- **预算管理**：设置每日/每月预算，超出时告警
- **优化建议**：提供成本优化建议

### 监控配置

监控功能包括：

- **Prometheus指标**：QPS、延迟、成功率、Token使用、成本等
- **请求追踪**：分布式追踪和请求链路分析
- **监控API**：提供 `/api/metrics` 端点查询指标

## 配置迁移

### 自动迁移

配置管理器支持自动检测和迁移旧版本配置：

```python
from infrastructure.config.manager import ConfigManager
from infrastructure.config.migrator import ConfigMigrator

# 自动迁移配置
migrator = ConfigMigrator()
migrated_config = migrator.migrate_config_file("config/default.yaml", backup=True)
```

### 手动迁移

如果需要手动迁移配置：

1. **备份原配置文件**
   ```bash
   cp config/default.yaml config/default.yaml.backup
   ```

2. **运行迁移工具**
   ```python
   from infrastructure.config.migrator import ConfigMigrator
   
   migrator = ConfigMigrator()
   config = migrator.migrate_config_file("config/default.yaml")
   ```

3. **验证迁移结果**
   ```python
   from infrastructure.config.validator import ConfigValidator
   
   validator = ConfigValidator()
   errors = validator.validate(config)
   if errors:
       print("配置验证失败:", errors)
   ```

## 配置验证

### 验证配置

```python
from infrastructure.config.manager import ConfigManager
from infrastructure.config.validator import ConfigValidator

# 加载配置
config_manager = ConfigManager.load()

# 验证配置
validator = ConfigValidator()
errors = validator.validate(config_manager.config, auto_migrate=True)

if errors:
    print("配置验证失败:")
    for error in errors:
        print(f"  - {error}")
else:
    print("配置验证通过")
```

### 验证规则

配置验证器会检查：

- 必需配置项是否存在
- 配置项类型是否正确
- 配置项取值范围是否合理
- 配置项之间的依赖关系
- 新架构配置项的兼容性

## 环境变量覆盖

支持通过环境变量覆盖配置值：

```bash
# 设置API密钥
export LLM_API_KEY="sk-xxx"

# 设置默认模型
export LLM_DEFAULT_MODEL="gpt-4"

# 设置路由策略
export LLM_DEFAULT_ROUTING_STRATEGY="cost_first"
```

环境变量命名规则：`{SECTION}_{KEY}`，使用大写字母和下划线。

## 加密配置

敏感配置项（如API密钥）支持加密存储：

```yaml
llm:
  api_key: "encrypted:salt:iv:ciphertext:tag"
```

使用 `ConfigManager.encrypt_value()` 方法生成加密值：

```python
from infrastructure.config.manager import ConfigManager

config_manager = ConfigManager.load()
encrypted_value = config_manager.encrypt_value("sk-xxx")
print(encrypted_value)  # encrypted:...
```

## 配置热重载

配置管理器支持热重载（需要手动触发）：

```python
from infrastructure.config.manager import ConfigManager

config_manager = ConfigManager.load()

# 重新加载配置
config_manager.reload()
```

## 常见问题

### Q: 如何启用路由功能？

A: 在配置文件中设置：
```yaml
llm:
  enable_routing: true
  default_routing_strategy: "balanced"
```

### Q: 如何启用成本管理？

A: 成本管理默认启用，如需配置预算：
```yaml
llm:
  cost:
    enabled: true
    budget_enabled: true
    daily_budget: 10.0  # 每日预算$10
    monthly_budget: 300.0  # 每月预算$300
```

### Q: 如何启用监控？

A: 监控默认启用，可通过配置调整：
```yaml
llm:
  monitoring:
    enabled: true
    tracing_enabled: true
    tracing:
      max_traces: 1000
      trace_ttl: 3600
```

### Q: 如何从v1.0迁移到v2.0？

A: 使用配置迁移工具：
```python
from infrastructure.config.migrator import ConfigMigrator

migrator = ConfigMigrator()
migrator.migrate_config_file("config/default.yaml", backup=True)
```

## 相关文档

- [架构设计文档](../architecture/architecture-overview.md)
- [API文档](../api/api-reference.md)
- [性能优化指南](../guides/performance-optimization.md)
- [成本管理指南](../guides/cost-management.md)
