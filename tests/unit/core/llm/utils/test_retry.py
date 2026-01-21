"""
测试模块：重试工具测试
功能描述：测试retry工具模块的所有功能
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from httpx import HTTPStatusError, Response
from core.llm.utils.retry import (
    is_retryable_error,
    retry_with_backoff,
)
from core.base.adapter import AdapterCallError


@pytest.mark.asyncio
class TestRetryUtils:
    """重试工具测试类"""
    
    def test_is_retryable_error_connection_error(self):
        """测试连接错误可重试"""
        error = ConnectionError("Connection failed")
        assert is_retryable_error(error) is True
    
    def test_is_retryable_error_timeout(self):
        """测试超时错误可重试"""
        error = TimeoutError("Timeout")
        assert is_retryable_error(error) is True
    
    def test_is_retryable_error_asyncio_timeout(self):
        """测试asyncio超时错误可重试"""
        error = asyncio.TimeoutError("Timeout")
        assert is_retryable_error(error) is True
    
    def test_is_retryable_error_5xx(self):
        """测试5xx服务器错误可重试"""
        mock_response = Response(status_code=500, text="Internal Server Error")
        error = HTTPStatusError("Server Error", request=None, response=mock_response)
        assert is_retryable_error(error) is True
    
    def test_is_retryable_error_429(self):
        """测试429限流错误可重试"""
        mock_response = Response(status_code=429, text="Too Many Requests")
        error = HTTPStatusError("Rate Limit", request=None, response=mock_response)
        assert is_retryable_error(error) is True
    
    def test_is_retryable_error_502(self):
        """测试502错误可重试"""
        mock_response = Response(status_code=502, text="Bad Gateway")
        error = HTTPStatusError("Bad Gateway", request=None, response=mock_response)
        assert is_retryable_error(error) is True
    
    def test_is_retryable_error_503(self):
        """测试503错误可重试"""
        mock_response = Response(status_code=503, text="Service Unavailable")
        error = HTTPStatusError("Service Unavailable", request=None, response=mock_response)
        assert is_retryable_error(error) is True
    
    def test_is_retryable_error_504(self):
        """测试504错误可重试"""
        mock_response = Response(status_code=504, text="Gateway Timeout")
        error = HTTPStatusError("Gateway Timeout", request=None, response=mock_response)
        assert is_retryable_error(error) is True
    
    def test_is_retryable_error_4xx_not_retryable(self):
        """测试4xx客户端错误不可重试"""
        mock_response = Response(status_code=400, text="Bad Request")
        error = HTTPStatusError("Bad Request", request=None, response=mock_response)
        assert is_retryable_error(error) is False
    
    def test_is_retryable_error_adapter_call_error(self):
        """测试AdapterCallError不可重试"""
        error = AdapterCallError("Adapter error")
        assert is_retryable_error(error) is False
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_success(self):
        """测试重试成功"""
        call_count = 0
        
        async def mock_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await retry_with_backoff(mock_func, max_attempts=3)
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_retry_once(self):
        """测试重试一次后成功"""
        call_count = 0
        
        async def mock_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Connection failed")
            return "success"
        
        result = await retry_with_backoff(mock_func, max_attempts=3, initial_wait=0.1)
        
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_max_attempts(self):
        """测试达到最大重试次数后失败"""
        call_count = 0
        
        async def mock_func():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Connection failed")
        
        with pytest.raises(ConnectionError):
            await retry_with_backoff(mock_func, max_attempts=3, initial_wait=0.1)
        
        assert call_count == 4  # 1 initial + 3 retries
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_non_retryable_error(self):
        """测试不可重试的错误直接抛出"""
        call_count = 0
        
        async def mock_func():
            nonlocal call_count
            call_count += 1
            raise AdapterCallError("Adapter error")
        
        with pytest.raises(AdapterCallError):
            await retry_with_backoff(mock_func, max_attempts=3, initial_wait=0.1)
        
        assert call_count == 1  # 只调用一次，不重试
