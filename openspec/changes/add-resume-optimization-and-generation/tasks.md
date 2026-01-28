# Tasks: 简历优化和生成功能

## Change ID
`add-resume-optimization-and-generation`

## Task Overview
本文档列出实现简历优化和生成功能的所有任务，按模块和优先级组织。

---

## 1. 后端核心模块开发

### 1.1 数据模型定义
- [x] 1.1.1 定义ResumeData数据模型（基本信息、教育、工作、项目、技能、证书）
- [x] 1.1.2 定义OptimizationResult数据模型（优化结果、建议、评分）
- [x] 1.1.3 定义TemplateInfo数据模型（模板信息）
- [x] 1.1.4 定义API请求/响应模型（ParseResumeRequest、OptimizeResumeRequest等）
- [x] 1.1.5 编写数据模型单元测试

**角色**：`infrastructure-developer`

### 1.2 ResumeParser实现
- [x] 1.2.1 实现ResumeParser基类（初始化、配置加载）
- [x] 1.2.2 实现PDF解析器（使用pdfplumber提取文本和结构）
- [x] 1.2.3 实现Word解析器（使用python-docx提取内容）
- [x] 1.2.4 实现JSON解析器（直接加载和验证）
- [x] 1.2.5 实现文本结构化提取（正则表达式识别关键字段）
- [x] 1.2.6 编写ResumeParser单元测试（覆盖各种格式和边界情况）

**角色**：`infrastructure-developer`

### 1.3 ResumeOptimizer实现
- [x] 1.3.1 实现ResumeOptimizer基类（初始化、LLM服务集成）
- [x] 1.3.2 实现优化提示词构建（基础优化和高级优化）
- [x] 1.3.3 实现LLM调用（使用通义千问qwen-max）
- [x] 1.3.4 实现LLM响应解析（提取优化建议和优化后内容）
- [x] 1.3.5 实现简历评分逻辑
- [x] 1.3.6 编写ResumeOptimizer单元测试（Mock LLM响应）

**角色**：`llm-service-developer`

### 1.4 ResumeGenerator实现
- [x] 1.4.1 实现ResumeGenerator基类（初始化、配置加载）
- [x] 1.4.2 实现Jinja2模板渲染（加载模板、渲染数据）
- [x] 1.4.3 实现HTML文件保存（异步文件操作）
- [x] 1.4.4 实现WeasyPrint PDF转换（HTML转PDF）
- [x] 1.4.5 实现文件清理机制（定期清理过期文件）
- [ ] 1.4.6 编写ResumeGenerator单元测试（模板渲染和PDF生成）

**角色**：`infrastructure-developer`

### 1.5 ResumeTemplate实现
- [x] 1.5.1 实现ResumeTemplate基类（初始化、配置加载）
- [x] 1.5.2 实现模板列表查询（加载模板元数据）
- [x] 1.5.3 实现模板路径获取
- [x] 1.5.4 创建4个基础模板（classic、modern、creative、tech）
- [x] 1.5.5 为每个模板创建HTML、CSS、metadata.json、preview.png
- [ ] 1.5.6 编写ResumeTemplate单元测试

**角色**：`infrastructure-developer`

### 1.6 ResumeService实现
- [x] 1.6.1 实现ResumeService基类（继承BaseService）
- [x] 1.6.2 实现parse_resume方法（调用ResumeParser）
- [x] 1.6.3 实现optimize_resume方法（调用ResumeOptimizer）
- [x] 1.6.4 实现generate_resume方法（调用ResumeGenerator）
- [x] 1.6.5 实现list_templates方法（调用ResumeTemplate）
- [x] 1.6.6 实现依赖注入（LLMService、ConfigManager、LogManager）
- [ ] 1.6.7 编写ResumeService单元测试

**角色**：`infrastructure-developer`

---

## 2. API接口层开发

### 2.1 Resume API路由实现
- [x] 2.1.1 创建resume.py路由文件
- [x] 2.1.2 实现POST /api/v1/resume/parse接口（文件上传和解析）
- [x] 2.1.3 实现POST /api/v1/resume/optimize接口（简历优化）
- [x] 2.1.4 实现POST /api/v1/resume/generate接口（简历生成）
- [x] 2.1.5 实现GET /api/v1/resume/templates接口（模板列表）
- [x] 2.1.6 实现GET /api/v1/resume/download/{file_id}接口（文件下载）
- [x] 2.1.7 实现GET /api/v1/resume/preview/{file_id}接口（文件预览）
- [x] 2.1.8 集成到FastAPI应用（注册路由）

**角色**：`api-developer`

### 2.2 API依赖注入
- [x] 2.2.1 在dependencies.py中添加get_resume_service依赖
- [x] 2.2.2 配置ResumeService生命周期管理
- [ ] 2.2.3 编写依赖注入单元测试

