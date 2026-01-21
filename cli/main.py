"""
模块名称：CLI入口模块
功能描述：提供命令行入口与命令分发
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队
"""

from __future__ import annotations

import argparse

from cli.commands.chat import main as chat_main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-framework", description="AI框架CLI")

    subparsers = parser.add_subparsers(dest="command", required=True)

    chat_parser = subparsers.add_parser("chat", help="交互式聊天")
    chat_parser.add_argument("--env", default="dev", help="配置环境：dev/prod")
    chat_parser.add_argument("--model", default=None, help="模型名称（可选）")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "chat":
        chat_main(env=args.env, model=args.model)
        return

    parser.error(f"未知命令: {args.command}")


if __name__ == "__main__":
    main()

