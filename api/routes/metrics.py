"""
模块名称：监控指标API路由模块
功能描述：提供Prometheus指标和监控数据的HTTP API端点
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要路由：
    - GET /api/metrics: 获取Prometheus格式的指标数据
    - GET /api/metrics/stats: 获取统计信息（JSON格式）
    - GET /api/metrics/traces: 获取追踪列表
    - GET /api/metrics/traces/{trace_id}: 获取单个追踪详情
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from typing import Optional, List
from datetime import datetime
from core.llm.metrics_collector import MetricsCollector
from core.llm.request_tracer import RequestTracer, TraceContext
from api.dependencies import get_llm_service


router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("")
async def get_metrics(
    llm_service = Depends(get_llm_service),
) -> Response:
    """
    获取Prometheus格式的指标数据
    
    返回:
        Prometheus格式的指标数据
    """
    if not hasattr(llm_service, "_metrics_collector") or not llm_service._metrics_collector:
        raise HTTPException(status_code=503, detail="指标采集器未启用")
    
    collector: MetricsCollector = llm_service._metrics_collector
    metrics_data = collector.get_metrics()
    
    return Response(
        content=metrics_data,
        media_type=collector.get_content_type(),
    )


@router.get("/stats")
async def get_stats(
    llm_service = Depends(get_llm_service),
) -> dict:
    """
    获取统计信息（JSON格式）
    
    返回:
        统计信息字典
    """
    stats = {}
    
    # 获取成本统计
    if hasattr(llm_service, "get_cost_statistics"):
        try:
            cost_stats = await llm_service.get_cost_statistics()
            stats["cost"] = cost_stats
        except Exception:
            pass
    
    # 获取指标统计（从Prometheus注册表）
    if hasattr(llm_service, "_metrics_collector") and llm_service._metrics_collector:
        collector: MetricsCollector = llm_service._metrics_collector
        registry = collector.get_registry()
        
        # 提取关键指标
        metrics_data = {}
        for collector_obj in registry._collector_to_names:
            if hasattr(collector_obj, "_name"):
                metrics_data[collector_obj._name] = {
                    "type": type(collector_obj).__name__,
                }
        
        stats["metrics"] = metrics_data
    
    return stats


@router.get("/traces")
async def list_traces(
    limit: int = 100,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    llm_service = Depends(get_llm_service),
) -> List[dict]:
    """
    获取追踪列表
    
    参数:
        limit: 返回数量限制（默认100）
        start_time: 开始时间（可选）
        end_time: 结束时间（可选）
    
    返回:
        追踪上下文列表
    """
    if not hasattr(llm_service, "_request_tracer") or not llm_service._request_tracer:
        raise HTTPException(status_code=503, detail="请求追踪器未启用")
    
    tracer: RequestTracer = llm_service._request_tracer
    traces = await tracer.list_traces(
        limit=limit,
        start_time=start_time,
        end_time=end_time,
    )
    
    # 转换为字典格式
    return [
        {
            "trace_id": trace.trace_id,
            "start_time": trace.start_time.isoformat(),
            "end_time": trace.end_time.isoformat() if trace.end_time else None,
            "total_duration": trace.total_duration,
            "span_count": len(trace.spans),
            "metadata": trace.metadata,
        }
        for trace in traces
    ]


@router.get("/traces/{trace_id}")
async def get_trace(
    trace_id: str,
    llm_service = Depends(get_llm_service),
) -> dict:
    """
    获取单个追踪详情
    
    参数:
        trace_id: 追踪ID
    
    返回:
        追踪上下文详情
    """
    if not hasattr(llm_service, "_request_tracer") or not llm_service._request_tracer:
        raise HTTPException(status_code=503, detail="请求追踪器未启用")
    
    tracer: RequestTracer = llm_service._request_tracer
    trace = await tracer.get_trace(trace_id)
    
    if not trace:
        raise HTTPException(status_code=404, detail="追踪不存在")
    
    # 转换为字典格式
    return {
        "trace_id": trace.trace_id,
        "start_time": trace.start_time.isoformat(),
        "end_time": trace.end_time.isoformat() if trace.end_time else None,
        "total_duration": trace.total_duration,
        "metadata": trace.metadata,
        "spans": [
            {
                "span_id": span.span_id,
                "parent_span_id": span.parent_span_id,
                "operation": span.operation,
                "start_time": span.start_time.isoformat(),
                "end_time": span.end_time.isoformat() if span.end_time else None,
                "duration": span.duration,
                "tags": span.tags,
                "logs": span.logs,
                "error": span.error,
            }
            for span in trace.spans
        ],
    }
