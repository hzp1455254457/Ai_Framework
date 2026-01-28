"""
ResumeGenerator单元测试
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import shutil

from core.resume.generator import ResumeGenerator, ResumeGenerateError
from core.resume.models import ResumeData, PersonalInfo


class TestResumeGenerator:
    """测试ResumeGenerator"""
    
    @pytest.fixture
    def generator_config(self):
        """生成器配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_dir = Path(tmpdir) / "templates"
            output_dir = Path(tmpdir) / "output"
            template_dir.mkdir()
            output_dir.mkdir()
            
            # 创建测试模板
            template_file = template_dir / "test.html"
            template_file.write_text("""
            <html>
            <body>
                <h1>{{ resume.personal_info.name }}</h1>
                <p>{{ resume.personal_info.email }}</p>
            </body>
            </html>
            """)
            
            yield {
                "resume": {
                    "template_dir": str(template_dir),
                    "output_dir": str(output_dir),
                }
            }
    
    @pytest.fixture
    def generator(self, generator_config):
        """创建ResumeGenerator实例"""
        return ResumeGenerator(generator_config)
    
    @pytest.fixture
    def sample_resume_data(self):
        """示例简历数据"""
        return ResumeData(
            personal_info=PersonalInfo(
                name="张三",
                email="zhangsan@example.com"
            )
        )
    
    @pytest.mark.asyncio
    async def test_init(self, generator_config):
        """测试初始化"""
        generator = ResumeGenerator(generator_config)
        assert generator.template_dir == generator_config["resume"]["template_dir"]
        assert generator.output_dir == generator_config["resume"]["output_dir"]
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, generator):
        """测试初始化成功"""
        await generator.initialize()
        assert generator._initialized is True
        assert generator.jinja_env is not None
    
    @pytest.mark.asyncio
    async def test_initialize_no_jinja2(self, generator_config):
        """测试Jinja2未安装"""
        with patch('core.resume.generator.Environment', None):
            generator = ResumeGenerator(generator_config)
            with pytest.raises(ResumeGenerateError) as exc_info:
                await generator.initialize()
            assert "Jinja2未安装" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_html_success(self, generator, sample_resume_data):
        """测试生成HTML成功"""
        await generator.initialize()
        
        result = await generator.generate(sample_resume_data, "test", "html")
        
        assert result["success"] is True
        assert result["file_id"] is not None
        assert result["format"] == "html"
        assert Path(result["file_path"]).exists()
    
    @pytest.mark.asyncio
    async def test_generate_template_not_found(self, generator, sample_resume_data):
        """测试模板不存在"""
        await generator.initialize()
        
        with pytest.raises(ResumeGenerateError) as exc_info:
            await generator.generate(sample_resume_data, "nonexistent", "html")
        assert "加载模板失败" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_pdf_no_weasyprint(self, generator, sample_resume_data):
        """测试WeasyPrint未安装"""
        await generator.initialize()
        
        with patch('core.resume.generator.HTML', None):
            with pytest.raises(ResumeGenerateError) as exc_info:
                await generator.generate(sample_resume_data, "test", "pdf")
            assert "WeasyPrint未安装" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_invalid_format(self, generator, sample_resume_data):
        """测试无效的输出格式"""
        await generator.initialize()
        
        with pytest.raises(ResumeGenerateError) as exc_info:
            await generator.generate(sample_resume_data, "test", "docx")
        assert "不支持的输出格式" in str(exc_info.value)
