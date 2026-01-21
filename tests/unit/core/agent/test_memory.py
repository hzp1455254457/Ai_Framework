"""
测试模块：记忆管理测试
功能描述：测试ShortTermMemory和LongTermMemory的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from core.agent.memory import ShortTermMemory, LongTermMemory, MemoryError


@pytest.mark.asyncio
class TestShortTermMemory:
    """ShortTermMemory测试类"""
    
    async def test_add_message(self):
        """测试添加消息"""
        # Arrange
        memory = ShortTermMemory()
        
        # Act
        memory.add_message("user", "你好")
        memory.add_message("assistant", "你好！")
        
        # Assert
        messages = memory.get_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "你好"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "你好！"
    
    async def test_add_tool_message(self):
        """测试添加工具消息"""
        # Arrange
        memory = ShortTermMemory()
        
        # Act
        memory.add_tool_message("get_weather", "晴天，25°C")
        
        # Assert
        messages = memory.get_messages()
        assert len(messages) == 1
        assert messages[0]["role"] == "tool"
        assert "get_weather" in messages[0]["content"]
        assert "晴天" in messages[0]["content"]
    
    async def test_add_tool_message_with_dict(self):
        """测试添加工具消息（字典结果）"""
        # Arrange
        memory = ShortTermMemory()
        
        # Act
        memory.add_tool_message("get_weather", {"weather": "晴天", "temp": 25})
        
        # Assert
        messages = memory.get_messages()
        assert len(messages) == 1
        assert messages[0]["role"] == "tool"
        assert "get_weather" in messages[0]["content"]
    
    async def test_max_messages_limit(self):
        """测试最大消息数限制"""
        # Arrange
        memory = ShortTermMemory(max_messages=2)
        
        # Act
        memory.add_message("user", "消息1")
        memory.add_message("user", "消息2")
        memory.add_message("user", "消息3")
        
        # Assert
        messages = memory.get_messages()
        assert len(messages) == 2
        assert messages[0]["content"] == "消息2"  # 最旧的消息被移除
        assert messages[1]["content"] == "消息3"
    
    async def test_clear(self):
        """测试清空记忆"""
        # Arrange
        memory = ShortTermMemory()
        memory.add_message("user", "你好")
        
        # Act
        memory.clear()
        
        # Assert
        assert memory.is_empty
        assert memory.message_count == 0


@pytest.mark.asyncio
class TestLongTermMemory:
    """LongTermMemory测试类"""
    
    async def test_save_conversation(self):
        """测试保存对话"""
        # Arrange
        mock_storage = MagicMock()
        mock_storage.save_conversation = AsyncMock()
        memory = LongTermMemory(mock_storage)
        
        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"},
        ]
        metadata = {"task": "greeting"}
        
        # Act
        await memory.save("conv1", messages, metadata)
        
        # Assert
        mock_storage.save_conversation.assert_called_once_with(
            "conv1",
            messages,
            metadata,
        )
    
    async def test_load_conversation(self):
        """测试加载对话"""
        # Arrange
        mock_storage = MagicMock()
        expected_messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"},
        ]
        mock_storage.get_conversation = AsyncMock(return_value=expected_messages)
        memory = LongTermMemory(mock_storage)
        
        # Act
        messages = await memory.load("conv1")
        
        # Assert
        assert messages == expected_messages
        mock_storage.get_conversation.assert_called_once_with("conv1")
    
    async def test_load_nonexistent_conversation(self):
        """测试加载不存在的对话"""
        # Arrange
        mock_storage = MagicMock()
        mock_storage.get_conversation = AsyncMock(return_value=None)
        memory = LongTermMemory(mock_storage)
        
        # Act
        messages = await memory.load("nonexistent")
        
        # Assert
        assert messages is None
    
    async def test_delete_conversation(self):
        """测试删除对话"""
        # Arrange
        mock_storage = MagicMock()
        mock_storage.delete_conversation = AsyncMock()
        memory = LongTermMemory(mock_storage)
        
        # Act
        await memory.delete("conv1")
        
        # Assert
        mock_storage.delete_conversation.assert_called_once_with("conv1")
    
    async def test_list_conversations(self):
        """测试列出对话"""
        # Arrange
        mock_storage = MagicMock()
        expected_list = [
            {"conversation_id": "conv1", "metadata": {}},
            {"conversation_id": "conv2", "metadata": {}},
        ]
        mock_storage.list_conversations = AsyncMock(return_value=expected_list)
        memory = LongTermMemory(mock_storage)
        
        # Act
        conversations = await memory.list_conversations(limit=10, offset=0)
        
        # Assert
        assert conversations == expected_list
        mock_storage.list_conversations.assert_called_once_with(limit=10, offset=0)
    
    async def test_save_with_storage_error(self):
        """测试保存时存储错误"""
        # Arrange
        mock_storage = MagicMock()
        mock_storage.save_conversation = AsyncMock(side_effect=Exception("存储错误"))
        memory = LongTermMemory(mock_storage)
        
        # Act & Assert
        with pytest.raises(MemoryError, match="保存对话失败"):
            await memory.save("conv1", [], {})
