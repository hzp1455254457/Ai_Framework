"""
测试模块：配置管理器测试
功能描述：测试ConfigManager的所有功能
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from infrastructure.config import ConfigManager, ConfigError


@pytest.fixture
def temp_config_dir():
    """创建临时配置目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        
        # 创建默认配置
        default_config = {
            "llm": {
                "api_key": "",
                "timeout": 30,
                "max_retries": 3
            },
            "cache": {
                "backend": "memory",
                "ttl": 3600
            }
        }
        with open(config_dir / "default.yaml", "w", encoding="utf-8") as f:
            yaml.dump(default_config, f)
        
        # 创建开发环境配置
        dev_config = {
            "llm": {
                "api_key": "dev-key",
                "timeout": 10
            }
        }
        with open(config_dir / "dev.yaml", "w", encoding="utf-8") as f:
            yaml.dump(dev_config, f)
        
        yield config_dir


@pytest.mark.asyncio
class TestConfigManager:
    """ConfigManager测试类"""
    
    async def test_load_default_config(self, temp_config_dir):
        """测试加载默认配置"""
        # Act
        config = ConfigManager.load(env="dev", config_dir=str(temp_config_dir))
        
        # Assert
        assert config.get("llm.timeout") == 10  # 环境配置覆盖默认配置
        assert config.get("cache.backend") == "memory"  # 默认配置
    
    async def test_get_nested_config(self, temp_config_dir):
        """测试获取嵌套配置"""
        # Arrange
        config = ConfigManager.load(env="dev", config_dir=str(temp_config_dir))
        
        # Act & Assert
        assert config.get("llm.api_key") == "dev-key"
        assert config.get("llm.timeout") == 10
        assert config.get("llm.max_retries") == 3  # 来自默认配置
    
    async def test_get_with_default_value(self, temp_config_dir):
        """测试使用默认值"""
        # Arrange
        config = ConfigManager.load(env="dev", config_dir=str(temp_config_dir))
        
        # Act & Assert
        assert config.get("nonexistent.key", "default") == "default"
        assert config.get("llm.nonexistent", 100) == 100
    
    async def test_set_config(self, temp_config_dir):
        """测试设置配置值"""
        # Arrange
        config = ConfigManager.load(env="dev", config_dir=str(temp_config_dir))
        
        # Act
        config.set("llm.timeout", 60)
        
        # Assert
        assert config.get("llm.timeout") == 60
    
    async def test_reload_config(self, temp_config_dir):
        """测试重新加载配置"""
        # Arrange
        config = ConfigManager.load(env="dev", config_dir=str(temp_config_dir))
        original_timeout = config.get("llm.timeout")
        
        # 修改配置文件
        dev_config_path = temp_config_dir / "dev.yaml"
        new_config = {"llm": {"timeout": 99}}
        with open(dev_config_path, "w", encoding="utf-8") as f:
            yaml.dump(new_config, f)
        
        # Act
        await config.reload()
        
        # Assert
        assert config.get("llm.timeout") == 99
    
    async def test_config_access(self, temp_config_dir):
        """测试配置访问"""
        # Arrange
        config = ConfigManager.load(env="dev", config_dir=str(temp_config_dir))
        
        # Act
        full_config = config.config
        
        # Assert
        assert isinstance(full_config, dict)
        assert "llm" in full_config
        # 确保返回的是副本
        full_config["new_key"] = "new_value"
        assert "new_key" not in config.config
    
    async def test_env_property(self, temp_config_dir):
        """测试环境属性"""
        # Arrange
        config = ConfigManager.load(env="prod", config_dir=str(temp_config_dir))
        
        # Assert
        assert config.env == "prod"
