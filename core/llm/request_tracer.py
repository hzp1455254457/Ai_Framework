"""
模块名称：请求追踪模块
功能描述：提供请求追踪能力，支持分布式追踪和请求链路分析
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - RequestTracer: 请求追踪器
    - TraceContext: 追踪上下文

依赖模块：
    - typing: 类型注解
    - uuid: UUID生成
    - datetime: 日期时间处理
    - asyncio: 异步编程
"""

from typing import Dict, Any, Optional, List
from uuid import uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import asyncio


@dataclass
class TraceSpan:
    """追踪跨度"""
    span_id: str
    parent_span_id: Optional[str]
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class TraceContext:
    """追踪上下文"""
    trace_id: str
    spans: List[TraceSpan] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class RequestTracer:
    """
    请求追踪器
    
    提供请求追踪能力，支持：
    - 分布式追踪
    - 请求链路分析
    - 性能分析
    - 错误追踪
    
    示例:
        >>> tracer = RequestTracer()
        >>> context = tracer.start_trace("llm_request")
        >>> span = tracer.start_span(context, "adapter_call", adapter="openai")
        >>> tracer.end_span(span)
        >>> tracer.end_trace(context)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化请求追踪器
        
        参数:
            config: 配置字典
                - max_traces: 最大追踪数（默认1000）
                - trace_ttl: 追踪TTL（秒，默认3600）
                - enabled: 是否启用追踪（默认True）
        """
        self._config = config or {}
        self._max_traces = self._config.get("max_traces", 1000)
        self._trace_ttl = self._config.get("trace_ttl", 3600)
        self._enabled = self._config.get("enabled", True)
        
        self._traces: Dict[str, TraceContext] = {}
        self._lock = asyncio.Lock()
    
    def start_trace(
        self,
        operation: str,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TraceContext:
        """
        开始追踪
        
        参数:
            operation: 操作名称
            trace_id: 追踪ID（可选，自动生成）
            metadata: 元数据（可选）
        
        返回:
            追踪上下文
        """
        if not self._enabled:
            # 返回一个空的上下文，但不记录
            return TraceContext(trace_id=trace_id or str(uuid4()))
        
        trace_id = trace_id or str(uuid4())
        context = TraceContext(
            trace_id=trace_id,
            start_time=datetime.now(),
            metadata=metadata or {},
        )
        
        # 创建根跨度
        root_span = TraceSpan(
            span_id=str(uuid4()),
            parent_span_id=None,
            operation=operation,
            start_time=context.start_time,
        )
        context.spans.append(root_span)
        
        # 存储追踪上下文
        asyncio.create_task(self._store_trace(context))
        
        return context
    
    async def _store_trace(self, context: TraceContext) -> None:
        """
        存储追踪上下文（内部方法）
        
        参数:
            context: 追踪上下文
        """
        async with self._lock:
            # 清理过期追踪
            await self._cleanup_expired_traces()
            
            # 如果超过最大数量，删除最旧的
            if len(self._traces) >= self._max_traces:
                oldest_trace_id = min(
                    self._traces.keys(),
                    key=lambda k: self._traces[k].start_time,
                )
                del self._traces[oldest_trace_id]
            
            self._traces[context.trace_id] = context
    
    async def _cleanup_expired_traces(self) -> None:
        """清理过期追踪（内部方法）"""
        cutoff = datetime.now() - timedelta(seconds=self._trace_ttl)
        expired_ids = [
            trace_id
            for trace_id, trace in self._traces.items()
            if trace.start_time < cutoff
        ]
        for trace_id in expired_ids:
            del self._traces[trace_id]
    
    def start_span(
        self,
        context: TraceContext,
        operation: str,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
    ) -> TraceSpan:
        """
        开始跨度
        
        参数:
            context: 追踪上下文
            operation: 操作名称
            parent_span_id: 父跨度ID（可选，默认使用最后一个跨度）
            tags: 标签（可选）
        
        返回:
            追踪跨度
        """
        if not self._enabled:
            # 返回一个空的跨度，但不记录
            return TraceSpan(
                span_id=str(uuid4()),
                parent_span_id=parent_span_id,
                operation=operation,
                start_time=datetime.now(),
            )
        
        # 如果没有指定父跨度，使用最后一个跨度
        if parent_span_id is None and context.spans:
            parent_span_id = context.spans[-1].span_id
        
        span = TraceSpan(
            span_id=str(uuid4()),
            parent_span_id=parent_span_id,
            operation=operation,
            start_time=datetime.now(),
            tags=tags or {},
        )
        context.spans.append(span)
        
        return span
    
    def end_span(self, span: TraceSpan, error: Optional[str] = None) -> None:
        """
        结束跨度
        
        参数:
            span: 追踪跨度
            error: 错误信息（可选）
        """
        if not self._enabled:
            return
        
        span.end_time = datetime.now()
        span.duration = (span.end_time - span.start_time).total_seconds()
        if error:
            span.error = error
    
    def add_span_log(self, span: TraceSpan, message: str, level: str = "info") -> None:
        """
        添加跨度日志
        
        参数:
            span: 追踪跨度
            message: 日志消息
            level: 日志级别
        """
        if not self._enabled:
            return
        
        span.logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
        })
    
    def end_trace(self, context: TraceContext) -> None:
        """
        结束追踪
        
        参数:
            context: 追踪上下文
        """
        if not self._enabled:
            return
        
        context.end_time = datetime.now()
        if context.start_time:
            context.total_duration = (
                context.end_time - context.start_time
            ).total_seconds()
    
    async def get_trace(self, trace_id: str) -> Optional[TraceContext]:
        """
        获取追踪上下文
        
        参数:
            trace_id: 追踪ID
        
        返回:
            追踪上下文（如果存在）
        """
        async with self._lock:
            return self._traces.get(trace_id)
    
    async def list_traces(
        self,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[TraceContext]:
        """
        列出追踪上下文
        
        参数:
            limit: 返回数量限制
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
        
        返回:
            追踪上下文列表
        """
        async with self._lock:
            traces = list(self._traces.values())
            
            # 过滤时间范围
            if start_time:
                traces = [t for t in traces if t.start_time >= start_time]
            if end_time:
                traces = [t for t in traces if t.start_time <= end_time]
            
            # 按时间排序（最新的在前）
            traces.sort(key=lambda t: t.start_time, reverse=True)
            
            return traces[:limit]
    
    async def clear_traces(self) -> int:
        """
        清理所有追踪
        
        返回:
            清理的追踪数
        """
        async with self._lock:
            count = len(self._traces)
            self._traces.clear()
            return count
