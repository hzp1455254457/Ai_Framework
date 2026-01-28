# Spec: Resume Service

## Capability
`resume-service`

## Operation
`ADDED`

## Overview
简历优化和生成服务，提供简历解析、优化、生成和模板管理功能。

---

## ADDED Requirements

### Requirement: 简历解析功能 (REQ-RESUME-001)
**描述**：系统SHALL支持解析PDF、Word、JSON格式的简历文件，提取结构化数据

**优先级**：P1

**验收标准**：
- 支持PDF格式解析（使用pdfplumber）
- 支持Word格式解析（使用python-docx）
- 支持JSON格式解析（直接加载）
- 提取基本信息、教育经历、工作经历、项目经历、技能、证书
- 支持最大10MB文件
- 解析时间 < 5秒

#### Scenario: 上传并解析PDF简历

用户上传PDF格式的简历，系统解析并提取结构化数据。

**前置条件**：
- 用户已准备好PDF格式的简历文件
- 文件大小 < 10MB

**操作步骤**：
1. 用户在前端选择PDF文件
2. 前端调用POST /api/v1/resume/parse接口，上传文件
3. 后端ResumeService接收请求
4. ResumeParser解析PDF文件，提取文本和结构化数据
5. 返回ResumeData结构化数据

**预期结果**：
- 解析成功，返回完整的ResumeData
- 包含基本信息、教育经历、工作经历、项目经历、技能、证书
- 解析时间 < 5秒

**示例请求**：
```http
POST /api/v1/resume/parse
Content-Type: multipart/form-data

file: resume.pdf
format: pdf
```

**示例响应**：
```json
{
  "resume_data": {
    "basic_info": {
      "name": "张三",
      "email": "zhangsan@example.com",
      "phone": "13800138000"
    },
    "education": [...],
    "work_experience": [...],
    "projects": [...],
    "skills": [...],
    "certificates": [...]
  },
  "parse_status": "success",
  "message": "简历解析成功"
}
```

### Requirement: 简历优化功能 (REQ-RESUME-002)
**描述**：系统SHALL基于通义千问大模型优化简历内容，提供改进建议

**优先级**：P1

**验收标准**：
- 使用通义千问qwen-max或qwen-plus模型
- 支持基础优化和高级优化
- 支持针对岗位描述的优化（可选）
- 提供优化建议列表和简历评分
- 优化时间 < 10秒

#### Scenario: 优化简历内容

用户提供简历数据和岗位描述，系统基于通义千问优化简历内容。

**前置条件**：
- 用户已上传并解析简历
- 系统已配置通义千问API密钥

**操作步骤**：
1. 用户在前端输入岗位描述（可选）
2. 用户选择优化级别（基础/高级）
3. 前端调用POST /api/v1/resume/optimize接口
4. 后端ResumeOptimizer构建优化提示词
5. 调用通义千问LLM（qwen-max）
6. 解析LLM响应，提取优化建议和优化后内容
7. 返回OptimizationResult

**预期结果**：
- 优化成功，返回优化建议列表
- 返回优化后的简历内容
- 返回简历评分（0-100）
- 优化时间 < 10秒

**示例请求**：
```http
POST /api/v1/resume/optimize
Content-Type: application/json

{
  "resume_data": {...},
  "job_description": "招聘高级Java开发工程师...",
  "optimization_level": "advanced"
}
```

**示例响应**：
```json
{
  "result": {
    "optimized_resume": {...},
    "suggestions": [
      {
        "category": "工作经历",
        "severity": "high",
        "description": "建议添加量化数据"
      }
    ],
    "score": 85.5
  },
  "status": "success"
}
```

### Requirement: 简历生成功能 (REQ-RESUME-003)
**描述**：系统SHALL基于模板生成HTML和PDF格式的简历文件

**优先级**：P1

**验收标准**：
- 使用Jinja2模板引擎渲染HTML
- 使用WeasyPrint转换HTML为PDF
- 支持HTML和PDF两种输出格式
- 提供文件下载URL和预览URL
- 生成时间 < 5秒

#### Scenario: 生成PDF简历

用户选择模板，系统生成PDF格式的简历文件。

**前置条件**：
- 用户已上传并解析简历
- 用户已选择模板

**操作步骤**：
1. 用户在前端选择模板（如"modern"）
2. 用户选择输出格式（PDF）
3. 前端调用POST /api/v1/resume/generate接口
4. 后端ResumeTemplate获取模板路径
5. ResumeGenerator使用Jinja2渲染HTML
6. 使用WeasyPrint转换HTML为PDF
7. 保存文件并返回下载URL

**预期结果**：
- 生成成功，返回文件下载URL和预览URL
- 生成的PDF排版美观、可打印
- 生成时间 < 5秒

**示例请求**：
```http
POST /api/v1/resume/generate
Content-Type: application/json

{
  "resume_data": {...},
  "template_id": "modern",
  "format": "pdf"
}
```

**示例响应**：
```json
{
  "file_url": "/api/v1/resume/download/abc123",
  "preview_url": "/api/v1/resume/preview/abc123",
  "status": "success"
}
```

### Requirement: 模板管理功能 (REQ-RESUME-004)
**描述**：系统SHALL管理简历模板，提供多种专业模板选择

**优先级**：P1

**验收标准**：
- 提供至少4个专业模板（经典、现代、创意、技术）
- 每个模板包含HTML模板、CSS样式、元数据、预览图
- 支持模板列表查询和预览
- 模板易于扩展

#### Scenario: 查询模板列表

用户查询可用的简历模板列表。

**前置条件**：
- 系统已配置至少4个模板

**操作步骤**：
1. 前端调用GET /api/v1/resume/templates接口
2. 后端ResumeTemplate加载模板元数据
3. 返回模板列表

**预期结果**：
- 返回至少4个模板（classic、modern、creative、tech）
- 每个模板包含ID、名称、描述、预览图URL

**示例请求**：
```http
GET /api/v1/resume/templates
```

**示例响应**：
```json
{
  "templates": [
    {
      "id": "classic",
      "name": "经典模板",
      "description": "传统简历格式",
      "preview_image": "/templates/classic/preview.png"
    },
    {
      "id": "modern",
      "name": "现代模板",
      "description": "简洁现代设计",
      "preview_image": "/templates/modern/preview.png"
    }
  ]
}
```

---

**规格创建日期**：2026-01-28
**规格创建人**：AI Framework Architect
**最后更新日期**：2026-01-28
