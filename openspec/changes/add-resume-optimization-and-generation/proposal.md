# Proposal: 简历优化和生成功能

## Change ID
`add-resume-optimization-and-generation`

## Status
- **Current**: Draft
- **Proposed**: 2026-01-28
- **Approved**: Pending
- **Implemented**: Pending

## Priority
P1 (High)

## Overview

### What Changes
添加完整的简历优化和生成功能，包括：
1. **简历解析模块**：支持PDF、Word、JSON格式的简历上传和解析
2. **简历优化模块**：基于阿里通义千问大模型进行内容优化和改进建议
3. **简历生成模块**：基于模板引擎生成HTML/PDF格式的简历
4. **简历美化模块**：提供多种专业模板和样式选择
5. **前端页面重构**：移除Agent页面，保留Chat和Vision页面，新增Resume页面

### Why This Change
1. **用户需求**：简历优化是AI应用的高频场景，可以显著提升用户价值
2. **技术整合**：充分利用现有的LLM服务（通义千问）和Vision服务能力
3. **产品定位**：将框架从通用AI工具扩展到垂直场景应用
4. **前端优化**：简化界面，聚焦核心功能（对话、图片识别、简历优化）

### Impact
- **用户影响**：新增简历优化功能，移除Agent页面（简化界面）
- **开发影响**：新增Resume服务模块，前端路由和页面调整
- **性能影响**：PDF生成可能消耗较多资源，需要异步处理
- **兼容性影响**：前端移除Agent页面，需要更新路由和导航

## Motivation

### Business Value
1. **垂直场景落地**：从通用AI框架到实际应用场景
2. **用户价值提升**：解决简历优化的真实需求
3. **产品差异化**：结合AI能力的简历工具

### Technical Value
1. **模块化设计**：简历功能作为独立模块，易于扩展
2. **技术整合**：整合LLM、文档处理、模板引擎等技术
3. **架构验证**：验证框架的垂直场景适配能力

## Detailed Design

### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                     前端层 (Frontend)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Chat     │  │ Vision   │  │ Resume   │               │
│  │ 页面     │  │ 页面     │  │ 页面     │               │
│  └──────────┘  └──────────┘  └──────────┘               │
│  (移除Agent页面)                                          │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                     API层 (API Routes)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ LLM      │  │ Vision   │  │ Resume   │               │
│  │ Routes   │  │ Routes   │  │ Routes   │               │
│  └──────────┘  └──────────┘  └──────────┘               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   服务层 (Service Layer)                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │ ResumeService (简历服务)                          │   │
│  │ - parse_resume()     # 解析简历                  │   │
│  │ - optimize_resume()  # 优化简历                  │   │
│  │ - generate_resume()  # 生成简历                  │   │
│  │ - beautify_resume()  # 美化简历                  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Resume   │  │ Resume   │  │ Resume   │  │ Resume   ││
│  │ Parser   │  │Optimizer │  │Generator │  │Template  ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   依赖层 (Dependencies)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ 通义千问 │  │ PyPDF2   │  │WeasyPrint│  │ Jinja2   ││
│  │ LLM      │  │python-   │  │ReportLab │  │ 模板引擎 ││
│  │          │  │docx      │  │          │  │          ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
```

### 核心模块设计

#### 1. ResumeService (简历服务)
- **职责**：统一的简历处理接口
- **方法**：
  - `parse_resume(file, format)`: 解析简历文件
  - `optimize_resume(resume_data, job_description)`: 优化简历内容
  - `generate_resume(resume_data, template_id)`: 生成简历文件
  - `list_templates()`: 列出可用模板

#### 2. ResumeParser (简历解析器)
- **职责**：解析不同格式的简历文件
- **支持格式**：
  - PDF: 使用PyPDF2或pdfplumber提取文本
  - Word: 使用python-docx提取内容
  - JSON: 直接解析结构化数据
- **输出**：统一的简历数据结构（JSON Schema）

#### 3. ResumeOptimizer (简历优化器)
- **职责**：基于LLM优化简历内容
- **使用模型**：阿里通义千问（qwen-max或qwen-plus）
- **优化维度**：
  - 内容完整性检查
  - 语言表达优化
  - 关键词优化（针对岗位描述）
  - 格式规范建议
  - 亮点提炼
- **输出**：优化建议列表 + 优化后的内容

#### 4. ResumeGenerator (简历生成器)
- **职责**：基于模板生成简历文件
- **模板引擎**：Jinja2
- **生成流程**：
  1. 加载模板（HTML模板）
  2. 渲染数据到模板
  3. 生成HTML
  4. 转换为PDF（使用WeasyPrint或ReportLab）
- **输出**：HTML文件 + PDF文件

#### 5. ResumeTemplate (模板管理器)
- **职责**：管理简历模板
- **模板类型**：
  - 经典模板（传统格式）
  - 现代模板（简洁设计）
  - 创意模板（个性化设计）
  - 技术模板（适合技术岗位）
- **模板结构**：
  - HTML模板文件
  - CSS样式文件
  - 模板元数据（名称、描述、预览图）

### 数据模型设计

#### ResumeData (简历数据模型)
```python
class ResumeData(BaseModel):
    """简历数据模型"""
    # 基本信息
    basic_info: BasicInfo
    # 教育经历
    education: List[Education]
    # 工作经历
    work_experience: List[WorkExperience]
    # 项目经历
    projects: List[Project]
    # 技能
    skills: List[Skill]
    # 证书
    certificates: List[Certificate]
    # 其他
    others: Optional[Dict[str, Any]]

