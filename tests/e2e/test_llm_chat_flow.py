"""
端到端测试：LLM聊天流程
功能描述：测试完整的LLM聊天端到端流程
"""

import pytest
from core.llm.service import LLMService
from core.llm.context import ConversationContext
from core.llm.adapters.base import BaseLLMAdapter
from unittest.mock import AsyncMock


class MockAdapter(BaseLLMAdapter):
    """用于测试的Mock适配器"""
    
    @property
    def name(self) -> str:
        return "mock-adapter"
    
    @property
    def provider(self) -> str:
        return "mock"
    
    async def call(self, messages, model, **kwargs):
        # 模拟根据消息内容返回不同的响应
        last_message = messages[-1]["content"] if messages else ""
        if "你好" in last_message or "Hello" in last_message:
            return {
                "content": "你好！很高兴为您服务。",
                "usage": {"total_tokens": 20},
                "metadata": {},
            }
        elif "问题" in last_message or "question" in last_message.lower():
            return {
                "content": "这是一个很好的问题。让我来帮您解答。",
                "usage": {"total_tokens": 25},
                "metadata": {},
            }
        else:
            return {
                "content": "我明白了。",
                "usage": {"total_tokens": 15},
                "metadata": {},
            }


@pytest.mark.asyncio
class TestLLMChatFlow:
    """LLM聊天流程端到端测试类"""
    
    async def test_complete_chat_conversation(self):
        """测试完整的对话流程"""
        # Arrange
        config = {
            "llm": {
                "default_model": "mock-model",
                "auto_discover_adapters": False,
            }
        }
        service = LLMService(config)
        await service.initialize()
        
        adapter = MockAdapter({})
        await adapter.initialize()
        service.register_adapter(adapter)
        
        context = ConversationContext(max_messages=10)
        
        # Act & Assert - 第一轮对话
        user_message1 = "你好"
        context.add_message("user", user_message1)
        
        response1 = await service.chat(context.get_messages())
        assert "你好" in response1.content or "Hello" in response1.content
        
        context.add_message("assistant", response1.content)
        
        # Act & Assert - 第二轮对话
        user_message2 = "我有一个问题"
        context.add_message("user", user_message2)
        
        response2 = await service.chat(context.get_messages())
        assert len(response2.content) > 0
        
        context.add_message("assistant", response2.content)
        
        # Assert - 验证上下文管理
        assert len(context.get_messages()) == 4  # 2轮对话，每轮2条消息
    
    async def test_context_limits(self):
        """测试上下文消息数限制"""
        # Arrange
        config = {
            "llm": {
                "default_model": "mock-model",
                "auto_discover_adapters": False,
            }
        }
        service = LLMService(config)
        await service.initialize()
        
        adapter = MockAdapter({})
        await adapter.initialize()
        service.register_adapter(adapter)
        
        context = ConversationContext(max_messages=3)  # 限制为3条消息
        
        # Act - 添加超过限制的消息
        context.add_message("user", "消息1")
        context.add_message("assistant", "回复1")
        context.add_message("user", "消息2")
        context.add_message("assistant", "回复2")  # 这应该触发限制
        
        # Assert
        messages = context.get_messages()
        assert len(messages) <= 3  # 应该不超过限制
    
    async def test_error_handling(self):
        """测试错误处理"""
        # Arrange
        config = {
            "llm": {
                "default_model": "mock-model",
                "auto_discover_adapters": False,
            }
        }
        service = LLMService(config)
        await service.initialize()
        
        # Act & Assert - 没有适配器时应该抛出异常
        with pytest.raises(Exception):
            await service.chat([{"role": "user", "content": "Hello"}])
        
        # Act & Assert - 空消息列表应该抛出异常
        adapter = MockAdapter({})
        await adapter.initialize()
        service.register_adapter(adapter)
        
        with pytest.raises(ValueError):
            await service.chat([])
