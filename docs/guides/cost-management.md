# 成本管理指南

本文档介绍AI框架的成本管理功能，帮助用户跟踪、控制和优化LLM API调用成本。

## 成本管理功能概览

v2.0引入了完整的成本管理功能：

1. **Token使用跟踪**：自动跟踪每次请求的Token使用情况
2. **成本计算**：根据模型定价自动计算成本
3. **预算管理**：支持每日和每月预算设置
4. **成本告警**：预算超限时自动告警
5. **优化建议**：提供成本优化建议

## 启用成本管理

### 配置成本管理

在配置文件中启用成本管理：

```yaml
llm:
  cost:
    enabled: true  # 启用成本管理
    daily_budget: 10.0  # 每日预算（美元）
    monthly_budget: 300.0  # 每月预算（美元）
    alert_threshold: 0.8  # 告警阈值（80%）
```

### 代码中使用

```python
from infrastructure.config import ConfigManager
from core.llm.service import LLMService

# 加载配置
config_manager = ConfigManager.load(env="dev")
config = config_manager.get_all()

# 创建服务（成本管理自动启用）
service = LLMService(config)
await service.initialize()

# 正常使用，成本会自动跟踪
messages = [{"role": "user", "content": "你好"}]
response = await service.chat(messages)

# 获取成本统计
stats = await service.get_cost_statistics()
print(f"总成本: ${stats['total_cost']:.2f}")
print(f"总Token: {stats['total_tokens']}")
```

## 成本跟踪

### 自动跟踪

成本管理器会自动跟踪每次请求：

- **Token使用**：输入Token、输出Token、总Token
- **成本计算**：根据模型定价自动计算
- **请求统计**：按适配器、模型、时间统计

### 查看成本统计

#### 1. 通过代码查询

```python
# 获取总体统计
stats = await service.get_cost_statistics()
print(f"总成本: ${stats['total_cost']:.2f}")
print(f"总Token: {stats['total_tokens']}")
print(f"请求数: {stats['request_count']}")

# 按适配器统计
print(f"OpenAI成本: ${stats['adapter_stats']['openai-adapter']['total_cost']:.2f}")

# 按模型统计
print(f"GPT-4成本: ${stats['model_stats']['gpt-4']['total_cost']:.2f}")
```

#### 2. 通过API查询

```bash
# 获取成本统计
curl http://localhost:8000/api/v1/llm/cost/stats

# 响应示例
{
  "total_cost": 12.34,
  "total_tokens": 123456,
  "request_count": 100,
  "adapter_stats": {
    "openai-adapter": {
      "total_cost": 10.00,
      "total_tokens": 100000,
      "request_count": 50
    }
  },
  "model_stats": {
    "gpt-4": {
      "total_cost": 8.00,
      "total_tokens": 80000,
      "request_count": 40
    }
  }
}
```

#### 3. 通过监控指标

启用监控后，可以通过Prometheus指标查看成本：

```bash
# 查看Prometheus指标
curl http://localhost:8000/api/metrics | grep llm_cost
```

## 预算管理

### 设置预算

```yaml
llm:
  cost:
    enabled: true
    daily_budget: 10.0  # 每日预算10美元
    monthly_budget: 300.0  # 每月预算300美元
    alert_threshold: 0.8  # 达到80%时告警
```

### 预算告警

当成本达到告警阈值时，系统会：

1. **记录警告日志**：在日志中记录预算警告
2. **返回告警信息**：在API响应中包含告警信息
3. **（可选）发送通知**：可以集成通知系统发送告警

### 代码中检查预算

```python
# 获取成本统计
stats = await service.get_cost_statistics()

# 检查预算
if stats['daily_cost'] >= stats['daily_budget'] * 0.8:
    print("⚠️ 每日预算已达到80%，请注意控制成本")

if stats['monthly_cost'] >= stats['monthly_budget'] * 0.8:
    print("⚠️ 每月预算已达到80%，请注意控制成本")
```

## 成本优化建议

### 获取优化建议

```python
# 获取成本优化建议
suggestions = await service.get_cost_optimization_suggestions([])

for suggestion in suggestions:
    print(f"建议: {suggestion['message']}")
    print(f"预期节省: ${suggestion['potential_savings']:.2f}")
```

### 优化建议类型

1. **模型替换建议**：推荐使用成本更低的模型
2. **缓存使用建议**：建议启用缓存减少重复请求
3. **批量处理建议**：建议使用批量处理提高效率
4. **Token优化建议**：建议优化提示词减少Token使用

### 优化策略

#### 1. 使用成本优先路由

```python
from core.llm.models import RoutingStrategy

# 使用成本优先路由，自动选择成本最低的模型
response = await service.chat(
    messages,
    routing_strategy=RoutingStrategy.COST_FIRST
)
```

#### 2. 启用请求缓存

