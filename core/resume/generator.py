"""
Resume模块 - 简历生成器

基于Jinja2模板引擎生成HTML格式的简历，并支持转换为PDF。
"""

import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError:
    Environment = None
    FileSystemLoader = None
    Template = None

# WeasyPrint是可选的，在Windows上可能需要GTK+库
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    # ImportError: 模块未安装
    # OSError: 模块已安装但缺少系统依赖（如GTK+）
    HTML = None
    CSS = None
    WEASYPRINT_AVAILABLE = False

from core.base.service import BaseService
from core.resume.models import ResumeData


class ResumeGenerateError(Exception):
    """简历生成错误"""
    pass


class ResumeGenerator(BaseService):
    """
    简历生成器
    
    基于Jinja2模板引擎生成HTML格式的简历，并支持使用WeasyPrint转换为PDF。
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        初始化生成器
        
        参数:
            config: 配置字典
        """
        super().__init__(config)
        resume_config = config.get("resume", {})
        self.template_dir = resume_config.get("template_dir", "templates/resume")
        self.output_dir = resume_config.get("output_dir", "output/resume")
        self.jinja_env: Optional[Environment] = None
        
        # 确保输出目录存在
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    async def initialize(self) -> None:
        """初始化Jinja2环境"""
        await super().initialize()
        
        if Environment is None:
            raise ResumeGenerateError("Jinja2未安装，请先安装: pip install Jinja2")
        
        # 创建Jinja2环境
        template_path = Path(self.template_dir)
        if not template_path.exists():
            self.logger.warning(f"模板目录不存在: {self.template_dir}，将使用默认模板")
            template_path = Path(__file__).parent / "templates"
            template_path.mkdir(exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        self.logger.info(f"ResumeGenerator初始化完成，模板目录: {template_path}")
    
    async def generate(
        self,
        resume_data: ResumeData,
        template_id: str,
        output_format: str = "html"
    ) -> Dict[str, Any]:
        """
        生成简历
        
        参数:
            resume_data: 简历数据
            template_id: 模板ID
            output_format: 输出格式（html/pdf）
        
        返回:
            Dict包含生成的文件信息（file_id, file_path, download_url等）
        
        异常:
            ResumeGenerateError: 生成失败时抛出
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # 加载模板
            template = await self._load_template(template_id)
            
            # 渲染模板
            html_content = await self._render_template(template, resume_data, template_id)
            
            # 生成文件ID
            file_id = str(uuid.uuid4())
            
            if output_format == "html":
                # 保存HTML文件
                file_path = await self._save_html(html_content, file_id)
                return {
                    "file_id": file_id,
                    "file_path": file_path,
                    "download_url": f"/api/v1/resume/download/{file_id}",
                    "preview_url": f"/api/v1/resume/preview/{file_id}",
                    "format": "html",
                }
            elif output_format == "pdf":
                # 转换为PDF
                file_path = await self._convert_to_pdf(html_content, file_id)
                return {
                    "file_id": file_id,
                    "file_path": file_path,
                    "download_url": f"/api/v1/resume/download/{file_id}",
                    "preview_url": f"/api/v1/resume/preview/{file_id}",
                    "format": "pdf",
                }
            else:
                raise ResumeGenerateError(f"不支持的输出格式: {output_format}")
        except Exception as e:
            self.logger.error(f"生成简历失败: {e}", exc_info=True)
            raise ResumeGenerateError(f"生成简历失败: {e}") from e
    
    async def _load_template(self, template_id: str) -> Template:
        """
        加载模板
        
        参数:
            template_id: 模板ID
        
        返回:
            Template: Jinja2模板对象
        """
        template_file = f"{template_id}.html"
        
        try:
            template = self.jinja_env.get_template(template_file)
            return template
        except Exception as e:
            self.logger.error(f"加载模板失败: {template_file}, 错误: {e}")
            raise ResumeGenerateError(f"加载模板失败: {template_id}") from e
    
    async def _render_template(
        self,
        template: Template,
        resume_data: ResumeData,
        template_id: str
    ) -> str:
        """
        渲染模板
        
        参数:
            template: Jinja2模板对象
            resume_data: 简历数据
            template_id: 模板ID
        
        返回:
            str: 渲染后的HTML内容
        """
        try:
            # 准备模板上下文
            context = {
                "resume": resume_data,
                "personal_info": resume_data.personal_info,
                "education": resume_data.education,
                "work_experience": resume_data.work_experience,
                "project_experience": resume_data.project_experience,
                "skills": resume_data.skills,
                "certificates": resume_data.certificates,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "template_id": template_id,
            }
            
            # 渲染模板
            html_content = template.render(**context)
            return html_content
        except Exception as e:
            self.logger.error(f"渲染模板失败: {e}", exc_info=True)
            raise ResumeGenerateError(f"渲染模板失败: {e}") from e
    
    async def _save_html(self, html_content: str, file_id: str) -> str:
        """
        保存HTML文件
        
        参数:
            html_content: HTML内容
            file_id: 文件ID
        
        返回:
            str: 文件路径
        """
        file_path = Path(self.output_dir) / f"{file_id}.html"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        self.logger.info(f"HTML文件已保存: {file_path}")
        return str(file_path)
    
    async def _convert_to_pdf(self, html_content: str, file_id: str) -> str:
        """
        将HTML转换为PDF
        
        参数:
            html_content: HTML内容
            file_id: 文件ID
        
        返回:
            str: PDF文件路径
        """
        if not WEASYPRINT_AVAILABLE or HTML is None:
            raise ResumeGenerateError(
                "WeasyPrint不可用。请先安装: pip install WeasyPrint\n"
                "在Windows上，还需要安装GTK+库。"
            )
        
        try:
            pdf_path = Path(self.output_dir) / f"{file_id}.pdf"
            
            # 使用WeasyPrint转换
            html_doc = HTML(string=html_content)
            html_doc.write_pdf(pdf_path)
            
            self.logger.info(f"PDF文件已生成: {pdf_path}")
            return str(pdf_path)
        except Exception as e:
            self.logger.error(f"PDF转换失败: {e}", exc_info=True)
            raise ResumeGenerateError(f"PDF转换失败: {e}") from e
    
    async def cleanup(self) -> None:
        """清理资源"""
        # 可以在这里实现定期清理过期文件的逻辑
        await super().cleanup()
