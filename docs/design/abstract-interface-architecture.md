# 抽象接口架构设计

## 📋 概述

本文档设计一个完全抽象的接口层架构，允许在运行时灵活选择不同的实现（LangChain、LangGraph、自研），并支持随意组装。

**设计原则**：
- **接口抽象**：所有核心功能都定义抽象接口
- **实现解耦**：具体实现与接口完全分离
- **策略模式**：通过策略选择不同实现
- **工厂模式**：通过工厂创建具体实现
- **依赖注入**：通过配置注入依赖

**设计日期**：2026-01-23

---

## 🏗️ 架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                   应用层（API/CLI）                       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│             抽象接口层（Abstract Interfaces）             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ ILLMProvider │  │ IAgentEngine │  │ IToolManager  │ │
│  │ IMemory      │  │ IWorkflow    │  │ IChain        │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│           实现层（Concrete Implementations）               │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 自研实现（Native）                                    │ │
│  │ - NativeLLMProvider                                 │ │
│  │ - NativeAgentEngine                                │ │
│  │ - NativeToolManager                                │ │
│  │ - NativeMemory                                     │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │ LangChain实现                                       │ │
│  │ - LangChainLLMProvider                             │ │
│  │ - LangChainAgentEngine                             │ │
│  │ - LangChainToolManager                             │ │
│  │ - LangChainMemory                                  │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │ LangGraph实现                                       │ │
│  │ - LangGraphWorkflow                                │ │
│  │ - LangGraphAgentEngine                             │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│           工厂层（Factory Layer）                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ LLMFactory   │  │ AgentFactory │  │ ToolFactory   │ │
│  │ MemoryFactory│  │ WorkflowFactory│ ChainFactory  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│           配置层（Configuration）                         │
│  - 实现选择（native/langchain/langgraph）                │
│  - 组件组装配置                                          │
│  - 运行时切换支持                                         │
└──────────────────────────────────────────────────────────┘
```

---

## 🔌 核心抽象接口

### 1. LLM提供者接口

```python
# core/interfaces/llm.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncIterator, Optional
from core.llm.models import LLMResponse

