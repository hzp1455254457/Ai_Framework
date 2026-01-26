"""
模块名称：LangChain工具管理器实现
功能描述：使用LangChain Tools实现IToolManager接口
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - LangChainToolManager: LangChain工具管理器实现

依赖模块：
    - core.interfaces.tools: 工具管理器接口
    - langchain: LangChain框架（可选）
"""

from typing import Dict, Any, List, Callable
import json

try:
    from langchain_core.tools import BaseTool, StructuredTool
    from pydantic import BaseModel, create_model, Field
    # LangChain 1.2+ 中Tool已移除，使用StructuredTool
    Tool = StructuredTool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseTool = None
    Tool = None
    StructuredTool = None
    BaseModel = None
    create_model = None
    Field = None

try:
    from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults
    LANGCHAIN_COMMUNITY_AVAILABLE = True
except ImportError:
    LANGCHAIN_COMMUNITY_AVAILABLE = False
    DuckDuckGoSearchRun = None
    DuckDuckGoSearchResults = None

from core.interfaces.tools import IToolManager
from core.agent.tools import Tool as NativeTool


class LangChainToolManager(IToolManager):
    """
    LangChain工具管理器实现
    
    使用LangChain Tools实现IToolManager接口。
    支持LangChain工具和自研工具的混合使用。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化LangChain工具管理器
        
        参数:
            config: 配置字典
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain未安装，请运行: pip install langchain")
        
        self._config = config
        self._tools: Dict[str, Any] = {}  # 存储LangChain工具
        
        # 配置选项：是否允许注册自研工具
        tools_config = config.get("tools", {})
        self._allow_native_tools = tools_config.get("allow_native_tools", False)
        
        # 自动注册LangChain原生搜索工具
        self._auto_register_langchain_tools(tools_config)
    
    def register(self, tool: Any) -> None:
        """
        注册工具
        
        参数:
            tool: 工具实例（优先使用LangChain原生工具，自研工具需要配置允许）
        """
        # 如果是LangChain工具，直接使用
        if LANGCHAIN_AVAILABLE and isinstance(tool, BaseTool):
            self._tools[tool.name] = tool
        # 如果是自研工具，根据配置决定是否允许
        elif isinstance(tool, NativeTool):
            if not self._allow_native_tools:
                raise ValueError(
                    f"不允许注册自研工具: {tool.name}。"
                    "请使用LangChain原生工具，或在配置中设置 tools.allow_native_tools=true"
                )
            # 如果允许，转换为LangChain工具
            langchain_tool = self._convert_native_tool_to_langchain(tool)
            self._tools[langchain_tool.name] = langchain_tool
        else:
            raise ValueError(f"不支持的工具类型: {type(tool)}")
    
    def _convert_native_tool_to_langchain(self, tool: NativeTool) -> Any:
        """
        将自研工具转换为LangChain工具
        
        参数:
            tool: 自研Tool实例
        
        返回:
            LangChain Tool实例
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain未安装")
        
        # 创建异步函数包装器
        async def langchain_func(**kwargs: Any) -> str:
            """LangChain工具函数包装器"""
            try:
                # 调用原生工具
                result = await tool.execute(kwargs)
                # 将结果转换为字符串
                if isinstance(result, str):
                    return result
                elif isinstance(result, (dict, list)):
                    return json.dumps(result, ensure_ascii=False)
                else:
                    return str(result)
            except Exception as e:
                return f"工具执行错误: {str(e)}"
        
        # 创建Pydantic模型用于参数验证（简化实现）
        # 注意：完整的JSON Schema到Pydantic转换比较复杂，这里提供基础实现
        args_model = None
        if tool.parameters and isinstance(tool.parameters, dict):
            try:
                # 尝试从JSON Schema创建Pydantic模型
                properties = tool.parameters.get("properties", {})
                required = tool.parameters.get("required", [])
                
                # 创建字段字典
                field_definitions = {}
                for prop_name, prop_schema in properties.items():
                    prop_type = prop_schema.get("type", "string")
                    prop_desc = prop_schema.get("description", "")
                    
                    # 映射JSON Schema类型到Python类型
                    python_type = str
                    if prop_type == "integer":
                        python_type = int
                    elif prop_type == "number":
                        python_type = float
                    elif prop_type == "boolean":
                        python_type = bool
                    
                    # 创建字段
                    if prop_name in required:
                        field_definitions[prop_name] = (python_type, Field(..., description=prop_desc))
                    else:
                        field_definitions[prop_name] = (python_type, Field(None, description=prop_desc))
                
                # 创建Pydantic模型
                if field_definitions:
                    args_model = create_model(
                        f"{tool.name}Args",
                        **field_definitions
                    )
            except Exception:
                # 如果创建失败，使用None（LangChain Tool会使用默认验证）
                args_model = None
        
        # 创建LangChain Tool
        # 注意：在新版本LangChain中，Tool已被StructuredTool替代
        # 优先使用Tool（如果可用），否则使用StructuredTool
        if Tool is not None and Tool != StructuredTool:
            # 使用旧版本的Tool
            return Tool(
                name=tool.name,
                description=tool.description,
                func=langchain_func,
                args_schema=args_model if args_model else None
            )
        elif StructuredTool is not None:
            # 使用StructuredTool（需要args_schema，如果没有则创建默认的）
            if args_model is None:
                from pydantic import BaseModel
                class DefaultArgs(BaseModel):
                    pass
                args_model = DefaultArgs
            return StructuredTool(
                name=tool.name,
                description=tool.description,
                func=langchain_func,
                args_schema=args_model
            )
        else:
            raise RuntimeError("无法创建LangChain工具：Tool和StructuredTool都不可用")
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        执行工具
        
        参数:
            tool_name: 工具名称
            arguments: 工具参数
        
        返回:
            工具执行结果
        """
        if tool_name not in self._tools:
            raise ValueError(f"工具不存在: {tool_name}")
        
        tool = self._tools[tool_name]
        
        # 调用LangChain Tool的ainvoke方法
        try:
            result = await tool.ainvoke(arguments)
            return result
        except Exception as e:
            raise ValueError(f"工具执行失败: {e}") from e
    
    def list_tools(self) -> List[str]:
        """
        列出所有工具
        
        返回:
            工具名称列表
        """
        return list(self._tools.keys())
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """
        获取工具schema
        
        参数:
            tool_name: 工具名称
        
        返回:
            工具schema字典（Function Calling格式）
        """
        if tool_name not in self._tools:
            raise ValueError(f"工具不存在: {tool_name}")
        
        tool = self._tools[tool_name]
        
        # 从LangChain Tool获取schema
        schema = {
            "name": tool.name,
            "description": tool.description,
        }
        
        # 如果有args_schema，转换为JSON Schema格式
        if hasattr(tool, "args_schema") and tool.args_schema:
            try:
                # 从Pydantic模型获取JSON Schema
                json_schema = tool.args_schema.schema()
                schema["parameters"] = {
                    "type": "object",
                    "properties": json_schema.get("properties", {}),
                    "required": json_schema.get("required", [])
                }
            except Exception:
                # 如果转换失败，使用空schema
                schema["parameters"] = {"type": "object", "properties": {}}
        else:
            # 如果没有args_schema，使用空schema
            schema["parameters"] = {"type": "object", "properties": {}}
        
        return schema
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        获取所有工具schema
        
        返回:
            所有工具的schema列表（Function Calling格式）
        """
        schemas = []
        for tool_name in self._tools.keys():
            try:
                schema = self.get_tool_schema(tool_name)
                schemas.append(schema)
            except Exception:
                # 如果获取失败，跳过
                continue
        return schemas
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        获取所有工具的Function Calling schema列表（API兼容方法）
        
        返回:
            工具schema列表（Function Calling格式，包含function包装）
        """
        schemas = []
        for tool_name in self._tools.keys():
            try:
                schema = self.get_tool_schema(tool_name)
                # 转换为Function Calling格式
                function_schema = {
                    "function": {
                        "name": schema.get("name", tool_name),
                        "description": schema.get("description", ""),
                        "parameters": schema.get("parameters", {"type": "object", "properties": {}})
                    }
                }
                schemas.append(function_schema)
            except Exception:
                # 如果获取失败，跳过
                continue
        return schemas
    
    def _auto_register_langchain_tools(self, tools_config: Dict[str, Any]) -> None:
        """
        自动注册LangChain原生工具
        
        参数:
            tools_config: 工具配置字典
        """
        # 检查是否启用自动注册
        auto_register = tools_config.get("auto_register_langchain_tools", True)
        if not auto_register:
            return
        
        # 注册DuckDuckGo搜索工具
        if LANGCHAIN_COMMUNITY_AVAILABLE and DuckDuckGoSearchRun is not None:
            try:
                # 使用DuckDuckGoSearchRun（返回文本结果）
                search_tool = DuckDuckGoSearchRun()
                self._tools[search_tool.name] = search_tool
            except Exception as e:
                # 如果注册失败，记录但不抛出异常（允许继续运行）
                pass
        
        # 可以在这里添加其他LangChain原生工具的自动注册
        # 例如：Wikipedia工具、Python REPL工具等