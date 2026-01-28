"""
ResumeOptimizer单元测试
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from core.resume.optimizer import ResumeOptimizer, ResumeOptimizeError
from core.resume.models import ResumeData, PersonalInfo, OptimizationResult
from core.llm.models import LLMResponse


class TestResumeOptimizer:
    """测试ResumeOptimizer"""
    
    @pytest.fixture
    def optimizer_config(self):
        """优化器配置"""
        return {
            "resume": {
                "optimizer_model": "qwen-max",
                "optimizer_temperature": 0.7,
                "optimizer_max_tokens": 4000,
            }
        }
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLMService"""
        service = MagicMock()
        service.chat = AsyncMock()
        return service
    
    @pytest.fixture
    def optimizer(self, optimizer_config, mock_llm_service):
        """创建ResumeOptimizer实例"""
        return ResumeOptimizer(optimizer_config, mock_llm_service)
    
    @pytest.fixture
    def sample_resume_data(self):
        """示例简历数据"""
        return ResumeData(
            personal_info=PersonalInfo(
                name="张三",
                email="zhangsan@example.com",
                phone="13800138000"
            )
        )
    
    def test_init(self, optimizer_config, mock_llm_service):
        """测试初始化"""
        optimizer = ResumeOptimizer(optimizer_config, mock_llm_service)
        assert optimizer.default_model == "qwen-max"
        assert optimizer.temperature == 0.7
        assert optimizer.max_tokens == 4000
    
    @pytest.mark.asyncio
    async def test_optimize_success(self, optimizer, sample_resume_data):
        """测试优化成功"""
        # Mock LLM响应
        optimized_resume_json = sample_resume_data.model_dump()
        llm_response_json = {
            "optimized_resume": optimized_resume_json,
            "suggestions": [
                {
                    "category": "内容",
                    "priority": "高",
                    "description": "建议添加量化成果"
                }
            ],
            "score": 85.5,
            "score_breakdown": {
                "内容": 90.0,
                "格式": 80.0,
                "关键词": 86.0
            }
        }
        
        mock_response = LLMResponse(
            content=json.dumps(llm_response_json, ensure_ascii=False),
            model="qwen-max",
            usage={"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
        )
        
        optimizer.llm_service.chat.return_value = mock_response
        
        result = await optimizer.optimize(sample_resume_data, optimization_level="basic")
        
        assert isinstance(result, OptimizationResult)
        assert result.score == 85.5
        assert len(result.suggestions) == 1
        assert result.optimization_level == "basic"
        
        # 验证LLM调用
        optimizer.llm_service.chat.assert_called_once()
        call_args = optimizer.llm_service.chat.call_args
        assert call_args.kwargs["model"] == "qwen-max"
        assert len(call_args.args[0]) == 2  # system和user消息
    
    @pytest.mark.asyncio
    async def test_optimize_with_job_description(self, optimizer, sample_resume_data):
        """测试带职位描述的优化"""
        job_description = "Python开发工程师，要求3年以上经验"
        
        mock_response = LLMResponse(
            content=json.dumps({
                "optimized_resume": sample_resume_data.model_dump(),
                "suggestions": [],
                "score": 80.0
            }, ensure_ascii=False),
            model="qwen-max",
            usage={"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
        )
        
        optimizer.llm_service.chat.return_value = mock_response
        
        result = await optimizer.optimize(
            sample_resume_data,
            job_description=job_description,
            optimization_level="advanced"
        )
        
        assert result.optimization_level == "advanced"
        
        # 验证提示词包含职位描述
        call_args = optimizer.llm_service.chat.call_args
        user_message = call_args.args[0][1]["content"]
        assert job_description in user_message
    
    @pytest.mark.asyncio
    async def test_optimize_llm_error(self, optimizer, sample_resume_data):
        """测试LLM调用失败"""
        optimizer.llm_service.chat.side_effect = Exception("LLM调用失败")
        
        with pytest.raises(ResumeOptimizeError) as exc_info:
            await optimizer.optimize(sample_resume_data)
        assert "优化简历失败" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_optimize_invalid_json_response(self, optimizer, sample_resume_data):
        """测试LLM返回无效JSON"""
        mock_response = LLMResponse(
            content="这不是JSON格式的响应",
            model="qwen-max",
            usage={"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
        )
        
        optimizer.llm_service.chat.return_value = mock_response
        
        result = await optimizer.optimize(sample_resume_data)
        
        # 应该返回回退结果
        assert isinstance(result, OptimizationResult)
        assert result.optimized_resume == sample_resume_data
        assert len(result.suggestions) > 0
        assert "系统" in [s.category for s in result.suggestions]
    
    def test_build_optimization_prompt_basic(self, optimizer, sample_resume_data):
        """测试构建基础优化提示词"""
        prompt = optimizer._build_optimization_prompt(
            sample_resume_data,
            None,
            "basic"
        )
        
        assert "简历进行优化分析" in prompt
        assert "基础优化" in prompt
        assert sample_resume_data.personal_info.name in prompt
    
    def test_build_optimization_prompt_advanced(self, optimizer, sample_resume_data):
        """测试构建高级优化提示词"""
        job_description = "Python开发工程师"
        prompt = optimizer._build_optimization_prompt(
            sample_resume_data,
            job_description,
            "advanced"
        )
        
        assert "高级优化" in prompt
        assert job_description in prompt
        assert "深度优化分析" in prompt
    
    @pytest.mark.asyncio
    async def test_parse_optimization_response_valid(self, optimizer, sample_resume_data):
        """测试解析有效的优化响应"""
        response_json = {
            "optimized_resume": sample_resume_data.model_dump(),
            "suggestions": [
                {
                    "category": "内容",
                    "priority": "高",
                    "description": "建议添加量化成果"
                }
            ],
            "score": 85.5,
            "score_breakdown": {
                "内容": 90.0
            }
        }
        
        response_content = json.dumps(response_json, ensure_ascii=False)
        result = optimizer._parse_optimization_response(
            response_content,
            sample_resume_data,
            "basic"
        )
        
        assert isinstance(result, OptimizationResult)
        assert result.score == 85.5
        assert len(result.suggestions) == 1
        assert result.suggestions[0].category == "内容"
