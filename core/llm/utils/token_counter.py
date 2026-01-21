"""
模块名称：Token计数工具模块
功能描述：提供基于tiktoken的精确Token计算能力，并对非OpenAI模型提供合理回退
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - TokenCounter: Token计数器

依赖模块：
    - tiktoken: OpenAI Tokenizer（精确Token计算）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import tiktoken


@dataclass(frozen=True)
class TokenCounter:
    """
    Token计数器

    说明：
        - 对 OpenAI GPT 系列：使用 tiktoken.encoding_for_model() 获取精确编码器
        - 对未知/非OpenAI模型：使用 cl100k_base 作为保守回退（多数chat模型兼容）
    """

    _encoding_cache: Dict[str, tiktoken.Encoding]

    def __init__(self) -> None:
        object.__setattr__(self, "_encoding_cache", {})

    def count_text_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        计算纯文本Token数量

        参数：
            text: 文本内容
            model: 模型名称（可选）

        返回：
            Token数量（>=0）
        """
        if not text:
            return 0

        encoding = self._get_encoding(model)
        return len(encoding.encode(text))

    def _get_encoding(self, model: Optional[str]) -> tiktoken.Encoding:
        """
        获取并缓存编码器

        - model为空：使用cl100k_base
        - model有值：优先encoding_for_model；失败则回退cl100k_base
        """
        key = (model or "cl100k_base").strip()
        if key in self._encoding_cache:
            return self._encoding_cache[key]

        if model:
            try:
                enc = tiktoken.encoding_for_model(model)
                self._encoding_cache[key] = enc
                return enc
            except KeyError:
                # 不认识的模型名，回退到通用编码
                pass

        enc = tiktoken.get_encoding("cl100k_base")
        self._encoding_cache[key] = enc
        return enc

