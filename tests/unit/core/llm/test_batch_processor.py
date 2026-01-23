"""
测试模块：批量处理器测试
功能描述：测试BatchProcessor的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from core.llm.batch_processor import BatchProcessor


@pytest.mark.asyncio
class TestBatchProcessor:
    """BatchProcessor测试类"""
    
    @pytest.fixture
    def batch_processor(self):
        """创建批量处理器fixture"""
        return BatchProcessor(
            batch_size=5,
            batch_interval=0.1,
            max_wait_time=1.0,
        )
    
    async def test_batch_processor_initialization(self):
        """测试批量处理器初始化"""
        # Act
        processor = BatchProcessor(
            batch_size=10,
            batch_interval=0.2,
            max_wait_time=2.0,
        )
        
        # Assert
        assert processor._batch_size == 10
        assert processor._batch_interval == 0.2
        assert processor._max_wait_time == 2.0
    
    async def test_add_request(self, batch_processor):
        """测试添加请求"""
        # Arrange
        request_id = "req1"
        request_data = {"messages": [{"role": "user", "content": "test"}]}
        callback = AsyncMock()
        
        # Act
        await batch_processor.add_request(request_id, request_data, callback)
        
        # Assert
        assert request_id in batch_processor._pending_requests
    
    async def test_process_batch_when_full(self, batch_processor):
        """测试批量达到大小时处理"""
        # Arrange
        callback = AsyncMock()
        callback.return_value = {"content": "response"}
        
        # 添加足够多的请求填满批次
        for i in range(batch_processor._batch_size):
            await batch_processor.add_request(f"req{i}", {"data": i}, callback)
        
        # 等待批次处理
        import asyncio
        await asyncio.sleep(0.2)
        
        # Assert
        # 回调应该被调用
        assert callback.call_count == batch_processor._batch_size
    
    async def test_process_batch_on_interval(self, batch_processor):
        """测试按间隔处理批次"""
        # Arrange
        callback = AsyncMock()
        callback.return_value = {"content": "response"}
        
        # 添加一个请求（不足以填满批次）
        await batch_processor.add_request("req1", {"data": 1}, callback)
        
        # 等待间隔时间
        import asyncio
        await asyncio.sleep(batch_processor._batch_interval + 0.1)
        
        # Assert
        # 回调应该被调用（按间隔处理）
        assert callback.call_count >= 1
    
    async def test_cleanup(self, batch_processor):
        """测试清理批量处理器"""
        # Arrange
        callback = AsyncMock()
        await batch_processor.add_request("req1", {"data": 1}, callback)
        assert len(batch_processor._pending_requests) > 0
        
        # Act
        await batch_processor.cleanup()
        
        # Assert
        assert len(batch_processor._pending_requests) == 0
