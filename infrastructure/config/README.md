# 配置管理模块

## 模块概述

本模块提供统一的配置管理能力，支持多环境配置、配置热重载、环境变量覆盖等功能。

**在整体架构中的位置**：
- 属于基础设施层
- 被所有其他模块依赖
- 不依赖其他业务模块

**核心职责**：
- 统一管理所有配置
- 支持多环境配置切换
- 支持配置热重载
- 提供配置访问接口

---

## 模块结构

```
infrastructure/config/
├── __init__.py          # 模块导出
├── manager.py           # 配置管理器主类
├── loader.py            # 配置加载器
├── validator.py         # 配置验证器
└── README.md            # 本文件
```

---

## 核心API

### ConfigManager（配置管理器）

**主要方法**：
- `load(env, config_dir)` - 加载配置（类方法）
- `get(key, default)` - 获取配置值
- `set(key, value)` - 设置配置值
- `reload()` - 重新加载配置
- `validate()` - 验证配置

**使用示例**：
```python
from infrastructure.config import ConfigManager

# 加载配置
config = ConfigManager.load(env="dev")

# 获取配置值（支持点号分隔的嵌套键）
api_key = config.get("llm.api_key")
timeout = config.get("llm.timeout", 30)

# 设置配置值
config.set("llm.timeout", 60)

# 重新加载配置（热重载）
await config.reload()
```

---

## 配置文件格式

### default.yaml（默认配置）

```yaml
llm:
  api_key: ""
  timeout: 30
  max_retries: 3

cache:
  backend: "memory"
  ttl: 3600
```

### dev.yaml（开发环境配置）

```yaml
llm:
  api_key: "dev-api-key"
  timeout: 10
```

### prod.yaml（生产环境配置）

```yaml
llm:
  timeout: 60
```

---

## 环境变量支持

环境变量会覆盖配置文件中的值。

**命名规则**：`AI_FRAMEWORK_{SECTION}_{KEY}`

**示例**：
- `AI_FRAMEWORK_LLM_API_KEY` → `{"llm": {"api_key": "value"}}`
- `AI_FRAMEWORK_LLM_TIMEOUT` → `{"llm": {"timeout": "value"}}`

---

## 依赖关系

### 依赖的其他模块
- 无（基础设施模块，不依赖业务模块）

### 外部依赖
- `PyYAML`：YAML文件解析（可选，推荐安装）
- `python-dotenv`：环境变量管理（可选）

### 被哪些模块依赖
- 所有其他模块

---

## 相关文档

- [配置管理设计文档](../../docs/design/config-manager.md)
- [架构方案文档](../../AI框架架构方案文档.md)

---

## 更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-01-21 | 1.0 | 初始版本，实现配置管理模块 | - |
