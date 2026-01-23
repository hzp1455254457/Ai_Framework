"""
模块名称：适配器注册表模块
功能描述：提供适配器的注册、发现和管理功能
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - AdapterRegistry: 适配器注册表
    - ModelAdapterMapping: 模型到适配器的映射

依赖模块：
    - core.llm.adapters.base: 适配器基类
    - typing: 类型注解
    - importlib: 动态导入
"""

from typing import Dict, List, Optional, Type, Any
from importlib import import_module
from pathlib import Path
import inspect
from core.llm.adapters.base import BaseLLMAdapter


class AdapterRegistry:
    """
    适配器注册表
    
    管理所有适配器的注册、发现和查找。
    
    特性：
        - 自动发现适配器类
        - 适配器注册和管理
        - 模型到适配器的映射
        - 适配器实例缓存
    
    示例:
        >>> registry = AdapterRegistry()
        >>> registry.discover_adapters()
        >>> adapter = registry.create_adapter("doubao", config)
        >>> adapter = registry.get_adapter_for_model("qwen-turbo")
    """
    
    def __init__(self) -> None:
        """初始化适配器注册表"""
        self._adapters: Dict[str, Type[BaseLLMAdapter]] = {}
        self._instances: Dict[str, BaseLLMAdapter] = {}
        self._model_mapping: Dict[str, str] = {}  # model_name -> adapter_name
        self._initialized: bool = False
    
    def discover_adapters(self) -> None:
        """
        自动发现适配器类
        
        扫描adapters目录下的所有适配器类并注册。
        
        说明:
            自动扫描core.llm.adapters模块下的所有适配器类，
            识别BaseLLMAdapter的子类并注册。
        """
        try:
            # 导入适配器模块
            from core.llm.adapters import (
                doubao_adapter,
                qwen_adapter,
                deepseek_adapter,
                openai_adapter,
                claude_adapter,
                ollama_adapter,
            )
            
            # 扫描模块中的适配器类
            modules = [
                doubao_adapter,
                qwen_adapter,
                deepseek_adapter,
                openai_adapter,
                claude_adapter,
                ollama_adapter,
            ]
            
            # 尝试导入LiteLLM适配器（可选）
            try:
                from core.llm.adapters import litellm_adapter
                modules.append(litellm_adapter)
            except ImportError:
                # LiteLLM未安装，跳过
                pass
            
            for module in modules:
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # 检查是否是适配器类（BaseLLMAdapter的子类，但不是基类本身）
                    if (
                        issubclass(obj, BaseLLMAdapter)
                        and obj is not BaseLLMAdapter
                        and obj.__module__ == module.__name__
                    ):
                        # 创建临时实例获取适配器名称
                        try:
                            temp_instance = obj({})
                            adapter_name = temp_instance.name
                            self._adapters[adapter_name] = obj
                        except Exception:
                            # 如果无法实例化，跳过
                            continue
            
            self._initialized = True
            
        except Exception as e:
            raise RuntimeError(f"适配器发现失败: {e}") from e
    
    def register_adapter(
        self,
        adapter_class: Type[BaseLLMAdapter],
        models: Optional[List[str]] = None,
    ) -> None:
        """
        手动注册适配器类
        
        参数:
            adapter_class: 适配器类
            models: 该适配器支持的模型列表（可选，用于自动映射）
        
        示例:
            >>> registry.register_adapter(MyAdapter, models=["model1", "model2"])
        """
        try:
            # 创建临时实例获取适配器名称
            temp_instance = adapter_class({})
            adapter_name = temp_instance.name
            
            self._adapters[adapter_name] = adapter_class
            
            # 注册模型映射
            if models:
                for model in models:
                    self._model_mapping[model] = adapter_name
                    
        except Exception as e:
            raise ValueError(f"适配器注册失败: {e}") from e
    
    async def create_adapter(
        self,
        adapter_name: str,
        config: Dict[str, Any],
        connection_pool: Optional[Any] = None,
    ) -> BaseLLMAdapter:
        """
        创建适配器实例
        
        参数:
            adapter_name: 适配器名称
            config: 适配器配置
        
        返回:
            适配器实例
        
        异常:
            ValueError: 适配器不存在时抛出
        """
        if adapter_name not in self._adapters:
            raise ValueError(f"适配器不存在: {adapter_name}")
        
        # 如果已有实例且配置相同，返回缓存实例
        cache_key = f"{adapter_name}_{id(config)}"
        if cache_key in self._instances:
            return self._instances[cache_key]
        
        # 创建新实例（传递连接池）
        adapter_class = self._adapters[adapter_name]
        adapter = adapter_class(config, connection_pool=connection_pool)
        await adapter.initialize()
        
        # 缓存实例
        self._instances[cache_key] = adapter
        
        return adapter
    
    def get_adapter_for_model(self, model: str) -> Optional[str]:
        """
        根据模型名称获取适配器名称
        
        参数:
            model: 模型名称（如 "qwen-turbo", "deepseek-chat"）
        
        返回:
            适配器名称，如果未找到返回None
        """
        # 直接匹配
        if model in self._model_mapping:
            return self._model_mapping[model]
        
        # 模糊匹配（模型名称包含适配器名称）
        model_lower = model.lower()
        for adapter_name in self._adapters.keys():
            if adapter_name.replace("-adapter", "") in model_lower:
                return adapter_name
        
        # 默认匹配（基于模型名称前缀）
        if model.startswith("gpt") or model.startswith("o1"):
            return "openai-adapter"
        elif model.startswith("claude"):
            return "claude-adapter"
        elif model.startswith("qwen"):
            return "qwen-adapter"
        elif model.startswith("deepseek"):
            return "deepseek-adapter"
        elif "doubao" in model.lower():
            return "doubao-adapter"
        elif "ollama" in model.lower() or model.lower().startswith("ollama:"):
            return "ollama-adapter"
        
        return None
    
    def register_model_mapping(self, model: str, adapter_name: str) -> None:
        """
        注册模型到适配器的映射
        
        参数:
            model: 模型名称
            adapter_name: 适配器名称
        
        示例:
            >>> registry.register_model_mapping("qwen-turbo", "qwen-adapter")
        """
        if adapter_name not in self._adapters:
            raise ValueError(f"适配器不存在: {adapter_name}")
        
        self._model_mapping[model] = adapter_name
    
    def get_available_adapters(self) -> List[str]:
        """
        获取所有可用的适配器名称
        
        返回:
            适配器名称列表
        """
        return list(self._adapters.keys())
    
    def get_supported_models(self) -> List[str]:
        """
        获取所有支持的模型列表
        
        返回:
            模型名称列表
        """
        return list(self._model_mapping.keys())
    
    @property
    def is_initialized(self) -> bool:
        """检查注册表是否已初始化"""
        return self._initialized
