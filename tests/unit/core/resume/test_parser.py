"""
ResumeParser单元测试
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.resume.parser import ResumeParser, ResumeParseError
from core.resume.models import ResumeData, PersonalInfo


class TestResumeParser:
    """测试ResumeParser"""
    
    @pytest.fixture
    def parser_config(self):
        """解析器配置"""
        return {
            "resume": {
                "max_file_size": 10 * 1024 * 1024,  # 10MB
            }
        }
    
    @pytest.fixture
    def parser(self, parser_config):
        """创建ResumeParser实例"""
        return ResumeParser(parser_config)
    
    def test_init(self, parser_config):
        """测试初始化"""
        parser = ResumeParser(parser_config)
        assert parser.max_file_size == 10 * 1024 * 1024
        assert "pdf" in parser.supported_formats
        assert "docx" in parser.supported_formats
        assert "json" in parser.supported_formats
    
    @pytest.mark.asyncio
    async def test_parse_unsupported_format(self, parser):
        """测试解析不支持的文件格式"""
        with pytest.raises(ResumeParseError) as exc_info:
            await parser.parse("/path/to/file.txt", "txt")
        assert "不支持的文件格式" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_parse_nonexistent_file(self, parser):
        """测试解析不存在的文件"""
        with pytest.raises(ResumeParseError) as exc_info:
            await parser.parse("/nonexistent/file.pdf", "pdf")
        assert "文件不存在" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_parse_json_valid(self, parser):
        """测试解析有效的JSON文件"""
        # 创建临时JSON文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json_data = {
                "personal_info": {
                    "name": "张三",
                    "email": "zhangsan@example.com",
                    "phone": "13800138000"
                },
                "education": [],
                "work_experience": [],
                "project_experience": [],
                "skills": [],
                "certificates": []
            }
            json.dump(json_data, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            result = await parser.parse(temp_path, "json")
            assert isinstance(result, ResumeData)
            assert result.personal_info.name == "张三"
            assert result.personal_info.email == "zhangsan@example.com"
        finally:
            Path(temp_path).unlink()
    
    @pytest.mark.asyncio
    async def test_parse_json_invalid(self, parser):
        """测试解析无效的JSON文件"""
        # 创建临时无效JSON文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            with pytest.raises(ResumeParseError) as exc_info:
                await parser.parse(temp_path, "json")
            assert "JSON格式错误" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()
    
    @pytest.mark.asyncio
    @patch('core.resume.parser.pdfplumber')
    async def test_parse_pdf_success(self, mock_pdfplumber, parser):
        """测试解析PDF文件成功"""
        # Mock pdfplumber
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        张三
        zhangsan@example.com
        13800138000
        北京
        
        教育
        清华大学 本科 计算机科学与技术 2015-09 2019-06
        
        工作
        某科技公司 高级Python工程师 2019-07 至今
        """
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        
        result = await parser.parse("/path/to/resume.pdf", "pdf")
        assert isinstance(result, ResumeData)
        assert result.personal_info.name == "张三"
        assert result.personal_info.email == "zhangsan@example.com"
    
    @pytest.mark.asyncio
    @patch('core.resume.parser.pdfplumber', None)
    async def test_parse_pdf_no_pdfplumber(self, parser):
        """测试解析PDF但未安装pdfplumber"""
        with pytest.raises(ResumeParseError) as exc_info:
            await parser.parse("/path/to/resume.pdf", "pdf")
        assert "pdfplumber未安装" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('core.resume.parser.Document')
    async def test_parse_docx_success(self, mock_document, parser):
        """测试解析Word文件成功"""
        # Mock Document
        mock_doc = MagicMock()
        mock_paragraph = MagicMock()
        mock_paragraph.text = """
        张三
        zhangsan@example.com
        13800138000
        北京
        
        教育
        清华大学 本科 计算机科学与技术 2015-09 2019-06
        """
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = []
        mock_document.return_value = mock_doc
        
        result = await parser.parse("/path/to/resume.docx", "docx")
        assert isinstance(result, ResumeData)
        assert result.personal_info.name == "张三"
    
    @pytest.mark.asyncio
    @patch('core.resume.parser.Document', None)
    async def test_parse_docx_no_python_docx(self, parser):
        """测试解析Word但未安装python-docx"""
        with pytest.raises(ResumeParseError) as exc_info:
            await parser.parse("/path/to/resume.docx", "docx")
        assert "python-docx未安装" in str(exc_info.value)
    
    def test_extract_personal_info(self, parser):
        """测试提取个人信息"""
        text = """
        张三
        zhangsan@example.com
        13800138000
        北京
        https://github.com/zhangsan
        """
        info = parser._extract_personal_info(text)
        assert info.name == "张三"
        assert info.email == "zhangsan@example.com"
        assert info.phone == "13800138000"
        assert info.location == "北京"
        assert "github.com" in (info.github or "")
    
    def test_extract_education(self, parser):
        """测试提取教育经历"""
        text = """
        教育
        清华大学 本科 计算机科学与技术 2015-09 2019-06
        北京大学 硕士 软件工程 2019-09 2022-06
        """
        education_list = parser._extract_education(text)
        assert len(education_list) > 0
        assert any("清华" in edu.school for edu in education_list)
    
    def test_extract_work_experience(self, parser):
        """测试提取工作经历"""
        text = """
        工作
        某科技公司 高级Python工程师 2019-07 至今
        另一公司 软件工程师 2017-07 2019-06
        """
        work_list = parser._extract_work_experience(text)
        assert len(work_list) > 0
        assert any("科技" in work.company for work in work_list)
    
    def test_extract_skills(self, parser):
        """测试提取技能"""
        text = """
        技能
        Python, JavaScript, React, Vue, FastAPI, MySQL, Redis, Docker
        """
        skills_list = parser._extract_skills(text)
        assert len(skills_list) > 0
        assert any("Python" in skill.items for skill in skills_list)