class ILLMProvider(ABC):
    """LLM提供者抽象接口"""
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """发送聊天请求"""
        pass
    
    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> AsyncIterator[LLMResponse]:
        """流式聊天"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass
```

### 2. Agent引擎接口

```python
# core/interfaces/agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class IAgentEngine(ABC):
    """Agent引擎抽象接口"""
    
    @abstractmethod
    async def run_task(
        self,
        task: str,
        conversation_id: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """执行任务"""
        pass
    
    @abstractmethod
    def register_tool(self, tool: Any) -> None:
        """注册工具"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[str]:
        """获取工具列表"""
        pass
    
    @abstractmethod
    def clear_memory(self) -> None:
        """清空记忆"""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理资源"""
        pass
```

### 3. 工具管理器接口

```python
# core/interfaces/tools.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class IToolManager(ABC):
    """工具管理器抽象接口"""
    
    @abstractmethod
    def register(self, tool: Any) -> None:
        """注册工具"""
        pass
    
    @abstractmethod
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """执行工具"""
        pass
    
    @abstractmethod
    def list_tools(self) -> List[str]:
        """列出所有工具"""
        pass
    
    @abstractmethod
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """获取工具schema"""
        pass
    
    @abstractmethod
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """获取所有工具schema"""
        pass
```

### 4. 记忆管理接口

```python
# core/interfaces/memory.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IMemory(ABC):
    """记忆管理抽象接口"""
    
    @abstractmethod
    def add_message(self, role: str, content: str, **kwargs: Any) -> None:
        """添加消息"""
        pass
    
    @abstractmethod
    def get_messages(self) -> List[Dict[str, Any]]:
        """获取消息列表"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """清空记忆"""
        pass
    
    @abstractmethod
    async def save(self, conversation_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """保存记忆（长期）"""
        pass
    
    @abstractmethod
    async def load(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        """加载记忆（长期）"""
        pass
    
    @property
    @abstractmethod
    def message_count(self) -> int:
        """消息数量"""
        pass
```

### 5. 工作流接口

```python
# core/interfaces/workflow.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class IWorkflow(ABC):
    """工作流抽象接口"""
    
    @abstractmethod
    async def execute(
        self,
        input_data: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行工作流"""
        pass
    
    @abstractmethod
    def add_node(self, node_id: str, node_func: Any) -> None:
        """添加节点"""
        pass
    
    @abstractmethod
    def add_edge(self, from_node: str, to_node: str, condition: Optional[Any] = None) -> None:
        """添加边"""
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        pass
```

### 6. 链式调用接口

```python
# core/interfaces/chain.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class IChain(ABC):
    """链式调用抽象接口"""
    
    @abstractmethod
    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行链"""
        pass
    
    @abstractmethod
    def add_link(self, link_func: Any, name: Optional[str] = None) -> None:
        """添加链节点"""
        pass
    
    @abstractmethod
    def get_links(self) -> List[str]:
        """获取链节点列表"""
        pass
```

---

## 🏭 工厂模式实现

### 1. LLM工厂

```python
# core/factories/llm_factory.py
from typing import Dict, Any, Optional
from core.interfaces.llm import ILLMProvider
from core.llm.service import LLMService
from core.llm.adapters.litellm_adapter import LiteLLMAdapter

# LangChain实现
try:
    from core.implementations.langchain.langchain_llm import LangChainLLMProvider
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LangChainLLMProvider = None

class LLMFactory:
    """LLM提供者工厂"""
    
    @staticmethod
    def create(
        implementation: str,
        config: Dict[str, Any]
    ) -> ILLMProvider:
        """
        创建LLM提供者
        
        参数:
            implementation: 实现类型（native/litellm/langchain）
            config: 配置字典
        
        返回:
            LLM提供者实例
        """
        if implementation == "native":
            return NativeLLMProvider(config)
        elif implementation == "litellm":
            return LiteLLMLLMProvider(config)
        elif implementation == "langchain":
            if not LANGCHAIN_AVAILABLE:
                raise ValueError("LangChain未安装")
            return LangChainLLMProvider(config)
        else:
            raise ValueError(f"不支持的实现类型: {implementation}")
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> ILLMProvider:
        """从配置创建（自动选择实现）"""
        llm_config = config.get("llm", {})
        implementation = llm_config.get("implementation", "native")
        return LLMFactory.create(implementation, config)


class NativeLLMProvider(ILLMProvider):
    """自研LLM提供者实现"""
    
    def __init__(self, config: Dict[str, Any]):
        self._llm_service = LLMService(config)
        self._initialized = False
    
    async def initialize(self) -> None:
        await self._llm_service.initialize()
        self._initialized = True
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse:
        if not self._initialized:
            await self.initialize()
        return await self._llm_service.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> AsyncIterator[LLMResponse]:
        if not self._initialized:
            await self.initialize()
        async for chunk in self._llm_service.stream_chat(
            messages=messages,
            model=model,
            temperature=temperature,
            **kwargs
        ):
            yield chunk
    
    def get_available_models(self) -> List[str]:
        return self._llm_service.list_models()
    
    async def health_check(self) -> bool:
        return await self._llm_service.health_check()
```

### 2. Agent工厂

```python
# core/factories/agent_factory.py
from typing import Dict, Any, Optional
from core.interfaces.agent import IAgentEngine
from core.agent.engine import AgentEngine

# LangChain实现
try:
    from core.implementations.langchain.langchain_agent import LangChainAgentEngine
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LangChainAgentEngine = None

# LangGraph实现
try:
    from core.implementations.langgraph.langgraph_agent import LangGraphAgentEngine
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    LangGraphAgentEngine = None

class AgentFactory:
    """Agent引擎工厂"""
    
    @staticmethod
    def create(
        implementation: str,
        config: Dict[str, Any],
        llm_provider: Optional[ILLMProvider] = None,
        tool_manager: Optional[IToolManager] = None,
        memory: Optional[IMemory] = None
    ) -> IAgentEngine:
        """
        创建Agent引擎
        
        参数:
            implementation: 实现类型（native/langchain/langgraph）
            config: 配置字典
            llm_provider: LLM提供者（可选，如果未提供则从配置创建）
            tool_manager: 工具管理器（可选）
            memory: 记忆管理器（可选）
        
        返回:
            Agent引擎实例
        """
        # 如果没有提供依赖，从配置创建
        if llm_provider is None:
            llm_provider = LLMFactory.create_from_config(config)
        
        if tool_manager is None:
            tool_manager = ToolFactory.create_from_config(config)
        
        if memory is None:
            memory = MemoryFactory.create_from_config(config)
        
        if implementation == "native":
            return NativeAgentEngine(config, llm_provider, tool_manager, memory)
        elif implementation == "langchain":
            if not LANGCHAIN_AVAILABLE:
                raise ValueError("LangChain未安装")
            return LangChainAgentEngine(config, llm_provider, tool_manager, memory)
        elif implementation == "langgraph":
            if not LANGGRAPH_AVAILABLE:
                raise ValueError("LangGraph未安装")
            return LangGraphAgentEngine(config, llm_provider, tool_manager, memory)
        else:
            raise ValueError(f"不支持的实现类型: {implementation}")
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> IAgentEngine:
        """从配置创建（自动选择实现）"""
        agent_config = config.get("agent", {})
        implementation = agent_config.get("implementation", "native")
        return AgentFactory.create(implementation, config)


class NativeAgentEngine(IAgentEngine):
    """自研Agent引擎实现"""
    
    def __init__(
        self,
        config: Dict[str, Any],
        llm_provider: ILLMProvider,
        tool_manager: IToolManager,
        memory: IMemory
    ):
        self._config = config
        self._llm_provider = llm_provider
        self._tool_manager = tool_manager
        self._memory = memory
        self._engine = None
    
    async def initialize(self) -> None:
        # 将接口适配到现有实现
        # 这里需要适配层将接口转换为现有AgentEngine的调用
        self._engine = AgentEngine(self._config)
        await self._engine.initialize()
    
    async def run_task(
        self,
        task: str,
        conversation_id: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        return await self._engine.run_task(task, conversation_id, **kwargs)
    
    def register_tool(self, tool: Any) -> None:
        self._engine.register_tool(tool)
    
    def get_tools(self) -> List[str]:
        return self._engine.get_tools()
    
    def clear_memory(self) -> None:
        self._engine.clear_memory()
    
    async def cleanup(self) -> None:
        await self._engine.cleanup()
```

### 3. 工具工厂

```python
# core/factories/tool_factory.py
from typing import Dict, Any, List
from core.interfaces.tools import IToolManager
from core.agent.tools import ToolRegistry

# LangChain实现
try:
    from core.implementations.langchain.langchain_tools import LangChainToolManager
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LangChainToolManager = None

class ToolFactory:
    """工具管理器工厂"""
    
    @staticmethod
    def create(implementation: str, config: Dict[str, Any]) -> IToolManager:
        if implementation == "native":
            return NativeToolManager(config)
        elif implementation == "langchain":
            if not LANGCHAIN_AVAILABLE:
                raise ValueError("LangChain未安装")
            return LangChainToolManager(config)
        else:
            raise ValueError(f"不支持的实现类型: {implementation}")
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> IToolManager:
        tool_config = config.get("tools", {})
        implementation = tool_config.get("implementation", "native")
        return ToolFactory.create(implementation, config)


class NativeToolManager(IToolManager):
    """自研工具管理器实现"""
    
    def __init__(self, config: Dict[str, Any]):
        self._registry = ToolRegistry()
    
    def register(self, tool: Any) -> None:
        self._registry.register(tool)
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        return await self._registry.execute(tool_name, arguments)
    
    def list_tools(self) -> List[str]:
        return self._registry.list_tools()
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        tool = self._registry.get_tool(tool_name)
        return tool.to_function_schema()
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        return self._registry.get_function_schemas()
```

### 4. 记忆工厂

```python
# core/factories/memory_factory.py
from typing import Dict, Any, Optional, List
from core.interfaces.memory import IMemory
from core.agent.memory import ShortTermMemory, LongTermMemory

# LangChain实现
try:
    from core.implementations.langchain.langchain_memory import LangChainMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LangChainMemory = None

class MemoryFactory:
    """记忆管理器工厂"""
    
    @staticmethod
    def create(
        implementation: str,
        config: Dict[str, Any],
        storage_manager: Optional[Any] = None
    ) -> IMemory:
        if implementation == "native":
            return NativeMemory(config, storage_manager)
        elif implementation == "langchain":
            if not LANGCHAIN_AVAILABLE:
                raise ValueError("LangChain未安装")
            return LangChainMemory(config)
        else:
            raise ValueError(f"不支持的实现类型: {implementation}")
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> IMemory:
        memory_config = config.get("memory", {})
        implementation = memory_config.get("implementation", "native")
        return MemoryFactory.create(implementation, config)


class NativeMemory(IMemory):
    """自研记忆管理器实现"""
    
    def __init__(self, config: Dict[str, Any], storage_manager: Optional[Any] = None):
        self._short_term = ShortTermMemory()
        self._long_term = LongTermMemory(storage_manager) if storage_manager else None
    
    def add_message(self, role: str, content: str, **kwargs: Any) -> None:
        self._short_term.add_message(role, content, **kwargs)
    
    def get_messages(self) -> List[Dict[str, Any]]:
        return self._short_term.get_messages()
    
    def clear(self) -> None:
        self._short_term.clear()
    
    async def save(self, conversation_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        if self._long_term:
            messages = self.get_messages()
            await self._long_term.save(conversation_id, messages, metadata)
    
    async def load(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        if self._long_term:
            return await self._long_term.load(conversation_id)
        return None
    
    @property
    def message_count(self) -> int:
        return self._short_term.message_count
```

---

## 🧩 组合管理器

### 组件组合管理器

```python
# core/composition/component_manager.py
from typing import Dict, Any, Optional
from core.interfaces.llm import ILLMProvider
from core.interfaces.agent import IAgentEngine
from core.interfaces.tools import IToolManager
from core.interfaces.memory import IMemory
from core.factories.llm_factory import LLMFactory
from core.factories.agent_factory import AgentFactory
from core.factories.tool_factory import ToolFactory
from core.factories.memory_factory import MemoryFactory

class ComponentManager:
    """
    组件管理器
    
    负责创建和管理所有组件，支持运行时切换实现。
    """
    
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._llm_provider: Optional[ILLMProvider] = None
        self._tool_manager: Optional[IToolManager] = None
        self._memory: Optional[IMemory] = None
        self._agent_engine: Optional[IAgentEngine] = None
    
    async def initialize(self) -> None:
        """初始化所有组件"""
        # 创建LLM提供者
        self._llm_provider = LLMFactory.create_from_config(self._config)
        await self._llm_provider.initialize()
        
        # 创建工具管理器
        self._tool_manager = ToolFactory.create_from_config(self._config)
        
        # 创建记忆管理器
        self._memory = MemoryFactory.create_from_config(self._config)
        
        # 创建Agent引擎（注入依赖）
        agent_config = self._config.get("agent", {})
        implementation = agent_config.get("implementation", "native")
        self._agent_engine = AgentFactory.create(
            implementation=implementation,
            config=self._config,
            llm_provider=self._llm_provider,
            tool_manager=self._tool_manager,
            memory=self._memory
        )
        await self._agent_engine.initialize()
    
    def switch_llm_implementation(self, implementation: str) -> None:
        """切换LLM实现"""
        self._llm_provider = LLMFactory.create(implementation, self._config)
    
    def switch_agent_implementation(self, implementation: str) -> None:
        """切换Agent实现"""
        self._agent_engine = AgentFactory.create(
            implementation=implementation,
            config=self._config,
            llm_provider=self._llm_provider,
            tool_manager=self._tool_manager,
            memory=self._memory
        )
    
    def switch_tool_implementation(self, implementation: str) -> None:
        """切换工具实现"""
        self._tool_manager = ToolFactory.create(implementation, self._config)
        # 需要重新创建Agent引擎以使用新的工具管理器
        agent_config = self._config.get("agent", {})
        implementation = agent_config.get("implementation", "native")
        self._agent_engine = AgentFactory.create(
            implementation=implementation,
            config=self._config,
            llm_provider=self._llm_provider,
            tool_manager=self._tool_manager,
            memory=self._memory
        )
    
    def switch_memory_implementation(self, implementation: str) -> None:
        """切换记忆实现"""
        self._memory = MemoryFactory.create(implementation, self._config)
        # 需要重新创建Agent引擎以使用新的记忆管理器
        agent_config = self._config.get("agent", {})
        implementation = agent_config.get("implementation", "native")
        self._agent_engine = AgentFactory.create(
            implementation=implementation,
            config=self._config,
            llm_provider=self._llm_provider,
            tool_manager=self._tool_manager,
            memory=self._memory
        )
    
    @property
    def llm_provider(self) -> ILLMProvider:
        return self._llm_provider
    
    @property
    def agent_engine(self) -> IAgentEngine:
        return self._agent_engine
    
    @property
    def tool_manager(self) -> IToolManager:
        return self._tool_manager
    
    @property
    def memory(self) -> IMemory:
        return self._memory
```

---

## ⚙️ 配置示例

### 配置文件

```yaml
# config/default.yaml

# LLM配置
llm:
  implementation: "native"  # native/litellm/langchain
  default_model: "gpt-3.5-turbo"
  # ... 其他LLM配置

# Agent配置
agent:
  implementation: "native"  # native/langchain/langgraph
  max_iterations: 10
  # ... 其他Agent配置

# 工具配置
tools:
  implementation: "native"  # native/langchain
  # ... 其他工具配置

# 记忆配置
memory:
  implementation: "native"  # native/langchain
  max_messages: 100
  # ... 其他记忆配置

# 运行时切换配置（可选）
runtime:
  allow_switching: true  # 允许运行时切换实现
  hot_reload: false      # 是否支持热重载
```

### 运行时切换示例

```python
# 使用示例
from core.composition.component_manager import ComponentManager

# 初始化
config = load_config()
manager = ComponentManager(config)
await manager.initialize()

# 使用Agent
result = await manager.agent_engine.run_task("查询天气")

# 运行时切换到LangChain实现
manager.switch_agent_implementation("langchain")
result = await manager.agent_engine.run_task("查询天气")

# 切换到LangGraph实现
manager.switch_agent_implementation("langgraph")
result = await manager.agent_engine.run_task("查询天气")

# 混合使用：LangChain Agent + 自研工具 + LangChain记忆
manager.switch_agent_implementation("langchain")
manager.switch_tool_implementation("native")
manager.switch_memory_implementation("langchain")
result = await manager.agent_engine.run_task("查询天气")
```

---

## 📁 目录结构

```
core/
├── interfaces/              # 抽象接口层
│   ├── __init__.py
│   ├── llm.py              # ILLMProvider
│   ├── agent.py            # IAgentEngine
│   ├── tools.py            # IToolManager
│   ├── memory.py           # IMemory
│   ├── workflow.py          # IWorkflow
│   └── chain.py            # IChain
│
├── factories/              # 工厂层
│   ├── __init__.py
│   ├── llm_factory.py      # LLMFactory
│   ├── agent_factory.py    # AgentFactory
│   ├── tool_factory.py     # ToolFactory
│   ├── memory_factory.py   # MemoryFactory
│   └── workflow_factory.py # WorkflowFactory
│
├── implementations/        # 具体实现层
│   ├── native/            # 自研实现
│   │   ├── __init__.py
│   │   ├── native_llm.py
│   │   ├── native_agent.py
│   │   ├── native_tools.py
│   │   └── native_memory.py
│   │
│   ├── langchain/         # LangChain实现
│   │   ├── __init__.py
│   │   ├── langchain_llm.py
│   │   ├── langchain_agent.py
│   │   ├── langchain_tools.py
│   │   └── langchain_memory.py
│   │
│   └── langgraph/         # LangGraph实现
│       ├── __init__.py
│       ├── langgraph_workflow.py
│       └── langgraph_agent.py
│
└── composition/           # 组合管理
    ├── __init__.py
    └── component_manager.py
```

---

## 🎯 优势

### 1. 完全解耦
- ✅ 接口与实现完全分离
- ✅ 可以独立替换任何组件
- ✅ 不影响其他组件

### 2. 灵活组装
- ✅ 可以随意组合不同实现
- ✅ 支持运行时切换
- ✅ 支持混合使用

### 3. 易于扩展
- ✅ 新增实现只需实现接口
- ✅ 无需修改现有代码
- ✅ 符合开闭原则

### 4. 向后兼容
- ✅ 现有代码无需修改
- ✅ 通过适配器模式兼容
- ✅ 渐进式迁移

---

## 🚀 实施计划

### 阶段1：定义接口（1周）
- [ ] 创建 `core/interfaces/` 目录
- [ ] 定义所有抽象接口
- [ ] 编写接口文档

### 阶段2：实现工厂（1周）
- [ ] 创建 `core/factories/` 目录
- [ ] 实现所有工厂类
- [ ] 实现自研适配器（将现有实现适配到接口）

### 阶段3：实现LangChain适配器（2周）
- [ ] 创建 `core/implementations/langchain/` 目录
- [ ] 实现LangChain版本的各个接口
- [ ] 编写单元测试

### 阶段4：实现LangGraph适配器（2周）
- [ ] 创建 `core/implementations/langgraph/` 目录
- [ ] 实现LangGraph版本的各个接口
- [ ] 编写单元测试

### 阶段5：组合管理器（1周）
- [ ] 创建 `core/composition/` 目录
- [ ] 实现ComponentManager
- [ ] 实现运行时切换功能

### 阶段6：集成和测试（1周）
- [ ] 集成到现有系统
- [ ] 编写集成测试
- [ ] 更新文档

**总时间**：8-9周

---

## 📝 使用示例

### 示例1：使用自研实现

```python
config = {
    "llm": {"implementation": "native"},
    "agent": {"implementation": "native"},
    "tools": {"implementation": "native"},
    "memory": {"implementation": "native"}
}

manager = ComponentManager(config)
await manager.initialize()

result = await manager.agent_engine.run_task("查询天气")
```

### 示例2：使用LangChain实现

```python
config = {
    "llm": {"implementation": "langchain"},
    "agent": {"implementation": "langchain"},
    "tools": {"implementation": "langchain"},
    "memory": {"implementation": "langchain"}
}

manager = ComponentManager(config)
await manager.initialize()

result = await manager.agent_engine.run_task("查询天气")
```

### 示例3：混合使用

```python
config = {
    "llm": {"implementation": "native"},      # 自研LLM
    "agent": {"implementation": "langchain"}, # LangChain Agent
    "tools": {"implementation": "native"},    # 自研工具
    "memory": {"implementation": "langchain"}  # LangChain记忆
}

manager = ComponentManager(config)
await manager.initialize()

result = await manager.agent_engine.run_task("查询天气")
```

### 示例4：运行时切换

```python
manager = ComponentManager(config)
await manager.initialize()

# 使用自研实现
result1 = await manager.agent_engine.run_task("任务1")

# 切换到LangChain
manager.switch_agent_implementation("langchain")
result2 = await manager.agent_engine.run_task("任务2")

# 切换到LangGraph
manager.switch_agent_implementation("langgraph")
result3 = await manager.agent_engine.run_task("任务3")
```

---

## ✅ 总结

这个架构设计提供了：

1. **完全抽象**：所有核心功能都有抽象接口
2. **灵活切换**：可以在运行时切换任何实现
3. **随意组装**：可以混合使用不同实现
4. **易于扩展**：新增实现只需实现接口
5. **向后兼容**：现有代码无需修改

通过这个架构，你可以：
- ✅ 使用LangChain的Agent + 自研的工具 + LangGraph的工作流
- ✅ 运行时切换实现，无需重启
- ✅ 逐步迁移，不影响现有功能
- ✅ 灵活组合，发挥各框架优势
