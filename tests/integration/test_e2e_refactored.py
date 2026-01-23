"""
测试模块：重构后的端到端集成测试
功能描述：测试新架构功能的端到端集成
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from api.fastapi_app import app


@pytest.mark.asyncio
@pytest.mark.e2e
class TestE2ERefactored:
    """重构后的端到端测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端fixture"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """测试健康检查接口"""
        # Act
        response = client.get("/api/v1/health/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "adapters" in data
        assert "models" in data
    
    def test_model_capabilities_api(self, client):
        """测试模型能力查询API"""
        # Act
        response = client.get("/api/v1/llm/models/capabilities")
        
        # Assert
        assert response.status_code in [200, 503]  # 可能未启用
        if response.status_code == 200:
            data = response.json()
            assert "models" in data
            assert "count" in data
    
    def test_routing_strategies_api(self, client):
        """测试路由策略查询API"""
        # Act
        response = client.get("/api/v1/llm/routing-strategies")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
        assert "count" in data
        assert "default" in data
    
    def test_cost_statistics_api(self, client):
        """测试成本统计API"""
        # Act
        response = client.get("/api/v1/llm/cost/stats")
        
        # Assert
        assert response.status_code in [200, 503]  # 可能未启用
        if response.status_code == 200:
            data = response.json()
            assert "total_cost" in data or "error" in data
    
    def test_metrics_api(self, client):
        """测试监控指标API"""
        # Act
        response = client.get("/api/metrics")
        
        # Assert
        assert response.status_code in [200, 503]  # 可能未启用
        if response.status_code == 200:
            assert response.headers["content-type"].startswith("text/plain")
    
    def test_metrics_stats_api(self, client):
        """测试监控统计API"""
        # Act
        response = client.get("/api/metrics/stats")
        
        # Assert
        assert response.status_code in [200, 503]  # 可能未启用
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
