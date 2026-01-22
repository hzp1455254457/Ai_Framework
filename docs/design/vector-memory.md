# 向量检索功能设计文档

## 功能概述

向量检索是长期记忆的扩展功能，支持基于语义相似度的对话历史搜索。

**功能名称**：向量检索集成（Vector Memory）

**解决的问题**：
- 长期记忆仅支持基于conversation_id的精确检索
- 无法根据语义相似度搜索相关对话历史
- 需要RAG（检索增强生成）能力

**使用场景**：
- 根据查询文本搜索相关历史对话
- RAG场景：从历史对话中检索相关信息用于生成
- 知识库检索：从大量对话历史中查找相关知识

---

## 技术架构

### 核心类和接口

```
infrastructure/storage/vector_db.py
├── BaseVectorBackend: 向量后端基类
├── ChromaVectorBackend: Chroma向量数据库后端
└── SQLiteVSSVectorBackend: SQLite-VSS后端（占位）

core/agent/memory.py
└── LongTermMemory: 扩展支持向量检索方法
```

### 数据流设计

```
对话历史
  ↓
生成向量嵌入（需要嵌入模型）
  ↓
存储到向量数据库
  ↓
查询文本
  ↓
生成查询向量
  ↓
向量相似度搜索
  ↓
返回top-k结果
```

---

## 接口设计

### LongTermMemory扩展

#### search_by_semantics()

**功能**：基于语义相似度搜索对话历史

**接口**：
```python
async def search_by_semantics(
    self,
    query: str,
    top_k: int = 5,
    embedding_model: Optional[Any] = None,
) -> List[Dict[str, Any]]
```

**参数**：
- `query`: 查询文本
- `top_k`: 返回结果数量
- `embedding_model`: 嵌入模型（可选）

**返回**：
- 搜索结果列表，每个结果包含conversation_id、similarity、metadata

---

### BaseVectorBackend

**功能**：向量后端抽象接口

**主要方法**：
- `add_vectors()`: 添加向量
- `search()`: 向量搜索
- `delete()`: 删除向量

---

## 实现细节

### 关键技术选型

1. **向量后端**：
   - Chroma：主要后端，轻量级、易集成
   - SQLite-VSS：可选轻量级后端（占位实现）

2. **嵌入模型**：
   - 当前实现需要用户提供嵌入模型
   - 未来可以集成sentence-transformers等

3. **混合检索**：
   - 支持向量相似度 + 关键词匹配（未来扩展）

### 注意事项

- 向量检索需要先配置向量后端
- 需要嵌入模型生成向量（当前实现为占位）
- SQLite-VSS后端尚未实现（占位）

---

## 依赖关系

### 依赖的其他模块

- `infrastructure.storage.vector_db`: 向量数据库接口

### 外部依赖库

- `chromadb`: Chroma向量数据库（可选）

---

## 测试策略

### 单元测试计划

- `test_vector_memory.py`: 向量记忆测试（需要mock向量后端）

---

## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|---------|--------|
| v1.0 | 2026-01-21 | 初始版本，实现向量后端接口和Chroma集成 | - |
