"""
Resume模块数据模型定义

定义简历相关的所有数据结构，包括：
- ResumeData: 简历结构化数据
- OptimizationResult: 优化结果
- TemplateInfo: 模板信息
- API请求/响应模型
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


# ==================== 基础数据模型 ====================

class PersonalInfo(BaseModel):
    """个人基本信息"""
    name: str = Field(..., description="姓名")
    email: str = Field(..., description="电子邮箱")
    phone: Optional[str] = Field(None, description="电话号码")
    location: Optional[str] = Field(None, description="所在地")
    website: Optional[str] = Field(None, description="个人网站")
    linkedin: Optional[str] = Field(None, description="LinkedIn链接")
    github: Optional[str] = Field(None, description="GitHub链接")
    summary: Optional[str] = Field(None, description="个人简介")


class Education(BaseModel):
    """教育经历"""
    school: str = Field(..., description="学校名称")
    degree: str = Field(..., description="学位")
    major: str = Field(..., description="专业")
    start_date: str = Field(..., description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期（在读可为空）")
    gpa: Optional[str] = Field(None, description="GPA/成绩")
    achievements: List[str] = Field(default_factory=list, description="主要成就")


class WorkExperience(BaseModel):
    """工作经历"""
    company: str = Field(..., description="公司名称")
    position: str = Field(..., description="职位")
    start_date: str = Field(..., description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期（在职可为空）")
    location: Optional[str] = Field(None, description="工作地点")
    responsibilities: List[str] = Field(default_factory=list, description="主要职责")
    achievements: List[str] = Field(default_factory=list, description="主要成就")


class ProjectExperience(BaseModel):
    """项目经历"""
    name: str = Field(..., description="项目名称")
    role: str = Field(..., description="项目角色")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    description: str = Field(..., description="项目描述")
    technologies: List[str] = Field(default_factory=list, description="使用技术")
    achievements: List[str] = Field(default_factory=list, description="项目成果")


class Skill(BaseModel):
    """技能"""
    category: str = Field(..., description="技能类别（如：编程语言、框架、工具）")
    items: List[str] = Field(..., description="具体技能列表")
    proficiency: Optional[str] = Field(None, description="熟练程度（如：精通、熟悉、了解）")


class Certificate(BaseModel):
    """证书"""
    name: str = Field(..., description="证书名称")
    issuer: str = Field(..., description="颁发机构")
    date: Optional[str] = Field(None, description="获得日期")
    credential_id: Optional[str] = Field(None, description="证书编号")
    credential_url: Optional[str] = Field(None, description="证书链接")


class ResumeData(BaseModel):
    """简历结构化数据"""
    personal_info: PersonalInfo = Field(..., description="个人基本信息")
    education: List[Education] = Field(default_factory=list, description="教育经历")
    work_experience: List[WorkExperience] = Field(default_factory=list, description="工作经历")
    project_experience: List[ProjectExperience] = Field(default_factory=list, description="项目经历")
    skills: List[Skill] = Field(default_factory=list, description="技能")
    certificates: List[Certificate] = Field(default_factory=list, description="证书")
    languages: List[Dict[str, str]] = Field(default_factory=list, description="语言能力")
    awards: List[str] = Field(default_factory=list, description="获奖经历")
    publications: List[str] = Field(default_factory=list, description="论文/出版物")
    volunteer_experience: List[Dict[str, Any]] = Field(default_factory=list, description="志愿者经历")
    
    class Config:
        json_schema_extra = {
            "example": {
                "personal_info": {
                    "name": "张三",
                    "email": "zhangsan@example.com",
                    "phone": "13800138000",
                    "location": "北京",
                    "summary": "5年Python开发经验，擅长AI应用开发"
                },
                "education": [{
                    "school": "清华大学",
                    "degree": "本科",
                    "major": "计算机科学与技术",
                    "start_date": "2015-09",
                    "end_date": "2019-06",
                    "gpa": "3.8/4.0"
                }],
                "work_experience": [{
                    "company": "某科技公司",
                    "position": "高级Python工程师",
                    "start_date": "2019-07",
                    "end_date": None,
                    "responsibilities": ["负责AI应用开发", "优化系统性能"],
                    "achievements": ["提升系统性能30%"]
                }],
                "skills": [{
                    "category": "编程语言",
                    "items": ["Python", "JavaScript", "Go"],
                    "proficiency": "精通"
                }]
            }
        }


# ==================== 优化相关模型 ====================

class OptimizationSuggestion(BaseModel):
    """优化建议"""
    category: str = Field(..., description="建议类别（如：内容、格式、关键词）")
    priority: str = Field(..., description="优先级（高、中、低）")
    description: str = Field(..., description="建议描述")
    original_text: Optional[str] = Field(None, description="原始文本")
    suggested_text: Optional[str] = Field(None, description="建议修改后的文本")


class OptimizationResult(BaseModel):
    """优化结果"""
    optimized_resume: ResumeData = Field(..., description="优化后的简历数据")
    suggestions: List[OptimizationSuggestion] = Field(default_factory=list, description="优化建议列表")
    score: Optional[float] = Field(None, description="简历评分（0-100）")
    score_breakdown: Optional[Dict[str, float]] = Field(None, description="评分细分")
    optimization_level: str = Field(..., description="优化级别（basic/advanced）")
    timestamp: datetime = Field(default_factory=datetime.now, description="优化时间")


# ==================== 模板相关模型 ====================

class TemplateInfo(BaseModel):
    """模板信息"""
    id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: str = Field(..., description="模板描述")
    category: str = Field(..., description="模板类别（如：经典、现代、创意、技术）")
    preview_url: Optional[str] = Field(None, description="预览图URL")
    file_path: str = Field(..., description="模板文件路径")
    supported_sections: List[str] = Field(default_factory=list, description="支持的简历部分")


# ==================== API请求/响应模型 ====================

class ParseResumeRequest(BaseModel):
    """解析简历请求"""
    file_name: str = Field(..., description="文件名")
    file_format: str = Field(..., description="文件格式（pdf/docx/json）")
    
    @validator("file_format")
    def validate_format(cls, v):
        allowed_formats = ["pdf", "docx", "json"]
        if v.lower() not in allowed_formats:
            raise ValueError(f"不支持的文件格式: {v}，支持的格式: {', '.join(allowed_formats)}")
        return v.lower()


class ParseResumeResponse(BaseModel):
    """解析简历响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[ResumeData] = Field(None, description="解析后的简历数据")
    parse_time: float = Field(..., description="解析耗时（秒）")


