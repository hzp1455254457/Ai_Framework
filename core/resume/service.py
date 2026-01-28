"""
Resume模块 - 简历服务主类

提供统一的简历处理接口，协调Parser、Optimizer、Generator、Template等子模块。
"""

from typing import Dict, Any, Optional, List
from core.base.service import BaseService
from core.llm.service import LLMService
from core.resume.parser import ResumeParser
from core.resume.optimizer import ResumeOptimizer
from core.resume.generator import ResumeGenerator
from core.resume.templates import ResumeTemplate
from core.resume.models import (
    ResumeData,
    OptimizationResult,
    TemplateInfo,
    ParseResumeRequest,
    ParseResumeResponse,
    OptimizeResumeRequest,
    OptimizeResumeResponse,
    GenerateResumeRequest,
    GenerateResumeResponse,
    ListTemplatesResponse,
)


class ResumeService(BaseService):
    """
    简历服务主类
    
    提供统一的简历处理接口，包括：
    - 简历解析
    - 简历优化
    - 简历生成
    - 模板管理
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        llm_service: Optional[LLMService] = None
    ) -> None:
        """
        初始化简历服务
        
        参数:
            config: 配置字典
            llm_service: LLM服务实例（可选，如果提供则用于优化功能）
        """
        super().__init__(config)
        self.llm_service = llm_service
        
        # 初始化子模块
        self.parser = ResumeParser(config)
        self.optimizer = ResumeOptimizer(config, llm_service) if llm_service else None
        self.generator = ResumeGenerator(config)
        self.template_manager = ResumeTemplate(config)
    
    async def initialize(self) -> None:
        """初始化所有子模块"""
        await super().initialize()
        
        # 初始化子模块
        await self.parser.initialize()
        await self.generator.initialize()
        await self.template_manager.initialize()
        
        self.logger.info("ResumeService初始化完成")
    
    async def parse_resume(self, request: ParseResumeRequest) -> ParseResumeResponse:
        """
        解析简历文件
        
        参数:
            request: 解析请求
        
        返回:
            ParseResumeResponse: 解析响应
        """
        import time
        start_time = time.time()
        
        try:
            resume_data = await self.parser.parse(request.file_name, request.file_format)
            parse_time = time.time() - start_time
            
            return ParseResumeResponse(
                success=True,
                message="解析成功",
                data=resume_data,
                parse_time=parse_time,
            )
        except Exception as e:
            self.logger.error(f"解析简历失败: {e}", exc_info=True)
            parse_time = time.time() - start_time
            return ParseResumeResponse(
                success=False,
                message=f"解析失败: {str(e)}",
                data=None,
                parse_time=parse_time,
            )
    
    async def optimize_resume(self, request: OptimizeResumeRequest) -> OptimizeResumeResponse:
        """
        优化简历
        
        参数:
            request: 优化请求
        
        返回:
            OptimizeResumeResponse: 优化响应
        """
        if not self.optimizer:
            return OptimizeResumeResponse(
                success=False,
                message="优化功能不可用：LLM服务未配置",
                data=None,
                optimization_time=0.0,
            )
        
        import time
        start_time = time.time()
        
        try:
            result = await self.optimizer.optimize(
                request.resume_data,
                request.job_description,
                request.optimization_level,
            )
            optimization_time = time.time() - start_time
            
            return OptimizeResumeResponse(
                success=True,
                message="优化成功",
                data=result,
                optimization_time=optimization_time,
            )
        except Exception as e:
            optimization_time = time.time() - start_time
            error_type = type(e).__name__
            error_msg = str(e)
            
            self.logger.error(
                f"优化简历失败: {error_type}: {error_msg}",
                exc_info=True,
                extra={
                    "optimization_level": request.optimization_level,
                    "has_job_description": bool(request.job_description),
                    "optimization_time": optimization_time,
                    "resume_name": request.resume_data.personal_info.name if request.resume_data.personal_info else "未知",
                }
            )
            
            return OptimizeResumeResponse(
                success=False,
                message=f"优化失败: {error_msg}",
                data=None,
                optimization_time=optimization_time,
            )
    
    async def generate_resume(self, request: GenerateResumeRequest) -> GenerateResumeResponse:
        """
        生成简历
        
        参数:
            request: 生成请求
        
        返回:
            GenerateResumeResponse: 生成响应
        """
        import time
        start_time = time.time()
        
        try:
            result = await self.generator.generate(
                request.resume_data,
                request.template_id,
                request.output_format,
            )
            generation_time = time.time() - start_time
            
            return GenerateResumeResponse(
                success=True,
                message="生成成功",
                file_id=result["file_id"],
                file_path=result["file_path"],
                download_url=result["download_url"],
                preview_url=result["preview_url"],
                generation_time=generation_time,
            )
        except Exception as e:
            self.logger.error(f"生成简历失败: {e}", exc_info=True)
            generation_time = time.time() - start_time
            return GenerateResumeResponse(
                success=False,
                message=f"生成失败: {str(e)}",
                file_id=None,
                file_path=None,
                download_url=None,
                preview_url=None,
                generation_time=generation_time,
            )
    
    async def list_templates(self) -> ListTemplatesResponse:
        """
        获取所有可用模板
        
        返回:
            ListTemplatesResponse: 模板列表响应
        """
        try:
            templates = self.template_manager.get_all_templates()
            return ListTemplatesResponse(
                success=True,
                message="获取模板列表成功",
                templates=templates,
            )
        except Exception as e:
            self.logger.error(f"获取模板列表失败: {e}", exc_info=True)
            return ListTemplatesResponse(
                success=False,
                message=f"获取模板列表失败: {str(e)}",
                templates=[],
            )
    
    async def cleanup(self) -> None:
        """清理资源"""
        await self.parser.cleanup()
        await self.generator.cleanup()
        await self.template_manager.cleanup()
        await super().cleanup()
