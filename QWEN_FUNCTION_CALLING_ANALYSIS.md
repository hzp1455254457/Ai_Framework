# 通义千问Function Calling测试结果分析

## 测试结果总结

根据测试脚本运行结果：

### ✅ 测试3成功：在parameters中传递tools参数
- **请求格式**：
```json
{
  "model": "qwen-turbo",
  "input": {
    "messages": [...]
  },
  "parameters": {
    "temperature": 0.7,
    "tools": [...]  // ✅ 正确位置
  }
}
```

- **结果**：✅ 成功检测到tool_calls
- **工具调用**：
  - 函数: web_search
  - 参数: {"max_results": 5, "query": "Python异步编程的最新信息"}

### ❌ 测试2失败：在input中传递tools参数
- **请求格式**：
```json
{
  "model": "qwen-turbo",
  "input": {
    "messages": [...],
    "tools": [...]  // ❌ 错误位置
  },
  "parameters": {
    "temperature": 0.7
  }
}
```

- **结果**：❌ 请求失败（代码错误：tool_calls变量未定义）

## 问题根源

**我们的代码错误**：在`qwen_adapter.py`中，我们将tools放在了`input.tools`中，但通义千问API要求tools必须放在`parameters.tools`中！

### 修复前（错误）：
```python
if "functions" in kwargs:
    functions = kwargs.pop("functions")
    if functions:
        request_data["input"]["tools"] = functions  # ❌ 错误位置
```

### 修复后（正确）：
```python
if "functions" in kwargs:
    functions = kwargs.pop("functions")
    if functions:
        request_data["parameters"]["tools"] = functions  # ✅ 正确位置
```

## 为什么不会互联网搜索

1. **工具参数位置错误**：tools被放在了`input.tools`而不是`parameters.tools`
2. **通义千问API不接受**：API忽略了`input.tools`中的工具定义
3. **LLM没有收到工具定义**：因此不会调用工具
4. **结果**：Agent模式无法使用工具进行互联网搜索

## 修复方案

已修复`core/llm/adapters/qwen_adapter.py`：
- 将tools从`input.tools`移动到`parameters.tools`
- 与测试脚本验证的正确格式一致

## 验证步骤

1. **重启后端服务**（应用修复）
2. **测试Agent模式**：
   - 在前端勾选"Agent模式"
   - 发送消息："请使用web_search工具搜索Python异步编程"
   - 应该能看到工具调用和执行结果

3. **检查后端日志**：
   - 确认tools参数被正确传递到`parameters.tools`
   - 确认LLM返回了tool_calls

## 结论

✅ **通义千问支持Function Calling**
- 但必须将tools放在`parameters.tools`中
- 不能放在`input.tools`中

✅ **问题已修复**
- 代码已更新为正确的参数位置
- 需要重启后端服务应用修复
