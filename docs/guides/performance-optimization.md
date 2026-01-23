# 性能优化指南

本文档介绍AI框架的性能优化功能和使用方法，帮助用户提升应用性能。

## 性能优化功能概览

v2.0引入了以下性能优化功能：

1. **HTTP连接池**：复用HTTP连接，减少连接建立开销
2. **请求缓存**：缓存相同请求的结果，避免重复API调用
3. **请求去重**：合并并发相同请求，避免重复处理
4. **批量处理**：批量处理多个请求，提高吞吐量
5. **流式响应优化**：优化流式响应处理，减少首块延迟

## 配置性能优化

### 启用性能优化

在配置文件中启用性能优化功能：

```yaml
llm:
  performance:
    # 启用HTTP连接池
    enable_connection_pool: true
    max_connections: 100  # 最大连接数
    max_keepalive_connections: 20  # 最大保持连接数
    connection_timeout: 30.0  # 连接超时（秒）
    
    # 启用请求缓存
    enable_cache: true
    cache_ttl: 3600.0  # 缓存生存时间（秒）
    cache_max_size: 1000  # 最大缓存条目数
    
    # 启用请求去重
    enable_deduplication: true
    
    # 启用批量处理
    enable_batch_processing: true
    batch_size: 10  # 批量大小
    batch_interval: 0.1  # 批量间隔（秒）
    max_wait_time: 1.0  # 最大等待时间（秒）
```

## 使用场景和最佳实践

### 1. HTTP连接池

**适用场景**：
- 高频API调用
- 需要低延迟的场景
- 多个适配器同时使用

**最佳实践**：
```python
# 连接池会自动管理，无需手动配置
# 只需在配置中启用即可
service = LLMService(config)
await service.initialize()

# 多次调用会自动复用连接
for i in range(100):
    response = await service.chat(messages)
```

**性能提升**：
- 减少连接建立时间：~50-100ms/请求
- 提升并发性能：支持更多并发请求

### 2. 请求缓存

**适用场景**：
- 重复请求较多
- 对实时性要求不高的场景
- 需要减少API调用成本

**最佳实践**：
```python
# 相同请求会自动使用缓存
messages = [{"role": "user", "content": "什么是AI？"}]

# 第一次请求（调用API）
response1 = await service.chat(messages)

# 第二次请求（使用缓存，无需调用API）
response2 = await service.chat(messages)  # 从缓存返回

# 缓存会在TTL过期后自动失效
```

**性能提升**：
- 缓存命中时延迟：< 1ms（vs 500-2000ms API调用）
- 减少API调用：显著降低成本和延迟

**注意事项**：
- 缓存基于请求内容哈希，完全相同的请求才会命中缓存
- 调整 `cache_ttl` 根据数据实时性需求
- 调整 `cache_max_size` 根据内存限制

### 3. 请求去重

**适用场景**：
- 高并发场景
- 可能出现重复请求
- 需要避免重复API调用

**最佳实践**：
```python
# 并发发送相同请求
import asyncio

messages = [{"role": "user", "content": "你好"}]

# 并发发送3个相同请求
tasks = [
    service.chat(messages),
    service.chat(messages),
    service.chat(messages),
]

# 只会实际调用一次API，其他请求共享结果
responses = await asyncio.gather(*tasks)
```

**性能提升**：
- 避免重复API调用
- 减少API成本和延迟

### 4. 批量处理

**适用场景**：
- 需要处理大量请求
- 可以容忍一定延迟
- 需要提高吞吐量

**最佳实践**：
```python
# 批量处理多个请求
messages_list = [
    [{"role": "user", "content": "问题1"}],
    [{"role": "user", "content": "问题2"}],
    [{"role": "user", "content": "问题3"}],
]

# 批量处理（如果适配器支持批量API）
responses = await service.batch_chat(messages_list)
```

**性能提升**：
- 提高吞吐量：批量处理比单个处理更高效
- 减少网络开销：合并多个请求

**注意事项**：
- 不是所有适配器都支持批量API
- 批量处理会增加延迟（等待批量填满）

