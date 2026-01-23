"""
模块名称：配置验证器模块
功能描述：验证配置的有效性和完整性
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - ConfigValidator: 配置验证器
    - ConfigError: 配置错误异常
    - ConfigValidationError: 配置验证错误异常

依赖模块：
    - typing: 类型注解
"""

from typing import Dict, Any, List, Optional


class ConfigError(Exception):
    """配置错误异常基类"""
    pass


class ConfigValidationError(ConfigError):
    """配置验证错误异常"""
    pass


class ConfigValidator:
    """
    配置验证器
    
    验证配置的有效性和完整性。
    
    示例:
        >>> validator = ConfigValidator()
        >>> validator.validate(config)
    """
    
    def __init__(self, required_keys: Optional[List[str]] = None) -> None:
        """
        初始化配置验证器
        
        参数:
            required_keys: 必需配置键列表（可选）
        """
        self._required_keys: List[str] = required_keys or []
    
    def validate(self, config: Dict[str, Any]) -> bool:
        """
        验证配置有效性
        
        检查：
        1. 配置是否为字典类型
        2. 必需键是否存在
        3. 配置值类型是否正确（可选）
        4. 加密配置格式是否正确（如果存在）
        
        参数:
            config: 配置字典
        
        返回:
            True表示配置有效
        
        异常:
            ConfigValidationError: 配置验证失败时抛出
        """
        if not isinstance(config, dict):
            raise ConfigValidationError("配置必须是字典类型")
        
        # 检查必需键
        for key in self._required_keys:
            if key not in config:
                raise ConfigValidationError(f"缺少必需配置项: {key}")
        
        # 验证加密配置格式（递归检查）
        self._validate_encryption_format(config)
        
        return True
    
    def _validate_encryption_format(self, config: Dict[str, Any], path: str = "") -> None:
        """
        验证加密配置格式
        
        递归检查配置中的加密值格式是否正确。
        
        参数:
            config: 配置字典
            path: 当前配置路径（用于错误提示）
        
        异常:
            ConfigValidationError: 加密格式错误时抛出
        """
        for key, value in config.items():
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(value, dict):
                # 递归检查嵌套字典
                self._validate_encryption_format(value, current_path)
            elif isinstance(value, str) and value.startswith("encrypted:"):
                # 验证加密格式
                encrypted_value = value[10:]  # 移除 "encrypted:" 前缀
                parts = encrypted_value.split(":")
                if len(parts) != 4:
                    raise ConfigValidationError(
                        f"配置项 {current_path} 的加密格式错误，应为 'salt:iv:ciphertext:tag'"
                    )
    
    def add_required_key(self, key: str) -> None:
        """
        添加必需配置键
        
        参数:
            key: 配置键
        """
        if key not in self._required_keys:
            self._required_keys.append(key)
    
    def remove_required_key(self, key: str) -> None:
        """
        移除必需配置键
        
        参数:
            key: 配置键
        """
        if key in self._required_keys:
            self._required_keys.remove(key)
