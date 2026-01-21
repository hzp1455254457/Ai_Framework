# 缓存管理模块（infrastructure/cache）

## 模块概述

本模块提供 **统一的缓存接口**，用于在框架中缓存：
- 常用请求结果（例如LLM请求的幂等结果）
- 计算开销较大的中间结果（例如Token计算、向量化结果）
- 需要短期复用的数据（例如会话状态）

当前已实现：
- **Memory 后端**：支持 TTL 与 LRU 淘汰。

## 模块结构

```
infrastructure/cache/
├── __init__.py
├── manager.py                 # CacheManager：统一缓存入口
├── backends/
│   ├── __init__.py
│   ├── base.py                # BaseCacheBackend：后端接口定义
│   └── memory.py              # MemoryCacheBackend：内存缓存（TTL+LRU）
└── README.md
```

## 核心API

### CacheManager

- `await cache.get(key)`
- `await cache.set(key, value, ttl=None)`
- `await cache.delete(key)`
- `await cache.clear()`

示例：

```python
from infrastructure.cache.manager import CacheManager

cache = CacheManager({
    "cache": {"backend": "memory", "ttl": 60, "max_size": 100}
})

await cache.set("k1", {"v": 1})
value = await cache.get("k1")
```

## 配置项

在 `config/default.yaml` 中：

```yaml
cache:
  backend: "memory"
  ttl: 3600
  max_size: 1000
```

## 依赖关系

### 依赖的其他模块
- 无（基础设施模块，不依赖业务模块）

### 外部依赖
- 无

### 被哪些模块依赖
- `core/`（可选）：用于性能优化与结果复用
- `api/`（可选）：用于缓存某些接口结果

