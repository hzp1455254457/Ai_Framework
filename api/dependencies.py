"""
API依赖注入模块

提供FastAPI的依赖注入功能，包括服务实例获取等。
"""

from typing import Dict, Any
from fastapi import Depends, HTTPException
from infrastructure.config.manager import ConfigManager
from core.llm.service import LLMService
from core.agent.engine import AgentEngine
from core.agent.collaboration import AgentOrchestrator
from core.vision.service import VisionService
# 导入抽象接口架构
from core.interfaces.agent import IAgentEngine
from core.composition.component_manager import ComponentManager


# 全局服务实例缓存
_service_cache: Dict[str, Any] = {}


def get_config_manager() -> ConfigManager:
    """
    获取配置管理器实例
    
    返回:
        配置管理器实例
    """
    cache_key = "config_manager"
    
    if cache_key not in _service_cache:
        # 从环境变量获取环境配置，默认为dev
        import os
        env = os.getenv("APP_ENV", "dev")
        _service_cache[cache_key] = ConfigManager.load(env=env)
    
    return _service_cache[cache_key]


async def get_llm_service(
    config_manager: ConfigManager = Depends(get_config_manager),
) -> LLMService:
    """
    获取LLM服务实例
    
    参数:
        config_manager: 配置管理器实例
    
    返回:
        LLM服务实例
    
    异常:
        HTTPException: 服务初始化失败时抛出
    """
    cache_key = "llm_service"
    
    if cache_key not in _service_cache:
        try:
            config = config_manager.config
            service = LLMService(config)
            await service.initialize()
            _service_cache[cache_key] = service
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM服务初始化失败: {str(e)}"
            ) from e
    
    return _service_cache[cache_key]


async def get_agent_engine(
    config_manager: ConfigManager = Depends(get_config_manager),
) -> IAgentEngine:
    """
    获取Agent引擎实例（使用抽象接口架构）
    
    参数:
        config_manager: 配置管理器实例
    
    返回:
        Agent引擎实例（实现IAgentEngine接口，可能是Native/LangChain/LangGraph）
    
    异常:
        HTTPException: 服务初始化失败时抛出
    """
    cache_key = "agent_engine"
    
    if cache_key not in _service_cache:
        try:
            config = config_manager.config
            
            # 使用ComponentManager创建组件（支持LangChain实现）
            component_manager = ComponentManager(config)
            await component_manager.initialize()
            
            # 获取Agent引擎（根据配置自动选择实现类型）
            engine = component_manager.agent_engine
            _service_cache[cache_key] = engine
            
            # 同时缓存ComponentManager以便后续使用
            _service_cache["component_manager"] = component_manager
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Agent引擎初始化失败: {str(e)}"
            ) from e
    
    return _service_cache[cache_key]


async def get_agent_orchestrator(
    config_manager: ConfigManager = Depends(get_config_manager),
) -> AgentOrchestrator:
    """
    获取Agent编排器实例
    
    参数:
        config_manager: 配置管理器实例
    
    返回:
        Agent编排器实例
    
    异常:
        HTTPException: 服务初始化失败时抛出
    """
    cache_key = "agent_orchestrator"
    
    if cache_key not in _service_cache:
        try:
            config = config_manager.config
            orchestrator = AgentOrchestrator(config)
            await orchestrator.initialize()
            _service_cache[cache_key] = orchestrator
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Agent编排器初始化失败: {str(e)}"
            ) from e
    
    return _service_cache[cache_key]


async def get_vision_service(
    config_manager: ConfigManager = Depends(get_config_manager),
) -> VisionService:
    """
    获取Vision服务实例
    
    参数:
        config_manager: 配置管理器实例
    
    返回:
        Vision服务实例
    
    异常:
        HTTPException: 服务初始化失败时抛出
    """
    cache_key = "vision_service"
    
    if cache_key not in _service_cache:
        try:
            config = config_manager.config
            service = VisionService(config)
            await service.initialize()
            
            # 注册Vision适配器
            vision_config = config.get("vision", {})
            adapters_config = vision_config.get("adapters", {})
            
            # 注册DALL-E适配器
            if "dalle-adapter" in adapters_config:
                dalle_config = adapters_config["dalle-adapter"]
                api_key = dalle_config.get("api_key", "")
                
                if api_key:
                    try:
                        from core.vision.adapters.dalle_adapter import DALLEAdapter
                        dalle_adapter = DALLEAdapter(dalle_config)
                        await dalle_adapter.initialize(dalle_config)
                        service.register_adapter(dalle_adapter)
                    except Exception as e:
                        # 适配器注册失败不影响服务启动，只记录日志
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"DALL-E适配器注册失败: {e}")
            
            _service_cache[cache_key] = service
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Vision服务初始化失败: {str(e)}"
            ) from e
    
    return _service_cache[cache_key]
