# Change: Add Vision Service Core (视觉服务核心)

## Why
当前框架已实现 LLM 服务和 Agent 引擎，但缺少视觉服务能力。Vision 服务是第三阶段的核心功能（P1优先级），能够：
1. **扩展框架能力**：支持图像生成、分析和编辑，使框架具备多模态AI能力
2. **复用架构模式**：可复用 LLM 服务的适配器模式，保持架构一致性
3. **支撑上层应用**：为 API、CLI、Agent 工具等提供视觉能力基础

## What Changes
- 新增 `vision-service` capability：提供统一的视觉服务接口
- 实现 VisionService 核心类（`core/vision/service.py`）
- 实现 Vision 数据模型（`core/vision/models.py`）
- 实现 BaseVisionAdapter 基类（`core/vision/adapters/base.py`）
- 添加基础测试用例

## Impact
- **Affected specs**: `vision-service`（本次新增）
- **Affected code**:
  - `core/vision/service.py` - VisionService 核心类
  - `core/vision/models.py` - Vision 数据模型
  - `core/vision/adapters/base.py` - BaseVisionAdapter 基类
  - `tests/unit/core/vision/` - 单元测试
  - `docs/design/vision-service.md` - 功能设计文档（需创建）
  - `config/default.yaml` - 配置更新（Vision 服务配置）

## Non-Goals
- 不在本次 change 中实现具体的 Vision 适配器（DALL-E、Stable Diffusion 等）
- 不在本次 change 中实现 Vision API 路由
- 不在本次 change 中实现图像处理的具体算法
