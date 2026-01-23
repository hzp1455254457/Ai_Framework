"""
API路由模块

提供所有API路由定义。
"""

from fastapi import APIRouter

# 创建主路由
router = APIRouter()

# 导入各个路由模块
from .llm import router as llm_router
from .health import router as health_router
from .agent import router as agent_router
from .vision import router as vision_router

# 注册路由
router.include_router(llm_router, prefix="/llm", tags=["LLM"])
router.include_router(health_router, prefix="/health", tags=["Health"])
router.include_router(agent_router, prefix="/agent", tags=["Agent"])
router.include_router(vision_router, prefix="/vision", tags=["Vision"])

__all__ = ["router"]
