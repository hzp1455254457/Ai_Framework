"""
模块名称：CLI聊天命令模块
功能描述：提供交互式聊天命令
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队
"""

from __future__ import annotations

import asyncio
from typing import Optional

from infrastructure.config.manager import ConfigManager
from core.llm.service import LLMService


async def run_chat(env: str = "dev", model: Optional[str] = None) -> None:
    """
    运行交互式聊天

    参数：
        env: 配置环境（dev/prod）
        model: 模型名称（可选，不传则使用配置默认模型）
    """
    config_manager = ConfigManager.load(env=env)
    config = config_manager.get_all()

    service = LLMService(config)
    await service.initialize()

    print("进入聊天模式，输入 /exit 退出，/model <name> 切换模型。\n")

    current_model = model
    while True:
        user_input = input("You> ").strip()
        if not user_input:
            continue

        if user_input in ("/exit", "/quit"):
            break

        if user_input.startswith("/model "):
            current_model = user_input.split(" ", 1)[1].strip() or None
            print(f"已切换模型: {current_model}\n")
            continue

        try:
            resp = await service.chat(
                messages=[{"role": "user", "content": user_input}],
                model=current_model,
            )
            print(f"AI> {resp.content}\n")
        except Exception as e:
            print(f"ERROR> {e}\n")


def main(env: str = "dev", model: Optional[str] = None) -> None:
    """同步入口（便于argparse调用）"""
    asyncio.run(run_chat(env=env, model=model))

