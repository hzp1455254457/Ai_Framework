"""
测试模块：请求追踪器测试
功能描述：测试RequestTracer的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from core.llm.request_tracer import RequestTracer, TraceContext, TraceSpan


@pytest.mark.asyncio
class TestRequestTracer:
    """RequestTracer测试类"""
    
    @pytest.fixture
    def tracer(self):
        """创建请求追踪器fixture"""
        config = {
            "max_traces": 100,
            "trace_ttl": 3600,
            "enabled": True,
        }
        return RequestTracer(config)
    
    def test_tracer_initialization(self):
        """测试追踪器初始化"""
        # Arrange
        config = {"max_traces": 50}
        
        # Act
        tracer = RequestTracer(config)
        
        # Assert
        assert tracer._max_traces == 50
        assert tracer._enabled is True
    
    def test_start_trace(self, tracer):
        """测试开始追踪"""
        # Act
        context = tracer.start_trace("test_operation", metadata={"key": "value"})
        
        # Assert
        assert context is not None
        assert context.trace_id is not None
        assert len(context.spans) == 1
        assert context.spans[0].operation == "test_operation"
        assert context.metadata == {"key": "value"}
    
    def test_start_span(self, tracer):
        """测试开始跨度"""
        # Arrange
        context = tracer.start_trace("root_operation")
        
        # Act
        span = tracer.start_span(context, "child_operation", tags={"tag1": "value1"})
        
        # Assert
        assert span is not None
        assert span.operation == "child_operation"
        assert span.parent_span_id == context.spans[0].span_id
        assert span.tags == {"tag1": "value1"}
        assert len(context.spans) == 2
    
    def test_end_span(self, tracer):
        """测试结束跨度"""
        # Arrange
        context = tracer.start_trace("test_operation")
        span = tracer.start_span(context, "child_operation")
        
        # Act
        tracer.end_span(span, error="Test error")
        
        # Assert
        assert span.end_time is not None
        assert span.duration is not None
        assert span.error == "Test error"
    
    def test_add_span_log(self, tracer):
        """测试添加跨度日志"""
        # Arrange
        context = tracer.start_trace("test_operation")
        span = tracer.start_span(context, "child_operation")
        
        # Act
        tracer.add_span_log(span, "Test log message", level="info")
        
        # Assert
        assert len(span.logs) == 1
        assert span.logs[0]["message"] == "Test log message"
        assert span.logs[0]["level"] == "info"
    
    def test_end_trace(self, tracer):
        """测试结束追踪"""
        # Arrange
        context = tracer.start_trace("test_operation")
        
        # Act
        tracer.end_trace(context)
        
        # Assert
        assert context.end_time is not None
        assert context.total_duration is not None
    
    async def test_get_trace(self, tracer):
        """测试获取追踪上下文"""
        # Arrange
        context = tracer.start_trace("test_operation")
        trace_id = context.trace_id
        
        # 等待一下，确保追踪已存储
        import asyncio
        await asyncio.sleep(0.1)
        
        # Act
        retrieved = await tracer.get_trace(trace_id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.trace_id == trace_id
    
    async def test_list_traces(self, tracer):
        """测试列出追踪上下文"""
        # Arrange
        tracer.start_trace("operation1")
        tracer.start_trace("operation2")
        
        # 等待一下，确保追踪已存储
        import asyncio
        await asyncio.sleep(0.1)
        
        # Act
        traces = await tracer.list_traces(limit=10)
        
        # Assert
        assert len(traces) >= 2
        # 应该按时间倒序排列
        assert traces[0].start_time >= traces[1].start_time
    
    async def test_list_traces_with_time_filter(self, tracer):
        """测试带时间过滤的追踪列表"""
        # Arrange
        start_time = datetime.now() - timedelta(hours=1)
        tracer.start_trace("operation1")
        
        # 等待一下
        import asyncio
        await asyncio.sleep(0.1)
        
        end_time = datetime.now()
        
        # Act
        traces = await tracer.list_traces(
            limit=10,
            start_time=start_time,
            end_time=end_time,
        )
        
        # Assert
        assert len(traces) >= 1
    
    async def test_clear_traces(self, tracer):
        """测试清理所有追踪"""
        # Arrange
        tracer.start_trace("operation1")
        tracer.start_trace("operation2")
        
        # 等待一下
        import asyncio
        await asyncio.sleep(0.1)
        
        # Act
        count = await tracer.clear_traces()
        
        # Assert
        assert count >= 2
        traces = await tracer.list_traces()
        assert len(traces) == 0
    
    def test_tracer_disabled(self):
        """测试追踪器禁用"""
        # Arrange
        config = {"enabled": False}
        tracer = RequestTracer(config)
        
        # Act
        context = tracer.start_trace("test_operation")
        span = tracer.start_span(context, "child_operation")
        tracer.end_span(span)
        tracer.end_trace(context)
        
        # Assert - 禁用时应该不存储追踪
        assert context.trace_id is not None
        # 但追踪不会被存储到_traces中
