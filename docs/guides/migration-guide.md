# 迁移指南：从v1.0到v2.0

本文档帮助用户从AI框架v1.0迁移到v2.0，包括配置迁移、API变更和最佳实践。

## 版本对比

### v1.0特性
- 基础LLM服务，支持多种适配器
- 简单的配置管理
- 基础的缓存和日志功能

### v2.0新增特性
- 智能路由和负载均衡
- 性能优化（连接池、缓存、去重、批量处理）
- 成本管理和预算控制
- 监控和可观测性（Prometheus指标、请求追踪）
- 主流框架集成（LiteLLM、LangChain、LangGraph，可选）

## 迁移步骤

### 步骤1：备份现有配置

```bash
# 备份配置文件
cp config/dev.yaml config/dev.yaml.backup
cp config/prod.yaml config/prod.yaml.backup
```

### 步骤2：自动配置迁移

v2.0提供了自动配置迁移工具，会自动将v1.0配置升级到v2.0格式：

```python
from infrastructure.config import ConfigManager

# 加载配置（自动迁移）
config_manager = ConfigManager.load(env="dev")
config = config_manager.get_all()

# 验证迁移结果
print(f"配置版本: {config.get('config_version', '1.0')}")
```

**迁移内容**：
- 自动添加 `config_version: "2.0"`
- 自动添加新架构的默认配置项（路由、性能、成本、监控）
- 保持所有现有配置项不变

### 步骤3：验证兼容性

运行兼容性测试确保迁移成功：

```bash
# 运行兼容性测试
pytest tests/compatibility/test_backward_compatibility.py -v
```

### 步骤4：逐步启用新功能（可选）

#### 4.1 启用智能路由

```yaml
llm:
  enable_routing: true  # 启用路由层
  default_routing_strategy: "balanced"  # 或 "cost_first", "performance_first"
```

#### 4.2 启用性能优化

```yaml
llm:
  performance:
    enable_connection_pool: true  # 启用连接池
    enable_cache: true  # 启用请求缓存
    enable_deduplication: true  # 启用请求去重
```

#### 4.3 启用成本管理

```yaml
llm:
  cost:
    enabled: true  # 启用成本管理
    daily_budget: 10.0  # 每日预算（美元）
    monthly_budget: 300.0  # 每月预算（美元）
```

#### 4.4 启用监控

```yaml
llm:
  monitoring:
    enabled: true  # 启用监控
    tracing_enabled: true  # 启用请求追踪
```

## 配置迁移示例

### v1.0配置

```yaml
llm:
  default_model: "qwen-turbo"
  timeout: 30
  max_retries: 3
  adapters:
    qwen-adapter:
      api_key: "your-api-key"
```

### v2.0配置（自动迁移后）

```yaml
config_version: "2.0"  # 自动添加

llm:
  default_model: "qwen-turbo"
  timeout: 30
  max_retries: 3
  adapters:
    qwen-adapter:
      api_key: "your-api-key"
  
  # 自动添加的新配置项（使用默认值）
  enable_routing: false
  default_routing_strategy: "balanced"
  performance:
    enable_connection_pool: true
    enable_cache: true
    enable_deduplication: true
  cost:
    enabled: false
  monitoring:
    enabled: true
```

## API变更

### 向后兼容的API

所有现有API调用方式保持不变：

```python
# v1.0和v2.0都支持
response = await service.chat(messages, model="qwen-turbo")
```

### 新增API功能

#### 1. 路由策略参数

```python
# v2.0新增：支持路由策略
from core.llm.models import RoutingStrategy

response = await service.chat(
    messages,
    model="qwen-turbo",
    routing_strategy=RoutingStrategy.COST_FIRST  # 成本优先
)
```

#### 2. 成本统计API

```python
# v2.0新增：获取成本统计
stats = await service.get_cost_statistics()
print(f"总成本: ${stats['total_cost']:.2f}")
print(f"总Token: {stats['total_tokens']}")
```

#### 3. 模型能力查询

