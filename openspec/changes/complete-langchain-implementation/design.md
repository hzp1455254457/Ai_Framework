# LangChain适配器完善设计

## 设计原则

1. **接口转换**：将抽象接口转换为LangChain接口
2. **功能完整**：实现所有接口方法，不留TODO
3. **性能优化**：减少不必要的转换开销
4. **错误处理**：完善的错误处理和fallback机制

## 详细设计

### 1. LLM适配器完善

#### LangChainLLMWrapper设计

```python
class LangChainLLMWrapper(BaseLLM):
    """将ILLMProvider包装为LangChain BaseLLM"""
    
    def __init__(self, llm_provider: ILLMProvider):
        self._provider = llm_provider
    
    async def _agenerate(self, prompts, stop=None, **kwargs):
        # 将LangChain的prompts转换为消息列表
        messages = self._convert_prompts_to_messages(prompts)
        # 调用ILLMProvider.chat()
        response = await self._provider.chat(messages, **kwargs)
        # 转换为LangChain格式
        return self._convert_response_to_langchain(response)
    
    async def _stream(self, prompt, stop=None, **kwargs):
        # 实现流式输出
        messages = [{"role": "user", "content": prompt}]
        async for chunk in self._provider.stream_chat(messages, **kwargs):
            yield chunk
```

#### 实现要点
- 消息格式转换（LangChain格式 ↔ 标准格式）
- 流式输出支持
- 参数映射（temperature、max_tokens等）

### 2. 工具适配器完善

#### 工具转换设计

```python
def _convert_native_tool_to_langchain(self, tool: NativeTool):
    """将自研Tool转换为LangChain Tool"""
    from langchain.tools import Tool
    from pydantic import BaseModel, create_model
    
    # 创建Pydantic模型用于参数验证
    args_model = create_pydantic_model_from_schema(tool.parameters)
    
    async def langchain_func(**kwargs):
        # 调用原生工具
        return await tool.execute(kwargs)
    
    return Tool(
        name=tool.name,
        description=tool.description,
        func=langchain_func,
        args_schema=args_model
    )
```

#### 实现要点
- JSON Schema → Pydantic模型转换
- 异步函数包装
- 错误处理和类型转换

### 3. 记忆适配器完善

#### 消息管理设计

```python
def add_message(self, role: str, content: str, **kwargs):
    """添加消息到LangChain Memory"""
    if role == "user":
        self._memory.chat_memory.add_user_message(content)
    elif role == "assistant":
        self._memory.chat_memory.add_ai_message(content)
    elif role == "tool":
        # LangChain的tool消息处理
        tool_call_id = kwargs.get("tool_call_id")
        if tool_call_id:
            self._memory.chat_memory.add_message(
                AIMessage(content="", tool_calls=[...])
            )
            self._memory.chat_memory.add_message(
                ToolMessage(content=content, tool_call_id=tool_call_id)
            )

def get_messages(self):
    """从LangChain Memory获取消息"""
    messages = self._memory.chat_memory.messages
    result = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            result.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            result.append({"role": "assistant", "content": msg.content})
        elif isinstance(msg, ToolMessage):
            result.append({
                "role": "tool",
                "content": msg.content,
                "tool_call_id": msg.tool_call_id
            })
    return result
```

#### 实现要点
- 消息类型转换（HumanMessage/AIMessage/ToolMessage ↔ 标准格式）
- 工具消息的特殊处理
- 长期记忆持久化（可选）

### 4. Agent适配器完善

#### Agent创建设计

