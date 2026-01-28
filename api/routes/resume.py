"""
Resume路由模块

提供简历优化、生成相关的API接口。
"""

import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse, StreamingResponse

from api.dependencies import get_resume_service
from core.resume.service import ResumeService
from core.resume.models import (
    ParseResumeRequest,
    ParseResumeResponse,
    OptimizeResumeRequest,
    OptimizeResumeResponse,
    GenerateResumeRequest,
    GenerateResumeResponse,
    ListTemplatesResponse,
)

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/parse", response_model=ParseResumeResponse, status_code=status.HTTP_200_OK)
async def parse_resume(
    file: UploadFile = File(..., description="简历文件（PDF/DOCX/JSON）"),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ParseResumeResponse:
    """
    解析简历文件
    
    上传简历文件（PDF、Word或JSON格式），系统将自动解析并提取结构化数据。
    
    参数:
        file: 上传的简历文件
    
    返回:
        ParseResumeResponse: 解析结果，包含结构化的简历数据
    """
    try:
        # 保存上传的文件到临时目录
        temp_dir = Path("temp/resume")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        file_extension = file.filename.split(".")[-1].lower() if file.filename else ""
        if file_extension not in ["pdf", "docx", "json"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件格式: {file_extension}，支持的格式: pdf, docx, json"
            )
        
        temp_file_path = temp_dir / f"upload_{file.filename}"
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 创建解析请求
        request = ParseResumeRequest(
            file_name=str(temp_file_path),
            file_format=file_extension,
        )
        
        # 调用服务解析
        response = await resume_service.parse_resume(request)
        
        # 清理临时文件
        try:
            temp_file_path.unlink()
        except Exception:
            pass
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解析简历失败: {str(e)}"
        ) from e


@router.post("/optimize", response_model=OptimizeResumeResponse, status_code=status.HTTP_200_OK)
async def optimize_resume(
    request: OptimizeResumeRequest,
    resume_service: ResumeService = Depends(get_resume_service),
) -> OptimizeResumeResponse:
    """
    优化简历
    
    根据目标职位描述对简历进行智能优化，提供优化建议和评分。
    
    参数:
        request: 优化请求，包含简历数据和职位描述
    
    返回:
        OptimizeResumeResponse: 优化结果，包含优化后的简历和建议
    """
    try:
        response = await resume_service.optimize_resume(request)
        return response
    except Exception as e:
        # 记录详细错误信息
        import logging
        logger = logging.getLogger("api.routes.resume")
        logger.error(
            f"优化简历API调用失败: {type(e).__name__}: {str(e)}",
            exc_info=True,
            extra={
                "optimization_level": request.optimization_level,
                "has_job_description": bool(request.job_description),
                "has_resume_data": bool(request.resume_data),
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"优化简历失败: {str(e)}"
        ) from e


@router.post("/generate", response_model=GenerateResumeResponse, status_code=status.HTTP_200_OK)
async def generate_resume(
    request: GenerateResumeRequest,
    resume_service: ResumeService = Depends(get_resume_service),
) -> GenerateResumeResponse:
    """
    生成简历
    
    根据简历数据和选定的模板生成HTML或PDF格式的简历。
    
    参数:
        request: 生成请求，包含简历数据、模板ID和输出格式
    
    返回:
        GenerateResumeResponse: 生成结果，包含文件ID和下载URL
    """
    try:
        response = await resume_service.generate_resume(request)
        return response
    except Exception as e:
        # 记录详细错误信息
        import logging
        logger = logging.getLogger("api.routes.resume")
        logger.error(
            f"生成简历API调用失败: {type(e).__name__}: {str(e)}",
            exc_info=True,
            extra={
                "template_id": request.template_id,
                "output_format": request.output_format,
                "has_resume_data": bool(request.resume_data),
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成简历失败: {str(e)}"
        ) from e


@router.get("/templates", response_model=ListTemplatesResponse, status_code=status.HTTP_200_OK)
async def list_templates(
    resume_service: ResumeService = Depends(get_resume_service),
) -> ListTemplatesResponse:
    """
    获取所有可用模板
    
    返回系统中所有可用的简历模板列表。
    
    返回:
        ListTemplatesResponse: 模板列表
    """
    try:
        response = await resume_service.list_templates()
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模板列表失败: {str(e)}"
        ) from e


@router.get("/download/{file_id}")
async def download_resume(
    file_id: str,
    resume_service: ResumeService = Depends(get_resume_service),
):
    """
    下载生成的简历文件
    
    参数:
        file_id: 文件ID（从生成接口返回）
    
    返回:
        FileResponse: 文件下载响应
    """
    try:
        # 从输出目录查找文件
        output_dir = Path(resume_service.generator.output_dir)
        
        # 尝试查找HTML文件
        html_file = output_dir / f"{file_id}.html"
        if html_file.exists():
            return FileResponse(
                html_file,
                media_type="text/html",
                filename=f"resume_{file_id}.html",
                headers={"Content-Disposition": f'attachment; filename="resume_{file_id}.html"'},
            )
        
        # 尝试查找PDF文件
        pdf_file = output_dir / f"{file_id}.pdf"
        if pdf_file.exists():
            # 验证PDF文件是否有效（检查文件大小和PDF文件头）
            file_size = pdf_file.stat().st_size
            if file_size == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="PDF文件为空，可能生成失败"
                )
            
            # 检查PDF文件头（PDF文件应该以%PDF开头）
            with open(pdf_file, "rb") as f:
                header = f.read(4)
                if header != b"%PDF":
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="PDF文件格式无效，文件可能损坏"
                    )
            
            return FileResponse(
                pdf_file,
                media_type="application/pdf",
                filename=f"resume_{file_id}.pdf",
                headers={"Content-Disposition": f'attachment; filename="resume_{file_id}.pdf"'},
            )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文件不存在: {file_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载文件失败: {str(e)}"
        ) from e


@router.get("/preview/{file_id}")
async def preview_resume(
    file_id: str,
    resume_service: ResumeService = Depends(get_resume_service),
):
    """
    预览生成的简历文件
    
    参数:
        file_id: 文件ID（从生成接口返回）
    
    返回:
        FileResponse: 文件预览响应
    """
    try:
        # 从输出目录查找文件
        output_dir = Path(resume_service.generator.output_dir)
        
        # 尝试查找HTML文件
        html_file = output_dir / f"{file_id}.html"
        if html_file.exists():
            return FileResponse(
                html_file,
                media_type="text/html",
            )
        
        # 尝试查找PDF文件
        pdf_file = output_dir / f"{file_id}.pdf"
        if pdf_file.exists():
            return FileResponse(
                pdf_file,
                media_type="application/pdf",
            )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文件不存在: {file_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"预览文件失败: {str(e)}"
        ) from e
