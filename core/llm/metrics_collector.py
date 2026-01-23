"""
模块名称：指标采集器模块
功能描述：提供Prometheus指标采集能力，支持QPS、延迟、成功率、成本等关键指标
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - MetricsCollector: 指标采集器

依赖模块：
    - prometheus_client: Prometheus客户端
    - typing: 类型注解
    - time: 时间处理
    - asyncio: 异步编程
"""

from typing import Dict, Any, Optional
from time import time
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
    from prometheus_client.exposition import CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # 定义占位符类，避免导入错误
    class Counter:
        def __init__(self, *args, **kwargs):
            pass
        def inc(self, *args, **kwargs):
            pass
    class Histogram:
        def __init__(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass
    class Gauge:
        def __init__(self, *args, **kwargs):
            self._labels = None
        def labels(self, *args, **kwargs):
            return self
        def set(self, *args, **kwargs):
            pass
        def inc(self, *args, **kwargs):
            pass
        def dec(self, *args, **kwargs):
            pass
    class Summary:
        def __init__(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass
    class CollectorRegistry:
        def __init__(self):
            pass
    def generate_latest(*args, **kwargs):
        return b""
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
import asyncio


class MetricsCollector:
    """
    指标采集器
    
    使用Prometheus客户端采集LLM服务的各项指标。
    
    特性：
        - QPS（每秒请求数）
        - 延迟统计（P50, P95, P99）
        - 成功率统计
        - Token使用统计
        - 成本统计
        - 错误统计
    
    示例:
        >>> collector = MetricsCollector()
        >>> collector.record_request("openai-adapter", "gpt-3.5-turbo", 0.5, True)
        >>> metrics = collector.get_metrics()
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None) -> None:
        """
        初始化指标采集器
        
        参数:
            registry: Prometheus注册表（可选，默认使用全局注册表）
        
        异常:
            ImportError: 如果prometheus_client未安装且未提供占位符实现
        """
        if not PROMETHEUS_AVAILABLE:
            raise ImportError("prometheus_client is not installed. Install it with: pip install prometheus-client")
        self._registry = registry or CollectorRegistry()
        
        # 请求计数器（按适配器和模型）
        self._request_counter = Counter(
            "llm_requests_total",
            "Total number of LLM requests",
            ["adapter", "model", "status"],
            registry=self._registry,
        )
        
        # 请求延迟直方图（按适配器和模型）
        self._request_duration = Histogram(
            "llm_request_duration_seconds",
            "LLM request duration in seconds",
            ["adapter", "model"],
            registry=self._registry,
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
        )
        
        # 请求延迟摘要（用于计算分位数）
        self._request_duration_summary = Summary(
            "llm_request_duration_summary_seconds",
            "LLM request duration summary in seconds",
            ["adapter", "model"],
            registry=self._registry,
        )
        
        # Token使用计数器
        self._token_counter = Counter(
            "llm_tokens_total",
            "Total number of tokens used",
            ["adapter", "model", "type"],  # type: prompt/completion/total
            registry=self._registry,
        )
        
        # 成本计量器（当前总成本）
        self._cost_gauge = Gauge(
            "llm_cost_total",
            "Total cost in USD",
            ["adapter", "model"],
            registry=self._registry,
        )
        
        # 活跃请求数
        self._active_requests = Gauge(
            "llm_active_requests",
            "Number of active LLM requests",
            ["adapter", "model"],
            registry=self._registry,
        )
        
        # 错误计数器（按错误类型）
        self._error_counter = Counter(
            "llm_errors_total",
            "Total number of LLM errors",
            ["adapter", "model", "error_type"],
            registry=self._registry,
        )
        
        # QPS计量器（最近1分钟）
        self._qps_gauge = Gauge(
            "llm_qps",
            "Requests per second",
            ["adapter", "model"],
            registry=self._registry,
        )
        
        # 请求时间戳记录（用于计算QPS）
        self._request_timestamps: Dict[str, list] = {}
        self._lock = asyncio.Lock()
    
    def record_request(
        self,
        adapter: str,
        model: str,
        duration: float,
        success: bool,
        tokens: Optional[Dict[str, int]] = None,
        cost: Optional[float] = None,
        error_type: Optional[str] = None,
    ) -> None:
        """
        记录请求指标
        
        参数:
            adapter: 适配器名称
            model: 模型名称
            duration: 请求持续时间（秒）
            success: 是否成功
            tokens: Token使用信息 {prompt_tokens, completion_tokens, total_tokens}
            cost: 成本（美元）
            error_type: 错误类型（如果失败）
        """
        # 记录请求计数
        status = "success" if success else "error"
        self._request_counter.labels(adapter=adapter, model=model, status=status).inc()
        
        # 记录延迟
        self._request_duration.labels(adapter=adapter, model=model).observe(duration)
        self._request_duration_summary.labels(adapter=adapter, model=model).observe(duration)
        
        # 记录Token使用
        if tokens:
            self._token_counter.labels(
                adapter=adapter,
                model=model,
                type="prompt",
            ).inc(tokens.get("prompt_tokens", 0))
            self._token_counter.labels(
                adapter=adapter,
                model=model,
                type="completion",
            ).inc(tokens.get("completion_tokens", 0))
            self._token_counter.labels(
                adapter=adapter,
                model=model,
                type="total",
            ).inc(tokens.get("total_tokens", 0))
        
        # 记录成本
        if cost is not None:
            self._cost_gauge.labels(adapter=adapter, model=model).inc(cost)
        
        # 记录错误
        if not success and error_type:
            self._error_counter.labels(
                adapter=adapter,
                model=model,
                error_type=error_type,
            ).inc()
        
        # 记录请求时间戳（用于计算QPS）
        asyncio.create_task(self._record_timestamp(adapter, model))
    
    async def _record_timestamp(self, adapter: str, model: str) -> None:
        """
        记录请求时间戳（内部方法）
        
        参数:
            adapter: 适配器名称
            model: 模型名称
        """
        key = f"{adapter}:{model}"
        async with self._lock:
            if key not in self._request_timestamps:
                self._request_timestamps[key] = []
            self._request_timestamps[key].append(time())
            
            # 只保留最近1分钟的时间戳
            cutoff = time() - 60
            self._request_timestamps[key] = [
                ts for ts in self._request_timestamps[key] if ts > cutoff
            ]
            
            # 计算QPS
            qps = len(self._request_timestamps[key]) / 60.0
            self._qps_gauge.labels(adapter=adapter, model=model).set(qps)
    
    def increment_active_requests(self, adapter: str, model: str) -> None:
        """
        增加活跃请求数
        
        参数:
            adapter: 适配器名称
            model: 模型名称
        """
        self._active_requests.labels(adapter=adapter, model=model).inc()
    
    def decrement_active_requests(self, adapter: str, model: str) -> None:
        """
        减少活跃请求数
        
        参数:
            adapter: 适配器名称
            model: 模型名称
        """
        self._active_requests.labels(adapter=adapter, model=model).dec()
    
    def get_metrics(self) -> bytes:
        """
        获取Prometheus格式的指标数据
        
        返回:
            Prometheus格式的指标数据（字节）
        """
        return generate_latest(self._registry)
    
    def get_content_type(self) -> str:
        """
        获取指标数据的Content-Type
        
        返回:
            Content-Type字符串
        """
        return CONTENT_TYPE_LATEST
    
    def get_registry(self) -> CollectorRegistry:
        """
        获取Prometheus注册表
        
        返回:
            Prometheus注册表
        """
        return self._registry
