"""
模块名称：连接池管理模块
功能描述：提供HTTP和数据库连接池管理
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - ConnectionPoolManager: 连接池管理器
    - HTTPConnectionPool: HTTP连接池
    - DatabaseConnectionPool: 数据库连接池
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

from httpx import AsyncClient, Limits, Timeout
import aiosqlite

from .backends.base import StorageError


class HTTPConnectionPool:
    """
    HTTP连接池
    
    管理HTTP客户端连接池，提供连接复用和资源管理。
    
    特性：
        - 连接复用
        - 自动超时管理
        - 连接数限制
        - 异步上下文管理器支持
    
    示例：
        >>> pool = HTTPConnectionPool(max_connections=100)
        >>> async with pool.get_client() as client:
        ...     response = await client.get("https://api.example.com")
    """
    
    def __init__(
        self,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        timeout: float = 30.0,
    ) -> None:
        """
        初始化HTTP连接池
        
        参数:
            max_connections: 最大连接数
            max_keepalive_connections: 最大保持连接数
            timeout: 默认超时时间（秒）
        """
        self._max_connections: int = max_connections
        self._max_keepalive_connections: int = max_keepalive_connections
        self._timeout: float = timeout
        self._client: Optional[AsyncClient] = None
        self._lock: asyncio.Lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """
        初始化HTTP客户端
        
        创建共享的HTTP客户端实例。
        
        异常:
            StorageError: 初始化失败时抛出
        """
        async with self._lock:
            if self._client is not None:
                return
            
            try:
                limits = Limits(
                    max_connections=self._max_connections,
                    max_keepalive_connections=self._max_keepalive_connections,
                )
                timeout = Timeout(self._timeout)
                
                self._client = AsyncClient(
                    limits=limits,
                    timeout=timeout,
                )
            except Exception as e:
                raise StorageError(f"HTTP连接池初始化失败: {e}") from e
    
    async def cleanup(self) -> None:
        """
        清理HTTP客户端
        
        关闭所有连接。
        
        异常:
            StorageError: 清理失败时抛出
        """
        async with self._lock:
            if self._client is None:
                return
            
            try:
                await self._client.aclose()
                self._client = None
            except Exception as e:
                raise StorageError(f"HTTP连接池清理失败: {e}") from e
    
    @asynccontextmanager
    async def get_client(self) -> AsyncClient:
        """
        获取HTTP客户端（上下文管理器）
        
        返回:
            AsyncClient实例
        
        异常:
            StorageError: 客户端未初始化时抛出
        
        示例:
            >>> async with pool.get_client() as client:
            ...     response = await client.get(url)
        """
        if self._client is None:
            await self.initialize()
        
        if self._client is None:
            raise StorageError("HTTP客户端未初始化")
        
        yield self._client
    
    @property
    def client(self) -> Optional[AsyncClient]:
        """
        获取HTTP客户端（直接访问）
        
        返回:
            AsyncClient实例，如果未初始化返回None
        
        注意:
            推荐使用get_client()上下文管理器，确保资源正确管理
        """
        return self._client


class DatabaseConnectionPool:
    """
    数据库连接池
    
    管理数据库连接池，提供连接复用和资源管理。
    目前基于SQLite，未来可扩展支持PostgreSQL等。
    
    特性：
        - 连接复用
        - 自动连接管理
        - 异步上下文管理器支持
    
    示例：
        >>> pool = DatabaseConnectionPool(db_path="data/storage.db")
        >>> async with pool.get_connection() as conn:
        ...     await conn.execute("SELECT * FROM table")
    """
    
    def __init__(
        self,
        db_path: str = "data/storage.db",
        pool_size: int = 5,
    ) -> None:
        """
        初始化数据库连接池
        
        参数:
            db_path: 数据库文件路径
            pool_size: 连接池大小（SQLite通常为1，但保留接口用于未来扩展）
        """
        self._db_path: str = db_path
        self._pool_size: int = pool_size
        self._connection: Optional[aiosqlite.Connection] = None
        self._lock: asyncio.Lock = asyncio.Lock()
        self._initialized: bool = False
    
    async def initialize(self) -> None:
        """
        初始化数据库连接池
        
        创建数据库连接。
        
        异常:
            StorageError: 初始化失败时抛出
        """
        async with self._lock:
            if self._initialized:
                return
            
            try:
                self._connection = await aiosqlite.connect(self._db_path)
                self._initialized = True
            except Exception as e:
                raise StorageError(f"数据库连接池初始化失败: {e}") from e
    
    async def cleanup(self) -> None:
        """
        清理数据库连接池
        
        关闭所有连接。
        
        异常:
            StorageError: 清理失败时抛出
        """
        async with self._lock:
            if not self._initialized:
                return
            
            try:
                if self._connection:
                    await self._connection.close()
                    self._connection = None
                self._initialized = False
            except Exception as e:
                raise StorageError(f"数据库连接池清理失败: {e}") from e
    
    @asynccontextmanager
    async def get_connection(self) -> aiosqlite.Connection:
        """
        获取数据库连接（上下文管理器）
        
        返回:
            aiosqlite.Connection实例
        
        异常:
            StorageError: 连接未初始化时抛出
        
        示例:
            >>> async with pool.get_connection() as conn:
            ...     await conn.execute("SELECT * FROM table")
        """
        if not self._initialized:
            await self.initialize()
        
        if self._connection is None:
            raise StorageError("数据库连接未初始化")
        
        yield self._connection
    
    @property
    def connection(self) -> Optional[aiosqlite.Connection]:
        """
        获取数据库连接（直接访问）
        
        返回:
            aiosqlite.Connection实例，如果未初始化返回None
        
        注意:
            推荐使用get_connection()上下文管理器，确保资源正确管理
        """
        return self._connection


class ConnectionPoolManager:
    """
    连接池管理器
    
    统一管理所有类型的连接池（HTTP、数据库等）。
    
    特性：
        - 统一初始化接口
        - 统一清理接口
        - 支持多种连接池类型
    
    示例：
        >>> manager = ConnectionPoolManager(config)
        >>> await manager.initialize()
        >>> async with manager.get_http_client() as client:
        ...     response = await client.get(url)
        >>> await manager.cleanup()
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化连接池管理器
        
        参数:
            config: 配置字典，包含连接池配置
        """
        self._config: Dict[str, Any] = config or {}
        self._http_pool: Optional[HTTPConnectionPool] = None
        self._db_pool: Optional[DatabaseConnectionPool] = None
        self._initialized: bool = False
    
    async def initialize(self) -> None:
        """
        初始化所有连接池
        
        异常:
            StorageError: 初始化失败时抛出
        """
        if self._initialized:
            return
        
        try:
            # 初始化HTTP连接池
            http_config = self._config.get("http", {})
            self._http_pool = HTTPConnectionPool(
                max_connections=http_config.get("max_connections", 100),
                max_keepalive_connections=http_config.get("max_keepalive_connections", 20),
                timeout=http_config.get("timeout", 30.0),
            )
            await self._http_pool.initialize()
            
            # 初始化数据库连接池
            db_config = self._config.get("database", {})
            self._db_pool = DatabaseConnectionPool(
                db_path=db_config.get("db_path", "data/storage.db"),
                pool_size=db_config.get("pool_size", 5),
            )
            await self._db_pool.initialize()
            
            self._initialized = True
        except Exception as e:
            raise StorageError(f"连接池管理器初始化失败: {e}") from e
    
    async def cleanup(self) -> None:
        """
        清理所有连接池
        
        异常:
            StorageError: 清理失败时抛出
        """
        if not self._initialized:
            return
        
        try:
            if self._http_pool:
                await self._http_pool.cleanup()
            if self._db_pool:
                await self._db_pool.cleanup()
            self._initialized = False
        except Exception as e:
            raise StorageError(f"连接池管理器清理失败: {e}") from e
    
    @asynccontextmanager
    async def get_http_client(self) -> AsyncClient:
        """
        获取HTTP客户端（上下文管理器）
        
        返回:
            AsyncClient实例
        
        异常:
            StorageError: 连接池未初始化时抛出
        """
        if not self._initialized or self._http_pool is None:
            raise StorageError("连接池管理器未初始化")
        
        async with self._http_pool.get_client() as client:
            yield client
    
    @asynccontextmanager
    async def get_db_connection(self) -> aiosqlite.Connection:
        """
        获取数据库连接（上下文管理器）
        
        返回:
            aiosqlite.Connection实例
        
        异常:
            StorageError: 连接池未初始化时抛出
        """
        if not self._initialized or self._db_pool is None:
            raise StorageError("连接池管理器未初始化")
        
        async with self._db_pool.get_connection() as conn:
            yield conn
    
    @property
    def http_pool(self) -> Optional[HTTPConnectionPool]:
        """获取HTTP连接池实例"""
        return self._http_pool
    
    @property
    def db_pool(self) -> Optional[DatabaseConnectionPool]:
        """获取数据库连接池实例"""
        return self._db_pool
