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
import logging
from typing import List, Dict, Any, Optional, AsyncIterator
import httpx
from httpx import AsyncClient, HTTPError, ReadTimeout
from core.llm.adapters.base import BaseLLMAdapter
from core.base.adapter import AdapterCallError
from core.llm.models import ModelCapability
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.llm.connection_pool import ConnectionPoolManager


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
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        connection_pool: Optional["ConnectionPoolManager"] = None,
    ) -> None:
        """
        初始化通义千问适配器
        
        参数:
            config: 适配器配置，包含api_key等
            connection_pool: 连接池管理器（可选，用于性能优化）
        """
        super().__init__(config, connection_pool)
        self._api_key: str = ""
        self._base_url: str = "https://dashscope.aliyuncs.com/api/v1"
        self._client: Optional[AsyncClient] = None
        # 初始化logger
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
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
        
        # 从配置读取超时时间，默认120秒（支持简历优化等长时间操作）
        # 优先使用适配器配置的timeout，其次使用全局llm.timeout
        adapter_timeout = self._config.get("timeout", None)
        if adapter_timeout is None:
            # 尝试从全局配置读取
            global_config = self._config.get("_global_config", {})
            llm_config = global_config.get("llm", {})
            adapter_timeout = llm_config.get("timeout", 120.0)
        else:
            adapter_timeout = float(adapter_timeout)
        
        # 创建HTTP客户端（使用连接池或直接创建）
        if self._connection_pool:
            self._client = await self._connection_pool.get_client(
                base_url=self._base_url,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                timeout=adapter_timeout,
            )
        else:
            self._client = AsyncClient(
                base_url=self._base_url,
                timeout=adapter_timeout,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
        
        # 设置模型能力标签（通义千问模型能力）
        capability = ModelCapability(
            reasoning=True,
            creativity=True,
            cost_effective=True,  # 国内模型通常成本较低
            fast=True,
            multilingual=True,  # 支持中文和英文
            function_calling=True,
        )
        self.set_capability(capability)
        
        # 设置成本信息（通义千问的示例成本，实际成本可能因模型而异）
        # 注意：这里设置的是通用成本，实际应该根据具体模型调整
        self.set_cost_per_1k_tokens(
            input_cost=0.0003,   # 示例成本（需要根据实际定价调整）
            output_cost=0.0006,   # 示例成本（需要根据实际定价调整）
        )
        
        # 设置模型能力标签（通义千问模型能力）
        capability = ModelCapability(
            reasoning=True,
            creativity=True,
            cost_effective=True,  # 国内模型通常成本较低
            fast=True,
            multilingual=True,  # 支持中文和英文
            function_calling=True,
        )
        self.set_capability(capability)
        
        # 设置成本信息（通义千问的示例成本，实际成本可能因模型而异）
        # 注意：这里设置的是通用成本，实际应该根据具体模型调整
        self.set_cost_per_1k_tokens(
            input_cost=0.0003,   # 示例成本（需要根据实际定价调整）
            output_cost=0.0006,   # 示例成本（需要根据实际定价调整）
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
        # 通义千问要求工具格式为: {"type": "function", "function": {...}}
        if "functions" in kwargs:
            # 将functions转换为通义千问的tools格式
            functions = kwargs.pop("functions")
            if functions:
                # 转换格式：从 OpenAI 格式转换为通义千问格式
                # OpenAI格式: {"name": "...", "description": "...", "parameters": {...}}
                # 通义千问格式: {"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}
                qwen_tools = []
                for func in functions:
                    if isinstance(func, dict):
                        # 如果已经是通义千问格式（有type字段），直接使用
                        if "type" in func:
                            qwen_tools.append(func)
                        else:
                            # 转换为通义千问格式
                            qwen_tools.append({
                                "type": "function",
                                "function": {
                                    "name": func.get("name", ""),
                                    "description": func.get("description", ""),
                                    "parameters": func.get("parameters", {})
                                }
                            })
                    else:
                        self.logger.warning(f"跳过无效的工具定义格式: {func}")
                
                if qwen_tools:
                    # 通义千问使用tools参数
                    # 根据通义千问API文档，tools可以放在input或parameters中
                    # 尝试两种方式：先放在input中（这是更常见的做法）
                    if "input" not in request_data:
                        request_data["input"] = {}
                    request_data["input"]["tools"] = qwen_tools
                    
                    # 同时也在parameters中设置（某些版本可能需要）
                    request_data["parameters"]["tools"] = qwen_tools
                    
                    # 设置tool_choice以启用工具调用
                    # 根据通义千问API文档，tool_choice可选值：auto（自动选择）、none（不使用工具）、required（必须使用工具）
                    # 使用"auto"让LLM自动决定是否使用工具（第一次调用时使用，后续迭代中如果已有tool消息，LLM应该能正确判断）
                    request_data["parameters"]["tool_choice"] = "auto"
                    self.logger.info(f"添加工具定义: input.tools和parameters.tools, 工具数量={len(qwen_tools)}, tool_choice=auto")
                    self.logger.debug(f"工具定义详情: {qwen_tools}")
                else:
                    self.logger.warning("转换后的工具列表为空")
            else:
                self.logger.warning("functions参数为空，未添加工具定义")
        else:
            self.logger.debug("请求中未包含functions参数")
        
        # 合并其他参数到parameters
        if kwargs:
            request_data["parameters"].update(kwargs)
        
        # 记录关键请求信息（不记录完整数据以避免日志过大）
        try:
            import json as json_module
            # 只记录关键信息，不记录完整的prompt内容
            request_summary = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "messages_count": len(request_data.get("input", {}).get("messages", [])),
                "has_tools": bool(request_data.get("input", {}).get("tools")),
            }
            self.logger.debug(f"通义千问API请求摘要: {json_module.dumps(request_summary, ensure_ascii=False)}")
            # 只在TRACE级别记录完整数据（如果需要详细调试）
            if self.logger.isEnabledFor(logging.DEBUG - 1):  # TRACE级别
                request_str = json_module.dumps(request_data, ensure_ascii=False, indent=2)
                self.logger.log(logging.DEBUG - 1, f"通义千问API完整请求数据: {request_str}")
        except Exception as e:
            self.logger.debug(f"无法记录请求摘要: {e}")
        
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
            
            # 如果还是找不到内容，检查是否是工具调用（工具调用时content可能为空）
            if not content:
                # 检查是否有工具调用
                has_tool_calls = False
                if choices:
                    choice = choices[0]
                    message = choice.get("message", {})
                    if "tool_calls" in message or "function_call" in message:
                        has_tool_calls = True
                    elif choice.get("finish_reason") == "tool_calls":
                        has_tool_calls = True
                
                # 如果有工具调用，content为空是正常的
                if not has_tool_calls:
                    import json
                    error_detail = json.dumps(result, ensure_ascii=False, indent=2)
                    raise AdapterCallError(
                        f"API响应中没有找到有效内容。响应格式:\n{error_detail}"
                    )
                else:
                    # 工具调用时，content可以为空字符串
                    content = ""
            
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
                finish_reason = choices[0].get("finish_reason", "")
                
                # 详细记录响应结构（用于调试）
                # 注意：json已在文件顶部导入，这里直接使用
                try:
                    import json as json_module
                    message_str = json_module.dumps(message, ensure_ascii=False, indent=2)
                    self.logger.debug(f"通义千问响应message结构: {message_str}")
                except Exception as e:
                    self.logger.debug(f"无法序列化message: {e}, message类型: {type(message)}")
                
                # 记录完整的响应结构以便调试
                try:
                    import json as json_module
                    result_str = json_module.dumps(result, ensure_ascii=False, indent=2)
                    self.logger.debug(f"通义千问完整响应: {result_str}")
                except Exception as e:
                    self.logger.debug(f"无法序列化完整响应: {e}, result类型: {type(result)}")
                
                # 检查finish_reason，如果是tool_calls，说明需要工具调用
                self.logger.info(f"finish_reason: {finish_reason}")
                
                # 通义千问的工具调用可能在message.tool_calls中
                if "tool_calls" in message:
                    tool_calls = message.get("tool_calls", [])
                    # 转换通义千问格式到标准格式（如果需要）
                    # 通义千问格式: [{"function": {"name": "...", "arguments": "..."}, "type": "function", "id": "..."}]
                    # 标准格式: [{"id": "...", "type": "function", "function": {"name": "...", "arguments": "..."}}]
                    standardized_tool_calls = []
                    for tc in tool_calls:
                        if isinstance(tc, dict):
                            # 如果已经是标准格式（有function.name），直接使用
                            if "function" in tc and isinstance(tc["function"], dict) and "name" in tc["function"]:
                                standardized_tool_calls.append(tc)
                            # 如果是其他格式，尝试转换
                            elif "function" in tc:
                                standardized_tool_calls.append({
                                    "id": tc.get("id", tc.get("function", {}).get("name", "unknown")),
                                    "type": tc.get("type", "function"),
                                    "function": {
                                        "name": tc["function"].get("name", ""),
                                        "arguments": tc["function"].get("arguments", "{}")
                                    }
                                })
                    metadata["tool_calls"] = standardized_tool_calls if standardized_tool_calls else tool_calls
                    self.logger.info(f"✅ 从message.tool_calls提取工具调用: 数量={len(metadata['tool_calls'])}")
                # 或者可能在choice.tool_calls中
                elif "tool_calls" in choices[0]:
                    tool_calls = choices[0].get("tool_calls", [])
                    metadata["tool_calls"] = tool_calls
                    self.logger.info(f"✅ 从choice.tool_calls提取工具调用: 数量={len(tool_calls)}")
                # 检查output中是否有tool_calls
                elif "tool_calls" in output:
                    tool_calls = output.get("tool_calls", [])
                    metadata["tool_calls"] = tool_calls
                    self.logger.info(f"✅ 从output.tool_calls提取工具调用: 数量={len(tool_calls)}")
                # 检查result中是否有tool_calls
                elif "tool_calls" in result:
                    tool_calls = result.get("tool_calls", [])
                    metadata["tool_calls"] = tool_calls
                    self.logger.info(f"✅ 从result.tool_calls提取工具调用: 数量={len(tool_calls)}")
                # 检查message中是否有function_call（兼容旧格式）
                elif "function_call" in message:
                    function_call = message.get("function_call", {})
                    # 转换为tool_calls格式
                    tool_calls = [{
                        "id": function_call.get("name", "unknown"),
                        "type": "function",
                        "function": {
                            "name": function_call.get("name", ""),
                            "arguments": function_call.get("arguments", "{}")
                        }
                    }]
                    metadata["tool_calls"] = tool_calls
                    self.logger.info(f"✅ 从message.function_call提取工具调用: {function_call}")
                # 如果finish_reason是tool_calls，但响应中没有tool_calls字段，可能是通义千问的格式问题
                elif finish_reason == "tool_calls":
                    self.logger.warning("⚠️ finish_reason是tool_calls，但响应中没有找到tool_calls字段，可能是通义千问API格式问题")
                    # 尝试从message中查找可能的工具调用信息
                    if isinstance(message, dict):
                        self.logger.debug(f"message中的所有字段: {list(message.keys())}")
                else:
                    self.logger.warning("❌ 未在响应中找到tool_calls字段，检查所有可能位置...")
                    # 检查所有可能的位置
                    all_keys = set()
                    if isinstance(message, dict):
                        all_keys.update(message.keys())
                    if isinstance(choices[0], dict):
                        all_keys.update(choices[0].keys())
                    if isinstance(output, dict):
                        all_keys.update(output.keys())
                    if isinstance(result, dict):
                        all_keys.update(result.keys())
                    self.logger.debug(f"响应中所有可用字段: {sorted(all_keys)}")
                
                # 兼容function_call格式
                if "function_call" in message:
                    import json as json_module
                    metadata["function_call"] = message.get("function_call")
                    self.logger.info(f"✅ 检测到function_call: {json_module.dumps(metadata['function_call'], ensure_ascii=False)}")
            
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
            # 正确提取HTTP状态码和错误信息
            status_code = "unknown"
            error_body = None
            error_text = None
            
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                try:
                    error_body = e.response.json()
                except Exception:
                    try:
                        error_text = e.response.text[:500]  # 限制长度
                    except Exception:
                        pass
            
            # 构建详细的错误信息
            error_detail = f"HTTP状态码: {status_code}"
            if error_body:
                error_msg = error_body.get("message") or error_body.get("error", {}).get("message", "")
                if error_msg:
                    error_detail += f", 错误信息: {error_msg}"
                else:
                    error_detail += f", 响应: {json.dumps(error_body, ensure_ascii=False)[:200]}"
            elif error_text:
                error_detail += f", 响应文本: {error_text}"
            
            # 记录详细错误日志
            self.logger.error(
                f"通义千问API调用失败: {error_detail}",
                exc_info=True,
                extra={
                    "status_code": status_code,
                    "error_body": error_body,
                    "model": model,
                }
            )
            raise AdapterCallError(f"通义千问API调用失败: {error_detail}") from e
        except ReadTimeout as e:
            # 处理超时错误
            timeout_detail = f"请求超时（模型: {model}, 超时时间: {self._client.timeout if self._client else 'unknown'}秒）"
            self.logger.error(
                f"通义千问API调用超时: {timeout_detail}",
                exc_info=True,
                extra={
                    "model": model,
                    "timeout": self._client.timeout if self._client else None,
                }
            )
            raise AdapterCallError(f"通义千问API调用超时: {timeout_detail}") from e
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            self.logger.error(
                f"通义千问API调用出错: {error_type}: {error_msg}",
                exc_info=True,
                extra={
                    "model": model,
                    "error_type": error_type,
                }
            )
            raise AdapterCallError(f"通义千问API调用出错: {error_type}: {error_msg}") from e
    
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
