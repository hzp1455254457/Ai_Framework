"""
模块名称：健康检查服务模块
功能描述：提供适配器健康检查的基础功能
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - HealthStatus: 健康状态枚举
    - HealthCheckResult: 健康检查结果数据类
    - BaseHealthCheck: 健康检查抽象基类

依赖模块：
    - enum: Python标准库，枚举类型
    - dataclasses: Python标准库，数据类
    - typing: Python标准库，类型注解
    - datetime: Python标准库，日期时间
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from abc import ABC, abstractmethod


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"  # 健康，适配器可用
    UNHEALTHY = "unhealthy"  # 不健康，适配器不可用
    UNKNOWN = "unknown"  # 未知，健康状态未知


@dataclass
class HealthCheckResult:
    """
    健康检查结果数据类
    
    属性:
        status: 健康状态
        message: 健康检查消息（可选）
        timestamp: 检查时间戳
        details: 详细信息（可选）
    """
    status: HealthStatus
    message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        返回:
            健康检查结果的字典表示
        """
        result = {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.message:
            result["message"] = self.message
        if self.details:
            result["details"] = self.details
        return result


class BaseHealthCheck(ABC):
    """
    健康检查抽象基类
    
    提供健康检查的统一接口，子类需要实现具体的健康检查逻辑。
    
    示例:
        >>> class MyHealthCheck(BaseHealthCheck):
        ...     async def check(self) -> HealthCheckResult:
        ...         # 实现健康检查逻辑
        ...         return HealthCheckResult(HealthStatus.HEALTHY)
    """
    
    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """
        执行健康检查
        
        返回:
            健康检查结果
            
        异常:
            健康检查过程中的异常应该被捕获并返回UNHEALTHY状态
        """
        pass
    
    def check_sync(self) -> HealthCheckResult:
        """
        同步执行健康检查（默认实现）
        
        注意：此方法会阻塞，建议使用异步check()方法。
        
        返回:
            健康检查结果
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.check())
