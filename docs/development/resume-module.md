# Resume模块开发文档

## 📋 模块概述

Resume模块提供完整的简历处理功能，包括解析、优化、生成和美化。

## 🏗️ 模块架构

```
core/resume/
├── __init__.py          # 模块导出
├── models.py            # 数据模型定义
├── parser.py            # 简历解析器
├── optimizer.py         # 简历优化器
├── generator.py         # 简历生成器
├── templates.py         # 模板管理器
└── service.py           # 简历服务主类
```

## 📦 核心组件

### ResumeParser

**职责**：解析不同格式的简历文件

**支持格式**：
- PDF：使用`pdfplumber`提取文本
- Word：使用`python-docx`提取内容
- JSON：直接加载和验证

**关键方法**：
- `parse(file_path, file_format) -> ResumeData`: 解析简历文件

**使用示例**：
```python
from core.resume.parser import ResumeParser

parser = ResumeParser(config)
await parser.initialize()
resume_data = await parser.parse("resume.pdf", "pdf")
```

### ResumeOptimizer

**职责**：基于LLM优化简历内容

**依赖**：
- `LLMService`：使用通义千问（qwen-max）进行优化

**优化级别**：
- `basic`：基础优化（内容检查、关键词匹配）
- `advanced`：高级优化（深度分析、专业润色）

**关键方法**：
- `optimize(resume_data, job_description, optimization_level) -> OptimizationResult`: 优化简历

**使用示例**：
```python
from core.resume.optimizer import ResumeOptimizer
from core.llm.service import LLMService

llm_service = LLMService(config)
optimizer = ResumeOptimizer(config, llm_service)
result = await optimizer.optimize(resume_data, job_description, "advanced")
```

### ResumeGenerator

**职责**：基于模板生成简历文件

**依赖**：
- `Jinja2`：模板渲染引擎
- `WeasyPrint`：HTML转PDF（可选）

**支持格式**：
- HTML：直接渲染
- PDF：HTML转PDF

**关键方法**：
- `generate(resume_data, template_id, output_format) -> Dict`: 生成简历

**使用示例**：
```python
from core.resume.generator import ResumeGenerator

generator = ResumeGenerator(config)
await generator.initialize()
result = await generator.generate(resume_data, "classic", "pdf")
```

### ResumeTemplate

**职责**：管理简历模板

**功能**：
- 加载模板元数据
- 提供模板列表查询
- 创建默认模板

**关键方法**：
- `get_all_templates() -> List[TemplateInfo]`: 获取所有模板
- `get_template(template_id) -> Optional[TemplateInfo]`: 获取指定模板

### ResumeService

**职责**：统一的简历处理接口

**协调子模块**：
- ResumeParser：解析简历
- ResumeOptimizer：优化简历
- ResumeGenerator：生成简历
- ResumeTemplate：管理模板

**关键方法**：
- `parse_resume(request) -> ParseResumeResponse`
- `optimize_resume(request) -> OptimizeResumeResponse`
- `generate_resume(request) -> GenerateResumeResponse`
- `list_templates() -> ListTemplatesResponse`

## 🔧 扩展指南

### 添加新的解析器

1. 在`ResumeParser`中添加新的解析方法
2. 更新`supported_formats`列表
3. 添加相应的单元测试

**示例**：
```python
async def _parse_markdown(self, file_path: str) -> ResumeData:
    """解析Markdown格式的简历"""
    # 实现解析逻辑
    pass
```

### 添加新的模板

1. 在`templates/resume/`目录下创建新模板目录
2. 创建`template.html`文件
3. 创建`metadata.json`文件
4. （可选）创建`preview.png`预览图

**模板目录结构**：
```
templates/resume/my-template/
├── template.html      # 模板HTML文件
├── metadata.json      # 模板元数据
└── preview.png        # 预览图（可选）
```

**metadata.json格式**：
```json
{
  "name": "我的模板",
  "description": "模板描述",
  "category": "自定义",
  "supported_sections": [
    "personal_info",
    "education",
    "work_experience"
  ]
}
```

### 自定义优化策略

1. 扩展`ResumeOptimizer`类
2. 重写`_build_optimization_prompt`方法
3. 实现自定义的优化逻辑

## 🧪 测试

### 运行单元测试

```bash
# 运行所有Resume模块测试
pytest tests/unit/core/resume/ -v

# 运行特定测试文件
pytest tests/unit/core/resume/test_parser.py -v

# 运行并生成覆盖率报告
pytest tests/unit/core/resume/ --cov=core.resume --cov-report=html
```

### 运行集成测试

```bash
# 运行集成测试
pytest tests/integration/test_resume_integration.py -v -m integration
```

### 运行E2E测试

```bash
# 运行E2E测试
pytest tests/e2e/test_resume_e2e.py -v -m e2e
```

## 📊 性能指标

- **解析时间**：< 5秒（PDF/Word），< 1秒（JSON）
- **优化时间**：< 10秒（基础优化），< 20秒（高级优化）
- **生成时间**：< 5秒（HTML），< 10秒（PDF）

## 🔒 安全考虑

- **文件大小限制**：默认10MB
- **文件类型验证**：严格验证文件格式
- **临时文件清理**：自动清理上传的临时文件

## 🐛 故障排查

### 问题1：PDF解析失败

**可能原因**：
- PDF文件是扫描版（图片格式）
- PDF文件损坏
- pdfplumber未正确安装

**解决方案**：
- 使用可复制文本的PDF文件
- 检查pdfplumber安装：`pip install pdfplumber`

### 问题2：优化功能不可用

**可能原因**：
- LLM服务未配置
- 通义千问API密钥无效
- 网络连接问题

**解决方案**：
- 检查`config/default.yaml`中的LLM配置
- 验证通义千问API密钥
- 检查网络连接

### 问题3：PDF生成失败

**可能原因**：
- WeasyPrint未安装
- Windows上缺少GTK+库

**解决方案**：
- 安装WeasyPrint：`pip install WeasyPrint`
- Windows上安装GTK+：参考[WeasyPrint文档](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)

## 📚 相关文档

- [API参考文档](../../api/api-reference.md#resume-api)
- [用户指南](../guides/resume-guide.md)
- [架构方案文档](../../AI框架架构方案文档.md)

---

**文档更新日期**: 2026-01-28
