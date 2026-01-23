"""
互联网工具注册模块

提供互联网访问工具的注册函数，用于在AgentEngine中自动注册。
"""

from typing import Any, Dict

# 导入Tool和ToolRegistry（兼容两种导入方式）
try:
    from core.agent.tools import Tool, ToolRegistry
except ImportError:
    try:
        from core.agent.tools.tools import Tool, ToolRegistry
    except ImportError:
        raise ImportError("无法导入Tool和ToolRegistry，请检查导入路径")

from core.agent.tools.web_tools import web_search, fetch_webpage


def create_web_tools(config: Dict[str, Any]) -> list[Tool]:
    """
    创建互联网访问工具实例
    
    根据配置创建 web_search 和 fetch_webpage 工具。
    
    参数:
        config: 工具配置字典，包含：
            - web_tools.enabled: 是否启用互联网工具（默认True）
            - web_tools.web_search.enabled: 是否启用web_search工具（默认True）
            - web_tools.fetch_webpage.enabled: 是否启用fetch_webpage工具（默认True）
            - web_tools.web_search.search_engine: 搜索引擎类型（duckduckgo/google/bing，默认duckduckgo）
            - web_tools.web_search.api_key: API密钥（Google/Bing需要）
            - web_tools.web_search.timeout: 超时时间（秒，默认10.0）
            - web_tools.web_search.max_retries: 最大重试次数（默认2）
            - web_tools.fetch_webpage.timeout: 超时时间（秒，默认10.0）
            - web_tools.fetch_webpage.max_retries: 最大重试次数（默认2）
            - web_tools.fetch_webpage.max_length: 最大文本长度（默认10000）
    
    返回:
        工具实例列表
    """
    tools = []
    web_tools_config = config.get("agent", {}).get("web_tools", {})
    
    # 检查是否启用互联网工具
    if not web_tools_config.get("enabled", True):
        return tools
    
    # 创建 web_search 工具
    if web_tools_config.get("web_search", {}).get("enabled", True):
        web_search_config = web_tools_config.get("web_search", {})
        
        async def web_search_wrapper(query: str, max_results: int = 5) -> str:
            """web_search工具包装函数"""
            return await web_search(
                query=query,
                max_results=max_results,
                search_engine=web_search_config.get("search_engine", "duckduckgo"),
                api_key=web_search_config.get("api_key"),
                timeout=web_search_config.get("timeout", 10.0),
                max_retries=web_search_config.get("max_retries", 2),
            )
        
        web_search_tool = Tool(
            name="web_search",
            description="通过搜索引擎查询互联网内容。支持查询实时信息、新闻、技术文档等。返回搜索结果摘要列表（包含标题、URL和摘要）。",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询关键词"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大返回结果数（1-20，默认5）",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 5
                    }
                },
                "required": ["query"]
            },
            func=web_search_wrapper
        )
        tools.append(web_search_tool)
    
    # 创建 fetch_webpage 工具
    if web_tools_config.get("fetch_webpage", {}).get("enabled", True):
        fetch_webpage_config = web_tools_config.get("fetch_webpage", {})
        
        async def fetch_webpage_wrapper(url: str) -> str:
            """fetch_webpage工具包装函数"""
            return await fetch_webpage(
                url=url,
                timeout=fetch_webpage_config.get("timeout", 10.0),
                max_retries=fetch_webpage_config.get("max_retries", 2),
                max_length=fetch_webpage_config.get("max_length", 10000),
            )
        
        fetch_webpage_tool = Tool(
            name="fetch_webpage",
            description="获取指定URL的网页内容并提取主要文本。用于分析网页内容、获取文档信息等。返回格式化的文本内容（去除HTML标签、脚本等）。",
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要获取的网页URL（必须是http或https协议）"
                    }
                },
                "required": ["url"]
            },
            func=fetch_webpage_wrapper
        )
        tools.append(fetch_webpage_tool)
    
    return tools


def register_web_tools(registry: ToolRegistry, config: Dict[str, Any]) -> None:
    """
    注册互联网访问工具到工具注册表
    
    参数:
        registry: 工具注册表实例
        config: 配置字典
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("开始注册互联网工具...")
    tools = create_web_tools(config)
    logger.info(f"创建了 {len(tools)} 个工具实例")
    
    if len(tools) == 0:
        logger.warning("未创建任何工具实例，请检查配置")
        return
    
    registered_count = 0
    for tool in tools:
        try:
            registry.register(tool)
            registered_count += 1
            logger.info(f"✅ 成功注册工具: {tool.name}")
        except Exception as e:
            # 如果工具已存在，记录警告但不中断
            logger.warning(f"注册互联网工具 {tool.name} 失败: {e}", exc_info=True)
    
    logger.info(f"互联网工具注册完成: 成功 {registered_count}/{len(tools)}")
    
    # 验证注册结果
    registered_tools = registry.list_tools()
    logger.info(f"当前已注册的工具: {registered_tools}")
