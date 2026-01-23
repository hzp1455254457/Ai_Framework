"""
Vision路由模块

提供Vision服务相关的API接口。
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from api.models.request import (
    VisionGenerateRequest,
    VisionAnalyzeRequest,
    VisionEditRequest,
)
from api.models.response import (
    VisionGenerateResponse,
    VisionAnalyzeResponse,
    VisionEditResponse,
)
from api.dependencies import get_vision_service
from core.vision.service import VisionService
from core.vision.models import (
    ImageGenerateRequest,
    ImageGenerateResponse,
    ImageAnalyzeRequest,
    ImageAnalyzeResponse,
    ImageEditRequest,
    ImageEditResponse,
)

router = APIRouter()


@router.post("/generate", response_model=VisionGenerateResponse)
async def generate_image(
    request: VisionGenerateRequest,
    vision_service: VisionService = Depends(get_vision_service),
) -> VisionGenerateResponse:
    """
    图像生成接口
    
    根据文本提示词生成图像。
    
    参数:
        request: 图像生成请求，包含提示词、尺寸等参数
        vision_service: Vision服务实例（依赖注入）
    
    返回:
        图像生成响应，包含生成的图像URL列表
    
    异常:
        HTTPException: 请求失败时抛出
    """
    try:
        # 转换请求模型
        vision_request = ImageGenerateRequest(
            prompt=request.prompt,
            size=request.size,
            n=request.n,
            quality=request.quality,
            style=request.style,
        )
        
        # 调用Vision服务
        response = await vision_service.generate_image(
            vision_request,
            adapter_name=request.adapter_name,
        )
        
        # 构建响应
        return VisionGenerateResponse(
            images=response.images,
            model=response.model,
            count=response.count,
            created_at=response.created_at.isoformat(),
            metadata=response.metadata,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        error_msg = str(e)
        # 检查是否是适配器未注册的错误
        if "没有注册的适配器" in error_msg or "适配器不存在" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vision服务暂不可用：未配置适配器。请检查后端配置或联系管理员。",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图像生成失败: {error_msg}",
        ) from e


@router.post("/analyze", response_model=VisionAnalyzeResponse)
async def analyze_image(
    request: VisionAnalyzeRequest,
    vision_service: VisionService = Depends(get_vision_service),
) -> VisionAnalyzeResponse:
    """
    图像分析接口
    
    分析图像内容（OCR、物体识别、图像理解等）。
    
    参数:
        request: 图像分析请求，包含图像数据和分析类型
        vision_service: Vision服务实例（依赖注入）
    
    返回:
        图像分析响应，包含分析结果
    
    异常:
        HTTPException: 请求失败时抛出
    """
    try:
        # 转换请求模型
        vision_request = ImageAnalyzeRequest(
            image=request.image,
            analyze_type=request.analyze_type,
            options=request.options,
        )
        
        # 调用Vision服务
        response = await vision_service.analyze_image(
            vision_request,
            adapter_name=request.adapter_name,
        )
        
        # 构建响应
        return VisionAnalyzeResponse(
            model=response.model,
            text=response.text,
            objects=response.objects,
            description=response.description,
            created_at=response.created_at.isoformat(),
            metadata=response.metadata,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图像分析失败: {str(e)}",
        ) from e


@router.post("/edit", response_model=VisionEditResponse)
async def edit_image(
    request: VisionEditRequest,
    vision_service: VisionService = Depends(get_vision_service),
) -> VisionEditResponse:
    """
    图像编辑接口
    
    根据编辑指令修改图像。
    
    参数:
        request: 图像编辑请求，包含原始图像和编辑提示词
        vision_service: Vision服务实例（依赖注入）
    
    返回:
        图像编辑响应，包含编辑后的图像URL列表
    
    异常:
        HTTPException: 请求失败时抛出
    """
    try:
        # 转换请求模型
        vision_request = ImageEditRequest(
            image=request.image,
            prompt=request.prompt,
            mask=request.mask,
            size=request.size,
            n=request.n,
        )
        
        # 调用Vision服务
        response = await vision_service.edit_image(
            vision_request,
            adapter_name=request.adapter_name,
        )
        
        # 构建响应
        return VisionEditResponse(
            images=response.images,
            model=response.model,
            count=response.count,
            created_at=response.created_at.isoformat(),
            metadata=response.metadata,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图像编辑失败: {str(e)}",
        ) from e
