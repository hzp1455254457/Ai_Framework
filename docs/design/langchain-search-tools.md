# LangChain搜索工具说明

## 📚 LangChain搜索工具概述

LangChain提供了两种DuckDuckGo搜索工具：

### 1. DuckDuckGoSearchRun
- **功能**：执行搜索并返回文本结果
- **返回格式**：字符串（搜索结果摘要）
- **适用场景**：简单搜索，需要文本结果

### 2. DuckDuckGoSearchResults
- **功能**：执行搜索并返回结构化结果
- **返回格式**：JSON格式的结构化数据
- **适用场景**：需要详细搜索结果（标题、URL、摘要等）

## 🔧 当前实现状态

### 当前使用
- ✅ **自研web_search工具**：已修复，使用`ddgs`库
- ❌ **LangChain搜索工具**：未集成

### 两种方案对比

| 特性 | 自研web_search | LangChain搜索工具 |
|------|---------------|------------------|
| **实现方式** | 使用`ddgs`库 | 使用`langchain_community.tools` |
| **返回格式** | 格式化文本 | 字符串或JSON |
| **集成度** | 已集成到框架 | 需要额外集成 |
| **灵活性** | 高度可定制 | 标准LangChain接口 |
| **维护成本** | 需要维护 | LangChain维护 |
| **LangChain兼容** | 需要转换 | 原生支持 |

## 💡 集成建议

### 方案1：继续使用自研工具（推荐）
**优势**：
- ✅ 已修复并测试通过
- ✅ 返回格式统一（格式化文本）
- ✅ 完全可控
- ✅ 已集成到框架

**适用场景**：
- 当前使用自研工具已满足需求
- 需要统一的返回格式
- 需要高度定制

### 方案2：集成LangChain搜索工具
**优势**：
- ✅ 原生LangChain支持
- ✅ 无需维护
- ✅ 标准接口

**适用场景**：
- 需要与LangChain生态完全兼容
- 需要结构化搜索结果
- 希望减少维护成本

### 方案3：混合使用（最佳）
**优势**：
- ✅ 灵活性最高
- ✅ 可以根据配置选择
- ✅ 向后兼容

**实现方式**：
1. 保留自研`web_search`工具
2. 添加LangChain搜索工具作为可选工具
3. 通过配置选择使用哪个工具

## 🚀 集成LangChain搜索工具（可选）

如果需要集成LangChain搜索工具，可以：

### 1. 在LangChainToolManager中自动注册

```python
# core/implementations/langchain/langchain_tools.py

def __init__(self, config: Dict[str, Any]):
    # ... 现有代码 ...
    
    # 可选：自动注册LangChain搜索工具
    if config.get("tools", {}).get("auto_register_langchain_search", False):
        try:
            from langchain_community.tools import DuckDuckGoSearchRun
            search_tool = DuckDuckGoSearchRun()
            self._tools[search_tool.name] = search_tool
        except ImportError:
            pass  # langchain_community未安装
```

### 2. 在配置文件中启用

```yaml
# config/default.yaml
tools:
  implementation: "langchain"
  auto_register_langchain_search: true  # 自动注册LangChain搜索工具
```

### 3. 手动注册

```python
from langchain_community.tools import DuckDuckGoSearchRun
from core.composition.component_manager import ComponentManager

# 获取工具管理器
tool_manager = component_manager.tool_manager

# 注册LangChain搜索工具
search_tool = DuckDuckGoSearchRun()
tool_manager.register(search_tool)
```

## 📊 推荐方案

**推荐继续使用自研web_search工具**，原因：

1. ✅ **已修复并测试**：使用`ddgs`库，稳定可靠
2. ✅ **返回格式统一**：格式化文本，易于Agent理解
3. ✅ **完全集成**：已集成到框架，无需额外配置
4. ✅ **向后兼容**：现有代码无需修改

**如果未来需要**：
- 可以添加LangChain搜索工具作为可选工具
- 通过配置选择使用哪个工具
- 支持混合使用

## 🔍 使用示例

### 当前自研工具（已修复）

```python
from core.agent.tools.web_tools import web_search

# 使用自研工具
result = await web_search("现在几点钟了", max_results=3)
# 返回：格式化文本结果
```

### LangChain搜索工具（如果集成）

```python
from langchain_community.tools import DuckDuckGoSearchRun

# 使用LangChain工具
search_tool = DuckDuckGoSearchRun()
result = await search_tool.ainvoke({"query": "现在几点钟了"})
# 返回：字符串结果
```

## 📝 总结

- ✅ LangChain确实有搜索工具（DuckDuckGoSearchRun/DuckDuckGoSearchResults）
- ✅ 当前使用自研web_search工具（已修复，稳定可靠）
- ✅ 可以集成LangChain搜索工具作为可选功能
- ✅ 推荐继续使用自研工具，保持当前架构
