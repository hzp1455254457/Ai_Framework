"""
测试模块：Token计数工具测试
功能描述：测试TokenCounter的Token计算逻辑
"""

import pytest

from core.llm.utils.token_counter import TokenCounter


class TestTokenCounter:
    """TokenCounter测试类"""

    def test_count_empty_text(self):
        """空文本应返回0"""
        counter = TokenCounter()
        assert counter.count_text_tokens("") == 0

    def test_count_text_tokens_with_gpt_model(self):
        """指定GPT模型时应可返回正整数"""
        counter = TokenCounter()
        tokens = counter.count_text_tokens("Hello, world!", model="gpt-3.5-turbo")
        assert isinstance(tokens, int)
        assert tokens > 0

    def test_count_text_tokens_with_unknown_model_fallback(self):
        """未知模型名应走回退编码器，仍返回正整数"""
        counter = TokenCounter()
        tokens = counter.count_text_tokens("Hello, world!", model="unknown-model-xyz")
        assert isinstance(tokens, int)
        assert tokens > 0

    def test_encoding_cache(self):
        """同一个model重复调用应命中缓存（行为层面：不抛异常且结果稳定）"""
        counter = TokenCounter()
        t1 = counter.count_text_tokens("Hello", model="gpt-3.5-turbo")
        t2 = counter.count_text_tokens("Hello", model="gpt-3.5-turbo")
        assert t1 == t2

