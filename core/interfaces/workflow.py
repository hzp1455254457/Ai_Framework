"""
模块名称：工作流抽象接口
功能描述：定义工作流的抽象接口，支持多种实现（自研、LangGraph）
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - IWorkflow: 工作流抽象接口

依赖模块：
    - abc: 抽象基类
    - typing: 类型注解
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class IWorkflow(ABC):
    """
    工作流抽象接口
    
    定义统一的工作流接口规范，支持多种实现（自研、LangGraph）。
    所有工作流实现都必须实现此接口。
    
    特性：
        - 工作流执行
        - 节点管理
        - 边管理
        - 状态管理
    
    示例：
        >>> workflow = LangGraphWorkflow(config)
        >>> workflow.add_node("node1", node_func)
        >>> workflow.add_edge("node1", "node2")
        >>> result = await workflow.execute({"input": "data"})
    """
    
    @abstractmethod
    async def execute(
        self,
        input_data: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行工作流
        
        根据输入数据和初始状态执行工作流。
        
        参数:
            input_data: 输入数据字典
            state: 初始状态（可选）
        
        返回:
            执行结果字典
        
        异常:
            RuntimeError: 工作流未初始化或执行失败时抛出
        
        示例:
            >>> result = await workflow.execute({"input": "data"})
            >>> print(result["output"])
        """
        pass
    
    @abstractmethod
    def add_node(self, node_id: str, node_func: Any) -> None:
        """
        添加节点
        
        向工作流添加一个节点。
        
        参数:
            node_id: 节点ID
            node_func: 节点函数（可以是普通函数、异步函数或可调用对象）
        
        异常:
            ValueError: 节点ID已存在时抛出
        
        示例:
            >>> async def my_node(state):
            ...     return {"output": "processed"}
            >>> workflow.add_node("process", my_node)
        """
        pass
    
    @abstractmethod
    def add_edge(self, from_node: str, to_node: str, condition: Optional[Any] = None) -> None:
        """
        添加边
        
        在工作流中添加一条边（连接两个节点）。
        
        参数:
            from_node: 起始节点ID
            to_node: 目标节点ID
            condition: 条件函数（可选，用于条件分支）
        
        异常:
            ValueError: 节点不存在时抛出
        
        示例:
            >>> workflow.add_edge("node1", "node2")
            >>> workflow.add_edge("node2", "node3", condition=lambda x: x["flag"])
        """
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """
        获取当前状态
        
        返回:
            当前工作流状态字典
        
        示例:
            >>> state = workflow.get_state()
            >>> print(state)
            {'step': 2, 'data': {...}}
        """
        pass
