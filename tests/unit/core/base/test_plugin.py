"""
测试模块：插件基类测试
功能描述：测试BasePlugin的所有功能
"""

import pytest
from typing import Dict, Any
from core.base.plugin import (
    BasePlugin,
    PluginError,
    PluginConfigurationError,
    PluginExecutionError,
)


class ConcretePlugin(BasePlugin):
    """用于测试的具体插件实现"""
    
    @property
    def name(self) -> str:
        return "test-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "测试插件"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """实现插件逻辑"""
        input_data = context.get("input", "")
        return {
            "result": f"处理结果: {input_data}",
            "metadata": {"processed": True}
        }


@pytest.mark.asyncio
class TestBasePlugin:
    """BasePlugin测试类"""
    
    async def test_plugin_initialization(self):
        """测试插件初始化"""
        # Arrange
        config = {"param1": "value1"}
        plugin = ConcretePlugin(config)
        
        # Act
        await plugin.initialize()
        
        # Assert
        assert plugin.is_initialized is True
        assert plugin.name == "test-plugin"
        assert plugin.version == "1.0.0"
        assert plugin.description == "测试插件"
    
    async def test_plugin_execute(self):
        """测试插件执行"""
        # Arrange
        plugin = ConcretePlugin()
        await plugin.initialize()
        context = {"input": "测试数据"}
        
        # Act
        result = await plugin.execute(context)
        
        # Assert
        assert result["result"] == "处理结果: 测试数据"
        assert result["metadata"]["processed"] is True
    
    async def test_plugin_dependencies(self):
        """测试插件依赖"""
        # Arrange
        plugin = ConcretePlugin()
        
        # Act
        dependencies = plugin.dependencies
        
        # Assert
        assert isinstance(dependencies, list)
        # 确保返回的是副本
        dependencies.append("new_dep")
        assert "new_dep" not in plugin.dependencies
    
    async def test_plugin_cleanup(self):
        """测试插件清理"""
        # Arrange
        plugin = ConcretePlugin()
        await plugin.initialize()
        
        # Act
        await plugin.cleanup()
        
        # Assert
        assert plugin.is_initialized is False
    
    async def test_plugin_context_manager(self):
        """测试异步上下文管理器"""
        # Arrange
        config = {"test": True}
        
        # Act
        async with ConcretePlugin(config) as plugin:
            assert plugin.is_initialized is True
            result = await plugin.execute({"input": "test"})
            assert result is not None
        
        # Assert
        assert plugin.is_initialized is False
    
    async def test_plugin_config_access(self):
        """测试配置访问"""
        # Arrange
        config = {"key1": "value1"}
        plugin = ConcretePlugin(config)
        
        # Act
        retrieved_config = plugin.config
        
        # Assert
        assert retrieved_config == config
        # 确保返回的是副本
        retrieved_config["new_key"] = "new_value"
        assert "new_key" not in plugin.config
