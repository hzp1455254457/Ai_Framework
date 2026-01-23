"""
模块名称：互联网访问工具模块
功能描述：提供互联网访问工具，包括搜索引擎查询和网页内容获取
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要函数：
    - web_search: 搜索引擎查询工具
    - fetch_webpage: 网页内容获取工具

依赖模块：
    - httpx: 异步HTTP客户端
    - bs4: HTML解析库（beautifulsoup4）
    - typing: 类型注解
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from httpx import AsyncClient, HTTPError, TimeoutException

# 导入ToolError（兼容两种导入方式）
try:
    from core.agent.tools.tools import ToolError
except ImportError:
    from core.agent.tools import ToolError


async def web_search(
    query: str,
    max_results: int = 5,
    search_engine: str = "duckduckgo",
    api_key: Optional[str] = None,
    timeout: float = 10.0,
    max_retries: int = 2,
) -> str:
    """
    搜索引擎查询工具
    
    通过搜索引擎查询互联网内容，返回搜索结果摘要。
    
    参数:
        query: 查询关键词
        max_results: 最大返回结果数（默认5）
        search_engine: 搜索引擎类型（duckduckgo/google/bing，默认duckduckgo）
        api_key: API密钥（Google/Bing需要，DuckDuckGo不需要）
        timeout: 请求超时时间（秒，默认10.0）
        max_retries: 最大重试次数（默认2）
    
    返回:
        格式化的搜索结果文本，包含标题、URL和摘要
    
    异常:
        ToolError: 查询失败时抛出
    
    示例:
        >>> result = await web_search("Python async programming")
        >>> # 返回: "1. Python Async Programming Guide\nURL: https://...\n摘要: ..."
    """
    if not query or not query.strip():
        raise ToolError("查询关键词不能为空")
    
    if max_results < 1 or max_results > 20:
        raise ToolError("max_results 必须在 1-20 之间")
    
    # 根据搜索引擎选择实现
    if search_engine.lower() == "duckduckgo":
        return await _duckduckgo_search(query, max_results, timeout, max_retries)
    elif search_engine.lower() == "google":
        if not api_key:
            raise ToolError("Google搜索需要API密钥")
        return await _google_search(query, max_results, api_key, timeout, max_retries)
    elif search_engine.lower() == "bing":
        if not api_key:
            raise ToolError("Bing搜索需要API密钥")
        return await _bing_search(query, max_results, api_key, timeout, max_retries)
    else:
        raise ToolError(f"不支持的搜索引擎: {search_engine}，支持: duckduckgo/google/bing")


async def _duckduckgo_search(
    query: str,
    max_results: int,
    timeout: float,
    max_retries: int,
) -> str:
    """
    DuckDuckGo 搜索引擎实现
    
    使用 DuckDuckGo HTML 接口进行搜索（无需API密钥）。
    """
    client = AsyncClient(timeout=timeout, follow_redirects=True)
    
    try:
        # DuckDuckGo HTML搜索接口
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        for attempt in range(max_retries + 1):
            try:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                break
            except (HTTPError, TimeoutException) as e:
                if attempt == max_retries:
                    raise ToolError(f"DuckDuckGo搜索失败: {e}") from e
                continue
        
        # 解析HTML结果
        if BeautifulSoup is None:
            # 如果没有beautifulsoup4，使用简单的正则表达式提取
            return _parse_duckduckgo_html_simple(response.text, max_results)
        else:
            return _parse_duckduckgo_html(response.text, max_results)
    
    except Exception as e:
        raise ToolError(f"搜索失败: {e}") from e
    finally:
        await client.aclose()


def _parse_duckduckgo_html(html: str, max_results: int) -> str:
    """使用BeautifulSoup解析DuckDuckGo搜索结果"""
    soup = BeautifulSoup(html, "html.parser")
    results = []
    
    # DuckDuckGo HTML结果结构
    result_divs = soup.find_all("div", class_="result")
    
    for i, result_div in enumerate(result_divs[:max_results]):
        title_elem = result_div.find("a", class_="result__a")
        snippet_elem = result_div.find("a", class_="result__snippet")
        
        if title_elem:
            title = title_elem.get_text(strip=True)
            url = title_elem.get("href", "")
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            
            results.append(f"{i+1}. {title}\n   URL: {url}\n   摘要: {snippet}")
    
    if not results:
        return "未找到相关搜索结果"
    
    return "\n\n".join(results)


def _parse_duckduckgo_html_simple(html: str, max_results: int) -> str:
    """简单的HTML解析（不使用BeautifulSoup）"""
    results = []
    # 简单的正则表达式匹配（不够健壮，但可以作为fallback）
    pattern = r'<a class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
    matches = re.findall(pattern, html)
    
    for i, (url, title) in enumerate(matches[:max_results]):
        results.append(f"{i+1}. {title}\n   URL: {url}")
    
    if not results:
        return "未找到相关搜索结果"
    
    return "\n\n".join(results)


async def _google_search(
    query: str,
    max_results: int,
    api_key: str,
    timeout: float,
    max_retries: int,
) -> str:
    """
    Google 自定义搜索API实现
    
    需要Google Custom Search API密钥。
    """
    client = AsyncClient(timeout=timeout)
    
    try:
        # Google Custom Search API
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": "YOUR_SEARCH_ENGINE_ID",  # 需要配置
            "q": query,
            "num": min(max_results, 10),  # Google API最多返回10个结果
        }
        
        for attempt in range(max_retries + 1):
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                break
            except (HTTPError, TimeoutException) as e:
                if attempt == max_retries:
                    raise ToolError(f"Google搜索失败: {e}") from e
                continue
        
        # 解析JSON结果
        results = []
        items = data.get("items", [])
        
        for i, item in enumerate(items[:max_results]):
            title = item.get("title", "")
            url = item.get("link", "")
            snippet = item.get("snippet", "")
            results.append(f"{i+1}. {title}\n   URL: {url}\n   摘要: {snippet}")
        
        if not results:
            return "未找到相关搜索结果"
        
        return "\n\n".join(results)
    
    except Exception as e:
        raise ToolError(f"Google搜索失败: {e}") from e
    finally:
        await client.aclose()


async def _bing_search(
    query: str,
    max_results: int,
    api_key: str,
    timeout: float,
    max_retries: int,
) -> str:
    """
    Bing 搜索API实现
    
    需要Bing Search API密钥。
    """
    client = AsyncClient(timeout=timeout)
    
    try:
        # Bing Search API v7
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {"q": query, "count": min(max_results, 50)}
        
        for attempt in range(max_retries + 1):
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                break
            except (HTTPError, TimeoutException) as e:
                if attempt == max_retries:
                    raise ToolError(f"Bing搜索失败: {e}") from e
                continue
        
        # 解析JSON结果
        results = []
        web_pages = data.get("webPages", {}).get("value", [])
        
        for i, page in enumerate(web_pages[:max_results]):
            title = page.get("name", "")
            url = page.get("url", "")
            snippet = page.get("snippet", "")
            results.append(f"{i+1}. {title}\n   URL: {url}\n   摘要: {snippet}")
        
        if not results:
            return "未找到相关搜索结果"
        
        return "\n\n".join(results)
    
    except Exception as e:
        raise ToolError(f"Bing搜索失败: {e}") from e
    finally:
        await client.aclose()


async def fetch_webpage(
    url: str,
    timeout: float = 10.0,
    max_retries: int = 2,
    max_length: int = 10000,
) -> str:
    """
    获取网页内容工具
    
    获取指定URL的网页内容，解析HTML提取主要文本。
    
    参数:
        url: 网页URL
        timeout: 请求超时时间（秒，默认10.0）
        max_retries: 最大重试次数（默认2）
        max_length: 最大返回文本长度（字符数，默认10000）
    
    返回:
        格式化的网页文本内容（去除HTML标签、脚本等）
    
    异常:
        ToolError: 获取失败时抛出
    
    示例:
        >>> result = await fetch_webpage("https://example.com")
        >>> # 返回: "网页主要内容文本..."
    """
    if not url or not url.strip():
        raise ToolError("URL不能为空")
    
    # 验证URL格式
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ToolError(f"无效的URL格式: {url}")
    
    if parsed.scheme not in ("http", "https"):
        raise ToolError(f"不支持的URL协议: {parsed.scheme}，仅支持 http/https")
    
    client = AsyncClient(timeout=timeout, follow_redirects=True)
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        for attempt in range(max_retries + 1):
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                break
            except (HTTPError, TimeoutException) as e:
                if attempt == max_retries:
                    raise ToolError(f"获取网页失败: {e}") from e
                continue
        
        # 检查Content-Type
        content_type = response.headers.get("content-type", "").lower()
        if "text/html" not in content_type:
            raise ToolError(f"不支持的Content-Type: {content_type}，仅支持 text/html")
        
        # 解析HTML
        if BeautifulSoup is None:
            # 如果没有beautifulsoup4，使用简单的文本提取
            text = _extract_text_simple(response.text)
        else:
            text = _extract_text(response.text)
        
        # 限制长度
        if len(text) > max_length:
            text = text[:max_length] + "...\n[内容已截断]"
        
        return text
    
    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError(f"获取网页失败: {e}") from e
    finally:
        await client.aclose()


def _extract_text(html: str) -> str:
    """使用BeautifulSoup提取网页文本内容"""
    soup = BeautifulSoup(html, "html.parser")
    
    # 移除脚本和样式
    for script in soup(["script", "style", "noscript"]):
        script.decompose()
    
    # 优先提取主要内容区域
    main_content = soup.find("main") or soup.find("article") or soup.find("body")
    
    if main_content:
        text = main_content.get_text(separator="\n", strip=True)
    else:
        text = soup.get_text(separator="\n", strip=True)
    
    # 清理多余的空白
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)


def _extract_text_simple(html: str) -> str:
    """简单的文本提取（不使用BeautifulSoup）"""
    # 移除脚本和样式标签
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    
    # 移除HTML标签
    text = re.sub(r"<[^>]+>", "", html)
    
    # 清理空白
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)
