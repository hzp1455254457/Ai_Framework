"""
健康检查路由模块

提供健康检查相关的API接口。
"""

from fastapi import APIRouter, Depends
from api.models.response import HealthResponse
from api.dependencies import get_llm_service, get_config_manager
from core.llm.service import LLMService
from infrastructure.config.manager import ConfigManager

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check(
    llm_service: LLMService = Depends(get_llm_service),
    config_manager: ConfigManager = Depends(get_config_manager),
) -> HealthResponse:
    """
    健康检查接口
    
    返回:
        健康状态信息，包括服务状态、版本、可用适配器和模型列表
    """
    try:
        # 获取可用适配器列表
        adapters = list(llm_service._adapters.keys())
        
        # 获取支持的模型列表
        models = llm_service._registry.get_supported_models()
        
        return HealthResponse(
            status="healthy",
            version="0.1.0",
            adapters=adapters,
            models=models,
        )
    except Exception:
        return HealthResponse(
            status="unhealthy",
            version="0.1.0",
            adapters=[],
            models=[],
        )
