"""
测试模块：API集成测试
功能描述：测试API接口的集成功能
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from api.fastapi_app import app
from core.llm.models import LLMResponse


@pytest.fixture
def mock_llm_service():
    """创建Mock LLM服务"""
    service = MagicMock()
    service._adapters = {"test-adapter": MagicMock()}
    service._registry = MagicMock()
    service._registry.get_supported_models.return_value = ["model1", "model2"]
    return service


@pytest.fixture
def mock_config_manager():
    """创建Mock配置管理器"""
    config = MagicMock()
    config.get_all.return_value = {
        "llm": {
            "default_model": "test-model",
            "auto_discover_adapters": True,
            "adapters": {}
        }
    }
    return config


@pytest.fixture
def client(mock_llm_service, mock_config_manager):
    """创建测试客户端，覆盖依赖"""
    # 覆盖依赖
    app.dependency_overrides.clear()
    
    async def get_config():
        return mock_config_manager
    
    async def get_llm():
        return mock_llm_service
    
    from api import dependencies
    from api.routes import health, llm
    
    app.dependency_overrides[dependencies.get_config_manager] = get_config
    app.dependency_overrides[dependencies.get_llm_service] = get_llm
    
    yield TestClient(app)
    
    # 清理
    app.dependency_overrides.clear()


class TestHealthAPI:
    """健康检查API测试"""
    
    def test_health_check(self, client, setup_mocks):
        """测试健康检查接口"""
        response = client.get("/api/v1/health/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "adapters" in data
        assert "models" in data


class TestLLMAPI:
    """LLM API测试"""
    
    def test_chat_endpoint(self, client, setup_mocks):
        """测试聊天接口"""
        # 需要为这个测试单独设置mock
        with patch("api.routes.llm.get_llm_service") as mock_get_service:
            from core.llm.models import LLMResponse
            
            mock_service = MagicMock()
            mock_response = LLMResponse(
                content="Hello, AI!",
                model="gpt-3.5-turbo",
                usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                metadata={}
            )
            mock_service.chat = AsyncMock(return_value=mock_response)
            mock_get_service.return_value = mock_service
            
            # 发送请求
            response = client.post(
                "/api/v1/llm/chat",
                json={
                    "messages": [{"role": "user", "content": "Hello"}],
                    "model": "gpt-3.5-turbo",
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "content" in data
            assert "model" in data
            assert "usage" in data
    
    def test_list_models(self, client, setup_mocks):
        """测试模型列表接口"""
        response = client.get("/api/v1/llm/models")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_root_endpoint(self, client):
        """测试根路径接口"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
