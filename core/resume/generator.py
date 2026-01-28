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
            # 验证简历数据
            if not resume_data or not resume_data.personal_info:
                raise ResumeGenerateError("简历数据无效：缺少个人信息")
            
            # 记录调试信息
            self.logger.debug(
                f"生成简历: 模板={template_id}, "
                f"姓名={resume_data.personal_info.name}, "
                f"邮箱={resume_data.personal_info.email}, "
                f"教育经历数={len(resume_data.education)}, "
                f"工作经历数={len(resume_data.work_experience)}"
            )
            
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
        # 模板文件路径：{template_id}/template.html
        template_file = f"{template_id}/template.html"
        
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
            # 验证数据
            if not resume_data or not resume_data.personal_info:
                raise ResumeGenerateError("简历数据无效：缺少个人信息")
            
            # 准备模板上下文
            context = {
                "resume": resume_data,
                "personal_info": resume_data.personal_info,
                "education": resume_data.education or [],
                "work_experience": resume_data.work_experience or [],
                "project_experience": resume_data.project_experience or [],
                "skills": resume_data.skills or [],
                "certificates": resume_data.certificates or [],
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "template_id": template_id,
            }
            
            # 记录调试信息
            self.logger.debug(
                f"渲染模板上下文: 姓名={context['personal_info'].name}, "
                f"邮箱={context['personal_info'].email}"
            )
            
            # 渲染模板
            html_content = template.render(**context)
            
            # 验证渲染结果
            if not html_content or len(html_content.strip()) < 100:
                self.logger.warning(f"渲染后的HTML内容过短: {len(html_content)} 字符")
            
            # 检查是否包含模板变量（未替换）
            if "{{" in html_content or "{%" in html_content:
                self.logger.warning("渲染后的HTML仍包含模板变量，可能渲染失败")
                # 尝试重新渲染
                try:
                    html_content = template.render(**context)
                except Exception as e:
                    self.logger.error(f"重新渲染失败: {e}")
            
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
                "在Windows上，还需要安装GTK+库。\n"
                "建议：在Windows上使用HTML格式，或安装GTK+运行时库。"
            )
        
        try:
            pdf_path = Path(self.output_dir) / f"{file_id}.pdf"
            
            # 使用WeasyPrint转换
            html_doc = HTML(string=html_content, base_url=str(Path(self.template_dir).parent))
            html_doc.write_pdf(pdf_path)
            
            # 验证PDF文件是否成功生成
            if not pdf_path.exists():
                raise ResumeGenerateError("PDF文件生成失败：文件不存在")
            
            file_size = pdf_path.stat().st_size
            if file_size == 0:
                raise ResumeGenerateError("PDF文件生成失败：文件为空")
            
            # 验证PDF文件头
            with open(pdf_path, "rb") as f:
                header = f.read(4)
                if header != b"%PDF":
                    pdf_path.unlink()  # 删除损坏的文件
                    raise ResumeGenerateError("PDF文件生成失败：文件格式无效")
            
            self.logger.info(f"PDF文件已生成: {pdf_path}, 大小: {file_size} bytes")
            return str(pdf_path)
        except ResumeGenerateError:
            raise
        except Exception as e:
            self.logger.error(f"PDF转换失败: {e}", exc_info=True)
            # 如果生成了损坏的文件，尝试删除
            pdf_path = Path(self.output_dir) / f"{file_id}.pdf"
            if pdf_path.exists():
                try:
                    pdf_path.unlink()
                    self.logger.info(f"已删除损坏的PDF文件: {pdf_path}")
                except Exception:
                    pass
            raise ResumeGenerateError(f"PDF转换失败: {e}") from e
    
    async def cleanup(self) -> None:
        """清理资源"""
        # 可以在这里实现定期清理过期文件的逻辑
        await super().cleanup()