class BasicInfo(BaseModel):
    """基本信息"""
    name: str
    email: str
    phone: str
    location: Optional[str]
    summary: Optional[str]
    avatar: Optional[str]

class Education(BaseModel):
    """教育经历"""
    school: str
    degree: str
    major: str
    start_date: str
    end_date: str
    gpa: Optional[str]
    achievements: Optional[List[str]]

class WorkExperience(BaseModel):
    """工作经历"""
    company: str
    position: str
    start_date: str
    end_date: str
    description: str
    achievements: List[str]

class Project(BaseModel):
    """项目经历"""
    name: str
    role: str
    start_date: str
    end_date: str
    description: str
    technologies: List[str]
    achievements: List[str]

class Skill(BaseModel):
    """技能"""
    category: str  # 技能类别
    items: List[str]  # 技能项

class Certificate(BaseModel):
    """证书"""
    name: str
    issuer: str
    date: str
```

#### OptimizationResult (优化结果模型)
```python
class OptimizationResult(BaseModel):
    """优化结果"""
    optimized_resume: ResumeData
    suggestions: List[Suggestion]
    score: float  # 简历评分 0-100

class Suggestion(BaseModel):
    """优化建议"""
    category: str  # 建议类别
    severity: str  # 严重程度: high/medium/low
    description: str  # 建议描述
    original: Optional[str]  # 原始内容
    optimized: Optional[str]  # 优化后内容
```

### API设计

#### 简历上传和解析
```
POST /api/v1/resume/parse
Content-Type: multipart/form-data

Request:
- file: 简历文件 (PDF/Word/JSON)
- format: 文件格式 (pdf/docx/json)

Response:
{
  "resume_data": ResumeData,
  "parse_status": "success",
  "message": "简历解析成功"
}
```

#### 简历优化
```
POST /api/v1/resume/optimize
Content-Type: application/json

Request:
{
  "resume_data": ResumeData,
  "job_description": "岗位描述（可选）",
  "optimization_level": "basic/advanced"
}

Response:
{
  "result": OptimizationResult,
  "status": "success"
}
```

#### 简历生成
```
POST /api/v1/resume/generate
Content-Type: application/json

