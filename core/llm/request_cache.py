"""
模块名称：请求缓存模块
功能描述：提供请求缓存和去重机制，优化重复请求性能
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - RequestCache: 请求缓存管理器
    - RequestDeduplicator: 请求去重器

依赖模块：
    - typing: 类型注解
    - hashlib: 哈希计算
    - json: JSON序列化
    - asyncio: 异步编程
    - time: 时间处理
"""

from typing import Dict, Any, Optional, Callable, Awaitable
import hashlib
import json
import asyncio
import time


class RequestCache:
    """
    请求缓存管理器
    
    缓存请求结果，减少重复请求，提高性能。
    
    特性：
        - 基于请求内容的哈希缓存
        - TTL（生存时间）支持
        - 异步安全
        - 可配置缓存大小限制
    
    示例:
        >>> cache = RequestCache(ttl=3600, max_size=1000)
        >>> result = await cache.get_or_set(key, fetch_function)
    """
    
    def __init__(
        self,
        ttl: float = 3600.0,
        max_size: int = 1000,
    ) -> None:
        """
        初始化请求缓存
        
        参数:
            ttl: 缓存生存时间（秒）
            max_size: 最大缓存条目数
        """
        self._ttl = ttl
        self._max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    def _generate_key(self, request_data: Dict[str, Any]) -> str:
        """
        生成缓存键
        
        参数:
            request_data: 请求数据
        
        返回:
            缓存键字符串
        """
        # 序列化请求数据并生成哈希
        request_str = json.dumps(request_data, sort_keys=True)
        return hashlib.sha256(request_str.encode()).hexdigest()
    
    async def get(
        self,
        request_data: Dict[str, Any],
    ) -> Optional[Any]:
        """
        获取缓存结果
        
        参数:
            request_data: 请求数据
        
        返回:
            缓存的结果，如果不存在或已过期返回None
        """
        key = self._generate_key(request_data)
        
        async with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            current_time = time.time()
            
            # 检查是否过期
            if current_time - entry["timestamp"] > self._ttl:
                del self._cache[key]
                return None
            
            return entry["value"]
    
    async def set(
        self,
        request_data: Dict[str, Any],
        value: Any,
    ) -> None:
        """
        设置缓存结果
        
        参数:
            request_data: 请求数据
            value: 缓存值
        """
        key = self._generate_key(request_data)
        
        async with self._lock:
            # 检查缓存大小限制
            if len(self._cache) >= self._max_size and key not in self._cache:
                # 删除最旧的条目（简单策略：删除第一个）
                if self._cache:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
            
            self._cache[key] = {
                "value": value,
                "timestamp": time.time(),
            }
    
    async def get_or_set(
        self,
        request_data: Dict[str, Any],
        fetch_func: Callable[[], Awaitable[Any]],
    ) -> Any:
        """
        获取缓存结果，如果不存在则调用函数获取并缓存
        
        参数:
            request_data: 请求数据
            fetch_func: 获取数据的异步函数
        
        返回:
            缓存或新获取的结果
        """
        # 先尝试获取缓存
        cached = await self.get(request_data)
        if cached is not None:
            return cached
        
        # 缓存未命中，调用函数获取
        value = await fetch_func()
        
        # 缓存结果
        await self.set(request_data, value)
        
        return value
    
    async def clear(self) -> None:
        """清空所有缓存"""
        async with self._lock:
            self._cache.clear()
    
    async def cleanup_expired(self) -> int:
        """
        清理过期缓存条目
        
        返回:
            清理的条目数
        """
        current_time = time.time()
        expired_keys = []
        
        async with self._lock:
            for key, entry in self._cache.items():
                if current_time - entry["timestamp"] > self._ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
        
        return len(expired_keys)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        返回:
            统计信息字典
        """
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "ttl": self._ttl,
        }


class RequestDeduplicator:
    """
    请求去重器
    
    合并相同请求，避免重复调用。
    
    特性：
        - 基于请求内容的去重
        - 异步安全
        - 自动清理完成的请求
    
    示例:
        >>> deduplicator = RequestDeduplicator()
        >>> result = await deduplicator.deduplicate(key, fetch_function)
    """
    
    def __init__(self) -> None:
        """初始化请求去重器"""
        self._pending_requests: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
    
    def _generate_key(self, request_data: Dict[str, Any]) -> str:
        """
        生成去重键
        
        参数:
            request_data: 请求数据
        
        返回:
            去重键字符串
        """
        request_str = json.dumps(request_data, sort_keys=True)
        return hashlib.sha256(request_str.encode()).hexdigest()
    
    async def deduplicate(
        self,
        request_data: Dict[str, Any],
        fetch_func: Callable[[], Awaitable[Any]],
    ) -> Any:
        """
        去重请求：如果已有相同请求在进行，则等待其结果
        
        参数:
            request_data: 请求数据
            fetch_func: 获取数据的异步函数
        
        返回:
            请求结果
        """
        key = self._generate_key(request_data)
        
        async with self._lock:
            # 检查是否已有相同请求在进行
            if key in self._pending_requests:
                # 等待现有请求完成
                task = self._pending_requests[key]
                return await task
        
        # 创建新请求任务
        async def _fetch_and_cleanup() -> Any:
            try:
                result = await fetch_func()
                return result
            finally:
                # 清理完成的请求
                async with self._lock:
                    if key in self._pending_requests:
                        del self._pending_requests[key]
        
        task = asyncio.create_task(_fetch_and_cleanup())
        
        async with self._lock:
            self._pending_requests[key] = task
        
        return await task
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取去重器统计信息
        
        返回:
            统计信息字典
        """
        return {
            "pending_requests": len(self._pending_requests),
        }
