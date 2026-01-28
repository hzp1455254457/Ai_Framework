"""
ResumeService单元测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.resume.service import ResumeService
from core.resume.models import (
    ResumeData,
    PersonalInfo,
    ParseResumeRequest,
    OptimizeResumeRequest,
    GenerateResumeRequest,
)


class TestResumeService:
    """测试ResumeService"""
    
    @pytest.fixture
    def service_config(self):
        """服务配置"""
        return {
            "resume": {
                "template_dir": "templates/resume",
                "output_dir": "output/resume",
            }
        }
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLMService"""
        return MagicMock()
    
    @pytest.fixture
    def service(self, service_config, mock_llm_service):
        """创建ResumeService实例"""
        return ResumeService(service_config, mock_llm_service)
    
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
    async def test_init(self, service_config, mock_llm_service):
        """测试初始化"""
        service = ResumeService(service_config, mock_llm_service)
        assert service.llm_service == mock_llm_service
        assert service.parser is not None
        assert service.generator is not None
        assert service.template_manager is not None
    
    @pytest.mark.asyncio
    async def test_parse_resume_success(self, service, sample_resume_data):
        """测试解析简历成功"""
        # Mock parser
        service.parser.parse = AsyncMock(return_value=sample_resume_data)
        
        request = ParseResumeRequest(
            file_name="test.pdf",
            file_format="pdf"
        )
        
        response = await service.parse_resume(request)
        
        assert response.success is True
        assert response.data == sample_resume_data
        assert response.parse_time > 0
    
    @pytest.mark.asyncio
    async def test_parse_resume_failure(self, service):
        """测试解析简历失败"""
        # Mock parser抛出异常
        service.parser.parse = AsyncMock(side_effect=Exception("解析失败"))
        
        request = ParseResumeRequest(
            file_name="test.pdf",
            file_format="pdf"
        )
        
        response = await service.parse_resume(request)
        
        assert response.success is False
        assert "解析失败" in response.message
    
    @pytest.mark.asyncio
    async def test_optimize_resume_success(self, service, sample_resume_data):
        """测试优化简历成功"""
        from core.resume.models import OptimizationResult
        
        # Mock optimizer
        optimization_result = OptimizationResult(
            optimized_resume=sample_resume_data,
            optimization_level="basic"
        )
        service.optimizer.optimize = AsyncMock(return_value=optimization_result)
        
        request = OptimizeResumeRequest(
            resume_data=sample_resume_data,
            optimization_level="basic"
        )
        
        response = await service.optimize_resume(request)
        
        assert response.success is True
        assert response.data == optimization_result
    
    @pytest.mark.asyncio
    async def test_optimize_resume_no_llm_service(self, service_config):
        """测试优化功能不可用（无LLM服务）"""
        service = ResumeService(service_config, None)
        
        request = OptimizeResumeRequest(
            resume_data=ResumeData(
                personal_info=PersonalInfo(name="张三", email="test@example.com")
            )
        )
        
        response = await service.optimize_resume(request)
        
        assert response.success is False
        assert "优化功能不可用" in response.message
    
    @pytest.mark.asyncio
    async def test_generate_resume_success(self, service, sample_resume_data):
        """测试生成简历成功"""
        # Mock generator
        service.generator.generate = AsyncMock(return_value={
            "file_id": "test_123",
            "file_path": "/path/to/resume.html",
            "download_url": "/api/v1/resume/download/test_123",
            "preview_url": "/api/v1/resume/preview/test_123",
            "format": "html",
        })
        
        request = GenerateResumeRequest(
            resume_data=sample_resume_data,
            template_id="classic"
        )
        
        response = await service.generate_resume(request)
        
        assert response.success is True
        assert response.file_id == "test_123"
    
    @pytest.mark.asyncio
    async def test_list_templates_success(self, service):
        """测试获取模板列表成功"""
        from core.resume.models import TemplateInfo
        
        # Mock template manager
        templates = [
            TemplateInfo(
                id="classic",
                name="经典模板",
                description="经典简历模板",
                category="经典",
                file_path="/templates/classic/template.html",
                supported_sections=[]
            )
        ]
        service.template_manager.get_all_templates = lambda: templates
        
        response = await service.list_templates()
        
        assert response.success is True
        assert len(response.templates) == 1
        assert response.templates[0].id == "classic"
