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
├── encryption.py        # 加密服务（新增）
└── README.md            # 本文件
```

---

## 核心API

### ConfigManager（配置管理器）

**主要方法**：
- `load(env, config_dir)` - 加载配置（类方法）
- `get(key, default)` - 获取配置值（自动解密加密配置）
- `set(key, value, encrypt=False)` - 设置配置值（支持加密存储）
- `encrypt_value(value)` - 加密配置值
- `decrypt_value(encrypted_value)` - 解密配置值
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

# 设置加密配置值（API密钥等敏感信息）
config.set("llm.api_key", "sk-...", encrypt=True)

# 加密配置值（手动）
encrypted = config.encrypt_value("sensitive-api-key")
config.set("llm.api_key", encrypted)

# 获取配置值（加密配置会自动解密）
api_key = config.get("llm.api_key")  # 自动解密

# 重新加载配置（热重载）
await config.reload()
```

### EncryptionService（加密服务）

**主要方法**：
- `encrypt(plaintext)` - 加密明文数据
- `decrypt(encrypted)` - 解密加密数据
- `is_encrypted(value)` - 检查值是否为加密格式

**使用示例**：
```python
from infrastructure.config.encryption import EncryptionService

# 创建加密服务（需要主密钥）
service = EncryptionService(master_key="your-master-key-here")

# 加密敏感数据
encrypted = service.encrypt("sensitive-api-key")
# 返回格式: "salt:iv:ciphertext:tag"

# 解密数据
decrypted = service.decrypt(encrypted)
# 返回: "sensitive-api-key"
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

**加密主密钥**：
- `ENCRYPTION_KEY` - 加密主密钥（用于加密存储API密钥等敏感信息）

---

## 加密配置

### 加密存储API密钥

生产环境中，API密钥等敏感信息应该加密存储。

**配置方式**：

1. **设置加密主密钥**（通过环境变量或配置文件）：
   ```bash
   # 环境变量方式（推荐）
   export ENCRYPTION_KEY="your-master-key-here"
   ```

   或在配置文件中：
   ```yaml
   encryption_key: "your-master-key-here"
   ```

2. **加密配置值**（使用 `encrypted:` 前缀）：
   ```yaml
   llm:
     api_key: "encrypted:salt:iv:ciphertext:tag"
   ```

3. **自动解密**：
   ```python
   # 获取配置时自动解密
   api_key = config.get("llm.api_key")  # 返回解密后的明文
   ```

**生成加密值**：

```python
from infrastructure.config import ConfigManager

# 加载配置（需要设置加密主密钥）
config = ConfigManager.load(env="prod")

# 加密API密钥
encrypted = config.encrypt_value("sk-your-api-key")
print(f"encrypted:{encrypted}")  # 复制到配置文件
```

**安全最佳实践**：

1. **主密钥管理**：
   - 生产环境必须通过环境变量 `ENCRYPTION_KEY` 设置主密钥
   - 主密钥长度至少16个字符，建议32个字符以上
   - 不要将主密钥提交到版本控制系统
   - 使用密钥管理服务（如 AWS KMS、Azure Key Vault）管理主密钥

2. **加密配置**：
   - 所有API密钥必须加密存储
   - 使用 `encrypted:` 前缀标记加密配置项
   - 开发环境可以使用明文配置（向后兼容）

3. **密钥轮换**：
   - 定期轮换主密钥和API密钥
   - 轮换时重新加密所有配置值

## 依赖关系

### 依赖的其他模块
- 无（基础设施模块，不依赖业务模块）

### 外部依赖
- `PyYAML`：YAML文件解析（可选，推荐安装）
- `python-dotenv`：环境变量管理（可选）
- `cryptography`：加密库（用于API密钥加密存储）

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
| 2026-01-23 | 1.1 | 添加API密钥加密存储功能，支持AES-256-GCM加密，自动解密配置值 | - |