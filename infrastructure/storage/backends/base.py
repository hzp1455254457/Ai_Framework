"""
模块名称：存储后端基类模块
功能描述：定义存储后端的统一接口
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - BaseStorageBackend: 存储后端基类
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class StorageError(Exception):
    """存储模块异常基类"""
    pass


class BaseStorageBackend(ABC):
    """
    存储后端基类
    
    所有存储后端均应实现此接口，提供统一的存储能力。
    
    说明：
        - 所有方法均为异步接口（便于统一IO模型）
        - 支持对话历史存储
        - 支持文件存储
        - 支持元数据存储
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        初始化存储后端
        
        执行必要的初始化操作，如创建数据库表、创建目录等。
        
        异常:
            StorageError: 初始化失败时抛出
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """
        清理存储后端资源
        
        关闭连接、清理资源等。
        
        异常:
            StorageError: 清理失败时抛出
        """
        pass
    
    # 对话历史相关方法
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    # 文件存储相关方法
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
