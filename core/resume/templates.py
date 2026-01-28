"""
Resume模块 - 模板管理

管理简历模板，提供模板列表查询和模板路径获取功能。
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from core.base.service import BaseService
from core.resume.models import TemplateInfo


class ResumeTemplateError(Exception):
    """模板管理错误"""
    pass


class ResumeTemplate(BaseService):
    """
    简历模板管理器
    
    管理简历模板，提供模板列表查询和模板路径获取功能。
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        初始化模板管理器
        
        参数:
            config: 配置字典
        """
        super().__init__(config)
        resume_config = config.get("resume", {})
        self.template_dir = resume_config.get("template_dir", "templates/resume")
        self._templates: Dict[str, TemplateInfo] = {}
    
    async def initialize(self) -> None:
        """初始化模板管理器，加载模板元数据"""
        await super().initialize()
        
        # 加载模板元数据
        await self._load_templates()
        
        self.logger.info(f"ResumeTemplate初始化完成，加载了 {len(self._templates)} 个模板")
    
    async def _load_templates(self) -> None:
        """加载模板元数据"""
        template_path = Path(self.template_dir)
        
        if not template_path.exists():
            self.logger.warning(f"模板目录不存在: {self.template_dir}，将创建默认模板")
            template_path.mkdir(parents=True, exist_ok=True)
            await self._create_default_templates(template_path)
            return
        
        # 扫描模板目录
        for template_dir in template_path.iterdir():
            if not template_dir.is_dir():
                continue
            
            template_id = template_dir.name
            metadata_file = template_dir / "metadata.json"
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    
                    template_info = TemplateInfo(
                        id=template_id,
                        name=metadata.get("name", template_id),
                        description=metadata.get("description", ""),
                        category=metadata.get("category", "经典"),
                        preview_url=metadata.get("preview_url"),
                        file_path=str(template_dir / "template.html"),
                        supported_sections=metadata.get("supported_sections", []),
                    )
                    
                    self._templates[template_id] = template_info
                except Exception as e:
                    self.logger.warning(f"加载模板元数据失败: {template_id}, 错误: {e}")
            else:
                # 如果没有metadata.json，创建默认模板信息
                template_info = TemplateInfo(
                    id=template_id,
                    name=template_id,
                    description=f"{template_id}简历模板",
                    category="经典",
                    file_path=str(template_dir / "template.html"),
                    supported_sections=[],
                )
                self._templates[template_id] = template_info
    
    async def _create_default_templates(self, template_path: Path) -> None:
        """创建默认模板"""
        default_templates = [
            {
                "id": "classic",
                "name": "经典模板",
                "description": "适合传统行业的经典简历模板",
                "category": "经典",
            },
            {
                "id": "modern",
                "name": "现代模板",
                "description": "现代简洁风格的简历模板",
                "category": "现代",
            },
            {
                "id": "creative",
                "name": "创意模板",
                "description": "适合创意行业的简历模板",
                "category": "创意",
            },
            {
                "id": "tech",
                "name": "技术模板",
                "description": "适合技术人员的简历模板",
                "category": "技术",
            },
        ]
        
        for template_data in default_templates:
            template_dir = template_path / template_data["id"]
            template_dir.mkdir(exist_ok=True)
            
            # 创建metadata.json
            metadata = {
                "name": template_data["name"],
                "description": template_data["description"],
                "category": template_data["category"],
                "supported_sections": [
                    "personal_info",
                    "education",
                    "work_experience",
                    "project_experience",
                    "skills",
                ],
            }
            
            with open(template_dir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 创建基础HTML模板（使用普通字符串，避免f-string解析Jinja2语法）
            template_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ resume.personal_info.name }}}} - 简历</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }}
        .section {{
            margin: 20px 0;
        }}
        .section h2 {{
            color: #666;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
        }}
    </style>
</head>
<body>
    <h1>{{{{ resume.personal_info.name }}}}</h1>
    <div class="section">
        <p>邮箱: {{{{ resume.personal_info.email }}}}</p>
        {% if resume.personal_info.phone %}
        <p>电话: {{{{ resume.personal_info.phone }}}}</p>
        {% endif %}
    </div>
    
    {% if resume.education %}
    <div class="section">
        <h2>教育经历</h2>
        {% for edu in resume.education %}
        <p><strong>{{{{ edu.school }}}}</strong> - {{{{ edu.degree }}}} - {{{{ edu.major }}}}</p>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if resume.work_experience %}
    <div class="section">
        <h2>工作经历</h2>
        {% for work in resume.work_experience %}
        <p><strong>{{{{ work.company }}}}</strong> - {{{{ work.position }}}}</p>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>"""
            
            with open(template_dir / "template.html", "w", encoding="utf-8") as f:
                f.write(template_html)
            
            # 创建模板信息
            template_info = TemplateInfo(
                id=template_data["id"],
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                file_path=str(template_dir / "template.html"),
                supported_sections=metadata["supported_sections"],
            )
            
            self._templates[template_data["id"]] = template_info
    
    def get_all_templates(self) -> List[TemplateInfo]:
        """
        获取所有可用模板
        
        返回:
            List[TemplateInfo]: 模板列表
        """
        return list(self._templates.values())
    
    def get_template(self, template_id: str) -> Optional[TemplateInfo]:
        """
        获取指定模板
        
        参数:
            template_id: 模板ID
        
        返回:
            Optional[TemplateInfo]: 模板信息，如果不存在返回None
        """
        return self._templates.get(template_id)
    
    def get_template_path(self, template_id: str) -> Optional[str]:
        """
        获取模板文件路径
        
        参数:
            template_id: 模板ID
        
        返回:
            Optional[str]: 模板文件路径，如果不存在返回None
        """
        template = self.get_template(template_id)
        if template:
            return template.file_path
        return None
