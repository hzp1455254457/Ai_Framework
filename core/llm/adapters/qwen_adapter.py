"""
模块名称：通义千问适配器模块
功能描述：实现阿里云通义千问AI的适配器
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - QwenAdapter: 通义千问适配器

依赖模块：
    - httpx: 异步HTTP客户端
    - core.llm.adapters.base: 适配器基类
"""

import json
from typing import List, Dict, Any, Optional, AsyncIterator
from httpx import AsyncClient, HTTPError
from core.llm.adapters.base import BaseLLMAdapter
from core.base.adapter import AdapterCallError


class QwenAdapter(BaseLLMAdapter):
    """
    通义千问AI适配器
    
    实现阿里云通义千问AI的服务适配器。
    
    特性：
        - 支持通义千问API调用
        - 支持流式响应
        - 错误处理和重试
    
    配置示例:
        {
            "api_key": "your-api-key",
            "base_url": "https://dashscope.aliyuncs.com/api/v1"  # 可选
        }
    
    示例:
        >>> adapter = QwenAdapter({"api_key": "your-key"})
        >>> await adapter.initialize()
        >>> response = await adapter.call(messages=[...])
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化通义千问适配器
        
        参数:
            config: 适配器配置，包含api_key等
        """
        super().__init__(config)
        self._api_key: str = ""
        self._base_url: str = "https://dashscope.aliyuncs.com/api/v1"
        self._client: Optional[AsyncClient] = None
    
    @property
    def name(self) -> str:
        """适配器名称"""
        return "qwen-adapter"
    
    @property
    def provider(self) -> str:
        """服务提供商名称"""
        return "qwen"
    
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
            raise AdapterCallError("通义千问API密钥未配置")
        
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
        调用通义千问API
        
        参数:
            messages: 消息列表
            model: 模型名称（如 qwen-turbo, qwen-plus, qwen-max）
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
            "input": {
                "messages": messages,
            },
            "parameters": {
                "temperature": temperature,
            },
        }
        
        if max_tokens:
            request_data["parameters"]["max_tokens"] = max_tokens
        
        # 处理Function Calling工具（通义千问使用tools参数）
        # 根据测试结果，tools应该放在parameters中，而不是input中
        if "functions" in kwargs:
            # 将functions转换为通义千问的tools格式
            functions = kwargs.pop("functions")
            if functions:
                # 通义千问使用tools参数，必须放在parameters中（测试验证）
                request_data["parameters"]["tools"] = functions
                self.logger.info(f"添加工具定义到parameters.tools: 工具数量={len(functions)}")
                self.logger.debug(f"工具定义详情: {functions}")
            else:
                self.logger.warning("functions参数为空，未添加工具定义")
        else:
            self.logger.debug("请求中未包含functions参数")
        
        # 合并其他参数到parameters
        if kwargs:
            request_data["parameters"].update(kwargs)
        
        try:
            # 发送请求
            response = await self._client.post(
                "/services/aigc/text-generation/generation",
                json=request_data,
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 检查是否有错误信息
            if "code" in result and result.get("code") != "Success":
                error_msg = result.get("message", "未知错误")
                raise AdapterCallError(f"通义千问API返回错误: {error_msg}")
            
            # 解析响应
            output = result.get("output", {})
            
            # 尝试多种响应格式
            choices = None
            content = ""
            
            # 格式1: output.choices[0].message.content (标准格式)
            if "choices" in output:
                choices = output.get("choices", [])
                if choices:
                    choice = choices[0]
                    message = choice.get("message", {})
                    content = message.get("content", "")
            
            # 格式2: output.text (直接文本格式)
            elif "text" in output:
                content = output.get("text", "")
                choices = [{"message": {"content": content}}]
            
            # 格式3: output.choices 直接是数组
            elif isinstance(output, list):
                choices = output
                if choices:
                    choice = choices[0]
                    message = choice.get("message", {})
                    content = message.get("content", "")
            
            # 如果还是找不到内容，记录响应以便调试
            if not content:
                import json
                error_detail = json.dumps(result, ensure_ascii=False, indent=2)
                raise AdapterCallError(
                    f"API响应中没有找到有效内容。响应格式:\n{error_detail}"
                )
            
            # 构建标准响应
            usage = result.get("usage", {})
            
            # 提取工具调用信息（如果存在）
            metadata: Dict[str, Any] = {
                "model": result.get("model", model),
                "finish_reason": choices[0].get("finish_reason") if choices else None,
            }
            
            # 检查是否有工具调用（通义千问可能在message中返回tool_calls）
            if choices:
                message = choices[0].get("message", {})
                # 通义千问的工具调用可能在message.tool_calls中
                if "tool_calls" in message:
                    metadata["tool_calls"] = message.get("tool_calls", [])
                # 或者可能在choice.tool_calls中
                elif "tool_calls" in choices[0]:
                    metadata["tool_calls"] = choices[0].get("tool_calls", [])
                # 兼容function_call格式
                if "function_call" in message:
                    metadata["function_call"] = message.get("function_call")
            
            return {
                "content": content,
                "usage": {
                    "prompt_tokens": usage.get("input_tokens", 0),
                    "completion_tokens": usage.get("output_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
                "metadata": metadata,
            }
            
        except HTTPError as e:
            error_detail = f"HTTP状态码: {e.response.status_code if hasattr(e, 'response') else 'unknown'}"
            if hasattr(e, 'response'):
                try:
                    error_body = e.response.json()
                    error_detail += f", 响应: {json.dumps(error_body, ensure_ascii=False)}"
                except:
                    error_detail += f", 响应文本: {e.response.text[:200]}"
            raise AdapterCallError(f"通义千问API调用失败: {error_detail}") from e
        except Exception as e:
            raise AdapterCallError(f"通义千问API调用出错: {e}") from e
    
    async def stream_call(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式调用通义千问API
        
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
            "input": {
                "messages": messages,
            },
            "parameters": {
                "temperature": temperature,
                "incremental_output": True,  # 流式输出
            },
        }
        request_data.update(kwargs)
        
        try:
            # 发送流式请求
            async with self._client.stream(
                "POST",
                "/services/aigc/text-generation/generation",
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
                            output = data.get("output", {})
                            choices = output.get("choices", [])
                            
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
            raise AdapterCallError(f"通义千问流式API调用失败: {e}") from e
        except Exception as e:
            raise AdapterCallError(f"通义千问流式API调用出错: {e}") from e
    
    async def cleanup(self) -> None:
        """清理适配器资源"""
        if self._client:
            await self._client.aclose()
            self._client = None
        await super().cleanup()
