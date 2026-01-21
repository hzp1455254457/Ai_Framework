"""
测试模块：适配器注册表测试
功能描述：测试AdapterRegistry的所有功能
"""

import pytest
from core.llm.adapters.registry import AdapterRegistry
from core.llm.adapters.doubao_adapter import DoubaoAdapter
from core.llm.adapters.qwen_adapter import QwenAdapter
from core.llm.adapters.deepseek_adapter import DeepSeekAdapter


@pytest.mark.asyncio
class TestAdapterRegistry:
    """AdapterRegistry测试类"""
    
    async def test_discover_adapters(self):
        """测试自动发现适配器"""
        # Arrange
        registry = AdapterRegistry()
        
        # Act
        registry.discover_adapters()
        
        # Assert
        assert registry.is_initialized is True
        adapters = registry.get_available_adapters()
        assert "doubao-adapter" in adapters
        assert "qwen-adapter" in adapters
        assert "deepseek-adapter" in adapters
    
    async def test_create_adapter(self):
        """测试创建适配器实例"""
        # Arrange
        registry = AdapterRegistry()
        registry.discover_adapters()
        
        config = {"api_key": "test-key"}
        
        # Act
        adapter = await registry.create_adapter("doubao-adapter", config)
        
        # Assert
        assert adapter is not None
        assert adapter.name == "doubao-adapter"
        assert adapter.provider == "doubao"
    
    async def test_create_nonexistent_adapter(self):
        """测试创建不存在的适配器时抛出异常"""
        # Arrange
        registry = AdapterRegistry()
        registry.discover_adapters()
        
        config = {"api_key": "test-key"}
        
        # Act & Assert
        with pytest.raises(ValueError):
            await registry.create_adapter("nonexistent-adapter", config)
    
    async def test_get_adapter_for_model(self):
        """测试根据模型名称获取适配器"""
        # Arrange
        registry = AdapterRegistry()
        registry.discover_adapters()
        
        # 注册模型映射
        registry.register_model_mapping("qwen-turbo", "qwen-adapter")
        registry.register_model_mapping("deepseek-chat", "deepseek-adapter")
        
        # Act & Assert
        assert registry.get_adapter_for_model("qwen-turbo") == "qwen-adapter"
        assert registry.get_adapter_for_model("deepseek-chat") == "deepseek-adapter"
    
    async def test_get_adapter_for_model_fuzzy_match(self):
        """测试模糊匹配模型名称"""
        # Arrange
        registry = AdapterRegistry()
        registry.discover_adapters()
        
        # Act & Assert
        # 基于模型名称前缀的匹配
        assert registry.get_adapter_for_model("qwen-plus") == "qwen-adapter"
        assert registry.get_adapter_for_model("deepseek-coder") == "deepseek-adapter"
    
    async def test_register_model_mapping(self):
        """测试注册模型映射"""
        # Arrange
        registry = AdapterRegistry()
        registry.discover_adapters()
        
        # Act
        registry.register_model_mapping("custom-model", "qwen-adapter")
        
        # Assert
        assert registry.get_adapter_for_model("custom-model") == "qwen-adapter"
        assert "custom-model" in registry.get_supported_models()
    
    async def test_get_available_adapters(self):
        """测试获取可用适配器列表"""
        # Arrange
        registry = AdapterRegistry()
        registry.discover_adapters()
        
        # Act
        adapters = registry.get_available_adapters()
        
        # Assert
        assert isinstance(adapters, list)
        assert len(adapters) > 0
        assert "doubao-adapter" in adapters
    
    async def test_get_supported_models(self):
        """测试获取支持的模型列表"""
        # Arrange
        registry = AdapterRegistry()
        registry.discover_adapters()
        
        # 注册一些模型映射
        registry.register_model_mapping("model1", "qwen-adapter")
        registry.register_model_mapping("model2", "deepseek-adapter")
        
        # Act
        models = registry.get_supported_models()
        
        # Assert
        assert "model1" in models
        assert "model2" in models
