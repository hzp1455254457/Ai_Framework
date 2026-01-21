"""
测试模块：对话上下文测试
功能描述：测试ConversationContext的所有功能
"""

import pytest
from core.llm.context import ConversationContext


class TestConversationContext:
    """ConversationContext测试类"""
    
    def test_add_message(self):
        """测试添加消息"""
        # Arrange
        context = ConversationContext()
        
        # Act
        context.add_message("user", "Hello")
        context.add_message("assistant", "Hi there!")
        
        # Assert
        assert context.message_count == 2
        messages = context.get_messages()
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "Hi there!"
    
    def test_add_message_invalid_role(self):
        """测试添加无效角色的消息"""
        # Arrange
        context = ConversationContext()
        
        # Act & Assert
        with pytest.raises(ValueError):
            context.add_message("invalid_role", "Hello")
    
    def test_get_messages(self):
        """测试获取消息列表"""
        # Arrange
        context = ConversationContext()
        context.add_message("user", "Hello")
        
        # Act
        messages = context.get_messages()
        
        # Assert
        assert isinstance(messages, list)
        assert len(messages) == 1
        # 确保返回的是副本
        messages.append({"role": "system", "content": "New"})
        assert len(context.get_messages()) == 1
    
    def test_clear(self):
        """测试清空上下文"""
        # Arrange
        context = ConversationContext()
        context.add_message("user", "Hello")
        
        # Act
        context.clear()
        
        # Assert
        assert context.is_empty is True
        assert context.message_count == 0
    
    def test_max_messages_limit(self):
        """测试最大消息数限制"""
        # Arrange
        context = ConversationContext(max_messages=2)
        
        # Act
        context.add_message("user", "Message 1")
        context.add_message("assistant", "Response 1")
        context.add_message("user", "Message 2")  # 应该移除第一条消息
        
        # Assert
        assert context.message_count == 2
        messages = context.get_messages()
        assert messages[0]["role"] == "assistant"  # 第一条用户消息被移除
    
    def test_is_empty(self):
        """测试空上下文检查"""
        # Arrange
        context = ConversationContext()
        
        # Assert
        assert context.is_empty is True
        
        # Act
        context.add_message("user", "Hello")
        
        # Assert
        assert context.is_empty is False
