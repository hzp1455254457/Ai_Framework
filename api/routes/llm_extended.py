"""
LLM扩展路由模块

提供LLM服务的扩展API接口，包括模型能力查询、路由策略查询、成本统计等。
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, Dict, Any, List
from datetime import datetime
from api.dependencies import get_llm_service
from core.llm.service import LLMService
from core.llm.models import RoutingStrategy, ModelCapability
from api.models.response import ErrorResponse

router = APIRouter()


@router.get("/models/capabilities")
async def get_model_capabilities(
    model: Optional[str] = Query(None, description="模型名称（可选，为空则返回所有模型）"),
    llm_service: LLMService = Depends(get_llm_service),
) -> Dict[str, Any]:
    """
    获取模型能力信息
    
    返回指定模型或所有模型的能力标签信息。
    
    参数:
        model: 模型名称（可选）
    
    返回:
        模型能力信息字典
    """
    try:
        capabilities_map: Dict[str, Dict[str, Any]] = {}
        
        # 获取所有适配器
        for adapter_name, adapter in llm_service._adapters.items():
            # 获取适配器支持的模型
            models = llm_service._registry.get_models_for_adapter(adapter_name)
            
            for model_name in models:
                # 如果指定了模型，只返回该模型
                if model and model_name != model:
                    continue
                
                # 获取模型能力
                capability = adapter.get_capability(model_name)
                cost_info = adapter.get_cost_per_1k_tokens(model_name)
                
                if capability:
                    capabilities_map[model_name] = {
                        "model": model_name,
                        "adapter": adapter_name,
                        "provider": adapter.provider,
                        "capability": {
                            "reasoning": capability.reasoning,
                            "creativity": capability.creativity,
                            "cost_effective": capability.cost_effective,
                            "fast": capability.fast,
                            "multilingual": capability.multilingual,
                            "vision": capability.vision,
                            "function_calling": capability.function_calling,
                        },
                        "cost_per_1k_tokens": cost_info or {},
                    }
        
        if model and model not in capabilities_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"模型 {model} 不存在或未注册"
            )
        
        return {
            "models": capabilities_map,
            "count": len(capabilities_map),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模型能力失败: {str(e)}"
        )


@router.get("/routing-strategies")
async def get_routing_strategies() -> Dict[str, Any]:
    """
    获取可用的路由策略列表
    
    返回:
        路由策略列表和描述
    """
    strategies = [
        {
            "name": "cost_first",
            "description": "成本优先：选择成本最低的适配器",
            "use_case": "适合对成本敏感的场景",
        },
        {
            "name": "performance_first",
            "description": "性能优先：选择延迟最低的适配器",
            "use_case": "适合对响应速度要求高的场景",
        },
        {
            "name": "availability_first",
            "description": "可用性优先：选择最健康的适配器",
            "use_case": "适合对稳定性要求高的场景",
        },
        {
            "name": "balanced",
            "description": "平衡模式：综合考虑成本、性能和可用性",
            "use_case": "适合大多数场景的默认策略",
        },
        {
            "name": "manual",
            "description": "手动模式：使用指定的适配器",
            "use_case": "适合需要精确控制适配器选择的场景",
        },
    ]
    
    return {
        "strategies": strategies,
        "count": len(strategies),
        "default": "balanced",
    }


@router.get("/cost/stats")
async def get_cost_statistics(
    start_date: Optional[datetime] = Query(None, description="开始日期（ISO格式）"),
    end_date: Optional[datetime] = Query(None, description="结束日期（ISO格式）"),
    adapter_name: Optional[str] = Query(None, description="适配器名称（可选）"),
    model: Optional[str] = Query(None, description="模型名称（可选）"),
    llm_service: LLMService = Depends(get_llm_service),
) -> Dict[str, Any]:
    """
    获取成本统计信息
    
    返回指定时间范围、适配器或模型的成本统计。
    
    参数:
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        adapter_name: 适配器名称（可选）
        model: 模型名称（可选）
    
    返回:
        成本统计信息
    """
    try:
        if not hasattr(llm_service, "get_cost_statistics"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="成本管理功能未启用"
            )
        
        stats = await llm_service.get_cost_statistics(
            start_date=start_date,
            end_date=end_date,
            adapter_name=adapter_name,
            model=model,
        )
        
        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=stats["error"]
            )
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取成本统计失败: {str(e)}"
        )


@router.get("/cost/optimization-suggestions")
async def get_cost_optimization_suggestions(
    llm_service: LLMService = Depends(get_llm_service),
) -> Dict[str, Any]:
    """
    获取成本优化建议
    
    返回:
        成本优化建议列表
    """
    try:
        if not hasattr(llm_service, "get_cost_optimization_suggestions"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="成本管理功能未启用"
            )
        
        suggestions = await llm_service.get_cost_optimization_suggestions()
        
        return {
            "suggestions": suggestions,
            "count": len(suggestions),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取优化建议失败: {str(e)}"
        )
