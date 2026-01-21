"""
测试模块：工具系统测试
功能描述：测试Tool和ToolRegistry的所有功能
"""

import pytest
from core.agent.tools import Tool, ToolRegistry, ToolError


@pytest.mark.asyncio
class TestTool:
    """Tool测试类"""
    
    async def test_tool_creation(self):
        """测试工具创建"""
        # Arrange
        async def get_weather(city: str) -> str:
            return f"{city}的天气是晴天"
        
        # Act
        tool = Tool(
            name="get_weather",
            description="获取城市天气",
            parameters={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"]
            },
            func=get_weather,
        )
        
        # Assert
        assert tool.name == "get_weather"
        assert tool.description == "获取城市天气"
        assert tool.parameters["type"] == "object"
    
    async def test_tool_creation_without_name(self):
        """测试工具创建时缺少名称"""
        # Arrange
        async def func():
            return "result"
        
        # Act & Assert
        with pytest.raises(ToolError, match="工具名称不能为空"):
            Tool(
                name="",
                description="描述",
                parameters={"type": "object"},
                func=func,
            )
    
    async def test_tool_to_function_schema(self):
        """测试工具转换为Function Calling schema"""
        # Arrange
        async def func():
            return "result"
        
        tool = Tool(
            name="test_tool",
            description="测试工具",
            parameters={"type": "object"},
            func=func,
        )
        
        # Act
        schema = tool.to_function_schema()
        
        # Assert
        assert schema["name"] == "test_tool"
        assert schema["description"] == "测试工具"
        assert schema["parameters"] == {"type": "object"}
    
    async def test_tool_execute(self):
        """测试工具执行"""
        # Arrange
        async def get_weather(city: str) -> str:
            return f"{city}的天气是晴天"
        
        tool = Tool(
            name="get_weather",
            description="获取城市天气",
            parameters={"type": "object"},
            func=get_weather,
        )
        
        # Act
        result = await tool.execute({"city": "北京"})
        
        # Assert
        assert result == "北京的天气是晴天"


@pytest.mark.asyncio
class TestToolRegistry:
    """ToolRegistry测试类"""
    
    async def test_register_tool(self):
        """测试注册工具"""
        # Arrange
        registry = ToolRegistry()
        async def func():
            return "result"
        
        tool = Tool(
            name="test_tool",
            description="测试工具",
            parameters={"type": "object"},
            func=func,
        )
        
        # Act
        registry.register(tool)
        
        # Assert
        assert registry.has("test_tool")
        assert registry.get("test_tool") == tool
    
    async def test_register_duplicate_tool(self):
        """测试注册重复工具（默认不允许覆盖）"""
        # Arrange
        registry = ToolRegistry()
        async def func():
            return "result"
        
        tool1 = Tool(
            name="test_tool",
            description="测试工具1",
            parameters={"type": "object"},
            func=func,
        )
        tool2 = Tool(
            name="test_tool",
            description="测试工具2",
            parameters={"type": "object"},
            func=func,
        )
        
        registry.register(tool1)
        
        # Act & Assert
        with pytest.raises(ToolError, match="工具已存在"):
            registry.register(tool2)
    
    async def test_register_duplicate_tool_with_override(self):
        """测试注册重复工具（允许覆盖）"""
        # Arrange
        registry = ToolRegistry(allow_override=True)
        async def func():
            return "result"
        
        tool1 = Tool(
            name="test_tool",
            description="测试工具1",
            parameters={"type": "object"},
            func=func,
        )
        tool2 = Tool(
            name="test_tool",
            description="测试工具2",
            parameters={"type": "object"},
            func=func,
        )
        
        registry.register(tool1)
        
        # Act
        registry.register(tool2)
        
        # Assert
        assert registry.get("test_tool").description == "测试工具2"
    
    async def test_get_function_schemas(self):
        """测试获取Function Calling schema列表"""
        # Arrange
        registry = ToolRegistry()
        async def func():
            return "result"
        
        tool1 = Tool(
            name="tool1",
            description="工具1",
            parameters={"type": "object"},
            func=func,
        )
        tool2 = Tool(
            name="tool2",
            description="工具2",
            parameters={"type": "object"},
            func=func,
        )
        
        registry.register(tool1)
        registry.register(tool2)
        
        # Act
        schemas = registry.get_function_schemas()
        
        # Assert
        assert len(schemas) == 2
        assert schemas[0]["name"] in ["tool1", "tool2"]
        assert schemas[1]["name"] in ["tool1", "tool2"]
    
    async def test_execute_tool(self):
        """测试执行工具"""
        # Arrange
        registry = ToolRegistry()
        async def get_weather(city: str) -> str:
            return f"{city}的天气是晴天"
        
        tool = Tool(
            name="get_weather",
            description="获取城市天气",
            parameters={"type": "object"},
            func=get_weather,
        )
        
        registry.register(tool)
        
        # Act
        result = await registry.execute("get_weather", {"city": "北京"})
        
        # Assert
        assert result == "北京的天气是晴天"
    
    async def test_execute_nonexistent_tool(self):
        """测试执行不存在的工具"""
        # Arrange
        registry = ToolRegistry()
        
        # Act & Assert
        with pytest.raises(ToolError, match="工具不存在"):
            await registry.execute("nonexistent_tool", {})
