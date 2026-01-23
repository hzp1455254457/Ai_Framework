"""
Agent工具模块

提供工具定义、注册和管理功能。
"""

# 从父级tools.py模块导入核心类
# 注意：tools.py在core/agent/目录下，而当前文件在core/agent/tools/目录下
# 由于包名冲突，需要使用sys.modules直接访问已加载的模块
import sys
import os

# 获取tools.py文件的完整路径
tools_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools.py')

# 如果tools.py模块还未加载，先加载它
if 'core.agent.tools' not in sys.modules or not hasattr(sys.modules.get('core.agent.tools', None), 'Tool'):
    # 直接执行tools.py文件
    with open(tools_file, 'r', encoding='utf-8') as f:
        code = compile(f.read(), tools_file, 'exec')
        # 创建一个新的命名空间
        namespace = {'__name__': 'core.agent.tools', '__file__': tools_file}
        exec(code, namespace)
        # 将命名空间的内容添加到sys.modules
        if 'core.agent.tools' not in sys.modules:
            import types
            module = types.ModuleType('core.agent.tools')
            module.__file__ = tools_file
            sys.modules['core.agent.tools'] = module
        for key, value in namespace.items():
            if not key.startswith('__'):
                setattr(sys.modules['core.agent.tools'], key, value)

# 从已加载的模块导入
tools_module = sys.modules['core.agent.tools']
Tool = tools_module.Tool
ToolRegistry = tools_module.ToolRegistry
ToolError = tools_module.ToolError

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
