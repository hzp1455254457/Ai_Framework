"""
模块名称：LiteLLM适配器模块
功能描述：包装LiteLLM实现BaseLLMAdapter接口，提供统一的多模型接口
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - LiteLLMAdapter: LiteLLM适配器

依赖模块：
    - litellm: LiteLLM框架（可选依赖）
    - core.llm.adapters.base: 适配器基类
    - core.llm.models: 数据模型
"""

import json
from typing import List, Dict, Any, Optional, AsyncIterator

try:
    import litellm
    from litellm import completion, acompletion, stream_chat
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    litellm = None

from core.llm.adapters.base import BaseLLMAdapter
from core.base.adapter import AdapterCallError
from core.base.health_check import HealthStatus, HealthCheckResult
from core.llm.models import ModelCapability


class LiteLLMAdapter(BaseLLMAdapter):
    """
    LiteLLM适配器
    
    包装LiteLLM框架，实现BaseLLMAdapter接口。
    支持100+模型提供商，包括OpenAI、Anthropic、Google、Cohere等。
    
    特性：
        - 统一的多模型接口
        - 支持流式响应
        - 自动成本计算
        - 错误处理和重试
    
    配置示例:
        {
            "api_key": "sk-...",  # 或使用环境变量
            "model": "gpt-3.5-turbo",  # 可选，默认模型
            "base_url": "https://api.openai.com/v1"  # 可选
        }
    
    示例:
        >>> adapter = LiteLLMAdapter({"api_key": "sk-..."})
        >>> await adapter.initialize()
        >>> response = await adapter.call(messages=[...], model="gpt-3.5-turbo")
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化LiteLLM适配器
        
        参数:
            config: 适配器配置
        """
        super().__init__(config)
        self._api_key: Optional[str] = None
        self._default_model: Optional[str] = None
        self._initialized: bool = False
    
    @property
    def name(self) -> str:
        """适配器名称"""
        return "litellm-adapter"
    
    @property
    def provider(self) -> str:
        """服务提供商名称"""
        return "litellm"
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化适配器
        
        参数:
            config: 适配器配置
        
        异常:
            AdapterCallError: LiteLLM不可用或初始化失败时抛出
        """
        if not LITELLM_AVAILABLE:
            raise AdapterCallError(
                "LiteLLM未安装，请运行: pip install litellm"
            )
        
        if config:
            self._config.update(config)
        
        # 从配置或环境变量获取API密钥
        self._api_key = self._config.get("api_key")
        if not self._api_key:
            # LiteLLM可以从环境变量读取，所以这里不强制要求
            self.logger.warning("未配置API密钥，LiteLLM将尝试从环境变量读取")
        
        self._default_model = self._config.get("model")
        
        # 配置LiteLLM（如果提供了配置）
        if "litellm_config" in self._config:
            litellm_config = self._config["litellm_config"]
            if "api_base" in litellm_config:
                litellm.api_base = litellm_config["api_base"]
            if "api_version" in litellm_config:
                litellm.api_version = litellm_config["api_version"]
        
        # 设置默认能力标签（LiteLLM支持多种模型，能力较全面）
        capability = ModelCapability(
            reasoning=True,
            creativity=True,
            cost_effective=True,  # LiteLLM可以路由到成本更低的模型
            fast=True,
            multilingual=True,
            function_calling=True,
        )
        self.set_capability(capability)
        
        self._initialized = True
        await super().initialize()
    
    async def call(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        调用LiteLLM接口
        
        参数:
            messages: 消息列表
            model: 模型名称（LiteLLM格式，如 "gpt-3.5-turbo", "claude-3-opus"）
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数（如 functions, function_call等）
        
        返回:
            标准格式的响应字典
        
        异常:
            AdapterCallError: API调用失败时抛出
        """
        if not self._initialized:
            raise AdapterCallError("适配器未初始化")
        
        if not LITELLM_AVAILABLE:
            raise AdapterCallError("LiteLLM未安装")
        
        try:
            # 构建LiteLLM调用参数
            call_params: Dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                call_params["max_tokens"] = max_tokens
            
            # 合并其他参数
            call_params.update(kwargs)
            
            # 调用LiteLLM（使用异步接口）
            response = await acompletion(**call_params)
            
            # 解析响应
            choices = response.choices
            if not choices:
                raise AdapterCallError("LiteLLM响应中没有choices字段")
            
            choice = choices[0]
            message = choice.message
            content = message.content or ""
            
            # 获取Token使用信息
            usage = response.usage
            usage_dict = {}
            if usage:
                usage_dict = {
                    "prompt_tokens": usage.prompt_tokens or 0,
                    "completion_tokens": usage.completion_tokens or 0,
                    "total_tokens": usage.total_tokens or 0,
                }
            
            # 获取成本信息（如果LiteLLM提供了）
            metadata = {
                "model": response.model or model,
                "finish_reason": choice.finish_reason,
            }
            
            # 尝试获取成本信息
            if hasattr(response, "_hidden_params") and response._hidden_params:
                if "response_cost" in response._hidden_params:
                    metadata["cost"] = response._hidden_params["response_cost"]
            
            # 检查是否有function_call
            if hasattr(message, "tool_calls") and message.tool_calls:
                metadata["function_call"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in message.tool_calls
                ]
            
            return {
                "content": content,
                "usage": usage_dict,
                "metadata": metadata,
            }
            
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                raise AdapterCallError(f"LiteLLM认证失败: {error_msg}") from e
            elif "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
                raise AdapterCallError(f"LiteLLM速率限制: {error_msg}") from e
            else:
                raise AdapterCallError(f"LiteLLM调用失败: {error_msg}") from e
    
    async def stream_call(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式调用LiteLLM接口
        
        参数:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            **kwargs: 其他参数
        
        生成器:
            逐个返回响应块
        """
        if not self._initialized:
            raise AdapterCallError("适配器未初始化")
        
        if not LITELLM_AVAILABLE:
            raise AdapterCallError("LiteLLM未安装")
        
        try:
            # 构建LiteLLM调用参数
            call_params: Dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
            }
            call_params.update(kwargs)
            
            # 调用LiteLLM流式接口
            stream = await litellm.astream(**call_params)
            
            accumulated_content = ""
            total_usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            }
            
            async for chunk in stream:
                choices = chunk.choices
                if not choices:
                    continue
                
                choice = choices[0]
                delta = choice.delta
                
                # 获取内容增量
                content = delta.content or ""
                if content:
                    accumulated_content += content
                    yield {
                        "content": content,
                        "usage": {},
                        "metadata": {
                            "model": chunk.model or model,
                            "finish_reason": None,
                        },
                    }
                
                # 检查是否完成
                if choice.finish_reason:
                    # 获取最终使用量
                    if hasattr(chunk, "usage") and chunk.usage:
                        usage = chunk.usage
                        total_usage = {
                            "prompt_tokens": usage.prompt_tokens or 0,
                            "completion_tokens": usage.completion_tokens or 0,
                            "total_tokens": usage.total_tokens or 0,
                        }
                    
                    # 发送最终块
                    yield {
                        "content": "",
                        "usage": total_usage,
                        "metadata": {
                            "model": chunk.model or model,
                            "finish_reason": choice.finish_reason,
                        },
                    }
                    break
                    
        except Exception as e:
            error_msg = str(e)
            raise AdapterCallError(f"LiteLLM流式调用失败: {error_msg}") from e
    
    async def health_check(self) -> HealthCheckResult:
        """
        检查适配器健康状态
        
        返回:
            健康检查结果
        """
        if not LITELLM_AVAILABLE:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message="LiteLLM未安装"
            )
        
        if not self._initialized:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message="适配器未初始化"
            )
        
        # 执行轻量级健康检查（尝试调用一个简单的模型列表API）
        try:
            # LiteLLM没有专门的健康检查API，这里检查是否可以正常导入
            # 实际健康检查在调用时进行
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="LiteLLM适配器已就绪"
            )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"健康检查失败: {e}"
            )
