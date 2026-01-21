# CLI工具功能设计文档

## 📋 功能概述

### 功能名称
CLI工具（Command Line Interface）

### 功能目的
提供命令行入口，让用户能直接在终端中使用AI框架能力（优先覆盖LLM聊天），便于调试、演示与日常使用。

### 使用场景
- 本地快速聊天测试（无需启动FastAPI）
- 快速切换环境配置（dev/prod）
- 快速切换模型（如 gpt-3.5-turbo / qwen-turbo / deepseek-chat）

---

## 🏗️ 技术架构

### 目录结构

```
cli/
├── main.py                 # CLI入口与命令分发（argparse）
├── commands/
│   └── chat.py             # chat命令：交互式聊天
├── utils.py                # CLI工具函数
└── README.md               # 模块说明
```

### 设计原则
- **轻依赖**：优先使用标准库 `argparse`
- **复用核心能力**：CLI只负责交互和参数解析，业务逻辑调用 `core/`
- **异步优先**：内部调用依旧采用 `asyncio`，保持与框架一致的IO模型

---

## 🔌 接口设计

### 命令列表（v1）
- `chat`：交互式聊天

参数：
- `--env dev|prod`
- `--model <name>`

---

## 🧪 测试策略

### 单元测试
- `build_parser()` 能构建并解析参数
- chat 命令可在mock输入输出下运行（后续补充）

---

## 🔄 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|---|---|---|---|
| v1.0 | 2026-01-21 | 初始版本：chat命令与argparse入口 | - |

