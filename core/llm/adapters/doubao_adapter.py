"""
模块名称：豆包适配器模块
功能描述：实现字节跳动豆包AI的适配器
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - DoubaoAdapter: 豆包AI适配器

依赖模块：
    - httpx: 异步HTTP客户端
    - core.llm.adapters.base: 适配器基类
"""

import json
from typing import List, Dict, Any, Optional, AsyncIterator
from httpx import AsyncClient, HTTPError
from core.llm.adapters.base import BaseLLMAdapter
from core.base.adapter import AdapterCallError


class DoubaoAdapter(BaseLLMAdapter):
    """
    豆包AI适配器
    
    实现字节跳动豆包AI的服务适配器。
    
    特性：
        - 支持豆包API调用
        - 支持流式响应
        - 错误处理和重试
    
    配置示例:
        {
            "api_key": "your-api-key",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3"  # 可选
        }
    
    示例:
        >>> adapter = DoubaoAdapter({"api_key": "your-key"})
        >>> await adapter.initialize()
        >>> response = await adapter.call(messages=[...])
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化豆包适配器
        
        参数:
            config: 适配器配置，包含api_key等
        """
        super().__init__(config)
        self._api_key: str = ""
        self._base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
        self._client: Optional[AsyncClient] = None
    
    @property
    def name(self) -> str:
        """适配器名称"""
        return "doubao-adapter"
    
    @property
    def provider(self) -> str:
        """服务提供商名称"""
        return "doubao"
    
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
            raise AdapterCallError("豆包API密钥未配置")
        
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
        调用豆包API
        
        参数:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
        
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
        
        # 合并其他参数
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
                },
            }
            
        except HTTPError as e:
            raise AdapterCallError(f"豆包API调用失败: {e}") from e
        except Exception as e:
            raise AdapterCallError(f"豆包API调用出错: {e}") from e
    
    async def stream_call(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式调用豆包API
        
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
            raise AdapterCallError(f"豆包流式API调用失败: {e}") from e
        except Exception as e:
            raise AdapterCallError(f"豆包流式API调用出错: {e}") from e
    
    async def cleanup(self) -> None:
        """清理适配器资源"""
        if self._client:
            await self._client.aclose()
            self._client = None
        await super().cleanup()
