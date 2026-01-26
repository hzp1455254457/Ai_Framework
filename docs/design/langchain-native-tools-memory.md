# LangChain原生工具和记忆使用说明

## 📋 修改概述

根据要求，在使用LangChain Agent框架后，记忆和工具都使用LangChain原生的，不使用自定义封装工具。

## ✅ 已完成的修改

### 1. LangChainToolManager 修改

#### 1.1 自动注册LangChain原生搜索工具
- ✅ 在初始化时自动注册 `DuckDuckGoSearchRun` 工具
- ✅ 通过配置 `tools.auto_register_langchain_tools` 控制是否自动注册
- ✅ 默认启用自动注册

#### 1.2 拒绝注册自研工具
- ✅ 添加配置选项 `tools.allow_native_tools`（默认 `false`）
- ✅ 当 `allow_native_tools=false` 时，拒绝注册自研工具
- ✅ 如果尝试注册自研工具，会抛出明确的错误提示

#### 1.3 代码修改位置
- `core/implementations/langchain/langchain_tools.py`
  - 添加 `langchain_community.tools` 导入
  - 添加 `_auto_register_langchain_tools` 方法
  - 修改 `register` 方法，添加自研工具检查
  - 修改 `__init__` 方法，自动注册LangChain工具

### 2. LangChainMemory 确认

#### 2.1 已使用LangChain原生组件
- ✅ 使用 `ConversationBufferMemory`（LangChain原生）
- ✅ 使用 `ConversationSummaryMemory`（LangChain原生）
- ✅ 使用 `HumanMessage`、`AIMessage`（LangChain原生消息类型）
- ✅ 完全使用LangChain原生Memory组件，无自定义封装

#### 2.2 代码位置
- `core/implementations/langchain/langchain_memory.py`
  - 已完全使用LangChain原生Memory组件
  - 无需修改

### 3. 配置文件更新

#### 3.1 工具配置
```yaml
tools:
  implementation: "langchain"  # 使用LangChain实现
  auto_register_langchain_tools: true  # 自动注册LangChain原生工具
  allow_native_tools: false  # 不允许注册自研工具
```

#### 3.2 记忆配置
```yaml
memory:
  implementation: "langchain"  # 使用LangChain实现
```

### 4. 依赖更新

#### 4.1 requirements.txt
- ✅ 添加 `langchain-community>=0.0.20` 注释说明
- ✅ 已确认 `langchain-community` 已安装

## 🔧 使用说明

### 工具使用

#### 自动注册的LangChain工具
- **DuckDuckGoSearchRun**：自动注册，无需手动配置
- 工具名称：`duckduckgo_search`

#### 注册自研工具（已禁用）
```python
# 如果 allow_native_tools=false，以下代码会抛出错误
from core.agent.tools import Tool
tool = Tool(name="my_tool", ...)
tool_manager.register(tool)  # ❌ 会抛出 ValueError
```

#### 注册LangChain原生工具（允许）
```python
from langchain_community.tools import DuckDuckGoSearchRun
search_tool = DuckDuckGoSearchRun()
tool_manager.register(search_tool)  # ✅ 允许
```

### 记忆使用

#### LangChain原生Memory
- ✅ 完全使用LangChain原生Memory组件
- ✅ 支持 `ConversationBufferMemory`、`ConversationSummaryMemory` 等
- ✅ 使用LangChain原生消息类型（`HumanMessage`、`AIMessage`）

## 📊 配置选项说明

### tools.auto_register_langchain_tools
- **类型**：`boolean`
- **默认值**：`true`
- **说明**：是否自动注册LangChain原生工具（如DuckDuckGo搜索）

### tools.allow_native_tools
- **类型**：`boolean`
- **默认值**：`false`
- **说明**：是否允许注册自研工具
  - `false`：只允许LangChain原生工具（推荐）
  - `true`：允许自研工具（向后兼容）

## 🎯 优势

### 1. 完全使用LangChain原生组件
- ✅ 工具：使用LangChain原生工具（DuckDuckGoSearchRun等）
- ✅ 记忆：使用LangChain原生Memory组件
- ✅ 更好的兼容性和稳定性

### 2. 减少维护成本
- ✅ 无需维护自定义工具封装
- ✅ LangChain社区维护工具
- ✅ 自动获得工具更新

### 3. 更好的生态集成
- ✅ 与LangChain生态完全兼容
- ✅ 可以使用LangChain社区的所有工具
- ✅ 易于扩展和集成

## ⚠️ 注意事项

### 1. 自研工具注册
- 如果 `allow_native_tools=false`，尝试注册自研工具会抛出错误
- 如果需要使用自研工具，需要：
  1. 将自研工具转换为LangChain Tool格式
  2. 或设置 `allow_native_tools=true`

### 2. 工具名称冲突
- LangChain原生工具名称可能与自研工具冲突
- 建议使用LangChain原生工具名称

### 3. 依赖要求
- 需要安装 `langchain-community` 包
- 需要安装 `duckduckgo-search` 或 `ddgs` 包（用于搜索工具）

## 🔄 迁移指南

### 从自研工具迁移到LangChain原生工具

#### 1. 搜索工具迁移
**之前（自研工具）**：
```python
from core.agent.tools.web_tools import web_search
result = await web_search("查询内容")
```

**现在（LangChain原生工具）**：
```python
# 工具已自动注册，Agent会自动使用
# 工具名称：duckduckgo_search
```

#### 2. 工具注册迁移
**之前（自研工具）**：
```python
from core.agent.tools import Tool
tool = Tool(name="my_tool", ...)
tool_manager.register(tool)
```

**现在（LangChain原生工具）**：
```python
from langchain_community.tools import SomeTool
tool = SomeTool()
tool_manager.register(tool)
```

## 📝 总结

- ✅ **工具**：完全使用LangChain原生工具（DuckDuckGoSearchRun等）
- ✅ **记忆**：完全使用LangChain原生Memory组件
- ✅ **配置**：通过配置文件控制工具注册行为
- ✅ **兼容性**：保持向后兼容（可通过配置允许自研工具）

## 🚀 下一步

1. 测试LangChain原生工具的使用
2. 验证记忆功能正常工作
3. 根据需要添加更多LangChain原生工具
