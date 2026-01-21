"""
模块名称：Ollama适配器模块
功能描述：实现Ollama本地模型的适配器
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - OllamaAdapter: Ollama适配器

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


class OllamaAdapter(BaseLLMAdapter):
    """
    Ollama适配器

    基于Ollama HTTP API实现本地模型调用。

    配置示例:
        {
            "base_url": "http://localhost:11434"
        }
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._base_url: str = "http://localhost:11434"
        self._client: Optional[AsyncClient] = None

    @property
    def name(self) -> str:
        return "ollama-adapter"

    @property
    def provider(self) -> str:
        return "ollama"

    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        if config:
            self._config.update(config)

        self._base_url = self._config.get("base_url", self._base_url)
        self._client = AsyncClient(base_url=self._base_url, timeout=60.0)
        await super().initialize()

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

        options: Dict[str, Any] = {"temperature": temperature}
        # Ollama options中常见字段：num_predict 等
        if max_tokens is not None:
            options["num_predict"] = max_tokens

        request_data: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": options,
        }
        request_data.update(kwargs)

        try:
            response = await self._client.post("/api/chat", json=request_data)
            response.raise_for_status()
            result = response.json()

            message = result.get("message", {}) or {}
            content = message.get("content", "") or ""

            # Ollama并不总返回token usage，这里尽量兼容
            usage: Dict[str, Any] = {
                "prompt_tokens": result.get("prompt_eval_count", 0) or 0,
                "completion_tokens": result.get("eval_count", 0) or 0,
            }
            usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]

            return {
                "content": content,
                "usage": usage,
                "metadata": {
                    "model": result.get("model", model),
                    "done": result.get("done", True),
                },
            }
        except HTTPError as e:
            error_message = f"Ollama API调用失败: {e}"
            if getattr(e, "response", None) is not None:
                try:
                    detail = e.response.json()
                    error_message = f"Ollama API调用失败: {detail}"
                except Exception:
                    pass
            raise AdapterCallError(error_message) from e
        except Exception as e:
            raise AdapterCallError(f"Ollama API调用出错: {e}") from e

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

        options: Dict[str, Any] = {"temperature": temperature}
        if max_tokens is not None:
            options["num_predict"] = max_tokens

        request_data: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": options,
        }
        request_data.update(kwargs)

        try:
            async with self._client.stream("POST", "/api/chat", json=request_data) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    message = (data.get("message") or {})
                    content = message.get("content") or ""
                    if content:
                        yield {
                            "content": content,
                            "usage": {},
                            "metadata": {
                                "model": data.get("model", model),
                            },
                        }

                    if data.get("done") is True:
                        break
        except HTTPError as e:
            raise AdapterCallError(f"Ollama流式API调用失败: {e}") from e
        except Exception as e:
            raise AdapterCallError(f"Ollama流式API调用出错: {e}") from e

    async def cleanup(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
        await super().cleanup()

