"""
测试模块：Agent引擎测试
功能描述：测试AgentEngine的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.agent.engine import AgentEngine, AgentError
from core.agent.tools import Tool
from core.llm.service import LLMService
from core.llm.models import LLMResponse


@pytest.mark.asyncio
class TestAgentEngine:
    """AgentEngine测试类"""
    
    async def test_engine_initialization(self):
        """测试引擎初始化"""
        # Arrange
        config = {
            "llm": {
                "default_model": "gpt-3.5-turbo",
                "adapters": {}
            },
            "agent": {
                "max_iterations": 10,
                "enable_long_term_memory": False,
            }
        }
        
        # Act
        engine = AgentEngine(config)
        await engine.initialize()
        
        # Assert
        assert engine.is_initialized is True
        assert engine._llm_service is not None
        assert engine._short_term_memory is not None
    
    async def test_engine_initialization_without_llm_config(self):
        """测试缺少LLM配置时初始化失败"""
        # Arrange
        config = {
            "agent": {}
        }
        
        # Act
        engine = AgentEngine(config)
        
        # Act & Assert
        with pytest.raises(AgentError, match="LLM配置缺失"):
            await engine.initialize()
    
    @patch("core.agent.engine.LLMService")
    async def test_run_task_simple(self, mock_llm_service_class):
        """测试执行简单任务（无需工具）"""
        # Arrange
        config = {
            "llm": {
                "default_model": "gpt-3.5-turbo",
                "adapters": {}
            },
            "agent": {
                "max_iterations": 10,
            }
        }
        
        # Mock LLMService
        mock_llm_service = MagicMock()
        mock_llm_service._default_model = "gpt-3.5-turbo"
        mock_llm_service.chat = AsyncMock(return_value=LLMResponse(
            content="这是测试响应",
            model="gpt-3.5-turbo",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        ))
        mock_llm_service.initialize = AsyncMock()
        mock_llm_service.cleanup = AsyncMock()
        mock_llm_service_class.return_value = mock_llm_service
        
        engine = AgentEngine(config)
        await engine.initialize()
        engine._llm_service = mock_llm_service
        
        # Act
        result = await engine.run_task("测试任务")
        
        # Assert
        assert result["content"] == "这是测试响应"
        assert result["iterations"] == 1
        assert len(result["tool_calls"]) == 0
    
    @patch("core.agent.engine.LLMService")
    async def test_run_task_with_tool_call(self, mock_llm_service_class):
        """测试执行需要工具调用的任务"""
        # Arrange
        config = {
            "llm": {
                "default_model": "gpt-3.5-turbo",
                "adapters": {}
            },
            "agent": {
                "max_iterations": 10,
            }
        }
        
        # 注册工具
        async def get_weather(city: str) -> str:
            return f"{city}的天气是晴天"
        
        tool = Tool(
            name="get_weather",
            description="获取城市天气",
            parameters={
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            },
            func=get_weather,
        )
        
        # Mock LLMService - 第一次返回工具调用，第二次返回最终结果
        mock_llm_service = MagicMock()
        mock_llm_service._default_model = "gpt-3.5-turbo"
        
        call_count = 0
        async def mock_chat(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # 第一次调用：返回工具调用
                return LLMResponse(
                    content="",
                    model="gpt-3.5-turbo",
                    usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                    metadata={
                        "tool_calls": [{
                            "function": {
                                "name": "get_weather",
                                "arguments": '{"city": "北京"}'
                            }
                        }]
                    },
                )
            else:
                # 第二次调用：返回最终结果
                return LLMResponse(
                    content="北京今天晴天，温度25°C",
                    model="gpt-3.5-turbo",
                    usage={"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
                )
        
        mock_llm_service.chat = AsyncMock(side_effect=mock_chat)
        mock_llm_service.initialize = AsyncMock()
        mock_llm_service.cleanup = AsyncMock()
        mock_llm_service_class.return_value = mock_llm_service
        
        engine = AgentEngine(config)
        await engine.initialize()
        engine._llm_service = mock_llm_service
        engine.register_tool(tool)
        
        # Act
        result = await engine.run_task("查询北京天气")
        
        # Assert
        assert result["content"] == "北京今天晴天，温度25°C"
        assert result["iterations"] == 2
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["tool"] == "get_weather"
    
    async def test_run_task_without_initialization(self):
        """测试未初始化时执行任务"""
        # Arrange
        config = {"llm": {"default_model": "gpt-3.5-turbo"}}
        engine = AgentEngine(config)
        
        # Act & Assert
        with pytest.raises(AgentError, match="Agent引擎未初始化"):
            await engine.run_task("测试任务")
    
    async def test_run_task_with_empty_task(self):
        """测试空任务"""
        # Arrange
        config = {
            "llm": {
                "default_model": "gpt-3.5-turbo",
                "adapters": {}
            }
        }
        engine = AgentEngine(config)
        await engine.initialize()
        
        # Act & Assert
        with pytest.raises(AgentError, match="任务不能为空"):
            await engine.run_task("")
    
    async def test_register_tool(self):
        """测试注册工具"""
        # Arrange
        config = {
            "llm": {
                "default_model": "gpt-3.5-turbo",
                "adapters": {}
            }
        }
        engine = AgentEngine(config)
        await engine.initialize()
        
        async def test_func():
            return "result"
        
        tool = Tool(
            name="test_tool",
            description="测试工具",
            parameters={"type": "object"},
            func=test_func,
        )
        
        # Act
        engine.register_tool(tool)
        
        # Assert
        assert "test_tool" in engine.get_tools()
    
    async def test_get_tools(self):
        """测试获取工具列表"""
        # Arrange
        config = {
            "llm": {
                "default_model": "gpt-3.5-turbo",
                "adapters": {}
            }
        }
        engine = AgentEngine(config)
        await engine.initialize()
        
        # Act
        tools = engine.get_tools()
        
        # Assert
        assert isinstance(tools, list)
    
    async def test_clear_memory(self):
        """测试清空记忆"""
        # Arrange
        config = {
            "llm": {
                "default_model": "gpt-3.5-turbo",
                "adapters": {}
            }
        }
        engine = AgentEngine(config)
        await engine.initialize()
        
        # 添加一些消息
        engine._short_term_memory.add_message("user", "测试")
        
        # Act
        engine.clear_memory()
        
        # Assert
        assert engine._short_term_memory.is_empty
