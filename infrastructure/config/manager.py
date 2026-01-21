"""
模块名称：配置管理器模块
功能描述：提供统一的配置管理能力，支持多环境配置、配置热重载
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - ConfigManager: 配置管理器主类

依赖模块：
    - .loader: 配置加载器
    - .validator: 配置验证器
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from .loader import ConfigLoader
from .validator import ConfigValidator, ConfigError, ConfigValidationError


class ConfigManager:
    """
    配置管理器
    
    提供统一的配置管理能力，支持：
    - 多环境配置（dev/prod）
    - 配置热重载
    - 嵌套配置访问（点号分隔）
    - 环境变量覆盖
    
    特性：
        - 支持YAML配置文件
        - 支持环境变量覆盖
        - 支持配置热重载
        - 配置验证
    
    示例：
        >>> config = ConfigManager.load(env="dev")
        >>> api_key = config.get("llm.api_key")
        >>> config.set("llm.timeout", 60)
    
    属性：
        _config: 配置字典
        _env: 当前环境
        _config_dir: 配置目录路径
        _loader: 配置加载器
        _validator: 配置验证器
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        env: str = "dev",
        config_dir: Optional[str] = None,
    ) -> None:
        """
        初始化配置管理器
        
        参数:
            config: 配置字典
            env: 环境名称
            config_dir: 配置目录路径
        
        异常:
            ConfigError: 配置错误时抛出
        """
        self._config: Dict[str, Any] = config
        self._env: str = env
        self._config_dir: Path = Path(config_dir) if config_dir else Path("config")
        self._loader: ConfigLoader = ConfigLoader()
        self._validator: ConfigValidator = ConfigValidator()
    
    @classmethod
    def load(
        cls,
        env: str = "dev",
        config_dir: Optional[str] = None,
    ) -> "ConfigManager":
        """
        加载配置
        
        加载顺序：
        1. 默认配置（default.yaml）
        2. 环境配置（{env}.yaml）
        3. 环境变量（覆盖配置）
        
        参数:
            env: 环境名称（dev/prod/test）
            config_dir: 配置目录路径（可选，默认"config"）
        
        返回:
            ConfigManager实例
        
        异常:
            ConfigError: 配置加载失败时抛出
        
        示例:
            >>> config = ConfigManager.load(env="dev")
        """
        loader = ConfigLoader()
        config_dir_path = Path(config_dir) if config_dir else Path("config")
        
        # 加载默认配置
        default_config = loader.load_default(config_dir_path)
        
        # 加载环境配置
        env_config = loader.load_env(env, config_dir_path)
        
        # 合并配置（环境配置覆盖默认配置）
        merged_config = cls._merge_config(default_config, env_config)
        
        # 加载环境变量（覆盖配置）
        env_overrides = loader.load_environment_variables()
        merged_config = cls._merge_config(merged_config, env_overrides)
        
        # 创建配置管理器实例
        manager = cls(merged_config, env, str(config_dir_path))
        
        # 验证配置
        try:
            manager.validate()
        except ConfigValidationError as e:
            raise ConfigError(f"配置验证失败: {e}") from e
        
        return manager
    
    @staticmethod
    def _merge_config(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并配置字典
        
        深度合并两个配置字典，override中的值会覆盖base中的值。
        
        参数:
            base: 基础配置
            override: 覆盖配置
        
        返回:
            合并后的配置字典
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        支持点号分隔的嵌套键访问（如 "llm.api_key"）。
        
        参数:
            key: 配置键，支持点号分隔（如 "llm.api_key"）
            default: 默认值（如果键不存在）
        
        返回:
            配置值，如果键不存在返回default
        
        示例:
            >>> api_key = config.get("llm.api_key")
            >>> timeout = config.get("llm.timeout", 30)
        """
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        支持点号分隔的嵌套键设置。
        
        参数:
            key: 配置键，支持点号分隔
            value: 配置值
        
        示例:
            >>> config.set("llm.timeout", 60)
        """
        keys = key.split(".")
        config = self._config
        
        # 创建嵌套字典结构
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            elif not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    async def reload(self) -> None:
        """
        重新加载配置（热重载）
        
        从配置文件重新加载配置，更新当前配置。
        
        异常:
            ConfigError: 重新加载失败时抛出
        
        示例:
            >>> await config.reload()
        """
        try:
            # 重新加载配置
            new_config = ConfigManager.load(self._env, str(self._config_dir))
            self._config = new_config._config
        except Exception as e:
            raise ConfigError(f"配置重新加载失败: {e}") from e
    
    def validate(self) -> bool:
        """
        验证配置有效性
        
        返回:
            True表示配置有效
        
        异常:
            ConfigValidationError: 配置验证失败时抛出
        
        示例:
            >>> config.validate()
        """
        return self._validator.validate(self._config)
    
    @property
    def config(self) -> Dict[str, Any]:
        """
        获取完整配置字典
        
        返回:
            配置字典的只读副本
        """
        return self._config.copy()
    
    @property
    def env(self) -> str:
        """获取当前环境名称"""
        return self._env
