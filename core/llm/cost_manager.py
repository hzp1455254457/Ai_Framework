"""
模块名称：成本管理器模块
功能描述：提供Token使用统计、成本计算、预算管理和成本优化建议
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - CostManager: 成本管理器

依赖模块：
    - core.llm.models: 数据模型
    - typing: 类型注解
    - datetime: 日期时间处理
    - asyncio: 异步编程
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import asyncio


@dataclass
class TokenUsage:
    """Token使用记录"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CostRecord:
    """成本记录"""
    adapter_name: str
    model: str
    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CostBudget:
    """成本预算"""
    daily_budget: float = 0.0  # 每日预算（美元）
    monthly_budget: float = 0.0  # 每月预算（美元）
    alert_threshold: float = 0.8  # 告警阈值（0.8表示80%）
    enabled: bool = False


class CostManager:
    """
    成本管理器
    
    管理LLM调用的成本统计、预算管理和优化建议。
    
    特性：
        - Token使用统计
        - 成本计算
        - 预算管理和告警
        - 成本优化建议
    
    示例:
        >>> cost_manager = CostManager()
        >>> await cost_manager.record_usage("openai-adapter", "gpt-3.5-turbo", usage)
        >>> stats = await cost_manager.get_statistics()
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化成本管理器
        
        参数:
            config: 配置字典
        """
        self._config = config or {}
        self._records: List[CostRecord] = []
        self._lock = asyncio.Lock()
        self._budget: CostBudget = CostBudget(
            daily_budget=self._config.get("daily_budget", 0.0),
            monthly_budget=self._config.get("monthly_budget", 0.0),
            alert_threshold=self._config.get("alert_threshold", 0.8),
            enabled=self._config.get("budget_enabled", False),
        )
    
    async def record_usage(
        self,
        adapter_name: str,
        model: str,
        usage: Dict[str, Any],
        cost_info: Optional[Dict[str, float]] = None,
    ) -> CostRecord:
        """
        记录Token使用和成本
        
        参数:
            adapter_name: 适配器名称
            model: 模型名称
            usage: Token使用信息 {prompt_tokens, completion_tokens, total_tokens}
            cost_info: 成本信息 {input: cost, output: cost}（可选，如果适配器已设置则自动获取）
        
        返回:
            成本记录
        """
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        
        # 计算成本
        if cost_info is None:
            # 如果没有提供成本信息，尝试从适配器获取
            # 这里需要适配器实例，暂时使用默认值
            cost_info = {"input": 0.0, "output": 0.0}
        
        input_cost = (prompt_tokens / 1000.0) * cost_info.get("input", 0.0)
        output_cost = (completion_tokens / 1000.0) * cost_info.get("output", 0.0)
        total_cost = input_cost + output_cost
        
        # 创建记录
        record = CostRecord(
            adapter_name=adapter_name,
            model=model,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            token_usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            ),
            timestamp=datetime.now(),
        )
        
        async with self._lock:
            self._records.append(record)
        
        # 检查预算
        if self._budget.enabled:
            await self._check_budget(record)
        
        return record
    
    async def _check_budget(self, record: CostRecord) -> None:
        """
        检查预算（内部方法）
        
        参数:
            record: 成本记录
        """
        # 计算今日和本月总成本
        today = datetime.now().date()
        month_start = datetime.now().replace(day=1).date()
        
        today_cost = sum(
            r.total_cost for r in self._records
            if r.timestamp.date() == today
        )
        month_cost = sum(
            r.total_cost for r in self._records
            if r.timestamp.date() >= month_start
        )
        
        # 检查告警
        if self._budget.daily_budget > 0:
            daily_ratio = today_cost / self._budget.daily_budget
            if daily_ratio >= self._budget.alert_threshold:
                # TODO: 发送告警通知
                pass
        
        if self._budget.monthly_budget > 0:
            monthly_ratio = month_cost / self._budget.monthly_budget
            if monthly_ratio >= self._budget.alert_threshold:
                # TODO: 发送告警通知
                pass
    
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        adapter_name: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        获取成本统计信息
        
        参数:
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            adapter_name: 适配器名称（可选，用于过滤）
            model: 模型名称（可选，用于过滤）
        
        返回:
            统计信息字典
        """
        async with self._lock:
            # 过滤记录
            filtered_records = self._records
            
            if start_date:
                filtered_records = [
                    r for r in filtered_records
                    if r.timestamp >= start_date
                ]
            
            if end_date:
                filtered_records = [
                    r for r in filtered_records
                    if r.timestamp <= end_date
                ]
            
            if adapter_name:
                filtered_records = [
                    r for r in filtered_records
                    if r.adapter_name == adapter_name
                ]
            
            if model:
                filtered_records = [
                    r for r in filtered_records
                    if r.model == model
                ]
            
            # 计算统计信息
            total_cost = sum(r.total_cost for r in filtered_records)
            total_input_cost = sum(r.input_cost for r in filtered_records)
            total_output_cost = sum(r.output_cost for r in filtered_records)
            
            total_prompt_tokens = sum(r.token_usage.prompt_tokens for r in filtered_records)
            total_completion_tokens = sum(r.token_usage.completion_tokens for r in filtered_records)
            total_tokens = sum(r.token_usage.total_tokens for r in filtered_records)
            
            # 按适配器分组统计
            adapter_stats: Dict[str, Dict[str, Any]] = {}
            for record in filtered_records:
                if record.adapter_name not in adapter_stats:
                    adapter_stats[record.adapter_name] = {
                        "total_cost": 0.0,
                        "total_tokens": 0,
                        "request_count": 0,
                    }
                adapter_stats[record.adapter_name]["total_cost"] += record.total_cost
                adapter_stats[record.adapter_name]["total_tokens"] += record.token_usage.total_tokens
                adapter_stats[record.adapter_name]["request_count"] += 1
            
            # 按模型分组统计
            model_stats: Dict[str, Dict[str, Any]] = {}
            for record in filtered_records:
                if record.model not in model_stats:
                    model_stats[record.model] = {
                        "total_cost": 0.0,
                        "total_tokens": 0,
                        "request_count": 0,
                    }
                model_stats[record.model]["total_cost"] += record.total_cost
                model_stats[record.model]["total_tokens"] += record.token_usage.total_tokens
                model_stats[record.model]["request_count"] += 1
            
            return {
                "total_cost": total_cost,
                "total_input_cost": total_input_cost,
                "total_output_cost": total_output_cost,
                "total_prompt_tokens": total_prompt_tokens,
                "total_completion_tokens": total_completion_tokens,
                "total_tokens": total_tokens,
                "request_count": len(filtered_records),
                "adapter_stats": adapter_stats,
                "model_stats": model_stats,
                "budget": {
                    "daily_budget": self._budget.daily_budget,
                    "monthly_budget": self._budget.monthly_budget,
                    "enabled": self._budget.enabled,
                },
            }
    
    async def get_optimization_suggestions(
        self,
        adapters: List[Any],
    ) -> List[Dict[str, Any]]:
        """
        获取成本优化建议
        
        参数:
            adapters: 适配器列表
        
        返回:
            优化建议列表
        """
        suggestions = []
        
        # 获取最近的成本统计
        stats = await self.get_statistics()
        
        # 建议1：推荐使用成本更低的模型
        if stats["model_stats"]:
            # 找到成本最低的模型
            cheapest_model = min(
                stats["model_stats"].items(),
                key=lambda x: x[1]["total_cost"] / max(x[1]["request_count"], 1)
            )
            suggestions.append({
                "type": "use_cheaper_model",
                "message": f"考虑使用成本更低的模型: {cheapest_model[0]}",
                "priority": "medium",
            })
        
        # 建议2：检查是否有高成本适配器
        if stats["adapter_stats"]:
            for adapter_name, adapter_stat in stats["adapter_stats"].items():
                avg_cost = adapter_stat["total_cost"] / max(adapter_stat["request_count"], 1)
                if avg_cost > 0.01:  # 平均每次调用成本超过$0.01
                    suggestions.append({
                        "type": "high_cost_adapter",
                        "message": f"适配器 {adapter_name} 平均成本较高: ${avg_cost:.4f}",
                        "priority": "low",
                    })
        
        # 建议3：检查预算使用情况
        if self._budget.enabled:
            today = datetime.now().date()
            today_cost = sum(
                r.total_cost for r in self._records
                if r.timestamp.date() == today
            )
            if self._budget.daily_budget > 0:
                daily_ratio = today_cost / self._budget.daily_budget
                if daily_ratio > 0.5:
                    suggestions.append({
                        "type": "budget_warning",
                        "message": f"今日预算使用率: {daily_ratio*100:.1f}%",
                        "priority": "high" if daily_ratio > 0.8 else "medium",
                    })
        
        return suggestions
    
    def set_budget(
        self,
        daily_budget: Optional[float] = None,
        monthly_budget: Optional[float] = None,
        alert_threshold: Optional[float] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        """
        设置成本预算
        
        参数:
            daily_budget: 每日预算（美元）
            monthly_budget: 每月预算（美元）
            alert_threshold: 告警阈值（0-1）
            enabled: 是否启用预算管理
        """
        if daily_budget is not None:
            self._budget.daily_budget = daily_budget
        if monthly_budget is not None:
            self._budget.monthly_budget = monthly_budget
        if alert_threshold is not None:
            self._budget.alert_threshold = alert_threshold
        if enabled is not None:
            self._budget.enabled = enabled
    
    async def clear_records(
        self,
        before_date: Optional[datetime] = None,
    ) -> int:
        """
        清理历史记录
        
        参数:
            before_date: 清理此日期之前的记录（如果为None，清理所有记录）
        
        返回:
            清理的记录数
        """
        async with self._lock:
            if before_date is None:
                count = len(self._records)
                self._records.clear()
                return count
            else:
                original_count = len(self._records)
                self._records = [
                    r for r in self._records
                    if r.timestamp >= before_date
                ]
                return original_count - len(self._records)
