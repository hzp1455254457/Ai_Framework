"""
模块名称：互联网工具注册测试模块
功能描述：测试互联网工具注册功能
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队
"""

import pytest
from unittest.mock import MagicMock
from core.agent.tools.tools import ToolRegistry
from core.agent.tools.web_tools_registry import create_web_tools, register_web_tools


class TestWebToolsRegistry:
    """互联网工具注册测试类"""
    
    def test_create_web_tools_disabled(self):
        """测试工具被禁用"""
        config = {
            "agent": {
                "web_tools": {
                    "enabled": False
                }
            }
        }
        tools = create_web_tools(config)
        assert len(tools) == 0
    
    def test_create_web_tools_enabled(self):
        """测试工具启用"""
        config = {
            "agent": {
                "web_tools": {
                    "enabled": True,
                    "web_search": {
                        "enabled": True,
                        "search_engine": "duckduckgo"
                    },
                    "fetch_webpage": {
                        "enabled": True
                    }
                }
            }
        }
        tools = create_web_tools(config)
        assert len(tools) == 2
        assert any(tool.name == "web_search" for tool in tools)
        assert any(tool.name == "fetch_webpage" for tool in tools)
    
    def test_create_web_tools_partial_enabled(self):
        """测试部分工具启用"""
        config = {
            "agent": {
                "web_tools": {
                    "enabled": True,
                    "web_search": {
                        "enabled": True
                    },
                    "fetch_webpage": {
                        "enabled": False
                    }
                }
            }
        }
        tools = create_web_tools(config)
        assert len(tools) == 1
        assert tools[0].name == "web_search"
    
    def test_register_web_tools(self):
        """测试注册工具到注册表"""
        registry = ToolRegistry()
        config = {
            "agent": {
                "web_tools": {
                    "enabled": True,
                    "web_search": {
                        "enabled": True
                    },
                    "fetch_webpage": {
                        "enabled": True
                    }
                }
            }
        }
        
        register_web_tools(registry, config)
        
        assert registry.has("web_search")
        assert registry.has("fetch_webpage")
        assert len(registry.list_tools()) == 2
    
    def test_web_search_tool_schema(self):
        """测试web_search工具的schema"""
        config = {
            "agent": {
                "web_tools": {
                    "enabled": True,
                    "web_search": {
                        "enabled": True
                    }
                }
            }
        }
        tools = create_web_tools(config)
        web_search_tool = next(t for t in tools if t.name == "web_search")
        
        schema = web_search_tool.to_function_schema()
        assert schema["name"] == "web_search"
        assert "query" in schema["parameters"]["properties"]
        assert "max_results" in schema["parameters"]["properties"]
        assert "query" in schema["parameters"]["required"]
    
    def test_fetch_webpage_tool_schema(self):
        """测试fetch_webpage工具的schema"""
        config = {
            "agent": {
                "web_tools": {
                    "enabled": True,
                    "fetch_webpage": {
                        "enabled": True
                    }
                }
            }
        }
        tools = create_web_tools(config)
        fetch_tool = next(t for t in tools if t.name == "fetch_webpage")
        
        schema = fetch_tool.to_function_schema()
        assert schema["name"] == "fetch_webpage"
        assert "url" in schema["parameters"]["properties"]
        assert "url" in schema["parameters"]["required"]
