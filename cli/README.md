# CLI模块（cli/）

## 模块概述

本模块提供 AI 框架的命令行入口，便于本地快速验证与日常使用（无需启动HTTP服务）。

## 使用方式

### 安装依赖

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

### 运行聊天

```bash
python -m cli.main chat --env dev
```

可选参数：
- `--model <name>`：指定模型名称
- `--env dev|prod`：指定环境配置（默认dev）

交互命令：
- `/exit` 或 `/quit`：退出
- `/model <name>`：切换模型

