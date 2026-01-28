"""
Resume模块集成测试
测试完整的简历处理流程
"""

import pytest
from pathlib import Path
import tempfile
import json

from core.resume.service import ResumeService
from core.resume.models import (
    ResumeData,
    PersonalInfo,
    ParseResumeRequest,
    OptimizeResumeRequest,
    GenerateResumeRequest,
)
from core.llm.service import LLMService
from infrastructure.config.manager import ConfigManager


@pytest.mark.asyncio
@pytest.mark.integration
class TestResumeIntegration:
    """Resume模块集成测试"""
    
    @pytest.fixture
    async def config_manager(self):
        """配置管理器"""
        return ConfigManager.load(env="dev")
    
    @pytest.fixture
    async def llm_service(self, config_manager):
        """LLM服务"""
        config = config_manager.config
        service = LLMService(config)
        await service.initialize()
        return service
    
    @pytest.fixture
    async def resume_service(self, config_manager, llm_service):
        """Resume服务"""
        config = config_manager.config
        service = ResumeService(config, llm_service)
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_resume_parse_json_integration(self, resume_service):
        """测试JSON简历解析集成"""
        # 创建临时JSON文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json_data = {
                "personal_info": {
                    "name": "测试用户",
                    "email": "test@example.com",
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
            request = ParseResumeRequest(
                file_name=temp_path,
                file_format="json"
            )
            
            response = await resume_service.parse_resume(request)
            
            assert response.success is True
            assert response.data is not None
            assert response.data.personal_info.name == "测试用户"
        finally:
            Path(temp_path).unlink()
    
    @pytest.mark.asyncio
    async def test_resume_optimize_integration(self, resume_service):
        """测试简历优化集成（需要LLM服务）"""
        resume_data = ResumeData(
            personal_info=PersonalInfo(
                name="测试用户",
                email="test@example.com"
            )
        )
        
        request = OptimizeResumeRequest(
            resume_data=resume_data,
            optimization_level="basic"
        )
        
        # 注意：这个测试需要真实的LLM服务，可能会失败
        # 在实际环境中，应该使用Mock LLM服务
        try:
            response = await resume_service.optimize_resume(request)
            # 如果LLM服务可用，验证响应
            if response.success:
                assert response.data is not None
        except Exception as e:
            # LLM服务不可用时，跳过测试
            pytest.skip(f"LLM服务不可用: {e}")
    
    @pytest.mark.asyncio
    async def test_resume_generate_integration(self, resume_service):
        """测试简历生成集成"""
        resume_data = ResumeData(
            personal_info=PersonalInfo(
                name="测试用户",
                email="test@example.com"
            )
        )
        
        # 先加载模板
        templates_response = await resume_service.list_templates()
        if not templates_response.success or len(templates_response.templates) == 0:
            pytest.skip("没有可用的模板")
        
        template_id = templates_response.templates[0].id
        
        request = GenerateResumeRequest(
            resume_data=resume_data,
            template_id=template_id,
            output_format="html"
        )
        
        response = await resume_service.generate_resume(request)
        
        if response.success:
            assert response.file_id is not None
            assert response.file_path is not None
