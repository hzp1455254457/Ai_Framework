"""
模块名称：插件基类模块
功能描述：提供所有插件的基础抽象类，定义统一的插件接口
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - BasePlugin: 插件基类，所有插件的抽象基类
    - PluginError: 插件错误异常

依赖模块：
    - abc: Python标准库，抽象基类
    - typing: Python标准库，类型注解
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class PluginError(Exception):
    """插件错误异常基类"""
    pass


class PluginConfigurationError(PluginError):
    """插件配置错误"""
    pass


class PluginExecutionError(PluginError):
    """插件执行错误"""
    pass


class BasePlugin(ABC):
    """
    插件基类
    
    所有插件的抽象基类，定义统一的插件接口。
    通过继承此类，可以实现各种功能插件，扩展框架能力。
    
    设计目的：
        - 支持功能扩展
        - 统一插件管理
        - 简化插件开发
        - 支持插件热加载
    
    特性：
        - 统一的插件接口
        - 生命周期管理
        - 配置管理
        - 依赖管理
    
    示例：
        >>> class MyPlugin(BasePlugin):
        ...     @property
        ...     def name(self) -> str:
        ...         return "my-plugin"
        ...     
        ...     async def execute(self, context: Dict) -> Dict:
        ...         # 实现插件逻辑
        ...         return {"result": "..."}
    
    属性：
        _config: 插件配置
        _initialized: 是否已初始化标志
        _dependencies: 插件依赖列表
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化插件
        
        参数:
            config: 插件配置字典（可选）
                包含插件的配置参数
        
        异常:
            PluginConfigurationError: 配置错误时抛出
        """
        self._config: Dict[str, Any] = config or {}
        self._initialized: bool = False
        self._dependencies: List[str] = []
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        插件名称
        
        返回:
            插件的唯一标识名称，用于识别和注册插件
        
        示例:
            >>> plugin.name
            "weather-plugin"
        """
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """
        插件版本
        
        返回:
            插件版本号，遵循语义化版本规范（如 "1.0.0"）
        
        示例:
            >>> plugin.version
            "1.0.0"
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        插件描述
        
        返回:
            插件的功能描述，用于文档和用户了解插件用途
        
        示例:
            >>> plugin.description
            "提供天气查询功能的插件"
        """
        pass
    
    @property
    def dependencies(self) -> List[str]:
        """
        插件依赖列表
        
        返回:
            依赖的其他插件名称列表
        
        说明:
            插件管理器会根据此列表确保依赖插件先于当前插件加载
        """
        return self._dependencies.copy()
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化插件
        
        初始化插件所需的所有资源（如连接、缓存等）。
        如果提供了新的配置，会更新插件配置。
        
        参数:
            config: 插件配置字典（可选）
                如果提供，会更新现有配置
        
        异常:
            PluginConfigurationError: 初始化失败时抛出
        
        示例:
            >>> await plugin.initialize({"api_key": "..."})
        """
        if config:
            self._config.update(config)
        
        # 验证配置
        self._validate_config()
        
        # 加载依赖
        await self._load_dependencies()
        
        self._initialized = True
    
    def _validate_config(self) -> None:
        """
        验证配置有效性
        
        子类可以重写此方法实现自定义的配置验证逻辑。
        
        异常:
            PluginConfigurationError: 配置验证失败时抛出
        """
        # 基础验证：子类可以扩展
        pass
    
    async def _load_dependencies(self) -> None:
        """
        加载插件依赖
        
        子类可以重写此方法实现依赖加载逻辑。
        """
        # 默认实现：由插件管理器负责依赖加载
        pass
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行插件逻辑
        
        插件的主要执行方法，实现插件的核心功能。
        
        参数:
            context: 执行上下文，包含：
                - input: 输入数据
                - config: 运行时配置
                - metadata: 元数据信息
        
        返回:
            插件执行结果字典，包含：
                - result: 执行结果
                - metadata: 结果元数据
        
        异常:
            PluginExecutionError: 执行失败时抛出
        
        示例:
            >>> context = {"input": "查询天气", "city": "北京"}
            >>> result = await plugin.execute(context)
            >>> print(result["result"])
        """
        pass
    
    async def cleanup(self) -> None:
        """
        清理插件资源
        
        清理插件占用的所有资源（如关闭连接、清理缓存等）。
        子类应该重写此方法实现具体的清理逻辑。
        
        异常:
            清理过程中的异常会被记录但不抛出，确保清理流程能够完成
        """
        if self._initialized:
            self._initialized = False
    
    @property
    def config(self) -> Dict[str, Any]:
        """
        获取插件配置
        
        返回:
            配置字典的只读副本
        """
        return self._config.copy()
    
    @property
    def is_initialized(self) -> bool:
        """
        检查插件是否已初始化
        
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
