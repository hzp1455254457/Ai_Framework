#!/usr/bin/env python
"""测试LangChainLLMWrapper的callbacks处理"""

import asyncio
from unittest.mock import MagicMock

# 模拟PromptValue
class MockPrompt:
    def to_string(self):
        return "test prompt"

# 模拟ILLMProvider
class MockLLMProvider:
    async def chat(self, messages, model=None, temperature=0.7, max_tokens=None, **kwargs):
        class MockResponse:
            content = "Test response"
        return MockResponse()

# 测试LangChainLLMWrapper
from core.implementations.langchain.langchain_llm import LangChainLLMWrapper, LANGCHAIN_AVAILABLE

if not LANGCHAIN_AVAILABLE:
    print("LangChain not available, skipping test")
    exit(0)

async def test_agenerate_prompt():
    # 创建mock LLM provider
    llm_provider = MockLLMProvider()
    
    # 创建LangChainLLMWrapper
    wrapper = LangChainLLMWrapper(llm_provider)
    
    # 测试1: 正常调用（无callbacks）
    print("Test 1: Normal call without callbacks")
    try:
        result = await wrapper.agenerate_prompt([MockPrompt()], stop=None)
        print(f"  Result type: {type(result)}")
        print("  ✓ Test 1 passed")
    except Exception as e:
        print(f"  ✗ Test 1 failed: {e}")
    
    # 测试2: 调用时传递callbacks
    print("\nTest 2: Call with callbacks in kwargs")
    try:
        callbacks = MagicMock()
        result = await wrapper.agenerate_prompt([MockPrompt()], stop=None, callbacks=callbacks)
        print(f"  Result type: {type(result)}")
        print("  ✓ Test 2 passed")
    except TypeError as e:
        if "multiple values" in str(e):
            print(f"  ✗ Test 2 failed: callbacks conflict - {e}")
        else:
            print(f"  ✗ Test 2 failed: {e}")
    except Exception as e:
        print(f"  ✗ Test 2 failed: {e}")
    
    # 测试3: 传递多个参数
    print("\nTest 3: Call with multiple kwargs")
    try:
        result = await wrapper.agenerate_prompt(
            [MockPrompt()],
            stop=None,
            callbacks=MagicMock(),
            tags=["test"],
            metadata={"key": "value"}
        )
        print(f"  Result type: {type(result)}")
        print("  ✓ Test 3 passed")
    except TypeError as e:
        if "multiple values" in str(e):
            print(f"  ✗ Test 3 failed: callbacks conflict - {e}")
        else:
            print(f"  ✗ Test 3 failed: {e}")
    except Exception as e:
        print(f"  ✗ Test 3 failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_agenerate_prompt())
