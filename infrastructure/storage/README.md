# 存储管理模块

## 📋 模块概述

存储管理模块提供统一的存储管理能力，支持多种存储后端（数据库、文件存储等）。

**核心功能**：
- 对话历史存储
- 文件信息存储
- 元数据管理
- 连接池管理（HTTP和数据库）

**支持的存储后端**：
- SQLite数据库存储
- 文件系统存储

---

## 🏗️ 模块结构

```
infrastructure/storage/
├── __init__.py              # 模块导出
├── manager.py               # 存储管理器主类
├── connection_pool.py       # 连接池管理
├── backends/                # 存储后端实现
│   ├── __init__.py
│   ├── base.py              # 存储后端基类
│   ├── database.py          # SQLite数据库存储后端
│   └── file_storage.py      # 文件存储后端
└── README.md                # 本文档
```

---

## 🚀 快速开始

### 基本使用

```python
from infrastructure.storage import StorageManager

# 初始化存储管理器
config = {
    "storage": {
        "backend": "database",  # 或 "file"
        "database": {
            "db_path": "data/storage.db"
        }
    }
}

manager = StorageManager(config)
await manager.initialize()

# 保存对话历史
await manager.save_conversation(
    conversation_id="conv1",
    messages=[
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ],
    metadata={"model": "gpt-3.5-turbo"}
)

# 获取对话历史
conversation = await manager.get_conversation("conv1")

# 列出所有对话
conversations = await manager.list_conversations(limit=10)

# 清理资源
await manager.cleanup()
```

### 使用连接池

```python
from infrastructure.storage import ConnectionPoolManager

# 初始化连接池管理器
config = {
    "http": {
        "max_connections": 100,
        "max_keepalive_connections": 20,
        "timeout": 30.0
    },
    "database": {
        "db_path": "data/storage.db",
        "pool_size": 5
    }
}

pool_manager = ConnectionPoolManager(config)
await pool_manager.initialize()

# 使用HTTP连接池
async with pool_manager.get_http_client() as client:
    response = await client.get("https://api.example.com")

# 使用数据库连接池
async with pool_manager.get_db_connection() as conn:
    await conn.execute("SELECT * FROM conversations")

# 清理资源
await pool_manager.cleanup()
```

---

## 📚 API参考

### StorageManager

存储管理器主类，提供统一的存储接口。

#### 方法

##### `save_conversation(conversation_id, messages, metadata=None)`

保存对话历史。

**参数**：
- `conversation_id` (str): 对话ID
- `messages` (List[Dict]): 消息列表
- `metadata` (Dict, optional): 元数据

**异常**：
- `StorageError`: 保存失败时抛出

##### `get_conversation(conversation_id)`

获取对话历史。

**参数**：
- `conversation_id` (str): 对话ID

**返回**：
- `Optional[List[Dict]]`: 消息列表，如果不存在返回None

**异常**：
- `StorageError`: 获取失败时抛出

##### `delete_conversation(conversation_id)`

删除对话历史。

**参数**：
- `conversation_id` (str): 对话ID

**异常**：
- `StorageError`: 删除失败时抛出

##### `list_conversations(limit=100, offset=0)`

列出对话列表。

**参数**：
- `limit` (int): 返回数量限制
- `offset` (int): 偏移量

**返回**：
- `List[Dict]`: 对话列表

**异常**：
- `StorageError`: 查询失败时抛出

##### `save_file(file_id, file_path, metadata=None)`

保存文件信息。

**参数**：
- `file_id` (str): 文件ID
- `file_path` (str): 文件路径
- `metadata` (Dict, optional): 元数据

**异常**：
- `StorageError`: 保存失败时抛出

##### `get_file(file_id)`

获取文件信息。

**参数**：
- `file_id` (str): 文件ID

**返回**：
- `Optional[Dict]`: 文件信息字典，如果不存在返回None

**异常**：
- `StorageError`: 获取失败时抛出

##### `delete_file(file_id)`

删除文件信息。

**参数**：
- `file_id` (str): 文件ID

**异常**：
- `StorageError`: 删除失败时抛出

##### `list_files(limit=100, offset=0)`

