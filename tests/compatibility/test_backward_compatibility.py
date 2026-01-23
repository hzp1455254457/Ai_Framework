"""
测试模块：向后兼容性测试
功能描述：测试新架构与旧版本的兼容性
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.llm.service import LLMService
from core.llm.adapters.base import BaseLLMAdapter


class MockAdapter(BaseLLMAdapter):
    """用于兼容性测试的Mock适配器"""
    
    @property
    def name(self) -> str:
        return "mock-adapter"
    
    @property
    def provider(self) -> str:
        return "mock"
    
    async def call(self, messages, model, **kwargs):
        return {
            "content": "Mock response",
            "usage": {"total_tokens": 10},
            "metadata": {},
        }


@pytest.mark.asyncio
@pytest.mark.compatibility
class TestBackwardCompatibility:
    """向后兼容性测试类"""
    
    async def test_old_config_format(self):
        """测试旧配置格式兼容性"""
        # Arrange - 使用旧配置格式（无新架构配置项）
        old_config = {
            "llm": {
                "default_model": "gpt-3.5-turbo",
                "timeout": 30,
                "max_retries": 3,
                # 没有 performance, cost, monitoring 等新配置项
            },
        }
        
        # Act
        service = LLMService(old_config)
        await service.initialize()
        
        # Assert
        assert service.is_initialized is True
        assert service._config["llm"]["default_model"] == "gpt-3.5-turbo"
        
        print("✅ 旧配置格式兼容性测试通过")
    
    async def test_old_api_usage(self):
        """测试旧API使用方式兼容性"""
        # Arrange
        config = {"llm": {"default_model": "gpt-3.5-turbo"}}
        service = LLMService(config)
        await service.initialize()
        
        adapter = MockAdapter()
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act - 使用旧的API调用方式（不传递新参数）
        response = await service.chat(messages)
        
        # Assert
        assert response is not None
        assert response.content == "Mock response"
        assert response.total_tokens == 10
        
        print("✅ 旧API使用方式兼容性测试通过")
    
    async def test_old_adapter_interface(self):
        """测试旧适配器接口兼容性"""
        # Arrange - 创建只实现旧接口的适配器
        class OldStyleAdapter(BaseLLMAdapter):
            @property
            def name(self) -> str:
                return "old-adapter"
            
            @property
            def provider(self) -> str:
                return "old"
            
            async def call(self, messages, model, **kwargs):
                return {
                    "content": "Old style response",
                    "usage": {"total_tokens": 10},
                    "metadata": {},
                }
        
        config = {"llm": {"default_model": "test-model"}}
        service = LLMService(config)
        await service.initialize()
        
        adapter = OldStyleAdapter()
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act
        response = await service.chat(messages)
        
        # Assert
        assert response is not None
        assert response.content == "Old style response"
        
        print("✅ 旧适配器接口兼容性测试通过")
    
    async def test_migration_path(self):
        """测试配置迁移路径"""
        # Arrange - 模拟从v1.0到v2.0的配置迁移
        from infrastructure.config.migrator import ConfigMigrator
        
        v1_config = {
            "llm": {
                "default_model": "gpt-3.5-turbo",
                "timeout": 30,
                # v1.0 没有新架构配置项
            },
        }
        
        # Act - 执行迁移
        migrator = ConfigMigrator()
        migrated_config = migrator.migrate(v1_config)
        
        # Assert
        assert "config_version" in migrated_config
        assert migrated_config["config_version"] == "2.0"
        assert "llm" in migrated_config
        assert "performance" in migrated_config["llm"]
        assert "cost" in migrated_config["llm"]
        assert "monitoring" in migrated_config["llm"]
        
        print("✅ 配置迁移路径测试通过")
    
    async def test_optional_features_disabled(self):
        """测试可选功能禁用时的兼容性"""
        # Arrange - 禁用所有新功能
        config = {
            "llm": {
                "default_model": "gpt-3.5-turbo",
                "enable_routing": False,  # 禁用路由
                "performance": {
                    "enable_connection_pool": False,
                    "enable_cache": False,
                    "enable_deduplication": False,
                },
                "cost": {
                    "enabled": False,  # 禁用成本管理
                },
                "monitoring": {
                    "enabled": False,  # 禁用监控
                },
            },
        }
        
        # Act
        service = LLMService(config)
        await service.initialize()
        
        adapter = MockAdapter()
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = await service.chat(messages)
        
        # Assert
        assert response is not None
        assert service.is_initialized is True
        
        print("✅ 可选功能禁用兼容性测试通过")
    
    async def test_adapter_registration_backward_compatible(self):
        """测试适配器注册向后兼容"""
        # Arrange
        config = {"llm": {"default_model": "test-model"}}
        service = LLMService(config)
        await service.initialize()
        
        # Act - 使用旧的注册方式
        adapter = MockAdapter()
        service.register_adapter(adapter)
        
        # Assert
        assert "mock-adapter" in service._adapters
        assert service._adapters["mock-adapter"] == adapter
        
        print("✅ 适配器注册向后兼容性测试通过")
    
    async def test_response_format_compatibility(self):
        """测试响应格式兼容性"""
        # Arrange
        config = {"llm": {"default_model": "test-model"}}
        service = LLMService(config)
        await service.initialize()
        
        adapter = MockAdapter()
        service.register_adapter(adapter)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act
        response = await service.chat(messages)
        
        # Assert - 验证响应格式与旧版本一致
        assert hasattr(response, "content")
        assert hasattr(response, "model")
        assert hasattr(response, "total_tokens")
        assert hasattr(response, "usage")
        
        # 验证响应内容
        assert response.content == "Mock response"
        assert response.total_tokens == 10
        
        print("✅ 响应格式兼容性测试通过")
    
    async def test_error_handling_compatibility(self):
        """测试错误处理兼容性"""
        # Arrange
        config = {"llm": {"default_model": "test-model"}}
        service = LLMService(config)
        await service.initialize()
        
        # Act & Assert - 测试旧错误场景
        # 空消息列表
        with pytest.raises(ValueError):
            await service.chat([])
        
        # 没有适配器
        from core.llm.service import LLMError
        with pytest.raises(LLMError):
            await service.chat([{"role": "user", "content": "Hello"}])
        
        print("✅ 错误处理兼容性测试通过")
