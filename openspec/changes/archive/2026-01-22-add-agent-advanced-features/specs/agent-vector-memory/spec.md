## ADDED Requirements

### Requirement: Vector-based Semantic Search
系统 SHALL 提供基于向量嵌入的语义检索能力，支持在长期记忆中根据语义相似度搜索相关对话历史。

#### Scenario: Store conversation with vector embeddings
- **WHEN** 长期记忆保存对话历史且配置启用向量检索
- **THEN** 系统 SHALL 将对话内容转换为向量嵌入并存储到向量数据库

#### Scenario: Search conversations by semantic similarity
- **WHEN** 用户提供查询文本进行语义搜索
- **THEN** 系统 SHALL 将查询文本转换为向量嵌入，在向量数据库中搜索相似度最高的对话历史，返回 top-k 结果

#### Scenario: Support multiple vector backends
- **WHEN** 配置选择不同的向量后端（Chroma 或 SQLite-VSS）
- **THEN** 系统 SHALL 通过统一的接口使用选定的后端，无需修改上层代码

### Requirement: Vector Backend Abstraction
系统 SHALL 提供向量后端抽象接口，支持多种向量数据库实现。

#### Scenario: Use Chroma backend
- **WHEN** 配置使用 Chroma 作为向量后端
- **THEN** 系统 SHALL 使用 Chroma 进行向量存储和检索

#### Scenario: Use SQLite-VSS backend
- **WHEN** 配置使用 SQLite-VSS 作为向量后端
- **THEN** 系统 SHALL 使用 SQLite-VSS 进行向量存储和检索（如果可用）

### Requirement: Hybrid Search Support
系统 SHALL 支持混合检索（向量相似度 + 关键词匹配），提高检索准确性。

#### Scenario: Perform hybrid search
- **WHEN** 用户执行语义搜索且配置启用混合检索
- **THEN** 系统 SHALL 结合向量相似度和关键词匹配结果，返回综合排序的结果
