"""
模块名称：服务基类模块
功能描述：提供所有服务的基础抽象类，定义统一的服务接口和基础功能
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - BaseService: 服务基类，所有服务的抽象基类

依赖模块：
    - abc: Python标准库，抽象基类
    - typing: Python标准库，类型注解
    - logging: Python标准库，日志管理
"""

from abc import ABC
from typing import Dict, Any, Optional
from logging import Logger, getLogger
import asyncio


class ConfigError(Exception):
    """配置错误异常"""
    pass


class InitializationError(Exception):
    """初始化错误异常"""
    pass


class BaseService(ABC):
    """
    服务基类
    
    所有服务的抽象基类，提供统一的初始化、配置管理和日志管理功能。
    通过继承此类，可以确保所有服务具有一致的接口和行为。
    
    特性：
        - 统一的初始化流程
        - 配置管理
        - 日志管理
        - 生命周期管理（初始化/清理）
    
    示例：
        >>> class MyService(BaseService):
        ...     async def initialize(self) -> None:
        ...         # 自定义初始化逻辑
        ...         pass
        
        >>> service = MyService(config)
        >>> await service.initialize()
    
    属性：
        _config: 服务配置字典
        _logger: 日志记录器实例
        _initialized: 是否已初始化标志
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        初始化服务
        
        参数:
            config: 配置字典，包含服务所需的所有配置
        
        异常:
            ConfigError: 配置错误时抛出（如必需配置缺失）
            ValueError: 配置值无效时抛出
        """
        if not config:
            raise ConfigError("配置不能为空")
        
        self._config: Dict[str, Any] = config
        self._logger: Logger = self._get_logger()
        self._initialized: bool = False
        
        # 验证配置
        self._validate_config()
    
    def _validate_config(self) -> None:
        """
        验证配置有效性
        
        子类可以重写此方法实现自定义的配置验证逻辑。
        
        异常:
            ConfigError: 配置验证失败时抛出
        """
        # 基础验证：检查必需字段
        if not isinstance(self._config, dict):
            raise ConfigError("配置必须是字典类型")
    
    def _get_logger(self) -> Logger:
        """
        获取日志记录器
        
        返回:
            日志记录器实例
        
        说明:
            使用类名作为logger名称，确保日志分类清晰
        """
        logger_name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return getLogger(logger_name)
    
    async def initialize(self) -> None:
        """
        初始化服务资源
        
        异步初始化服务所需的所有资源（如连接池、HTTP客户端、缓存等）。
        子类应该重写此方法实现具体的初始化逻辑。
        
        异常:
            InitializationError: 初始化失败时抛出
        
        示例:
            >>> await service.initialize()
        """
        if self._initialized:
            self._logger.warning("服务已经初始化，跳过重复初始化")
            return
        
        try:
            # 子类可以在这里实现自定义初始化逻辑
            self._initialized = True
            self._logger.info(f"{self.__class__.__name__} 初始化完成")
        except Exception as e:
            self._logger.error(f"服务初始化失败: {e}", exc_info=True)
            raise InitializationError(f"服务初始化失败: {e}") from e
    
    async def cleanup(self) -> None:
        """
        清理服务资源
        
        清理服务占用的所有资源（如关闭连接、清理缓存等）。
        子类应该重写此方法实现具体的清理逻辑。
        
        异常:
            清理过程中的异常会被记录但不抛出，确保清理流程能够完成
        
        示例:
            >>> await service.cleanup()
        """
        if not self._initialized:
            return
        
        try:
            # 子类可以在这里实现自定义清理逻辑
            self._initialized = False
            self._logger.info(f"{self.__class__.__name__} 资源清理完成")
        except Exception as e:
            # 清理失败不应该阻止流程，只记录警告
            self._logger.warning(f"服务清理过程中出现错误: {e}", exc_info=True)
    
    @property
    def config(self) -> Dict[str, Any]:
        """
        获取服务配置
        
        返回:
            配置字典的只读副本，防止意外修改
        
        示例:
            >>> api_key = service.config.get("api_key")
        """
        return self._config.copy()
    
    @property
    def logger(self) -> Logger:
        """
        获取日志记录器
        
        返回:
            日志记录器实例
        
        示例:
            >>> service.logger.info("这是一条日志")
        """
        return self._logger
    
    @property
    def is_initialized(self) -> bool:
        """
        检查服务是否已初始化
        
        返回:
            True表示已初始化，False表示未初始化
        """
        return self._initialized
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup()
        return False