Request:
{
  "resume_data": ResumeData,
  "template_id": "classic/modern/creative/tech",
  "format": "html/pdf"
}

Response:
{
  "file_url": "/api/v1/resume/download/{file_id}",
  "preview_url": "/api/v1/resume/preview/{file_id}",
  "status": "success"
}
```

#### 模板列表
```
GET /api/v1/resume/templates

Response:
{
  "templates": [
    {
      "id": "classic",
      "name": "经典模板",
      "description": "传统简历格式",
      "preview_image": "/templates/classic/preview.png"
    },
    ...
  ]
}
```

### 前端页面设计

#### Resume页面结构
```
Resume.vue
├── 上传区域 (ResumeUpload.vue)
│   ├── 文件拖拽上传
│   ├── 格式选择 (PDF/Word/JSON)
│   └── 上传按钮
├── 解析结果展示 (ResumePreview.vue)
│   ├── 基本信息
│   ├── 教育经历
│   ├── 工作经历
│   ├── 项目经历
│   └── 技能证书
├── 优化区域 (ResumeOptimization.vue)
│   ├── 岗位描述输入（可选）
│   ├── 优化级别选择
│   ├── 优化按钮
│   └── 优化建议展示
├── 模板选择 (TemplateSelector.vue)
│   ├── 模板列表
│   ├── 模板预览
│   └── 模板选择
└── 导出区域 (ResumeExport.vue)
    ├── 格式选择 (HTML/PDF)
    ├── 预览按钮
    └── 下载按钮
```

#### 前端路由调整
```typescript
// 移除Agent路由
// 保留Chat和Vision路由
// 新增Resume路由

const routes = [
  { path: '/', component: Home },
  { path: '/chat', component: Chat },
  { path: '/vision', component: Vision },
  { path: '/resume', component: Resume },  // 新增
]
```

### 技术选型

#### 后端依赖
- **LLM服务**：通义千问（qwen-max或qwen-plus）
  - 用于简历内容优化和建议生成
  - 复用现有的QwenAdapter
- **文档解析**：
  - PyPDF2 或 pdfplumber：PDF解析
  - python-docx：Word文档解析
- **PDF生成**：
  - WeasyPrint：HTML转PDF（推荐，支持CSS）
  - 或 ReportLab：直接生成PDF（更灵活）
- **模板引擎**：
  - Jinja2：HTML模板渲染

#### 前端依赖
- **文件上传**：
  - 复用现有的文件上传组件
  - 支持拖拽上传
- **富文本编辑**：
  - Quill 或 TinyMCE（用于编辑简历内容）
- **PDF预览**：
  - PDF.js（浏览器内预览PDF）

### 配置示例

```yaml
# config/default.yaml
resume:
  # LLM配置（使用通义千问）
  llm:
    provider: "qwen"
    model: "qwen-max"  # 或 qwen-plus
    temperature: 0.7
    max_tokens: 2000
  
  # 解析配置
  parser:
    max_file_size: 10485760  # 10MB
    supported_formats: ["pdf", "docx", "json"]
  
  # 生成配置
  generator:
    output_dir: "data/resumes/generated"
    pdf_engine: "weasyprint"  # weasyprint/reportlab
    default_template: "modern"
  
  # 模板配置
  templates:
    dir: "core/resume/templates"
    available: ["classic", "modern", "creative", "tech"]
