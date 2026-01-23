"""
健康检查路由模块

提供健康检查相关的API接口。
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from api.models.response import (
    HealthResponse,
    AdapterHealthResponse,
    AdapterHealthStatus,
)
from api.dependencies import get_llm_service, get_vision_service, get_config_manager
from core.llm.service import LLMService
from core.vision.service import VisionService
from infrastructure.config.manager import ConfigManager
from core.base.health_check import HealthStatus

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


@router.get("/adapters", response_model=AdapterHealthResponse)
async def adapter_health_check(
    service_type: Optional[str] = Query(None, description="服务类型：llm/vision，为空则检查所有"),
    adapter_name: Optional[str] = Query(None, description="适配器名称，为空则检查所有"),
    llm_service: LLMService = Depends(get_llm_service),
    vision_service: VisionService = Depends(get_vision_service),
) -> AdapterHealthResponse:
    """
    适配器健康检查接口
    
    检查指定服务类型或所有服务的适配器健康状态。
    
    参数:
        service_type: 服务类型（llm/vision），为空则检查所有
        adapter_name: 适配器名称，为空则检查所有
    
    返回:
        适配器健康状态响应，包含所有适配器的健康状态
    """
    all_results: dict = {}
    
    # 检查LLM适配器
    if not service_type or service_type == "llm":
        llm_results = await llm_service.check_adapter_health(adapter_name)
        # 添加服务类型前缀
        for name, result in llm_results.items():
            all_results[f"llm:{name}"] = result
    
    # 检查Vision适配器
    if not service_type or service_type == "vision":
        vision_results = await vision_service.check_adapter_health(adapter_name)
        # 添加服务类型前缀
        for name, result in vision_results.items():
            all_results[f"vision:{name}"] = result
    
    # 转换为响应格式
    adapter_statuses = {}
    healthy_count = 0
    unhealthy_count = 0
    unknown_count = 0
    
    for name, result in all_results.items():
        status_str = result.status.value
        if result.status == HealthStatus.HEALTHY:
            healthy_count += 1
        elif result.status == HealthStatus.UNHEALTHY:
            unhealthy_count += 1
        else:
            unknown_count += 1
        
        adapter_statuses[name] = AdapterHealthStatus(
            name=name,
            status=status_str,
            message=result.message,
            timestamp=result.timestamp.isoformat(),
            details=result.details,
        )
    
    return AdapterHealthResponse(
        adapters=adapter_statuses,
        healthy_count=healthy_count,
        unhealthy_count=unhealthy_count,
        unknown_count=unknown_count,
    )
