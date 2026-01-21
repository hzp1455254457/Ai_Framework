"""
FastAPI应用主文件

提供FastAPI应用的初始化、配置和路由注册。
"""

from fastapi import FastAPI
from api.middleware import setup_middleware
from api.routes import router

# 创建FastAPI应用
app = FastAPI(
    title="AI框架API",
    description="个人AI应用框架的HTTP API接口",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 设置中间件
setup_middleware(app)

# 注册路由
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI框架API",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
