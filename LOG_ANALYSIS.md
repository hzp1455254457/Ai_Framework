# 日志分析和问题诊断

## 问题描述
1. 前端工具列表为空（显示"暂无可用工具"）
2. Agent模式无法调用工具进行互联网搜索

## 可能的原因分析

### 1. 工具注册问题

**检查点**：
- Agent引擎初始化时是否正确调用了`register_web_tools`
- 工具注册过程中是否出现异常
- 配置文件中`web_tools.enabled`是否为`true`

**代码位置**：
- `core/agent/engine.py` 第117-127行：工具注册逻辑
- `core/agent/tools/web_tools_registry.py`：工具创建和注册

**可能的问题**：
1. 工具注册时出现异常但被捕获，只记录警告
2. 配置读取错误，`web_tools.enabled`实际为`false`
3. 工具注册函数未正确导入或调用

### 2. API返回格式问题

**已修复**：后端API已修改为返回字典格式，但需要确认：
- 前端是否正确解析响应
- 工具字典的键值是否正确

### 3. 工具调用链路问题

**检查点**：
- AgentEngine是否正确传递`functions`参数给LLMService
- LLMService是否正确传递`functions`给适配器
- 通义千问适配器是否正确处理`tools`参数
- LLM响应中是否包含`tool_calls`

**代码位置**：
- `core/agent/engine.py` 第209-226行：工具schema传递
- `core/llm/service.py` 第310行：functions参数传递
- `core/llm/adapters/qwen_adapter.py` 第137-144行：tools参数处理

### 4. 日志文件未生成

**可能原因**：
- 服务未正常启动
- 日志目录未创建
- 日志记录器未正确初始化

## 诊断步骤

### 步骤1：检查工具注册
```python
# 运行测试脚本
python test_tool_registration.py
```

**预期结果**：
- 工具数量 > 0
- 工具名称包含 `web_search` 和 `fetch_webpage`
- Schema数量 > 0

### 步骤2：检查API响应
```bash
curl http://localhost:8000/api/v1/agent/tools
```

**预期结果**：
```json
{
  "tools": {
    "web_search": {...},
    "fetch_webpage": {...}
  },
  "count": 2
}
```

### 步骤3：检查后端日志
查看以下日志文件：
- `logs/agent_api.log` - Agent API日志
- `logs/llm_api.log` - LLM API日志

**关键日志**：
- "已注册互联网工具: web_search, fetch_webpage"
- "收到工具列表请求"
- "工具列表响应: count=2"
- "检查工具注册情况: 已注册工具=..."
- "传递工具schema给LLM: functions参数已设置"

### 步骤4：检查前端日志
- 浏览器控制台（F12）
- `logs/frontend.log`

**关键日志**：
- "开始加载工具列表"
- "工具列表API响应"
- "工具列表加载完成"

## 常见问题和解决方案

### 问题1：工具数量为0

**可能原因**：
1. `web_tools.enabled = false` 在配置中
2. 工具注册异常被静默捕获
3. Agent引擎初始化失败

**解决方案**：
1. 检查`config/default.yaml`中`agent.web_tools.enabled`
2. 查看Agent引擎初始化日志
3. 检查工具注册异常信息

### 问题2：工具已注册但API返回空

**可能原因**：
1. API返回格式转换错误
2. Schema解析失败

**解决方案**：
1. 检查`api/routes/agent.py`的`list_tools`方法
2. 验证schema格式是否正确

### 问题3：工具调用不工作

**可能原因**：
1. `functions`参数未传递到适配器
2. 通义千问适配器`tools`参数位置错误（已修复）
3. LLM响应中无`tool_calls`

**解决方案**：
1. 检查日志中是否有"传递工具schema给LLM"
2. 检查日志中是否有"添加工具定义到parameters.tools"
3. 检查日志中是否有"检测到tool_calls"

## 下一步操作

1. **运行测试脚本**：`python test_tool_registration.py`
2. **检查API响应**：`curl http://localhost:8000/api/v1/agent/tools`
3. **查看日志文件**：检查`logs/`目录下的日志文件
4. **测试Agent模式**：在前端测试工具调用
5. **分析日志**：根据日志定位具体问题

## 日志文件位置

- `F:\Ai_Framework\logs\agent_api.log` - Agent API日志
- `F:\Ai_Framework\logs\llm_api.log` - LLM API日志
- `F:\Ai_Framework\logs\frontend.log` - 前端日志

## 查看日志命令

```powershell
# 实时查看Agent API日志
Get-Content F:\Ai_Framework\logs\agent_api.log -Wait -Tail 20

# 实时查看LLM API日志
Get-Content F:\Ai_Framework\logs\llm_api.log -Wait -Tail 20

# 查看所有日志文件
Get-ChildItem F:\Ai_Framework\logs\*.log | ForEach-Object {
    Write-Host "`n=== $($_.Name) ==="
    Get-Content $_.FullName -Tail 10
}
```
