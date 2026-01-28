# 简历功能使用指南

## 📋 概述

简历功能提供完整的简历优化、生成和美化服务，支持：
- **简历解析**：自动解析PDF、Word、JSON格式的简历文件
- **简历优化**：基于AI（通义千问）智能优化简历内容
- **简历生成**：使用专业模板生成HTML/PDF格式的简历
- **简历美化**：提供多种专业模板和样式选择

## 🚀 快速开始

### 1. 上传简历

支持三种格式：
- **PDF格式**：`.pdf`文件
- **Word格式**：`.docx`文件
- **JSON格式**：`.json`文件（结构化数据）

**前端操作**：
1. 访问`/resume`页面
2. 点击上传区域或拖拽文件
3. 等待解析完成

**API调用**：
```python
import httpx

async with httpx.AsyncClient() as client:
    with open("resume.pdf", "rb") as f:
        response = await client.post(
            "http://localhost:8000/api/v1/resume/parse",
            files={"file": ("resume.pdf", f, "application/pdf")}
        )
    result = response.json()
    resume_data = result["data"]
```

### 2. 优化简历

**基础优化**：
- 内容完整性检查
- 关键词匹配建议
- 基本语言润色

**高级优化**：
- 深度内容优化
- 量化成果建议
- 亮点提炼
- 专业语言润色
- 格式检查

**前端操作**：
1. 在优化区域选择优化级别
2. （可选）输入目标职位描述
3. 点击"开始优化"
4. 查看优化建议和评分

**API调用**：
```python
response = await client.post(
    "http://localhost:8000/api/v1/resume/optimize",
    json={
        "resume_data": resume_data,
        "job_description": "Python开发工程师，要求3年以上经验",
        "optimization_level": "advanced"
    }
)
result = response.json()
optimized_resume = result["data"]["optimized_resume"]
suggestions = result["data"]["suggestions"]
score = result["data"]["score"]
```

### 3. 选择模板

系统提供4种专业模板：
- **经典模板**：适合传统行业
- **现代模板**：现代简洁风格
- **创意模板**：适合创意行业
- **技术模板**：适合技术人员

**前端操作**：
1. 在模板选择区浏览可用模板
2. 点击模板卡片选择模板
3. 点击"生成简历"

**API调用**：
```python
# 获取模板列表
templates_response = await client.get("http://localhost:8000/api/v1/resume/templates")
templates = templates_response.json()["templates"]

# 生成简历
response = await client.post(
    "http://localhost:8000/api/v1/resume/generate",
    json={
        "resume_data": resume_data,
        "template_id": "classic",
        "output_format": "html"
    }
)
```

### 4. 导出简历

支持两种格式：
- **HTML格式**：可在浏览器中查看和编辑
- **PDF格式**：适合打印和投递

**前端操作**：
1. 在导出区选择格式
2. 点击"预览"查看效果
3. 点击"下载"保存文件

**API调用**：
```python
# 下载简历
file_id = "resume_123"
response = await client.get(
    f"http://localhost:8000/api/v1/resume/download/{file_id}"
)
with open("resume.pdf", "wb") as f:
    f.write(response.content)
```

## 📝 使用示例

### 完整流程示例

```python
import httpx
import asyncio

async def resume_workflow():
    """完整的简历处理流程"""
    async with httpx.AsyncClient() as client:
        base_url = "http://localhost:8000/api/v1"
        
        # Step 1: 解析简历
        with open("resume.pdf", "rb") as f:
            parse_response = await client.post(
                f"{base_url}/resume/parse",
                files={"file": ("resume.pdf", f, "application/pdf")}
            )
        resume_data = parse_response.json()["data"]
        print("✅ 简历解析成功")
        
        # Step 2: 优化简历
        optimize_response = await client.post(
            f"{base_url}/resume/optimize",
            json={
                "resume_data": resume_data,
                "job_description": "Python开发工程师",
                "optimization_level": "advanced"
            }
        )
        optimized_result = optimize_response.json()["data"]
        print(f"✅ 简历优化完成，评分: {optimized_result['score']}")
        
        # Step 3: 生成简历
        generate_response = await client.post(
            f"{base_url}/resume/generate",
            json={
                "resume_data": optimized_result["optimized_resume"],
                "template_id": "classic",
                "output_format": "pdf"
            }
        )
        file_id = generate_response.json()["file_id"]
        print(f"✅ 简历生成成功，文件ID: {file_id}")
        
        # Step 4: 下载简历
        download_response = await client.get(
            f"{base_url}/resume/download/{file_id}"
        )
        with open("optimized_resume.pdf", "wb") as f:
            f.write(download_response.content)
        print("✅ 简历下载完成")

asyncio.run(resume_workflow())
```

## 💡 最佳实践

### 1. 简历解析

- **PDF格式**：确保PDF文件可复制文本（非扫描版）
- **Word格式**：使用标准格式，避免复杂表格
- **JSON格式**：按照标准格式提供结构化数据

### 2. 简历优化

- **提供职位描述**：输入目标职位描述可获得更精准的优化建议
- **选择优化级别**：
  - 基础优化：快速检查和建议
  - 高级优化：深度分析和专业润色
- **查看优化建议**：仔细阅读优化建议，选择性采纳

### 3. 模板选择

- **根据行业选择**：传统行业选择经典模板，技术行业选择技术模板
- **预览效果**：生成后先预览，确认效果后再下载

### 4. 导出格式

- **HTML格式**：适合在线查看和进一步编辑
- **PDF格式**：适合打印和正式投递

## ❓ 常见问题

### Q1: 支持哪些文件格式？

A: 目前支持PDF、Word（.docx）和JSON三种格式。

### Q2: 优化功能需要多长时间？

A: 基础优化通常需要5-10秒，高级优化可能需要10-20秒（取决于LLM响应时间）。

### Q3: 如何提高优化效果？

A: 
- 提供详细的职位描述
- 选择高级优化级别
- 确保原始简历内容完整

### Q4: 可以自定义模板吗？

A: 当前版本支持使用预设模板。自定义模板功能正在开发中。

### Q5: PDF生成失败怎么办？

A: PDF生成需要WeasyPrint库，在Windows上还需要安装GTK+。请参考[WeasyPrint安装指南](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)。

## 📚 相关文档

- [API参考文档](../api/api-reference.md#resume-api) - 详细的API接口说明
- [开发文档](../development/resume-module.md) - 模块开发文档
- [架构方案文档](../../AI框架架构方案文档.md) - 整体架构设计

---

**文档更新日期**: 2026-01-28
