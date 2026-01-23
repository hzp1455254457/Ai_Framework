# Agent工具调用问题修复说明

## 问题描述
大模型在Agent模式下无法连接互联网搜索，工具调用功能不工作。

## 根本原因
1. **LLMService.chat方法缺少functions参数支持**
   - AgentEngine传递了functions参数，但LLMService.chat方法没有接收
   - 导致工具schema无法传递给LLM适配器

2. **通义千问适配器可能不支持Function Calling**
   - 默认模型是qwen-turbo（通义千问）
   - 通义千问API可能不完全支持Function Calling功能
   - 需要检查通义千问API文档确认是否支持tools参数

## 已修复的问题

### 1. LLMService.chat方法
- ✅ 添加了`functions`参数支持
- ✅ 添加了`**kwargs`参数传递
- ✅ 将functions参数传递给适配器

### 2. 通义千问适配器
- ✅ 添加了tools参数支持（将functions转换为tools格式）
- ✅ 添加了tool_calls解析逻辑
- ✅ 兼容function_call格式

## 解决方案

### 方案1：使用支持Function Calling的模型（推荐）
如果通义千问不支持Function Calling，建议切换到OpenAI模型：

1. 修改 `config/default.yaml`:
```yaml
llm:
  default_model: "gpt-3.5-turbo"  # 或 "gpt-4"
```

2. 确保OpenAI适配器已配置API密钥：
```yaml
adapters:
  openai-adapter:
    api_key: "sk-..."  # 你的OpenAI API密钥
```

### 方案2：检查通义千问API文档
查看通义千问最新API文档，确认：
- 是否支持tools/function calling
- 参数格式是什么
- 需要哪个版本的模型

### 方案3：测试当前修复
重启后端服务后测试：
1. 确保Agent模式已启用
2. 发送明确要求使用工具的消息
3. 查看后端日志，确认工具schema是否传递
4. 检查LLM响应中是否包含tool_calls

## 测试步骤

1. **重启后端服务**（应用代码更改）
2. **测试Agent模式**：
   ```bash
   curl -X POST http://localhost:8000/api/v1/llm/chat \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [{"role": "user", "content": "请使用web_search工具搜索Python异步编程"}],
       "use_agent": true
     }'
   ```
3. **检查响应**：
   - 查看metadata中是否有tool_calls
   - 查看后端日志，确认工具是否被调用

## 注意事项

1. **模型兼容性**：不是所有LLM模型都支持Function Calling
2. **API格式差异**：不同提供商的Function Calling格式可能不同
3. **工具注册**：确保web_tools已正确注册到AgentEngine

## 后续优化建议

1. 添加模型Function Calling能力检测
2. 自动选择支持Function Calling的模型
3. 提供更友好的错误提示
4. 添加工具调用调试日志