```python
# v2.0新增：查询模型能力
capabilities = await service.get_model_capabilities("qwen-turbo")
print(f"支持推理: {capabilities.reasoning}")
print(f"支持函数调用: {capabilities.function_calling}")
```

## 代码迁移示例

### 示例1：基础使用（无需修改）

```python
# v1.0代码，v2.0完全兼容
import asyncio
from infrastructure.config import ConfigManager
from core.llm.service import LLMService

async def main():
    config_manager = ConfigManager.load(env="dev")
    config = config_manager.get_all()
    
    service = LLMService(config)
    await service.initialize()
    
    messages = [{"role": "user", "content": "你好"}]
    response = await service.chat(messages)
    
    print(response.content)
    await service.cleanup()

asyncio.run(main())
```

### 示例2：使用新功能（可选）

```python
# v2.0新增功能使用示例
import asyncio
from infrastructure.config import ConfigManager
from core.llm.service import LLMService
from core.llm.models import RoutingStrategy

async def main():
    config_manager = ConfigManager.load(env="dev")
    config = config_manager.get_all()
    
    service = LLMService(config)
    await service.initialize()
    
    # 使用成本优先路由
    messages = [{"role": "user", "content": "你好"}]
    response = await service.chat(
        messages,
        routing_strategy=RoutingStrategy.COST_FIRST
    )
    
    # 获取成本统计
    stats = await service.get_cost_statistics()
    print(f"本次请求成本: ${stats['total_cost']:.2f}")
    
    await service.cleanup()

asyncio.run(main())
```

## 常见问题

### Q1: 迁移后性能会下降吗？

**A**: 不会。v2.0在保持向后兼容的同时，提供了性能优化功能。如果启用性能优化（连接池、缓存等），性能会显著提升。

### Q2: 必须使用新功能吗？

**A**: 不需要。所有新功能都是可选的，可以通过配置启用/禁用。默认情况下，新功能都是禁用的，保持与v1.0相同的行为。

### Q3: 如何回退到v1.0？

**A**: 如果遇到问题，可以：
1. 恢复备份的配置文件
2. 在配置中禁用所有新功能：
   ```yaml
   llm:
     enable_routing: false
     performance:
       enable_connection_pool: false
       enable_cache: false
     cost:
       enabled: false
     monitoring:
       enabled: false
   ```

### Q4: 配置迁移失败怎么办？

**A**: 
1. 检查配置文件格式是否正确
2. 查看日志文件了解详细错误信息
3. 手动迁移配置（参考配置迁移示例）

### Q5: 新功能会增加依赖吗？

**A**: 
- **核心功能**：无新增依赖，保持轻量级
- **可选功能**：
  - Prometheus监控：需要 `prometheus-client`（已在requirements.txt中）
  - LiteLLM集成：需要 `litellm`（可选，注释状态）
  - LangChain集成：需要 `langchain`（可选，注释状态）
  - LangGraph集成：需要 `langgraph`（可选，注释状态）

## 迁移检查清单

- [ ] 备份现有配置文件
- [ ] 运行自动配置迁移
- [ ] 验证配置版本为2.0
- [ ] 运行兼容性测试
- [ ] 验证现有功能正常工作
- [ ] （可选）逐步启用新功能
- [ ] （可选）更新代码以使用新API
- [ ] 查看监控指标（如果启用）
- [ ] 查看成本统计（如果启用）

## 获取帮助

如果迁移过程中遇到问题：

1. 查看[配置文档](configuration.md)了解详细配置说明
2. 查看[API文档](../api/api-reference.md)了解新API
3. 查看[架构文档](../architecture/refactored-architecture.md)了解新架构
4. 提交Issue获取帮助

## 下一步

迁移完成后，建议：

1. 阅读[性能优化指南](performance-optimization.md)了解如何优化性能
2. 阅读[成本管理指南](cost-management.md)了解如何控制成本
3. 查看[快速参考](quick-reference.md)了解常用功能
