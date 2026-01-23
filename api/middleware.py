"""
API中间件模块

提供FastAPI中间件，包括CORS、请求日志、错误处理等。
"""

import time
import logging
from typing import Callable, Optional, Dict, Any
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from infrastructure.log.masking import DataMaskingService

logger = logging.getLogger(__name__)

# 全局数据脱敏服务实例（延迟初始化）
_masking_service: Optional[DataMaskingService] = None


def get_masking_service(config: Optional[Dict[str, Any]] = None) -> Optional[DataMaskingService]:
    """
    获取数据脱敏服务实例（单例模式）
    
    参数:
        config: 脱敏配置（可选）
    
    返回:
        数据脱敏服务实例（如果配置启用）或None
    """
    global _masking_service
    
    if _masking_service is None and config:
        masking_config = config.get("masking", {})
        if masking_config.get("enabled", True):
            _masking_service = DataMaskingService(masking_config)
    
    return _masking_service


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录日志"""
        start_time = time.time()
        
        # 记录请求信息
        logger.info(
            f"请求: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
            }
        )
        
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"响应: {request.method} {request.url.path} - {response.status_code} "
                f"({process_time:.3f}s)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": process_time,
                }
            )
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录错误
            logger.error(
                f"请求失败: {request.method} {request.url.path} - {str(e)} "
                f"({process_time:.3f}s)",
                exc_info=True,
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time": process_time,
                }
            )
            
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""
    
    def __init__(self, app, masking_config: Optional[Dict[str, Any]] = None):
        """
        初始化错误处理中间件
        
        参数:
            app: FastAPI应用实例
            masking_config: 数据脱敏配置（可选）
        """
        super().__init__(app)
        self._masking_service = get_masking_service(masking_config)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并捕获异常"""
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            # 记录异常（日志会自动脱敏，如果启用了脱敏功能）
            logger.exception(f"未处理的异常: {str(e)}")
            
            # 构建错误响应
            error_detail = str(e)
            
            # 如果启用了脱敏，对错误详情进行脱敏
            if self._masking_service and self._masking_service.is_enabled():
                error_detail = self._masking_service.mask_text(error_detail)
            
            # 返回统一错误响应
            return JSONResponse(
                status_code=500,
                content={
                    "error": "内部服务器错误",
                    "detail": error_detail if logger.level <= logging.DEBUG else None,
                }
            )


def setup_cors(app) -> None:
    """
    设置CORS中间件
    
    参数:
        app: FastAPI应用实例
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_middleware(app, config: Optional[Dict[str, Any]] = None) -> None:
    """
    设置所有中间件
    
    参数:
        app: FastAPI应用实例
        config: 配置字典（可选，用于数据脱敏配置）
    """
    # CORS中间件
    setup_cors(app)
    
    # 请求日志中间件
    app.add_middleware(RequestLoggingMiddleware)
    
    # 错误处理中间件（传入脱敏配置）
    app.add_middleware(ErrorHandlingMiddleware, masking_config=config)
