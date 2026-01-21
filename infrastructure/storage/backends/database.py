"""
模块名称：数据库存储后端模块
功能描述：基于SQLite的数据库存储实现
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - DatabaseStorageBackend: SQLite数据库存储后端
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

import aiosqlite

from .base import BaseStorageBackend, StorageError


class DatabaseStorageBackend(BaseStorageBackend):
    """
    SQLite数据库存储后端
    
    提供基于SQLite的存储实现，支持：
    - 对话历史存储
    - 文件信息存储
    - 元数据存储
    
    特性：
        - 异步SQLite操作（使用aiosqlite）
        - 自动创建数据库和表
        - 支持JSON元数据存储
    
    示例：
        >>> backend = DatabaseStorageBackend(db_path="data/storage.db")
        >>> await backend.initialize()
        >>> await backend.save_conversation("conv1", [{"role": "user", "content": "Hello"}])
    """
    
    def __init__(
        self,
        db_path: str = "data/storage.db",
    ) -> None:
        """
        初始化数据库存储后端
        
        参数:
            db_path: 数据库文件路径
        
        异常:
            StorageError: 路径无效时抛出
        """
        self._db_path: Path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[aiosqlite.Connection] = None
        self._initialized: bool = False
    
    async def initialize(self) -> None:
        """
        初始化数据库
        
        创建数据库连接并初始化表结构。
        
        异常:
            StorageError: 初始化失败时抛出
        """
        if self._initialized:
            return
        
        try:
            self._connection = await aiosqlite.connect(str(self._db_path))
            await self._create_tables()
            self._initialized = True
        except Exception as e:
            raise StorageError(f"数据库初始化失败: {e}") from e
    
    async def _create_tables(self) -> None:
        """创建数据库表"""
        if not self._connection:
            raise StorageError("数据库连接未初始化")
        
        # 对话历史表
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                messages TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 文件信息表
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS files (
                file_id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        await self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_created_at 
            ON conversations(created_at DESC)
        """)
        
        await self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_created_at 
            ON files(created_at DESC)
        """)
        
        await self._connection.commit()
    
    async def cleanup(self) -> None:
        """
        清理数据库连接
        
        关闭数据库连接。
        
        异常:
            StorageError: 清理失败时抛出
        """
        if not self._initialized:
            return
        
        try:
            if self._connection:
                await self._connection.close()
                self._connection = None
            self._initialized = False
        except Exception as e:
            raise StorageError(f"数据库清理失败: {e}") from e
    
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
        if not self._initialized or not self._connection:
            raise StorageError("数据库未初始化")
        
        try:
            messages_json = json.dumps(messages, ensure_ascii=False)
            metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None
            
            await self._connection.execute("""
                INSERT OR REPLACE INTO conversations 
                (conversation_id, messages, metadata, updated_at)
                VALUES (?, ?, ?, ?)
            """, (conversation_id, messages_json, metadata_json, datetime.utcnow()))
            
            await self._connection.commit()
        except Exception as e:
            raise StorageError(f"保存对话失败: {e}") from e
    
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
        if not self._initialized or not self._connection:
            raise StorageError("数据库未初始化")
        
        try:
            async with self._connection.execute(
                "SELECT messages FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                
                messages_json = row[0]
                return json.loads(messages_json)
        except Exception as e:
            raise StorageError(f"获取对话失败: {e}") from e
    
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
        if not self._initialized or not self._connection:
            raise StorageError("数据库未初始化")
        
        try:
            await self._connection.execute(
                "DELETE FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            )
            await self._connection.commit()
        except Exception as e:
            raise StorageError(f"删除对话失败: {e}") from e
    
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
        if not self._initialized or not self._connection:
            raise StorageError("数据库未初始化")
        
        try:
            async with self._connection.execute(
                """
                SELECT conversation_id, metadata, created_at, updated_at
                FROM conversations
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            ) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    conversation_id, metadata_json, created_at, updated_at = row
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    result.append({
                        "conversation_id": conversation_id,
                        "metadata": metadata,
                        "created_at": created_at,
                        "updated_at": updated_at,
                    })
                return result
        except Exception as e:
            raise StorageError(f"列出对话失败: {e}") from e
    
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
        if not self._initialized or not self._connection:
            raise StorageError("数据库未初始化")
        
        try:
            metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None
            
            await self._connection.execute("""
                INSERT OR REPLACE INTO files 
                (file_id, file_path, metadata, updated_at)
                VALUES (?, ?, ?, ?)
            """, (file_id, file_path, metadata_json, datetime.utcnow()))
            
            await self._connection.commit()
        except Exception as e:
            raise StorageError(f"保存文件失败: {e}") from e
    
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
        if not self._initialized or not self._connection:
            raise StorageError("数据库未初始化")
        
        try:
            async with self._connection.execute(
                "SELECT file_path, metadata FROM files WHERE file_id = ?",
                (file_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                
                file_path, metadata_json = row
                metadata = json.loads(metadata_json) if metadata_json else {}
                return {
                    "file_path": file_path,
                    "metadata": metadata,
                }
        except Exception as e:
            raise StorageError(f"获取文件失败: {e}") from e
    
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
        if not self._initialized or not self._connection:
            raise StorageError("数据库未初始化")
        
        try:
            await self._connection.execute(
                "DELETE FROM files WHERE file_id = ?",
                (file_id,)
            )
            await self._connection.commit()
        except Exception as e:
            raise StorageError(f"删除文件失败: {e}") from e
    
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
        if not self._initialized or not self._connection:
            raise StorageError("数据库未初始化")
        
        try:
            async with self._connection.execute(
                """
                SELECT file_id, metadata, created_at, updated_at
                FROM files
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            ) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    file_id, metadata_json, created_at, updated_at = row
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    result.append({
                        "file_id": file_id,
                        "metadata": metadata,
                        "created_at": created_at,
                        "updated_at": updated_at,
                    })
                return result
        except Exception as e:
            raise StorageError(f"列出文件失败: {e}") from e