```

## Implementation Plan

### Phase 1: 后端核心模块（1周）
1. 实现ResumeService基础框架
2. 实现ResumeParser（支持PDF、Word、JSON）
3. 实现ResumeOptimizer（集成通义千问）
4. 定义数据模型和API接口

### Phase 2: 简历生成和模板（1周）
1. 实现ResumeGenerator（HTML渲染 + PDF转换）
2. 实现ResumeTemplate管理器
3. 创建4个基础模板（经典、现代、创意、技术）
4. 实现模板预览和选择

### Phase 3: API和路由（3天）
1. 实现Resume API路由
2. 实现文件上传和下载
3. 实现API依赖注入
4. 编写API单元测试

### Phase 4: 前端页面（1周）
1. 移除Agent页面和路由
2. 创建Resume页面和子组件
3. 实现文件上传和解析
4. 实现优化建议展示
5. 实现模板选择和预览
6. 实现导出和下载

### Phase 5: 测试和文档（3天）
1. 编写单元测试（覆盖率80%+）
2. 编写集成测试
3. 更新API文档
4. 更新用户指南
5. 更新项目计划

## Testing Strategy

### 单元测试
- ResumeParser测试（各种格式）
- ResumeOptimizer测试（Mock LLM）
- ResumeGenerator测试（模板渲染）
- ResumeTemplate测试（模板加载）

### 集成测试
- 完整简历处理流程测试
- API接口测试
- 文件上传下载测试

### 端到端测试
- 前端上传 → 解析 → 优化 → 生成 → 下载

## Documentation

### 需要更新的文档
1. **API文档**：新增Resume API接口文档
2. **用户指南**：新增简历功能使用教程
3. **开发文档**：新增Resume模块开发文档
4. **项目计划**：更新完成状态

## Risks and Mitigations

### 风险1：PDF生成性能问题
- **风险**：PDF生成可能消耗较多CPU和内存
- **缓解**：使用异步任务队列，限制并发数量

### 风险2：简历解析准确性
- **风险**：不同格式的简历解析可能不准确
- **缓解**：提供手动编辑功能，支持JSON导入导出

### 风险3：LLM优化质量
- **风险**：LLM优化建议可能不符合预期
- **缓解**：提供多个优化级别，用户可选择是否采纳

### 风险4：前端兼容性
- **风险**：移除Agent页面可能影响现有用户
- **缓解**：提前通知，提供迁移指南

## Alternatives Considered

### 方案1：使用OpenAI GPT-4
- **优点**：效果可能更好
- **缺点**：成本高，不符合"尽量使用阿里系"的要求
- **决策**：不采用

### 方案2：使用第三方简历解析API
- **优点**：解析准确性高
- **缺点**：依赖外部服务，成本高
- **决策**：不采用，自研解析器

### 方案3：使用LaTeX生成简历
- **优点**：排版质量高
- **缺点**：学习成本高，不易维护
- **决策**：不采用，使用HTML+CSS+PDF转换

## Success Criteria

### 功能完整性
- [x] 支持PDF、Word、JSON格式解析
- [x] 基于通义千问的内容优化
- [x] 提供至少4个专业模板
- [x] 支持HTML和PDF导出
- [x] 前端页面完整（上传、优化、模板、导出）

### 性能指标
- [x] 简历解析时间 < 5秒
- [x] 优化建议生成时间 < 10秒
- [x] PDF生成时间 < 5秒
- [x] 支持最大10MB文件

### 质量指标
- [x] 单元测试覆盖率 > 80%
- [x] API响应成功率 > 99%
- [x] 用户满意度 > 4.0/5.0

## Rollout Plan

### 阶段1：内部测试（1周）
- 开发团队内部测试
- 修复关键bug

### 阶段2：Beta测试（1周）
- 邀请部分用户测试
- 收集反馈和优化

### 阶段3：正式发布
- 发布到生产环境
- 监控性能和错误

## Related Changes

### 依赖的变更
- 无（复用现有LLM服务和Vision服务）

### 相关的变更
- 前端路由调整（移除Agent页面）
- 导航菜单更新

## Approval

### Reviewers
- [ ] 架构师
- [ ] 后端开发负责人
- [ ] 前端开发负责人
- [ ] 测试负责人

### Sign-off
- [ ] 产品负责人
- [ ] 技术负责人

---

**提案创建日期**：2026-01-28
**提案创建人**：AI Framework Architect
**最后更新日期**：2026-01-28
