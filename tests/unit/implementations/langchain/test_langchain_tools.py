"""
LangChain工具适配器单元测试

测试LangChainToolManager的功能。
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock

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
def native_tool():
    """创建自研Tool实例"""
    from core.agent.tools import Tool
    
    async def tool_func(city: str) -> str:
        return f"{city}的天气是晴天"
    
    return Tool(
        name="get_weather",
        description="获取城市天气",
        parameters={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称"}
            },
            "required": ["city"]
        },
        func=tool_func
    )


@pytest.fixture
def langchain_tool_config() -> Dict[str, Any]:
    """LangChain工具配置"""
    return {
        "tools": {}
    }


@pytest.mark.asyncio
async def test_convert_native_tool_to_langchain(native_tool, langchain_tool_config):
    """测试自研工具转换为LangChain工具"""
    from core.implementations.langchain.langchain_tools import LangChainToolManager
    
    manager = LangChainToolManager(langchain_tool_config)
    langchain_tool = manager._convert_native_tool_to_langchain(native_tool)
    
    assert langchain_tool.name == "get_weather"
    assert langchain_tool.description == "获取城市天气"


def test_register_native_tool(native_tool, langchain_tool_config):
    """测试注册自研工具"""
    from core.implementations.langchain.langchain_tools import LangChainToolManager
    
    manager = LangChainToolManager(langchain_tool_config)
    manager.register(native_tool)
    
    assert "get_weather" in manager.list_tools()


@pytest.mark.asyncio
async def test_execute_tool(native_tool, langchain_tool_config):
    """测试执行工具"""
    from core.implementations.langchain.langchain_tools import LangChainToolManager
    
    manager = LangChainToolManager(langchain_tool_config)
    manager.register(native_tool)
    
    result = await manager.execute("get_weather", {"city": "北京"})
    assert "北京" in result
    assert "天气" in result


def test_get_tool_schema(native_tool, langchain_tool_config):
    """测试获取工具schema"""
    from core.implementations.langchain.langchain_tools import LangChainToolManager
    
    manager = LangChainToolManager(langchain_tool_config)
    manager.register(native_tool)
    
    schema = manager.get_tool_schema("get_weather")
    assert schema["name"] == "get_weather"
    assert "parameters" in schema


def test_get_all_schemas(native_tool, langchain_tool_config):
    """测试获取所有工具schema"""
    from core.implementations.langchain.langchain_tools import LangChainToolManager
    
    manager = LangChainToolManager(langchain_tool_config)
    manager.register(native_tool)
    
    schemas = manager.get_all_schemas()
    assert len(schemas) == 1
    assert schemas[0]["name"] == "get_weather"
