"""
模块名称：OpenAI适配器模块
功能描述：实现OpenAI的适配器
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - OpenAIAdapter: OpenAI适配器

依赖模块：
    - httpx: 异步HTTP客户端
    - core.llm.adapters.base: 适配器基类
"""

import json
import asyncio
from typing import List, Dict, Any, Optional, AsyncIterator
from httpx import AsyncClient, HTTPError, TimeoutException
from core.llm.adapters.base import BaseLLMAdapter
from core.base.adapter import AdapterCallError
from core.base.health_check import HealthStatus, HealthCheckResult


class OpenAIAdapter(BaseLLMAdapter):
    """
    OpenAI适配器
    
    实现OpenAI的服务适配器，支持GPT-3.5、GPT-4等模型。
    
    特性：
        - 支持OpenAI API调用
        - 支持流式响应
        - 错误处理和重试
        - Function Calling支持
    
    配置示例:
        {
            "api_key": "sk-...",
            "base_url": "https://api.openai.com/v1"  # 可选，支持自定义端点
        }
    
    示例:
        >>> adapter = OpenAIAdapter({"api_key": "sk-..."})
        >>> await adapter.initialize()
        >>> response = await adapter.call(messages=[...], model="gpt-3.5-turbo")
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化OpenAI适配器
        
        参数:
            config: 适配器配置，包含api_key等
        """
        super().__init__(config)
        self._api_key: str = ""
        self._base_url: str = "https://api.openai.com/v1"
        self._client: Optional[AsyncClient] = None
    
    @property
    def name(self) -> str:
        """适配器名称"""
        return "openai-adapter"
    
    @property
    def provider(self) -> str:
        """服务提供商名称"""
        return "openai"
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化适配器
        
        参数:
            config: 适配器配置
        """
        if config:
            self._config.update(config)
        
        self._api_key = self._config.get("api_key", "")
        if not self._api_key:
            raise AdapterCallError("OpenAI API密钥未配置")
        
        self._base_url = self._config.get("base_url", self._base_url)
        
        # 创建HTTP客户端
        self._client = AsyncClient(
            base_url=self._base_url,
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )
        
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
        调用OpenAI API
        
        参数:
            messages: 消息列表
            model: 模型名称（如 "gpt-3.5-turbo", "gpt-4"）
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数（如 functions, function_call等）
        
        返回:
            标准格式的响应字典
        
        异常:
            AdapterCallError: API调用失败时抛出
        """
        if not self._client:
            raise AdapterCallError("适配器未初始化")
        
        # 构建请求数据
        request_data: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            request_data["max_tokens"] = max_tokens
        
        # 合并其他参数（如functions, function_call等）
        request_data.update(kwargs)
        
        try:
            # 发送请求
            response = await self._client.post(
                "/chat/completions",
                json=request_data,
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 解析响应
            choices = result.get("choices", [])
            if not choices:
                raise AdapterCallError("API响应中没有choices字段")
            
            choice = choices[0]
            message = choice.get("message", {})
            content = message.get("content", "")
            
            # 构建标准响应
            usage = result.get("usage", {})
            
            return {
                "content": content,
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
                "metadata": {
                    "model": result.get("model", model),
                    "finish_reason": choice.get("finish_reason"),
                    "function_call": message.get("function_call"),  # Function Calling支持
                },
            }
            
        except HTTPError as e:
            error_message = f"OpenAI API调用失败: {e}"
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    if "error" in error_detail:
                        error_message = f"OpenAI API调用失败: {error_detail['error'].get('message', str(e))}"
                except Exception:
                    pass
            raise AdapterCallError(error_message) from e
        except Exception as e:
            raise AdapterCallError(f"OpenAI API调用出错: {e}") from e
    
    async def stream_call(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式调用OpenAI API
        
        参数:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            **kwargs: 其他参数
        
        生成器:
            逐个返回响应块
        """
        if not self._client:
            raise AdapterCallError("适配器未初始化")
        
        # 构建请求数据
        request_data: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        request_data.update(kwargs)
        
        try:
            # 发送流式请求
            async with self._client.stream(
                "POST",
                "/chat/completions",
                json=request_data,
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    # 解析SSE格式
                    if line.startswith("data: "):
                        data_str = line[6:]  # 移除 "data: " 前缀
                        
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            choices = data.get("choices", [])
                            
                            if choices:
                                choice = choices[0]
                                delta = choice.get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    yield {
                                        "content": content,
                                        "usage": {},
                                        "metadata": {
                                            "model": data.get("model", model),
                                        },
                                    }
                        except json.JSONDecodeError:
                            continue
                            
        except HTTPError as e:
            error_message = f"OpenAI流式API调用失败: {e}"
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    if "error" in error_detail:
                        error_message = f"OpenAI流式API调用失败: {error_detail['error'].get('message', str(e))}"
                except Exception:
                    pass
            raise AdapterCallError(error_message) from e
        except Exception as e:
            raise AdapterCallError(f"OpenAI流式API调用出错: {e}") from e
    
    async def health_check(self) -> HealthCheckResult:
        """
        执行健康检查
        
        通过发送轻量级的API请求（模型列表）来检测适配器是否可用。
        
        返回:
            健康检查结果
        """
        if not self._initialized or not self._client:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message="适配器未初始化"
            )
        
        try:
            # 使用较短的超时时间进行健康检查
            timeout = 5.0
            async with asyncio.timeout(timeout):
                # 发送轻量级请求：获取模型列表（如果API支持）
                # 或者发送一个最小的chat completion请求
                response = await self._client.get(
                    "/models",
                    timeout=timeout,
                )
                response.raise_for_status()
                
                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    message="适配器可用",
                    details={"provider": self.provider}
                )
        except TimeoutException:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message="健康检查超时"
            )
        except HTTPError as e:
            # 401/403 表示API密钥问题，但适配器本身可能可用
            if e.response and e.response.status_code in (401, 403):
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message="API密钥无效或权限不足"
                )
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"健康检查失败: {e}"
            )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"健康检查出错: {e}"
            )
    
    async def cleanup(self) -> None:
        """清理适配器资源"""
        if self._client:
            await self._client.aclose()
            self._client = None
        await super().cleanup()
