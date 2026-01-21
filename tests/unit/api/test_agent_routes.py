"""
测试模块：Agent API路由测试
功能描述：测试Agent路由的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from api.fastapi_app import app
from core.agent.engine import AgentEngine, AgentError


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_agent_engine():
    """创建Mock Agent引擎"""
    engine = MagicMock(spec=AgentEngine)
    engine.run_task = AsyncMock(return_value={
        "content": "测试响应",
        "tool_calls": [],
        "iterations": 1,
        "metadata": {},
    })
    engine.get_tools = MagicMock(return_value=[])
    engine.get_tool_schemas = MagicMock(return_value=[])
    engine._tool_registry = MagicMock()
    return engine


@pytest.mark.asyncio
class TestAgentRoutes:
    """Agent路由测试类"""
    
    @patch("api.dependencies.get_agent_engine")
    async def test_run_task_success(self, mock_get_engine, client, mock_agent_engine):
        """测试任务执行成功"""
        # Arrange
        mock_get_engine.return_value = mock_agent_engine
        request_data = {
            "task": "测试任务",
            "conversation_id": "conv-123",
        }
        
        # Act
        response = client.post("/api/v1/agent/task", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "测试响应"
        assert data["iterations"] == 1
        mock_agent_engine.run_task.assert_called_once()
    
    @patch("api.dependencies.get_agent_engine")
    async def test_run_task_with_empty_task(self, mock_get_engine, client, mock_agent_engine):
        """测试空任务请求"""
        # Arrange
        mock_get_engine.return_value = mock_agent_engine
        mock_agent_engine.run_task = AsyncMock(side_effect=AgentError("任务不能为空"))
        request_data = {
            "task": "",
        }
        
        # Act
        response = client.post("/api/v1/agent/task", json=request_data)
        
        # Assert
        assert response.status_code == 400
    
    @patch("api.dependencies.get_agent_engine")
    async def test_list_tools(self, mock_get_engine, client, mock_agent_engine):
        """测试获取工具列表"""
        # Arrange
        mock_get_engine.return_value = mock_agent_engine
        mock_agent_engine.get_tools = MagicMock(return_value=["tool1", "tool2"])
        mock_agent_engine.get_tool_schemas = MagicMock(return_value=[
            {"name": "tool1", "description": "工具1"},
            {"name": "tool2", "description": "工具2"},
        ])
        
        # Act
        response = client.get("/api/v1/agent/tools")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert "tool1" in data["tools"]
        assert "tool2" in data["tools"]
    
    @patch("api.dependencies.get_agent_engine")
    async def test_register_tool_success(self, mock_get_engine, client, mock_agent_engine):
        """测试工具注册成功"""
        # Arrange
        mock_get_engine.return_value = mock_agent_engine
        mock_agent_engine.get_tools = MagicMock(return_value=[])
        request_data = {
            "name": "test_tool",
            "description": "测试工具",
            "parameters": {
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                }
            },
            "allow_override": False,
        }
        
        # Act
        response = client.post("/api/v1/agent/tools/register", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["tool_name"] == "test_tool"
    
    @patch("api.dependencies.get_agent_engine")
    async def test_register_tool_with_duplicate_name(self, mock_get_engine, client, mock_agent_engine):
        """测试注册重复工具名称"""
        # Arrange
        mock_get_engine.return_value = mock_agent_engine
        mock_agent_engine.get_tools = MagicMock(return_value=["test_tool"])
        request_data = {
            "name": "test_tool",
            "description": "测试工具",
            "parameters": {"type": "object"},
            "allow_override": False,
        }
        
        # Act
        response = client.post("/api/v1/agent/tools/register", json=request_data)
        
        # Assert
        assert response.status_code == 409
        data = response.json()
        assert "工具已存在" in data["detail"]
