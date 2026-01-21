"""
测试模块：CLI入口测试
功能描述：测试CLI参数解析
"""

from cli.main import build_parser


class TestCliMain:
    def test_build_parser_chat(self):
        parser = build_parser()
        args = parser.parse_args(["chat", "--env", "dev", "--model", "gpt-3.5-turbo"])
        assert args.command == "chat"
        assert args.env == "dev"
        assert args.model == "gpt-3.5-turbo"

