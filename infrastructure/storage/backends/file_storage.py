"""
模块名称：文件存储后端模块
功能描述：基于文件系统的存储实现
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - FileStorageBackend: 文件存储后端
"""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

import aiofiles
import aiofiles.os

from .base import BaseStorageBackend, StorageError


class FileStorageBackend(BaseStorageBackend):
    """
    文件存储后端
    
    提供基于文件系统的存储实现，支持：
    - 对话历史存储（JSON文件）
    - 文件信息存储（元数据JSON文件）
    - 实际文件存储
    
    特性：
        - 异步文件操作（使用aiofiles）
        - 自动创建目录结构
        - 支持JSON元数据存储
    
    目录结构：
        storage_root/
        ├── conversations/
        │   └── {conversation_id}.json
        ├── files/
        │   ├── {file_id}.json  # 元数据
        │   └── {file_id}       # 实际文件
        └── metadata/
    
    示例：
        >>> backend = FileStorageBackend(storage_root="data/storage")
        >>> await backend.initialize()
        >>> await backend.save_conversation("conv1", [{"role": "user", "content": "Hello"}])
    """
    
    def __init__(
        self,
        storage_root: str = "data/storage",
    ) -> None:
        """
        初始化文件存储后端
        
        参数:
            storage_root: 存储根目录路径
        
        异常:
            StorageError: 路径无效时抛出
        """
        self._storage_root: Path = Path(storage_root)
        self._conversations_dir: Path = self._storage_root / "conversations"
        self._files_dir: Path = self._storage_root / "files"
        self._metadata_dir: Path = self._storage_root / "metadata"
        self._initialized: bool = False
    
    async def initialize(self) -> None:
        """
        初始化文件存储
        
        创建必要的目录结构。
        
        异常:
            StorageError: 初始化失败时抛出
        """
        if self._initialized:
            return
        
        try:
            # 创建目录结构
            await aiofiles.os.makedirs(self._conversations_dir, exist_ok=True)
            await aiofiles.os.makedirs(self._files_dir, exist_ok=True)
            await aiofiles.os.makedirs(self._metadata_dir, exist_ok=True)
            self._initialized = True
        except Exception as e:
            raise StorageError(f"文件存储初始化失败: {e}") from e
    
    async def cleanup(self) -> None:
        """
        清理文件存储资源
        
        目前无需特殊清理操作。
        
        异常:
            StorageError: 清理失败时抛出
        """
        if not self._initialized:
            return
        
        try:
            self._initialized = False
        except Exception as e:
            raise StorageError(f"文件存储清理失败: {e}") from e
    
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
            raise StorageError("文件存储未初始化")
        
        try:
            file_path = self._conversations_dir / f"{conversation_id}.json"
            data = {
                "conversation_id": conversation_id,
                "messages": messages,
                "metadata": metadata or {},
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
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
        if not self._initialized:
            raise StorageError("文件存储未初始化")
        
        try:
            file_path = self._conversations_dir / f"{conversation_id}.json"
            
            if not await aiofiles.os.path.exists(file_path):
                return None
            
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                data = json.loads(content)
                return data.get("messages")
        except FileNotFoundError:
            return None
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
        if not self._initialized:
            raise StorageError("文件存储未初始化")
        
        try:
            file_path = self._conversations_dir / f"{conversation_id}.json"
            if await aiofiles.os.path.exists(file_path):
                await aiofiles.os.remove(file_path)
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
        if not self._initialized:
            raise StorageError("文件存储未初始化")
        
        try:
            conversations = []
            
            # 获取所有对话文件
            if await aiofiles.os.path.exists(self._conversations_dir):
                # 使用标准库os.scandir（aiofiles没有scandir）
                import os
                for entry in os.scandir(self._conversations_dir):
                    if entry.is_file() and entry.name.endswith(".json"):
                        conversation_id = entry.name[:-5]  # 移除.json后缀
                        
                        try:
                            async with aiofiles.open(entry.path, "r", encoding="utf-8") as f:
                                content = await f.read()
                                data = json.loads(content)
                                conversations.append({
                                    "conversation_id": conversation_id,
                                    "metadata": data.get("metadata", {}),
                                    "created_at": data.get("created_at"),
                                    "updated_at": data.get("updated_at"),
                                })
                        except Exception:
                            # 跳过损坏的文件
                            continue
            
            # 按更新时间排序（降序）
            conversations.sort(
                key=lambda x: x.get("updated_at") or "",
                reverse=True
            )
            
            # 分页
            return conversations[offset:offset + limit]
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
            file_path: 文件路径（源文件路径，会被复制到存储目录）
            metadata: 元数据（可选）
        
        异常:
            StorageError: 保存失败时抛出
        """
        if not self._initialized:
            raise StorageError("文件存储未初始化")
        
        try:
            # 保存元数据
            metadata_path = self._files_dir / f"{file_id}.json"
            metadata_data = {
                "file_id": file_id,
                "file_path": file_path,
                "metadata": metadata or {},
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            async with aiofiles.open(metadata_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(metadata_data, ensure_ascii=False, indent=2))
            
            # 如果源文件存在，复制到存储目录
            source_path = Path(file_path)
            if await aiofiles.os.path.exists(source_path):
                dest_path = self._files_dir / file_id
                # 使用shutil.copy2保持元数据
                shutil.copy2(source_path, dest_path)
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
        if not self._initialized:
            raise StorageError("文件存储未初始化")
        
        try:
            metadata_path = self._files_dir / f"{file_id}.json"
            
            if not await aiofiles.os.path.exists(metadata_path):
                return None
            
            async with aiofiles.open(metadata_path, "r", encoding="utf-8") as f:
                content = await f.read()
                data = json.loads(content)
                return {
                    "file_path": data.get("file_path"),
                    "metadata": data.get("metadata", {}),
                }
        except FileNotFoundError:
            return None
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
        if not self._initialized:
            raise StorageError("文件存储未初始化")
        
        try:
            # 删除元数据文件
            metadata_path = self._files_dir / f"{file_id}.json"
            if await aiofiles.os.path.exists(metadata_path):
                await aiofiles.os.remove(metadata_path)
            
            # 删除实际文件
            file_path = self._files_dir / file_id
            if await aiofiles.os.path.exists(file_path):
                await aiofiles.os.remove(file_path)
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
        if not self._initialized:
            raise StorageError("文件存储未初始化")
        
        try:
            files = []
            
            # 获取所有文件元数据
            if await aiofiles.os.path.exists(self._files_dir):
                # 使用标准库os.scandir（aiofiles没有scandir）
                import os
                for entry in os.scandir(self._files_dir):
                    if entry.is_file() and entry.name.endswith(".json"):
                        file_id = entry.name[:-5]  # 移除.json后缀
                        
                        try:
                            async with aiofiles.open(entry.path, "r", encoding="utf-8") as f:
                                content = await f.read()
                                data = json.loads(content)
                                files.append({
                                    "file_id": file_id,
                                    "metadata": data.get("metadata", {}),
                                    "created_at": data.get("created_at"),
                                    "updated_at": data.get("updated_at"),
                                })
                        except Exception:
                            # 跳过损坏的文件
                            continue
            
            # 按更新时间排序（降序）
            files.sort(
                key=lambda x: x.get("updated_at") or "",
                reverse=True
            )
            
            # 分页
            return files[offset:offset + limit]
        except Exception as e:
            raise StorageError(f"列出文件失败: {e}") from e
