"""
模块名称：LLM重试工具模块
功能描述：提供LLM适配器的重试机制
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要功能：
    - retry_llm_call: LLM调用重试装饰器
    - is_retryable_error: 判断错误是否可重试
"""

import asyncio
from typing import Callable, Any, Type, Tuple, List
from functools import wraps
from httpx import HTTPError, HTTPStatusError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_exception,
    RetryError,
)
from core.base.adapter import AdapterCallError


def is_retryable_error(exception: Exception) -> bool:
    """
    判断错误是否可重试
    
    可重试的错误类型：
        - 网络错误（ConnectionError, TimeoutError）
        - 5xx服务器错误
        - 429请求过多（限流）
        - 某些4xx错误（如502 Bad Gateway）
    
    参数:
        exception: 异常对象
    
    返回:
        True表示可重试，False表示不可重试
    """
    # 网络错误可重试
    if isinstance(exception, (ConnectionError, TimeoutError, asyncio.TimeoutError)):
        return True
    
    # HTTP错误
    if isinstance(exception, HTTPStatusError):
        if exception.response is None:
            # 没有响应对象的HTTP错误，可能是网络错误，可重试
            return True
        
        status_code = exception.response.status_code
        
        # 5xx服务器错误可重试
        if 500 <= status_code < 600:
            return True
        
        # 429请求过多可重试
        if status_code == 429:
            return True
        
        # 502 Bad Gateway可重试
        if status_code == 502:
            return True
        
        # 503 Service Unavailable可重试
        if status_code == 503:
            return True
        
        # 504 Gateway Timeout可重试
        if status_code == 504:
            return True
        
        # 其他4xx错误不可重试
        return False
    
    # HTTPError（其他HTTP错误，通常是网络层面的错误，可重试）
    if isinstance(exception, HTTPError):
        # HTTPError但不包含status code，通常是网络错误，可重试
        return True
    
    # 其他AdapterCallError不重试（可能是参数错误等）
    if isinstance(exception, AdapterCallError):
        return False
    
    # 其他异常默认不重试
    return False


def retry_llm_call(
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 10.0,
    exponential_base: float = 2.0,
):
    """
    LLM调用重试装饰器
    
    使用指数退避策略进行重试，避免对服务器造成过大压力。
    
    参数:
        max_attempts: 最大重试次数（不包括首次尝试）
        initial_wait: 初始等待时间（秒）
        max_wait: 最大等待时间（秒）
        exponential_base: 指数退避的基数
    
    示例:
        >>> @retry_llm_call(max_attempts=3, initial_wait=1.0)
        ... async def call_api():
        ...     # API调用逻辑
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_attempts + 1),  # +1 包括首次尝试
            wait=wait_exponential(
                multiplier=initial_wait,
                max=max_wait,
                exp_base=exponential_base,
            ),
            retry=retry_if_exception(is_retryable_error),
            reraise=True,
        )
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # 如果错误不可重试，直接抛出
                if not is_retryable_error(e):
                    raise
                # 可重试的错误会由tenacity处理
                raise
        
        return wrapper
    
    return decorator


async def retry_with_backoff(
    func: Callable,
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 10.0,
    exponential_base: float = 2.0,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    带指数退避的重试函数
    
    不依赖装饰器，直接调用函数并处理重试。
    
    参数:
        func: 要重试的异步函数
        max_attempts: 最大重试次数
        initial_wait: 初始等待时间（秒）
        max_wait: 最大等待时间（秒）
        exponential_base: 指数退避的基数
        *args: 传递给func的位置参数
        **kwargs: 传递给func的关键字参数
    
    返回:
        func的返回值
    
    异常:
        最后一次重试失败后抛出原始异常
    """
    last_exception = None
    
    for attempt in range(max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            # 如果错误不可重试，直接抛出
            if not is_retryable_error(e):
                raise
            
            # 如果是最后一次尝试，抛出异常
            if attempt >= max_attempts:
                break
            
            # 计算等待时间（指数退避）
            wait_time = min(
                initial_wait * (exponential_base ** attempt),
                max_wait,
            )
            
            await asyncio.sleep(wait_time)
    
    # 所有重试都失败了，抛出最后一个异常
    raise last_exception
