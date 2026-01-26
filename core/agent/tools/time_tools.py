"""
时间工具模块

提供获取当前时间的工具函数，用于Agent系统中。
"""

from datetime import datetime
from typing import Dict, Any, Optional


async def get_current_time(timezone: str = "Asia/Shanghai", format_type: str = "full") -> str:
    """
    获取当前时间的工具函数

    参数:
        timezone: 时区（默认 Asia/Shanghai，即中国标准时间）
        format_type: 时间格式类型:
            - "full": 完整格式（2026年1月26日 13:45:30 星期日）
            - "short": 简短格式（2026-01-26 13:45:30）
            - "time": 仅时间（13:45:30）
            - "date": 仅日期（2026年1月26日 星期日）

    返回:
        格式化的时间字符串
    """
    import pytz

    # 获取当前时间
    now = datetime.now(pytz.timezone(timezone))

    # 根据格式类型返回不同格式
    if format_type == "full":
        # 中文完整格式
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return now.strftime(f"%Y年%m月%d日 %H:%M:%S {weekdays[now.weekday()]}")
    elif format_type == "short":
        # ISO格式
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif format_type == "time":
        # 仅时间
        return now.strftime("%H:%M:%S")
    elif format_type == "date":
        # 仅日期（中文）
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return now.strftime(f"%Y年%m月%d日 {weekdays[now.weekday()]}")
    else:
        # 默认完整格式
        return now.strftime("%Y-%m-%d %H:%M:%S")


def create_time_tools() -> list:
    """
    创建时间工具实例列表

    返回:
        Tool实例列表
    """
    try:
        from core.agent.tools import Tool
    except ImportError:
        from core.agent.tools import Tool

    tools = []

    async def get_time_wrapper(timezone: str = "Asia/Shanghai", format_type: str = "full") -> str:
        """获取当前时间"""
        return await get_current_time(timezone=timezone, format_type=format_type)

    time_tool = Tool(
        name="get_current_time",
        description="获取当前时间。支持获取本地时间（默认中国标准时间）。当用户询问'现在几点了'、'今天日期'、'当前时间'等问题时，必须使用此工具获取准确的当前时间，而不是说无法提供。",
        parameters={
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "时区（默认 Asia/Shanghai，如 America/New_York、Europe/London）",
                    "default": "Asia/Shanghai"
                },
                "format_type": {
                    "type": "string",
                    "description": "时间格式：full(完整)、short(简短)、time(仅时间)、date(仅日期)",
                    "enum": ["full", "short", "time", "date"],
                    "default": "full"
                }
            },
            "required": []
        },
        func=get_time_wrapper
    )
    tools.append(time_tool)

    return tools


def register_time_tools(registry, config: Dict[str, Any] = None) -> None:
    """
    注册时间工具到工具注册表

    参数:
        registry: 工具注册表实例
        config: 配置字典（可选）
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info("开始注册时间工具...")
    tools = create_time_tools()
    logger.info(f"创建了 {len(tools)} 个时间工具实例")

    for tool in tools:
        try:
            registry.register(tool)
            logger.info(f"✅ 成功注册时间工具: {tool.name}")
        except Exception as e:
            logger.warning(f"注册时间工具 {tool.name} 失败: {e}", exc_info=True)

    logger.info(f"时间工具注册完成: {len(tools)} 个工具")
