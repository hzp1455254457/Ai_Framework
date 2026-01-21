"""
测试模块：服务基类测试
功能描述：测试BaseService的所有功能
"""

"""
测试模块：服务基类测试
功能描述：测试BaseService的所有功能
"""

import pytest
from typing import Dict, Any
from core.base.service import BaseService, ConfigError, InitializationError


class ConcreteService(BaseService):
    """用于测试的具体服务实现"""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self.custom_initialized = False
        self.custom_cleaned = False
    
    async def initialize(self) -> None:
        """自定义初始化"""
        await super().initialize()
        self.custom_initialized = True
    
    async def cleanup(self) -> None:
        """自定义清理"""
        await super().cleanup()
        self.custom_cleaned = True


@pytest.mark.asyncio
class TestBaseService:
    """BaseService测试类"""
    
    async def test_service_initialization_success(self):
        """测试服务初始化成功场景"""
        # Arrange
        config = {"api_key": "test-key", "timeout": 30}
        
        # Act
        service = ConcreteService(config)
        await service.initialize()
        
        # Assert
        assert service.is_initialized is True
        assert service.custom_initialized is True
        assert service.config["api_key"] == "test-key"
    
    async def test_service_initialization_with_empty_config(self):
        """测试空配置时抛出异常"""
        # Act & Assert
        with pytest.raises(ConfigError):
            ConcreteService({})
    
    async def test_service_config_access(self):
        """测试配置访问"""
        # Arrange
        config = {"key1": "value1", "key2": "value2"}
        service = ConcreteService(config)
        
        # Act
        retrieved_config = service.config
        
        # Assert
        assert retrieved_config == config
        # 确保返回的是副本，修改不影响原配置
        retrieved_config["new_key"] = "new_value"
        assert "new_key" not in service.config
    
    async def test_service_logger_access(self):
        """测试日志记录器访问"""
        # Arrange
        config = {"test": True}
        service = ConcreteService(config)
        
        # Act
        logger = service.logger
        
        # Assert
        assert logger is not None
        # 日志记录器名称应该是类名
        assert "ConcreteService" in logger.name
    
    async def test_service_cleanup(self):
        """测试服务清理"""
        # Arrange
        config = {"test": True}
        service = ConcreteService(config)
        await service.initialize()
        
        # Act
        await service.cleanup()
        
        # Assert
        assert service.is_initialized is False
        assert service.custom_cleaned is True
    
    async def test_service_context_manager(self):
        """测试异步上下文管理器"""
        # Arrange
        config = {"test": True}
        
        # Act
        async with ConcreteService(config) as service:
            assert service.is_initialized is True
        
        # Assert (退出上下文后自动清理)
        assert service.is_initialized is False
    
    async def test_service_double_initialization(self):
        """测试重复初始化"""
        # Arrange
        config = {"test": True}
        service = ConcreteService(config)
        await service.initialize()
        
        # Act - 第二次初始化应该被忽略并记录警告
        await service.initialize()
        
        # Assert
        assert service.is_initialized is True
