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
            config = config_manager.get_all()
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
) -> AgentEngine:
    """
    获取Agent引擎实例
    
    参数:
        config_manager: 配置管理器实例
    
    返回:
        Agent引擎实例
    
    异常:
        HTTPException: 服务初始化失败时抛出
    """
    cache_key = "agent_engine"
    
    if cache_key not in _service_cache:
        try:
            config = config_manager.get_all()
            engine = AgentEngine(config)
            await engine.initialize()
            _service_cache[cache_key] = engine
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
            config = config_manager.get_all()
            orchestrator = AgentOrchestrator(config)
            await orchestrator.initialize()
            _service_cache[cache_key] = orchestrator
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Agent编排器初始化失败: {str(e)}"
            ) from e
    
    return _service_cache[cache_key]
