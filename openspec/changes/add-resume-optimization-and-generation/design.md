# Design Document: 简历优化和生成功能

## Change ID
`add-resume-optimization-and-generation`

## Overview
本文档详细描述简历优化和生成功能的技术设计，包括架构设计、模块设计、数据流设计、接口设计等。

---

## 1. 架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端层 (Ai_Web)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Chat.vue     │  │ Vision.vue   │  │ Resume.vue   │          │
│  │ (对话)       │  │ (图片识别)   │  │ (简历优化)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  移除: Agent.vue                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP API
┌─────────────────────────────────────────────────────────────────┐
│                        API层 (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ /api/v1/llm  │  │ /api/v1/     │  │ /api/v1/     │          │
│  │              │  │ vision       │  │ resume       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      服务层 (Service Layer)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ResumeService (继承BaseService)                           │  │
│  │ - parse_resume()      # 解析简历                         │  │
│  │ - optimize_resume()   # 优化简历（调用LLMService）       │  │
│  │ - generate_resume()   # 生成简历                         │  │
│  │ - list_templates()    # 列出模板                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Resume   │  │ Resume   │  │ Resume   │  │ Resume   │       │
│  │ Parser   │  │Optimizer │  │Generator │  │Template  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      依赖层 (Dependencies)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ LLM      │  │ PyPDF2   │  │WeasyPrint│  │ Jinja2   │       │
│  │ Service  │  │pdfplumber│  │          │  │          │       │
│  │(通义千问)│  │python-   │  │          │  │          │       │
│  │          │  │docx      │  │          │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 模块职责划分

| 模块 | 职责 | 依赖 |
|------|------|------|
| ResumeService | 简历服务统一入口 | Parser, Optimizer, Generator, Template |
| ResumeParser | 解析不同格式的简历文件 | PyPDF2, python-docx |
| ResumeOptimizer | 基于LLM优化简历内容 | LLMService (通义千问) |
| ResumeGenerator | 基于模板生成简历文件 | Jinja2, WeasyPrint |
| ResumeTemplate | 管理简历模板 | 无 |

---

## 2. 模块详细设计

### 2.1 ResumeService

#### 类定义
```python
class ResumeService(BaseService):
    """简历服务主类"""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        llm_service: LLMService,
        log_manager: LogManager
    ):
        super().__init__(config_manager, log_manager)
        self.llm_service = llm_service
        self.parser = ResumeParser(config_manager, log_manager)
        self.optimizer = ResumeOptimizer(llm_service, log_manager)
        self.generator = ResumeGenerator(config_manager, log_manager)
        self.template_manager = ResumeTemplate(config_manager, log_manager)
    
    async def parse_resume(
        self,
        file_path: str,
        file_format: str
    ) -> ResumeData:
        """解析简历文件"""
        pass
    
    async def optimize_resume(
        self,
        resume_data: ResumeData,
        job_description: Optional[str] = None,
        optimization_level: str = "basic"
    ) -> OptimizationResult:
        """优化简历内容"""
        pass
    
    async def generate_resume(
        self,
        resume_data: ResumeData,
        template_id: str,
        output_format: str = "pdf"
    ) -> str:
        """生成简历文件"""
        pass
    
    def list_templates(self) -> List[TemplateInfo]:
        """列出可用模板"""
        pass
```

#### 设计决策
1. **继承BaseService**：复用基础服务框架（配置、日志、生命周期）
2. **依赖注入**：通过构造函数注入LLMService，便于测试和替换
3. **模块组合**：组合Parser、Optimizer、Generator、Template四个子模块
4. **异步设计**：所有IO操作使用异步方法

### 2.2 ResumeParser

#### 类定义
```python
class ResumeParser:
    """简历解析器"""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        log_manager: LogManager
    ):
        self.config = config_manager.get("resume.parser", {})
        self.logger = log_manager.get_logger("resume.parser")
        self.max_file_size = self.config.get("max_file_size", 10485760)
    
    async def parse(
        self,
        file_path: str,
        file_format: str
    ) -> ResumeData:
        """解析简历文件"""
        if file_format == "pdf":
            return await self._parse_pdf(file_path)
        elif file_format == "docx":
            return await self._parse_docx(file_path)
        elif file_format == "json":
            return await self._parse_json(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_format}")
    
    async def _parse_pdf(self, file_path: str) -> ResumeData:
        """解析PDF文件"""
        # 使用PyPDF2或pdfplumber提取文本
        # 使用正则表达式或NLP提取结构化信息
        pass
    
    async def _parse_docx(self, file_path: str) -> ResumeData:
        """解析Word文件"""
        # 使用python-docx提取内容
        # 解析段落和表格
        pass
    
    async def _parse_json(self, file_path: str) -> ResumeData:
        """解析JSON文件"""
        # 直接加载JSON并验证
        pass
```

#### 解析策略

**PDF解析**：
1. 使用pdfplumber提取文本（保留布局信息）
2. 使用正则表达式识别关键字段（姓名、邮箱、电话等）
3. 使用NLP技术（可选）提取工作经历、项目经历等
4. 如果解析失败，返回原始文本供用户手动编辑

**Word解析**：
1. 使用python-docx提取段落和表格
2. 根据标题和格式识别各个部分
3. 提取结构化数据

**JSON解析**：
1. 直接加载JSON文件
2. 使用Pydantic验证数据格式
3. 如果格式不符，返回错误提示

### 2.3 ResumeOptimizer

#### 类定义
```python
class ResumeOptimizer:
    """简历优化器"""
    
    def __init__(
        self,
        llm_service: LLMService,
        log_manager: LogManager
    ):
        self.llm_service = llm_service
        self.logger = log_manager.get_logger("resume.optimizer")
    
    async def optimize(
        self,
        resume_data: ResumeData,
        job_description: Optional[str] = None,
        optimization_level: str = "basic"
    ) -> OptimizationResult:
        """优化简历内容"""
        # 1. 构建优化提示词
        prompt = self._build_optimization_prompt(
            resume_data,
            job_description,
            optimization_level
        )
        
        # 2. 调用通义千问LLM
        response = await self.llm_service.chat(
            messages=[{"role": "user", "content": prompt}],
            model="qwen-max"  # 或 qwen-plus
        )
        
        # 3. 解析LLM响应
        result = self._parse_optimization_result(response.content)
        
        return result
    
    def _build_optimization_prompt(
        self,
        resume_data: ResumeData,
        job_description: Optional[str],
        optimization_level: str
    ) -> str:
        """构建优化提示词"""
        # 根据优化级别构建不同的提示词
        pass
    
    def _parse_optimization_result(
        self,
        llm_response: str
    ) -> OptimizationResult:
        """解析LLM响应"""
        # 解析LLM返回的优化建议和优化后的内容
        pass
```

#### 优化策略

**基础优化（basic）**：
- 检查基本信息完整性
- 检查语法和拼写错误
- 检查格式规范
- 提供基本改进建议

**高级优化（advanced）**：
- 基础优化 +
- 针对岗位描述优化关键词
- 提炼工作亮点和成就
- 优化语言表达（更专业、更有说服力）
- 提供详细的改进建议和示例

**提示词模板**：
```
你是一位专业的简历优化专家。请帮我优化以下简历内容。

【简历内容】
{resume_content}

【岗位描述】（如果提供）
{job_description}

【优化要求】
1. 检查基本信息完整性
2. 优化语言表达，使其更专业、更有说服力
3. 提炼工作亮点和成就，使用量化数据
4. 针对岗位描述优化关键词（如果提供）
5. 提供具体的改进建议

【输出格式】
请以JSON格式输出优化结果，包括：
- optimized_resume: 优化后的简历内容
- suggestions: 优化建议列表
- score: 简历评分（0-100）
```

### 2.4 ResumeGenerator

#### 类定义
```python
class ResumeGenerator:
    """简历生成器"""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        log_manager: LogManager
    ):
        self.config = config_manager.get("resume.generator", {})
        self.logger = log_manager.get_logger("resume.generator")
        self.output_dir = self.config.get("output_dir", "data/resumes/generated")
        self.pdf_engine = self.config.get("pdf_engine", "weasyprint")
    
    async def generate(
        self,
        resume_data: ResumeData,
        template_path: str,
        output_format: str = "pdf"
    ) -> str:
        """生成简历文件"""
        # 1. 渲染HTML模板
        html_content = await self._render_template(resume_data, template_path)
        
        # 2. 保存HTML文件
        html_file = await self._save_html(html_content)
        
        # 3. 如果需要PDF，转换HTML为PDF
        if output_format == "pdf":
            pdf_file = await self._convert_to_pdf(html_file)
            return pdf_file
        
        return html_file
    
    async def _render_template(
        self,
        resume_data: ResumeData,
        template_path: str
    ) -> str:
        """渲染Jinja2模板"""
        from jinja2 import Environment, FileSystemLoader
        
        env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
        template = env.get_template(os.path.basename(template_path))
        html_content = template.render(resume=resume_data.dict())
        
        return html_content
    
    async def _save_html(self, html_content: str) -> str:
        """保存HTML文件"""
        import aiofiles
        
        file_id = str(uuid.uuid4())
        file_path = os.path.join(self.output_dir, f"{file_id}.html")
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(html_content)
        
        return file_path
    
    async def _convert_to_pdf(self, html_file: str) -> str:
        """转换HTML为PDF"""
        if self.pdf_engine == "weasyprint":
            return await self._convert_with_weasyprint(html_file)
        elif self.pdf_engine == "reportlab":
            return await self._convert_with_reportlab(html_file)
        else:
            raise ValueError(f"Unsupported PDF engine: {self.pdf_engine}")
    
    async def _convert_with_weasyprint(self, html_file: str) -> str:
        """使用WeasyPrint转换"""
        from weasyprint import HTML
        
        pdf_file = html_file.replace('.html', '.pdf')
        HTML(html_file).write_pdf(pdf_file)
        
        return pdf_file
```

#### 生成流程

```
ResumeData + Template
        ↓
  Jinja2渲染
        ↓
   HTML文件
        ↓
  (可选) PDF转换
        ↓
   输出文件
```

### 2.5 ResumeTemplate

#### 类定义
```python
class ResumeTemplate:
    """简历模板管理器"""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        log_manager: LogManager
    ):
        self.config = config_manager.get("resume.templates", {})
        self.logger = log_manager.get_logger("resume.template")
        self.template_dir = self.config.get("dir", "core/resume/templates")
        self.available_templates = self.config.get("available", [])
    
    def list_templates(self) -> List[TemplateInfo]:
        """列出可用模板"""
        templates = []
        for template_id in self.available_templates:
            template_info = self._load_template_info(template_id)
            templates.append(template_info)
        return templates
    
    def get_template_path(self, template_id: str) -> str:
        """获取模板路径"""
        return os.path.join(self.template_dir, template_id, "template.html")
    
    def _load_template_info(self, template_id: str) -> TemplateInfo:
        """加载模板信息"""
        metadata_path = os.path.join(
            self.template_dir,
            template_id,
            "metadata.json"
        )
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        return TemplateInfo(
            id=template_id,
            name=metadata['name'],
            description=metadata['description'],
            preview_image=metadata['preview_image']
        )
```

#### 模板结构

```
core/resume/templates/
├── classic/                 # 经典模板
│   ├── template.html       # HTML模板
│   ├── style.css           # CSS样式
│   ├── metadata.json       # 模板元数据
│   └── preview.png         # 预览图
├── modern/                  # 现代模板
│   ├── template.html
│   ├── style.css
│   ├── metadata.json
│   └── preview.png
├── creative/                # 创意模板
│   ├── template.html
│   ├── style.css
│   ├── metadata.json
│   └── preview.png
└── tech/                    # 技术模板
    ├── template.html
    ├── style.css
    ├── metadata.json
    └── preview.png
```

---

## 3. 数据流设计

### 3.1 简历解析流程

```
用户上传文件
    ↓
前端 → POST /api/v1/resume/parse
    ↓
API层 → ResumeService.parse_resume()
    ↓
ResumeParser.parse()
    ↓
根据格式选择解析器
    ↓
提取文本和结构化数据
    ↓
返回 ResumeData
    ↓
前端展示解析结果
```

### 3.2 简历优化流程

```
用户点击优化按钮
    ↓
前端 → POST /api/v1/resume/optimize
    ↓
API层 → ResumeService.optimize_resume()
    ↓
ResumeOptimizer.optimize()
    ↓
构建优化提示词
    ↓
调用LLMService (通义千问)
    ↓
解析LLM响应
    ↓
返回 OptimizationResult
    ↓
前端展示优化建议
```

### 3.3 简历生成流程

```
用户选择模板和格式
    ↓
前端 → POST /api/v1/resume/generate
    ↓
API层 → ResumeService.generate_resume()
    ↓
ResumeTemplate.get_template_path()
    ↓
ResumeGenerator.generate()
    ↓
Jinja2渲染HTML
    ↓
(可选) WeasyPrint转换PDF
    ↓
保存文件并返回URL
    ↓
前端下载或预览
```

---

## 4. API设计

### 4.1 API路由

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/resume/parse | 解析简历文件 |
| POST | /api/v1/resume/optimize | 优化简历内容 |
| POST | /api/v1/resume/generate | 生成简历文件 |
| GET | /api/v1/resume/templates | 列出可用模板 |
| GET | /api/v1/resume/download/{file_id} | 下载生成的文件 |
| GET | /api/v1/resume/preview/{file_id} | 预览生成的文件 |

### 4.2 请求/响应模型

#### ParseResumeRequest
```python
class ParseResumeRequest(BaseModel):
    """解析简历请求"""
    file: UploadFile  # 文件
    format: str  # pdf/docx/json
```

#### ParseResumeResponse
```python
class ParseResumeResponse(BaseModel):
    """解析简历响应"""
    resume_data: ResumeData
    parse_status: str
    message: str
```

#### OptimizeResumeRequest
```python
class OptimizeResumeRequest(BaseModel):
    """优化简历请求"""
    resume_data: ResumeData
    job_description: Optional[str] = None
    optimization_level: str = "basic"  # basic/advanced
```

#### OptimizeResumeResponse
```python
class OptimizeResumeResponse(BaseModel):
    """优化简历响应"""
    result: OptimizationResult
    status: str
```

#### GenerateResumeRequest
```python
class GenerateResumeRequest(BaseModel):
    """生成简历请求"""
    resume_data: ResumeData
    template_id: str
    format: str = "pdf"  # html/pdf
```

#### GenerateResumeResponse
```python
class GenerateResumeResponse(BaseModel):
    """生成简历响应"""
    file_url: str
    preview_url: str
    status: str
```

---

## 5. 前端设计

### 5.1 页面结构

```
Resume.vue
├── <div class="resume-container">
│   ├── <div class="upload-section">
│   │   └── <ResumeUpload />
│   ├── <div class="preview-section">
│   │   └── <ResumePreview :resume-data="resumeData" />
│   ├── <div class="optimization-section">
│   │   └── <ResumeOptimization :resume-data="resumeData" />
│   ├── <div class="template-section">
│   │   └── <TemplateSelector :templates="templates" />
│   └── <div class="export-section">
│       └── <ResumeExport :resume-data="resumeData" />
```

### 5.2 组件设计

#### ResumeUpload.vue
```vue
<template>
  <div class="upload-container">
    <div class="upload-area" @drop="handleDrop" @dragover.prevent>
      <input type="file" @change="handleFileSelect" accept=".pdf,.docx,.json" />
      <p>拖拽文件到此处或点击上传</p>
      <p>支持格式：PDF、Word、JSON</p>
    </div>
    <button @click="parseResume">解析简历</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { resumeApi } from '@/api/endpoints/resume'

const file = ref<File | null>(null)

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    file.value = target.files[0]
  }
}

const parseResume = async () => {
  if (!file.value) return
  
  const formData = new FormData()
  formData.append('file', file.value)
  formData.append('format', getFileFormat(file.value.name))
  
  const result = await resumeApi.parse(formData)
  // 处理解析结果
}
</script>
```

#### ResumeOptimization.vue
```vue
<template>
  <div class="optimization-container">
    <textarea v-model="jobDescription" placeholder="输入岗位描述（可选）"></textarea>
    <select v-model="optimizationLevel">
      <option value="basic">基础优化</option>
      <option value="advanced">高级优化</option>
    </select>
    <button @click="optimizeResume">优化简历</button>
    
    <div v-if="optimizationResult" class="suggestions">
      <h3>优化建议</h3>
      <div v-for="suggestion in optimizationResult.suggestions" :key="suggestion.id">
        <p>{{ suggestion.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { resumeApi } from '@/api/endpoints/resume'

const jobDescription = ref('')
const optimizationLevel = ref('basic')
const optimizationResult = ref(null)

const optimizeResume = async () => {
  const result = await resumeApi.optimize({
    resume_data: props.resumeData,
    job_description: jobDescription.value,
    optimization_level: optimizationLevel.value
  })
  optimizationResult.value = result
}
</script>
```

### 5.3 路由调整

```typescript
// src/router/index.ts

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat.vue')
  },
  {
    path: '/vision',
    name: 'Vision',
    component: () => import('@/views/Vision.vue')
  },
  {
    path: '/resume',
    name: 'Resume',
    component: () => import('@/views/Resume.vue')
  }
  // 移除 Agent 路由
]
```

---

## 6. 依赖管理

### 6.1 后端依赖

```txt
# requirements.txt 新增依赖

# 文档解析
PyPDF2==3.0.1
pdfplumber==0.10.3
python-docx==1.1.0

# PDF生成
WeasyPrint==60.1
# 或 reportlab==4.0.7

# 模板引擎
Jinja2==3.1.2

# 通义千问（已有）
dashscope>=1.14.0
```

### 6.2 前端依赖

```json
// package.json 新增依赖

{
  "dependencies": {
    "pdfjs-dist": "^3.11.174",  // PDF预览
    "quill": "^1.3.7"  // 富文本编辑（可选）
  }
}
```

---

## 7. 配置管理

### 7.1 配置文件

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

---

## 8. 性能优化

### 8.1 异步处理
- 所有IO操作使用异步方法
- PDF生成使用后台任务队列（可选）

### 8.2 缓存策略
- 模板文件缓存（避免重复加载）
- LLM响应缓存（相同输入缓存结果）

### 8.3 资源限制
- 限制文件上传大小（10MB）
- 限制并发PDF生成数量
- 限制LLM请求频率

---

## 9. 安全性考虑

### 9.1 文件上传安全
- 验证文件类型和大小
- 扫描恶意文件（可选）
- 隔离上传文件存储

### 9.2 数据隐私
- 简历数据加密存储
- 定期清理临时文件
- 不记录敏感信息到日志

### 9.3 API安全
- 请求限流
- 文件访问权限控制
- 防止路径遍历攻击

---

## 10. 测试策略

### 10.1 单元测试
- ResumeParser测试（各种格式）
- ResumeOptimizer测试（Mock LLM）
- ResumeGenerator测试（模板渲染）
- ResumeTemplate测试（模板加载）

### 10.2 集成测试
- 完整简历处理流程测试
- API接口测试
- 文件上传下载测试

### 10.3 端到端测试
- 前端上传 → 解析 → 优化 → 生成 → 下载

---

## 11. 监控和日志

### 11.1 关键指标
- 简历解析成功率
- 优化请求响应时间
- PDF生成成功率
- 文件下载次数

### 11.2 日志记录
- 解析错误日志
- LLM调用日志
- PDF生成日志
- 文件访问日志

---

## 12. 部署考虑

### 12.1 依赖安装
- WeasyPrint需要系统依赖（如libpango、libcairo）
- 确保Python环境正确配置

### 12.2 文件存储
- 配置文件存储目录
- 定期清理过期文件
- 考虑使用对象存储（如OSS）

---

**设计文档创建日期**：2026-01-28
**设计文档创建人**：AI Framework Architect
**最后更新日期**：2026-01-28
