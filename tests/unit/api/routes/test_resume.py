"""
测试模块：Resume API路由测试
功能描述：测试Resume路由的所有功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from api.fastapi_app import app
from api.dependencies import get_resume_service
from core.resume.service import ResumeService
from core.resume.models import (
    ResumeData,
    PersonalInfo,
    ParseResumeResponse,
    OptimizeResumeResponse,
    GenerateResumeResponse,
    ListTemplatesResponse,
    TemplateInfo,
)
import tempfile
from pathlib import Path


@pytest.fixture
def mock_resume_service():
    """创建Mock Resume服务"""
    service = MagicMock(spec=ResumeService)
    
    # Mock parse_resume
    parse_response = ParseResumeResponse(
        success=True,
        message="解析成功",
        data=ResumeData(
            personal_info=PersonalInfo(
                name="张三",
                email="zhangsan@example.com"
            )
        ),
        parse_time=2.5,
    )
    service.parse_resume = AsyncMock(return_value=parse_response)
    
    # Mock optimize_resume
    from core.resume.models import OptimizationResult
    optimize_response = OptimizeResumeResponse(
        success=True,
        message="优化成功",
        data=OptimizationResult(
            optimized_resume=ResumeData(
                personal_info=PersonalInfo(name="张三", email="zhangsan@example.com")
            ),
            optimization_level="basic"
        ),
        optimization_time=5.2,
    )
    service.optimize_resume = AsyncMock(return_value=optimize_response)
    
    # Mock generate_resume
    generate_response = GenerateResumeResponse(
        success=True,
        message="生成成功",
        file_id="resume_123",
        file_path="/output/resume_123.html",
        download_url="/api/v1/resume/download/resume_123",
        preview_url="/api/v1/resume/preview/resume_123",
        generation_time=3.8,
    )
    service.generate_resume = AsyncMock(return_value=generate_response)
    
    # Mock list_templates
    list_response = ListTemplatesResponse(
        success=True,
        message="获取模板列表成功",
        templates=[
            TemplateInfo(
                id="classic",
                name="经典模板",
                description="经典简历模板",
                category="经典",
                file_path="/templates/classic/template.html",
                supported_sections=[]
            )
        ],
    )
    service.list_templates = AsyncMock(return_value=list_response)
    
    # Mock generator for download/preview
    service.generator = MagicMock()
    service.generator.output_dir = "output/resume"
    
    return service


@pytest.fixture
def client(mock_resume_service):
    """创建测试客户端"""
    app.dependency_overrides[get_resume_service] = lambda: mock_resume_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestResumeParse:
    """测试解析简历接口"""
    
    def test_parse_resume_success(self, client, mock_resume_service):
        """测试解析简历成功"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"fake pdf content")
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/api/v1/resume/parse",
                    files={"file": ("test.pdf", file, "application/pdf")}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"] is not None
            assert data["data"]["personal_info"]["name"] == "张三"
        finally:
            Path(temp_path).unlink()
    
    def test_parse_resume_invalid_format(self, client):
        """测试无效的文件格式"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"test content")
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/api/v1/resume/parse",
                    files={"file": ("test.txt", file, "text/plain")}
                )
            
            assert response.status_code == 400
        finally:
            Path(temp_path).unlink()


class TestResumeOptimize:
    """测试优化简历接口"""
    
    def test_optimize_resume_success(self, client, mock_resume_service):
        """测试优化简历成功"""
        request_data = {
            "resume_data": {
                "personal_info": {
                    "name": "张三",
                    "email": "zhangsan@example.com"
                },
                "education": [],
                "work_experience": [],
                "project_experience": [],
                "skills": [],
                "certificates": []
            },
            "optimization_level": "basic"
        }
        
        response = client.post("/api/v1/resume/optimize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] is not None


class TestResumeGenerate:
    """测试生成简历接口"""
    
    def test_generate_resume_success(self, client, mock_resume_service):
        """测试生成简历成功"""
        request_data = {
            "resume_data": {
                "personal_info": {
                    "name": "张三",
                    "email": "zhangsan@example.com"
                },
                "education": [],
                "work_experience": [],
                "project_experience": [],
                "skills": [],
                "certificates": []
            },
            "template_id": "classic",
            "output_format": "html"
        }
        
        response = client.post("/api/v1/resume/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["file_id"] == "resume_123"


class TestResumeTemplates:
    """测试模板列表接口"""
    
    def test_list_templates_success(self, client, mock_resume_service):
        """测试获取模板列表成功"""
        response = client.get("/api/v1/resume/templates")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["templates"]) > 0
        assert data["templates"][0]["id"] == "classic"


class TestResumeDownload:
    """测试下载简历接口"""
    
    def test_download_resume_not_found(self, client, mock_resume_service):
        """测试文件不存在"""
        response = client.get("/api/v1/resume/download/nonexistent")
        
        assert response.status_code == 404
