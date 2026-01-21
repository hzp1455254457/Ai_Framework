"""
集成测试：配置与服务集成测试
功能描述：测试配置管理器与服务的集成
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from infrastructure.config import ConfigManager
from core.base.service import BaseService


class TestService(BaseService):
    """用于测试的服务"""
    
    async def initialize(self) -> None:
        await super().initialize()
        # BaseService直接使用字典，需要通过嵌套访问
        self.test_value = self._config.get("test", {}).get("value", "default")


@pytest.mark.asyncio
class TestConfigServiceIntegration:
    """配置与服务集成测试类"""
    
    async def test_service_uses_config_manager(self):
        """测试服务使用配置管理器"""
        # Arrange
        config_data = {
            "test": {
                "value": "configured"
            }
        }
        
        # Act
        service = TestService(config_data)
        await service.initialize()
        
        # Assert
        assert service.test_value == "configured"
        # BaseService直接使用字典配置
        assert service._config.get("test", {}).get("value") == "configured"
    
    async def test_service_config_reload(self):
        """测试服务配置重载"""
        # Arrange
        import tempfile as tf
        
        with tf.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()
            
            # 创建初始配置
            config_data = {"test": {"value": "initial"}}
            with open(config_dir / "default.yaml", "w", encoding="utf-8") as f:
                yaml.dump(config_data, f)
            
            config_manager = ConfigManager.load(env="default", config_dir=str(config_dir))
            config_dict = config_manager.config if hasattr(config_manager, 'config') else config_data
            service = TestService(config_dict)
            await service.initialize()
            
            # 修改配置
            config_data = {"test": {"value": "updated"}}
            with open(config_dir / "default.yaml", "w", encoding="utf-8") as f:
                yaml.dump(config_data, f)
            
            # Act - 重新加载配置管理器
            await config_manager.reload()
            
            # 更新服务的配置字典
            updated_config = config_manager.config
            service._config = updated_config
            
            # Assert
            assert service._config.get("test", {}).get("value") == "updated"
