"""
模块名称：链式调用抽象接口
功能描述：定义链式调用的抽象接口，支持多种实现（自研、LangChain）
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - IChain: 链式调用抽象接口

依赖模块：
    - abc: 抽象基类
    - typing: 类型注解
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class IChain(ABC):
    """
    链式调用抽象接口
    
    定义统一的链式调用接口规范，支持多种实现（自研、LangChain）。
    所有链实现都必须实现此接口。
    
    特性：
        - 链执行
        - 链节点管理
        - 链查询
    
    示例：
        >>> chain = LangChainChain(config)
        >>> chain.add_link(link_func1, "link1")
        >>> chain.add_link(link_func2, "link2")
        >>> result = await chain.invoke({"input": "data"})
    """
    
    @abstractmethod
    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行链
        
        根据输入数据执行链式调用。
        
        参数:
            input_data: 输入数据字典
        
        返回:
            执行结果字典
        
        异常:
            RuntimeError: 链未初始化或执行失败时抛出
        
        示例:
            >>> result = await chain.invoke({"input": "Hello"})
            >>> print(result["output"])
        """
        pass
    
    @abstractmethod
    def add_link(self, link_func: Any, name: Optional[str] = None) -> None:
        """
        添加链节点
        
        向链添加一个节点。
        
        参数:
            link_func: 链节点函数（可以是普通函数、异步函数或可调用对象）
            name: 节点名称（可选，如果未提供则使用函数名）
        
        异常:
            ValueError: 节点名称已存在时抛出
        
        示例:
            >>> async def my_link(input_data):
            ...     return {"output": input_data["input"].upper()}
            >>> chain.add_link(my_link, "uppercase")
        """
        pass
    
    @abstractmethod
    def get_links(self) -> List[str]:
        """
        获取链节点列表
        
        返回:
            链节点名称列表（按添加顺序）
        
        示例:
            >>> links = chain.get_links()
            >>> print(links)
            ['link1', 'link2', 'link3']
        """
        pass
