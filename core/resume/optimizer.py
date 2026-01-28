"""
Resume模块 - 简历优化器

基于LLM（通义千问）对简历内容进行智能优化，提供优化建议和评分。
"""

import json
import re
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
        resume_config = config.get("resume", {})
        self.default_model = resume_config.get("optimizer_model", "qwen-max")
        self.temperature = resume_config.get("optimizer_temperature", 0.7)
        self.max_tokens = resume_config.get("optimizer_max_tokens", 8000)  # 增加到8000以支持更长的响应
        self.optimizer_timeout = resume_config.get("optimizer_timeout", 120)  # 优化器超时时间（秒）
    
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
            
            # 记录优化请求信息
            self.logger.info(
                f"开始优化简历: 模型={self.default_model}, "
                f"优化级别={optimization_level}, "
                f"职位描述={'已提供' if job_description else '未提供'}, "
                f"简历字段数={len(resume_data.dict(exclude_none=True))}"
            )
            
            try:
                response = await self.llm_service.chat(
                    messages=messages,
                    model=self.default_model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                self.logger.debug(f"LLM响应成功: 内容长度={len(response.content) if response.content else 0}")
            except Exception as llm_error:
                self.logger.error(
                    f"LLM调用失败: 模型={self.default_model}, "
                    f"错误={type(llm_error).__name__}: {str(llm_error)}",
                    exc_info=True,
                    extra={
                        "model": self.default_model,
                        "optimization_level": optimization_level,
                        "has_job_description": bool(job_description),
                    }
                )
                raise
            
            # 解析LLM响应
            return self._parse_optimization_response(
                response.content,
                resume_data,
                optimization_level
            )
        except ResumeOptimizeError:
            raise
        except Exception as e:
            self.logger.error(
                f"优化简历失败: {type(e).__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "model": self.default_model,
                    "optimization_level": optimization_level,
                    "has_job_description": bool(job_description),
                    "resume_fields": list(resume_data.dict(exclude_none=True).keys()),
                }
            )
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
            # 尝试从响应中提取JSON（处理markdown代码块）
            # 1. 先尝试提取markdown代码块中的JSON
            import re
            
            # 查找markdown代码块中的JSON（改进正则表达式以匹配多行JSON）
            # 匹配 ```json ... ``` 或 ``` ... ``` 中的JSON对象
            json_code_block_pattern = r'```(?:json)?\s*(\{(?:[^{}]|(?:\{[^{}]*\}))*\})\s*```'
            json_matches = re.findall(json_code_block_pattern, response_content, re.DOTALL)
            
            # 如果没找到，尝试更宽松的匹配（匹配嵌套的JSON对象）
            if not json_matches:
                # 尝试匹配整个代码块内容
                code_block_pattern = r'```(?:json)?\s*(.*?)\s*```'
                code_blocks = re.findall(code_block_pattern, response_content, re.DOTALL)
                for block in code_blocks:
                    # 在代码块中查找JSON对象
                    json_start = block.find("{")
                    json_end = block.rfind("}") + 1
                    if json_start != -1 and json_end > json_start:
                        json_matches.append(block[json_start:json_end])
            
            result_data = {}
            optimized_resume_json = None
            suggestions_json = None
            
            if json_matches:
                # 解析每个JSON块
                for json_str in json_matches:
                    try:
                        data = json.loads(json_str)
                        
                        # 如果包含optimized_resume，这是优化后的简历数据
                        if "optimized_resume" in data:
                            optimized_resume_json = data["optimized_resume"]
                            result_data["optimized_resume"] = optimized_resume_json
                        
                        # 如果是数组，可能是suggestions
                        if isinstance(data, list):
                            suggestions_json = data
                            result_data["suggestions"] = suggestions_json
                        
                        # 如果包含suggestions字段
                        if "suggestions" in data:
                            suggestions_json = data["suggestions"]
                            result_data["suggestions"] = suggestions_json
                        
                        # 如果包含score字段
                        if "score" in data:
                            result_data["score"] = data["score"]
                        
                        # 如果包含score_breakdown字段
                        if "score_breakdown" in data:
                            result_data["score_breakdown"] = data["score_breakdown"]
                            
                    except json.JSONDecodeError as e:
                        self.logger.debug(f"解析JSON块失败: {e}")
                        continue
                
                # 如果找到了optimized_resume但没有找到suggestions，尝试从其他JSON块中提取
                if "optimized_resume" in result_data and "suggestions" not in result_data:
                    for json_str in json_matches:
                        try:
                            data = json.loads(json_str)
                            if isinstance(data, list) and len(data) > 0:
                                # 检查是否是建议列表格式
                                if all(isinstance(item, dict) and "category" in item for item in data):
                                    result_data["suggestions"] = data
                                    break
                        except json.JSONDecodeError:
                            continue
                
                # 如果找到了suggestions但没有找到optimized_resume，使用原始简历
                if "suggestions" in result_data and "optimized_resume" not in result_data:
                    result_data["optimized_resume"] = original_resume.model_dump()
            
            # 从文本中提取评分信息（如果JSON中没有）
            if "score" not in result_data:
                score_match = re.search(r'总分[：:]\s*(\d+\.?\d*)/100', response_content)
                if score_match:
                    try:
                        result_data["score"] = float(score_match.group(1))
                    except ValueError:
                        pass
            
            # 从文本中提取评分详情
            if "score_breakdown" not in result_data:
                breakdown = {}
                for key in ["内容", "格式", "关键词匹配", "关键词"]:
                    pattern = rf'{key}[：:]\s*(\d+\.?\d*)'
                    match = re.search(pattern, response_content)
                    if match:
                        try:
                            breakdown[key] = float(match.group(1))
                        except ValueError:
                            pass
                if breakdown:
                    result_data["score_breakdown"] = breakdown
            
            # 2. 如果没有找到代码块，尝试直接提取JSON对象
            if not result_data:
                json_start = response_content.find("{")
                json_end = response_content.rfind("}") + 1
                
                if json_start == -1 or json_end == 0:
                    # 如果没有找到JSON，使用原始简历并生成基础建议
                    self.logger.warning("LLM响应中未找到JSON格式，使用原始简历")
                    return self._create_fallback_result(original_resume, response_content)
                
                json_str = response_content[json_start:json_end]
                # 尝试清理JSON字符串（移除可能的markdown标记）
                json_str = re.sub(r'```json\s*', '', json_str)
                json_str = re.sub(r'```\s*', '', json_str)
                result_data = json.loads(json_str)
            
            if not result_data or "optimized_resume" not in result_data:
                self.logger.warning("无法解析LLM响应中的优化简历数据，使用原始简历")
                return self._create_fallback_result(original_resume, response_content)
            
            # 解析优化后的简历
            optimized_resume_data = result_data.get("optimized_resume", original_resume.model_dump())
            
            # 记录解析结果
            self.logger.debug(
                f"解析优化结果: 找到optimized_resume={bool(optimized_resume_data)}, "
                f"suggestions数量={len(result_data.get('suggestions', []))}, "
                f"score={result_data.get('score', 'None')}"
            )
            
            # 转换数据格式（LLM可能返回不同格式的字段）
            if isinstance(optimized_resume_data, dict):
                # 转换work_experience格式
                if "work_experience" in optimized_resume_data:
                    work_exp = optimized_resume_data["work_experience"]
                    if work_exp and isinstance(work_exp, list):
                        converted_work_exp = []
                        for work in work_exp:
                            if isinstance(work, dict):
                                converted_work = {}
                                # 字段映射
                                converted_work["company"] = work.get("company", work.get("company_name", ""))
                                converted_work["position"] = work.get("position", work.get("job_title", ""))
                                duration = work.get("duration", "")
                                if duration and "-" in duration:
                                    parts = duration.split("-")
                                    converted_work["start_date"] = work.get("start_date", parts[0].strip())
                                    converted_work["end_date"] = work.get("end_date", parts[-1].strip() if len(parts) > 1 else None)
                                else:
                                    converted_work["start_date"] = work.get("start_date", "")
                                    converted_work["end_date"] = work.get("end_date")
                                converted_work["location"] = work.get("location")
                                # description可能是字符串或列表
                                description = work.get("description", work.get("responsibilities", ""))
                                if isinstance(description, str):
                                    converted_work["responsibilities"] = [d.strip() for d in description.split("；") if d.strip()] if "；" in description else ([description] if description else [])
                                elif isinstance(description, list):
                                    converted_work["responsibilities"] = description
                                else:
                                    converted_work["responsibilities"] = []
                                converted_work["achievements"] = work.get("achievements", [])
                                converted_work_exp.append(converted_work)
                        optimized_resume_data["work_experience"] = converted_work_exp
                
                # 转换project_experience格式
                if "project_experience" in optimized_resume_data:
                    project_exp = optimized_resume_data["project_experience"]
                    if project_exp and isinstance(project_exp, list):
                        converted_project_exp = []
                        for project in project_exp:
                            if isinstance(project, dict):
                                converted_project = {}
                                converted_project["name"] = project.get("name", project.get("project_name", ""))
                                converted_project["role"] = project.get("role", project.get("project_role", ""))
                                converted_project["start_date"] = project.get("start_date")
                                converted_project["end_date"] = project.get("end_date")
                                # description可能是字符串
                                description = project.get("description", "")
                                if isinstance(description, str):
                                    converted_project["description"] = description
                                else:
                                    converted_project["description"] = str(description) if description else ""
                                converted_project["technologies"] = project.get("technologies", project.get("tools_used", []))
                                converted_project["achievements"] = project.get("achievements", [])
                                converted_project_exp.append(converted_project)
                        optimized_resume_data["project_experience"] = converted_project_exp
            
            try:
                optimized_resume = ResumeData(**optimized_resume_data)
            except Exception as e:
                self.logger.warning(f"解析优化后的简历失败，使用原始简历: {e}", exc_info=True)
                # 尝试修复常见问题
                try:
                    # 确保personal_info存在
                    if "personal_info" not in optimized_resume_data or not optimized_resume_data["personal_info"]:
                        optimized_resume_data["personal_info"] = original_resume.personal_info.model_dump()
                    
                    # 确保所有必需字段存在
                    for field in ["education", "work_experience", "project_experience", "skills", "certificates"]:
                        if field not in optimized_resume_data:
                            optimized_resume_data[field] = []
                    
                    optimized_resume = ResumeData(**optimized_resume_data)
                    self.logger.info("修复数据格式后成功解析优化后的简历")
                except Exception as e2:
                    self.logger.error(f"修复后仍无法解析，使用原始简历: {e2}")
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
