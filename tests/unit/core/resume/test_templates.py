"""
ResumeTemplate单元测试
"""

import pytest
from pathlib import Path
from unittest.mock import patch
import tempfile
import json

from core.resume.templates import ResumeTemplate, ResumeTemplateError
from core.resume.models import TemplateInfo


class TestResumeTemplate:
    """测试ResumeTemplate"""
    
    @pytest.fixture
    def template_config(self):
        """模板配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_dir = Path(tmpdir) / "templates"
            template_dir.mkdir()
            
            # 创建测试模板
            test_template_dir = template_dir / "test"
            test_template_dir.mkdir()
            
            metadata = {
                "name": "测试模板",
                "description": "测试用模板",
                "category": "测试",
                "supported_sections": ["personal_info", "education"]
            }
            
            with open(test_template_dir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False)
            
            with open(test_template_dir / "template.html", "w", encoding="utf-8") as f:
                f.write("<html><body>Test Template</body></html>")
            
            yield {
                "resume": {
                    "template_dir": str(template_dir),
                }
            }
    
    @pytest.fixture
    def template(self, template_config):
        """创建ResumeTemplate实例"""
        return ResumeTemplate(template_config)
    
    @pytest.mark.asyncio
    async def test_init(self, template_config):
        """测试初始化"""
        template = ResumeTemplate(template_config)
        assert template.template_dir == template_config["resume"]["template_dir"]
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, template):
        """测试初始化成功"""
        await template.initialize()
        assert template._initialized is True
        assert len(template._templates) > 0
    
    @pytest.mark.asyncio
    async def test_get_all_templates(self, template):
        """测试获取所有模板"""
        await template.initialize()
        templates = template.get_all_templates()
        assert len(templates) > 0
        assert all(isinstance(t, TemplateInfo) for t in templates)
    
    @pytest.mark.asyncio
    async def test_get_template_success(self, template):
        """测试获取指定模板"""
        await template.initialize()
        template_info = template.get_template("test")
        assert template_info is not None
        assert template_info.id == "test"
    
    @pytest.mark.asyncio
    async def test_get_template_not_found(self, template):
        """测试获取不存在的模板"""
        await template.initialize()
        template_info = template.get_template("nonexistent")
        assert template_info is None
    
    @pytest.mark.asyncio
    async def test_get_template_path(self, template):
        """测试获取模板路径"""
        await template.initialize()
        path = template.get_template_path("test")
        assert path is not None
        assert Path(path).exists()
