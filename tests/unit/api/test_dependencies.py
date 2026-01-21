"""
测试模块：API依赖注入测试
功能描述：测试API依赖注入功能
"""

import pytest
from unittest.mock import MagicMock, patch
from api.dependencies import get_config_manager, get_llm_service
from infrastructure.config.manager import ConfigManager
from core.llm.service import LLMService


class TestDependencies:
    """依赖注入测试类"""
    
    def test_get_config_manager(self):
        """测试获取配置管理器"""
        with patch("api.dependencies.ConfigManager") as mock_config_manager:
            mock_instance = MagicMock()
            mock_config_manager.load.return_value = mock_instance
            
            # 清除缓存
            import api.dependencies
            api.dependencies._service_cache.clear()
            
            result = get_config_manager()
            
            assert result is not None
            mock_config_manager.load.assert_called_once()
    
    def test_get_config_manager_cached(self):
        """测试配置管理器缓存"""
        with patch("api.dependencies.ConfigManager") as mock_config_manager:
            mock_instance = MagicMock()
            mock_config_manager.load.return_value = mock_instance
            
            # 清除缓存
            import api.dependencies
            api.dependencies._service_cache.clear()
            
            result1 = get_config_manager()
            result2 = get_config_manager()
            
            # 应该返回同一个实例
            assert result1 is result2
            # 应该只加载一次
            assert mock_config_manager.load.call_count == 1
    
    @pytest.mark.asyncio
    async def test_get_llm_service(self):
        """测试获取LLM服务"""
        with patch("api.dependencies.LLMService") as mock_llm_service, \
             patch("api.dependencies.get_config_manager") as mock_get_config:
            
            # 设置mock
            mock_config_manager = MagicMock()
            mock_config_manager.get_all.return_value = {"llm": {}}
            mock_get_config.return_value = mock_config_manager
            
            mock_service_instance = MagicMock()
            mock_service_instance.initialize = AsyncMock()
            mock_llm_service.return_value = mock_service_instance
            
            # 清除缓存
            import api.dependencies
            api.dependencies._service_cache.clear()
            
            result = await get_llm_service(mock_config_manager)
            
            assert result is not None
            mock_llm_service.assert_called_once()
            mock_service_instance.initialize.assert_called_once()