### 5. 流式响应优化

**适用场景**：
- 需要实时显示响应
- 长文本生成
- 需要低延迟首块响应

**最佳实践**：
```python
# 流式响应会自动优化
messages = [{"role": "user", "content": "写一篇长文章"}]

async for chunk in service.stream_chat(messages):
    print(chunk.content, end="", flush=True)  # 实时显示
```

**性能提升**：
- 首块延迟：< 50ms（优化后）
- 用户体验：实时显示，无需等待完整响应

## 性能监控

### 查看性能指标

启用监控后，可以通过API查看性能指标：

```bash
# 查看Prometheus指标
curl http://localhost:8000/api/metrics

# 查看性能统计
curl http://localhost:8000/api/metrics/stats
```

### 关键指标

- **QPS**：每秒请求数
- **延迟**：P50、P95、P99延迟
- **成功率**：请求成功率
- **缓存命中率**：缓存命中比例
- **连接池使用率**：连接池使用情况

## 性能调优建议

### 1. 连接池配置

```yaml
llm:
  performance:
    max_connections: 100  # 根据并发需求调整
    max_keepalive_connections: 20  # 根据长期连接需求调整
```

**调优建议**：
- 高并发场景：增加 `max_connections`
- 低并发场景：减少 `max_connections` 节省资源
- 长期连接：增加 `max_keepalive_connections`

### 2. 缓存配置

```yaml
llm:
  performance:
    cache_ttl: 3600.0  # 根据数据实时性需求调整
    cache_max_size: 1000  # 根据内存限制调整
```

**调优建议**：
- 实时性要求高：减少 `cache_ttl`
- 实时性要求低：增加 `cache_ttl`
- 内存充足：增加 `cache_max_size`
- 内存受限：减少 `cache_max_size`

### 3. 批量处理配置

```yaml
llm:
  performance:
    batch_size: 10  # 根据适配器支持调整
    batch_interval: 0.1  # 根据延迟容忍度调整
```

**调优建议**：
- 适配器支持大批量：增加 `batch_size`
- 需要低延迟：减少 `batch_interval`
- 可以容忍延迟：增加 `batch_interval` 提高批量效率

## 性能基准测试

运行性能基准测试：

```bash
# 运行性能测试
pytest tests/performance/test_benchmark.py -v -m performance
```

### 性能指标目标

- **平均延迟**：< 50ms（启用优化）
- **最大延迟**：< 100ms（启用优化）
- **首块延迟**：< 50ms（流式响应）
- **并发性能**：20个并发请求总时间 < 150ms
- **内存使用**：100次请求后内存增长 < 50MB

## 故障排查

### 性能问题排查步骤

1. **检查配置**：确认性能优化功能已启用
2. **查看监控指标**：检查QPS、延迟、成功率
3. **检查缓存命中率**：如果缓存命中率低，考虑调整缓存策略
4. **检查连接池使用率**：如果使用率高，考虑增加连接数
5. **查看日志**：检查是否有错误或警告

### 常见问题

**Q: 启用缓存后性能没有提升？**

A: 检查：
- 请求内容是否完全相同（包括顺序）
- 缓存TTL是否设置合理
- 缓存大小是否足够

**Q: 连接池没有效果？**

A: 检查：
- 是否启用了连接池
- 连接数配置是否合理
- 是否有连接泄漏

**Q: 批量处理延迟增加？**

A: 这是正常的，批量处理会等待批量填满。如果无法容忍延迟，可以减少 `batch_interval` 或禁用批量处理。

## 最佳实践总结

1. **启用连接池**：对于高频调用场景，始终启用连接池
2. **合理使用缓存**：根据数据实时性需求调整缓存TTL
3. **启用请求去重**：高并发场景下避免重复请求
4. **监控性能指标**：定期查看性能指标，及时发现问题
5. **根据场景调整**：根据实际使用场景调整配置参数

## 相关文档

- [配置文档](configuration.md) - 详细配置说明
- [架构文档](../architecture/refactored-architecture.md) - 架构设计说明
- [API文档](../api/api-reference.md) - API使用说明
