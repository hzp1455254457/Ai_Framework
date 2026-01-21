# 缓存管理模块功能设计文档

## 📋 功能概述

### 功能名称
缓存管理模块（Cache Manager）

### 功能目的
提供统一的缓存能力，支持多种缓存后端（内存/Redis/文件），用于提升性能、降低重复计算成本。

### 解决的问题
1. **重复计算**：同样的请求/中间结果频繁重复计算
2. **响应延迟**：一些昂贵操作（如向量化、长文本处理）导致延迟升高
3. **扩展困难**：缺少统一缓存接口，后续难以切换/扩展缓存后端

### 使用场景
- 缓存LLM调用结果（在幂等、可缓存场景）
- 缓存Token计算/向量化等昂贵计算结果
- 缓存短期会话状态

---

## 🏗️ 技术架构

### 架构设计

```
infrastructure/cache/
├── manager.py                 # CacheManager
└── backends/
    ├── base.py                # BaseCacheBackend
    ├── memory.py              # MemoryCacheBackend（TTL+LRU）
    ├── redis.py               # 预留（P2）
    └── file.py                # 预留（P2）
```

### 类设计

```
CacheManager
  ├── get/set/delete/clear
  └── backend: BaseCacheBackend

BaseCacheBackend
  ├── get/set/delete/clear（异步接口）

MemoryCacheBackend
  ├── OrderedDict 维护LRU
  ├── expires_at 实现TTL
  └── asyncio.Lock 保证并发安全
```

---

## 🔌 接口设计

### CacheManager

```python
class CacheManager:
    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None: ...
    async def delete(self, key: str) -> None: ...
    async def clear(self) -> None: ...
```

---

## 🔧 实现细节

### 后端选择策略
- `cache.backend=memory`：默认内存缓存
- 后续扩展 `redis/file` 时仅新增后端文件，不改上层调用代码

### 过期策略（TTL）
- 每个 key 存储 `expires_at`
- `get/set` 时清理过期项

### 淘汰策略（LRU）
- 超过 `max_size` 时，优先淘汰最久未访问项

---

## 🧪 测试策略

### 单元测试
- MemoryCacheBackend：
  - get/set 命中与未命中
  - TTL过期
  - LRU淘汰
- CacheManager：
  - 基于配置创建memory后端

---

## 🔄 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|---|---|---|---|
| v1.0 | 2026-01-21 | 初始版本：实现MemoryCacheBackend与CacheManager | - |

