# 日志管理模块

## 模块概述

本模块提供统一的日志管理能力，支持结构化日志、多级别日志、日志轮转等功能。

**在整体架构中的位置**：
- 属于基础设施层
- 被所有其他模块依赖
- 不依赖其他业务模块

**核心职责**：
- 统一管理所有日志
- 配置日志格式和级别
- 管理日志处理器
- 支持日志轮转

---

## 模块结构

```
infrastructure/log/
├── __init__.py          # 模块导出
├── manager.py           # 日志管理器主类
├── masking.py           # 数据脱敏服务
└── README.md            # 本文件
```

---

## 核心API

### LogManager（日志管理器）

**主要方法**：
- `get_logger(name)` - 获取日志记录器（自动脱敏敏感数据）
- `configure(config)` - 配置日志系统
- `shutdown()` - 关闭日志系统

### DataMaskingService（数据脱敏服务）

**主要方法**：
- `mask_text(text)` - 脱敏文本中的敏感数据
- `mask_dict(data)` - 脱敏字典中的敏感数据
- `add_custom_rule(name, pattern)` - 添加自定义脱敏规则
- `enable()` / `disable()` - 启用/禁用脱敏功能

**工具函数**：
- `mask_sensitive_data(text, config)` - 快速脱敏文本

**使用示例**：
```python
from infrastructure.log import LogManager

# 创建日志管理器
log_config = {
    "level": "INFO",
    "file": "logs/app.log",
    "max_bytes": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}
log_manager = LogManager(log_config)

# 获取日志记录器
logger = log_manager.get_logger("core.llm")

# 记录日志
logger.info("LLM服务启动")
logger.error("错误信息", exc_info=True)
logger.debug("调试信息")
```

---

## 日志配置

### 配置选项

- `level`：日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
- `format`：日志格式字符串
- `file`：日志文件路径（可选）
- `max_bytes`：日志文件最大大小（默认10MB）
- `backup_count`：备份文件数量（默认5）
- `masking`：数据脱敏配置（可选）
  - `enabled`：是否启用脱敏（默认true，生产环境建议启用）
  - `mode`：脱敏模式（partial/full/hash，默认partial）
  - `keep_prefix`：部分隐藏时保留的前缀长度（默认3）
  - `keep_suffix`：部分隐藏时保留的后缀长度（默认2）
  - `custom_rules`：自定义脱敏规则（可选）

### 日志格式

默认格式：`%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### 数据脱敏

日志管理器支持自动脱敏敏感数据，防止敏感信息泄露到日志中。

**脱敏模式**：
- `partial`（部分隐藏）：保留前后部分，中间用星号替换
  - 示例：`sk-1234567890abcdef` → `sk-****...****ef`
- `full`（完全隐藏）：全部替换为占位符
  - 示例：`sk-1234567890abcdef` → `***MASKED***`
- `hash`（哈希脱敏）：使用SHA256哈希值（用于调试）
  - 示例：`sk-1234567890abcdef` → `sha256:a1b2c3d4`

**自动检测的敏感数据**：
- API密钥（`sk-`, `pk-`, `sk_live_`, `sk_test_`等）
- 邮箱地址
- 手机号（中国）
- 身份证号（中国）
- 银行卡号
- 密码字段（`password`, `pwd`等）

**配置示例**：
```yaml
log:
  level: "INFO"
  masking:
    enabled: true
    mode: "partial"
    keep_prefix: 3
    keep_suffix: 2
    custom_rules:
      - name: "custom_id"
        pattern: "ID:\\d+"
```

**使用示例**：
```python
from infrastructure.log import LogManager

# 创建带脱敏功能的日志管理器
config = {
    "level": "INFO",
    "masking": {
        "enabled": True,
        "mode": "partial"
    }
}
log_manager = LogManager(config)
logger = log_manager.get_logger("my_module")

# 记录日志（自动脱敏）
logger.info("API key: sk-1234567890abcdef")
# 输出：API key: sk-****...****ef
```

**安全注意事项**：
- 生产环境必须启用数据脱敏
- 开发环境可以禁用脱敏以便调试
- 自定义脱敏规则需要仔细测试，避免误脱敏
- 脱敏后的日志仍然可能包含部分敏感信息，需要妥善保管

---

## 依赖关系

### 依赖的其他模块
- 无（基础设施模块，不依赖业务模块）

### 外部依赖
- Python标准库：`logging`, `re`, `hashlib`

### 被哪些模块依赖
- 所有其他模块

---

## 相关文档

- [日志管理设计文档](../../docs/design/log-manager.md)
- [架构方案文档](../../AI框架架构方案文档.md)

---

## 更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-01-21 | 1.0 | 初始版本，实现日志管理模块 | - |
| 2026-01-22 | 1.1 | 添加数据脱敏功能，支持自动脱敏日志中的敏感信息 | - |