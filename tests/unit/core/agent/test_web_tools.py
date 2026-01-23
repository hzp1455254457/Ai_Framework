"""
模块名称：互联网工具测试模块
功能描述：测试互联网访问工具（web_search、fetch_webpage）
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import Response, HTTPError
from core.agent.tools.web_tools import web_search, fetch_webpage
from core.agent.tools.tools import ToolError


class TestWebSearch:
    """web_search工具测试类"""
    
    @pytest.mark.asyncio
    async def test_web_search_empty_query(self):
        """测试空查询关键词"""
        with pytest.raises(ToolError, match="查询关键词不能为空"):
            await web_search("")
    
    @pytest.mark.asyncio
    async def test_web_search_invalid_max_results(self):
        """测试无效的max_results参数"""
        with pytest.raises(ToolError, match="max_results 必须在 1-20 之间"):
            await web_search("test", max_results=0)
        
        with pytest.raises(ToolError, match="max_results 必须在 1-20 之间"):
            await web_search("test", max_results=21)
    
    @pytest.mark.asyncio
    async def test_web_search_unsupported_engine(self):
        """测试不支持的搜索引擎"""
        with pytest.raises(ToolError, match="不支持的搜索引擎"):
            await web_search("test", search_engine="invalid")
    
    @pytest.mark.asyncio
    async def test_web_search_google_without_api_key(self):
        """测试Google搜索缺少API密钥"""
        with pytest.raises(ToolError, match="Google搜索需要API密钥"):
            await web_search("test", search_engine="google")
    
    @pytest.mark.asyncio
    async def test_web_search_bing_without_api_key(self):
        """测试Bing搜索缺少API密钥"""
        with pytest.raises(ToolError, match="Bing搜索需要API密钥"):
            await web_search("test", search_engine="bing")
    
    @pytest.mark.asyncio
    @patch("core.agent.tools.web_tools.AsyncClient")
    async def test_web_search_duckduckgo_success(self, mock_client_class):
        """测试DuckDuckGo搜索成功"""
        # Mock HTTP响应
        mock_response = MagicMock()
        mock_response.text = """
        <div class="result">
            <a class="result__a" href="https://example.com">Example Title</a>
            <a class="result__snippet">Example snippet text</a>
        </div>
        """
        mock_response.raise_for_status = MagicMock()
        
        # Mock客户端
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client
        
        result = await web_search("test query", search_engine="duckduckgo")
        
        assert "Example Title" in result
        assert "https://example.com" in result
        mock_client.get.assert_called_once()
        mock_client.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("core.agent.tools.web_tools.AsyncClient")
    async def test_web_search_timeout(self, mock_client_class):
        """测试搜索超时"""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=TimeoutException("Request timeout"))
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client
        
        with pytest.raises(ToolError, match="搜索失败"):
            await web_search("test", search_engine="duckduckgo", max_retries=0)
    
    @pytest.mark.asyncio
    @patch("core.agent.tools.web_tools.AsyncClient")
    async def test_web_search_retry(self, mock_client_class):
        """测试搜索重试机制"""
        mock_response = MagicMock()
        mock_response.text = "<div class='result'></div>"
        mock_response.raise_for_status = MagicMock()
        
        mock_client = AsyncMock()
        # 第一次失败，第二次成功
        mock_client.get = AsyncMock(side_effect=[
            TimeoutException("Request timeout"),
            mock_response
        ])
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client
        
        result = await web_search("test", search_engine="duckduckgo", max_retries=1)
        
        assert mock_client.get.call_count == 2


class TestFetchWebpage:
    """fetch_webpage工具测试类"""
    
    @pytest.mark.asyncio
    async def test_fetch_webpage_empty_url(self):
        """测试空URL"""
        with pytest.raises(ToolError, match="URL不能为空"):
            await fetch_webpage("")
    
    @pytest.mark.asyncio
    async def test_fetch_webpage_invalid_url(self):
        """测试无效URL格式"""
        with pytest.raises(ToolError, match="无效的URL格式"):
            await fetch_webpage("not-a-url")
        
        with pytest.raises(ToolError, match="不支持的URL协议"):
            await fetch_webpage("ftp://example.com")
    
    @pytest.mark.asyncio
    @patch("core.agent.tools.web_tools.AsyncClient")
    async def test_fetch_webpage_success(self, mock_client_class):
        """测试获取网页成功"""
        # Mock HTTP响应
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <main>
                    <h1>Test Title</h1>
                    <p>Test content</p>
                </main>
            </body>
        </html>
        """
        mock_response.headers = {"content-type": "text/html; charset=utf-8"}
        mock_response.raise_for_status = MagicMock()
        
        # Mock客户端
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client
        
        result = await fetch_webpage("https://example.com")
        
        assert "Test Title" in result
        assert "Test content" in result
        mock_client.get.assert_called_once()
        mock_client.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("core.agent.tools.web_tools.AsyncClient")
    async def test_fetch_webpage_unsupported_content_type(self, mock_client_class):
        """测试不支持的Content-Type"""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.raise_for_status = MagicMock()
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client
        
        with pytest.raises(ToolError, match="不支持的Content-Type"):
            await fetch_webpage("https://example.com")
    
    @pytest.mark.asyncio
    @patch("core.agent.tools.web_tools.AsyncClient")
    async def test_fetch_webpage_timeout(self, mock_client_class):
        """测试获取网页超时"""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=TimeoutException("Request timeout"))
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client
        
        with pytest.raises(ToolError, match="获取网页失败"):
            await fetch_webpage("https://example.com", max_retries=0)
    
    @pytest.mark.asyncio
    @patch("core.agent.tools.web_tools.AsyncClient")
    async def test_fetch_webpage_max_length(self, mock_client_class):
        """测试最大长度限制"""
        long_content = "A" * 20000
        mock_response = MagicMock()
        mock_response.text = f"<html><body><p>{long_content}</p></body></html>"
        mock_response.headers = {"content-type": "text/html"}
        mock_response.raise_for_status = MagicMock()
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client
        
        result = await fetch_webpage("https://example.com", max_length=10000)
        
        assert len(result) <= 10000 + 20  # 加上截断标记
        assert "[内容已截断]" in result
