# LLM服务模块功能设计文档

## 📋 功能概述

### 功能名称
LLM服务模块（LLM Service）

### 功能目的
提供统一的多模型LLM接口，支持多种AI服务提供商，实现对话、流式输出、上下文管理等功能。

### 解决的问题
1. **多提供商支持**：统一不同LLM提供商的接口
2. **接口复杂性**：简化LLM调用的复杂性
3. **上下文管理**：统一管理对话历史
4. **成本控制**：Token计算和成本估算

### 使用场景
- 简单的单次对话
- 带上下文的连续对话
- 流式输出场景
- 批量处理任务

---

## 🏗️ 技术架构

### 架构设计

```
core/llm/
├── service.py           # LLM服务主类
├── context.py           # 对话上下文管理
├── models.py            # 数据模型
└── adapters/            # 适配器实现
    ├── base.py          # 适配器基类
    ├── openai_adapter.py
    ├── claude_adapter.py
    └── ollama_adapter.py
```

### 类设计

```
LLMService (继承BaseService)
    ├── chat() - 发送聊天请求
    ├── stream_chat() - 流式聊天
    ├── calculate_tokens() - 计算Token
    └── estimate_cost() - 估算成本

ConversationContext
    ├── add_message() - 添加消息
    ├── get_messages() - 获取消息列表
    └── clear() - 清空上下文

BaseLLMAdapter (继承BaseAdapter)
    ├── call() - 调用LLM接口
    └── stream_call() - 流式调用
```

---

## 🔌 接口设计

### LLMService（LLM服务主类）

#### 核心职责
- 统一的多模型LLM接口
- 适配器管理和切换
- 上下文管理
- Token计算和成本估算

#### 公共接口

```python
class LLMService(BaseService):
    """LLM服务主类"""
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """发送聊天请求
        
        参数:
            messages: 消息列表
            model: 模型名称（可选，使用默认模型）
            temperature: 温度参数
            max_tokens: 最大token数
        
        返回:
            LLMResponse对象
        """
        pass
    
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[LLMResponse]:
        """流式聊天
        
        参数:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
        
        生成器:
            逐个返回响应块
        """
        pass
    
    def calculate_tokens(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> int:
        """计算Token数量
        
        参数:
            text: 文本内容
            model: 模型名称
        
        返回:
            Token数量
        """
        pass
```

### ConversationContext（对话上下文）

#### 核心职责
- 管理对话历史
- 维护上下文状态
- 支持上下文清理和限制

#### 公共接口

```python
class ConversationContext:
    """对话上下文管理"""
    
    def add_message(
        self,
        role: str,
        content: str,
    ) -> None:
        """添加消息
        
        参数:
            role: 角色（user/assistant/system）
            content: 消息内容
        """
        pass
    
    def get_messages(self) -> List[Dict[str, str]]:
        """获取消息列表
        
        返回:
            消息列表
        """
        pass
    
    def clear(self) -> None:
        """清空上下文"""
        pass
```

---

## 🔧 实现细节

### 关键技术选型及理由

1. **适配器模式**
   - **选型**：使用适配器模式统一多提供商接口
   - **理由**：便于扩展，降低耦合

2. **异步流式处理**
   - **选型**：使用异步生成器实现流式输出
   - **理由**：提升用户体验，减少等待时间

3. **Token计算库**
   - **选型**：使用tiktoken（OpenAI）或类似库
   - **理由**：准确计算Token数量，便于成本控制

### 核心算法或流程

#### 聊天请求流程

```
1. 验证参数
   ↓
2. 选择适配器（根据model）
   ↓
3. 调用适配器接口
   ↓
4. 处理响应
   ↓
5. 计算Token和成本
   ↓
6. 返回结果
```

### 异常处理策略

1. **参数验证错误**：抛出`ValidationError`
2. **适配器调用失败**：抛出`LLMError`，支持重试
3. **Token计算失败**：记录警告，返回估算值

---

## 🔗 依赖关系

### 依赖的其他模块
- `core/base/service.py` - 服务基类
- `core/base/adapter.py` - 适配器基类
- `infrastructure/config/` - 配置管理
- `infrastructure/log/` - 日志管理

### 外部依赖库
- `httpx`：异步HTTP客户端
- `tiktoken`：Token计算（OpenAI模型）

---

## 🧪 测试策略

### 单元测试计划
1. **服务功能测试**
   - 测试chat方法
   - 测试stream_chat方法
   - 测试Token计算

2. **上下文管理测试**
   - 测试消息添加
   - 测试上下文清理
   - 测试上下文限制

3. **适配器测试**
   - 测试适配器切换
   - 测试适配器调用

---

## 📝 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|---------|--------|
| 1.0 | 2026-01-21 | 初始版本，定义LLM服务模块 | - |

---

## 📚 相关文档

- [架构方案文档](../../AI框架架构方案文档.md)
- [基础服务框架设计文档](base-service-framework.md)
- [架构决策记录](../architecture/decisions/ADR-0001-适配器模式.md)
