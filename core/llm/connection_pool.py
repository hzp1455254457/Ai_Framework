"""
模块名称：HTTP连接池管理器模块
功能描述：提供HTTP连接池管理，优化连接复用和性能
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - ConnectionPoolManager: HTTP连接池管理器

依赖模块：
    - httpx: 异步HTTP客户端
    - typing: 类型注解
    - asyncio: 异步编程
"""

from typing import Dict, Optional, Any
from httpx import AsyncClient, Limits, Timeout
import asyncio


class ConnectionPoolManager:
    """
    HTTP连接池管理器
    
    管理HTTP连接池，提供连接复用、连接数限制、超时配置等功能。
    
    特性：
        - 连接复用（减少连接建立开销）
        - 连接数限制（防止资源耗尽）
        - 超时配置
        - 多域名连接池管理
    
    示例:
        >>> pool_manager = ConnectionPoolManager()
        >>> client = await pool_manager.get_client("https://api.openai.com")
        >>> response = await client.get("/models")
    """
    
    def __init__(
        self,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        timeout: float = 30.0,
    ) -> None:
        """
        初始化连接池管理器
        
        参数:
            max_connections: 最大连接数
            max_keepalive_connections: 最大保持活跃连接数
            timeout: 默认超时时间（秒）
        """
        self._max_connections = max_connections
        self._max_keepalive_connections = max_keepalive_connections
        self._timeout = timeout
        self._pools: Dict[str, AsyncClient] = {}
        self._lock = asyncio.Lock()
    
    async def get_client(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> AsyncClient:
        """
        获取HTTP客户端（复用连接池）
        
        参数:
            base_url: 基础URL
            headers: 请求头（可选）
            timeout: 超时时间（可选，默认使用初始化时的值）
        
        返回:
            AsyncClient实例
        """
        # 规范化base_url（移除尾部斜杠）
        normalized_url = base_url.rstrip('/')
        
        # 生成缓存键（base_url + headers的哈希）
        cache_key = self._get_cache_key(normalized_url, headers)
        
        async with self._lock:
            # 检查是否已有连接池
            if cache_key in self._pools:
                return self._pools[cache_key]
            
            # 创建新的连接池
            limits = Limits(
                max_connections=self._max_connections,
                max_keepalive_connections=self._max_keepalive_connections,
            )
            
            client_timeout = timeout or self._timeout
            
            client = AsyncClient(
                base_url=normalized_url,
                limits=limits,
                timeout=client_timeout,
                headers=headers or {},
            )
            
            self._pools[cache_key] = client
            return client
    
    def _get_cache_key(self, base_url: str, headers: Optional[Dict[str, str]]) -> str:
        """
        生成缓存键
        
        参数:
            base_url: 基础URL
            headers: 请求头
        
        返回:
            缓存键字符串
        """
        if not headers:
            return base_url
        
        # 使用headers的排序键值对生成哈希
        import hashlib
        import json
        
        headers_str = json.dumps(sorted(headers.items()), sort_keys=True)
        headers_hash = hashlib.md5(headers_str.encode()).hexdigest()[:8]
        return f"{base_url}_{headers_hash}"
    
    async def close_client(self, base_url: str, headers: Optional[Dict[str, str]] = None) -> None:
        """
        关闭指定连接池
        
        参数:
            base_url: 基础URL
            headers: 请求头（可选）
        """
        normalized_url = base_url.rstrip('/')
        cache_key = self._get_cache_key(normalized_url, headers)
        
        async with self._lock:
            if cache_key in self._pools:
                client = self._pools.pop(cache_key)
                await client.aclose()
    
    async def close_all(self) -> None:
        """关闭所有连接池"""
        async with self._lock:
            for client in self._pools.values():
                await client.aclose()
            self._pools.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取连接池统计信息
        
        返回:
            统计信息字典
        """
        return {
            "pool_count": len(self._pools),
            "max_connections": self._max_connections,
            "max_keepalive_connections": self._max_keepalive_connections,
            "pools": list(self._pools.keys()),
        }
