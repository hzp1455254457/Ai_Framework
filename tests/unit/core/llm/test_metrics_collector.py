"""
测试模块：指标采集器测试
功能描述：测试MetricsCollector的所有功能
"""

import pytest
from unittest.mock import MagicMock, patch
from prometheus_client import CollectorRegistry
from core.llm.metrics_collector import MetricsCollector


@pytest.mark.asyncio
class TestMetricsCollector:
    """MetricsCollector测试类"""
    
    @pytest.fixture
    def collector(self):
        """创建指标采集器fixture"""
        return MetricsCollector()
    
    def test_collector_initialization(self):
        """测试指标采集器初始化"""
        # Act
        collector = MetricsCollector()
        
        # Assert
        assert collector._registry is not None
        assert collector._request_counter is not None
        assert collector._request_duration is not None
        assert collector._token_counter is not None
        assert collector._cost_gauge is not None
    
    def test_collector_with_custom_registry(self):
        """测试使用自定义注册表"""
        # Arrange
        registry = CollectorRegistry()
        
        # Act
        collector = MetricsCollector(registry)
        
        # Assert
        assert collector._registry == registry
    
    def test_record_request_success(self, collector):
        """测试记录成功请求"""
        # Arrange
        tokens = {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        
        # Act
        collector.record_request(
            adapter="openai-adapter",
            model="gpt-3.5-turbo",
            duration=0.5,
            success=True,
            tokens=tokens,
            cost=0.001,
        )
        
        # Assert - 验证指标已记录（通过获取指标数据）
        metrics_data = collector.get_metrics()
        assert b"llm_requests_total" in metrics_data
        assert b"llm_request_duration_seconds" in metrics_data
        assert b"llm_tokens_total" in metrics_data
        assert b"llm_cost_total" in metrics_data
    
    def test_record_request_error(self, collector):
        """测试记录错误请求"""
        # Act
        collector.record_request(
            adapter="openai-adapter",
            model="gpt-3.5-turbo",
            duration=0.1,
            success=False,
            error_type="TimeoutError",
        )
        
        # Assert
        metrics_data = collector.get_metrics()
        assert b"llm_errors_total" in metrics_data
    
    def test_increment_active_requests(self, collector):
        """测试增加活跃请求数"""
        # Act
        collector.increment_active_requests("openai-adapter", "gpt-3.5-turbo")
        
        # Assert
        metrics_data = collector.get_metrics()
        assert b"llm_active_requests" in metrics_data
    
    def test_decrement_active_requests(self, collector):
        """测试减少活跃请求数"""
        # Arrange
        collector.increment_active_requests("openai-adapter", "gpt-3.5-turbo")
        
        # Act
        collector.decrement_active_requests("openai-adapter", "gpt-3.5-turbo")
        
        # Assert
        metrics_data = collector.get_metrics()
        assert b"llm_active_requests" in metrics_data
    
    def test_get_metrics(self, collector):
        """测试获取Prometheus格式指标"""
        # Arrange
        collector.record_request(
            adapter="openai-adapter",
            model="gpt-3.5-turbo",
            duration=0.5,
            success=True,
        )
        
        # Act
        metrics_data = collector.get_metrics()
        
        # Assert
        assert isinstance(metrics_data, bytes)
        assert len(metrics_data) > 0
        assert b"llm_requests_total" in metrics_data
    
    def test_get_content_type(self, collector):
        """测试获取Content-Type"""
        # Act
        content_type = collector.get_content_type()
        
        # Assert
        assert content_type == "text/plain; version=0.0.4; charset=utf-8"
    
    def test_get_registry(self, collector):
        """测试获取注册表"""
        # Act
        registry = collector.get_registry()
        
        # Assert
        assert registry is not None
        assert isinstance(registry, CollectorRegistry)
