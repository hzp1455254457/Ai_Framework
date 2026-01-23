"""
模块名称：Agent引擎核心模块
功能描述：提供Agent核心执行能力，包括任务执行、工具调用、LLM集成
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - AgentEngine: Agent引擎主类

依赖模块：
    - core.base.service: 服务基类
    - core.llm.service: LLM服务
    - core.agent.tools: 工具系统
    - core.agent.memory: 记忆管理
    - typing: 类型注解
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from core.base.service import BaseService
from core.llm.service import LLMService
from core.agent.tools.tools import ToolRegistry, ToolError
from core.agent.tools.web_tools_registry import register_web_tools
from core.agent.memory import ShortTermMemory, LongTermMemory
from core.agent.planner import Planner, LLMPlanner, Plan, PlannerError


class AgentError(Exception):
    """Agent引擎异常基类"""
    pass


class AgentEngine(BaseService):
    """
    Agent引擎主类
    
    提供Agent核心执行能力，支持任务接收、工具调用、LLM集成。
    
    特性：
        - 任务执行（接收任务并执行）
        - LLM服务集成
        - 工具调用（Function Calling）
        - 记忆管理（短期/长期）
        - 基础工作流循环
    
    工作流循环：
        1. 接收任务 → 组装消息（任务 + 记忆）
        2. 调用LLM（传入工具schema）
        3. 若LLM返回工具调用 → 执行工具 → 将结果回注 → 回到步骤2
        4. 否则输出最终结果
    
    示例：
        >>> engine = AgentEngine(config)
        >>> await engine.initialize()
        >>> result = await engine.run_task("查询北京天气")
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        初始化Agent引擎
        
        参数:
            config: 服务配置字典
        """
        super().__init__(config)
        self._llm_service: Optional[LLMService] = None
        self._tool_registry: ToolRegistry = ToolRegistry()
        self._short_term_memory: Optional[ShortTermMemory] = None
        self._long_term_memory: Optional[LongTermMemory] = None
        self._planner: Optional[Planner] = None
        self._max_iterations: int = config.get("agent", {}).get("max_iterations", 10)
        self._enable_long_term_memory: bool = config.get("agent", {}).get("enable_long_term_memory", False)
        self._enable_planner: bool = config.get("agent", {}).get("enable_planner", False)
    
    async def initialize(self) -> None:
        """
        初始化Agent引擎
        
        初始化LLM服务、记忆系统等资源。
        
        异常:
            InitializationError: 初始化失败时抛出
        """
        await super().initialize()
        
        try:
            # 初始化LLM服务
            llm_config = self._config.get("llm", {})
            if not llm_config:
                raise AgentError("LLM配置缺失")
            
            self._llm_service = LLMService(self._config)
            await self._llm_service.initialize()
            
            # 初始化短期记忆
            max_messages = self._config.get("agent", {}).get("max_messages")
            self._short_term_memory = ShortTermMemory(max_messages=max_messages)
            
            # 初始化长期记忆（如果启用）
            if self._enable_long_term_memory:
                from infrastructure.storage import StorageManager
                storage_config = self._config.get("storage", {})
                storage_manager = StorageManager(storage_config)
                await storage_manager.initialize()
                self._long_term_memory = LongTermMemory(storage_manager)
            
            # 初始化规划器（如果启用）
            if self._enable_planner:
                planner_config = self._config.get("planner", {})
                self._planner = LLMPlanner(self._llm_service, self._config)
                self.logger.info("规划器已启用")
            
            # 注册互联网访问工具（如果启用）
            web_tools_config = self._config.get("agent", {}).get("web_tools", {})
            if web_tools_config.get("enabled", True):
                try:
                    register_web_tools(self._tool_registry, self._config)
                    registered_tools = self._tool_registry.list_tools()
                    web_tools = [t for t in registered_tools if t in ("web_search", "fetch_webpage")]
                    if web_tools:
                        self.logger.info(f"已注册互联网工具: {', '.join(web_tools)}")
                except Exception as e:
                    self.logger.error(f"注册互联网工具失败: {e}", exc_info=True)
            
            self.logger.info("Agent引擎初始化完成")
        except Exception as e:
            self.logger.error(f"Agent引擎初始化失败: {e}", exc_info=True)
            raise
    
    async def run_task(
        self,
        task: str,
        conversation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        执行任务
        
        接收任务描述，执行Agent工作流循环，返回执行结果。
        
        参数:
            task: 任务描述（文本）
            conversation_id: 对话ID（可选，用于长期记忆）
            **kwargs: 其他参数（如temperature、model等）
        
        返回:
            执行结果字典，包含：
                - content: 最终输出内容
                - tool_calls: 工具调用记录（如果有）
                - iterations: 迭代次数
                - metadata: 其他元数据
        
        异常:
            AgentError: 任务执行失败时抛出
        
        示例:
            >>> result = await engine.run_task("查询北京天气")
            >>> print(result["content"])
        """
        if not self._initialized:
            raise AgentError("Agent引擎未初始化")
        
        if not task or not task.strip():
            raise AgentError("任务不能为空")
        
        # 加载长期记忆（如果启用且有conversation_id）
        if self._long_term_memory and conversation_id:
            try:
                saved_messages = await self._long_term_memory.load(conversation_id)
                if saved_messages:
                    # 恢复短期记忆
                    for msg in saved_messages:
                        self._short_term_memory.add_message(msg["role"], msg["content"])
            except Exception as e:
                self.logger.warning(f"加载长期记忆失败: {e}")
        
        # 如果启用规划器，先生成任务规划
        plan: Optional[Plan] = None
        if self._planner:
            try:
                plan = await self._planner.plan(task, context=kwargs.get("context"))
                self.logger.info(f"任务规划完成，共 {len(plan.steps)} 个步骤")
                # 将规划信息添加到记忆
                plan_summary = f"任务规划：\n" + "\n".join([
                    f"{i+1}. {step.description}" for i, step in enumerate(plan.steps)
                ])
                self._short_term_memory.add_message("system", plan_summary)
            except PlannerError as e:
                self.logger.warning(f"任务规划失败，将直接执行任务: {e}")
        
        # 添加任务到短期记忆
        self._short_term_memory.add_message("user", task)
        
        # 执行工作流循环
        iterations = 0
        tool_calls_history: List[Dict[str, Any]] = []
        
        try:
            while iterations < self._max_iterations:
                iterations += 1
                
                # 获取当前消息列表
                messages = self._short_term_memory.get_messages()
                
                # 获取工具schema（如果有工具）
                tools_schema = None
                registered_tools = self._tool_registry.list_tools()
                self.logger.info(f"检查工具注册情况: 已注册工具={registered_tools}, 数量={len(registered_tools)}")
                
                if registered_tools:
                    tools_schema = self._tool_registry.get_function_schemas()
                    self.logger.info(f"获取工具schema: 数量={len(tools_schema) if tools_schema else 0}")
                    if tools_schema:
                        self.logger.debug(f"工具schema详情: {tools_schema}")
                else:
                    self.logger.warning("没有已注册的工具，无法进行工具调用")
                
                # 调用LLM
                llm_kwargs = {
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens"),
                }
                if tools_schema:
                    llm_kwargs["functions"] = tools_schema
                    self.logger.info(f"传递工具schema给LLM: functions参数已设置, 工具数量={len(tools_schema)}")
                else:
                    self.logger.warning("未传递工具schema给LLM，LLM无法调用工具")
                
                self.logger.debug(f"LLM调用参数: model={kwargs.get('model', self._llm_service._default_model)}, messages_count={len(messages)}, has_functions={bool(tools_schema)}")
                
                response = await self._llm_service.chat(
                    messages=messages,
                    model=kwargs.get("model", self._llm_service._default_model),
                    **llm_kwargs,
                )
                
                self.logger.info(f"LLM响应: content_length={len(response.content)}, metadata={response.metadata}")
                
                # 检查是否有工具调用
                metadata = response.metadata or {}
                function_call = metadata.get("function_call")
                tool_calls = metadata.get("tool_calls") or []
                
                # 处理工具调用（优先使用tool_calls，兼容function_call）
                if tool_calls:
                    # 处理多个工具调用
                    for tool_call in tool_calls:
                        tool_name = tool_call.get("function", {}).get("name")
                        tool_args_str = tool_call.get("function", {}).get("arguments", "{}")
                        
                        if tool_name:
                            try:
                                tool_args = json.loads(tool_args_str) if isinstance(tool_args_str, str) else tool_args_str
                                # 执行工具
                                tool_result = await self._tool_registry.execute(tool_name, tool_args)
                                
                                # 记录工具调用
                                tool_calls_history.append({
                                    "tool": tool_name,
                                    "arguments": tool_args,
                                    "result": tool_result,
                                })
                                
                                # 将工具结果添加到记忆
                                self._short_term_memory.add_tool_message(tool_name, tool_result)
                                
                            except (ToolError, json.JSONDecodeError) as e:
                                self.logger.error(f"工具调用失败: {e}")
                                # 继续执行，不中断循环
                
                elif function_call:
                    # 兼容旧版function_call格式
                    tool_name = function_call.get("name")
                    tool_args_str = function_call.get("arguments", "{}")
                    
                    if tool_name:
                        try:
                            tool_args = json.loads(tool_args_str) if isinstance(tool_args_str, str) else tool_args_str
                            tool_result = await self._tool_registry.execute(tool_name, tool_args)
                            
                            tool_calls_history.append({
                                "tool": tool_name,
                                "arguments": tool_args,
                                "result": tool_result,
                            })
                            
                            self._short_term_memory.add_tool_message(tool_name, tool_result)
                            
                        except (ToolError, json.JSONDecodeError) as e:
                            self.logger.error(f"工具调用失败: {e}")
                
                else:
                    # 没有工具调用，输出最终结果
                    final_content = response.content
                    
                    # 将LLM响应添加到记忆
                    self._short_term_memory.add_message("assistant", final_content)
                    
                    # 保存长期记忆（如果启用）
                    if self._long_term_memory and conversation_id:
                        try:
                            await self._long_term_memory.save(
                                conversation_id=conversation_id,
                                messages=self._short_term_memory.get_messages(),
                                metadata={"task": task, "iterations": iterations},
                            )
                        except Exception as e:
                            self.logger.warning(f"保存长期记忆失败: {e}")
                    
                    return {
                        "content": final_content,
                        "tool_calls": tool_calls_history,
                        "iterations": iterations,
                        "metadata": {
                            "model": response.model,
                            "usage": response.usage,
                        },
                    }
            
            # 达到最大迭代次数
            raise AgentError(f"任务执行超时，已达到最大迭代次数: {self._max_iterations}")
        
        except Exception as e:
            self.logger.error(f"任务执行失败: {e}", exc_info=True)
            raise AgentError(f"任务执行失败: {e}") from e
    
    def register_tool(self, tool: Any) -> None:
        """
        注册工具
        
        参数:
            tool: Tool实例
        
        异常:
            ToolError: 工具注册失败时抛出
        
        示例:
            >>> from core.agent.tools import Tool
            >>> tool = Tool(name="get_weather", ...)
            >>> engine.register_tool(tool)
        """
        self._tool_registry.register(tool)
        self.logger.info(f"工具已注册: {tool.name}")
    
    def get_tools(self) -> List[str]:
        """
        获取已注册的工具列表
        
        返回:
            工具名称列表
        """
        return self._tool_registry.list_tools()
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        获取所有工具的Function Calling schema列表
        
        返回:
            工具schema列表
        """
        return self._tool_registry.get_function_schemas()
    
    def clear_memory(self) -> None:
        """清空短期记忆"""
        if self._short_term_memory:
            self._short_term_memory.clear()
    
    async def cleanup(self) -> None:
        """清理Agent引擎资源"""
        if self._llm_service:
            await self._llm_service.cleanup()
        if self._long_term_memory:
            # StorageManager的清理由外部管理
            pass
        await super().cleanup()
