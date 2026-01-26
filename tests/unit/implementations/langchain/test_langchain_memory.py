"""
LangChain记忆适配器单元测试

测试LangChainMemory的功能。
"""

import pytest
from typing import Dict, Any

# 检查LangChain是否可用
try:
    import langchain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not LANGCHAIN_AVAILABLE,
    reason="LangChain未安装，跳过测试"
)


@pytest.fixture
def langchain_memory_config() -> Dict[str, Any]:
    """LangChain记忆配置"""
    return {
        "memory": {
            "type": "buffer"
        }
    }


def test_add_user_message(langchain_memory_config):
    """测试添加user消息"""
    from core.implementations.langchain.langchain_memory import LangChainMemory
    
    memory = LangChainMemory(langchain_memory_config)
    memory.add_message("user", "Hello")
    
    assert memory.message_count > 0


def test_add_assistant_message(langchain_memory_config):
    """测试添加assistant消息"""
    from core.implementations.langchain.langchain_memory import LangChainMemory
    
    memory = LangChainMemory(langchain_memory_config)
    memory.add_message("assistant", "Hi there!")
    
    assert memory.message_count > 0


def test_get_messages(langchain_memory_config):
    """测试获取消息列表"""
    from core.implementations.langchain.langchain_memory import LangChainMemory
    
    memory = LangChainMemory(langchain_memory_config)
    memory.add_message("user", "Hello")
    memory.add_message("assistant", "Hi there!")
    
    messages = memory.get_messages()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


def test_clear_memory(langchain_memory_config):
    """测试清空记忆"""
    from core.implementations.langchain.langchain_memory import LangChainMemory
    
    memory = LangChainMemory(langchain_memory_config)
    memory.add_message("user", "Hello")
    memory.clear()
    
    assert memory.message_count == 0


def test_message_count(langchain_memory_config):
    """测试消息计数"""
    from core.implementations.langchain.langchain_memory import LangChainMemory
    
    memory = LangChainMemory(langchain_memory_config)
    assert memory.message_count == 0
    
    memory.add_message("user", "Hello")
    assert memory.message_count == 1
    
    memory.add_message("assistant", "Hi")
    assert memory.message_count == 2
