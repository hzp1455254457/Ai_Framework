# llm-service Specification Delta

## MODIFIED Requirements

### Requirement: LangChain LLM Provider Implementation
系统 SHALL 提供完整的LangChain LLM提供者实现，支持将ILLMProvider转换为LangChain LLM。

**Rationale**: 通过完整的LangChain LLM适配器实现，可以使用LangChain生态的所有LLM相关功能。

#### Scenario: Use LangChain LLM Provider
**Given** 系统已安装LangChain，配置使用langchain实现
**When** 用户创建LLM提供者并调用chat方法
**Then** 系统应：
1. 创建LangChainLLMWrapper包装ILLMProvider
2. 将消息格式转换为LangChain格式
3. 调用ILLMProvider.chat()方法
4. 将响应转换为LangChain格式
5. 返回标准LLMResponse对象

#### Scenario: Stream Chat with LangChain
**Given** 系统已配置使用LangChain LLM提供者
**When** 用户调用stream_chat方法
**Then** 系统应：
1. 使用LangChainLLMWrapper的_stream方法
2. 逐个返回响应块
3. 每个块都是LLMResponse对象
4. 支持流式输出

#### Scenario: Convert Prompts to Messages
**Given** LangChain LLM需要prompts格式
**When** LangChainLLMWrapper接收prompts
**Then** 系统应：
1. 将prompts转换为标准消息列表
2. 处理多轮对话场景
3. 保持消息格式一致性
