"""
测试模块：请求缓存和去重测试
功能描述：测试RequestCache和RequestDeduplicator的所有功能
"""

import pytest
from unittest.mock import AsyncMock
from core.llm.request_cache import RequestCache, RequestDeduplicator
from core.llm.models import LLMResponse


@pytest.mark.asyncio
class TestRequestCache:
    """RequestCache测试类"""
    
    @pytest.fixture
    def cache(self):
        """创建请求缓存fixture"""
        return RequestCache(ttl=3600.0, max_size=100)
    
    async def test_cache_initialization(self):
        """测试缓存初始化"""
        # Act
        cache = RequestCache(ttl=1800.0, max_size=50)
        
        # Assert
        assert cache._ttl == 1800.0
        assert cache._max_size == 50
    
    async def test_get_cache_miss(self, cache):
        """测试缓存未命中"""
        # Arrange
        cache_key = "test_key"
        
        # Act
        result = await cache.get(cache_key)
        
        # Assert
        assert result is None
    
    async def test_set_and_get_cache(self, cache):
        """测试设置和获取缓存"""
        # Arrange
        cache_key = "test_key"
        response = LLMResponse(
            content="Test response",
            model="test-model",
            usage={"total_tokens": 10},
        )
        
        # Act
        await cache.set(cache_key, response)
        result = await cache.get(cache_key)
        
        # Assert
        assert result is not None
        assert result.content == "Test response"
    
    async def test_cache_expiration(self, cache):
        """测试缓存过期"""
        # Arrange
        cache_key = "test_key"
        response = LLMResponse(
            content="Test response",
            model="test-model",
            usage={"total_tokens": 10},
        )
        
        # 使用很短的TTL
        cache._ttl = 0.1
        
        # Act
        await cache.set(cache_key, response)
        import asyncio
        await asyncio.sleep(0.2)  # 等待过期
        result = await cache.get(cache_key)
        
        # Assert
        assert result is None
    
    async def test_cache_max_size(self, cache):
        """测试缓存最大大小限制"""
        # Arrange
        cache._max_size = 2
        
        # Act
        await cache.set("key1", LLMResponse("response1", "model1"))
        await cache.set("key2", LLMResponse("response2", "model2"))
        await cache.set("key3", LLMResponse("response3", "model3"))
        
        # Assert
        # 应该只保留最新的2个
        assert await cache.get("key1") is None
        assert await cache.get("key2") is not None
        assert await cache.get("key3") is not None
    
    async def test_cleanup(self, cache):
        """测试清理缓存"""
        # Arrange
        await cache.set("key1", LLMResponse("response1", "model1"))
        assert await cache.get("key1") is not None
        
        # Act
        await cache.cleanup()
        
        # Assert
        # 清理后缓存应该为空
        assert await cache.get("key1") is None


@pytest.mark.asyncio
class TestRequestDeduplicator:
    """RequestDeduplicator测试类"""
    
    @pytest.fixture
    def deduplicator(self):
        """创建请求去重器fixture"""
        return RequestDeduplicator()
    
    async def test_deduplicator_initialization(self):
        """测试去重器初始化"""
        # Act
        deduplicator = RequestDeduplicator()
        
        # Assert
        assert deduplicator._pending_requests == {}
    
    async def test_deduplicate_new_request(self, deduplicator):
        """测试去重新请求"""
        # Arrange
        request_key = "test_key"
        
        # Act
        result = await deduplicator.deduplicate(request_key)
        
        # Assert
        assert result is None  # 新请求，返回None
    
    async def test_deduplicate_duplicate_request(self, deduplicator):
        """测试去重重复请求"""
        # Arrange
        request_key = "test_key"
        
        # 第一个请求
        await deduplicator.deduplicate(request_key)
        
        # 创建响应
        response = LLMResponse("response", "model")
        await deduplicator.complete(request_key, response)
        
        # Act - 第二个相同请求
        result = await deduplicator.deduplicate(request_key)
        
        # Assert
        assert result is not None
        assert result.content == "response"
    
    async def test_complete_request(self, deduplicator):
        """测试完成请求"""
        # Arrange
        request_key = "test_key"
        response = LLMResponse("response", "model")
        
        # 先注册请求
        await deduplicator.deduplicate(request_key)
        
        # Act
        await deduplicator.complete(request_key, response)
        
        # Assert
        # 请求应该已完成
        assert request_key not in deduplicator._pending_requests
    
    async def test_cleanup(self, deduplicator):
        """测试清理去重器"""
        # Arrange
        await deduplicator.deduplicate("key1")
        assert len(deduplicator._pending_requests) > 0
        
        # Act
        await deduplicator.cleanup()
        
        # Assert
        assert len(deduplicator._pending_requests) == 0
