"""
模块名称：适配器工厂模块
功能描述：提供适配器工厂模式实现，支持动态创建适配器实例
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - AdapterFactory: 适配器工厂

依赖模块：
    - core.llm.adapters.base: 适配器基类
    - core.llm.adapters.registry: 适配器注册表
    - typing: 类型注解
"""

from typing import Dict, Any, Optional, Type
from core.llm.adapters.base import BaseLLMAdapter
from core.llm.adapters.registry import AdapterRegistry


class AdapterFactory:
    """
    适配器工厂
    
    根据配置动态创建适配器实例，支持插件式扩展。
    
    特性：
        - 统一创建接口
        - 支持动态注册
        - 实例缓存管理
        - 生命周期管理
    
    示例:
        >>> factory = AdapterFactory(registry)
        >>> adapter = await factory.create_adapter("openai-adapter", config)
        >>> factory.register_adapter("custom-adapter", CustomAdapter)
    """
    
    def __init__(self, registry: Optional[AdapterRegistry] = None) -> None:
        """
        初始化适配器工厂
        
        参数:
            registry: 适配器注册表，如果为None则创建新的注册表
        """
        self._registry = registry or AdapterRegistry()
        self._instances: Dict[str, BaseLLMAdapter] = {}
    
    def register_adapter(
        self,
        adapter_type: str,
        adapter_class: Type[BaseLLMAdapter],
        models: Optional[list[str]] = None,
    ) -> None:
        """
        注册适配器类
        
        参数:
            adapter_type: 适配器类型标识
            adapter_class: 适配器类
            models: 该适配器支持的模型列表（可选）
        
        示例:
            >>> factory.register_adapter("custom-adapter", CustomAdapter, ["model1", "model2"])
        """
        self._registry.register_adapter(adapter_class, models=models)
    
    async def create_adapter(
        self,
        adapter_type: str,
        config: Dict[str, Any],
        connection_pool: Optional[Any] = None,
    ) -> BaseLLMAdapter:
        """
        创建适配器实例
        
        根据适配器类型和配置创建适配器实例。
        如果已存在相同配置的实例，则返回缓存实例。
        
        参数:
            adapter_type: 适配器类型标识
            config: 适配器配置
        
        返回:
            适配器实例
        
        异常:
            ValueError: 适配器类型不存在时抛出
        
        示例:
            >>> adapter = await factory.create_adapter("openai-adapter", {"api_key": "..."})
        """
        # 检查是否已有缓存实例
        cache_key = self._get_cache_key(adapter_type, config)
        if cache_key in self._instances:
            return self._instances[cache_key]
        
        # 从注册表创建适配器（传递连接池）
        adapter = await self._registry.create_adapter(adapter_type, config, connection_pool=connection_pool)
        
        # 缓存实例
        self._instances[cache_key] = adapter
        
        return adapter
    
    def _get_cache_key(self, adapter_type: str, config: Dict[str, Any]) -> str:
        """
        生成缓存键
        
        参数:
            adapter_type: 适配器类型
            config: 配置字典
        
        返回:
            缓存键字符串
        """
        # 使用适配器类型和配置的哈希值作为缓存键
        import hashlib
        import json
        
        config_str = json.dumps(config, sort_keys=True)
        config_hash = hashlib.md5(config_str.encode()).hexdigest()[:8]
        return f"{adapter_type}_{config_hash}"
    
    def get_cached_instance(
        self,
        adapter_type: str,
        config: Dict[str, Any],
    ) -> Optional[BaseLLMAdapter]:
        """
        获取缓存的适配器实例
        
        参数:
            adapter_type: 适配器类型
            config: 配置字典
        
        返回:
            缓存的适配器实例，如果不存在返回None
        """
        cache_key = self._get_cache_key(adapter_type, config)
        return self._instances.get(cache_key)
    
    def clear_cache(self) -> None:
        """清空所有缓存的适配器实例"""
        self._instances.clear()
    
    def remove_instance(
        self,
        adapter_type: str,
        config: Dict[str, Any],
    ) -> bool:
        """
        移除缓存的适配器实例
        
        参数:
            adapter_type: 适配器类型
            config: 配置字典
        
        返回:
            是否成功移除
        """
        cache_key = self._get_cache_key(adapter_type, config)
        if cache_key in self._instances:
            adapter = self._instances.pop(cache_key)
            # 清理适配器资源
            if hasattr(adapter, 'cleanup'):
                # 异步清理，但这里不等待（因为可能不在async上下文中）
                pass
            return True
        return False
    
    @property
    def registry(self) -> AdapterRegistry:
        """获取适配器注册表"""
        return self._registry
