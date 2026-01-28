"""
Resume模块数据模型单元测试
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from core.resume.models import (
    PersonalInfo,
    Education,
    WorkExperience,
    ProjectExperience,
    Skill,
    Certificate,
    ResumeData,
    OptimizationSuggestion,
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


class TestPersonalInfo:
    """测试PersonalInfo模型"""
    
    def test_create_personal_info_with_required_fields(self):
        """测试创建PersonalInfo（仅必填字段）"""
        info = PersonalInfo(
            name="张三",
            email="zhangsan@example.com"
        )
        assert info.name == "张三"
        assert info.email == "zhangsan@example.com"
        assert info.phone is None
    
    def test_create_personal_info_with_all_fields(self):
        """测试创建PersonalInfo（所有字段）"""
        info = PersonalInfo(
            name="张三",
            email="zhangsan@example.com",
            phone="13800138000",
            location="北京",
            website="https://example.com",
            linkedin="https://linkedin.com/in/zhangsan",
            github="https://github.com/zhangsan",
            summary="5年Python开发经验"
        )
        assert info.name == "张三"
        assert info.phone == "13800138000"
        assert info.summary == "5年Python开发经验"


class TestEducation:
    """测试Education模型"""
    
    def test_create_education(self):
        """测试创建Education"""
        edu = Education(
            school="清华大学",
            degree="本科",
            major="计算机科学与技术",
            start_date="2015-09",
            end_date="2019-06",
            gpa="3.8/4.0",
            achievements=["国家奖学金", "优秀毕业生"]
        )
        assert edu.school == "清华大学"
        assert edu.degree == "本科"
        assert len(edu.achievements) == 2


class TestWorkExperience:
    """测试WorkExperience模型"""
    
    def test_create_work_experience(self):
        """测试创建WorkExperience"""
        work = WorkExperience(
            company="某科技公司",
            position="高级Python工程师",
            start_date="2019-07",
            end_date=None,
            location="北京",
            responsibilities=["负责AI应用开发", "优化系统性能"],
            achievements=["提升系统性能30%"]
        )
        assert work.company == "某科技公司"
        assert work.end_date is None  # 在职
        assert len(work.responsibilities) == 2


class TestProjectExperience:
    """测试ProjectExperience模型"""
    
    def test_create_project_experience(self):
        """测试创建ProjectExperience"""
        project = ProjectExperience(
            name="AI框架项目",
            role="技术负责人",
            start_date="2023-01",
            end_date="2023-12",
            description="开发通用AI框架",
            technologies=["Python", "FastAPI", "Vue3"],
            achievements=["完成核心功能开发", "性能优化50%"]
        )
        assert project.name == "AI框架项目"
        assert len(project.technologies) == 3


class TestSkill:
    """测试Skill模型"""
    
    def test_create_skill(self):
        """测试创建Skill"""
        skill = Skill(
            category="编程语言",
            items=["Python", "JavaScript", "Go"],
            proficiency="精通"
        )
        assert skill.category == "编程语言"
        assert len(skill.items) == 3
        assert skill.proficiency == "精通"


class TestCertificate:
    """测试Certificate模型"""
    
    def test_create_certificate(self):
        """测试创建Certificate"""
        cert = Certificate(
            name="AWS认证开发者",
            issuer="Amazon Web Services",
            date="2023-06",
            credential_id="ABC123",
            credential_url="https://aws.amazon.com/verify/ABC123"
        )
        assert cert.name == "AWS认证开发者"
        assert cert.issuer == "Amazon Web Services"


class TestResumeData:
    """测试ResumeData模型"""
    
    def test_create_resume_data(self):
        """测试创建ResumeData"""
        resume = ResumeData(
            personal_info=PersonalInfo(
                name="张三",
                email="zhangsan@example.com"
            ),
            education=[
                Education(
                    school="清华大学",
                    degree="本科",
                    major="计算机科学与技术",
                    start_date="2015-09",
                    end_date="2019-06"
                )
            ],
            work_experience=[
                WorkExperience(
                    company="某科技公司",
                    position="高级Python工程师",
                    start_date="2019-07",
                    responsibilities=["负责AI应用开发"]
                )
            ],
            skills=[
                Skill(
                    category="编程语言",
                    items=["Python", "JavaScript"]
                )
            ]
        )
        assert resume.personal_info.name == "张三"
        assert len(resume.education) == 1
        assert len(resume.work_experience) == 1
        assert len(resume.skills) == 1


class TestOptimizationSuggestion:
    """测试OptimizationSuggestion模型"""
    
    def test_create_optimization_suggestion(self):
        """测试创建OptimizationSuggestion"""
        suggestion = OptimizationSuggestion(
            category="内容",
            priority="高",
            description="建议添加量化成果",
            original_text="负责系统开发",
            suggested_text="负责系统开发，提升性能30%"
        )
        assert suggestion.category == "内容"
        assert suggestion.priority == "高"


class TestOptimizationResult:
    """测试OptimizationResult模型"""
    
    def test_create_optimization_result(self):
        """测试创建OptimizationResult"""
        resume_data = ResumeData(
            personal_info=PersonalInfo(
                name="张三",
                email="zhangsan@example.com"
            )
        )
        result = OptimizationResult(
            optimized_resume=resume_data,
            suggestions=[
                OptimizationSuggestion(
                    category="内容",
                    priority="高",
                    description="建议添加量化成果"
                )
            ],
            score=85.5,
            score_breakdown={"内容": 90.0, "格式": 80.0, "关键词": 86.0},
            optimization_level="advanced"
        )
        assert result.score == 85.5
        assert len(result.suggestions) == 1
        assert result.optimization_level == "advanced"


class TestTemplateInfo:
    """测试TemplateInfo模型"""
    
    def test_create_template_info(self):
        """测试创建TemplateInfo"""
        template = TemplateInfo(
            id="classic",
            name="经典模板",
            description="适合传统行业的经典简历模板",
            category="经典",
            preview_url="/templates/classic/preview.png",
            file_path="/templates/classic/template.html",
            supported_sections=["personal_info", "education", "work_experience"]
        )
        assert template.id == "classic"
        assert template.category == "经典"
        assert len(template.supported_sections) == 3


class TestParseResumeRequest:
    """测试ParseResumeRequest模型"""
    
    def test_create_parse_request_valid_format(self):
        """测试创建ParseResumeRequest（有效格式）"""
        request = ParseResumeRequest(
            file_name="resume.pdf",
            file_format="pdf"
        )
        assert request.file_name == "resume.pdf"
        assert request.file_format == "pdf"
    
    def test_create_parse_request_invalid_format(self):
        """测试创建ParseResumeRequest（无效格式）"""
        with pytest.raises(ValidationError) as exc_info:
            ParseResumeRequest(
                file_name="resume.txt",
                file_format="txt"
            )
        assert "不支持的文件格式" in str(exc_info.value)


class TestParseResumeResponse:
    """测试ParseResumeResponse模型"""
    
    def test_create_parse_response(self):
        """测试创建ParseResumeResponse"""
        resume_data = ResumeData(
            personal_info=PersonalInfo(
                name="张三",
                email="zhangsan@example.com"
            )
        )
        response = ParseResumeResponse(
            success=True,
            message="解析成功",
            data=resume_data,
            parse_time=2.5
        )
        assert response.success is True
        assert response.parse_time == 2.5
        assert response.data.personal_info.name == "张三"


class TestOptimizeResumeRequest:
    """测试OptimizeResumeRequest模型"""
    
    def test_create_optimize_request_valid_level(self):
        """测试创建OptimizeResumeRequest（有效级别）"""
        resume_data = ResumeData(
            personal_info=PersonalInfo(
                name="张三",
                email="zhangsan@example.com"
            )
        )
        request = OptimizeResumeRequest(
            resume_data=resume_data,
            job_description="Python开发工程师",
            optimization_level="advanced"
        )
        assert request.optimization_level == "advanced"
    
    def test_create_optimize_request_invalid_level(self):
        """测试创建OptimizeResumeRequest（无效级别）"""
        resume_data = ResumeData(
            personal_info=PersonalInfo(
                name="张三",
                email="zhangsan@example.com"
            )
        )
        with pytest.raises(ValidationError) as exc_info:
            OptimizeResumeRequest(
                resume_data=resume_data,
                optimization_level="expert"
            )
        assert "不支持的优化级别" in str(exc_info.value)


class TestOptimizeResumeResponse:
    """测试OptimizeResumeResponse模型"""
    
    def test_create_optimize_response(self):
        """测试创建OptimizeResumeResponse"""
        resume_data = ResumeData(
            personal_info=PersonalInfo(
                name="张三",
                email="zhangsan@example.com"
            )
        )
        result = OptimizationResult(
            optimized_resume=resume_data,
            optimization_level="basic"
        )
        response = OptimizeResumeResponse(
            success=True,
            message="优化成功",
            data=result,
            optimization_time=5.2
        )
        assert response.success is True
        assert response.optimization_time == 5.2


class TestGenerateResumeRequest:
    """测试GenerateResumeRequest模型"""
    
    def test_create_generate_request_valid_format(self):
        """测试创建GenerateResumeRequest（有效格式）"""
        resume_data = ResumeData(
            personal_info=PersonalInfo(
                name="张三",
                email="zhangsan@example.com"
            )
        )
        request = GenerateResumeRequest(
            resume_data=resume_data,
            template_id="classic",
            output_format="pdf"
        )
        assert request.template_id == "classic"
        assert request.output_format == "pdf"
    
    def test_create_generate_request_invalid_format(self):
        """测试创建GenerateResumeRequest（无效格式）"""
        resume_data = ResumeData(
            personal_info=PersonalInfo(
                name="张三",
                email="zhangsan@example.com"
            )
        )
        with pytest.raises(ValidationError) as exc_info:
            GenerateResumeRequest(
                resume_data=resume_data,
                template_id="classic",
                output_format="docx"
            )
        assert "不支持的输出格式" in str(exc_info.value)


class TestGenerateResumeResponse:
    """测试GenerateResumeResponse模型"""
    
    def test_create_generate_response(self):
        """测试创建GenerateResumeResponse"""
        response = GenerateResumeResponse(
            success=True,
            message="生成成功",
            file_id="resume_123",
            file_path="/output/resume_123.pdf",
            download_url="/api/v1/resume/download/resume_123",
            preview_url="/api/v1/resume/preview/resume_123",
            generation_time=3.8
        )
        assert response.success is True
        assert response.file_id == "resume_123"
        assert response.generation_time == 3.8


class TestListTemplatesResponse:
    """测试ListTemplatesResponse模型"""
    
    def test_create_list_templates_response(self):
        """测试创建ListTemplatesResponse"""
        templates = [
            TemplateInfo(
                id="classic",
                name="经典模板",
                description="经典简历模板",
                category="经典",
                file_path="/templates/classic/template.html"
            ),
            TemplateInfo(
                id="modern",
                name="现代模板",
                description="现代简历模板",
                category="现代",
                file_path="/templates/modern/template.html"
            )
        ]
        response = ListTemplatesResponse(
            success=True,
            message="获取模板列表成功",
            templates=templates
        )
        assert response.success is True
        assert len(response.templates) == 2
        assert response.templates[0].id == "classic"