**角色**：`api-developer`

### 2.3 API测试
- [ ] 2.3.1 编写Resume API单元测试（Mock ResumeService）
- [ ] 2.3.2 编写文件上传测试
- [ ] 2.3.3 编写文件下载测试
- [ ] 2.3.4 编写API集成测试

**角色**：`ai-framework-qa-engineer`

---

## 3. 前端页面开发

### 3.1 移除Agent页面
- [x] 3.1.1 删除src/views/Agent.vue文件
- [x] 3.1.2 删除src/api/endpoints/agent.ts文件
- [x] 3.1.3 删除src/stores/agent.ts文件
- [x] 3.1.4 从router/index.ts中移除Agent路由
- [x] 3.1.5 从导航菜单中移除Agent入口
- [x] 3.1.6 清理相关类型定义和组件

**角色**：`ai-framework-frontend-developer`

### 3.2 Resume API客户端
- [x] 3.2.1 创建src/api/endpoints/resume.ts文件
- [x] 3.2.2 实现parse API调用方法
- [x] 3.2.3 实现optimize API调用方法
- [x] 3.2.4 实现generate API调用方法
- [x] 3.2.5 实现templates API调用方法
- [x] 3.2.6 定义Resume相关类型（src/types/resume.ts）

**角色**：`ai-framework-frontend-developer`

### 3.3 Resume状态管理
- [x] 3.3.1 创建src/stores/resume.ts文件
- [x] 3.3.2 定义Resume状态（resumeData、optimizationResult、templates等）
- [x] 3.3.3 实现parse action
- [x] 3.3.4 实现optimize action
- [x] 3.3.5 实现generate action
- [x] 3.3.6 实现loadTemplates action

**角色**：`ai-framework-frontend-developer`

### 3.4 Resume页面组件
- [x] 3.4.1 创建src/views/Resume.vue主页面
- [x] 3.4.2 创建ResumeUpload.vue组件（文件上传、拖拽支持）
- [x] 3.4.3 创建ResumePreview.vue组件（解析结果展示）
- [x] 3.4.4 创建ResumeOptimization.vue组件（优化区域、建议展示）
- [x] 3.4.5 创建TemplateSelector.vue组件（模板列表、预览、选择）
- [x] 3.4.6 创建ResumeExport.vue组件（格式选择、预览、下载）
- [x] 3.4.7 实现组件间通信和状态同步

**角色**：`ai-framework-frontend-developer`

### 3.5 Resume路由配置
- [x] 3.5.1 在router/index.ts中添加Resume路由
- [x] 3.5.2 配置路由守卫（如需要）
- [x] 3.5.3 更新导航菜单（添加Resume入口）
- [x] 3.5.4 更新Home页面（添加Resume功能入口）

**角色**：`ai-framework-frontend-developer`

### 3.6 前端样式和交互
- [x] 3.6.1 设计Resume页面布局和样式
- [x] 3.6.2 实现响应式设计（移动端适配）
- [x] 3.6.3 实现加载状态和错误提示
- [ ] 3.6.4 实现PDF预览功能（使用PDF.js）
- [x] 3.6.5 优化用户体验（动画、过渡效果）

**角色**：`ai-framework-frontend-developer`

---

## 4. 配置和依赖管理

### 4.1 后端依赖安装
- [x] 4.1.1 更新requirements.txt（添加PyPDF2、pdfplumber、python-docx、WeasyPrint、Jinja2）
- [x] 4.1.2 安装后端依赖（pip install -r requirements.txt）
- [x] 4.1.3 验证依赖安装成功

**角色**：`infrastructure-developer`

### 4.2 前端依赖安装
- [ ] 4.2.1 更新package.json（添加pdfjs-dist等）
- [ ] 4.2.2 安装前端依赖（npm install）
- [ ] 4.2.3 验证依赖安装成功

**角色**：`ai-framework-frontend-developer`

### 4.3 配置文件更新
- [x] 4.3.1 在config/default.yaml中添加resume配置
- [x] 4.3.2 配置LLM服务（通义千问qwen-max）
- [x] 4.3.3 配置解析器参数（文件大小限制、支持格式）
- [x] 4.3.4 配置生成器参数（输出目录、PDF引擎）
- [x] 4.3.5 配置模板参数（模板目录、可用模板）

**角色**：`infrastructure-developer`

---

## 5. 测试

### 5.1 单元测试
- [x] 5.1.1 编写ResumeParser单元测试（覆盖率80%+）
- [x] 5.1.2 编写ResumeOptimizer单元测试（覆盖率80%+）
- [x] 5.1.3 编写ResumeGenerator单元测试（覆盖率80%+）
- [x] 5.1.4 编写ResumeTemplate单元测试（覆盖率80%+）
- [x] 5.1.5 编写ResumeService单元测试（覆盖率80%+）
- [x] 5.1.6 编写Resume API单元测试（覆盖率80%+）
- [ ] 5.1.7 运行所有单元测试并修复失败的测试

