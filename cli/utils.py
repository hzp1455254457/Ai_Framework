"""
模块名称：CLI工具模块
功能描述：提供CLI通用工具函数（输入输出、消息格式化等）
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队
"""

from __future__ import annotations

from typing import Dict, List


def format_messages_from_pairs(pairs: List[str]) -> List[Dict[str, str]]:
    """
    将CLI参数中的文本转换为messages结构

    参数：
        pairs: 文本列表（每个元素为用户输入）

    返回：
        messages: [{"role": "user", "content": "..."}]
    """
    return [{"role": "user", "content": p} for p in pairs if p.strip()]

