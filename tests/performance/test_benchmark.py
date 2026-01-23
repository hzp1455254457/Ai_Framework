"""
测试模块：性能基准测试
功能描述：测试新架构的性能，确保性能不下降
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from core.llm.service import LLMService
from core.llm.adapters.base import BaseLLMAdapter


class MockAdapter(BaseLLMAdapter):
    """用于性能测试的Mock适配器"""
    
    def __init__(self, name="mock-adapter", delay=0.01):
        super().__init__()
        self._name = name
        self._delay = delay  # 模拟网络延迟
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def provider(self) -> str:
        return "mock"
    
    async def call(self, messages, model, **kwargs):
        # 模拟网络延迟
        await asyncio.sleep(self._delay)
        return {
            "content": "Mock response",
            "usage": {"total_tokens": 10},
            "metadata": {},
        }
    
    async def stream_call(self, messages, model, **kwargs):
        # 模拟流式响应
        await asyncio.sleep(self._delay)
        yield {"content": "Mock", "usage": {"total_tokens": 5}}
        await asyncio.sleep(self._delay)
        yield {"content": " response", "usage": {"total_tokens": 5}}


@pytest.mark.asyncio
@pytest.mark.slow
class TestPerformanceBenchmark:
    """性能基准测试类"""
    
    @pytest.fixture
    def service_config(self):
        """创建服务配置fixture"""
        return {
            "llm": {
                "default_model": "test-model",
                "performance": {
                    "enable_connection_pool": True,
                    "enable_cache": True,
                    "enable_deduplication": True,
                },
            },
        }
    
    @pytest.fixture
    def service_config_no_optimization(self):
        """创建无优化配置fixture"""
        return {
            "llm": {
                "default_model": "test-model",
                "performance": {
                    "enable_connection_pool": False,
                    "enable_cache": False,
                    "enable_deduplication": False,
                },
            },
        }
    
    async def test_chat_latency_with_optimization(self, service_config):
        """测试启用优化后的聊天延迟"""
        # Arrange
        service = LLMService(service_config)
        await service.initialize()
        
        adapter = MockAdapter(delay=0.01)
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act - 执行多次请求并测量延迟
        latencies = []
        for _ in range(10):
            start_time = time.time()
            await service.chat(messages)
            latency = time.time() - start_time
            latencies.append(latency)
        
        # Assert
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        # 平均延迟应该小于50ms（包括优化开销）
        assert avg_latency < 0.05, f"平均延迟 {avg_latency:.3f}s 超过阈值"
        # 最大延迟应该小于100ms
        assert max_latency < 0.1, f"最大延迟 {max_latency:.3f}s 超过阈值"
        
        print(f"✅ 启用优化后 - 平均延迟: {avg_latency:.3f}s, 最大延迟: {max_latency:.3f}s")
    
    async def test_chat_latency_without_optimization(self, service_config_no_optimization):
        """测试未启用优化时的聊天延迟（基准）"""
        # Arrange
        service = LLMService(service_config_no_optimization)
        await service.initialize()
        
        adapter = MockAdapter(delay=0.01)
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act - 执行多次请求并测量延迟
        latencies = []
        for _ in range(10):
            start_time = time.time()
            await service.chat(messages)
            latency = time.time() - start_time
            latencies.append(latency)
        
        # Assert
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        print(f"📊 未启用优化 - 平均延迟: {avg_latency:.3f}s, 最大延迟: {max_latency:.3f}s")
    
    async def test_cache_performance(self, service_config):
        """测试缓存性能提升"""
        # Arrange
        service = LLMService(service_config)
        await service.initialize()
        
        adapter = MockAdapter(delay=0.05)  # 较大的延迟以突出缓存效果
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act - 第一次请求（无缓存）
        start_time = time.time()
        await service.chat(messages)
        first_request_time = time.time() - start_time
        
        # 第二次请求（有缓存）
        start_time = time.time()
        await service.chat(messages)
        second_request_time = time.time() - start_time
        
        # Assert
        # 缓存请求应该明显更快
        assert second_request_time < first_request_time * 0.5, \
            f"缓存未生效: 第一次 {first_request_time:.3f}s, 第二次 {second_request_time:.3f}s"
        
        print(f"✅ 缓存性能 - 第一次: {first_request_time:.3f}s, 第二次: {second_request_time:.3f}s")
    
    async def test_concurrent_requests(self, service_config):
        """测试并发请求性能"""
        # Arrange
        service = LLMService(service_config)
        await service.initialize()
        
        adapter = MockAdapter(delay=0.01)
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act - 并发执行多个请求
        start_time = time.time()
        tasks = [service.chat(messages) for _ in range(20)]
        await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Assert
        # 并发请求总时间应该远小于串行请求时间
        # 串行时间约为 20 * 0.01 = 0.2s，并发应该明显更快
        assert total_time < 0.15, f"并发性能不佳: 总时间 {total_time:.3f}s"
        
        print(f"✅ 并发性能 - 20个请求总时间: {total_time:.3f}s")
    
    async def test_stream_chat_latency(self, service_config):
        """测试流式聊天延迟"""
        # Arrange
        service = LLMService(service_config)
        await service.initialize()
        
        adapter = MockAdapter(delay=0.01)
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act - 测量首块延迟
        start_time = time.time()
        first_chunk = None
        async for chunk in service.stream_chat(messages):
            if first_chunk is None:
                first_chunk_time = time.time() - start_time
                first_chunk = chunk
                break
        
        # Assert
        # 首块延迟应该小于50ms
        assert first_chunk_time < 0.05, f"首块延迟 {first_chunk_time:.3f}s 超过阈值"
        
        print(f"✅ 流式响应首块延迟: {first_chunk_time:.3f}s")
    
    async def test_memory_usage(self, service_config):
        """测试内存使用情况"""
        import psutil
        import os
        
        # Arrange
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        service = LLMService(service_config)
        await service.initialize()
        
        adapter = MockAdapter()
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act - 执行多次请求
        for _ in range(100):
            await service.chat(messages)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Assert
        # 内存增长应该小于50MB（包括缓存等）
        assert memory_increase < 50, f"内存增长 {memory_increase:.2f}MB 超过阈值"
        
        print(f"✅ 内存使用 - 初始: {initial_memory:.2f}MB, 最终: {final_memory:.2f}MB, 增长: {memory_increase:.2f}MB")
    
    async def test_cleanup(self, service_config):
        """测试资源清理"""
        # Arrange
        service = LLMService(service_config)
        await service.initialize()
        
        # Act
        await service.cleanup()
        
        # Assert - 应该没有异常抛出
        assert True
