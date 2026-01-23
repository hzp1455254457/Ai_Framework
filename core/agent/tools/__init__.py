"""
Agent工具模块

提供工具定义、注册和管理功能。
"""

# 从tools子模块导入核心类
from core.agent.tools.tools import Tool, ToolRegistry, ToolError

# 导入互联网工具函数
try:
    from core.agent.tools.web_tools import web_search, fetch_webpage
except ImportError:
    # 如果web_tools不可用，设置为None
    web_search = None
    fetch_webpage = None

__all__ = [
    "Tool",
    "ToolRegistry",
    "ToolError",
]

if web_search is not None:
    __all__.append("web_search")
if fetch_webpage is not None:
    __all__.append("fetch_webpage")
