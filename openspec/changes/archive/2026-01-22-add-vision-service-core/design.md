# Vision Service Core 技术设计文档

## Context
Vision 服务是 AI 框架第三阶段的核心功能，需要提供统一的图像生成、分析和编辑接口。本设计参考 LLM 服务的架构模式，保持框架架构的一致性。

## Goals / Non-Goals

### Goals
- 提供统一的 Vision 服务接口，支持图像生成、分析、编辑
- 采用适配器模式，支持多种 Vision 服务提供商
- 复用 BaseService 和 BaseAdapter 架构，保持代码一致性
- 提供完整的类型注解和文档
- 实现基础测试用例，确保代码质量

### Non-Goals
- 不实现具体的 Vision 适配器（DALL-E、Stable Diffusion 等）
- 不实现 Vision API 路由（在后续 change 中实现）
- 不实现图像处理的具体算法（由适配器处理）

## Decisions

### Decision 1: 复用 LLM 服务架构模式
**What**: Vision 服务采用与 LLM 服务相同的架构模式
- VisionService 继承 BaseService
- BaseVisionAdapter 继承 BaseAdapter
- 使用适配器注册表管理适配器

**Why**:
- 保持架构一致性，降低学习成本
- 复用已验证的架构模式，减少设计风险
- 便于维护和扩展

**Alternatives considered**:
- 独立设计 Vision 服务架构：会增加架构复杂度，不利于维护

### Decision 2: 支持三种核心能力
**What**: Vision 服务提供图像生成、分析、编辑三种核心能力
- `generate_image()`: 根据文本提示生成图像
- `analyze_image()`: 分析图像内容（OCR、物体识别、图像理解）
- `edit_image()`: 编辑图像（修改、增强、风格转换）

**Why**:
- 覆盖 Vision 服务的主要应用场景
- 为后续适配器实现提供清晰的接口规范

**Alternatives considered**:
- 仅支持图像生成：功能过于单一，无法满足完整需求

### Decision 3: 使用 Pydantic 进行数据验证
**What**: Vision 数据模型使用 Pydantic BaseModel（与 LLM 服务保持一致）

**Why**:
- 提供自动数据验证
- 支持类型注解和文档生成
- 与项目其他模块保持一致

**Alternatives considered**:
- 使用普通类：缺少自动验证，需要手动实现

## Risks / Trade-offs

### Risks
1. **接口设计可能不够灵活**：不同 Vision 提供商的 API 差异较大
   - **Mitigation**: 设计时考虑扩展性，支持 provider-specific 参数

2. **性能考虑**：图像处理可能涉及大文件传输
   - **Mitigation**: 使用异步 IO，支持流式传输（如需要）

### Trade-offs
- **统一接口 vs 灵活性**：选择统一接口，通过 kwargs 支持扩展
- **同步 vs 异步**：选择异步，与框架整体架构一致

## Migration Plan
- 本次为新增功能，无需迁移
- 后续添加适配器时，只需实现 BaseVisionAdapter 接口

## Open Questions
- 图像存储策略：是否需要框架提供图像存储能力，还是由适配器处理？
- 流式图像生成：是否需要支持流式图像生成（如 DALL-E 3）？
