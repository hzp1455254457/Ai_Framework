"""
测试模块：连接池管理器测试
功能描述：测试ConnectionPoolManager的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from core.llm.connection_pool import ConnectionPoolManager


@pytest.mark.asyncio
class TestConnectionPoolManager:
    """ConnectionPoolManager测试类"""
    
    @pytest.fixture
    def pool_manager(self):
        """创建连接池管理器fixture"""
        return ConnectionPoolManager(
            max_connections=10,
            max_keepalive_connections=5,
            timeout=30.0,
        )
    
    async def test_pool_manager_initialization(self):
        """测试连接池管理器初始化"""
        # Act
        manager = ConnectionPoolManager(
            max_connections=100,
            max_keepalive_connections=20,
            timeout=30.0,
        )
        
        # Assert
        assert manager._max_connections == 100
        assert manager._max_keepalive_connections == 20
        assert manager._timeout == 30.0
        assert manager._pools == {}
    
    async def test_get_client_new_pool(self, pool_manager):
        """测试获取客户端（新建连接池）"""
        # Arrange
        base_url = "https://api.example.com"
        headers = {"Authorization": "Bearer test-key"}
        
        # Act
        client = await pool_manager.get_client(base_url, headers, timeout=30.0)
        
        # Assert
        assert client is not None
        assert isinstance(client, AsyncClient)
        assert base_url in pool_manager._pools
    
    async def test_get_client_reuse_pool(self, pool_manager):
        """测试获取客户端（复用连接池）"""
        # Arrange
        base_url = "https://api.example.com"
        headers = {"Authorization": "Bearer test-key"}
        
        # 第一次获取
        client1 = await pool_manager.get_client(base_url, headers, timeout=30.0)
        
        # Act - 第二次获取（应该复用）
        client2 = await pool_manager.get_client(base_url, headers, timeout=30.0)
        
        # Assert
        assert client1 is client2  # 应该是同一个客户端
    
    async def test_get_client_different_headers(self, pool_manager):
        """测试不同headers创建不同连接池"""
        # Arrange
        base_url = "https://api.example.com"
        headers1 = {"Authorization": "Bearer key1"}
        headers2 = {"Authorization": "Bearer key2"}
        
        # Act
        client1 = await pool_manager.get_client(base_url, headers1, timeout=30.0)
        client2 = await pool_manager.get_client(base_url, headers2, timeout=30.0)
        
        # Assert
        # 不同headers应该创建不同的连接池
        assert len(pool_manager._pools) == 2
    
    async def test_close_all(self, pool_manager):
        """测试关闭所有连接池"""
        # Arrange
        base_url = "https://api.example.com"
        headers = {"Authorization": "Bearer test-key"}
        
        client = await pool_manager.get_client(base_url, headers, timeout=30.0)
        assert len(pool_manager._pools) > 0
        
        # Act
        await pool_manager.aclose_all()
        
        # Assert
        assert len(pool_manager._pools) == 0
