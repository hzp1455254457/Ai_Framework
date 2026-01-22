# Agent引擎功能设计文档

## 功能概述

Agent引擎是AI框架的核心价值体现，提供智能体（Agent）执行能力，包括任务接收、工具调用、记忆管理和工作流编排。

**功能名称**：Agent引擎核心（AgentEngine + 工具系统 + 记忆管理 + 工作流）

**解决的问题**：
- 如何让AI系统能够执行复杂任务（需要多步推理和工具调用）
- 如何管理Agent的对话历史和长期记忆
- 如何扩展Agent的能力（通过工具系统）

**使用场景**：
- 复杂任务执行（需要调用外部工具）
- 多轮对话场景（需要维护上下文）
- 需要持久化对话历史的场景

---

## 技术架构

### 核心类和接口

```
core/agent/
├── engine.py          # AgentEngine主类
├── tools.py           # 工具系统（Tool, ToolRegistry）
├── memory.py          # 记忆管理（ShortTermMemory, LongTermMemory）
└── workflow.py        # 工作流编排（Workflow, WorkflowStep）
```

### 数据流设计

```
用户任务
  ↓
AgentEngine.run_task()
  ↓
组装消息（任务 + 短期记忆）
  ↓
调用LLM（传入工具schema）
  ↓
检查工具调用
  ├── 有工具调用 → 执行工具 → 回注结果 → 继续调用LLM
  └── 无工具调用 → 输出最终结果
  ↓
保存长期记忆（可选）
  ↓
返回结果
```

---

## 接口设计

### AgentEngine

#### run_task()

**功能**：执行Agent任务

**接口**：
```python
async def run_task(
    self,
    task: str,
    conversation_id: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]
```

**参数**：
- `task`: 任务描述（文本）
- `conversation_id`: 对话ID（可选，用于长期记忆）
- `**kwargs`: 其他参数（如temperature、model等）

**返回**：
```python
{
    "content": str,           # 最终输出内容
    "tool_calls": List[Dict], # 工具调用记录
    "iterations": int,        # 迭代次数
    "metadata": Dict,         # 其他元数据
}
```

**异常**：
- `AgentError`: 任务执行失败时抛出

---

### 工具系统

#### Tool

**功能**：工具定义类

**接口**：
```python
@dataclass
class Tool:
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema格式
    func: Callable[..., Awaitable[Any]]
```

#### ToolRegistry

**功能**：工具注册表

**主要方法**：
- `register(tool: Tool) -> None`: 注册工具
- `execute(name: str, arguments: Dict) -> Any`: 执行工具
- `get_function_schemas() -> List[Dict]`: 获取Function Calling schema列表

---

### 记忆管理

#### ShortTermMemory

**功能**：短期记忆（会话上下文）

**主要方法**：
- `add_message(role: str, content: str) -> None`: 添加消息
- `add_tool_message(tool_name: str, tool_result: Any) -> None`: 添加工具消息
- `get_messages() -> List[Dict[str, str]]`: 获取消息列表
- `clear() -> None`: 清空记忆

#### LongTermMemory

**功能**：长期记忆（持久化存储）

**主要方法**：
- `save(conversation_id: str, messages: List[Dict], metadata: Optional[Dict]) -> None`: 保存对话
- `load(conversation_id: str) -> Optional[List[Dict]]`: 加载对话
- `delete(conversation_id: str) -> None`: 删除对话
- `list_conversations(limit: int, offset: int) -> List[Dict]`: 列出对话

---

## 实现细节

### 关键技术选型

1. **工具协议**：优先兼容OpenAI Function Calling格式
   - 理由：框架已有OpenAI适配器，且多家厂商兼容此格式
   - 实现：Tool.to_function_schema()返回OpenAI格式的schema

2. **记忆分层**：
   - 短期记忆：基于ConversationContext（内存）
   - 长期记忆：基于StorageManager（持久化）

3. **工作流循环**：采用ReAct-like最小循环
   - 线性执行：LLM → 工具调用 → LLM → 输出
   - 最大迭代次数限制（防止无限循环）

### 核心算法或流程

**Agent工作流循环**：
```python
while iterations < max_iterations:
    # 1. 组装消息
    messages = short_term_memory.get_messages()
    
    # 2. 调用LLM（传入工具schema）
    response = await llm_service.chat(messages, functions=tool_schemas)
    
    # 3. 检查工具调用
    if response.metadata.get("tool_calls"):
        # 执行工具并回注结果
        for tool_call in tool_calls:
            result = await tool_registry.execute(tool_name, tool_args)
            short_term_memory.add_tool_message(tool_name, result)
        continue  # 继续循环
    
    # 4. 输出最终结果
    return {
        "content": response.content,
        "tool_calls": tool_calls_history,
        "iterations": iterations,
    }
```

### 异常处理策略

- **AgentError**：Agent引擎异常基类
- **ToolError**：工具执行异常
- **MemoryError**：记忆操作异常
- **WorkflowError**：工作流执行异常

---

## 依赖关系

### 依赖的其他模块

- `core.base.service`: BaseService基类
- `core.llm.service`: LLMService（用于LLM调用）
- `core.llm.context`: ConversationContext（用于短期记忆）
- `infrastructure.storage`: StorageManager（用于长期记忆）

### 外部依赖库

- `httpx`: 异步HTTP客户端（通过LLMService间接使用）
- `pydantic`: 数据验证（API模型）

### 数据依赖

- 配置：`config/*.yaml`中的`agent`和`llm`配置
- 存储：StorageManager的对话历史存储

---

## 测试策略

### 单元测试计划

- `test_tools.py`: 工具系统测试（Tool、ToolRegistry）
- `test_memory.py`: 记忆管理测试（ShortTermMemory、LongTermMemory）
- `test_engine.py`: Agent引擎测试（AgentEngine核心功能）

### 集成测试计划

- Agent引擎与LLM服务集成
- Agent引擎与StorageManager集成
- Agent API路由集成测试

### 性能测试指标

- 任务执行响应时间
- 工具调用延迟
- 记忆读写性能

---

---

## 扩展功能

### 任务规划器

Agent引擎支持可选的任务规划器，能够将复杂任务分解为可执行的步骤序列。

**启用方式**：
- 配置 `agent.enable_planner: true`
- 在 `run_task()` 中设置 `use_planner=True`

**相关文档**：`docs/design/agent-planner.md`

### 向量检索

长期记忆支持基于向量嵌入的语义检索，可以搜索语义相似的对话历史。

**启用方式**：
- 配置向量后端（Chroma或SQLite-VSS）
- 在LongTermMemory初始化时传入vector_backend

**相关文档**：`docs/design/vector-memory.md`

### 多Agent协作

支持多个Agent实例协同执行任务，通过AgentOrchestrator进行任务分配和结果聚合。

**使用方式**：
- 创建AgentOrchestrator实例
- 添加多个Agent实例
- 使用编排器执行任务

**相关文档**：`docs/design/agent-collaboration.md`

---

## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|---------|--------|
| v1.0 | 2026-01-21 | 初始版本，实现Agent引擎核心功能 | - |
| v1.1 | 2026-01-21 | 扩展功能：任务规划器、向量检索、多Agent协作 | - |