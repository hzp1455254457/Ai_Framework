"""
模块名称：配置加载器模块
功能描述：负责从各种源加载配置（YAML文件、JSON文件、环境变量）
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - ConfigLoader: 配置加载器

依赖模块：
    - yaml: YAML文件解析（需要安装PyYAML）
    - python-dotenv: 环境变量管理
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from .encryption import EncryptionService
except ImportError:
    EncryptionService = None


class ConfigLoader:
    """
    配置加载器
    
    负责从各种源加载配置：
    - YAML文件
    - JSON文件
    - 环境变量
    
    示例:
        >>> loader = ConfigLoader()
        >>> config = loader.load_yaml("config/default.yaml")
    """
    
    def load_default(self, config_dir: Path) -> Dict[str, Any]:
        """
        加载默认配置
        
        参数:
            config_dir: 配置目录路径
        
        返回:
            默认配置字典
        
        异常:
            FileNotFoundError: 配置文件不存在时抛出
        """
        default_path = config_dir / "default.yaml"
        if default_path.exists():
            return self.load_yaml(str(default_path))
        return {}
    
    def load_env(self, env: str, config_dir: Path) -> Dict[str, Any]:
        """
        加载环境配置
        
        参数:
            env: 环境名称
            config_dir: 配置目录路径
        
        返回:
            环境配置字典
        """
        env_path = config_dir / f"{env}.yaml"
        if env_path.exists():
            return self.load_yaml(str(env_path))
        return {}
    
    def load_yaml(self, filepath: str) -> Dict[str, Any]:
        """
        加载YAML配置文件
        
        参数:
            filepath: YAML文件路径
        
        返回:
            配置字典
        
        异常:
            FileNotFoundError: 文件不存在时抛出
            ValueError: YAML格式错误时抛出
        """
        if yaml is None:
            raise ImportError("PyYAML未安装，请运行: pip install pyyaml")
        
        path = Path(filepath)
        if not path.exists():
            return {}
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            return config if isinstance(config, dict) else {}
        except yaml.YAMLError as e:
            raise ValueError(f"YAML文件格式错误: {filepath}") from e
    
    def load_json(self, filepath: str) -> Dict[str, Any]:
        """
        加载JSON配置文件
        
        参数:
            filepath: JSON文件路径
        
        返回:
            配置字典
        
        异常:
            FileNotFoundError: 文件不存在时抛出
            ValueError: JSON格式错误时抛出
        """
        path = Path(filepath)
        if not path.exists():
            return {}
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config if isinstance(config, dict) else {}
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON文件格式错误: {filepath}") from e
    
    def load_environment_variables(self, prefix: str = "AI_FRAMEWORK_") -> Dict[str, Any]:
        """
        加载环境变量
        
        将环境变量转换为配置字典。环境变量名使用下划线分隔，
        会被转换为嵌套的配置结构。
        
        例如：AI_FRAMEWORK_LLM_API_KEY -> {"llm": {"api_key": "value"}}
        
        注意：加密配置项（`encrypted:` 前缀）不会被自动解密，
        解密操作由 ConfigManager 在 get() 方法中处理。
        
        参数:
            prefix: 环境变量前缀（可选）
        
        返回:
            配置字典
        """
        # 加载.env文件（如果存在）
        if load_dotenv is not None:
            load_dotenv()
        
        config: Dict[str, Any] = {}
        
        for key, value in os.environ.items():
            if prefix and not key.startswith(prefix):
                continue
            
            # 移除前缀
            if prefix:
                key = key[len(prefix):]
            
            # 转换为小写并分割
            keys = key.lower().split("_")
            
            # 构建嵌套字典
            current = config
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # 设置值（保持加密格式，不解密）
            current[keys[-1]] = value
        
        return config