列出文件列表。

**参数**：
- `limit` (int): 返回数量限制
- `offset` (int): 偏移量

**返回**：
- `List[Dict]`: 文件列表

**异常**：
- `StorageError`: 查询失败时抛出

### ConnectionPoolManager

连接池管理器，统一管理HTTP和数据库连接池。

#### 方法

##### `get_http_client()`

获取HTTP客户端（上下文管理器）。

**返回**：
- `AsyncClient`: httpx异步客户端

**异常**：
- `StorageError`: 连接池未初始化时抛出

##### `get_db_connection()`

获取数据库连接（上下文管理器）。

**返回**：
- `aiosqlite.Connection`: SQLite异步连接

**异常**：
- `StorageError`: 连接池未初始化时抛出

---

## ⚙️ 配置说明

### StorageManager配置

```yaml
storage:
  backend: "database"  # 或 "file"
  database:
    db_path: "data/storage.db"
  file:
    storage_root: "data/storage"
```

### ConnectionPoolManager配置

```yaml
http:
  max_connections: 100
  max_keepalive_connections: 20
  timeout: 30.0

database:
  db_path: "data/storage.db"
  pool_size: 5
```

---

## 🔧 存储后端

### DatabaseStorageBackend

基于SQLite的数据库存储后端。

**特性**：
- 异步SQLite操作（使用aiosqlite）
- 自动创建数据库和表
- 支持JSON元数据存储
- 支持索引优化

**表结构**：
- `conversations`: 对话历史表
- `files`: 文件信息表

### FileStorageBackend

基于文件系统的存储后端。

**特性**：
- 异步文件操作（使用aiofiles）
- 自动创建目录结构
- 支持JSON元数据存储

**目录结构**：
```
storage_root/
├── conversations/
│   └── {conversation_id}.json
├── files/
│   ├── {file_id}.json  # 元数据
│   └── {file_id}       # 实际文件
└── metadata/
```

---

## 📝 使用示例

### 示例1：保存和获取对话历史

```python
from infrastructure.storage import StorageManager

manager = StorageManager(config)
await manager.initialize()

# 保存对话
await manager.save_conversation(
    conversation_id="conv1",
    messages=[
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language."}
    ],
    metadata={"model": "gpt-3.5-turbo", "temperature": 0.7}
)

# 获取对话
conversation = await manager.get_conversation("conv1")
print(conversation)
```

### 示例2：文件存储

```python
# 保存文件信息
await manager.save_file(
    file_id="file1",
    file_path="/path/to/file.txt",
    metadata={"size": 1024, "type": "text/plain"}
)

# 获取文件信息
file_info = await manager.get_file("file1")
print(file_info["file_path"])
```

### 示例3：使用连接池

```python
from infrastructure.storage import ConnectionPoolManager

pool_manager = ConnectionPoolManager(config)
await pool_manager.initialize()

# 使用HTTP连接池
async with pool_manager.get_http_client() as client:
    response = await client.get("https://api.example.com/data")
    data = response.json()

# 使用数据库连接池
async with pool_manager.get_db_connection() as conn:
    async with conn.execute("SELECT * FROM conversations") as cursor:
        rows = await cursor.fetchall()
        for row in rows:
            print(row)
```

---

## 🔍 依赖关系

**依赖模块**：
- `infrastructure.config`: 配置管理（可选）
- `infrastructure.log`: 日志管理（可选）

**外部依赖**：
- `aiosqlite`: 异步SQLite驱动
- `aiofiles`: 异步文件操作
- `httpx`: 异步HTTP客户端

---

## 🧪 测试

存储管理模块的测试位于 `tests/unit/infrastructure/test_storage/`。

运行测试：
```bash
pytest tests/unit/infrastructure/test_storage/
```

---

## 📚 相关文档

- [架构方案文档](../../../AI框架架构方案文档.md)
- [代码规范](../../../.cursor/rules/CodeStandards.mdc)
- [项目规则](../../../.cursor/rules/ProjectRules.mdc)

---

## 🔄 更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|---|---|---|-----|
| 2026-01-21 | v1.0 | 初始版本，实现StorageManager和连接池管理 | - |
