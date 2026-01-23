"""
模块名称：批量请求处理模块
功能描述：提供批量请求处理功能，支持批量API调用
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - BatchProcessor: 批量请求处理器

依赖模块：
    - typing: 类型注解
    - asyncio: 异步编程
"""

from typing import List, Dict, Any, Callable, Awaitable, TypeVar, Generic
import asyncio

T = TypeVar('T')


class BatchProcessor(Generic[T]):
    """
    批量请求处理器
    
    将多个请求合并为批量请求，提高处理效率。
    
    特性：
        - 批量请求合并
        - 并发控制
        - 结果映射
        - 错误处理
    
    示例:
        >>> processor = BatchProcessor(batch_size=10, max_concurrent=5)
        >>> results = await processor.process(requests, process_func)
    """
    
    def __init__(
        self,
        batch_size: int = 10,
        max_concurrent: int = 5,
        timeout: float = 60.0,
    ) -> None:
        """
        初始化批量处理器
        
        参数:
            batch_size: 批量大小
            max_concurrent: 最大并发数
            timeout: 超时时间（秒）
        """
        self._batch_size = batch_size
        self._max_concurrent = max_concurrent
        self._timeout = timeout
    
    async def process(
        self,
        items: List[T],
        process_func: Callable[[List[T]], Awaitable[List[Any]]],
    ) -> List[Any]:
        """
        批量处理项目
        
        参数:
            items: 待处理项目列表
            process_func: 处理函数（接收批量项目，返回批量结果）
        
        返回:
            处理结果列表
        """
        if not items:
            return []
        
        # 分批处理
        batches = [
            items[i:i + self._batch_size]
            for i in range(0, len(items), self._batch_size)
        ]
        
        # 使用信号量控制并发
        semaphore = asyncio.Semaphore(self._max_concurrent)
        
        async def process_batch(batch: List[T]) -> List[Any]:
            async with semaphore:
                try:
                    return await asyncio.wait_for(
                        process_func(batch),
                        timeout=self._timeout,
                    )
                except asyncio.TimeoutError:
                    # 超时返回空结果
                    return [None] * len(batch)
                except Exception as e:
                    # 错误返回空结果
                    return [None] * len(batch)
        
        # 并发处理所有批次
        batch_results = await asyncio.gather(*[
            process_batch(batch) for batch in batches
        ])
        
        # 展平结果
        results = []
        for batch_result in batch_results:
            results.extend(batch_result)
        
        return results
    
    async def process_with_mapping(
        self,
        items: List[T],
        process_func: Callable[[List[T]], Awaitable[Dict[T, Any]]],
    ) -> Dict[T, Any]:
        """
        批量处理项目（返回映射结果）
        
        参数:
            items: 待处理项目列表
            process_func: 处理函数（接收批量项目，返回映射结果）
        
        返回:
            处理结果映射
        """
        if not items:
            return {}
        
        # 分批处理
        batches = [
            items[i:i + self._batch_size]
            for i in range(0, len(items), self._batch_size)
        ]
        
        # 使用信号量控制并发
        semaphore = asyncio.Semaphore(self._max_concurrent)
        
        async def process_batch(batch: List[T]) -> Dict[T, Any]:
            async with semaphore:
                try:
                    return await asyncio.wait_for(
                        process_func(batch),
                        timeout=self._timeout,
                    )
                except (asyncio.TimeoutError, Exception):
                    # 超时或错误返回空映射
                    return {}
        
        # 并发处理所有批次
        batch_results = await asyncio.gather(*[
            process_batch(batch) for batch in batches
        ])
        
        # 合并结果
        result = {}
        for batch_result in batch_results:
            result.update(batch_result)
        
        return result
