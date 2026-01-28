"""
Resume模块 - 简历优化器

基于LLM（通义千问）对简历内容进行智能优化，提供优化建议和评分。
"""

import json
from typing import Dict, Any, Optional, List
from core.base.service import BaseService
from core.llm.service import LLMService
from core.resume.models import (
    ResumeData,
    OptimizationResult,
    OptimizationSuggestion,
)


class ResumeOptimizeError(Exception):
    """简历优化错误"""
    pass


class ResumeOptimizer(BaseService):
    """
    简历优化器
    
    使用LLM（通义千问）对简历内容进行智能优化，提供：
    - 内容优化建议
    - 关键词匹配优化
    - 语句润色
    - 简历评分
    """
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService) -> None:
        """
        初始化优化器
        
        参数:
            config: 配置字典
            llm_service: LLM服务实例
        """
        super().__init__(config)
        self.llm_service = llm_service
        self.default_model = config.get("resume", {}).get("optimizer_model", "qwen-max")
        self.temperature = config.get("resume", {}).get("optimizer_temperature", 0.7)
        self.max_tokens = config.get("resume", {}).get("optimizer_max_tokens", 4000)
    
    async def optimize(
        self,
        resume_data: ResumeData,
        job_description: Optional[str] = None,
        optimization_level: str = "basic"
    ) -> OptimizationResult:
        """
        优化简历
        
        参数:
            resume_data: 原始简历数据
            job_description: 目标职位描述（可选）
            optimization_level: 优化级别（basic/advanced）
        
        返回:
            OptimizationResult: 优化结果
        
        异常:
            ResumeOptimizeError: 优化失败时抛出
        """
        try:
            # 构建优化提示词
            prompt = self._build_optimization_prompt(resume_data, job_description, optimization_level)
            
            # 调用LLM进行优化
            messages = [
                {
                    "role": "system",
                    "content": "你是一位专业的简历优化专家，擅长分析简历内容并提供针对性的优化建议。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = await self.llm_service.chat(
                messages=messages,
                model=self.default_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            # 解析LLM响应
            return self._parse_optimization_response(
                response.content,
                resume_data,
                optimization_level
            )
        except Exception as e:
            self.logger.error(f"优化简历失败: {e}", exc_info=True)
            raise ResumeOptimizeError(f"优化简历失败: {e}") from e
    
    def _build_optimization_prompt(
        self,
        resume_data: ResumeData,
        job_description: Optional[str],
        optimization_level: str
    ) -> str:
        """
        构建优化提示词
        
        参数:
            resume_data: 简历数据
            job_description: 职位描述
            optimization_level: 优化级别
        
        返回:
            str: 优化提示词
        """
        # 将简历数据转换为JSON字符串
        resume_json = resume_data.model_dump_json(indent=2, ensure_ascii=False)
        
        prompt_parts = [
            "请对以下简历进行优化分析，并提供优化建议。",
            "",
            "## 简历内容（JSON格式）",
            resume_json,
        ]
        
        if job_description:
            prompt_parts.extend([
                "",
                "## 目标职位描述",
                job_description,
            ])
        
        if optimization_level == "advanced":
            prompt_parts.extend([
                "",
                "## 优化要求（高级优化）",
                "请进行深度优化分析，包括：",
                "1. 内容优化：检查描述是否具体、量化、有说服力",
                "2. 关键词匹配：识别与职位描述相关的关键词，建议添加或优化",
                "3. 结构优化：检查简历结构是否合理，信息是否完整",
                "4. 亮点提炼：识别并突出个人亮点和核心优势",
                "5. 语言润色：优化表达方式，使其更专业、更有吸引力",
                "6. 格式检查：检查格式是否规范、排版是否美观",
            ])
        else:
            prompt_parts.extend([
                "",
                "## 优化要求（基础优化）",
                "请进行基础优化分析，包括：",
                "1. 内容完整性检查",
                "2. 关键词匹配建议",
                "3. 基本语言润色建议",
            ])
        
        prompt_parts.extend([
            "",
            "## 输出格式要求",
            "请以JSON格式返回优化结果，格式如下：",
            "{",
            '  "optimized_resume": { /* 优化后的简历数据，JSON格式，与输入格式相同 */ },',
            '  "suggestions": [',
            '    {',
            '      "category": "内容/格式/关键词",',
            '      "priority": "高/中/低",',
            '      "description": "建议描述",',
            '      "original_text": "原始文本（可选）",',
            '      "suggested_text": "建议修改后的文本（可选）"',
            '    }',
            '  ],',
            '  "score": 85.5,  /* 简历评分，0-100 */',
            '  "score_breakdown": {',
            '    "内容": 90.0,',
            '    "格式": 80.0,',
            '    "关键词": 86.0',
            '  }',
            "}",
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_optimization_response(
        self,
        response_content: str,
        original_resume: ResumeData,
        optimization_level: str
    ) -> OptimizationResult:
        """
        解析LLM优化响应
        
        参数:
            response_content: LLM响应内容
            original_resume: 原始简历数据
            optimization_level: 优化级别
        
        返回:
            OptimizationResult: 优化结果
        """
        try:
            # 尝试从响应中提取JSON
            json_start = response_content.find("{")
            json_end = response_content.rfind("}") + 1
            
            if json_start == -1 or json_end == 0:
                # 如果没有找到JSON，使用原始简历并生成基础建议
                self.logger.warning("LLM响应中未找到JSON格式，使用原始简历")
                return self._create_fallback_result(original_resume, response_content)
            
            json_str = response_content[json_start:json_end]
            result_data = json.loads(json_str)
            
            # 解析优化后的简历
            optimized_resume_data = result_data.get("optimized_resume", original_resume.model_dump())
            try:
                optimized_resume = ResumeData(**optimized_resume_data)
            except Exception as e:
                self.logger.warning(f"解析优化后的简历失败，使用原始简历: {e}")
                optimized_resume = original_resume
            
            # 解析优化建议
            suggestions_data = result_data.get("suggestions", [])
            suggestions = [
                OptimizationSuggestion(**s) for s in suggestions_data
            ]
            
            # 解析评分
            score = result_data.get("score", None)
            score_breakdown = result_data.get("score_breakdown", None)
            
            return OptimizationResult(
                optimized_resume=optimized_resume,
                suggestions=suggestions,
                score=score,
                score_breakdown=score_breakdown,
                optimization_level=optimization_level,
            )
        except json.JSONDecodeError as e:
            self.logger.error(f"解析LLM响应JSON失败: {e}")
            return self._create_fallback_result(original_resume, response_content)
        except Exception as e:
            self.logger.error(f"解析优化响应失败: {e}", exc_info=True)
            return self._create_fallback_result(original_resume, response_content)
    
    def _create_fallback_result(
        self,
        original_resume: ResumeData,
        response_content: str
    ) -> OptimizationResult:
        """
        创建回退结果（当LLM响应解析失败时）
        
        参数:
            original_resume: 原始简历数据
            response_content: LLM响应内容
        
        返回:
            OptimizationResult: 回退结果
        """
        # 生成基础建议
        suggestions = [
            OptimizationSuggestion(
                category="系统",
                priority="中",
                description="LLM响应解析失败，请检查简历内容或重试。原始响应：" + response_content[:200],
            )
        ]
        
        return OptimizationResult(
            optimized_resume=original_resume,
            suggestions=suggestions,
            score=None,
            score_breakdown=None,
            optimization_level="basic",
        )
