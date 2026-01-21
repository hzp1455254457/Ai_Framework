"""
模块名称：Claude适配器模块
功能描述：实现Anthropic Claude的适配器
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - ClaudeAdapter: Claude适配器

依赖模块：
    - httpx: 异步HTTP客户端
    - core.llm.adapters.base: 适配器基类
"""

from __future__ import annotations

import json
from typing import Any, AsyncIterator, Dict, List, Optional

from httpx import AsyncClient, HTTPError

from core.base.adapter import AdapterCallError
from core.llm.adapters.base import BaseLLMAdapter


class ClaudeAdapter(BaseLLMAdapter):
    """
    Claude适配器

    基于Anthropic Messages API实现Claude模型调用。

    配置示例:
        {
            "api_key": "sk-ant-...",
            "base_url": "https://api.anthropic.com/v1",   # 可选
            "anthropic_version": "2023-06-01"            # 可选
        }
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._api_key: str = ""
        self._base_url: str = "https://api.anthropic.com/v1"
        self._anthropic_version: str = "2023-06-01"
        self._client: Optional[AsyncClient] = None

    @property
    def name(self) -> str:
        return "claude-adapter"

    @property
    def provider(self) -> str:
        return "claude"

    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        if config:
            self._config.update(config)

        self._api_key = self._config.get("api_key", "")
        if not self._api_key:
            raise AdapterCallError("Claude API密钥未配置")

        self._base_url = self._config.get("base_url", self._base_url)
        self._anthropic_version = self._config.get("anthropic_version", self._anthropic_version)

        self._client = AsyncClient(
            base_url=self._base_url,
            timeout=30.0,
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": self._anthropic_version,
                "Content-Type": "application/json",
            },
        )

        await super().initialize()

    def _extract_system_prompt(self, messages: List[Dict[str, str]]) -> tuple[Optional[str], List[Dict[str, str]]]:
        """
        Claude Messages API将system作为顶层字段。

        约定：
            - 如果messages中包含role=system的消息，则合并为system字段
            - 其余消息按原样传递
        """
        system_parts: List[str] = []
        remaining: List[Dict[str, str]] = []
        for m in messages:
            role = m.get("role")
            if role == "system":
                content = m.get("content") or ""
                if content:
                    system_parts.append(content)
            else:
                remaining.append(m)

        system_prompt = "\n".join(system_parts) if system_parts else None
        return system_prompt, remaining

    async def call(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if not self._client:
            raise AdapterCallError("适配器未初始化")

        system_prompt, chat_messages = self._extract_system_prompt(messages)

        request_data: Dict[str, Any] = {
            "model": model,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens if max_tokens is not None else 1024,
        }
        if system_prompt:
            request_data["system"] = system_prompt

        # 允许透传Anthropic参数（如 top_p, stop_sequences 等）
        request_data.update(kwargs)

        try:
            response = await self._client.post("/messages", json=request_data)
            response.raise_for_status()
            result = response.json()

            # content: [{"type":"text","text":"..."}]
            content_blocks = result.get("content", []) or []
            texts: List[str] = []
            for block in content_blocks:
                if isinstance(block, dict) and block.get("type") == "text":
                    texts.append(block.get("text", "") or "")
            content = "".join(texts)

            usage = result.get("usage", {}) or {}
            return {
                "content": content,
                "usage": {
                    "prompt_tokens": usage.get("input_tokens", 0),
                    "completion_tokens": usage.get("output_tokens", 0),
                    "total_tokens": (usage.get("input_tokens", 0) + usage.get("output_tokens", 0)),
                },
                "metadata": {
                    "model": result.get("model", model),
                    "stop_reason": result.get("stop_reason"),
                    "id": result.get("id"),
                },
            }
        except HTTPError as e:
            error_message = f"Claude API调用失败: {e}"
            if getattr(e, "response", None) is not None:
                try:
                    detail = e.response.json()
                    error_message = f"Claude API调用失败: {detail}"
                except Exception:
                    pass
            raise AdapterCallError(error_message) from e
        except Exception as e:
            raise AdapterCallError(f"Claude API调用出错: {e}") from e

    async def stream_call(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        if not self._client:
            raise AdapterCallError("适配器未初始化")

        system_prompt, chat_messages = self._extract_system_prompt(messages)

        request_data: Dict[str, Any] = {
            "model": model,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens if max_tokens is not None else 1024,
            "stream": True,
        }
        if system_prompt:
            request_data["system"] = system_prompt
        request_data.update(kwargs)

        try:
            async with self._client.stream("POST", "/messages", json=request_data) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    if not line.startswith("data: "):
                        continue

                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    event_type = data.get("type")
                    if event_type == "content_block_delta":
                        delta = (data.get("delta") or {})
                        text = delta.get("text") or ""
                        if text:
                            yield {
                                "content": text,
                                "usage": {},
                                "metadata": {
                                    "model": model,
                                },
                            }
                    elif event_type == "message_stop":
                        break
        except HTTPError as e:
            raise AdapterCallError(f"Claude流式API调用失败: {e}") from e
        except Exception as e:
            raise AdapterCallError(f"Claude流式API调用出错: {e}") from e

    async def cleanup(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
        await super().cleanup()