```yaml
llm:
  performance:
    enable_cache: true  # 启用缓存，减少重复请求
    cache_ttl: 3600.0
```

#### 3. 选择合适的模型

```python
# 对于简单任务，使用成本更低的模型
simple_messages = [{"role": "user", "content": "简单问题"}]
response = await service.chat(simple_messages, model="gpt-3.5-turbo")  # 更便宜

# 对于复杂任务，使用能力更强的模型
complex_messages = [{"role": "user", "content": "复杂问题"}]
response = await service.chat(complex_messages, model="gpt-4")  # 更贵但能力更强
```

#### 4. 优化提示词

- 减少不必要的上下文
- 使用更简洁的提示词
- 避免重复内容

## 成本分析

### 按时间分析

```python
# 获取指定时间范围的成本统计
from datetime import datetime, timedelta

end_time = datetime.now()
start_time = end_time - timedelta(days=7)  # 最近7天

stats = await service.get_cost_statistics(
    start_time=start_time,
    end_time=end_time
)
```

### 按适配器分析

```python
# 获取按适配器的成本统计
stats = await service.get_cost_statistics()

for adapter, adapter_stats in stats['adapter_stats'].items():
    print(f"{adapter}:")
    print(f"  成本: ${adapter_stats['total_cost']:.2f}")
    print(f"  Token: {adapter_stats['total_tokens']}")
    print(f"  请求数: {adapter_stats['request_count']}")
```

### 按模型分析

```python
# 获取按模型的成本统计
stats = await service.get_cost_statistics()

for model, model_stats in stats['model_stats'].items():
    print(f"{model}:")
    print(f"  成本: ${model_stats['total_cost']:.2f}")
    print(f"  Token: {model_stats['total_tokens']}")
    print(f"  请求数: {model_stats['request_count']}")
    print(f"  平均成本/请求: ${model_stats['total_cost'] / model_stats['request_count']:.4f}")
```

## 成本控制

### 1. 设置预算限制

```yaml
llm:
  cost:
    daily_budget: 10.0  # 每日最多10美元
    monthly_budget: 300.0  # 每月最多300美元
```

### 2. 监控成本趋势

定期查看成本统计，了解成本趋势：

```python
# 每日检查成本
daily_stats = await service.get_cost_statistics()
print(f"今日成本: ${daily_stats['daily_cost']:.2f}")
print(f"今日预算: ${daily_stats['daily_budget']:.2f}")
print(f"预算使用率: {daily_stats['daily_cost'] / daily_stats['daily_budget'] * 100:.1f}%")
```

### 3. 自动成本控制（未来功能）

未来版本可能支持：
- 达到预算时自动停止请求
- 自动切换到成本更低的模型
- 自动启用缓存和去重

## 成本报告

### 生成成本报告

```python
# 获取详细成本报告
stats = await service.get_cost_statistics()

# 生成报告
report = f"""
成本报告
========
总成本: ${stats['total_cost']:.2f}
总Token: {stats['total_tokens']:,}
请求数: {stats['request_count']}

按适配器:
"""
for adapter, adapter_stats in stats['adapter_stats'].items():
    report += f"  {adapter}: ${adapter_stats['total_cost']:.2f}\n"

print(report)
```

### 导出成本数据

```python
# 导出为JSON
import json

stats = await service.get_cost_statistics()
with open('cost_report.json', 'w') as f:
    json.dump(stats, f, indent=2)
```

## 最佳实践

1. **设置合理预算**：根据实际需求设置每日和每月预算
2. **定期查看统计**：定期查看成本统计，了解使用情况
3. **使用成本优先路由**：对于非关键任务，使用成本优先路由
4. **启用缓存**：启用请求缓存减少重复请求
5. **优化提示词**：减少不必要的Token使用
6. **选择合适的模型**：根据任务复杂度选择合适的模型
7. **监控告警**：设置告警阈值，及时发现问题

## 常见问题

### Q1: 成本计算准确吗？

**A**: 成本计算基于模型官方定价，但实际成本可能因以下因素有所不同：
- 模型定价可能变化
- 某些模型可能有折扣
- 实际Token计算可能有差异

建议定期核对实际账单。

### Q2: 如何减少成本？

**A**: 
1. 使用成本优先路由
2. 启用请求缓存
3. 优化提示词减少Token
4. 选择合适的模型（简单任务用便宜模型）
5. 使用批量处理提高效率

### Q3: 预算超限会怎样？

**A**: 当前版本只提供告警，不会自动停止请求。未来版本可能支持自动停止。

### Q4: 如何查看历史成本？

**A**: 成本记录存储在内存中，重启后会清空。未来版本可能支持持久化存储。

## 相关文档

- [配置文档](configuration.md) - 成本管理配置说明
- [性能优化指南](performance-optimization.md) - 性能优化相关
- [API文档](../api/api-reference.md) - 成本管理API说明