**角色**：`ai-framework-qa-engineer`

### 5.2 集成测试
- [x] 5.2.1 编写简历解析集成测试（完整流程）
- [x] 5.2.2 编写简历优化集成测试（完整流程）
- [x] 5.2.3 编写简历生成集成测试（完整流程）
- [x] 5.2.4 编写API集成测试（所有接口）
- [ ] 5.2.5 运行所有集成测试并修复失败的测试

**角色**：`ai-framework-qa-engineer`

### 5.3 端到端测试
- [x] 5.3.1 编写前端E2E测试（上传 → 解析 → 优化 → 生成 → 下载）
- [x] 5.3.2 测试各种简历格式（PDF、Word、JSON）
- [x] 5.3.3 测试各种模板（classic、modern、creative、tech）
- [x] 5.3.4 测试错误处理和边界情况
- [ ] 5.3.5 运行所有E2E测试并修复失败的测试

**角色**：`ai-framework-qa-engineer`

---

## 6. 文档

### 6.1 API文档
- [ ] 6.1.1 更新docs/api/api-reference.md（添加Resume API文档）
- [ ] 6.1.2 添加请求/响应示例
- [ ] 6.1.3 添加错误码说明
- [ ] 6.1.4 验证API文档完整性

**角色**：`ai-framework-documenter`

### 6.2 用户指南
- [ ] 6.2.1 创建docs/guides/resume-guide.md（简历功能使用指南）
- [ ] 6.2.2 添加上传简历教程
- [ ] 6.2.3 添加优化简历教程
- [ ] 6.2.4 添加生成简历教程
- [ ] 6.2.5 添加模板选择教程
- [ ] 6.2.6 添加常见问题解答

**角色**：`ai-framework-documenter`

### 6.3 开发文档
- [ ] 6.3.1 创建docs/development/resume-module.md（Resume模块开发文档）
- [ ] 6.3.2 添加模块架构说明
- [ ] 6.3.3 添加数据模型说明
- [ ] 6.3.4 添加扩展指南（如何添加新模板、新解析器）

**角色**：`ai-framework-documenter`

### 6.4 项目计划更新
- [ ] 6.4.1 更新docs/PROJECT_PLAN.md（添加Resume功能需求）
- [ ] 6.4.2 标记已完成的任务
- [ ] 6.4.3 更新完成度统计
- [ ] 6.4.4 更新最近更新记录

**角色**：`ai-framework-documenter`

---

## 7. 部署和验证

### 7.1 本地验证
- [ ] 7.1.1 启动后端服务（uvicorn）
- [ ] 7.1.2 启动前端服务（npm run dev）
- [ ] 7.1.3 验证所有功能正常工作
- [ ] 7.1.4 验证性能指标（解析时间、优化时间、生成时间）

**角色**：`ai-framework-qa-engineer`

### 7.2 代码审查
- [ ] 7.2.1 代码规范检查（Lint）
- [ ] 7.2.2 代码质量检查（SonarQube等）
- [ ] 7.2.3 安全性检查（依赖漏洞扫描）
- [ ] 7.2.4 性能检查（性能测试）

**角色**：`ai-framework-qa-engineer`

### 7.3 发布准备
- [ ] 7.3.1 更新CHANGELOG.md
- [ ] 7.3.2 更新版本号
- [ ] 7.3.3 创建Git标签
- [ ] 7.3.4 准备发布说明

**角色**：`ai-framework-architect`

---

## Task Summary

### 按模块统计
- **后端核心模块**：34个任务
- **API接口层**：11个任务
- **前端页面**：22个任务
- **配置和依赖**：8个任务
- **测试**：17个任务
- **文档**：14个任务
- **部署和验证**：8个任务

**总计**：114个任务

### 按角色统计
- **infrastructure-developer**：30个任务
- **llm-service-developer**：6个任务
- **api-developer**：11个任务
- **ai-framework-frontend-developer**：22个任务
- **ai-framework-qa-engineer**：25个任务
- **ai-framework-documenter**：14个任务
- **ai-framework-architect**：4个任务

### 预估工作量
- **Phase 1（后端核心模块）**：1周
- **Phase 2（简历生成和模板）**：1周
- **Phase 3（API和路由）**：3天
- **Phase 4（前端页面）**：1周
- **Phase 5（测试和文档）**：3天

**总计**：约3-4周

---

**任务清单创建日期**：2026-01-28
**任务清单创建人**：AI Framework Architect
**最后更新日期**：2026-01-28
