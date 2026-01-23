# 前端工具列表为空问题修复

## 问题描述

前端Agent页面显示"暂无可用工具"，但后端实际上已经注册了工具（如web_search、fetch_webpage）。

## 根本原因

**后端API返回格式与前端期望不匹配**：

1. **后端返回格式**（修复前）：
```python
{
    "tools": ["web_search", "fetch_webpage"],  # List[str]
    "schemas": [...],
    "count": 2
}
```

2. **前端期望格式**：
```typescript
{
    tools: {  // Record<string, any>
        "web_search": {
            name: "web_search",
            description: "...",
            parameters: {...}
        },
        "fetch_webpage": {...}
    },
    schemas: [...],
    count: 2
}
```

3. **前端代码**（`src/stores/agent.ts`）：
```typescript
const data = await agentApi.listTools()
tools.value = data.tools  // 期望是对象，但收到的是数组
```

当`data.tools`是数组时，`Object.keys(tools.value).length === 0`为true，导致显示"暂无可用工具"。

## 修复方案

修改后端API（`api/routes/agent.py`的`list_tools`方法），将工具列表转换为字典格式：

```python
# 将工具列表转换为字典格式，方便前端使用
tools_dict = {}
for schema in tool_schemas:
    tool_name = schema.get("function", {}).get("name", "")
    if tool_name:
        tools_dict[tool_name] = {
            "name": tool_name,
            "description": schema.get("function", {}).get("description", ""),
            "parameters": schema.get("function", {}).get("parameters", {}),
        }

# 如果schema中没有但工具名称列表中有，也添加进去
for tool_name in tool_names:
    if tool_name not in tools_dict:
        tools_dict[tool_name] = {
            "name": tool_name,
            "description": "工具描述不可用",
            "parameters": {},
        }

return {
    "tools": tools_dict,  # 转换为字典格式
    "schemas": tool_schemas,
    "count": len(tool_names),
}
```

## 修复后的返回格式

```json
{
    "tools": {
        "web_search": {
            "name": "web_search",
            "description": "通过搜索引擎查询互联网内容，返回搜索结果摘要",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询关键词"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大返回结果数",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        },
        "fetch_webpage": {
            "name": "fetch_webpage",
            "description": "...",
            "parameters": {...}
        }
    },
    "schemas": [...],
    "count": 2
}
```

## 测试步骤

1. **重启后端服务**（应用代码更改）
2. **刷新前端页面**
3. **检查工具列表**：
   - 应该能看到已注册的工具（web_search、fetch_webpage等）
   - 每个工具显示名称和描述

## 验证方法

使用API测试：
```bash
curl http://localhost:8000/api/v1/agent/tools
```

应该返回包含`tools`字典的JSON响应。

## 相关文件

- `api/routes/agent.py` - 后端API修复
- `src/stores/agent.ts` - 前端状态管理
- `src/components/agent/ToolList.vue` - 前端工具列表组件

## 注意事项

1. **需要重启后端服务**才能应用修复
2. **工具注册**：确保`web_tools`已在AgentEngine初始化时注册
3. **配置检查**：确认`config/default.yaml`中`agent.web_tools.enabled: true`
