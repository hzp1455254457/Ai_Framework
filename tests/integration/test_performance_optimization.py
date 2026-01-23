"""
测试模块：性能优化集成测试
功能描述：测试连接池、缓存、去重、批量处理等性能优化功能的集成
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.llm.service import LLMService
from core.llm.connection_pool import ConnectionPoolManager
from core.llm.request_cache import RequestCache, RequestDeduplicator
from core.llm.batch_processor import BatchProcessor


@pytest.mark.asyncio
@pytest.mark.integration
class TestPerformanceOptimization:
    """性能优化集成测试类"""
    
    @pytest.fixture
    def config_with_performance(self):
        """创建带性能优化配置的配置字典"""
        return {
            "llm": {
                "default_model": "test-model",
                "performance": {
                    "enable_connection_pool": True,
                    "max_connections": 10,
                    "enable_cache": True,
                    "cache_ttl": 3600.0,
                    "enable_deduplication": True,
                    "enable_batch_processing": True,
                    "batch_size": 5,
                },
            },
        }
    
    async def test_connection_pool_integration(self, config_with_performance):
        """测试连接池集成"""
        # Arrange
        service = LLMService(config_with_performance)
        
        # Act
        await service.initialize()
        
        # Assert
        assert service._connection_pool_manager is not None
        assert isinstance(service._connection_pool_manager, ConnectionPoolManager)
    
    async def test_request_cache_integration(self, config_with_performance):
        """测试请求缓存集成"""
        # Arrange
        service = LLMService(config_with_performance)
        
        # Act
        await service.initialize()
        
        # Assert
        assert service._request_cache is not None
        assert isinstance(service._request_cache, RequestCache)
    
    async def test_request_deduplication_integration(self, config_with_performance):
        """测试请求去重集成"""
        # Arrange
        service = LLMService(config_with_performance)
        
        # Act
        await service.initialize()
        
        # Assert
        assert service._request_deduplicator is not None
        assert isinstance(service._request_deduplicator, RequestDeduplicator)
    
    async def test_batch_processor_integration(self, config_with_performance):
        """测试批量处理器集成"""
        # Arrange
        service = LLMService(config_with_performance)
        
        # Act
        await service.initialize()
        
        # Assert
        assert service._batch_processor is not None
        assert isinstance(service._batch_processor, BatchProcessor)
    
    async def test_cleanup_resources(self, config_with_performance):
        """测试资源清理"""
        # Arrange
        service = LLMService(config_with_performance)
        await service.initialize()
        
        # Act
        await service.cleanup()
        
        # Assert - 应该没有异常抛出
        assert True