class OptimizeResumeRequest(BaseModel):
    """优化简历请求"""
    resume_data: ResumeData = Field(..., description="简历数据")
    job_description: Optional[str] = Field(None, description="目标职位描述")
    optimization_level: str = Field(default="basic", description="优化级别（basic/advanced）")
    
    @validator("optimization_level")
    def validate_level(cls, v):
        allowed_levels = ["basic", "advanced"]
        if v not in allowed_levels:
            raise ValueError(f"不支持的优化级别: {v}，支持的级别: {', '.join(allowed_levels)}")
        return v


class OptimizeResumeResponse(BaseModel):
    """优化简历响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[OptimizationResult] = Field(None, description="优化结果")
    optimization_time: float = Field(..., description="优化耗时（秒）")


class GenerateResumeRequest(BaseModel):
    """生成简历请求"""
    resume_data: ResumeData = Field(..., description="简历数据")
    template_id: str = Field(..., description="模板ID")
    output_format: str = Field(default="pdf", description="输出格式（html/pdf）")
    
    @validator("output_format")
    def validate_output_format(cls, v):
        allowed_formats = ["html", "pdf"]
        if v.lower() not in allowed_formats:
            raise ValueError(f"不支持的输出格式: {v}，支持的格式: {', '.join(allowed_formats)}")
        return v.lower()


class GenerateResumeResponse(BaseModel):
    """生成简历响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    file_id: Optional[str] = Field(None, description="生成的文件ID")
    file_path: Optional[str] = Field(None, description="文件路径")
    download_url: Optional[str] = Field(None, description="下载URL")
    preview_url: Optional[str] = Field(None, description="预览URL")
    generation_time: float = Field(..., description="生成耗时（秒）")


class ListTemplatesResponse(BaseModel):
    """列出模板响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    templates: List[TemplateInfo] = Field(default_factory=list, description="模板列表")