```python
async def initialize(self):
    """初始化LangChain Agent"""
    # 1. 转换LLM
    from core.implementations.langchain.langchain_llm import LangChainLLMWrapper
    langchain_llm = LangChainLLMWrapper(self._llm_provider)
    
    # 2. 转换工具
    langchain_tools = []
    for tool_name in self._tool_manager.list_tools():
        # 如果工具管理器是LangChainToolManager，直接获取
        if isinstance(self._tool_manager, LangChainToolManager):
            tool = self._tool_manager._tools.get(tool_name)
            if tool:
                langchain_tools.append(tool)
        else:
            # 否则需要转换
            native_tool = self._tool_manager._registry.get_tool(tool_name)
            if native_tool:
                langchain_tool = self._tool_manager._convert_native_tool_to_langchain(native_tool)
                langchain_tools.append(langchain_tool)
    
    # 3. 转换记忆
    langchain_memory = None
    if isinstance(self._memory, LangChainMemory):
        langchain_memory = self._memory._memory
    else:
        # 需要转换自研记忆为LangChain记忆
        langchain_memory = self._convert_memory_to_langchain(self._memory)
    
    # 4. 创建Agent
    from langchain.agents import initialize_agent, AgentType
    
    agent_config = self._config.get("agent", {})
    agent_type = agent_config.get("agent_type", "openai-functions")
    
    agent_type_map = {
        "openai-functions": AgentType.OPENAI_FUNCTIONS,
        "openai-multi-functions": AgentType.OPENAI_MULTI_FUNCTIONS,
        "react": AgentType.REACT_DOCSTORE,
        "self-ask-with-search": AgentType.SELF_ASK_WITH_SEARCH,
    }
    
    self._agent_executor = initialize_agent(
        tools=langchain_tools,
        llm=langchain_llm,
        agent=agent_type_map.get(agent_type, AgentType.OPENAI_FUNCTIONS),
        memory=langchain_memory,
        verbose=agent_config.get("verbose", False),
        max_iterations=agent_config.get("max_iterations", 10),
        return_intermediate_steps=agent_config.get("return_intermediate_steps", True),
    )
```

#### 任务执行设计

```python
async def run_task(self, task: str, conversation_id: Optional[str] = None, **kwargs):
    """执行任务"""
    if not self._agent_executor:
        raise RuntimeError("Agent未初始化")
    
    # 执行Agent
    result = await self._agent_executor.ainvoke({"input": task})
    
    # 提取工具调用信息
    tool_calls = []
    if "intermediate_steps" in result:
        for step in result["intermediate_steps"]:
            tool_calls.append({
                "tool": step[0].tool,
                "input": step[0].tool_input,
                "output": step[1]
            })
    
    # 转换为标准格式
    return {
        "content": result.get("output", ""),
        "tool_calls": tool_calls,
        "iterations": len(result.get("intermediate_steps", [])),
        "metadata": {
            "agent_type": self._config.get("agent", {}).get("agent_type"),
            "langchain_result": result
        }
    }
```

#### 实现要点
- 支持多种Agent类型（OpenAI Functions、ReAct等）
- 工具调用信息提取
- 结果格式转换
- 错误处理和重试

## 设计决策

### 1. 为什么需要LLM包装器？

**决策**：LangChain需要BaseLLM接口，而我们的ILLMProvider接口不同，需要包装器转换。

### 2. 为什么需要工具转换？

**决策**：自研Tool和LangChain Tool接口不同，需要转换以支持混合使用。

### 3. 为什么需要记忆转换？

**决策**：自研Memory和LangChain Memory接口不同，需要转换以支持混合使用。

### 4. 如何支持多种Agent类型？

**决策**：通过配置选择Agent类型，使用LangChain的AgentType枚举。

## 目录结构

```
core/implementations/langchain/
├── __init__.py
├── langchain_llm.py          # 完善LLM适配器
│   └── LangChainLLMWrapper   # 新增：LLM包装器
├── langchain_agent.py        # 完善Agent适配器
├── langchain_tools.py         # 完善工具适配器
└── langchain_memory.py        # 完善记忆适配器
```

## 使用示例

### 示例1：完全使用LangChain

```yaml
# config/default.yaml
llm:
  implementation: "langchain"
agent:
  implementation: "langchain"
  agent_type: "openai-functions"  # 选择Agent类型
tools:
  implementation: "langchain"
memory:
  implementation: "langchain"
  type: "buffer"  # buffer/summary
```

### 示例2：混合使用

```yaml
# config/default.yaml
llm:
  implementation: "native"      # 自研LLM
agent:
  implementation: "langchain"   # LangChain Agent
tools:
  implementation: "native"      # 自研工具（会自动转换）
memory:
  implementation: "langchain"    # LangChain记忆
```
