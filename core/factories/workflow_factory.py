"""
模块名称：工作流工厂
功能描述：提供工作流的工厂方法，支持创建不同实现（native/langgraph）
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - WorkflowFactory: 工作流工厂

依赖模块：
    - core.interfaces.workflow: 工作流接口
"""

from typing import Dict, Any, Optional
from core.interfaces.workflow import IWorkflow

# LangGraph实现（可选）
try:
    from core.implementations.langgraph.langgraph_workflow import LangGraphWorkflow
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    LangGraphWorkflow = None

# Native实现（可选，如果实现了自研工作流）
try:
    from core.implementations.native.native_workflow import NativeWorkflow
    NATIVE_WORKFLOW_AVAILABLE = True
except ImportError:
    NATIVE_WORKFLOW_AVAILABLE = False
    NativeWorkflow = None


class WorkflowFactory:
    """
    工作流工厂
    
    负责创建不同实现的工作流实例。
    支持native（自研）、langgraph两种实现。
    
    示例：
        >>> factory = WorkflowFactory()
        >>> workflow = factory.create("langgraph", config)
    """
    
    @staticmethod
    def create(
        implementation: str,
        config: Dict[str, Any],
        **kwargs: Any
    ) -> IWorkflow:
        """
        创建工作流
        
        参数:
            implementation: 实现类型（native/langgraph）
            config: 配置字典
            **kwargs: 其他参数
        
        返回:
            工作流实例（实现IWorkflow接口）
        
        异常:
            ValueError: 实现类型不支持时抛出
            RuntimeError: 实现依赖不可用时抛出
        
        示例:
            >>> workflow = WorkflowFactory.create("langgraph", config)
        """
        if implementation == "native":
            if not NATIVE_WORKFLOW_AVAILABLE:
                raise RuntimeError("Native工作流实现不可用")
            return NativeWorkflow(config, **kwargs)
        elif implementation == "langgraph":
            if not LANGGRAPH_AVAILABLE:
                raise RuntimeError("LangGraph未安装，请运行: pip install langgraph")
            return LangGraphWorkflow(config, **kwargs)
        else:
            raise ValueError(f"不支持的实现类型: {implementation}，支持的类型：native, langgraph")
    
    @staticmethod
    def create_from_config(config: Dict[str, Any], **kwargs: Any) -> IWorkflow:
        """
        从配置创建工作流（自动选择实现）
        
        参数:
            config: 配置字典，应包含 `workflow.implementation` 配置项
            **kwargs: 其他参数
        
        返回:
            工作流实例
        
        示例:
            >>> workflow = WorkflowFactory.create_from_config(config)
        """
        workflow_config = config.get("workflow", {})
        implementation = workflow_config.get("implementation", "langgraph")
        return WorkflowFactory.create(implementation, config, **kwargs)
