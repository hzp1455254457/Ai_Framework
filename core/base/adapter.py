"""
模块名称：适配器基类模块
功能描述：提供所有适配器的基础抽象类，定义统一的适配器接口
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - BaseAdapter: 适配器基类，所有适配器的抽象基类
    - AdapterError: 适配器错误异常

依赖模块：
    - abc: Python标准库，抽象基类
    - typing: Python标准库，类型注解
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncIterator


class AdapterError(Exception):
    """适配器错误异常基类"""
    pass


class AdapterConfigurationError(AdapterError):
    """适配器配置错误"""
    pass


class AdapterCallError(AdapterError):
    """适配器调用错误"""
    pass


class BaseAdapter(ABC):
    """
    适配器基类
    
    所有适配器的抽象基类，定义统一的适配器接口。
    通过继承此类，可以实现对不同服务提供商的统一调用接口。
    
    设计目的：
        - 统一多服务提供商的接口
        - 简化服务调用的复杂性
        - 支持灵活的适配器实现
        - 便于添加新的服务提供商
    
    特性：
        - 统一的调用接口
        - 流式调用支持
        - 配置管理
        - 生命周期管理
    
    示例：
        >>> class MyAdapter(BaseAdapter):
        ...     @property
        ...     def name(self) -> str:
        ...         return "my-adapter"
        ...     
        ...     async def call(self, *args, **kwargs) -> Dict[str, Any]:
        ...         # 实现调用逻辑
        ...         return {"result": "..."}
    
    属性：
        _config: 适配器配置
        _initialized: 是否已初始化标志
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化适配器
        
        参数:
            config: 适配器配置字典（可选）
                包含API密钥、端点URL等配置信息
        
        异常:
            AdapterConfigurationError: 配置错误时抛出
        """
        self._config: Dict[str, Any] = config or {}
        self._initialized: bool = False
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        适配器名称
        
        返回:
            适配器的唯一标识名称，用于识别和注册适配器
        
        示例:
            >>> adapter.name
            "openai-adapter"
        """
        pass
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """
        服务提供商名称
        
        返回:
            服务提供商的名称（如 "openai", "claude", "ollama"）
        
        示例:
            >>> adapter.provider
            "openai"
        """
        pass
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化适配器
        
        初始化适配器所需的所有资源（如HTTP客户端、连接池等）。
        如果提供了新的配置，会更新适配器配置。
        
        参数:
            config: 适配器配置字典（可选）
                如果提供，会更新现有配置
        
        异常:
            AdapterConfigurationError: 初始化失败时抛出
        
        示例:
            >>> await adapter.initialize({"api_key": "sk-..."})
        """
        if config:
            self._config.update(config)
        
        # 验证配置
        self._validate_config()
        
        self._initialized = True
    
    def _validate_config(self) -> None:
        """
        验证配置有效性
        
        子类可以重写此方法实现自定义的配置验证逻辑。
        
        异常:
            AdapterConfigurationError: 配置验证失败时抛出
        """
        # 基础验证：子类可以扩展
        pass
    
    @abstractmethod
    async def call(self, *args, **kwargs) -> Dict[str, Any]:
        """
        调用服务接口
        
        统一的服务调用接口，各适配器实现具体的调用逻辑。
        将统一的接口转换为提供商特定的API调用。
        
        参数:
            *args: 位置参数，适配器特定的参数
            **kwargs: 关键字参数，适配器特定的参数
        
        返回:
            服务响应的标准格式字典，包含：
                - content: 响应内容
                - metadata: 元数据（如token使用量、成本等）
        
        异常:
            AdapterCallError: 调用失败时抛出
        
        示例:
            >>> response = await adapter.call(messages=[...])
            >>> print(response["content"])
        """
        pass
    
    async def stream_call(self, *args, **kwargs) -> AsyncIterator[Dict[str, Any]]:
        """
        流式调用接口
        
        支持流式响应的服务调用，返回异步生成器。
        对于不支持流式调用的适配器，可以重写此方法提供模拟实现。
        
        参数:
            *args: 位置参数，适配器特定的参数
            **kwargs: 关键字参数，适配器特定的参数
        
        生成器:
            逐个返回响应块，每个块为字典格式
        
        异常:
            AdapterCallError: 调用失败时抛出
        
        示例:
            >>> async for chunk in adapter.stream_call(messages=[...]):
            ...     print(chunk["content"])
        """
        # 默认实现：调用非流式接口并包装为流式响应
        response = await self.call(*args, **kwargs)
        yield response
    
    async def cleanup(self) -> None:
        """
        清理适配器资源
        
        清理适配器占用的所有资源（如关闭HTTP连接、清理缓存等）。
        子类应该重写此方法实现具体的清理逻辑。
        
        异常:
            清理过程中的异常会被记录但不抛出，确保清理流程能够完成
        """
        if self._initialized:
            self._initialized = False
    
    @property
    def config(self) -> Dict[str, Any]:
        """
        获取适配器配置
        
        返回:
            配置字典的只读副本
        """
        return self._config.copy()
    
    @property
    def is_initialized(self) -> bool:
        """
        检查适配器是否已初始化
        
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
