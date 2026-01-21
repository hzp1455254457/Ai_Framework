"""
模块名称：存储管理器模块
功能描述：提供统一的存储管理能力，支持多后端存储
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - StorageManager: 存储管理器
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .backends.base import BaseStorageBackend
from .backends.database import DatabaseStorageBackend
from .backends.file_storage import FileStorageBackend


class StorageManager:
    """
    存储管理器
    
    提供统一的存储接口，支持多种存储后端（数据库、文件存储等）。
    
    约定配置（来自 config/*.yaml）：
        storage:
          backend: "database"  # 或 "file"
          database:
            db_path: "data/storage.db"
          file:
            storage_root: "data/storage"
    
    示例：
        >>> manager = StorageManager(config)
        >>> await manager.initialize()
        >>> await manager.save_conversation("conv1", [{"role": "user", "content": "Hello"}])
        >>> conversation = await manager.get_conversation("conv1")
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化存储管理器
        
        参数:
            config: 配置字典，包含存储配置
        """
        self._config: Dict[str, Any] = config or {}
        self._backend: BaseStorageBackend = self._create_backend(self._config)
        self._initialized: bool = False
    
    def _create_backend(self, config: Dict[str, Any]) -> BaseStorageBackend:
        """
        创建存储后端
        
        根据配置选择并创建对应的存储后端。
        
        参数:
            config: 配置字典
        
        返回:
            BaseStorageBackend实例
        
        异常:
            ValueError: 不支持的存储后端类型
        """
        storage_cfg = config.get("storage", {}) if isinstance(config, dict) else {}
        backend = (storage_cfg.get("backend") or "database").lower()
        
        if backend == "database":
            db_cfg = storage_cfg.get("database", {})
            db_path = db_cfg.get("db_path", "data/storage.db")
            return DatabaseStorageBackend(db_path=db_path)
        
        elif backend == "file":
            file_cfg = storage_cfg.get("file", {})
            storage_root = file_cfg.get("storage_root", "data/storage")
            return FileStorageBackend(storage_root=storage_root)
        
        else:
            raise ValueError(f"不支持的存储后端: {backend}")
    
    async def initialize(self) -> None:
        """
        初始化存储管理器
        
        初始化存储后端。
        
        异常:
            StorageError: 初始化失败时抛出
        """
        if self._initialized:
            return
        
        try:
            await self._backend.initialize()
            self._initialized = True
        except Exception as e:
            raise StorageError(f"存储管理器初始化失败: {e}") from e
    
    async def cleanup(self) -> None:
        """
        清理存储管理器
        
        清理存储后端资源。
        
        异常:
            StorageError: 清理失败时抛出
        """
        if not self._initialized:
            return
        
        try:
            await self._backend.cleanup()
            self._initialized = False
        except Exception as e:
            raise StorageError(f"存储管理器清理失败: {e}") from e
    
    # 对话历史相关方法
    
    async def save_conversation(
        self,
        conversation_id: str,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        保存对话历史
        
        参数:
            conversation_id: 对话ID
            messages: 消息列表
            metadata: 元数据（可选）
        
        异常:
            StorageError: 保存失败时抛出
        """
        if not self._initialized:
            await self.initialize()
        
        await self._backend.save_conversation(conversation_id, messages, metadata)
    
    async def get_conversation(
        self,
        conversation_id: str,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        获取对话历史
        
        参数:
            conversation_id: 对话ID
        
        返回:
            消息列表，如果不存在返回None
        
        异常:
            StorageError: 获取失败时抛出
        """
        if not self._initialized:
            await self.initialize()
        
        return await self._backend.get_conversation(conversation_id)
    
    async def delete_conversation(
        self,
        conversation_id: str,
    ) -> None:
        """
        删除对话历史
        
        参数:
            conversation_id: 对话ID
        
        异常:
            StorageError: 删除失败时抛出
        """
        if not self._initialized:
            await self.initialize()
        
        await self._backend.delete_conversation(conversation_id)
    
    async def list_conversations(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        列出对话列表
        
        参数:
            limit: 返回数量限制
            offset: 偏移量
        
        返回:
            对话列表，每个元素包含conversation_id和metadata
        
        异常:
            StorageError: 查询失败时抛出
        """
        if not self._initialized:
            await self.initialize()
        
        return await self._backend.list_conversations(limit=limit, offset=offset)
    
    # 文件存储相关方法
    
    async def save_file(
        self,
        file_id: str,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        保存文件信息
        
        参数:
            file_id: 文件ID
            file_path: 文件路径
            metadata: 元数据（可选）
        
        异常:
            StorageError: 保存失败时抛出
        """
        if not self._initialized:
            await self.initialize()
        
        await self._backend.save_file(file_id, file_path, metadata)
    
    async def get_file(
        self,
        file_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        参数:
            file_id: 文件ID
        
        返回:
            文件信息字典，包含file_path和metadata，如果不存在返回None
        
        异常:
            StorageError: 获取失败时抛出
        """
        if not self._initialized:
            await self.initialize()
        
        return await self._backend.get_file(file_id)
    
    async def delete_file(
        self,
        file_id: str,
    ) -> None:
        """
        删除文件信息
        
        参数:
            file_id: 文件ID
        
        异常:
            StorageError: 删除失败时抛出
        """
        if not self._initialized:
            await self.initialize()
        
        await self._backend.delete_file(file_id)
    
    async def list_files(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        列出文件列表
        
        参数:
            limit: 返回数量限制
            offset: 偏移量
        
        返回:
            文件列表，每个元素包含file_id和metadata
        
        异常:
            StorageError: 查询失败时抛出
        """
        if not self._initialized:
            await self.initialize()
        
        return await self._backend.list_files(limit=limit, offset=offset)
    
    @property
    def backend(self) -> BaseStorageBackend:
        """
        获取当前存储后端实例
        
        返回:
            BaseStorageBackend实例
        """
        return self._backend
